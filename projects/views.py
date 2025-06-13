"""
Super simplified for new panel and model methods testing.
NOTE TO FUTURE ME: See archived_system_view.py in scratch or previous commits for all previous views.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse

from django.db.models import Count, Avg, Q, Sum, Max, Min, F, Prefetch, OuterRef
from django.db.models.functions import TruncMonth, Extract
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache

import re
from datetime import timedelta, datetime, date
import random

from .models import SystemModule, SystemType, Technology, SystemFeature, SystemMetric, SystemDependency, SystemImage
from blog.models import Post, SystemLogEntry
from core.models import Skill, PortfolioAnalytics


class EnhancedSystemsDashboardView(TemplateView):
    """
    🚀 AURA Systems Command Center - The Ultimate Dashboard

    Using New Manager Methods
    """

    template_name = "projects/systems_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Use cache for expensive queries (5 min)
        cache_timeout = 300

        # Core dashboard stats using new manager
        dashboard_stats = cache.get('dashboard_stats_v2')
        if not dashboard_stats:
            dashboard_stats = self.get_dashboard_stats()
            cache.set('dashboard_stats_v2', dashboard_stats, cache_timeout)

        context['dashboard_stats'] = dashboard_stats

        # Featured systems using new manager methods
        context["featured_systems"] = SystemModule.objects.featured().deployed()[:6]

        # Recent systems activity using new manager methods
        context["recent_systems"] = SystemModule.objects.recently_updated(7)[:8]
        context['systems_in_development'] = SystemModule.objects.in_development()[:5]

        # Technology insights
        context['technology_insights'] = self.get_technology_insights()
        context['tech_usage_stats'] = context['technology_insights']['usage_stats']

        # Recent logs
        context["recent_logs"] = SystemLogEntry.objects.select_related(
            'system', 'post'
        ).order_by('-created_at')[:8]

        # Performance data for dashboard panels
        context['performance_data'] = self.get_performance_data()

        # System alerts
        context['system_alerts'] = self.get_system_alerts()

        # Systems by status for status panels
        context['systems_by_status'] = self.get_systems_by_status()

        # Chart for visualizations
        context['chart_data'] = self.get_chart_data()

        return context

    def get_dashboard_stats(self):
        """Enahnced dashboard stats using new manager methods."""

        # Use new dashboard_stats() method
        base_stats = SystemModule.objects.dashboard_stats()

        # Add performance-specific stats
        performance_systems = SystemModule.objects.with_performance_data()

        # Add development metrics
        all_systems = SystemModule.objects.all()

        enhanced_stats = {
            # Include all base stats from manager
            **base_stats,

            # Performance metrics
            'avg_uptime': performance_systems.aggregate(
                avg=Avg('uptime_percentage')
            )['avg'],

            'total_daily_users': performance_systems.aggregate(
                total=Sum('daily_users')
            )['total'] or 0,

            # Development metrics
            'total_code_lines': all_systems.aggregate(
                total=Sum('code_lines')
            )['total'] or 0,

            'total_commits': all_systems.aggregate(
                total=Sum('commit_count')
            )['total'] or 0,

            # New manager method stats
            'recently_updated_count': SystemModule.objects.recently_updated(7).count(),
            'high_priority_count': SystemModule.objects.high_priority().count(),

        }

        return enhanced_stats

    def get_technology_insights(self):
        """Technology usage analytics and trends."""
        # Top technologies by usage
        usage_stats = Technology.objects.annotate(
            usage_count=Count('systems', filter=Q(systems_status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:8]

        # Technology diversity score
        total_systems = SystemModule.objects.filter(status__in=['deployed', 'published']).count()
        unique_technologies = Technology.objects.filter(
            systems__status__in=['deployed', 'published']
        ).distinct().count()

        diversity_score = (unique_technologies / total_systems * 100) if total_systems > 0 else 0

        return {
            'usage_stats': usage_stats,
            'total_unique_technologies': unique_technologies,
            'diversity_score': round(diversity_score, 1),
        }

    def get_performance_data(self):
        """Performance metrics for dashboard panels."""
        # Get systems w performance data
        performing_systems = SystemModule.objects.with_performancec_data()

        if not performing_systems.exists():
            return {
                'avg_performance': None,
                'avg_uptime': None,
                'health_distribution': {}
            }

        # Calculate averages
        avg_performance = performing_systems.aggregate(
            avg=Avg('performance_score')
        )['avg']

        avg_uptime = performing_systems.aggregate(
            avg=Avg('uptime_percentage')
        )['avg']

        # Health distribution using new model method
        health_distribution = SystemModule.get_health_distribution()

        return {
            "avg_performance": round(avg_performance, 1) if avg_performance else None,
            "avg_uptime": round(avg_uptime, 1) if avg_uptime else None,
            "health_distribution": health_distribution,
        }

    def get_system_alerts(self):
        """Generate alerts for alert panels."""
        alerts = []

        # Use new manager methods for cleaner queries
        low_performance_systems = SystemModule.objects.with_performance_data().filter(
            performance_score__lt=70
        )

        if low_performance_systems.exists():
            alerts.append(
                {
                    "icon": "speed",
                    "title": "Performance Alert",
                    "message": f"{low_performance_systems.count()} system{'s' if low_performance_systems.count() > 1 else ''} showing low performance scores.",
                    "created_at": timezone.now(),
                    "level": "warning",
                }
            )

        # Check for stale development projects using new method, this is really only blanket checkc but can dial in later
        stale_systems = SystemModule.objects.in_development().recently_updated(30)
        if not stale_systems.exists():
            # If no recent updates, that means all dev systems are stale
            total_dev_systems = SystemModule.objects.in_development().count()
            if total_dev_systems > 0:
                alerts.append(
                    {
                        "icon": "schedule",
                        "title": "Stale Development",
                        "message": f"{total_dev_systems} systems not updated in 30+ days",
                        "created_at": timezone.now(),
                        "level": "info",
                    }
                )

        return alerts

    # May be able to eliminate as well and get from dashboard_stats() model method
    def get_systems_by_status(self):
        """
        Get systems count using new model methods.
        """
        return {
            'deployed': SystemModule.objects.deployed().count(),
            'published': SystemModule.objects.published().count(),
            'in_development': SystemModule.objects.in_development().count(),
            'featured': SystemModule.objects.featured().count()
        }

    def get_chart_data(self):
        """Data formatted for charts and visualizations (simplified)"""
        # Simple completion trend
        all_systems = SystemModule.objects.all()
        avg_completion = (
            all_systems.aggregate(avg=Avg("completion_percent"))["avg"] or 0
        )

        # Mock trend data - you can enhance this with real historical data
        completion_trend = [
            {"month": "Jan", "value": max(0, avg_completion - 15)},
            {"month": "Feb", "value": max(0, avg_completion - 10)},
            {"month": "Mar", "value": max(0, avg_completion - 5)},
            {"month": "Apr", "value": avg_completion},
        ]

        return {
            "completion_trend": completion_trend,
            "current_completion": avg_completion,
        }

# ===================== ENHANCED SYSTEM LIST VIEW =====================


class SystemModuleListView(ListView):
    """Enhanced system list using new manager methods."""

    model = SystemModule
    template_name = "projects/system_list.html"
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        """Simplified filtered query using new manager methods."""
        # Start w all systems
        queryset = SystemModule.objects.select_related('system_type', 'author')

        # Apply filters using new clean methods
        status_filter = self.request.GET.get('status')
        if status_filter == "deployed":
            queryset = queryset.deployed()
        elif status_filter == "published":
            queryset = queryset.published()
        elif status_filter == "in_development":
            queryset = queryset.in_development()
        elif status_filter == "featured":
            queryset = queryset.featured()
        elif status_filter == "recent":
            queryset = queryset.recently_updated(30)
        elif status_filter == "high_priority":
            queryset = queryset.high_priority()
        elif status_filter == "with_metrics":
            queryset = queryset.with_performance_data()

        # Trimmed additional filters for testing

        # Technology filter
        tech_filter = self.request.GET.get("tech")
        if tech_filter:
            queryset = queryset.filter(technologies__slug=tech_filter)

        # Ordering
        order = self.request.GET.get("order", "recent")
        if order == "recent":
            queryset = queryset.order_by("-updated_at")
        elif order == "name":
            queryset = queryset.order_by("title")
        elif order == "completion":
            queryset = queryset.order_by("-completion_percent")
        elif order == "performance":
            queryset = queryset.order_by("-performance_score")

        # complexity_filter = self.request.GET.get('complexity')
        # if complexity_filter:
        #     queryset = queryset.filter(complexity=complexity_filter)

        # tech_filter = self.request.GET.get('technology')
        # if tech_filter:
        #     queryset = queryset.filter(technologies__slug=tech_filter)

        # # Performance filtering using enhanced fields
        # min_performance = self.request.GET.get('min_performance')
        # if min_performance:
        #     queryset = queryset.filter(performance_score__gte=min_performance)

        # health_filter = self.request.GET.get('health')
        # if health_filter:
        #     # This would require custom filtering logic for health status, can work on later
        #     pass

        # Search across enhanced fields
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(technical_details__icontains=search) |
                Q(technologies__name__icontains=search) |
                Q(features__title__icontains=search)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter stats using clean methods - Trimmed for testing
        context.update(
            {
                "total_count": SystemModule.objects.count(),
                "deployed_count": SystemModule.objects.deployed().count(),
                "featured_count": SystemModule.objects.featured().count(),
                "recent_count": SystemModule.objects.recently_updated(30).count(),
                "high_priority_count": SystemModule.objects.high_priority().count(),
                "with_metrics_count": SystemModule.objects.with_performance_data().count(),
            }
        )

        # Filter parameters for template
        context.update(
            {
                "current_status": self.request.GET.get("status", ""),
                "current_tech": self.request.GET.get("tech", ""),
                "current_order": self.request.GET.get("order", "recent"),
            }
        )

        # Technologies for filter dropdown
        context["technologies"] = (
            Technology.objects.annotate(usage_count=Count("systems"))
            .filter(usage_count__gt=0)
            .order_by("name")
        )

        return context

        # context.update(
        #     {
        #         "system_types": SystemType.objects.all().order_by("display_order"),
        #         "technologies": Technology.objects.annotate(
        #             system_count=Count("systems")
        #         )
        #         .filter(system_count__gt=0)
        #         .order_by("-system_count"),
        #         "complexity_choices": SystemModule.COMPLEXITY_CHOICES,
        #         "status_choices": SystemModule.STATUS_CHOICES,
        #         "current_filters": {
        #             "status": self.request.GET.get("status", ""),
        #             "complexity": self.request.GET.get("complexity", ""),
        #             "technology": self.request.GET.get("technology", ""),
        #             "search": self.request.GET.get("search", ""),
        #             "min_performance": self.request.GET.get("min_performance", ""),
        #         },
        #         # Quick stats for the page header
        #         "page_stats": {
        #             "total_systems": self.get_queryset().count(),
        #             "deployed_count": self.get_queryset()
        #             .filter(status="deployed")
        #             .count(),
        #             "avg_completion": self.get_queryset().aggregate(
        #                 avg=Avg("completion_percent")
        #             )["avg"]
        #             or 0,
        #         },
        #     }
        # )
        # return context

# ===================== ENHANCED SYSTEM DETAIL VIEW =====================


class SystemModuleDetailView(DetailView):
    """Enhanced system detail view."""

    model = SystemModule
    template_name = "projects/system_detail.html"
    context_object_name = "system"

    def get_queryset(self):
        # Optimize the query with related data
        return SystemModule.objects.select_related(
            "system_type", "author"
        ).prefetch_related("technologies", "features", "images", "log_entries__post")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.object

        # Related systems using new manager methods
        context["related_systems"] = (
            SystemModule.objects.filter(technologies__in=system.technologies.all())
            .exclude(id=system.id)
            .distinct()[:4]
        )

        # Recent logs for this system
        context["recent_logs"] = system.get_related_logs()[:5]

        # System metrics for dashboard panels
        context["system_metrics"] = system.get_dashboard_metrics()

        # Similar systems using new manager methods
        if system.is_live():
            context["similar_systems"] = (
                SystemModule.objects.deployed()
                .filter(system_type=system.system_type)
                .exclude(id=system.id)[:3]
            )
        else:
            context["similar_systems"] = (
                SystemModule.objects.in_development()
                .filter(system_type=system.system_type)
                .exclude(id=system.id)[:3]
            )

        return context


# ===================== ENHANCED FEATURE VIEWS =====================


class FeaturedSystemsView(ListView):
    """Featured systems using new manager methods."""

    template_name = "projects/featured_systems.html"
    context_object_name = "systems"

    def get_queryset(self):
        # Use new featured() method
        return SystemModule.objects.featured().select_related("system_type")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Stats using new manager methods
        context.update(
            {
                "total_featured": SystemModule.objects.featured().count(),
                "featured_deployed": SystemModule.objects.featured().deployed().count(),
                "featured_in_dev": SystemModule.objects.featured()
                .in_development()
                .count(),
            }
        )

        return context


# ===================== TECHNOLOGY AND TYPE VIEWS =====================


class SystemTypeDetailView(DetailView):
    """Enhanced system type view using new manager methods."""

    model = SystemType
    template_name = "projects/system_type.html"
    context_object_name = "system_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system_type = self.object

        # Systems in this type using new manager methods
        context["systems"] = SystemModule.objects.filter(
            system_type=system_type
        ).deployed()  # Use our new deployed() method

        # Stats using new manager methods
        type_systems = SystemModule.objects.filter(system_type=system_type)
        context.update(
            {
                "total_systems": type_systems.count(),
                "deployed_systems": type_systems.deployed().count(),
                "featured_systems": type_systems.featured().count(),
                "avg_completion": type_systems.aggregate(avg=Avg("completion_percent"))[
                    "avg"
                ]
                or 0,
            }
        )

        return context


class TechnologyDetailView(DetailView):
    """Enhanced technology view using new manager methods."""

    model = Technology
    template_name = "projects/technology_detail.html"
    context_object_name = "technology"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        technology = self.object

        # Systems using this tech - use new manager methods
        tech_systems = SystemModule.objects.filter(technologies=technology)
        context["systems"] = tech_systems.deployed()  # Only show deployed

        # Stats using new manager methods
        context.update(
            {
                "total_systems": tech_systems.count(),
                "deployed_systems": tech_systems.deployed().count(),
                "featured_systems": tech_systems.featured().count(),
                "in_development": tech_systems.in_development().count(),
            }
        )

        return context


# ===================== API ENDPOINTS =====================

@require_http_methods(["GET"])
def dashboard_api(request):
    """API endpoint for real-time dashboard updates using new manager methods."""

    # Get fresh stats using our dashboard_stats() method
    stats = SystemModule.objects.dashboard_stats()

    # Add real-time metrics
    recent_activity = SystemModule.objects.recently_updated(1).count()  # Last 24 hours
    high_priority_count = SystemModule.objects.high_priority().count()

    # Health distribution
    health_distribution = SystemModule.get_health_distribution()

    return JsonResponse(
        {
            "stats": stats,
            "recent_activity_count": recent_activity,
            "high_priority_count": high_priority_count,
            "health_distribution": health_distribution,
            "timestamp": timezone.now().isoformat(),
        }
    )

# ===================== ADMIN/MANAGEMENT VIEWS (AS-IS WILL NEED UPDATING WHEN USE) =====================


class SystemModuleCreateView(LoginRequiredMixin, CreateView):
    """Create a new system module."""

    model = SystemModule
    template_name = "projects/admin/system_form.html"
    fields = [
        "title",
        "subtitle",
        "system_type",
        "description",
        "features_overview",
        "technical_details",
        "complexity",
        "priority",
        "status",
        "featured",
        "technologies",
        "github_url",
        "live_url",
        "demo_url",
        "thumbnail",
        "banner_image",
        "start_date",
        "end_date",
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(
            self.request, f"System '{form.instance.title}' created successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New System"
        context["submit_text"] = "Create System"
        return context


class SystemModuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing system module."""

    model = SystemModule
    template_name = "projects/admin/system_form.html"
    fields = [
        "title",
        "subtitle",
        "system_type",
        "description",
        "features_overview",
        "technical_details",
        "challenges",
        "future_enhancements",
        "complexity",
        "priority",
        "status",
        "featured",
        "technologies",
        "github_url",
        "live_url",
        "demo_url",
        "documentation_url",
        "completion_percent",
        "performance_score",
        "uptime_percentage",
        "thumbnail",
        "banner_image",
        "featured_image",
        "architecture_diagram",
        "start_date",
        "end_date",
        "deployment_date",
    ]

    def test_func(self):
        system = self.get_object()
        return self.request.user == system.author or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(
            self.request, f"System '{form.instance.title}' updated successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Edit System: {self.object.title}"
        context["submit_text"] = "Update System"
        return context


class SystemModuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a system module."""

    model = SystemModule
    template_name = "projects/admin/system_confirm_delete.html"
    success_url = reverse_lazy("projects:system_list")

    def test_func(self):
        system = self.get_object()
        return self.request.user == system.author or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        system = self.get_object()
        messages.success(request, f"System '{system.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Delete System: {self.object.title}"

        # Get related data that will be affected
        context["related_logs"] = self.object.get_related_logs()
        context["related_features"] = self.object.features.count()
        context["related_images"] = self.object.images.count()

        return context
