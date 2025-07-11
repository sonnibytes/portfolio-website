"""
Global Admin View Classes for AURA Portfolio - Enhanced w Core Admin Views
Provides consistent base functionality for all app admin interfaces
*NEW* Handles all Core app models CRUD Ops
Version 4.0 - Enpanded Global with Core Model Admin Views
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
from django.utils import timezone
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404, render

from django.http import HttpResponse


from datetime import datetime, timedelta

from .models import CorePage, Skill, Education, EducationSkillDevelopment, Experience, Contact, SocialLink, PortfolioAnalytics
from .forms import CorePageForm, SkillForm, EducationForm, EducationSkillDevelopmentForm, ExperienceForm, ContactForm, SocialLinkForm, PortfolioAnalyticsForm


# ======= BUTTON STYLE TESTING ========
def test_admin_styles(request):
    """Test some admin button styling."""

    basic = [
        {"style": "primary", "text": "Primary", "icon": "fa-database"},
        {"style": "secondary", "text": "Secondary", "icon": "fa-users"},
        {"style": "outline", "text": "Outline", "icon": "fa-chart-simple"},
    ]

    status = [
        {"style": "danger", "text": "Danger", "icon": "fa-skull-crossbones"},
        {"style": "warning", "text": "Warning", "icon": "fa-triangle-exclamation"},
        {"style": "success", "text": "Success", "icon": "fa-fire"},
        {"style": "info", "text": "Info", "icon": "fa-circle-exclamation"},
    ]

    aura = [
        {"style": "teal", "text": "Teal", "icon": "fa-rocket"},
        {"style": "yellow", "text": "Yellow", "icon": "fa-star"},
        {"style": "navy", "text": "Navy", "icon": "fa-microchip"},
        {"style": "lavender", "text": "Lavender", "icon": "fa-brain"},
        {"style": "coral", "text": "Coral", "icon": "fa-sun"},
        {"style": "mint", "text": "Mint", "icon": "fa-leaf"},
        {"style": "gunmetal", "text": "Gunmetal", "icon": "fa-cogs"},
    ]

    colors = [
        {"style": "purple", "text": "Purple", "icon": "fa-route"},
        {"style": "emerald", "text": "Emerald", "icon": "fa-flask"},
        {"style": "orange", "text": "Orange", "icon": "fa-fish"},
        {"style": "blue", "text": "Blue", "icon": "fa-mountain-sun"},
        {"style": "gray", "text": "Gray", "icon": "fa-circle-xmark"},
        {"style": "cyan", "text": "Cyan", "icon": "fa-code-branch"},
        {"style": "red", "text": "Red", "icon": "fa-bullseye"},
    ]

    context = {
        'basic': basic,
        'status': status,
        'aura': aura,
        'colors': colors
    }
    return render(request, "core/admin/test-admin-styles.html", context)



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


# ================== CORE APP MODELS ADMIN VIEWS =============================


class CoreAdminDashboardView(AdminAccessMixin, TemplateView):
    """Core app admin dashboard w comprehensive metrics."""

    template_name = "core/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import models to avoid circular imports
        from blog.models import Post
        from projects.models import SystemModule, Technology

        # Core Page Analytics
        page_stats = {
            'total_pages': CorePage.objects.count(),
            'published_pages': CorePage.objects.filter(is_published=True).count(),
            'draft_pages': CorePage.objects.filter(is_published=False).count(),
        }

        # Skill Analytics
        skill_stats = {
            'total_skills': Skill.objects.count(),
            'featured_skills': Skill.objects.filter(is_featured=True).count(),
            'currently_learning': Skill.objects.filter(is_currently_learning=True).count(),
            'certified_skills': Skill.objects.filter(is_certified=True).count(),
            'avg_proficiency': Skill.objects.aggregate(avg=Avg('proficiency'))['avg'] or 0,
            'skills_with_tech_links': Skill.objects.filter(related_technology__isnull=False).count(),
        }

        # Education Analytics
        education_stats = {
            "total_education": Education.objects.count(),
            "current_education": Education.objects.filter(is_current=True).count(),
            "completed_courses": Education.objects.filter(
                learning_type__in=["online_course", "certification"],
                end_date__isnull=False,
            ).count(),
            "total_learning_hours": Education.objects.aggregate(
                total=Sum("hours_completed")
            )["total"] or 0,
            "avg_career_relevance": Education.objects.aggregate(
                avg=Avg("career_relevance")
            )["avg"] or 0,
        }

        # Experience Analytics
        experience_stats = {
            "total_positions": Experience.objects.count(),
            "current_positions": Experience.objects.filter(is_current=True).count(),
            "total_companies": Experience.objects.values("company").distinct().count(),
            "years_experience": self.calculate_total_experience(),
        }

        # Contact Analytics
        contact_stats = {
            "total_contacts": Contact.objects.count(),
            "unread_contacts": Contact.objects.filter(is_read=False).count(),
            "this_month_contacts": Contact.objects.filter(
                created_at__gte=timezone.now().replace(day=1)
            ).count(),
            "pending_responses": Contact.objects.filter(response_sent=False).count(),
            "high_priority_contacts": Contact.objects.filter(priority="high").count(),
        }

        # Portfolio Analytics
        analytics_stats = {
            "total_analytics_days": PortfolioAnalytics.objects.count(),
            "avg_learning_hours": PortfolioAnalytics.objects.aggregate(
                avg=Avg("learning_hours_logged")
            )["avg"] or 0,
            "total_visitors_month": PortfolioAnalytics.objects.filter(
                date__gte=timezone.now().date().replace(day=1)
            ).aggregate(total=Sum("unique_visitors"))["total"] or 0,
            "last_analytics_date": PortfolioAnalytics.objects.order_by("-date").first(),
        }

        # Cross-app integration stats
        integration_stats = {
            "education_skill_connections": EducationSkillDevelopment.objects.count(),
            "skills_linked_to_projects": Skill.objects.filter(
                developed_in_projects__isnull=False
            )
            .distinct()
            .count(),
            "education_with_projects": Education.objects.filter(
                related_systems__isnull=False
            )
            .distinct()
            .count(),
        }

        context.update(
            {
                "title": "Core Admin Dashboard",
                "app_color": "emerald",
                "page_stats": page_stats,
                "skill_stats": skill_stats,
                "education_stats": education_stats,
                "experience_stats": experience_stats,
                "contact_stats": contact_stats,
                "analytics_stats": analytics_stats,
                "integration_stats": integration_stats,
                "recent_contacts": Contact.objects.order_by("-created_at")[:5],
                "recent_education": Education.objects.order_by("-end_date", "-start_date")[:5],
                "recent_analytics": PortfolioAnalytics.objects.order_by("-date")[:7],
            }
        )

        return context

    def calculate_total_experience(self):
        """Calculate total years of professional experience."""
        total_days = 0
        for exp in Experience.objects.all():
            start_date = exp.start_date
            end_date = exp.end_date or timezone.now().date()
            total_days += (end_date - start_date).days
        return round(total_days / 365.25, 1)


# ===================
# CORE PAGE MANAGEMENT
# ===================


class CorePageListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage static core pages."""

    model = CorePage
    template_name = "core/admin/corepage_list.html"
    context_object_name = "pages"

    def get_queryset(self):
        queryset = CorePage.objects.order_by("title")

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(content__icontains=search_query)
                | Q(meta_description__icontains=search_query)
            )

        # Filter by publication status
        status_filter = self.request.GET.get("status", "")
        if status_filter == "published":
            queryset = queryset.filter(is_published=True)
        elif status_filter == "draft":
            queryset = queryset.filter(is_published=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Core Pages",
                "subtitle": "Static pages like privacy policy, about, etc.",
            }
        )
        return context


class CorePageCreateAdminView(SlugAdminCreateView):
    """Create new core page."""

    model = CorePage
    form_class = CorePageForm
    template_name = "core/admin/corepage_form.html"
    success_url = reverse_lazy("aura_admin:core:corepage_list")


class CorePageUpdateAdminView(BaseAdminUpdateView):
    """Edit existing core page."""

    model = CorePage
    form_class = CorePageForm
    template_name = "core/admin/corepage_form.html"
    success_url = reverse_lazy("aura_admin:core:corepage_list")


class CorePageDeleteAdminView(BaseAdminDeleteView):
    """Delete core page."""

    model = CorePage
    success_url = reverse_lazy("aura_admin:core:corepage_list")


# ===================
# SKILL MANAGEMENT
# ===================


class SkillListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage skills with technology relationships."""

    model = Skill
    template_name = "core/admin/skill_list.html"
    context_object_name = "skills"

    def get_queryset(self):
        queryset = Skill.objects.select_related("related_technology").order_by(
            "category", "display_order"
        )

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Filter by category
        category_filter = self.request.GET.get("category", "")
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        # Filter by proficiency level
        proficiency_filter = self.request.GET.get("proficiency", "")
        if proficiency_filter:
            queryset = queryset.filter(proficiency=int(proficiency_filter))

        # Filter by learning status
        learning_filter = self.request.GET.get("learning_status", "")
        if learning_filter == "currently_learning":
            queryset = queryset.filter(is_currently_learning=True)
        elif learning_filter == "featured":
            queryset = queryset.filter(is_featured=True)
        elif learning_filter == "certified":
            queryset = queryset.filter(is_certified=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Skills",
                "subtitle": "Technical skills and learning progression",
                "skill_categories": Skill.CATEGORY_CHOICES,
                "proficiency_levels": [(i, i) for i in range(1, 6)],
                "featured": Skill.objects.filter(is_featured=True).count(),
                "is_learning": Skill.objects.filter(is_currently_learning=True).count(),
                "certified": Skill.objects.filter(is_certified=True).count(),
            }
        )
        return context


class SkillCreateAdminView(SlugAdminCreateView):
    """Create new skill."""

    model = Skill
    form_class = SkillForm
    template_name = "core/admin/skill_form.html"
    success_url = reverse_lazy("aura_admin:core:skill_list")


class SkillUpdateAdminView(BaseAdminUpdateView):
    """Edit existing skill."""

    model = Skill
    form_class = SkillForm
    template_name = "core/admin/skill_form.html"
    success_url = reverse_lazy("aura_admin:core:skill_list")


class SkillDeleteAdminView(BaseAdminDeleteView):
    """Delete skill."""

    model = Skill
    success_url = reverse_lazy("aura_admin:core:skill_list")


# ===================
# EDUCATION MANAGEMENT
# ===================


class EducationListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage education entries with skill connections."""

    model = Education
    template_name = "core/admin/education_list.html"
    context_object_name = "education_entries"

    def get_queryset(self):
        queryset = Education.objects.prefetch_related("skills_learned").order_by(
            "-start_date"
        )

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(institution__icontains=search_query)
                | Q(degree__icontains=search_query)
                | Q(field_of_study__icontains=search_query)
                | Q(platform__icontains=search_query)
            )

        # Filter by learning type
        type_filter = self.request.GET.get("learning_type", "")
        if type_filter:
            queryset = queryset.filter(learning_type=type_filter)

        # Filter by status
        status_filter = self.request.GET.get("status", "")
        if status_filter == "current":
            queryset = queryset.filter(is_current=True)
        elif status_filter == "completed":
            queryset = queryset.filter(is_current=False, end_date__isnull=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Education",
                "subtitle": "Learning history and skill development",
                "learning_types": Education._meta.get_field("learning_type").choices,
                "current": Education.objects.filter(is_current=True).count(),
                "certified": Education.objects.filter(certificate_url__isnull=False).count(),
                "hours_completed": Education.objects.aggregate(hours=Sum('hours_completed'))['hours'] or 0,
            }
        )
        return context


class EducationCreateAdminView(SlugAdminCreateView):
    """Create new education entry."""

    model = Education
    form_class = EducationForm
    template_name = "core/admin/education_form.html"
    success_url = reverse_lazy("aura_admin:core:education_list")


class EducationUpdateAdminView(BaseAdminUpdateView):
    """Edit existing education entry."""

    model = Education
    form_class = EducationForm
    template_name = "core/admin/education_form.html"
    success_url = reverse_lazy("aura_admin:core:education_list")


class EducationDeleteAdminView(BaseAdminDeleteView):
    """Delete education entry."""

    model = Education
    success_url = reverse_lazy("aura_admin:core:education_list")


# ===================
# EDUCATION-SKILL DEVELOPMENT MANAGEMENT
# ===================


class EducationSkillListAdminView(BaseAdminListView):
    """Manage education-skill development connections."""

    model = EducationSkillDevelopment
    template_name = "core/admin/education_skill_list.html"
    context_object_name = "skill_developments"

    def get_queryset(self):
        return EducationSkillDevelopment.objects.select_related(
            "education", "skill"
        ).order_by("-education__start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Education-Skill Connections",
                "subtitle": "Skill development through education",
            }
        )
        return context


class EducationSkillCreateAdminView(BaseAdminCreateView):
    """Create new education-skill connection."""

    model = EducationSkillDevelopment
    form_class = EducationSkillDevelopmentForm
    template_name = "core/admin/education_skill_form.html"
    success_url = reverse_lazy("aura_admin:core:education_skill_list")


class EducationSkillUpdateAdminView(BaseAdminUpdateView):
    """Edit education-skill connection."""

    model = EducationSkillDevelopment
    form_class = EducationSkillDevelopmentForm
    template_name = "core/admin/education_skill_form.html"
    success_url = reverse_lazy("aura_admin:core:education_skill_list")


class EducationSkillDeleteAdminView(BaseAdminDeleteView):
    """Delete education-skill connection."""

    model = EducationSkillDevelopment
    success_url = reverse_lazy("aura_admin:core:education_skill_list")


# ===================
# EXPERIENCE MANAGEMENT
# ===================


class ExperienceListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage work experience entries."""

    model = Experience
    template_name = "core/admin/experience_list.html"
    context_object_name = "experiences"

    def get_queryset(self):
        queryset = Experience.objects.order_by("-start_date")

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(position__icontains=search_query)
                | Q(company__icontains=search_query)
                | Q(location__icontains=search_query)
                | Q(technologies__icontains=search_query)
            )

        # Filter by status
        status_filter = self.request.GET.get("status", "")
        if status_filter == "current":
            queryset = queryset.filter(is_current=True)
        elif status_filter == "past":
            queryset = queryset.filter(is_current=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Experience",
                "subtitle": "Work history and professional experience",
            }
        )
        return context


class ExperienceCreateAdminView(SlugAdminCreateView):
    """Create new experience entry."""

    model = Experience
    form_class = ExperienceForm
    template_name = "core/admin/experience_form.html"
    success_url = reverse_lazy("aura_admin:core:experience_list")


class ExperienceUpdateAdminView(BaseAdminUpdateView):
    """Edit existing experience."""

    model = Experience
    form_class = ExperienceForm
    template_name = "core/admin/experience_form.html"
    success_url = reverse_lazy("aura_admin:core:experience_list")


class ExperienceDeleteAdminView(BaseAdminDeleteView):
    """Delete experience entry."""

    model = Experience
    success_url = reverse_lazy("aura_admin:core:experience_list")


# ===================
# CONTACT MANAGEMENT
# ===================


class ContactListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage contact form submissions."""

    model = Contact
    template_name = "core/admin/contact_list.html"
    context_object_name = "contacts"

    def get_queryset(self):
        queryset = Contact.objects.order_by("-created_at")

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(subject__icontains=search_query)
            )

        # Filter by read status
        read_filter = self.request.GET.get("read_status", "")
        if read_filter == "unread":
            queryset = queryset.filter(is_read=False)
        elif read_filter == "read":
            queryset = queryset.filter(is_read=True)

        # Filter by inquiry category
        category_filter = self.request.GET.get("category", "")
        if category_filter:
            queryset = queryset.filter(inquiry_category=category_filter)

        # Filter by priority
        priority_filter = self.request.GET.get("priority", "")
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Contacts",
                "subtitle": "Portfolio contact submissions",
                "inquiry_categories": Contact._meta.get_field(
                    "inquiry_category"
                ).choices,
                "priority_levels": Contact._meta.get_field("priority").choices,
                "unread_count": Contact.objects.filter(is_read=False).count(),
            }
        )
        return context


class ContactCreateAdminView(BaseAdminCreateView):
    """Create new contact (admin use)."""

    model = Contact
    form_class = ContactForm
    template_name = "core/admin/contact_form.html"
    success_url = reverse_lazy("aura_admin:core:contact_list")


class ContactUpdateAdminView(BaseAdminUpdateView):
    """Edit existing contact."""

    model = Contact
    form_class = ContactForm
    template_name = "core/admin/contact_form.html"
    success_url = reverse_lazy("aura_admin:core:contact_list")


class ContactDeleteAdminView(BaseAdminDeleteView):
    """Delete contact."""

    model = Contact
    success_url = reverse_lazy("aura_admin:core:contact_list")


# ===================
# SOCIAL LINK MANAGEMENT
# ===================


class SocialLinkListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage social media links."""

    model = SocialLink
    template_name = "core/admin/sociallink_list.html"
    context_object_name = "social_links"

    def get_queryset(self):
        return SocialLink.objects.order_by("display_order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Social Links",
                "subtitle": "Social media and external profile links",
            }
        )
        return context


class SocialLinkCreateAdminView(BaseAdminCreateView):
    """Create new social link."""

    model = SocialLink
    form_class = SocialLinkForm
    template_name = "core/admin/sociallink_form.html"
    success_url = reverse_lazy("aura_admin:core:sociallink_list")


class SocialLinkUpdateAdminView(BaseAdminUpdateView):
    """Edit existing social link."""

    model = SocialLink
    form_class = SocialLinkForm
    template_name = "core/admin/sociallink_form.html"
    success_url = reverse_lazy("aura_admin:core:sociallink_list")


class SocialLinkDeleteAdminView(BaseAdminDeleteView):
    """Delete social link."""

    model = SocialLink
    success_url = reverse_lazy("aura_admin:core:sociallink_list")


# ===================
# PORTFOLIO ANALYTICS MANAGEMENT
# ===================


class PortfolioAnalyticsListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage portfolio analytics entries."""

    model = PortfolioAnalytics
    template_name = "core/admin/analytics_list.html"
    context_object_name = "analytics"

    def get_queryset(self):
        queryset = PortfolioAnalytics.objects.select_related(
            "top_datalog", "top_system"
        ).order_by("-date")

        # Filter by date range
        date_filter = self.request.GET.get("date_range", "")
        if date_filter == "week":
            queryset = queryset.filter(
                date__gte=timezone.now().date() - timedelta(days=7)
            )
        elif date_filter == "month":
            queryset = queryset.filter(
                date__gte=timezone.now().date() - timedelta(days=30)
            )
        elif date_filter == "quarter":
            queryset = queryset.filter(
                date__gte=timezone.now().date() - timedelta(days=90)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate summary statistics
        recent_analytics = PortfolioAnalytics.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        )

        context.update(
            {
                "title": "Portfolio Analytics",
                "subtitle": "Learning metrics and portfolio performance",
                "summary_stats": {
                    "avg_learning_hours": recent_analytics.aggregate(
                        avg=Avg("learning_hours_logged")
                    )["avg"]
                    or 0,
                    "total_visitors": recent_analytics.aggregate(
                        total=Sum("unique_visitors")
                    )["total"]
                    or 0,
                    "total_resume_downloads": recent_analytics.aggregate(
                        total=Sum("resume_downloads")
                    )["total"]
                    or 0,
                },
            }
        )
        return context


class PortfolioAnalyticsCreateAdminView(BaseAdminCreateView):
    """Create new analytics entry."""

    model = PortfolioAnalytics
    form_class = PortfolioAnalyticsForm
    template_name = "core/admin/analytics_form.html"
    success_url = reverse_lazy("aura_admin:core:analytics_list")


class PortfolioAnalyticsUpdateAdminView(BaseAdminUpdateView):
    """Edit existing analytics entry."""

    model = PortfolioAnalytics
    form_class = PortfolioAnalyticsForm
    template_name = "core/admin/analytics_form.html"
    success_url = reverse_lazy("aura_admin:core:analytics_list")


class PortfolioAnalyticsDeleteAdminView(BaseAdminDeleteView):
    """Delete analytics entry."""

    model = PortfolioAnalytics
    success_url = reverse_lazy("aura_admin:core:analytics_list")


# ===================
# AJAX VIEWS FOR ENHANCED FUNCTIONALITY
# ===================


class ContactMarkReadView(AdminAccessMixin, TemplateView):
    """AJAX view to mark contact as read."""

    def post(self, request, *args, **kwargs):
        contact = get_object_or_404(Contact, pk=kwargs["pk"])
        contact.is_read = True
        contact.save()

        return JsonResponse(
            {"success": True, "message": f"Marked contact from {contact.name} as read"}
        )


class ContactMarkResponseSentView(AdminAccessMixin, TemplateView):
    """AJAX view to mark contact response as sent."""

    def post(self, request, *args, **kwargs):
        contact = get_object_or_404(Contact, pk=kwargs["pk"])
        contact.mark_as_responded()

        return JsonResponse(
            {
                "success": True,
                "message": f"Marked response sent to {contact.name}",
                "response_date": contact.response_date.strftime("%Y-%m-%d %H:%M"),
            }
        )


class SkillToggleFeaturedView(AdminAccessMixin, TemplateView):
    """AJAX view to toggle skill featured status."""

    def post(self, request, *args, **kwargs):
        skill = get_object_or_404(Skill, pk=kwargs["pk"])
        skill.is_featured = not skill.is_featured
        skill.save()

        return JsonResponse(
            {
                "success": True,
                "featured": skill.is_featured,
                "message": f"{'Featured' if skill.is_featured else 'Unfeatured'} {skill.name}",
            }
        )


class SkillToggleLearningView(AdminAccessMixin, TemplateView):
    """AJAX view to toggle skill learning status."""

    def post(self, request, *args, **kwargs):
        skill = get_object_or_404(Skill, pk=kwargs["pk"])
        skill.is_currently_learning = not skill.is_currently_learning
        skill.save()

        return JsonResponse(
            {
                "success": True,
                "learning": skill.is_currently_learning,
                "message": f"{'Now learning' if skill.is_currently_learning else 'Not learning'} {skill.name}",
            }
        )


class AnalyticsChartDataView(AdminAccessMixin, TemplateView):
    """AJAX view to provide chart data for analytics dashboard."""

    def get(self, request, *args, **kwargs):
        days = int(request.GET.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        analytics = PortfolioAnalytics.objects.filter(date__gte=start_date).order_by(
            "date"
        )

        chart_data = {
            "labels": [a.date.strftime("%Y-%m-%d") for a in analytics],
            "learning_hours": [float(a.learning_hours_logged) for a in analytics],
            "unique_visitors": [a.unique_visitors for a in analytics],
            "resume_downloads": [a.resume_downloads for a in analytics],
            "contact_submissions": [a.contact_form_submissions for a in analytics],
        }

        return JsonResponse(chart_data)
