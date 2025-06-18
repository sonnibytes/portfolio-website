"""
Global Admin View Classes for AURA Portfolio
Provides consistent base functionality for all app admin interfaces
"""

from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from django.utils.text import slugify


class AdminAccessMixin(UserPassesTestMixin):
    """Ensures only staff/admin users can access admin views."""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this area.")
        return super().handle_no_permission()


class BaseAdminView:
    """Base mixin for all admin views with common context."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Global admin context
        context.update({
            'admin_section': True,
            'model_name': self.model._meta.verbose_name,
            'model_name_plural': self.model._meta.verbose_name_plural,
            'app_label': self.model._meta.app_label,
            'app_color': self.get_app_color(),
            'breadcrumbs': self.get_breadcrumbs(),
        })

        return context
    
    def get_app_color(self):
        """Return app-specific color for themeing."""
        app_colors = {
            'blog': 'lavender',
            'projects': 'cyan',
            'core': 'emerald',
        }
        return app_colors.get(self.model._meta.app_label, 'slate')
    
    def get_breadcrumbs(self):
        """Generate breadcrumb navigation"""
        app_label = self.model._meta.app_label
        model_name = self.model._meta.verbose_name_plural

        breadcrumbs = [
            {'name': 'Admin', 'url': reverse_lazy('core:admin_dashboard')},
            {'name': app_label.title(), 'url': f"/{app_label}/admin/"},
            {'name': model_name.title(), 'url': None},
        ]

        return breadcrumbs


class BaseAdminListView(AdminAccessMixin, BaseAdminView, ListView):
    """Base list view for admin interface."""

    template_name = 'admin/list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'title': f'Manage {self.model._meta.verbose_name_plural}',
            'can_add': self.get_can_add(),
            'search_query': self.request.GET.get('search', ''),
            'total_count': self.get_queryset().count(),
            'filtered_count': context['object_list'].count() if context.get('object_list') else 0,
        })

        return context

    def get_can_add(self):
        """Override to control add permissions per model."""
        return True
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Add search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = self.filter_queryset(queryset, search_query)
        
        return queryset

    def filter_queryset(self, queryset, search_query):
        """Override in subclasses to define search fields."""
        return queryset


class BaseAdminCreateView(AdminAccessMixin, BaseAdminView, CreateView):
    """Base create view for admin operations."""

    template_name = 'admin/forms/create_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'{self.model._meta.verbose_name.title()} created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'title': f'Create {self.model._meta.verbose_name}',
            'submit_text': f'Create {self.model._meta.verbose_name}',
            'cancel_url': self.get_success_url(),
            'form_type': 'create',
            'icon': self.get_form_icon(),
        })

        return context
    
    def get_form_icon(self):
        """Return Font Awesome icon for form."""
        return 'fas fa-plus-circle'


class BaseAdminUpdateView(AdminAccessMixin, BaseAdminView, UpdateView):
    """Base update view for admin operations."""

    template_name = 'admon/forms/update_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'{self.model._meta.verbose_name.title()} updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'title': f'Edit {self.model._meta.verbose_name}',
            'submit_text': f'Update {self.model._meta.verbose_name}',
            'cancel_url': self.get_success_url(),
            'form_type': 'update',
            'object_name': str(self.object),
            'icon': self.get_form_icon(),
        })

        return context
    
    def get_form_icon(self):
        """Return Font Awesome icon for form."""
        return 'fas fa-edit'




