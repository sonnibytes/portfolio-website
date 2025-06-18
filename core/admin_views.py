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


class BaseAdminDeleteView(AdminAccessMixin, BaseAdminView, DeleteView):
    """Base delete view for admin operations."""

    template_name = 'admin/forms/delete_confirm.html'

    def delete(self, request, *args, **kwargs):
        obj_name = str(self.get_object())
        response = super().delete(request, *args, **kwargs)

        messages.success(request, f'{self.model._meta.verbose_name.title()} "{obj_name}" deleted successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'title': f'Delete {self.model._meta.verbose_name}',
            'object_name': str(self.object),
            'form_type': 'delete',
            'icon': 'fas fa-trash-alt',
            'warning_message': self.get_delete_warning(),
            'related_objects': self.get_related_objects(),
        })

        return context
    
    def get_delete_warning(self):
        """Override to provide model-specific delete warnings."""
        return f'This will permanently delete this {self.model._meta.verbose_name}.'
    
    def get_related_objects(self):
        """Override to show related objects that will be affected."""
        return []


class AjaxableResponseMixin:
    """Mixin to add AJAX support to admin views."""

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{self.model._meta.verbose_name.title()} saved successfully!',
                'redirect_url': str(self.get_success_url()),
                'object_id': self.object.pk if hasattr(self, 'object') else None,
            })
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors below.',
            }, status=400)
        return response


class BulkActionMixin:
    """Mixin to add bulk actions to list views."""

    def post(self, request, *args, **kwargs):
        """Handle bulk actions."""
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')

        if not action or not selected_ids:
            messages.error(request, 'No action or items selected.')
            return self.get(request, *args, **kwargs)
        return self.handle_bulk_action(action, selected_ids)
    
    def handle_bulk_action(self, action, selected_ids):
        """Override in subclasses to handle specific bulk actions."""
        queryset = self.model.objects.filter(id__in=selected_ids)

        if action == 'delete':
            count = queryset.count()
            queryset.delete()
            messages.success(self.request, f'Successfully deleted {count} {self.model._meta.verbose_name_plural}.')

        return self.get(self.request)


# Specioalized admin views for common patterns
class SlugAdminCreateView(BaseAdminCreateView):
    """Create view that auto-generates slugs."""

    def form_valid(self, form):
        if hasattr(form.instance, 'slug') and not form.instance.slug:
            if hasattr(form.instance, 'title'):
                form.instance.slug = slugify(form.instance.title)
            elif hasattr(form.instance, 'name'):
                form.instance.slug = slugify(form.instance.name)
        
        return super().form_valid(form)


class AuthorAdminCreateView(BaseAdminCreateView):
    """Create view that set the current user as author."""

    def form_valid(self, form):
        if hasattr(form.instance, 'author') and not form.instance.author:
            form.instance.author = self.request.user
        
        return super().form_valid(form)


class StatusAdminCreateView(BaseAdminCreateView):
    """Create view w status-specific logic."""

    def form_valid(self, form):
        # Auto-set published_date for published items
        if (hasattr(form.instance, 'status') and 
            form.instance.status == 'published' and
            hasattr(form.instance, 'published_date') and
            not form.instance.published_date):
            from django.utils import timezone
            form.instance.published_date = timezone.now()
        
        return super().form_valid(form)
