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
from collections import Counter

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
            usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
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
        performing_systems = SystemModule.objects.with_performance_data()

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
                    "icon": "tachometer-alt",
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


class EnhancedSystemListView(ListView):
    """
    Enhanced System List using all new manager methods and model enhancements
    Features: Advanced filtering, search, performance analytics, unified container styling
    """

    model = SystemModule
    template_name = "projects/system_list.html"
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        """Enhanced filtered query using new manager methods w optimized queries."""
        # Start w optimized base query
        queryset = SystemModule.objects.select_related('system_type', 'author').prefetch_related('technologies', 'features')

        # Apply enhanced filters using new manager methods
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

        # Technology filter
        tech_filter = self.request.GET.get("tech")
        if tech_filter:
            queryset = queryset.filter(technologies__slug=tech_filter)

        # System Type Filter
        type_filter = self.request.GET.get("type")
        if type_filter:
            queryset = queryset.filter(system_type__slug=type_filter)

        # Complexity filter
        complexity_filter = self.request.GET.get('complexity')
        if complexity_filter:
            queryset = queryset.filter(complexity=complexity_filter)

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

        # Enhanced Ordering
        order = self.request.GET.get("order", "recent")
        if order == "recent":
            queryset = queryset.order_by("-updated_at")
        elif order == "name":
            queryset = queryset.order_by("title")
        elif order == "completion":
            queryset = queryset.order_by("-completion_percent")
        elif order == "performance":
            queryset = queryset.order_by("-performance_score")
        elif order == "priority":
            queryset = queryset.order_by("-priority", "-updated_at")
        elif order == "complexity":
            queryset = queryset.order_by("-complexity")
        elif order == "status":
            queryset = queryset.order_by("status", "-updated_at")

        return queryset

    def get_context_data(self, **kwargs):
        """Enhanced context using new manager methods and dashboard stats."""
        context = super().get_context_data(**kwargs)

        # Use new dashboard_stats() method
        context['dashboard_stats'] = SystemModule.objects.dashboard_stats()

        # Enhanced filter data
        context.update({
            # Tecchnology stats using new methods
            'technologies': Technology.objects.annotate(
                usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
            ).filter(usage_count__gt=0).order_by('-usage_count')[:10],

            # System types w counts
            'system_types': SystemType.objects.annotate(
                usage_count=Count('systems')
            ).filter(usage_count__gt=0).order_by('-usage_count'),

            # Quick stats using new manager methods
            'quick_stats': {
                "featured_count": SystemModule.objects.featured().count(),
                "deployed_count": SystemModule.objects.deployed().count(),
                "in_development_count": SystemModule.objects.in_development().count(),
                "high_priority_count": SystemModule.objects.high_priority().count(),
                "with_performance_count": SystemModule.objects.with_performance_data().count(),
                "recently_updated_count": SystemModule.objects.recently_updated(7).count(),
            },

            # Performance analytics
            'performance_analytics': self.get_performance_analytics(),

            # Active filters for display
            'active_filters': self.get_active_filters(),

            # Pagination info
            'total_systems': self.get_queryset().count(),

            # Featured Systems for sidebar
            'featured_systems': SystemModule.objects.featured().deployed()[:4],
        })

        return context

    def get_performance_analytics(self):
        """Get performance analytics using enhanced model methods."""
        systems_with_performance = SystemModule.objects.with_performance_data()

        if not systems_with_performance.exists():
            return None

        return {
            'avg_performance': systems_with_performance.aggregate(
                avg=Avg('performance_score')
            )['avg'],
            'avg_uptime': systems_with_performance.aggregate(
                avg=Avg('uptime_percentage')
            )['avg'],
            'total_daily_users': systems_with_performance.aggregate(
                total=Sum('daily_users')
            )['total'] or 0,
            'performance_distribution': self.get_performance_distribution(),
        }

    def get_performance_distribution(self):
        """Get distribution of systems by performance score."""
        systems = SystemModule.objects.with_performance_data()

        distribution = {
            'excellent': systems.filter(performance_score__gte=90).count(),
            'good': systems.filter(performance_score__range=[70, 89]).count(),
            'fair': systems.filter(performance_score__range=[50, 69]).count(),
            'poor': systems.filter(performance_score__lt=50).count(),
        }

        return distribution

    def get_active_filters(self):
        """Get currently active filters for display."""
        filters = {}

        if self.request.GET.get('status'):
            filters['Status'] = self.request.GET.get('status').replace('_', '').title()

        if self.request.GET.get('tech'):
            try:
                tech = Technology.objects.get(slug=self.request.GET.get('tech'))
                filters['Technology'] = tech.name
            except:
                pass

        if self.request.GET.get('type'):
            try:
                sys_type = SystemType.objects.get(slug=self.request.GET.get('type'))
                filters['Type'] = sys_type.name
            except:
                pass

        if self.request.GET.get('complexity'):
            complexity_map = {
                1: 'Basic',
                2: 'Intermediate',
                3: 'Advanced',
                4: 'Complex',
                5: 'Enterprise'
            }
            complexity = int(self.request.GET.get('complexity'))
            filters['Complexity'] = complexity_map.get(complexity, 'Unknown')

        if self.request.GET.get('search'):
            filters['Search'] = self.request.GET.get('search')

        return filters

# ===================== ENHANCED SYSTEM DETAIL VIEW =====================


class SystemControlInterfaceView(DetailView):
    """
    System Control Interface - Nested System Command Center

    Like logging into a specific system's control panel with nested interfaces:
    - Main system overview dashboard
    - DataLogs control panel (nested view of related logs)
    - Technology stack analyzer
    - Performance monitoring console
    - Feature management interface
    - Development timeline viewer
    - Dependencies analyzer
    """

    model = SystemModule
    template_name = "projects/system_control_interface.html"
    context_object_name = "system"

    def get_queryset(self):
        """Optimized queryset for system control interface"""
        return SystemModule.objects.select_related(
            "system_type", "author"
        ).prefetch_related(
            "technologies",
            "features",
            "images",
            "metrics",
            "dependencies",
            "dependents",
            "log_entries__post",
            "log_entries__post__category",
            "log_entries__post__tags")

    def get_context_data(self, **kwargs):
        """Enhanced context for system control interface"""
        context = super().get_context_data(**kwargs)
        system = self.object

        # Get active control panel from URL parameter
        active_panel = self.request.GET.get('panel', 'overview')
        context['active_panel'] = active_panel

        # System metrics and dashboard data
        context.update({
            # Enhanced system metrics using model methods
            'system_metrics': system.get_dashboard_metrics(),
            'deployment_readiness': system.get_deployment_readiness(),
            'health_status': system.get_health_status(),

            # Performance analytics
            'performance_data': self.get_performance_analytics(system),

            # Related systems using enhanced manager methods
            'related_systems': SystemModule.objects.filter(technologies__in=system.technologies.all())
            .exclude(id=system.id)
            .distinct()[:6],

            # Similar systems by type and status
            'similar_systems': self.get_similar_systems(system),

            # Panel-specific context data
            'panel_data': self.get_panel_data(system, active_panel),

            # Navigation data for control interface
            'control_panels': self.get_control_panels(system),

            # Quick access data
            'quick_stats': self.get_quick_stats(system),

            # For System Info
            'system': system,
        })

        return context

    def get_performance_analytics(self, system):
        """Get detailed performance analytics for the system"""
        analytics = {
            'completion_score': system.completion_percent or 0,
            'complexity_rating': system.get_complexity_display(),
            'status_color': system.get_status_badge_color(),
            'progress_color': system.get_progress_color(),
        }

        # Add performance metrics if available
        if hasattr(system, 'performance_score') and system.performance_score:
            analytics.update({
                'performance_score': system.performance_score,
                'uptime_percentage': getattr(system, 'uptime_percecntage', None),
                'daily_users': getattr(system, 'daily_users', None),
                'response_time': getattr(system, 'response_time_ms', None),
            })

        return analytics

    def get_similar_systems(self, system):
        """Get similar systems using enhanced manager methods."""
        if system.status == 'deployed':
            return SystemModule.objects.deployed().filter(
                system_type=system.system_type
            ).exclude(id=system.id)[:4]
        elif system.status in ['in_development', 'testing']:
            return SystemModule.objects.in_development().filter(
                system_type=system.system_type
            ).exclude(id=system.id)[:4]
        else:
            return SystemModule.objects.filter(
                system_type=system.system_type
            ).exclude(id=system.id)[:4]

    def get_control_panels(self, system):
        """Define available control panels w dynamic counts."""
        panels = [
            {
                "id": "overview",
                "name": "System Overview",
                "icon": "tachometer-alt",
                "description": "Main system dashboard and metrics",
                "count": None,
                "color": "teal",
            },
            {
                "id": "details",
                "name": "System Details",
                "icon": "info-circle",
                "description": "Comprehensive system documentation and challenges",
                "count": None,
                "color": "navy",
            },
            {
                "id": "datalogs",
                "name": "DataLogs",
                "icon": "file-alt",
                "description": "Related development logs and documentation",
                "count": system.log_entries.count(),
                "color": "lavender",
            },
            {
                "id": "technologies",
                "name": "Tech Stack",
                "icon": "code",
                "description": "Technology analysis and dependencies",
                "count": system.technologies.count(),
                "color": "coral",
            },
            {
                "id": "features",
                "name": "Features",
                "icon": "puzzle-piece",
                "description": "System features and capabilities",
                "count": system.features.count() if hasattr(system, "features") else 0,
                "color": "mint",
            },
            {
                "id": "performance",
                "name": "Performance",
                "icon": "chart-line",
                "description": "Performance metrics and monitoring",
                "count": None,
                "color": "yellow",
            },
            {
                "id": "dependencies",
                "name": "Dependencies",
                "icon": "project-diagram",
                "description": "System dependencies and relationships",
                "count": system.dependencies.count()
                if hasattr(system, "dependencies")
                else 0,
                "color": "navy",
            },
            {
                "id": "timeline",
                "name": "Timeline",
                "icon": "history",
                "description": "Development timeline and milestones",
                "count": None,
                "color": "gunmetal",
            },
        ]

        return panels

    def get_panel_data(self, system, panel):
        """Get data specific to the active control panel."""
        if panel == 'details':
            return self.get_details_panel_data(system)
        elif panel == 'datalogs':
            return self.get_datalogs_panel_data(system)
        elif panel == 'technologies':
            return self.get_technologies_panel_data(system)
        elif panel == 'features':
            return self.get_features_panel_data(system)
        elif panel == 'performance':
            return self.get_performance_panel_data(system)
        elif panel == 'dependencies':
            return self.get_dependencies_panel_data(system)
        elif panel == "timeline":
            return self.get_timeline_panel_data(system)
        else:
            # Overview
            return self.get_overview_panel_data(system)

    def get_details_panel_data(self, system):
        """System details panel - conprehensive documentation."""
        # Get challenges related to DataLogs
        challenges_logs = []
        if system.challenges:
            # Search for DataLogs that might address challenges mentioned in challenges field
            challenges_keywords = self.extract_keywords_from_markdown(system.challenges)

            # Find posts that contain challenge-related keywords
            for keyword in challenges_keywords[:5]:  # Limit to top 5 keywords
                related_posts = system.log_entries.select_related('post').filter(
                    Q(post__title__icontains=keyword) |
                    Q(post__content__icontains=keyword) |
                    Q(post__excerpt__icontains=keyword)
                )[:3]
                for entry in related_posts:
                    if entry not in challenges_logs:
                        challenges_logs.append({
                            'log_entry': entry,
                            'keyword': keyword,
                            'relevance': 'addresses challenges'
                        })
        return {
            'has_description': bool(system.description),
            'has_technical_details': bool(system.technical_details),
            'has_challenges': bool(system.challenges),
            'description_content': system.rendered_content() if system.description else None,
            'technical_details_content': system.render_technical_details() if system.technical_details else None,
            'challenges_content': system.rendered_challenges() if system.challenges else None,
            'challenges_logs': challenges_logs,
            'content_stats': {
                'description_word_count': len(system.description.split()) if system.description else 0,
                'technical_word_count': len(system.technical_details.split()) if system.technical_details else 0,
                'challenges_word_count': len(system.challenges.split()) if system.challenges else 0,
            }
        }

    def get_overview_panel_data(self, system):
        """Main overview panel data."""
        return {
            'recent_activity': system.log_entries.select_related('post').order_by('-created_at')[:5],
            'key_technologies': system.technologies.all()[:6],
            'completion_breakdown': {
                'completed': system.completion_percent or 0,
                'remaining': 100 - (system.completion_percent or 0)
            },
            'status_info': {
                'current_status': system.get_status_display(),
                'status_color': system.get_status_badge_color(),
                'last_updated': system.updated_at,
            }
        }

    def get_datalogs_panel_data(self, system):
        """DataLogs control panel - nested interface for system logs."""
        # Get all related logs w full details
        log_entries = system.log_entries.select_related(
            'post', 'post__category', 'post__author'
        ).prefetch_related(
            'post__tags'
        ).order_by('-created_at')

        # Group logs by category
        logs_by_category = {}
        for entry in log_entries:
            category = entry.post.category.name if entry.post.category else 'Uncategorized'
            if category not in logs_by_category:
                logs_by_category[category] = []
            logs_by_category[category].append(entry)

        # Get log stats
        log_stats = {
            'total_logs': log_entries.count(),
            'categories_count': len(logs_by_category),
            'recent_logs': log_entries[:8],
            'logs_by_priority': {
                'high': log_entries.filter(priority__gte=3).count(),
                'medium': log_entries.filter(priority=2).count(),
                'low': log_entries.filter(priority=1).count(),
            }
        }

        return {
            'logs_by_category': logs_by_category,
            'log_stats': log_stats,
            'all_log_entries': log_entries,
            'connection_types': SystemLogEntry.objects.filter(
                system=system
            ).values_list('connection_type', flat=True).distinct()
        }

    def get_technologies_panel_data(self, system):
        """Technology stack analyzer panel."""
        technologies = system.technologies.all()

        # Analyze technology usage across similar systems
        tech_analysis = {}
        for tech in technologies:
            similar_systems = SystemModule.objects.filter(
                technologies=tech,
                system_type=system.system_type
            ).exclude(id=system.id)

            tech_analysis[tech.name] = {
                'technology': tech,
                'usage_in_similar': similar_systems.count(),
                'similar_systems': similar_systems[:3],
                'category': getattr(tech, 'category', 'Unknown'),
            }

        return {
            'technologies': technologies,
            'tech_analysis': tech_analysis,
            'tech_stats': {
                'total_technologies': technologies.count(),
                'categories': technologies.values_list('category', flat=True).distinct(),
                'primary_stack': technologies.filter(is_primary=True) if hasattr(technologies.first(), 'is_primary') else technologies[:3],
            }
        }

    def get_features_panel_data(self, system):
        """Enhanced Features management interface with smart content generation."""
        features_data = {'features': [], 'feature_stats': {}}

        if hasattr(system, 'features'):
            features = system.features.all()

            feature_stats = {
                'total_features': features.count(),
                'completed_features': features.filter(implementation_status='completed').count() if features else 0,
                'in_progress_features': features.filter(implementation_status='in_progress').count() if features else 0,
                'planned_features': features.filter(implementation_status='planned').count() if features else 0,
            }

            features_data = {
                "features": features,
                "feature_stats": feature_stats,
                "features_by_status": {
                    "completed": features.filter(implementation_status="completed"),
                    "in_progress": features.filter(implementation_status="in_progress"),
                    "planned": features.filter(implementation_status="planned"),
                }
                if features
                else {},
            }

        # Smart content generation for features_overview and future_enhancecments
        features_data.update({
            'features_overview_content': self.get_or_generate_features_overview(system, features_data),
            'future_enhancements_content': self.get_or_generate_future_enhancements(system, features_data),
            'has_custom_features_overview': bool(system.features_overview),
            'has_custom_future_enhancements': bool(system.future_enhancements),
        })

        return features_data

    def get_or_generate_features_overview(self, system, features_data):
        """Get features over or generate from related features."""
        if system.features_overview:
            # Use existing content
            return system.features_overview

        # Auto-generate from related features if available
        if features_data['features']:
            completed_features = features_data['features_by_status'].get('completed', [])
            in_progress_features = features_data['features_by_status'].get('in_progress', [])

            generated_content = f'### {system.title} Features\n\n'

            if completed_features:
                generated_content += '#### **Implemented Features**\n\n'
                for feature in completed_features[:5]:  # Limit to 5
                    generated_content += f'- **{feature.title}**: {feature.description[:100]}{"..." if len(feature.description) > 100 else ""}\n'
                    generated_content += "\n"
            if in_progress_features:
                generated_content += '#### **Features in Development**\n\n'
                for feature in in_progress_features[:3]:  # Limit to 3
                    generated_content += f'- **{feature.title}**: {feature.description[:100]}{"..." if len(feature.description) > 100 else ""}\n'
                    generated_content += "\n"

            generated_content += f"*Total features: {features_data['feature_stats']['total_features']} ({features_data['feature_stats']['completed_features']} completed)*"

            return generated_content

        # Fallback: Generate from system description or technologies
        if system.description:
            return f'## Key Capabilities\n\n{system.excerpt or 'This system provides essential functionality for the portfolio ecosystem.'}\n\n*Features documentation is being developed.**'

        return None

    def get_or_generate_future_enhancements(self, system, features_data):
        """Get future enhanccements or generate from planned features."""
        if system.future_enhancements:
            # Use existing content
            return system.future_enhancements

        # Auto-Generate from planned features
        if features_data['features']:
            planned_features = features_data['features_by_status'].get('planned', [])

            if planned_features:
                generated_content = f'## {system.title} Roadmap\n\n'
                generated_content += "### **Planned Enhancements**\n\n"

                for i, feature in enumerate(planned_features[:6], 1):  # Limit to 6
                    generated_content += f"{i}. **{feature.title}**\n"
                    generated_content += f"   {feature.description[:150]}{'...' if len(feature.description) > 150 else ''}\n\n"

                generated_content += "### **Development Priorities**\n\n"
                high_priority = [f for f in planned_features if hasattr(f, "priority") and f.priority >= 3]
                if high_priority:
                    generated_content += "**High Priority:**\n"
                    for feature in high_priority[:3]:
                        generated_content += f"- {feature.title}\n"
                else:
                    generated_content += "Priorities are being evaluated based on user feedback and technical requirements.\n"

                return generated_content

        # Fallback: Generate generic roadmap
        if system.status in ["in_development", "testing"]:
            return f"## Development Roadmap\n\n### **Current Focus**\n\nCompleting core functionality and preparing for deployment.\n\n### 🎯 **Next Steps**\n\n- Performance optimization\n- Enhanced user experience\n- Additional feature development\n- Comprehensive testing\n\n*Detailed roadmap will be updated as development progresses.*"
        elif system.status == "deployed":
            return f"## Enhancement Roadmap\n\n### **Continuous Improvement**\n\nThis system is actively maintained with regular updates and enhancements.\n\n### 🎯 **Areas of Focus**\n\n- Performance monitoring and optimization\n- Feature enhancement based on usage analytics\n- Security updates and improvements\n- Integration with new technologies\n\n*Enhancement requests are evaluated based on user feedback and technical feasibility.*"

        return None

    def extract_keywords_from_markdown(self, markdown_content):
        """Extract key terms from markdown content for finding related logs."""
        if not markdown_content:
            return []

        # Remove additional formatting
        text = re.sub(r"[#*`\[\]()_-]", " ", markdown_content)

        # Split into words and filter for meaningful terms
        words = text.lower().split()

        # Filter out common words and keep technical terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

        keywords = [word for word in words if len(word) > 3 and word not in stopwords]

        # Count frequency and return top keywords
        word_counts = Counter(keywords)

        return [word for word, count in word_counts.most_common(10)]

    def get_performance_panel_data(self, system):
        """Performance monitoring controls."""
        performance_data = {
            'has_performance_data': hasattr(system, 'performance_score') and system.performance_score,
            'current_metrics': {},
            'performance_history': [],
            'benchmarks': {}
        }

        if performance_data['has_performance_data']:
            performance_data['current_metrics'] = {
                'performance_score': system.performance_score,
                'uptime': getattr(system, 'uptime_percentage', None),
                'daily_users': getattr(system, 'daily_users', None),
                'response_time': getattr(system, 'response_time_ms', None),
            }

            # Mock performance history
            # TODO: Replace w real data
            performance_data['performance_history'] = [
                {'date': '2024-01-01', 'performance': 85, 'uptime': 99.2},
                {'date': '2024-01-02', 'performance': 88, 'uptime': 99.5},
                {'date': '2024-01-03', 'performance': 92, 'uptime': 99.8},
            ]

        return performance_data

    def get_dependencies_panel_data(self, system):
        """Dependencies and relationship analyzer."""
        dependencies_data = {
            'dependencies': [],
            'dependents': [],
            'dependency_graph': {},
            'risk_analysis': {}
        }

        if hasattr(system, 'dependencies'):
            dependencies_data['dependencies'] = system.dependencies.select_related('depends_on').all()

        if hasattr(system, 'dependents'):
            dependencies_data['dependents'] = system.dependents.select_related('system').all()

        return dependencies_data

    def get_timeline_panel_data(self, system):
        """Development timeline and milestones."""
        timeline_events = []

        # Add system creation
        timeline_events.append({
            'date': system.created_at,
            'event': 'System Created',
            'type': 'milestone',
            'description': f'System {system.title} was created'
        })

        # Add related log entries as timeline events
        for log_entry in system.log_entries.select_related('post').order_by('created_at'):
            timeline_events.append({
                'date': log_entry.created_at,
                'event': log_entry.post.title,
                'type': 'log',
                'description': log_entry.post.excerpt or 'Development log entry',
                'url': log_entry.post.get_absolute_url()
            })

        # Sort timeline by date
        timeline_events.sort(key=lambda x: x['date'], reverse=True)

        return {
            'timeline_events': timeline_events[:20],  # Limit to recent events
            'milestones': [event for event in timeline_events if event['type'] == 'milestone'],
            'development_logs': [event for event in timeline_events if event['type'] == 'log'],
        }

    def get_quick_stats(self, system):
        """Quick access stats for the system interface."""
        return {
            'completion_percent': system.completion_percent or 0,
            'technologies_count': system.technologies.count(),
            'logs_count': system.log_entries.count(),
            'days_since_update': (timezone.now().date() - system.updated_at.date()).days,
            'status_display': system.get_status_display(),
            'complexity_level': system.get_complexity_display(),
        }


# ===================== ENHANCED SYSTEM TYPE VIEWS =====================

class SystemTypeOverviewView(ListView):
    """
    Global System Type Overview - Shows all systems grouped by type
    This view renders when no specific system type is selected
    """
    model = SystemType
    template_name = "projects/system_type_overview.html"
    context_object_name = "system_types"

    def get_queryset(self):
        return SystemType.objects.prefetch_related(
            "systems__technologies"
        ).annotate(
            systems_count=Count('systems', filter=Q(systems__status='published')),
            deployed_count=Count('systems', filter=Q(systems__status='deployed')),
            avg_completion=Avg('systems__completion_percent')
        ).order_by('display_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Global stats using enhanced manager methods
        all_systems = SystemModule.objects.all()

        context.update({
            'page_title': 'System Types Overview',
            'total_systems': all_systems.count(),
            'total_deployed': all_systems.deployed().count(),
            'total_featured': all_systems.featured().count(),
            'total_in_development': all_systems.in_development().count(),

            # Performance distribution
            'performance_distribution': self.get_performance_distribution(),

            # Technology distribution across all types
            'top_technologies': Technology.objects.annotate(
                systems_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
            ).order_by('-systems_count')[:8],

            # Recent activity
            'recently_updated': all_systems.recently_updated(7).select_related('system_type')[:5],

            # Type analytics
            'type_analytics': self.get_type_analytics(),
        })

        return context

    def get_performance_distribution(self):
        """Get performance score distribution across all systems."""
        systems = SystemModule.objects.with_performance_data()

        return {
            'excellent': systems.filter(performance_score__gte=90).count(),
            'good': systems.filter(performance_score__range=[70, 89]).count(),
            'fair': systems.filter(performance_score__range=[50, 69]).count(),
            'poor': systems.filter(performance_score__lt=50).count(),
        }

    def get_type_analytics(self):
        """Get analytics for each system type."""
        type_data = []

        for system_type in self.get_queryset():
            type_systems = SystemModule.objects.filter(system_type=system_type)

            # Calculate health score based on deployment ratio and completion
            deployed_ratio = type_systems.deployed().count() / max(type_systems.count(), 1)
            avg_completion = type_systems.aggregate(avg=Avg('completion_percent'))['avg'] or 0
            health_score = (deployed_ratio * 50) + (avg_completion * 0.5)

            type_data.append({
                'type': system_type,
                'systems_count': type_systems.count(),
                'deployed_count': type_systems.deployed().count(),
                'featured_count': type_systems.featured().count(),
                'avg_completion': avg_completion,
                'health_score': min(100, health_score),
                'top_technologies': Technology.objects.filter(
                    systems__system_type=system_type
                ).annotate(
                    count=Count('systems')
                ).order_by('-count')[:3]
            })


class SystemTypeDetailView(DetailView):
    """
    Enhanced System Type Detail View - Focused analytics for spcific type
    This view renders when specific system type is selected
    """
    model = SystemType
    template_name = "projects/system_type_detail.html"
    context_object_name = "system_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system_type = self.object

        # Get systems for this type using enhancecd manager methods
        type_systems = SystemModule.objects.filter(system_type=system_type)

        # Filter systems based on user params
        systems_queryset = self.get_filtered_systems(type_systems)

        context.update({
            'systems': systems_queryset.select_related('system_type').prefetch_related('technologies'),

            # Type-spcific metrics
            'type_metrics': self.get_type_metrics(type_systems),

            # Technology analysis for this type
            'technology_analysis': self.get_technology_analysis(type_systems),

            # Performance insights
            'performance_insights': self.get_performance_insights(type_systems),

            # Development timeline
            'development_timeline': self.get_development_timeline(type_systems),
        })






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
