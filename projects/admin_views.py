"""
Projects Admin Views - Systems Management Interface
Extends the global admin system with projects-specific functionality
"""

from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from core.admin_views import (
    BaseAdminListView,
    BaseAdminCreateView,
    BaseAdminUpdateView,
    BaseAdminDeleteView,
    SlugAdminCreateView,
    BulkActionMixin,
    AjaxableResponseMixin,
)
from .models import (
    SystemModule,
    Technology,
    SystemType,
    SystemFeature,
    SystemImage,
    SystemMetric,
)
from .forms import SystemModuleForm, TechnologyForm, SystemTypeForm


class SystemsAdminDashboardView(BaseAdminListView):
    """Main Systems admin dashboard with enhanced metrics."""

    model = SystemModule
    template_name = 'projects/admin/dashboard.html'
    context_object_name = 'recent_systems'
    paginate_by = 8

    def get_queryset(self):
        return SystemModule.objects.select_related('system_type').prefetch_related(
            'technologies'
        ).order_by('-updated_at')[:8]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # System metrics using enhanced manager methods
        stats = SystemModule.objects.dashboard_stats()

        context.update({
            'title': 'Systems Command Center',
            'icon': 'fas fa-microchip',

            # Core metrics
            'total_systems': stats['total_systems'],
            'deployed_systems': stats['deployed_count'],
            'published_systems': stats['published_count'],
            'dev_systems': stats['in_development_count'],
            'featured_systems': stats['featured_count'],
            
            # Performance metrics
            'avg_completion': round(stats['avg_completion'], 1),
            'avg_performance': round(stats['avg_performance'], 1),
            
            # System health indicators
            'high_priority_systems': SystemModule.objects.high_priority().count(),
            'recently_updated': SystemModule.objects.recently_updated().count(),
            'systems_with_metrics': SystemModule.objects.with_performance_data().count(),
            
            # Technology insights
            'total_technologies': Technology.objects.count(),
            'active_technologies': Technology.objects.filter(
                systems__isnull=False
            ).distinct().count(),
            'popular_technologies': Technology.objects.annotate(
                usage_count=Count('systems')
            ).order_by('-usage_count')[:5],
            
            # System types breakdown
            'system_types': SystemType.objects.annotate(
                system_count=Count('systems')
            ).order_by('-system_count'),
            
            # Recent activity
            'recent_systems': self.get_queryset(),
            'critical_systems': SystemModule.objects.filter(priority=4),
            
            # Performance insights
            'top_performers': SystemModule.objects.filter(
                performance_score__isnull=False
            ).order_by('-performance_score')[:3],
            
            'systems_needing_attention': SystemModule.objects.filter(
                Q(performance_score__lt=70) | 
                Q(uptime_percentage__lt=95) |
                Q(health_status='critical')
            )[:5],
        })
        
        return context


class SystemListAdminView(BaseAdminListView, BulkActionMixin):
    """Enhanced system list view with filtering and bulk actions."""

    model = SystemModule
    template_name = "projects/admin/system_list.html"
    context_object_name = "systems"
    paginate_by = 20

    def get_queryset(self):
        queryset = SystemModule.objects.select_related("system_type").prefetch_related(
            "technologies"
        )

        # Apply filters
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        type_filter = self.request.GET.get("type")
        if type_filter:
            queryset = queryset.filter(system_type__slug=type_filter)

        priority_filter = self.request.GET.get("priority")
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        health_filter = self.request.GET.get("health")
        if health_filter:
            queryset = queryset.filter(health_status=health_filter)

        return queryset.order_by("-updated_at")

    def filter_queryset(self, queryset, search_query):
        """Enhanced search across multiple fields."""
        return queryset.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(system_type__name__icontains=search_query)
            | Q(technologies__name__icontains=search_query)
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Manage Systems",
                "create_url": reverse_lazy("projects:system_create_admin"),
                "edit_url_name": "projects:system_update_admin",
                "delete_url_name": "projects:system_delete_admin",
                "system_types": SystemType.objects.all(),
                "technologies": Technology.objects.all(),
                "current_filters": {
                    "status": self.request.GET.get("status"),
                    "type": self.request.GET.get("type"),
                    "priority": self.request.GET.get("priority"),
                    "health": self.request.GET.get("health"),
                },
            }
        )

        return context
    
    def handle_bulk_action(self, action, selected_ids):
        """Handle system-specific bulk actions."""
        queryset = SystemModule.objects.filter(id__in=selected_ids)

        if action == "deploy":
            count = queryset.filter(status="published").update(
                status="deployed", deployment_date=timezone.now()
            )
            messages.success(self.request, f"Successfully deployed {count} systems.")
        elif action == "publish":
            count = queryset.filter(status="in_development").update(status="published")
            messages.success(self.request, f"Successfully published {count} systems.")
        elif action == "feature":
            count = queryset.update(featured=True)
            messages.success(self.request, f"Successfully featured {count} systems.")
        elif action == "update_health":
            # Bulk health status update
            for system in queryset:
                system.update_health_status()
            messages.success(
                self.request,
                f"Successfully updated health status for {queryset.count()} systems.",
            )
        else:
            return super().handle_bulk_action(action, selected_ids)

        return self.get(self.request)


class SystemCreateAdminView(SlugAdminCreateView, AjaxableResponseMixin):
    """Create new system with enhanced features."""

    model = SystemModule
    form_class = SystemModuleForm
    template_name = "projects/admin/system_form.html"
    success_url = reverse_lazy("projects:system_list_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Create New System",
                "submit_text": "Create System",
                "icon": "fas fa-plus-circle",
                "available_types": SystemType.objects.all(),
                "available_technologies": Technology.objects.all(),
                "priority_choices": SystemModule.PRIORITY_CHOICES,
                "status_choices": SystemModule.STATUS_CHOICES,
            }
        )

        return context

    def form_valid(self, form):
        # Set initial values for new systems
        form.instance.health_status = "healthy"
        form.instance.completion_percent = 0

        return super().form_valid(form)


class SystemUpdateAdminView(BaseAdminUpdateView, AjaxableResponseMixin):
    """Update existing system."""

    model = SystemModule
    form_class = SystemModuleForm
    template_name = "projects/admin/system_form.html"
    success_url = reverse_lazy("projects:system_list_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": f"Edit System: {self.object.name}",
                "submit_text": "Update System",
                "icon": "fas fa-edit",
                "available_types": SystemType.objects.all(),
                "available_technologies": Technology.objects.all(),
                "priority_choices": SystemModule.PRIORITY_CHOICES,
                "status_choices": SystemModule.STATUS_CHOICES,
                # System-specific context
                "system_features": SystemFeature.objects.filter(system=self.object),
                "system_images": SystemImage.objects.filter(system=self.object),
                "system_metrics": SystemMetric.objects.filter(
                    system=self.object
                ).order_by("-recorded_at")[:5],
                "datalog_connections": self.object.related_posts.all(),
            }
        )

        return context

    def form_valid(self, form):
        # Update health status and metrics on save
        form.instance.update_health_status()

        return super().form_valid(form)


class SystemDeleteAdminView(BaseAdminDeleteView):
    """Delete system with comprehensive safety checks."""

    model = SystemModule
    success_url = reverse_lazy("projects:system_list_admin")

    def get_delete_warning(self):
        return f"This will permanently delete the system '{self.object.name}' and all associated data."

    def get_related_objects(self):
        """Show related objects that will be affected."""
        related = []

        # Features
        features_count = SystemFeature.objects.filter(system=self.object).count()
        if features_count > 0:
            related.append(f"{features_count} system feature(s)")

        # Images
        images_count = SystemImage.objects.filter(system=self.object).count()
        if images_count > 0:
            related.append(f"{images_count} system image(s)")

        # Metrics
        metrics_count = SystemMetric.objects.filter(system=self.object).count()
        if metrics_count > 0:
            related.append(f"{metrics_count} performance metric(s)")

        # DataLog connections
        datalog_connections = self.object.related_posts.count()
        if datalog_connections > 0:
            related.append(f"{datalog_connections} DataLog connection(s)")

        # Dependencies
        dependencies = self.object.dependencies.count()
        if dependencies > 0:
            related.append(f"{dependencies} system dependencies")

        return related


# Technology Management Views


class TechnologyListAdminView(BaseAdminListView, BulkActionMixin):
    """Technology management interface."""

    model = Technology
    template_name = "projects/admin/technology_list.html"
    context_object_name = "technologies"

    def get_queryset(self):
        return Technology.objects.annotate(
            system_count=Count("systems"), skill_count=Count("skills")
        ).order_by("-system_count", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Manage Technologies",
                "create_url": reverse_lazy("projects:technology_create_admin"),
                "edit_url_name": "projects:technology_update_admin",
                "delete_url_name": "projects:technology_delete_admin",
            }
        )

        return context


class TechnologyCreateAdminView(SlugAdminCreateView):
    """Create new technology."""

    model = Technology
    form_class = TechnologyForm
    success_url = reverse_lazy("projects:technology_list_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Add Technology",
                "icon": "fas fa-code-branch",
            }
        )
        return context


class TechnologyUpdateAdminView(BaseAdminUpdateView):
    """Update existing technology."""

    model = Technology
    form_class = TechnologyForm
    success_url = reverse_lazy("projects:technology_list_admin")


# System Type Management Views


class SystemTypeListAdminView(BaseAdminListView):
    """System type management interface."""

    model = SystemType
    template_name = "projects/admin/system_type_list.html"
    context_object_name = "system_types"

    def get_queryset(self):
        return SystemType.objects.annotate(system_count=Count("systems")).order_by(
            "name"
        )


class SystemTypeCreateAdminView(SlugAdminCreateView):
    """Create new system type."""

    model = SystemType
    form_class = SystemTypeForm
    success_url = reverse_lazy("projects:system_type_list_admin")


# API Views for AJAX functionality


class SystemMetricsAPIView(BaseAdminListView):
    """API endpoint for system metrics dashboard."""

    def get(self, request, *args, **kwargs):
        system_slug = kwargs.get("slug")

        if system_slug:
            # Individual system metrics
            try:
                system = SystemModule.objects.get(slug=system_slug)
                metrics = SystemMetric.objects.filter(system=system).order_by(
                    "-recorded_at"
                )[:10]

                data = {
                    "system": {
                        "name": system.name,
                        "performance_score": system.performance_score,
                        "uptime_percentage": system.uptime_percentage,
                        "health_status": system.health_status,
                        "completion_percent": system.completion_percent,
                    },
                    "metrics": [
                        {
                            "date": metric.recorded_at.isoformat(),
                            "performance": metric.performance_score,
                            "uptime": metric.uptime_percentage,
                            "response_time": metric.response_time_ms,
                            "error_rate": metric.error_rate,
                        }
                        for metric in metrics
                    ],
                }

                return JsonResponse(data)

            except SystemModule.DoesNotExist:
                return JsonResponse({"error": "System not found"}, status=404)

        else:
            # Dashboard metrics
            stats = SystemModule.objects.dashboard_stats()

            # Recent performance data
            recent_systems = SystemModule.objects.with_performance_data().order_by(
                "-updated_at"
            )[:5]

            data = {
                "overview": stats,
                "recent_performance": [
                    {
                        "name": system.name,
                        "performance": system.performance_score,
                        "uptime": system.uptime_percentage,
                        "health": system.health_status,
                    }
                    for system in recent_systems
                ],
                "system_distribution": {
                    "deployed": stats["deployed_count"],
                    "published": stats["published_count"],
                    "in_development": stats["in_development_count"],
                },
            }

            return JsonResponse(data)


class SystemHealthCheckAPIView(BaseAdminListView):
    """API endpoint for bulk health checks."""

    def post(self, request, *args, **kwargs):
        system_ids = request.POST.getlist("system_ids")

        if system_ids:
            systems = SystemModule.objects.filter(id__in=system_ids)
            updated_count = 0

            for system in systems:
                system.update_health_status()
                updated_count += 1

            return JsonResponse(
                {
                    "success": True,
                    "updated_count": updated_count,
                    "message": f"Updated health status for {updated_count} systems.",
                }
            )

        return JsonResponse(
            {"success": False, "message": "No systems selected."}, status=400
        )