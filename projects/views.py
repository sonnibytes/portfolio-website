from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.utils import timezone

from .models import SystemModule, SystemType, Technology, SystemFeature, SystemMetric
from blog.models import Post, SystemLogEntry


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
        sort_by = self.request.GET.get('sort', '-created')
        valid_sorts = ['-created', 'title', '-completion_percent', 'complexity']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # System types for filtering
        context['system_types'] = SystemType.objects.annotate(
            system_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(systems_count__gt=0)

        # Technologies for filtering
        context['technologies'] = Technology.objects.annotate(
            system_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(systems_count__gt=0).order_by('category', 'name')

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

        return context


class SystemModuleDetailView(DetailView):
    """Detailed system view with specs, logs, and metrics."""

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
                created__lt=system.created,
                status__in=['deployed', 'published']
            ).order_by('-created').first()
        except SystemModule.DoesNotExist:
            context['previous_system'] = None

        try:
            context['next_system'] = SystemModule.objects.filter(
                created__gt=system.created,
                status__in=['deployed', 'published']
            ).order_by('created').first()
        except SystemModule.DoesNotExist:
            context['next_system'] = None

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
        ).order_by('-created')

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
        ).order_by('-created')

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


class SystemDashboardView(ListView):
    """HUD-style dashboard overview of all systems."""

    model = SystemModule
    template_name = "projects/systems_dashboard.html"
    context_object_name = "recent_systems"

    def get_queryset(self):
        return SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).order_by('-created')[:6]

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
            'post', 'systems'
        ).order_by('-logged_at')[:5]

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
        sort_by = self.request.GET.get('sort', '-created')
        valid_sorts = ['-created', 'title', '-completion_percent', 'complexity', '-updated']
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
            'sort': self.request.GET.get('sort', '-created'),
        }

        return context

