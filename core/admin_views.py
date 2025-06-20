"""
Global Admin View Classes for AURA Portfolio
Provides consistent base functionality for all app admin interfaces
Version 2.0 - FIXED URL Namespaces
"""

from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Sum
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.shortcuts import redirect


class AdminAccessMixin(UserPassesTestMixin):
    """Ensures only staff/admin users can access admin views."""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this area.")
        return redirect("core:home")


class BaseAdminView:
    """Base mixin for all admin views with common context."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Global admin context
        context.update(
            {
                "admin_section": True,
                "model_name": self.model._meta.verbose_name,
                "model_name_plural": self.model._meta.verbose_name_plural,
                "app_label": self.model._meta.app_label,
                "app_color": self.get_app_color(),
                "breadcrumbs": self.get_breadcrumbs(),
            }
        )

        return context

    def get_app_color(self):
        """Return app-specific color for theming."""
        app_colors = {
            "blog": "lavender",
            "projects": "cyan",
            "core": "emerald",
        }
        return app_colors.get(self.model._meta.app_label, "slate")

    def get_breadcrumbs(self):
        """Generate breadcrumb navigation - FIXED URL namespaces"""
        app_label = self.model._meta.app_label
        model_name = self.model._meta.verbose_name_plural

        breadcrumbs = [
            {"name": "AURA Admin", "url": reverse_lazy("aura_admin:dashboard")},
        ]
        
        # Add app-specific breadcrumb
        if app_label == "blog":
            breadcrumbs.append({
                "name": "DataLogs", 
                "url": reverse_lazy("aura_admin:blog:dashboard")
            })
        elif app_label == "projects":
            breadcrumbs.append({
                "name": "Systems", 
                "url": reverse_lazy("aura_admin:projects:dashboard")
            })
        else:
            breadcrumbs.append({
                "name": app_label.title(), 
                "url": None
            })
        
        # Add model name
        breadcrumbs.append({
            "name": model_name.title(), 
            "url": None
        })

        return breadcrumbs


class BaseAdminListView(AdminAccessMixin, BaseAdminView, ListView):
    """Base list view for admin interface."""
    
    template_name = 'admin/list.html'
    context_object_name = 'objects'
    paginate_by = 25
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": f"Manage {self.model._meta.verbose_name_plural}",
                "can_add": self.get_can_add(),
                "search_query": self.request.GET.get("search", ""),
                "status_filter": self.request.GET.get("status", ""),
                "total_count": self.get_base_queryset().count(),
                "filtered_count": self.get_queryset().count(),
            }
        )

        return context

    def get_can_add(self):
        """Override to control add permissions per model."""
        return True

    def get_base_queryset(self):
        """Get the base queryset before filtering."""
        return self.model.objects.all()

    def get_queryset(self):
        """Get filtered queryset with search."""
        queryset = self.get_base_queryset()

        # Search functionality
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = self.filter_queryset(queryset, search_query)

        # Status filtering if model has status field
        status_filter = self.request.GET.get("status", "")
        if status_filter and hasattr(self.model, "status"):
            queryset = queryset.filter(status=status_filter)

        return queryset.distinct()

    def filter_queryset(self, queryset, search_query):
        """Override to implement model-specific search."""
        # Default search on title/name fields
        if hasattr(self.model, "title"):
            return queryset.filter(title__icontains=search_query)
        elif hasattr(self.model, "name"):
            return queryset.filter(name__icontains=search_query)
        return queryset


class BaseAdminCreateView(AdminAccessMixin, BaseAdminView, CreateView):
    """Base create view for admin interface."""

    template_name = "admin/forms/create_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": f"Create {self.model._meta.verbose_name}",
                "form_mode": "create",
            }
        )
        return context

    def form_valid(self, form):
        # Auto-assign author if model has author field
        if hasattr(self.model, "author") and not form.instance.author:
            form.instance.author = self.request.user

        # Auto-generate slug if model has slug field
        if hasattr(self.model, "slug") and not form.instance.slug:
            if hasattr(self.model, "title"):
                form.instance.slug = slugify(form.instance.title)
            elif hasattr(self.model, "name"):
                form.instance.slug = slugify(form.instance.name)

        response = super().form_valid(form)
        messages.success(
            self.request,
            f'{self.model._meta.verbose_name} "{self.object}" created successfully!',
        )
        return response


class BaseAdminUpdateView(AdminAccessMixin, BaseAdminView, UpdateView):
    """Base update view for admin interface."""

    template_name = "admin/forms/update_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": f"Edit {self.model._meta.verbose_name}",
                "form_mode": "update",
            }
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'{self.model._meta.verbose_name} "{self.object}" updated successfully!',
        )
        return response


class BaseAdminDeleteView(AdminAccessMixin, BaseAdminView, DeleteView):
    """Base delete view for admin interface."""

    template_name = "admin/forms/delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": f"Delete {self.model._meta.verbose_name}",
            }
        )
        return context

    def delete(self, request, *args, **kwargs):
        object_name = str(self.get_object())
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request, 
            f'{self.model._meta.verbose_name.title()} "{object_name}" deleted successfully!'
        )
        return response


class BulkActionMixin:
    """Mixin to add bulk action functionality."""
    
    def post(self, request, *args, **kwargs):
        """Handle bulk actions."""
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_items")

        if not action or not selected_ids:
            messages.error(request, "No action or items selected.")
            return redirect(request.path)

        queryset = self.model.objects.filter(id__in=selected_ids)

        if action == "delete":
            count = queryset.count()
            queryset.delete()
            messages.success(request, f"Deleted {count} items successfully.")

        elif action == "publish" and hasattr(self.model, "status"):
            count = queryset.update(status="published")
            messages.success(request, f"Published {count} items successfully.")

        elif action == "draft" and hasattr(self.model, "status"):
            count = queryset.update(status="draft")
            messages.success(request, f"Moved {count} items to draft.")

        elif action == "feature" and hasattr(self.model, "featured"):
            count = queryset.update(featured=True)
            messages.success(request, f"Featured {count} items.")

        elif action == "unfeature" and hasattr(self.model, "featured"):
            count = queryset.update(featured=False)
            messages.success(request, f"Unfeatured {count} items.")

        return redirect(request.path)


class MainAdminDashboardView(AdminAccessMixin, TemplateView):
    """Main admin dashboard with overview statistics."""

    template_name = "admin/main_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import models dynamically to avoid circular imports
        from blog.models import Post, Category, Tag
        from projects.models import SystemModule, Technology, SystemType

        context.update(
            {
                "title": "AURA Admin Dashboard",
                "admin_section": True,
                # Blog/DataLogs stats
                "blog_stats": {
                    "total_posts": Post.objects.count(),
                    "published_posts": Post.objects.filter(status="published").count(),
                    "draft_posts": Post.objects.filter(status="draft").count(),
                    "total_categories": Category.objects.count(),
                    "total_tags": Tag.objects.count(),
                },
                # Projects/Systems stats
                "projects_stats": {
                    "total_systems": SystemModule.objects.count(),
                    "published_systems": SystemModule.objects.filter(
                        status="published"
                    ).count(),
                    "deployed_systems": SystemModule.objects.filter(
                        status="deployed"
                    ).count(),
                    "in_dev_systems": SystemModule.objects.filter(
                        status="in_development"
                    ).count(),
                    "total_technologies": Technology.objects.count(),
                    "total_system_types": SystemType.objects.count(),
                },
                # Recent activity
                "recent_posts": Post.objects.order_by("-created_at")[:5],
                "recent_systems": SystemModule.objects.order_by("-updated_at")[:5],
            }
        )

        return context


# Specialized mixins for common patterns
class SlugAdminCreateView(BaseAdminCreateView):
    """Create view that auto-generates slugs."""

    def form_valid(self, form):
        if not form.instance.slug:
            if hasattr(form.instance, "title"):
                form.instance.slug = slugify(form.instance.title)
            elif hasattr(form.instance, "name"):
                form.instance.slug = slugify(form.instance.name)
        return super().form_valid(form)


class AuthorAdminCreateView(BaseAdminCreateView):
    """Create view that auto-assigns author."""

    def form_valid(self, form):
        if hasattr(form.instance, "author") and not form.instance.author:
            form.instance.author = self.request.user
        return super().form_valid(form)


class StatusAdminCreateView(BaseAdminCreateView):
    """Create view with default status handling."""

    def form_valid(self, form):
        if hasattr(form.instance, "status") and not form.instance.status:
            form.instance.status = "draft"
        return super().form_valid(form)


class AjaxableResponseMixin:
    """Mixin to add AJAX support to any admin view."""

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": f"{self.model._meta.verbose_name} saved successfully!",
                    "redirect_url": self.get_success_url(),
                }
            )
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "errors": form.errors,
                    "message": "Please correct the errors below.",
                }
            )
        return response
