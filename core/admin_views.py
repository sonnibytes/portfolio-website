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
    DetailView,
    View
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

from .models import CorePage, Skill, Education, EducationSkillDevelopment, Experience, Contact, SocialLink, PortfolioAnalytics, SkillTechnologyRelation
from .forms import CorePageForm, SkillForm, EducationForm, EducationSkillDevelopmentForm, ExperienceForm, ContactForm, SocialLinkForm, PortfolioAnalyticsForm, SkillTechnologyRelationForm
from projects.models import ArchitectureComponent, ArchitectureConnection, SystemModule, Technology
from blog.models import Post, Category

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

        # ADD ARCHITECTURE STATISTICS
        context['architecture_stats'] = {
            'total_components': ArchitectureComponent.objects.count(),
            'systems_with_architecture': SystemModule.objects.filter(
                architecture_components__isnull=False
            ).distinct().count(),
            'total_connections': ArchitectureConnection.objects.count(),
            'core_components': ArchitectureComponent.objects.filter(is_core=True).count(),
        }
        
        # Systems that need architecture diagrams
        context['systems_without_architecture'] = SystemModule.objects.filter(
            architecture_components__isnull=True,
            status__in=['deployed', 'published', 'in_development', 'testing']
        ).exclude(status__in=['draft', 'archived']).order_by('-updated_at')[:6]

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
            # "avg_career_relevance": Education.objects.aggregate(
            #     avg=Avg("career_relevance")
            # )["avg"] or 0,
            "formal_education": Education.objects.filter(
                learning_type__in=['degree', 'bootcamp']
            ).count(),
        }

        # Experience Analytics
        experience_stats = {
            "years_experience": self.calculate_total_experience(),
            "total_companies": Experience.objects.values('company').distinct().count(),
            "current_positions": Experience.objects.filter(is_current=True).count(),
            "unique_industries": 4,  # Placeholder for now
            # TODO: Enhance Experience model w industry?
            # "unique_industries": Experience.objects.values('industry').distinct().count(),
        }

        # Contact Analytics
        contact_stats = {
            "total_contacts": Contact.objects.count(),
            "unread_contacts": Contact.objects.filter(is_read=False).count(),
            "this_month_contacts": Contact.objects.filter(
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).count(),
            "pending_responses": Contact.objects.filter(is_read=True, response_sent=False).count(),
            "high_priority_contacts": Contact.objects.filter(priority="high").count(),
        }

        # NEW: Social Links Analytics
        social_stats = {
            "total_social_links": SocialLink.objects.count(),
            "professional_links": SocialLink.objects.filter(category='professional').count(),
            "community_links": SocialLink.objects.filter(category='community').count(),
            "media_links": SocialLink.objects.filter(category='media').count(),
            "chat_links": SocialLink.objects.filter(category='chat').count(),
            "blog_links": SocialLink.objects.filter(category='blog').count(),
            "other_links": SocialLink.objects.filter(category='other').count(),
            # Category breakdown for dashboard display
            "category_breakdown": {
                category[0]: SocialLink.objects.filter(category=category[0]).count()
                for category in SocialLink.CATEGORY_CHOICES
            }
        }

        # Portfolio Analytics
        # analytics_stats = {
        #     "total_analytics_days": PortfolioAnalytics.objects.count(),
        #     "avg_learning_hours": PortfolioAnalytics.objects.aggregate(
        #         avg=Avg("learning_hours_logged")
        #     )["avg"] or 0,
        #     "total_visitors_month": PortfolioAnalytics.objects.filter(
        #         date__gte=timezone.now().date().replace(day=1)
        #     ).aggregate(total=Sum("unique_visitors"))["total"] or 0,
        #     "last_analytics_date": PortfolioAnalytics.objects.order_by("-date").first(),
        # }

        # Cross-app integration stats
        integration_stats = {
            "education_skill_connections": EducationSkillDevelopment.objects.count(),
            "skills_linked_to_projects": Skill.objects.filter(
                related_technology__systems__isnull=False
            ).distinct().count(),
            # "education_with_projects": Education.objects.filter(
            #     related_systems__isnull=False
            # )
            # .distinct()
            # .count(),
            "total_skill_tech_relations": SkillTechnologyRelation.objects.count(),
        }

        # Recent Analytics (Portfolio Analytics) - replacing analytics above
        recent_analytics = PortfolioAnalytics.objects.order_by('-date')[:7]

        context.update(
            {
                "title": "Core Admin Dashboard",
                "app_color": "emerald",
                "page_stats": page_stats,
                "skill_stats": skill_stats,
                "education_stats": education_stats,
                "experience_stats": experience_stats,
                "contact_stats": contact_stats,
                "social_stats": social_stats,
                "recent_analytics": recent_analytics,
                # "analytics_stats": analytics_stats,
                "integration_stats": integration_stats,
                # "recent_contacts": Contact.objects.order_by("-created_at")[:5],
                # "recent_education": Education.objects.order_by("-end_date", "-start_date")[:5],
                # "recent_analytics": PortfolioAnalytics.objects.order_by("-date")[:7],

                # Meta information
                'dashboard_title': 'Core System Management',
                'dashboard_subtitle': 'Portfolio foundation, skills, and learning journey administration',
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
    success_url = reverse_lazy("aura_admin:corepage_list")


class CorePageUpdateAdminView(BaseAdminUpdateView):
    """Edit existing core page."""

    model = CorePage
    form_class = CorePageForm
    template_name = "core/admin/corepage_form.html"
    success_url = reverse_lazy("aura_admin:corepage_list")


class CorePageDeleteAdminView(BaseAdminDeleteView):
    """Delete core page."""

    model = CorePage
    success_url = reverse_lazy("aura_admin:corepage_list")


# ===================
# SKILL MANAGEMENT
# ===================


class SkillListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage skills with technology relationships."""

    model = Skill
    template_name = "core/admin/skill_list.html"
    context_object_name = "skills"

    def get_queryset(self):
        queryset = Skill.objects.prefetch_related('related_technologies').order_by(
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
                # NEW: Technology relationship stats
                'skills_with_tech': Skill.objects.filter(
                    related_technologies__isnull=False
                ).distinct().count(),
                'total_tech_relationships': SkillTechnologyRelation.objects.count(),
            }
        )
        return context


class SkillCreateAdminView(SlugAdminCreateView):
    """Create new skill."""

    model = Skill
    form_class = SkillForm
    template_name = "core/admin/skill_form.html"
    success_url = reverse_lazy("aura_admin:skill_list")

    # ADD THIS METHOD FOR DEBUGGING:
    def form_valid(self, form):
        """Debug the form submission."""
        print(f"🟢 FORM IS VALID")
        print(f"🟢 Form cleaned_data: {form.cleaned_data}")
        
        try:
            # Call the parent form_valid which should save the object
            response = super().form_valid(form)
            print(f"🟢 Object created successfully: {self.object}")
            print(f"🟢 Object ID: {self.object.pk}")
            print(f"🟢 Redirecting to: {self.get_success_url()}")
            return response
        except Exception as e:
            print(f"🔴 ERROR in form_valid: {e}")
            import traceback
            traceback.print_exc()
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Debug form validation errors."""
        print(f"🔴 FORM IS INVALID")
        print(f"🔴 Form errors: {form.errors}")
        print(f"🔴 Form non_field_errors: {form.non_field_errors}")
        return super().form_invalid(form)
    
    def post(self, request, *args, **kwargs):
        """Debug the entire POST process."""
        print(f"🔵 POST request received")
        print(f"🔵 POST data: {request.POST}")
        return super().post(request, *args, **kwargs)


class SkillUpdateAdminView(BaseAdminUpdateView):
    """Edit existing skill."""

    model = Skill
    form_class = SkillForm
    template_name = "core/admin/skill_form.html"
    success_url = reverse_lazy("aura_admin:skill_list")


class SkillDeleteAdminView(BaseAdminDeleteView):
    """Delete skill."""

    model = Skill
    success_url = reverse_lazy("aura_admin:skill_list")


# ========== NEW: SKILL-TECHNOLOGY RELATIONSHIP VIEWS ==========

class SkillTechnologyRelationListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage skill-technology relationships."""

    model = SkillTechnologyRelation
    template_name = "core/admin/skill_technology_relation_list.html"
    context_object_name = "relationships"

    def get_queryset(self):
        queryset = SkillTechnologyRelation.objects.select_related(
            'skill', 'technology'
        ).order_by('skill__category', 'skill__name', '-strength')

        # Filter by skill
        skill_filter = self.request.GET.get('skill', '')
        if skill_filter:
            queryset = queryset.filter(skill__slug=skill_filter)
        
        # Filter by technology
        tech_filter = self.request.GET.get('technology', '')
        if tech_filter:
            queryset = queryset.filter(technology__slug=tech_filter)
        
        # Filter by strength
        strength_filter = self.request.GET.get('strength', '')
        if strength_filter:
            queryset = queryset.filter(strength=int(strength_filter))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Skill-Technology Relationships',
            'subtitle': 'Manage connections between skills and technologies',
            'skills': Skill.objects.all().order_by('name'),
            'technologies': Technology.objects.all().order_by('name'),
            'strength_choices': SkillTechnologyRelation.RELATIONSHIP_STRENGTH,
            'relationship_stats': self.get_relationship_stats(),
        })
        return context
    
    def get_relationship_stats(self):
        """Get stats for the dashboard"""
        relationships = SkillTechnologyRelation.objects.all()
        return {
            'total_relationships': relationships.count(),
            'primary_relationships': relationships.filter(strength=4).count(),
            'essential_relationships': relationships.filter(strength=3).count(),
            'skills_with_tech': Skill.objects.filter(
                related_technologies__isnull=False
            ).distinct().count(),
            'technologies_with_skills': Technology.objects.filter(
                related_skills__isnull=False
            ).distinct().count(),
        }


class SkillTechnologyRelationCreateAdminView(BaseAdminCreateView):
    """Create a new skill-technology relationship."""

    model = SkillTechnologyRelation
    form_class = SkillTechnologyRelationForm
    template_name = "core/admin/skill_technology_relation_form.html"
    success_url = reverse_lazy("aura_admin:skill_tech_relation_list")


class SkillTechnologyRelationUpdateAdminView(BaseAdminUpdateView):
    """Edit existing skill-technology relationship."""

    model = SkillTechnologyRelation
    form_class = SkillTechnologyRelationForm
    template_name = "core/admin/skill_technology_relation_form.html"
    success_url = reverse_lazy("aura_admin:skill_tech_relation_list")


class SkillTechnologyRelationDeleteAdminView(BaseAdminDeleteView):
    """Delete skill-technology relationship."""

    model = SkillTechnologyRelation
    success_url = reverse_lazy("aura_admin:skill_tech_relation_list")


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
    success_url = reverse_lazy("aura_admin:education_list")


class EducationUpdateAdminView(BaseAdminUpdateView):
    """Edit existing education entry."""

    model = Education
    form_class = EducationForm
    template_name = "core/admin/education_form.html"
    success_url = reverse_lazy("aura_admin:education_list")


class EducationDeleteAdminView(BaseAdminDeleteView):
    """Delete education entry."""

    model = Education
    success_url = reverse_lazy("aura_admin:education_list")


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
    success_url = reverse_lazy("aura_admin:education_skill_list")


class EducationSkillUpdateAdminView(BaseAdminUpdateView):
    """Edit education-skill connection."""

    model = EducationSkillDevelopment
    form_class = EducationSkillDevelopmentForm
    template_name = "core/admin/education_skill_form.html"
    success_url = reverse_lazy("aura_admin:education_skill_list")


class EducationSkillDeleteAdminView(BaseAdminDeleteView):
    """Delete education-skill connection."""

    model = EducationSkillDevelopment
    success_url = reverse_lazy("aura_admin:education_skill_list")


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
    success_url = reverse_lazy("aura_admin:experience_list")


class ExperienceUpdateAdminView(BaseAdminUpdateView):
    """Edit existing experience."""

    model = Experience
    form_class = ExperienceForm
    template_name = "core/admin/experience_form.html"
    success_url = reverse_lazy("aura_admin:experience_list")


class ExperienceDeleteAdminView(BaseAdminDeleteView):
    """Delete experience entry."""

    model = Experience
    success_url = reverse_lazy("aura_admin:experience_list")


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
    success_url = reverse_lazy("aura_admin:contact_list")


class ContactUpdateAdminView(BaseAdminUpdateView):
    """Edit existing contact."""

    model = Contact
    form_class = ContactForm
    template_name = "core/admin/contact_form.html"
    success_url = reverse_lazy("aura_admin:contact_list")


class ContactDeleteAdminView(BaseAdminDeleteView):
    """Delete contact."""

    model = Contact
    success_url = reverse_lazy("aura_admin:contact_list")


# ===================
# SOCIAL LINK MANAGEMENT
# ===================


class SocialLinkListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage social media links."""

    model = SocialLink
    template_name = "core/admin/sociallink_list.html"
    context_object_name = "social_links"

    def get_queryset(self):
        queryset = SocialLink.objects.order_by("display_order")

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(url__icontains=search_query) |
                Q(handle__icontains=search_query)
            )
        
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Manage Social Links",
                "subtitle": "Social media and external profile links",
                "category_choices": SocialLink.CATEGORY_CHOICES,
                "categories_count": self.get_sociallink_categories(),
                "current_filters": {
                    'search': self.request.GET.get('search', ''),
                    'category': self.request.GET.get('category', ''),
                }
            }
        )
        return context
    
    def get_sociallink_categories(self):
        """Get SocialLinks grouped by category"""
        links = SocialLink.objects.all()

        categories = {}
        for l in links:
            link_cat = l.category
            if link_cat not in categories:
                categories[link_cat] = []
            categories[link_cat].append(l)
        
        return categories


class SocialLinkCreateAdminView(BaseAdminCreateView):
    """Create new social link."""

    model = SocialLink
    form_class = SocialLinkForm
    template_name = "core/admin/sociallink_form.html"
    success_url = reverse_lazy("aura_admin:sociallink_list")


class SocialLinkUpdateAdminView(BaseAdminUpdateView):
    """Edit existing social link."""

    model = SocialLink
    form_class = SocialLinkForm
    template_name = "core/admin/sociallink_form.html"
    success_url = reverse_lazy("aura_admin:sociallink_list")


class SocialLinkDeleteAdminView(BaseAdminDeleteView):
    """Delete social link."""

    model = SocialLink
    success_url = reverse_lazy("aura_admin:sociallink_list")


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
    success_url = reverse_lazy("aura_admin:analytics_list")


class PortfolioAnalyticsUpdateAdminView(BaseAdminUpdateView):
    """Edit existing analytics entry."""

    model = PortfolioAnalytics
    form_class = PortfolioAnalyticsForm
    template_name = "core/admin/analytics_form.html"
    success_url = reverse_lazy("aura_admin:analytics_list")


class PortfolioAnalyticsDeleteAdminView(BaseAdminDeleteView):
    """Delete analytics entry."""

    model = PortfolioAnalytics
    success_url = reverse_lazy("aura_admin:analytics_list")


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

# ========= INTEGRATION - REWORK ===========

class ProfessionalDevelopmentDashboardView(AdminAccessMixin, TemplateView):
    """Enhanced Professional Development Command Center Dashboard"""

    template_name = 'core/admin/professional_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import models to avoid circular imports
        from blog.models import Post, Category
        from projects.models import SystemModule, Technology

        # ===== CORE STATISTICS =====
        
        # Education Statistics
        education_stats = {
            'total_education': Education.objects.count(),
            'current_education': Education.objects.filter(is_current=True).count(),
            'completed_courses': Education.objects.filter(
                learning_type__in=['online_course', 'certification'],
                end_date__isnull=False,
            ).count(),
            'formal_education': Education.objects.filter(
                learning_type__in=['degree', 'bootcamp']
            ).count(),
            'total_learning_hours': Education.objects.aggregate(
                total=Sum('hours_completed')
            )['total'] or 0,
            'recent_completions': Education.objects.filter(
                end_date__gte=timezone.now() - timedelta(days=90),
                end_date__isnull=False
            ).count(),
        }
        
        # Skill Statistics  
        skill_stats = {
            'total_skills': Skill.objects.count(),
            'featured_skills': Skill.objects.filter(is_featured=True).count(),
            'currently_learning': Skill.objects.filter(is_currently_learning=True).count(),
            'certified_skills': Skill.objects.filter(is_certified=True).count(),
            'avg_proficiency': Skill.objects.aggregate(avg=Avg('proficiency'))['avg'] or 0,
            'high_proficiency': Skill.objects.filter(proficiency__gte=4).count(),
            'skills_with_tech_links': Skill.objects.filter(
                technology_relations__isnull=False
            ).distinct().count(),
        }
        
        # System/Projects Statistics
        system_stats = {
            'total_systems': SystemModule.objects.count(),
            'deployed_systems': SystemModule.objects.filter(status='deployed').count(),
            'in_development': SystemModule.objects.filter(status='in_development').count(),
            'total_technologies': Technology.objects.count(),
            'technologies_in_use': Technology.objects.filter(
                systems__isnull=False
            ).distinct().count(),
        }
        
        # ===== INTEGRATION ANALYTICS =====
        
        # Cross-app relationship counts
        integration_stats = {
            'skill_tech_relations': SkillTechnologyRelation.objects.count(),
            'education_skill_connections': EducationSkillDevelopment.objects.count(),
            'total_connections': (
                SkillTechnologyRelation.objects.count() + 
                EducationSkillDevelopment.objects.count()
            ),
            
            # Skills applied in projects (via shared technologies)
            'skills_in_projects': Skill.objects.filter(
                technology_relations__technology__systems__isnull=False
            ).distinct().count(),
            
            # Learning documented in blog
            'documented_learning': Post.objects.filter(
                related_systems__isnull=False
            ).distinct().count(),
            
            # Education that led to skills
            'education_with_skills': Education.objects.filter(
                skills_learned__isnull=False
            ).distinct().count(),
            
            # Technologies with skill connections
            'technologies_with_skills': Technology.objects.filter(
                skill_relations__isnull=False
            ).distinct().count(),
        }
        
        # ===== FEATURED CONTENT =====
        
        # Featured skills for demonstration
        featured_skills = Skill.objects.filter(
            is_featured=True
        ).prefetch_related('technology_relations__technology')[:6]
        
        # If no featured skills, get highest proficiency
        if not featured_skills.exists():
            featured_skills = Skill.objects.filter(
                proficiency__gte=3
            ).prefetch_related('technology_relations__technology').order_by('-proficiency')[:6]
        
        # Skills with technology connections for matrix preview
        skills_with_tech = Skill.objects.filter(
            technology_relations__isnull=False
        ).prefetch_related('technology_relations__technology').order_by('-proficiency')[:8]
        
        # ===== RECENT ACTIVITY TIMELINE =====
        
        recent_activities = []
        
        # Recent education completions
        recent_education = Education.objects.filter(
            end_date__gte=timezone.now() - timedelta(days=180),
            end_date__isnull=False
        ).order_by('-end_date')[:3]
        
        for edu in recent_education:
            recent_activities.append({
                'date': edu.end_date,
                'type': 'education',
                'icon': 'graduation-cap',
                'title': f'Completed {edu.degree}',
                'source': edu.institution,
                'category': 'Learning'
            })
        
        # Recent skill additions
        recent_skills = Skill.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=90)
        ).order_by('-created_at')[:3]
        
        for skill in recent_skills:
            recent_activities.append({
                'date': skill.created_at.date(),
                'type': 'skill',
                'icon': 'brain',
                'title': f'Added {skill.name} skill',
                'source': f'Level {skill.proficiency}',
                'category': 'Development'
            })
        
        # Recent project deployments
        recent_projects = SystemModule.objects.filter(
            status='deployed',
            updated_at__gte=timezone.now() - timedelta(days=120)
        ).order_by('-updated_at')[:3]
        
        for project in recent_projects:
            recent_activities.append({
                'date': project.updated_at.date(),
                'type': 'project',
                'icon': 'rocket',
                'title': f'Deployed {project.title}',
                'source': 'Project Application',
                'category': 'Application'
            })
        
        # Recent blog posts about learning
        recent_posts = Post.objects.filter(
            status='published',
            published_date__gte=timezone.now() - timedelta(days=60)
        ).order_by('-published_date')[:2]
        
        for post in recent_posts:
            recent_activities.append({
                'date': post.published_date.date() if post.published_date else post.created_at.date(),
                'type': 'blog',
                'icon': 'file-alt',
                'title': f'Documented: {post.title[:30]}...',
                'source': 'Learning Blog',
                'category': 'Documentation'
            })
        
        # Sort activities by date (most recent first)
        recent_activities.sort(key=lambda x: x['date'], reverse=True)
        recent_activities = recent_activities[:8]  # Limit to 8 most recent
        
        # ===== GROWTH METRICS =====
        
        # Calculate learning velocity (skills/education added per month)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        
        growth_metrics = {
            'skills_this_month': Skill.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'skills_last_month': Skill.objects.filter(
                created_at__gte=sixty_days_ago,
                created_at__lt=thirty_days_ago
            ).count(),
            'education_this_month': Education.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'projects_this_month': SystemModule.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
        }
        
        # ===== SUGGESTED ACTIONS =====
        
        suggested_actions = []
        
        # Skills without technology connections
        skills_without_tech = Skill.objects.filter(
            technology_relations__isnull=True
        ).count()
        
        if skills_without_tech > 0:
            suggested_actions.append({
                'type': 'skill_tech_connection',
                'title': f'Connect {skills_without_tech} skills to technologies',
                'priority': 'high',
                'url': reverse_lazy('aura_admin:skill_tech_relation_list')
            })
        
        # Education without skill connections
        education_without_skills = Education.objects.filter(
            skill_developments__isnull=True
        ).count()
        
        if education_without_skills > 0:
            suggested_actions.append({
                'type': 'education_skill_connection', 
                'title': f'Link {education_without_skills} education items to skills',
                'priority': 'medium',
                'url': reverse_lazy('aura_admin:education_skill_list')
            })
        
        # High proficiency skills without projects
        expert_skills = Skill.objects.filter(
            proficiency__gte=4,
            technology_relations__technology__systemmodule__isnull=True
        ).distinct()
        
        if expert_skills.exists():
            suggested_actions.append({
                'type': 'skill_demonstration',
                'title': f'Create projects for {expert_skills.count()} expert-level skills',
                'priority': 'high',
                'url': reverse_lazy('aura_admin:projects:system_create')
            })
        
        # ===== PORTFOLIO READINESS SCORE =====
        
        # Calculate overall portfolio readiness based on integrations
        portfolio_score = 0
        max_score = 100
        
        # Skills documented (20 points)
        if skill_stats['total_skills'] > 0:
            portfolio_score += min(20, skill_stats['total_skills'] * 2)
        
        # Skills connected to technologies (25 points)  
        if integration_stats['skill_tech_relations'] > 0:
            portfolio_score += min(25, integration_stats['skill_tech_relations'] * 2)
        
        # Skills applied in projects (25 points)
        if integration_stats['skills_in_projects'] > 0:
            portfolio_score += min(25, integration_stats['skills_in_projects'] * 3)
        
        # Learning documented (15 points)
        if integration_stats['documented_learning'] > 0:
            portfolio_score += min(15, integration_stats['documented_learning'] * 2)
        
        # Education linked to skills (15 points)
        if integration_stats['education_skill_connections'] > 0:
            portfolio_score += min(15, integration_stats['education_skill_connections'])
        
        portfolio_readiness = {
            'score': min(portfolio_score, max_score),
            'level': 'Excellent' if portfolio_score >= 80 else 
                    'Good' if portfolio_score >= 60 else
                    'Developing' if portfolio_score >= 40 else 'Getting Started'
        }
        
        # ===== CONTEXT ASSEMBLY =====
        
        context.update({
            'title': 'Professional Development Command Center',
            'subtitle': 'Unified view of learning journey and skill applications',
            
            # Core statistics
            'education_stats': education_stats,
            'skill_stats': skill_stats,
            'system_stats': system_stats,
            'integration_stats': integration_stats,
            
            # Featured content
            'featured_skills': featured_skills,
            'skills_with_tech': skills_with_tech,
            'recent_activities': recent_activities,
            
            # Analytics
            'growth_metrics': growth_metrics,
            'suggested_actions': suggested_actions,
            'portfolio_readiness': portfolio_readiness,
            
            # Additional context for template
            'current_learning': Education.objects.filter(is_current=True)[:3],
            'top_technologies': Technology.objects.annotate(
                skill_count=Count('skill_relations')
            ).order_by('-skill_count')[:5],
            'recent_skill_developments': EducationSkillDevelopment.objects.select_related(
                'education', 'skill'
            ).order_by('-created_at')[:5],
        })
        
        return context


class SkillDemonstrationView(BaseAdminView, DetailView):
    """Enhanced skill detail showing ecosystem-wide demonstrations"""

    model = Skill
    template_name = 'core/admin/skill_demonstration.html'
    context_object_name = 'skill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill = self.object 

        # Technology Relationships
        tech_relations = skill.technology_relations.select_related('technology').order_by('-strength')

        # Projects using this skill (via technologies)
        skill_technologies = tech_relations.values_list('technology', flat=True)
        projects_using_skill = SystemModule.objects.filter(
            technologies__in=skill_technologies
        ).distinct().prefetch_related('technologies')

        # Blog posts related to this skill (via project connections)
        related_blog_posts = Post.objects.filter(
            systemlogentry__system__in=projects_using_skill
        ).distinct()[:10]

        # Education that developed this skill
        education_sources = EducationSkillDevelopment.objects.filter(
            skill=skill
        ).select_related('education').order_by('-proficiency_gained')

        # Learning progression timeline
        learning_timeline = self.build_skill_timeline(skill)

        # Skill analytics
        skill_analytics = {
            'total_projects': projects_using_skill.count(),
            'primary_technologies': tech_relations.filter(strength__gte=3).count(),
            'blog_documentation': related_blog_posts.count(),
            'learning_sources': education_sources.count(),
            'skill_progression_score': skill.get_mastery_progression_score() if hasattr(skill, 'get_mastery_progression_score') else 0,
            'practical_applications': projects_using_skill.filter(status__in=['deployed', 'published']).count(),
        }

        # Related skills (those that share technologies)
        related_skills = Skill.objects.filter(
            technology_relations__technology__in=skill_technologies
        ).exclude(id=skill.id).distinct()[:6]

        # Suggested next steps
        next_steps = self.get_skill_next_steps(skill, tech_relations, projects_using_skill)

        context.update({
            'title': f'Skill Overview: {skill.name}',
            'subtitle': 'Cross-ecosystem skill demonstration and development',

            # Core relationships
            'tech_relations': tech_relations,
            'projects_using_skill': projects_using_skill,
            'related_blog_posts': related_blog_posts,
            'education_sources': education_sources,
            'related_skills': related_skills,

            # Analytics and progression
            'skill_analytics': skill_analytics,
            'learning_timeline': learning_timeline,
            'next_steps': next_steps,

            # Available options for new connections
            'available_technologies': Technology.objects.exclude(
                id__in=skill_technologies
            ).order_by('name')[:20],
            'available_projects': SystemModule.objects.exclude(
                id__in=projects_using_skill.values_list('id', flat=True)
            ).filter(status__in=['deployed', 'in_development']).order_by('-updated_at')[:10],
        })

        return context
    
    def build_skill_timeline(self, skill):
        """Build chronological timeline of skill development"""
        timeline_events = []

        # Education events
        for edu_dev in skill.education_development.all():
            timeline_events.append({
                'date': edu_dev.education.start_date,
                'type': 'education_start',
                'title': f'Started learning {skill.name}',
                'source': edu_dev.education.institution,
                'details': f'{edu_dev.education.degree} - {edu_dev.education.field_of_study}',
                'proficiency_gained': edu_dev.proficiency_gained,
            })

            if edu_dev.education.end_date:
                timeline_events.append({
                    'date': edu_dev.education.end_date,
                    'type': 'education_complete',
                    'title': f'Completed {skill.name} training',
                    'source': edu_dev.education.institution,
                    'details': f'Gained {edu_dev.get_proficiency_gained_display()} proficiency',
                })

        # Technology associations
        for tech_relation in skill.technology_relations.all():
            if tech_relation.first_used_together:
                timeline_events.append({
                    'date': tech_relation.first_used_together,
                    'type': 'technology_first_use',
                    'title': f'First used {tech_relation.technology.name}',
                    'source': 'Practical Application',
                    'details': f'{tech_relation.get_relationship_type_display()} - {tech_relation.get_strength_display()}',
                })

        # Project applications (approximate from system creation dates)
        skill_technologies = skill.technology_relations.values_list('technology', flat=True)
        for project in SystemModule.objects.filter(technologies__in=skill_technologies).distinct():
            timeline_events.append({
                'date': project.created_at.date(),
                'type': 'project_application',
                'title': f'Applied {skill.name} in {project.title}',
                'source': 'Project Development',
                'details': f'{project.get_status_display()} - {project.system_type}',
            })
        
        # Sort chronologically and return recent events
        timeline_events.sort(key=lambda x: x['date'])
        return timeline_events[-10:]  # Last 10 events
    
    def get_skill_next_steps(self, skill, tech_relations, projects_using_skill):
        """Suggest next steps for skill development"""
        suggestions = []

        # Suggest technologies commonly used with current ones
        current_tech_ids = tech_relations.values_list('technology_id', flat=True)
        commonly_paired_techs = Technology.objects.filter(
            systemmodule__technologies__in=current_tech_ids
        ).exclude(id__in=current_tech_ids).annotate(
            usage_count=Count('systemmodule')
        ).order_by('-usage_count')[:3]

        for tech in commonly_paired_techs:
            suggestions.append({
                'type': 'technology',
                'title': f'Learn {tech.name}',
                'reason': f'Commonly used with {skill.name}',
                'action_url': reverse('aura_admin:skill_tech_relation_create') + f'?skill={skill.id}&technology={tech.id}',
                'priority': 'high' if tech.usage_count > 2 else 'medium'
            })
        
        # Suggest project types if skill isn't heavily used
        if projects_using_skill.count() < 3:
            suggestions.append({
                'type': 'project',
                'title': f'Build project showcasing {skill.name}',
                'reason': 'Limited practical demonstrations',
                'action_url': reverse('aura_admin:projects:system_create'),
                'priority': 'high'
            })

        # Suggest documentation if no blog posts
        related_posts = Post.objects.filter(
            systemlogentry__system__in=projects_using_skill
        ).distinct()

        if not related_posts.exists():
            suggestions.append({
                'type': 'documentation',
                'title': f'Document {skill.name} learning journey',
                'reason': 'No learning documentation found',
                'action_url': reverse('aura_admin:blog:discovery_create'),
                'priority': 'medium'
            })
        
        # Suggest certification if proficiency is high but not certified
        if skill.proficiency >= 4 and not skill.is_certified:
            suggestions.append({
                'type': 'certification',
                'title': f'Get {skill.name} certification',
                'reason': 'High proficiency without formal recognition',
                'action_url': reverse('aura_admin:education_create'),
                'priority': 'low'
            })
        
        return suggestions
    

class EnhancedSkillCreateView(BaseAdminCreateView):
    """Enahnced skill creation with ecosystem integration"""

    model = Skill
    form_class = SkillForm
    template_name = 'core/admin/skill_form_enhanced.html'
    success_url = reverse_lazy('aura_admin:skill_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Suggest technologies from existing projects
        suggested_technologies = Technology.objects.filter(
            systemmodule__status__in=['deployed', 'published', 'in_development']
        ).annotate(
            project_count=Count('systemmodule')
        ).order_by('-project_count')[:12]

        # Suggest related education
        recent_education = Education.objects.filter(
            is_current=True
        ).order_by('-start_date')[:5]

        completed_education = Education.objects.filter(
            is_current=False,
            end_date__isnull=False
        ).order_by('-end_date')[:5]


        # Popular skill categories
        popular_categories = Skill.objects.values('category').annotate(
            count=Count('category')
        ).order_by('-count')[:8]

        # Suggest blog categories for documentation
        blog_categories = Category.objects.annotate(
            post_count=Count('posts')
        ).order_by('-post_count')[:8]

        context.update({
            'title': 'Add New Skill',
            'subtitle': 'Build your technical competency portfolio',

            # Suggestions for smart form
            'suggested_technologies': suggested_technologies,
            'recent_education': recent_education,
            'completed_education': completed_education,
            'popular_categories': popular_categories,
            'blog_categories': blog_categories,

            # Form enhancement data
            'skill_categories': Skill.CATEGORY_CHOICES,
            'proficiency_levels': [(i, f'Level {i}') for i in range(1, 6)],
            'relationship_types': SkillTechnologyRelation.RELATIONSHIHP_TYPE,
            'relationship_strengths': SkillTechnologyRelation.RELATIONSHIP_STRENGTH,
        })

        return context

    def form_valid(self, form):
        """Enhanced form processing with automatic relationship creation"""
        response = super().form_valid(form)
        skill = self.object 

        # Auto-create technology relationships if provided
        technology_ids = self.request.POST.getlist('suggested_technologies')
        for tech_id in technology_ids:
            try:
                technology = Technology.objects.get(id=tech_id)
                relationship_strength = int(self.request.POST.get(f'tech_strength_{tech_id}', 2))
                relationship_type = self.request.POST.get(f'tech_type_{tech_id}', 'implementation')

                SkillTechnologyRelation.objects.create(
                    skill=skill,
                    technology=technology,
                    strength=relationship_strength,
                    relationship_type=relationship_type,
                    notes=f'Auto-created during skill setup'
                )
            except (Technology.DoesNotExist, ValueError):
                continue
        
        # Auto-create education relationships if provided
        education_ids = self.request.POST.getlist('related_education')
        for edu_id in education_ids:
            try:
                education = Education.objects.get(iid=edu_id)
                proficiency_gained = int(self.request.POST.get(f'edu_proficiency_{edu_id}', 2))

                EducationSkillDevelopment.objects.create(
                    education=education,
                    skill=skill,
                    proficiency_gained=proficiency_gained,
                    notes=f'Skill developed through {education.degree}'
                )
            except (Education.DoesNotExist, ValueError):
                continue
        
        messages.success(
            self.request,
            f'Skill "{skill.name}" created with ecosystem connections!'
        )

        return response


class ProfessionalGrowthTimelineView(AdminAccessMixin, TemplateView):
    """Professional development timeline across all apps"""
    template_name = 'core/admin/growth_timeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Build comprehensive timeline
        timeline_events = []

        # Education milestones
        for education in Education.objects.all().order_by('start_date'):
            timeline_events.append({
                'date': education.start_date,
                'type': 'education_start',
                'category': 'Learning',
                'title': f'Started {education.degree}',
                'description': f'{education.field_of_study} at {education.institution}',
                'icon': 'fa-solid fa-graduation-cap',
                'color': 'teal',
                'skills_gained': education.skill_developments.all()[:3]
            })

            if education.end_date:
                timeline_events.append({
                    'date': education.end_date,
                    'type': 'education_complete',
                    'category': 'Achievement',
                    'title': f'Completed {education.degree}',
                    'description': f'Gained expertise in {education.field_of_study}',
                    'icon': 'fa-solid fa-certificate',
                    'color': 'green',
                })

        
        # Project milestones
        for project in SystemModule.objects.filter(status='deployed').order_by('created_at'):
            timeline_events.append({
                'date': project.created_at.date(),
                'type': 'project_deployed',
                'category': 'Application',
                'title': f'Deployed {project.title}',
                'description': project.description[:100] + '...' if len(project.description) > 100 else project.description,
                'icon': 'fa-solid fa-rocket',
                'color': 'coral',
                'technologies_used': project.technologies.all()[:4]
            })
        

        # Blog documentation milestones
        for post in Post.objects.filter(status='published').order_by('published_date')[:20]:
            timeline_events.append({
                'date': post.published_date.date() if post.published_date else post.created_at.date(),
                'type': 'documentation',
                'category': 'Knowledge Sharing',
                'description': post.excerpt or (post.content[:100] + '...' if len(post.content) > 100 else post.content),
                'icon': 'fa-solid fa-file-alt',
                'color': 'lavender',
                'category_tag': post.category.name if post.category else None
            })
        
        # Sort chronologically
        timeline_events.sort(key=lambda x: x['date'])

        # Group by year for display
        grouped_timeline = {}
        for event in timeline_events:
            year = event['date'].year
            if year not in grouped_timeline:
                grouped_timeline[year] = []
            grouped_timeline[year].append(event)
        
        context.update({
            'title': 'Professional Growth Timeline',
            'subtitle': 'Complete development journey across all learning and projects',
            'timeline_events': timeline_events[-50:],  # Last 50 events
            'grouped_timeline': grouped_timeline,
            'total_events': len(timeline_events),
            'years_active': len(grouped_timeline),
        })

        return context


# ===== ADDITIONAL HELPER VIEWS =====

class SkillTechnologyMatrixView(AdminAccessMixin, TemplateView):
    """Full skill-technology relationship matrix visualization"""
    template_name = 'core/admin/skill_tech_matrix.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Build matrix data
        skills = Skill.objects.prefetch_related('technology_relations__technology')
        technologies = Technology.objects.prefetch_related('skill_relations__skill')

        # Create matrix structure
        matrix_data = []
        for skill in skills:
            skill_row = {
                'skill': skill,
                'technologies': {},
                'total_connections': skill.technology_relations.count()
            }

            for relation in skill.technology_relations.all():
                skill_row['technologies'][relation.technology.id] = {
                    'strength': relation.strength,
                    'type': relation.relationship_type,
                    'relation': relation
                }
            
            matrix_data.append(skill_row)
        
        # Matrix Stats
        matrix_stats = {
            'total_relationships': SkillTechnologyRelation.objects.count(),
            'skills_with_connections': Skill.objects.filter(
                technology_relations__isnull=False
            ).distinct().count(),
            'technologies_with_connections': Technology.objects.filter(
                skill_relations__isnull=False
            ).distinct().count(),
            'avg_connections_per_skill': matrix_data and sum(
                row['total_connections'] for row in matrix_data 
            ) / len(matrix_data) or 0,
        }

        context.update({
            'title': 'Skill-Technology Matrix',
            'subtitle': 'Complete overview of skill-technology relationships',
            'matrix_data': matrix_data,
            'technologies': technologies,
            'matrix_stats': matrix_stats,
            'strength_choices': SkillTechnologyRelation.RELATIONSHIP_STRENGTH,
            'type_choices': SkillTechnologyRelation.RELATIONSHIHP_TYPE,
        })

        return context

class QuickSkillTechConnectionView(BaseAdminView, View):
    """AJAX view for quick skill-technology connections"""

    def post(self, request, *args, **kwargs):
        skill_id = request.POST.get('skill_id')
        technology_id = request.POST.get('technology_id')
        strength = request.POST.get('strength', 2)
        relationship_type = request.POST.get('type', 'implementation')

        try:
            skill = Skill.objects.get(id=skill_id)
            technology = Technology.objects.get(id=technology_id)

            # Create or update relationship
            relation, created = SkillTechnologyRelation.objects.get_or_create(
                skill=skill,
                technology=technology,
                defaults={
                    'strength': int(strength),
                    'relationship_type': relationship_type,
                    'notes': f'Quick connection via matrix interface'
                }
            )

            if not created:
                # Update exisiting relationship
                relation.strength = int(strength)
                relation.relationship_type = relationship_type
                relation.save()
            
            return JsonResponse({
                'success': True,
                'created': created,
                'relationship': {
                    'id': relation.id,
                    'strength': relation.strength,
                    'strength_display': relation.get_strength_display(),
                    'type': relation.relationship_type,
                    'type_display': relation.get_relationship_type_display(),
                }
            })
        
        except (Skill.DoesNotExist, Technology.DoesNotExist, ValueError) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
