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
from blog.models import Post


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