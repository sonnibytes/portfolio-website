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

from django.db.models import Count, Avg, Q, Sum, Max, Min, F, Prefetch, OuterRef
from django.db.models.functions import TruncMonth, Extract
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache

import re
from datetime import timedelta, datetime
import random

from .models import SystemModule, SystemType, Technology, SystemFeature, SystemMetric, SystemDependency, SystemImage
from blog.models import Post, SystemLogEntry
from core.models import Skill, PortfolioAnalytics


class EnhancedSystemsDashboardView(TemplateView):
    """
    🚀 AURA Systems Command Center - The Ultimate Dashboard

    Showcases all enhanced data with real-time metrics, performance analytics,
    and comprehensive system insights using our enhanced models.
    """

    template_name = "projects/systems_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Core dashboard stats
        context.update(
            {
                "dashboard_stats": self.get_dashboard_stats(),
                "system_analytics": self.get_system_analytics(),
                "technology_insights": self.get_technology_insights(),
                "development_metrics": self.get_development_metrics(),
                "recent_activity": self.get_recent_activity(),
                "performance_data": self.get_performance_data(),
                "chart_data": self.get_chart_data(),
                "critical_alerts": self.get_critical_alerts(),
            }
        )

        return context

    def get_dashboard_stats(self):
        """Core dashboard stats with enhanced fields."""
        cache_key = 'systems_dashboard_stats'
        stats = cache.get(cache_key)

        if not stats:
            all_systems = SystemModule.objects.all()
            deployed_systems = all_systems.filter(status='deployed')

            stats = {
                # System counts
                'total_systems': all_systems.count(),
                'deployed_systems': deployed_systems.count(),
                'systems_in_development': all_systems.filter(status='in_development').count(),
                'systems_testing': all_systems.filter(status='testing').count(),

                # Performance avg using enhanced fields
                'avg_completion': all_systems.aggregate(
                    avg=Avg('completion_percent')
                )['avg'] or 0,

                'avg_performance': deployed_systems.aggregate(
                    avg=Avg('performance_score')
                )['avg'] or 0,

                'avg_uptime': deployed_systems.aggregate(
                    avg=Avg('uptime_percentage')
                )['avg'] or 0,

                'total_daily_users': deployed_systems.aggregate(
                    total=Sum('daily_users')
                )['total'] or 0,

                # Development metrics using enhanced fields
                'total_code_lines': all_systems.aggregate(
                    total=Sum('code_lines')
                )['total'] or 0,

                'total_commits': all_systems.aggregate(
                    total=Sum('commit_count')
                )['total'] or 0,

                'total_dev_hours': all_systems.aggregate(
                    actual=Sum('actual_dev_hours'),
                    estimated=Sum('estimated_dev_hours')
                ),

                # Team insights
                'avg_team_size': all_systems.aggregate(
                    avg=Avg('team_size')
                )['avg'] or 1,

                'largest_team': all_systems.aggregate(
                    max=Max('team_size')
                )['max'] or 1,
            }

            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)

        return stats

    def get_system_analytics(self):
        """Detailed system analytics and distributions."""
        cache_key = 'systems_analytics'
        analytics = cache.get(cache_key)

        if not analytics:
            systems = SystemModule.objects.select_related('system_type')

            analytics = {
                # Status breakdown
                'systems_by_status': dict(
                    systems.values('status').annotate(
                        count=Count('id')
                    ).values_list('status', 'count')
                ),

                # System type breakdown
                'systems_by_type': list(
                    systems.values(
                        'system_type__name',
                        'system_type__color',
                        'system_type__icon'
                    ).annotate(
                        count=Count('id')
                    ).order_by('-count')
                ),

                # Complexity breakdown
                'systems_by_complexity': dict(
                    systems.values('complexity').annotate(
                        count=Count('id')
                    ).values_list('complexity', 'count')
                ),

                # Health status breakdown using enhanced method
                'systems_by_health': self._get_systems_by_health(),

                # Featured v non-featured
                'featured_systems_count': systems.filter(featured=True).count(),
            }

            cache.set(cache_key, analytics, 300)  # 5 min

        return analytics

    def get_technology_insights(self):
        """Technology usage analytics and trends."""
        cache_key = 'technology_insights'
        insights = cache.get(cache_key)

        if not insights:
            # Technology usage w system counts
            tech_usage = Technology.objects.annotate(
                usage_count=Count('systems'),
                deployed_usage=Count('systems', filter=Q(systems__status='deployed'))
            ).filter(usage_count__gt=0).order_by('-usage_count')[:12]

            # Tech categories breakdown
            tech_categories = Technology.objects.values('category').annotate(
                count=Count('id'),
                usage=Count('systems')
            ).order_by('-usage')

            insights = {
                'top_technologies': [
                    {
                        'name': tech.name,
                        'usage_count': tech.usage_count,
                        'deployed_usage': tech.deployed_usage,
                        'color': tech.color,
                        'icon': tech.icon,
                        'category': tech.category
                    }
                    for tech in tech_usage
                ],
                'tech_categories': list(tech_categories),
                'total_technologies': Technology.objects.count(),
            }

            cache.set(cache_key, insights, 600)  # 10 minutes
        return insights

    def get_development_metrics(self):
        """Development and progress metrics."""
        systems = SystemModule.objects.all()

        # Calc hours variance for systems w both est and actual hours
        systems_with_hours = systems.filter(
            estimated_dev_hours__isnull=False,
            actual_dev_hours__isnull=False
        )

        hours_variance_data = []
        total_variance = 0
        for system in systems_with_hours:
            variance = system.actual_dev_hours - system.estimated_dev_hours
            hours_variance_data.append({
                'system': system.title,
                'variance': variance,
                'percentage': (variance / system.estimated_dev_hours * 100) if system.estimated_dev_hours > 0 else 0
            })
            total_variance += variance

        return {
            'hours_variance_data': hours_variance_data,
            'avg_hours_variance': total_variance / len(hours_variance_data) if hours_variance_data else 0,
            'systems_on_time': len([v for v in hours_variance_data if v['variance'] <= 0]),
            'systems_over_time': len([v for v in hours_variance_data if v['variance'] > 0]),

            # Recent commit activity
            'recent_commits': systems.filter(
                last_commit_date__isnull=False
            ).order_by('-last_commit_date')[:8],

            # Team size dist
            'team_size_distribution': dict(
                systems.values('team_size').annotate(
                    count=Count('id')
                ).values_list('team_size', 'count')
            ),
        }

    def get_recent_activity(self):
        """Recent activity and updates across systems and logs"""

        # Recent system updates
        recent_systems = SystemModule.objects.order_by('-updated_at')[:8]

        # Recent log entries
        recent_logs = SystemLogEntry.objects.select_related(
            'system', 'post'
        ).order_by('-created_at')[:8]

        # Recent metrics (from SystemMetric model)
        recent_metrics = SystemMetric.objects.select_related(
            'system', 'post'
        ).order_by('-created_at')[:8]

        return {
            'recent_systems': recent_systems,
            'recent_logs': recent_logs,
            'recent_metrics': recent_metrics,
            'last_updated': timezone.now(),
        }

    def get_performance_data(self):
        """System performance data and trends"""
        # Current performance snapshot
        deployed_systems = SystemModule.objects.filter(
            status='deployed',
            performance_score__isnull=False
        ).order_by('-performance_score')

        # Performance categories
        excellent_systems = deployed_systems.filter(performance_score__gte=90)
        good_systems = deployed_systems.filter(
            performance_score__gte=70,
            performance_score__lt=90
        )
        fair_systems = deployed_systems.filter(
            performance_score__gte=50,
            performance_score__lt=70
        )
        poor_systems = deployed_systems.filter(performance_score__lt=50)

        return {
            'top_performing_systems': deployed_systems[:6],
            'performance_breakdown': {
                'excellent': excellent_systems.count(),
                'good': good_systems.count(),
                'fair': fair_systems.count(),
                'poor': poor_systems.count(),
            },
            'avg_response_time': deployed_systems.aggregate(
                avg=Avg('response_time_ms')
            )['avg'] or 0,
        }

    def get_chart_data(self):
        """Data formatted for charts and visualizations"""
        systems = SystemModule.objects.all()

        # Completion progress data for chart
        completion_data = list(
            systems.values('title', 'completion_percent', 'status').order_by('-completion_percent')
        )

        # Performance trend data (last 30 days from SystemMetric)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        performance_metrics = SystemMetric.objects.filter(
            metric_type='performance',
            created_at__gte=thirty_days_ago
        ).values(
            'created_at__date'
        ).annotate(
            avg_performance=Avg('metric_value')
        ).order_by('created_at__date')

        # System creation timeline
        creation_timeline = systems.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        return {
            "completion_progress": completion_data,
            "performance_trend": list(performance_metrics),
            "creation_timeline": list(creation_timeline),
            "technology_usage": [
                {
                    "name": tech['name'],
                    "count": tech['usage_count'],
                    "color": tech['color'],
                }
                for tech in self.get_technology_insights()['top_technologies'][:8]
            ]
        }

    def get_critical_alerts(self):
        """Critical system alerts and issues"""
        alerts = []

        # Systems w low performance scores
        low_performance = SystemModule.objects.filter(
            performance_score__lt=70,
            performance_score__isnull=False,
            status='deployed'
        )

        for system in low_performance:
            alerts.append({
                'type': 'performance',
                'severity': 'warning' if system.performance_score >= 50 else 'critical',
                'message': f"{system.title} performance score is {system.performance_score}/100",
                'system': system,
                'action_url': system.get_absolute_url()
            })

        # Systems w low uptime
        low_uptime = SystemModule.objects.filter(
            uptime_percentage__lt=95,
            uptime_percentage__isnull=False,
            status='deployed'
        )

        for system in low_uptime:
            alerts.append({
                'type': 'uptime',
                'severity': 'critical' if system.uptime_percentage < 90 else 'warning',
                'message': f"{system.title} uptime is {system.uptime_percentage}%",
                'system': system,
                'action_url': system.get_absolute_url()
            })

        # Critical dependencies
        critical_deps = SystemDependency.objects.filter(
            is_critical=True
        ).select_related('system', 'depends_on')

        for dep in critical_deps:
            alerts.append({
                'type': 'dependency',
                'severity': 'info',
                'message': f"{dep.system.title} has critical dependency on {dep.depends_on.title}",
                'system': dep.system,
                'action_url': dep.system.get_absolute_url()
            })

        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return alerts[:10]  # Return top 10 alerts

    def _get_systems_by_health(self):
        """Helper method to categorize systems by health status"""
        systems = SystemModule.objects.all()
        health_categories = {
            'excellent': [],
            'good': [],
            'fair': [],
            'poor': [],
            'unknown': []
        }

        for system in systems:
            health = system.get_health_status()  # Using enhancecd model method
            health_categories[health].append(system)

        # Convert to counts for easier template usage
        return {
            status: len(systems_list)
            for status, systems_list in health_categories.items()
        }


# API view for Real-time Dashboard Updates
class DashboardAPIView(TemplateView):
    """API endpoint for real-time dashboard updates"""

    def get(self, request, *args, **kwargs):
        dashboard_view = EnhancedSystemsDashboardView()

        # Get fresh data (no caching for API)
        cache.delete('systems_dashboard_stats')
        cache.delete('systems_analytics')

        data = {
            'stats': dashboard_view.get_dashboard_stats(),
            'performance': dashboard_view.get_performance_data(),
            'alerts': dashboard_view.get_critical_alerts(),
            'timestamp': timezone.now().isoformat(),
        }

        return JsonResponse(data)


# Enhanced System List (for system cards)
class EnhancedSystemListView(ListView):
    """Enhanced system list with new filtering and display capabilities"""

    model = SystemModule
    template_name = "projects/system_list.html"
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        queryset = SystemModule.objects.select_related(
            'system_type', 'author'
        ).prefetch_related(
            'technologies', 'features'
        ).order_by('-updated_at')

        # Enhanced filtering w new fields
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        complexity_filter = self.request.GET.get('complexity')
        if complexity_filter:
            queryset = queryset.filter(complexity=complexity_filter)

        tech_filter = self.request.GET.get('technology')
        if tech_filter:
            queryset = queryset.filter(technologies__slug=tech_filter)

        # Performance filtering using enhanced fields
        min_performance = self.request.GET.get('min_performance')
        if min_performance:
            queryset = queryset.filter(performance_score__gte=min_performance)

        health_filter = self.request.GET.get('health')
        if health_filter:
            # This would require custom filtering logic for health status, can work on later
            pass

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
        context.update(
            {
                "system_types": SystemType.objects.all().order_by("display_order"),
                "technologies": Technology.objects.annotate(
                    system_count=Count("systems")
                )
                .filter(system_count__gt=0)
                .order_by("-system_count"),
                "complexity_choices": SystemModule.COMPLEXITY_CHOICES,
                "status_choices": SystemModule.STATUS_CHOICES,
                "current_filters": {
                    "status": self.request.GET.get("status", ""),
                    "complexity": self.request.GET.get("complexity", ""),
                    "technology": self.request.GET.get("technology", ""),
                    "search": self.request.GET.get("search", ""),
                    "min_performance": self.request.GET.get("min_performance", ""),
                },
                # Quick stats for the page header
                "page_stats": {
                    "total_systems": self.get_queryset().count(),
                    "deployed_count": self.get_queryset()
                    .filter(status="deployed")
                    .count(),
                    "avg_completion": self.get_queryset().aggregate(
                        avg=Avg("completion_percent")
                    )["avg"]
                    or 0,
                },
            }
        )
        return context


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


class EnhancedSystemModuleDetailView(DetailView):
    """
    🚀 Enhanced System Detail View - Complete Command Center

    Comprehensive system detail page showcasing all enhanced model data:
    - Performance metrics and analytics
    - System dependencies and relationships
    - Development timeline and progress
    - Technology stack with usage insights
    - Related DataLogs and documentation
    - Team information and collaboration data
    - Real-time health status and monitoring
    """

    model = SystemModule
    template_name = "projects/system_detail.html"
    context_object_name = "system"

    def get_queryset(self):
        """Optimized queryset with all related data."""
        return SystemModule.objects.select_related(
            "system_type", "author"
        ).prefetch_related(
            # Technologies with their skill profiles (FIXED - removed .select_related('category'))
            Prefetch(
                "technologies",
                queryset=Technology.objects.select_related("skill_profile").annotate(
                    systems_count=Count("systems")
                ),
            ),
            # Features ordered by priority and type
            Prefetch(
                "features",
                queryset=SystemFeature.objects.order_by("feature_type", "order"),
            ),
            # Images ordered by display order
            Prefetch("images", queryset=SystemImage.objects.order_by("order")),
            # Current metrics for real-time display
            Prefetch(
                "metrics",
                queryset=SystemMetric.objects.filter(is_current=True).order_by(
                    "metric_type"
                ),
            ),
            # System dependencies
            Prefetch(
                "dependencies",
                queryset=SystemDependency.objects.select_related(
                    "depends_on__system_type"
                ),
            ),
            # Systems that depend on this one
            Prefetch(
                "dependents",
                queryset=SystemDependency.objects.select_related("system__system_type"),
            ),
            # Related systems
            "related_systems__system_type",
            # Blog post connections
            Prefetch(
                "log_entries",
                queryset=SystemLogEntry.objects.select_related(
                    "post__category"
                ).order_by("-post__published_date"),
            ),
        )

    def get_context_data(self, **kwargs):
        """Enhanced context with comprehensive system analytics."""
        context = super().get_context_data(**kwargs)
        system = self.object

        # === PERFORMANCE ANALYTICS ===
        context.update(
            {
                # Real-time metrics from SystemMetric model
                "current_metrics": system.metrics.filter(is_current=True),
                "metric_history": system.metrics.filter(
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).order_by("created_at"),
                # System health and performance indicators
                "health_status": {
                    "overall": system.health_status
                    if hasattr(system, "health_status")
                    else "unknown",
                    "uptime": system.uptime_percentage
                    if hasattr(system, "uptime_percentage")
                    else None,
                    "performance": system.performance_score
                    if hasattr(system, "performance_score")
                    else None,
                    "last_check": system.health_last_check
                    if hasattr(system, "health_last_check")
                    else None,
                },
                # Development progress insights
                "development_insights": {
                    "completion": system.completion_percent,
                    "estimated_hours": system.estimated_development_hours
                    if hasattr(system, "estimated_development_hours")
                    else None,
                    "actual_hours": system.actual_development_hours
                    if hasattr(system, "actual_development_hours")
                    else None,
                    "team_size": system.team_size
                    if hasattr(system, "team_size")
                    else 1,
                    "last_commit": system.last_commit_date
                    if hasattr(system, "last_commit_date")
                    else None,
                },
            }
        )

        # === TECHNOLOGY ANALYSIS ===
        # Group technologies by category for better display
        technologies_by_category = {}
        for tech in system.technologies.all():
            category = tech.get_category_display()
            if category not in technologies_by_category:
                technologies_by_category[category] = []
            technologies_by_category[category].append(tech)

        context["technologies_by_category"] = technologies_by_category

        # Primary vs supporting technologies
        context.update(
            {
                "primary_technologies": system.technologies.filter(
                    category__in=["language", "framework"]
                ),
                "supporting_technologies": system.technologies.exclude(
                    category__in=["language", "framework"]
                ),
            }
        )

        # === FEATURES & FUNCTIONALITY ===
        # Features grouped by type and status
        features_by_type = {}
        features_by_status = {"completed": 0, "in_progress": 0, "planned": 0}

        for feature in system.features.all():
            # Group by type
            feature_type = (
                feature.get_feature_type_display()
                if hasattr(feature, "get_feature_type_display")
                else "Other"
            )
            if feature_type not in features_by_type:
                features_by_type[feature_type] = []
            features_by_type[feature_type].append(feature)

            # Count by status
            status = getattr(feature, "status", "planned")
            if status in features_by_status:
                features_by_status[status] += 1

        context.update(
            {
                "features_by_type": features_by_type,
                "features_by_status": features_by_status,
                "total_features": system.features.count(),
            }
        )

        # === SYSTEM RELATIONSHIPS ===
        context.update(
            {
                # Dependencies analysis
                "critical_dependencies": system.dependencies.filter(is_critical=True),
                "optional_dependencies": system.dependencies.filter(is_critical=False),
                "total_dependencies": system.dependencies.count(),
                # Systems that depend on this one
                "dependent_systems": getattr(system, "dependent_systems", []),
                # Related content using our enhanced relationships
                "related_datalogs": system.log_entries.select_related("post")[:5],
                # Similar systems based on technology overlap
                "similar_systems": self._get_similar_systems(system),
            }
        )

        # === GALLERY & MEDIA ===
        context.update(
            {
                "gallery_images": system.images.all()[:8],  # Limit for performance
                "has_architecture_diagram": bool(system.architecture_diagram),
                "total_images": system.images.count(),
            }
        )

        # === ANALYTICS & INSIGHTS ===
        # Calculate development velocity if we have commit data
        if hasattr(system, "last_commit_date") and system.last_commit_date:
            days_since_last_commit = (
                timezone.now() - system.last_commit_date
            ).days
            context["days_since_last_commit"] = days_since_last_commit
            context["is_actively_developed"] = days_since_last_commit <= 30

        # Performance trends (if we have historical data)
        if system.metrics.exists():
            context["has_performance_data"] = True
            context["performance_trend"] = self._calculate_performance_trend(system)

        return context

    def _get_similar_systems(self, system):
        """Find systems with similar technology stacks"""
        system_tech_ids = list(system.technologies.values_list("id", flat=True))

        if not system_tech_ids:
            return SystemModule.objects.none()

        return (
            SystemModule.objects.filter(technologies__in=system_tech_ids)
            .exclude(id=system.id)
            .annotate(
                tech_overlap=Count(
                    "technologies", filter=Q(technologies__in=system_tech_ids)
                )
            )
            .filter(tech_overlap__gt=0)
            .order_by("-tech_overlap")[:3]
        )

    def _calculate_performance_trend(self, system):
        """Calculate performance trend over time"""
        recent_metrics = system.metrics.filter(
            metric_type="performance",
            created_at__gte=timezone.now() - timedelta(days=30),
        ).order_by("created_at")

        if recent_metrics.count() < 2:
            return "stable"

        first_value = recent_metrics.first().metric_value
        last_value = recent_metrics.last().metric_value

        if last_value > float(first_value) * 1.1:
            return "improving"
        elif last_value < float(first_value) * 0.9:
            return "declining"
        else:
            return "stable"


# Alternative simplified view if you want to keep using your existing one
class SystemModuleDetailView(DetailView):
    """Simplified system detail view with basic optimizations."""

    model = SystemModule
    template_name = "projects/system_detail.html"
    context_object_name = "system"

    def get_queryset(self):
        return SystemModule.objects.select_related(
            "system_type", "author"
        ).prefetch_related("technologies", "features", "images", "related_systems")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.object

        # Related system logs (blog posts) - FIXED
        if hasattr(system, "log_entries"):
            context["related_datalogs"] = system.log_entries.select_related("post")[:5]
        else:
            context["related_datalogs"] = []

        # System features grouped by type
        features = (
            system.features.all().order_by("order") if system.features.exists() else []
        )
        context["core_features"] = [
            f for f in features if getattr(f, "feature_type", None) == "core"
        ]
        context["advanced_features"] = [
            f for f in features if getattr(f, "feature_type", None) == "advanced"
        ]
        context["other_features"] = [
            f
            for f in features
            if getattr(f, "feature_type", None) not in ["core", "advanced"]
        ]

        # System images/gallery
        context["system_images"] = (
            system.images.all().order_by("order") if system.images.exists() else []
        )

        # Current metrics for HUD display
        if hasattr(system, "metrics"):
            context["current_metrics"] = system.metrics.filter(
                is_current=True
            ).order_by("metric_type")
        else:
            context["current_metrics"] = []

        # Related systems
        context["related_systems"] = system.related_systems.filter(
            status__in=["deployed", "published"]
        )[:3]

        # Technologies breakdown
        context["technologies_by_category"] = {}
        for tech in system.technologies.all():
            category = tech.get_category_display()
            if category not in context["technologies_by_category"]:
                context["technologies_by_category"][category] = []
            context["technologies_by_category"][category].append(tech)

        # Previous/Next system navigation
        try:
            context["previous_system"] = (
                SystemModule.objects.filter(
                    created_at__lt=system.created_at,
                    status__in=["deployed", "published"],
                )
                .order_by("-created_at")
                .first()
            )
        except SystemModule.DoesNotExist:
            context["previous_system"] = None

        try:
            context["next_system"] = (
                SystemModule.objects.filter(
                    created_at__gt=system.created_at,
                    status__in=["deployed", "published"],
                )
                .order_by("created_at")
                .first()
            )
        except SystemModule.DoesNotExist:
            context["next_system"] = None

        # Add breadcrumb data
        context["show_breadcrumbs"] = True
        context["current_system"] = system

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
