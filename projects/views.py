from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse

from django.db.models import Count, Avg, Q, Sum, Max, Min, F
from django.db.models.functions import TruncMonth, Extract
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache

import re
from datetime import timedelta, datetime
import random

from .models import SystemModule, SystemType, Technology, SystemFeature, SystemMetric
from blog.models import Post, SystemLogEntry, Category
from core.models import Skill, Experience


class EnhancedSystemsDashboard(TemplateView):
    """
    Enhanced Systems Dashboard - The main analytics command center
    Features real-time metrics, charts, and comprehensive system analytics.
    """
    template_name = "projects/enhanced_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # =================== CORE METRICS ===================
        context["dashboard_stats"] = self.get_dashboard_stats()

        # =================== SYSTEM ANALYTICS ===================
        context["system_analytics"] = self.get_system_analytics()

        # =================== TECHNOLOGY INSIGHTS ===================
        context["technology_insights"] = self.get_technology_insights()

        # =================== DEVELOPMENT METRICS ===================
        context["development_metrics"] = self.get_development_metrics()

        # =================== RECENT ACTIVITY ===================
        context["recent_activity"] = self.get_recent_activity()

        # =================== PERFORMANCE DATA ===================
        context["performance_data"] = self.get_performance_data()

        # =================== CHART DATA ===================
        context["chart_data"] = self.get_chart_data()

        return context
    
    def get_dashboard_stats(self):
        """Core dashboard stats with enhanced calculations."""

        total_systems = SystemModule.objects.count()
        active_systems = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).count()

        development_systems = SystemModule.objects.filter(
            status='in_development'
        ).count()

        testing_systems = SystemModule.objects.filter(
            status='testing'
        ).count()

        # Calculate avg completion acorss all systems
        avg_completion = SystemModule.objects.aggregate(
            avg=Avg('completion_percent')
        )['avg'] or 0

        # Calculate total lines of code equivalent
        total_complexity_score = SystemModule.objects.aggregate(
            total=Sum('complexity')
        )['total'] or 0
        estimated_loc = total_complexity_score * 10000  # 10k lines per complexity point

        # Calculate development hours estimate
        total_dev_hours = 0
        for system in SystemModule.objects.all():
            # Base hours: complexity * 100 hrs per point
            base_hours = system.complexity * 100
            # Completion factor
            completion_factor = (system.completion_percent or 0) / 100
            total_dev_hours += base_hours * completion_factor

        # Calculate portfolio value metrics
        featured_systems = SystemModule.objects.filter(featured=True).count()
        open_source_systems = SystemModule.objects.filter(
            github_url__isnull=False
        ).exclude(github_url='').count()

        return {
            'total_systems': total_systems,
            'active_systems': active_systems,
            'development_systems': development_systems,
            'testing_systems': testing_systems,
            'draft_systems': SystemModule.objects.filter(status='draft').count(),
            'archived_systems': SystemModule.objects.filter(status='archived').count(),
            'avg_completion': round(avg_completion, 1),
            'estimated_loc': estimated_loc,
            'total_dev_hours': int(total_dev_hours),
            'featured_systems': featured_systems,
            'open_source_systems': open_source_systems,
            'total_technologies': Technology.objects.count(),
            'active_technologies': Technology.objects.filter(
                systems__status__in=['deployed', 'published']
            ).distinct().count(),
        }

    def get_system_analytics(self):
        """Detailed system analytics and distributions."""

        # Status Distribution
        systems_by_status = {}
        for status_choice in SystemModule.STATUS_CHOICES:
            status_key = status_choice[0]
            count = SystemModule.objects.filter(status=status_key).count()
            systems_by_status[status_key] = {
                'count': count,
                'label': status_choice[1],
                'percentage': round((count / SystemModule.objects.count() * 100), 1) if SystemModule.objects.count() > 0 else 0
            }

        # Complexity distribution
        complexity_distribution = SystemModule.objects.values('complexity').annotate(
            count=Count('id'),
            avg_completion=Avg('completion_percent')
        ).order_by('complexity')

        # System type analytics
        system_type_stats = SystemType.objects.annotate(
            systems_count=Count('systems'),
            avg_completion=Avg('systems__completion_percent'),
            total_complexity=Sum('systems__complexity'),
        ).filter(systems_count__gt=0).order_by('-systems_count')

        # Recent systems (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_systems_count = SystemModule.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        return {
            'systems_by_status': systems_by_status,
            'complexity_distribution': list(complexity_distribution),
            'system_type_stats': system_type_stats,
            'recent_systems_count': recent_systems_count,
            'avg_system_complexity': SystemModule.objects.aggregate(
                avg=Avg('complexity')
            )['avg'] or 0,
        }

    def get_technology_insights(self):
        """Technology usage analytics and trends."""

        # Technology usage stats
        tech_usage_stats = Technology.objects.annotate(
            usage_count=Count('systems'),
            active_usage=Count('systems', filter=Q(systems__status__in=['deployed', 'published'])),
            avg_complexity=Avg('systems__complexity', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:15]

        # Technology categories
        tech_by_category = {}
        for tech in Technology.objects.all():
            category = tech.category
            if category not in tech_by_category:
                tech_by_category[category] = []
            tech_by_category[category].append({
                'name': tech.name,
                'systems_count': tech.systems.count(),
                'color': getattr(tech, 'color', '#26c6da')
            })

        # Most used technologies in recent systems (last 6 mo)
        six_months_ago = timezone.now() - timedelta(days=180)
        recent_tech_trends = Technology.objects.filter(
            systems__created_at__gte=six_months_ago
        ).annotate(
            recent_usage=Count('systems', filter=Q(systems__created_at__gte=six_months_ago))
        ).filter(recent_usage__gt=0).order_by('-recent_usage')[:10]

        return {
            'tech_usage_stats': tech_usage_stats,
            'tech_by_category': tech_by_category,
            'recent_tech_trends': recent_tech_trends,
            'total_tech_categories': len(tech_by_category),
        }

    def get_development_metrics(self):
        """Development and progress metrics."""

        # Monthly development progress
        current_month = timezone.now().replace(day=1)
        monthly_metrics = []

        for i in range(6):  # last 6mo
            month_start = current_month - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)

            systems_created = SystemModule.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()

            systems_completed = SystemModule.objects.filter(
                updated_at__gte=month_start,
                updated_at__lt=month_end,
                status__in=['deployed', 'published']
            ).count()

            monthly_metrics.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'systems_created': systems_created,
                'systems_completed': systems_completed,
            })

        # Feature completion metrics
        total_features = SystemFeature.objects.count()
        completed_features = SystemFeature.objects.filter(
            implementation_status='completed'
        ).count()

        # Avg development time (est)
        completed_systems = SystemModule.objects.filter(
            status__in=['deployed', 'published'],
            start_date__isnull=False,
            end_date__isnull=False
        )

        avg_dev_time_days = 0
        if completed_systems.exists():
            total_days = sum([
                (system.end_date - system.start_date).days
                for system in completed_systems
                if system.end_date and system.start_date
            ])
            avg_dev_time_days = total_days / completed_systems.count()

        return {
            'monthly_metrics': list(reversed(monthly_metrics)),  # Most recent first
            'total_features': total_features,
            'completed_features': completed_features,
            'feature_completion_rate': round((completed_features / total_features * 100), 1) if total_features > 0 else 0,
            'avg_dev_time_days': round(avg_dev_time_days, 1),
            'systems_with_github': SystemModule.objects.exclude(
                Q(github_url='') | Q(github_url__isnull=True)
            ).count(),
            'systems_with_demo': SystemModule.objects.exclude(
                Q(live_url='') | Q(live_url__isnull=True)
            ).count(),
        }

    def get_recent_activity(self):
        """Recent activity across systems and logs"""

        # Recent system updates
        recent_systems = SystemModule.objects.order_by('-updated_at')[:8]

        # Recent log entries
        recent_logs = SystemLogEntry.objects.select_related(
            'post', 'system'
        ).order_by('-created_at')[:8]

        # Recent feature additions
        recent_features = SystemFeature.objects.select_related(
            'system'
        ).order_by('-id')[:6]

        return {
            'recent_systems': recent_systems,
            'recent_logs': recent_logs,
            'recent_features': recent_features,
        }

    def get_performance_data(self):
        """System performance and uptime data"""

        # Avg performance score
        avg_performance = SystemModule.objects.aggregate(
            avg_performance=Avg('performance_score'),
            avg_uptime=Avg('uptime_percentage')
        )

        # Systems w performance issues (< 90% uptime)
        systems_with_issues = SystemModule.objects.filter(
            uptime_percentage__lt=90.0
        ).count()

        # High performing systems (> 95% uptime)
        high_performing_systems = SystemModule.objects.filter(
            uptime_percentage__gte=95.0
        ).count()

        return {
            'avg_performance_score': round(avg_performance['avg_performance'] or 0, 1),
            'avg_uptime': round(avg_performance['avg_uptime'] or 100, 2),
            'systems_with_issues': systems_with_issues,
            'high_performing_systems': high_performing_systems,
        }

    def get_chart_data(self):
        """Data formatted for charts and visualizations"""

        # System completion over time (for line charts)
        systems_timeline = SystemModule.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=365)
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            avg_completion=Avg('completion_percent')
        ).order_by('month')

        # Format the data for frontend consumption
        formatted_timeline = []
        for item in systems_timeline:
            formatted_timeline.append(
                {
                    "month": item["month"].strftime("%Y-%m") if item["month"] else "",
                    "count": item["count"],
                    "avg_completion": item["avg_completion"] or 0,
                }
            )

        # Technology distribution (for pie chart)
        tech_distribution = (
            Technology.objects.annotate(
                systems_count=Count(
                    "systems", filter=Q(systems__status__in=["deployed", "published"])
                )
            )
            .filter(systems_count__gt=0)
            .order_by("-systems_count")[:8]
        )

        # Complexity vs Completion (for scatter plot)
        complexity_completion = SystemModule.objects.values(
            "complexity", "completion_percent", "title"
        ).order_by("complexity")

        return {
            "systems_timeline": formatted_timeline,
            "tech_distribution": [
                {
                    "name": tech.name,
                    "count": tech.systems_count,
                    "color": getattr(tech, "color", "#26c6da"),
                }
                for tech in tech_distribution
            ],
            "complexity_completion": list(complexity_completion),
        }


# API endpoint for real-time dashboard updates
def dashboard_api(request):
    """API endpoint for real-time dashboard data"""

    if request.method == "GET":
        data_type = request.GET.get("type", "stats")

        if data_type == "stats":
            # Quick stats for real-time updates
            stats = {
                "total_systems": SystemModule.objects.count(),
                "active_systems": SystemModule.objects.filter(
                    status__in=["deployed", "published"]
                ).count(),
                "avg_completion": SystemModule.objects.aggregate(
                    avg=Avg("completion_percent")
                )["avg"]
                or 0,
                "timestamp": timezone.now().isoformat(),
            }
            return JsonResponse(stats)

        elif data_type == "activity":
            # Recent activity for live feed
            recent_activity = []

            # Recent systems
            for system in SystemModule.objects.order_by("-updated_at")[:5]:
                recent_activity.append(
                    {
                        "type": "system_update",
                        "title": system.title,
                        "timestamp": system.updated_at.isoformat(),
                        "url": system.get_absolute_url(),
                    }
                )

            # Recent logs
            for log in SystemLogEntry.objects.order_by("-created_at")[:5]:
                recent_activity.append(
                    {
                        "type": "log_entry",
                        "title": log.post.title,
                        "system": log.system.title,
                        "timestamp": log.created_at.isoformat(),
                        "url": log.post.get_absolute_url(),
                    }
                )

            # Sort by timestamp
            recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)

            return JsonResponse({"activity": recent_activity[:10]})

    return JsonResponse({"error": "Invalid request"}, status=400)


class SystemModuleListView(ListView):
    """Main systems overview page with HUD-style grid display."""

    model = SystemModule
    template_name = 'projects/system_list.html'
    context_object_name = 'systems'
    paginate_by = 9  # 3x3 grid

    def get_queryset(self):
        queryset = SystemModule.objects.filter(
            status__in=['deployed', 'published']
            ).select_related('system_type', 'author').prefetch_related('technologies')

        # Filter by system type if provided
        system_type_slug = self.request.GET.get('type')
        if system_type_slug:
            queryset = queryset.filter(system_type__slug=system_type_slug)

        # Filter by technology if provided
        tech_slug = self.request.GET.get("tech")
        if tech_slug:
            queryset = queryset.filter(technologies__slug=tech_slug)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(technologies__name__icontains=search_query)
            ).distinct()

        # Sort functionality
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['-created_at', 'title', '-completion_percent', 'complexity']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # System types for filtering
        context['system_types'] = SystemType.objects.annotate(
            system_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(system_count__gt=0)

        # Technologies for filtering
        context['technologies'] = Technology.objects.annotate(
            system_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(system_count__gt=0).order_by('category', 'name')

        # Featured systems for hero section
        context['featured_systems'] = SystemModule.objects.filter(
            featured=True,
            status__in=['deployed', 'published']
        )[:3]

        # Stats for HUD dashboard
        context['total_systems'] = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).count()

        context['systems_in_development'] = SystemModule.objects.filter(
            status='in_development'
        ).count()

        context['avg_completion'] = SystemModule.objects.aggregate(
            avg_completion=Avg('completion_percent')
        )['avg_completion'] or 0

        # Get current filters for navigation
        context['current_type'] = self.request.GET.get('type', '')
        context["current_tech"] = self.request.GET.get("tech", "")
        context["current_sort"] = self.request.GET.get("sort", "latest")
        context["search_search"] = self.request.GET.get("search", "")

        # Add show_filters tag for template
        context['show_filters'] = True

        return context


class SystemModuleDetailView(DetailView):
    """Enhanced system detail view with better metrics integration."""

    model = SystemModule
    template_name = 'projects/system_detail.html'
    context_object_name = 'system'

    def get_queryset(self):
        return SystemModule.objects.select_related(
            'system_type', 'author'
        ).prefetch_related(
            'technologies', 'features', 'images', 'related_systems'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.object

        # Related system logs (blog posts)
        context['related_logs'] = system.get_related_logs()[:5]

        # System features grouped by type
        features = system.features.all().order_by('order')
        context['core_features'] = features.filter(feature_type='core')
        context['advanced_features'] = features.filter(feature_type='advanced')
        context['other_features'] = features.exclude(feature_type__in=['core', 'advanced'])

        # System images/gallery
        context['system_images'] = system.images.all().order_by('order')

        # Current metrics for HUD display
        context['current_metrics'] = SystemMetric.objects.filter(
            system=system,
            is_current=True
        ).order_by('metric_type')

        # Related systems
        context['related_systems'] = system.related_systems.filter(
            status__in=['deployed', 'published']
        )[:3]

        # Technologies breakdown
        context['technologies_by_category'] = {}
        for tech in system.technologies.all():
            if tech.category not in context['technologies_by_category']:
                context['technologies_by_category'][tech.category] = []
            context['technologies_by_category'][tech.category].append(tech)

        # Previous/Next system navigation
        try:
            context['previous_system'] = SystemModule.objects.filter(
                created_at__lt=system.created_at,
                status__in=['deployed', 'published']
            ).order_by('-created_at').first()
        except SystemModule.DoesNotExist:
            context['previous_system'] = None

        try:
            context['next_system'] = SystemModule.objects.filter(
                created_at__gt=system.created_at,
                status__in=['deployed', 'published']
            ).order_by('created_at').first()
        except SystemModule.DoesNotExist:
            context['next_system'] = None

        # Add breadcrumb data
        context['show_breadcrumbs'] = True
        context['current_system'] = system

        return context


class SystemTypeDetailView(DetailView):
    """View for displaying all systems of a specific type."""

    model = SystemType
    template_name = "projects/system_type.html"
    context_object_name = "system_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system_type = self.object 

        # Systems in this type
        context['systems'] = SystemModule.objects.filter(
            system_type=system_type,
            status__in=['deployed', 'published']
        ).order_by('-created_at')

        # Stats for this system type
        context['total_systems'] = context['systems'].count()
        context['avg_completion'] = context['systems'].aggregate(
            avg_completion=Avg('completion_percent')
        )['avg_completion'] or 0

        # Technologies used in this system type
        context['common_technologies'] = Technology.objects.filter(
            systems__system_type=system_type,
            systems__status__in=['deployed', 'published']
        ).annotate(
            usage_count=Count('systems')
        ).order_by('-usage_count')[:10]

        return context


class TechnologyDetailView(DetailView):
    """View for displaying all systems using a specific technology."""

    model = Technology
    template_name = "projects/technology_detail.html"
    context_object_name = "technology"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        technology = self.object 

        # Systems using this tech
        context['systems'] = SystemModule.objects.filter(
            technologies=technology,
            status__in=['deployed', 'published']
        ).order_by('-created_at')

        # Stats
        context['total_systems'] = context['systems'].count()

        # System types that use this tech
        context['system_types'] = SystemType.objects.filter(
            systems__technologies=technology,
            systems__status__in=['deployed', 'published']
        ).annotate(
            systems_count=Count('systems')
        ).distinct().order_by('-systems_count')

        return context


class SystemsDashboardView(ListView):
    """
    Traditional Systems Dashboard (can redirect to unified dashboard or serve as systems-focused view)
    Sending to Unified Temp for now can tweak later.
    """

    model = SystemModule
    template_name = "projects/unified_dashboard.html"
    context_object_name = "recent_systems"

    def get_queryset(self):
        return SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).order_by('-created_at')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard Stats
        context['dashboard_stats'] = {
            'total_systems': SystemModule.objects.filter(
                status__in=['deployed', 'published']
            ).count(),
            'systems_in_development': SystemModule.objects.filter(
                status='in_development'
            ).count(),
            'systems_testing': SystemModule.objects.filter(
                status='testing'
            ).count(),
            'total_technologies': Technology.objects.count(),
            'avg_completion': SystemModule.objects.aggregate(
                avg_completion=Avg('completion_percent')
            )['avg_completion'] or 0,
        }

        # System type distribution
        context['system_type_stats'] = SystemType.objects.annotate(
            systems_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(systems_count__gt=0).order_by('-systems_count')

        # Tech usuage stats
        context['tech_usuage_stats'] = Technology.objects.annotate(
            usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:10]

        # Recent system logs
        context['recent_logs'] = SystemLogEntry.objects.select_related(
            'post', 'system'
        ).order_by('-created_at')[:5]

        # Systems by status for HUD-display
        context['systems_by_status'] = {}
        for status_choice in SystemModule.STATUS_CHOICES:
            status_key = status_choice[0]
            context['systems_by_status'][status_key] = SystemModule.objects.filter(
                status=status_key
            ).count()

        return context

# ===================== ADMIN/MANAGEMENT VIEWS =====================


class SystemModuleCreateView(LoginRequiredMixin, CreateView):
    """Create a new system module."""

    model = SystemModule
    template_name = "projects/admin/system_form.html"
    fields = [
        'title', 'subtitle', 'system_type', 'description', 'features_overview',
        'technical_details', 'complexity', 'priority', 'status', 'featured',
        'technologies', 'github_url', 'live_url', 'demo_url',
        'thumbnail', 'banner_image', 'start_date', 'end_date'
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, f"System '{form.instance.title}' created successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create New System"
        context['submit_text'] = "Create System"
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
        messages.success(self.request, f"System '{form.instance.title}' updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit System: {self.object.title}"
        context['submit_text'] = "Update System"
        return context


class SystemModuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a system module."""

    model = SystemModule
    template_name = "projects/admin/system_confirm_delete.html"
    success_url = reverse_lazy('projects:system_list')

    def test_func(self):
        system = self.get_object()
        return self.request.user == system.author or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        system = self.get_object()
        messages.success(request, f"System '{system.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete System: {self.object.title}"

        # Get related data that will be affected
        context['related_logs'] = self.object.get_related_logs()
        context['related_features'] = self.object.features.count()
        context['related_images'] = self.object.images.count()

        return context

# ===================== API/AJAX VIEWS =====================


class SystemMetricsAPIView(DetailView):
    """API endopint for real-time system metrics (for HUD dashboard)."""

    model = SystemModule

    def get(self, request, *args, **kwargs):
        system = self.get_object()

        # Get current metrics
        metrics = {}
        for metric in system.metrics.filter(is_current=True):
            metrics[metric.metric_name] = {
                'value': float(metrics.metric_value),
                'unit': metric.metric_unit,
                'type': metrics.metric_type,
                'timestamp': metric.timestamp.isoformat()
            }

        # Add computed metrics
        metrics.update({
            'completion_progress': system.get_development_progress(),
            'status': system.status,
            'status_color': system.get_status_color(),
            'complexity_visual': system.get_complexity_display(),
            'related_logs_count': system.get_related_logs.count(),
        })

        return JsonResponse({
            'system_id': system.system_id,
            'title': system.title,
            'metrics': metrics,
            'last_updated': timezone.now().isoformat()
        })


class TechnologyUsageAPIView(ListView):
    """API endpoint for tech usage statistics."""

    model = Technology

    def get(self, request, *args, **kwargs):
        # Get tech usage stats
        tech_stats = []
        for tech in Technology.objects.annotate(
            usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count'):

            tech_stats.append({
                'name': tech.name,
                'slug': tech.slug,
                'usage_count': tech.usage_count,
                'color': tech.color,
                'icon': tech.icon,
                'category': tech.category,
            })

        return JsonResponse({
            'technologies': tech_stats,
            'total_technologies': len(tech_stats)
        })


# =============  Separated for now, may combine w SystemMetricsAPIView
class DashboardMetricsAPIView(ListView):
    """
    API Enpoint for real-time dashboard metrics.
    """

    model = SystemModule

    def get(self, request, *args, **kwargs):
        """Return JSON data for dashboard charts and metrics."""

        # Calculate metrics
        total_systems = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).count()

        systems_in_dev = SystemModule.objects.filter(
            status='in_development'
        ).count()

        avg_completion = SystemModule.objects.aggregate(
            avg_completion=Avg('completion_percent')
        )['avg_completion'] or 0

        total_logs = Post.objects.filter(status='published').count()

        # Tech usage data
        tech_usage = []
        for tech in Technology.objects.annotate(
            usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:8]:
            tech_usage.append({
                'name': tech.name,
                'usage_count': tech.usage_count,
                'color': tech.color,
                'icon': tech.icon,
            })

        # System status distribution
        status_distribution = {}
        for status_choice in SystemModule.STATUS_CHOICES:
            status_key = status_choice[0]
            status_distribution[status_key] = SystemModule.objects.filter(
                status=status_key
            ).count()

        # Recent activity
        recent_activity = []
        for log in SystemLogEntry.objects.select_related(
            'post', 'system'
        ).order_by('-created_at')[:10]:
            recent_activity.append({
                'id': log.log_entry_id,
                'title': log.post.title,
                'system_id': log.system.system_id,
                'system_title': log.system.title,
                'connection_type': log.connection_type,
                'priority': log.priority,
                'created_at': log.created_at.isoformat(),
                'status': log.log_status
            })

        # TODO: Add more useful performance metrics, these for testing
        data = {
            'timestamp': timezone.now().isoformat(),
            'metrics': {
                'total_systems': total_systems,
                'systems_in_development': systems_in_dev,
                'avg_completion': round(avg_completion, 1),
                'total_logs': total_logs,
            },
            'technology_usage': tech_usage,
            'status_distribution': status_distribution,
            'recent_activity': recent_activity,
            'performance': {
                'uptime': '99.7%',
                'response_time': '142ms',
                'memory_usage': '67%',
                'cpu_usage': '23%',
            }
        }

        return JsonResponse(data)


class SystemTimeSeriesAPIView(ListView):
    """
    API Endpoint for time-series data (charts)
    """

    model = SystemModule

    def get(self, request, *args, **kwargs):
        """Return time-series data for charts."""

        # Get date range (default to last 30 days)
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        # Generate date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.isoformat())
            current_date += timedelta(days=1)
        

        # TODO: In real app, query actual data
        # For now, generate sample data that shows realistic trends
        def generate_trend_data(base_value, volatility=0.1, trend=0.02):
            """Generate realistic trending data."""
            data = []
            current = base_value
            for i in range(len(date_range)):
                # Add trend and random variation
                current *= (1 + trend + random.uniform(-volatility, volatility))
                data.append(round(current, 2))
            return data

        # System Development progress over time
        system_progress = generate_trend_data(65, 0.05, 0.01)

        # DataLog entries over time
        datalog_activity = generate_trend_data(45, 0.08, 0.015)

        # Code contributions (lines added/modified)
        code_activity = generate_trend_data(1200, 0.15, 0.02)

        # Development hours logged
        dev_hours = generate_trend_data(8, 0.2, 0.005)

        data = {
            'date_range': date_range,
            'metrics': {
                'system_progress': system_progress,
                'datalog_activity': datalog_activity,
                'code_activity': code_activity,
                'dev_hours': dev_hours,
            },
            'meta': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }

        return JsonResponse(data)


# ===================== SEARCH AND FILTER VIEWS =====================


class SystemSearchView(ListView):
    """Advanced search functionality for systems."""

    model = SystemModule
    template_name = "projects/system_search.html"
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        queryset = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).select_related('system_type').prefetch_related('technologies')

        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(technical_details__icontains=query) |
                Q(technologies__name__icontains=query) |
                Q(system_type__name__icontains=query)
            ).distinct()

        # Advanced filters
        system_type_filter = self.request.GET.get('system_type')
        if system_type_filter:
            queryset = queryset.filter(system_type__slug=system_type_filter)

        technology_filter = self.request.GET.get('technology')
        if technology_filter:
            queryset = queryset.filter(technologies__slug=technology_filter)

        complexity_filter = self.request.GET.get('complexity')
        if complexity_filter:
            queryset = queryset.filter(complexity=complexity_filter)

        status_filter = self.requst.GET.get('status')
        if status_filter and status_filter in ['deployed', 'published']:
            queryset = queryset.filter(status=status_filter)

        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['-created_at', 'title', '-completion_percent', 'complexity', '-updated_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Search parameters
        context['query'] = self.request.GET.get('q', '')
        context['total_results'] = self.get_queryset().count()

        # Filter options
        context['system_types'] = SystemType.objects.all()
        context['technologies'] = Technology.objects.all().order_by('category', 'name')
        context['complexity_choices'] = SystemModule.COMPLEXITY_CHOICES

        # Current filter values
        context['current_filters'] = {
            'system_type': self.request.GET.get('system_type', ''),
            'technology': self.request.GET.get('technology', ''),
            'complexity': self.request.GET.get('complexity', ''),
            'status': self.request.GET.get('status', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }

        return context

# ===================== SHOWCASE VIEWS =====================


class FeaturedSystemsView(ListView):
    """Showcase of featured systems for portfolio."""

    model = SystemModule
    template_name = "projects/featured_systems.html"
    context_object_name = "featured_systems"

    def get_queryset(self):
        return (
            SystemModule.objects.filter(
                featured=True, status__in=["deployed", "published"]
            )
            .select_related("system_type")
            .prefetch_related("technologies")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Portfolio stats for showcase
        context["portfolio_stats"] = {
            "total_systems": SystemModule.objects.filter(
                status__in=["deployed", "published"]
            ).count(),
            "technologies_used": Technology.objects.filter(
                systems__status__in=["deployed", "published"]
            )
            .distinct()
            .count(),
            "system_types": SystemType.objects.filter(
                systems__status__in=["deployed", "published"]
            )
            .distinct()
            .count(),
            "lines_of_code": 50000,  # You can calculate this or set manually
            "years_experience": 3,  # Update as needed
        }

        # Technology highlights
        context["top_technologies"] = (
            Technology.objects.annotate(
                usage_count=Count(
                    "systems", filter=Q(systems__status__in=["deployed", "published"])
                )
            )
            .filter(usage_count__gt=0)
            .order_by("-usage_count")[:8]
        )

        return context


class SystemTimelineView(ListView):
    """Timeline view of system development."""

    model = SystemModule
    template_name = "projects/system_timeline.html"
    context_object_name = "systems"

    def get_queryset(self):
        return (
            SystemModule.objects.filter(status__in=["deployed", "published"])
            .select_related("system_type")
            .order_by("-start_date", "-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Group systems by year for timeline display
        systems_by_year = {}
        for system in context["systems"]:
            year = system.start_date.year if system.start_date else system.created_at.year
            if year not in systems_by_year:
                systems_by_year[year] = []
            systems_by_year[year].append(system)

        context["systems_by_year"] = dict(sorted(systems_by_year.items(), reverse=True))

        return context


# ===================== AURA STYLING - UPDATING VIEWS =====================

class UnifiedDashboardView(ListView):
    """
    AURA Unified Dashboard - Contral command center aggregating metrics from all apps
    """

    model = SystemModule
    template_name = "projects/unified_dashboard.html"
    context_object_name = "recent_systems"

    def get_queryset(self):
        return SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).order_by('-created_at')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ===================
        # CORE DASHBOARD STATS
        # ===================
        context["dashboard_stats"] = self.get_dashboard_stats()

        # ===================
        # SYSTEMS DATA
        # ===================
        context.update(self.get_systems_data())

        # ===================
        # DATALOGS DATA
        # ===================
        context.update(self.get_datalogs_data())

        # ===================
        # TECHNOLOGY DATA
        # ===================
        context.update(self.get_technology_data())

        # ===================
        # ACTIVITY DATA
        # ===================
        context.update(self.get_activity_data())

        # ===================
        # CHART DATA
        # ===================
        context.update(self.get_chart_data())

        return context

    def get_dashboard_stats(self):
        """Core dashboard Stats."""

        return {
            'total_systems': SystemModule.objects.filter(
                status__in=['deployed', 'published']
            ).count(),
            'systems_in_development': SystemModule.objects.filter(
                status='in_development'
            ).count(),
            'systems_testing': SystemModule.objects.filter(
                status='testing'
            ).count(),
            'total_technologies': Technology.objects.annotate(
                usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
            ).filter(usage_count__gt=0).count(),
            'avg_completion': SystemModule.objects.aggregate(
                avg_completion=Avg('completion_percent')
            )['avg_completion'] or 0,
        }

    def get_systems_data(self):
        """Systems-specific data."""

        systems_by_status = {}
        for status_choice in SystemModule.STATUS_CHOICES:
            status_key = status_choice[0]
            systems_by_status[status_key] = SystemModule.objects.filter(
                status=status_key
            ).count()

        return {
            'systems_by_status': systems_by_status,
            'system_type_stats': SystemType.objects.annotate(
                systems_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
            ).filter(systems_count__gt=0).order_by('-systems_count')
        }

    def get_datalogs_data(self):
        """DataLogs data."""

        recent_logs = SystemLogEntry.objects.select_related(
            'post', 'system'
        ).order_by('-created_at')[:5]

        total_logs = Post.objects.filter(status='published').count()

        # Calculate development hours (est based on reading time/complexity)
        total_dev_hours = 0
        for system in SystemModule.objects.all():
            # Est based on complexity/completion
            # 100 hours per complexity point
            base_hours = system.complexity * 100
            completion_factor = (system.completion_percent or 0) / 100
            total_dev_hours += base_hours * completion_factor

        return {
            'recent_logs': recent_logs,
            'total_logs': total_logs,
            'total_dev_hours': int(total_dev_hours),
        }

    def get_technology_data(self):
        """Technology usage stats."""

        tech_usage_stats = Technology.objects.annotate(
            usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:10]

        return {
            'tech_usage_stats': tech_usage_stats,
        }

    def get_activity_data(self):
        """Recent activity and metrics."""

        # Get recent system logs
        recent_logs = SystemLogEntry.objects.select_related(
            'post', 'system'
        ).order_by('-created_at')[:8]

        return {
            'recent_activity_logs': recent_logs,
        }

    def get_chart_data(self):
        """Data for charts and visualizations."""

        # System activity over time (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Generate sample data for charts
        # TODO: Calculate actual metrics, pull in GitHub data via API
        system_activity_data = "65,70,68,72,75,73,78,82,79,85,88,85,90,87,92,89,95,92,89,94,91,88,93,96,94,98,95,92,97,99"
        datalog_activity_data = "45,48,52,49,55,58,54,61,59,63,66,62,68,65,71,74,69,73,76,72,78,81,77,84,80,83,87,85,89,91"
        code_activity_data = "1200,1250,1180,1320,1400,1350,1480,1520,1490,1560,1580,1540,1620,1600,1680,1720,1690,1750,1780,1740,1810,1850,1820,1890,1860,1920,1950,1930,1980,2010"
        dev_time_data = "8,10,6,12,14,11,16,18,15,20,22,19,24,21,26,25,23,28,30,27,32,35,31,38,34,36,40,37,42,45"

        return {
            'system_activity_data': system_activity_data,
            'datalog_activity_data': datalog_activity_data,
            'code_activity_data': code_activity_data,
            'dev_time_data': dev_time_data,
            'lines_of_code': 52000,
        }

# ===================== AURA STYLING - UTILITY FUNCTIONS =====================


def get_system_health_score(system):
    """Calculate overall health score for a system."""

    score = 0

    # Completion percentage (40% weight)
    completion_weight = (system.completion_percent or 0) * 0.4
    score += completion_weight

    # Recent activity (30% weight)
    recent_logs = system.get_related_logs()[:5]
    # Max 30 points
    activity_score = min(len(recent_logs) * 6, 30)
    score += activity_score

    # Performance metrics (20% weight)
    if system.performance_score:
        score += (system.performance_score * 0.2)
    else:
        # Default moderate score
        score += 15

    # Uptime (10% weight)
    if system.uptime_percentage:
        score += (system.uptime_percentage * 0.1)
    else:
        # Default good uptime
        score += 9

    return min(100, max(0, score))


def get_technology_trend_score(tech):
    """Calculate trend score for tech usage."""

    current_usage = tech.systems.filter(
        status__in=['deployed', 'published']
    ).count()

    # TODO: In real app, compare w historical data
    # For now, return current usage as trend indicator
    return current_usage


def calculate_development_velocity(system):
    """Calculate development velocity for a system."""

    logs = system.get_related_logs()

    if not logs:
        return 0

    # Calculate based on log frequency and completion progress
    recent_logs = logs.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()

    velocity = recent_logs * (system.completion_percent or 0) / 100
    return round(velocity, 2)
