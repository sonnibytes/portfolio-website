"""
Projects Admin Views - Systems Management Interface
Extends the global admin system with projects-specific functionality
Version 2.0
"""

from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.db import models

from core.admin_views import (
    BaseAdminListView,
    BaseAdminCreateView, 
    BaseAdminUpdateView,
    BaseAdminDeleteView,
    SlugAdminCreateView,
    BulkActionMixin
)
from .models import SystemModule, Technology, SystemType
from .forms import SystemModuleForm, TechnologyForm, SystemTypeForm


class ProjectsAdminDashboardView(BaseAdminListView):
    """Main Systems admin dashboard with enhanced metrics."""
    
    model = SystemModule
    template_name = 'projects/admin/dashboard.html'
    context_object_name = 'recent_systems'
    paginate_by = 10
    
    def get_queryset(self):
        return SystemModule.objects.select_related('system_type').prefetch_related('technologies').order_by('-updated_at')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        total_systems = SystemModule.objects.count()
        deployed_systems = SystemModule.objects.filter(status='deployed').count()
        published_systems = SystemModule.objects.filter(status='published').count()
        in_dev_systems = SystemModule.objects.filter(status='in_development').count()
        
        # Performance metrics
        avg_completion = SystemModule.objects.aggregate(
            avg_completion=Avg('completion_percent')
        )['avg_completion'] or 0
        
        avg_performance = SystemModule.objects.filter(
            performance_score__isnull=False
        ).aggregate(
            avg_performance=Avg('performance_score')
        )['avg_performance'] or 0
        
        # Technology and type stats
        popular_technologies = Technology.objects.annotate(
            system_count=Count('systems')
        ).order_by('-system_count')[:5]
        
        popular_system_types = SystemType.objects.annotate(
            system_count=Count('systems')
        ).order_by('-system_count')[:5]
        
        # Recent activity
        recent_deployments = SystemModule.objects.filter(
            status='deployed'
        ).order_by('-updated_at')[:5]
        
        context.update({
            'title': 'Systems Command Center',
            'subtitle': 'Manage portfolio projects and technologies',
            
            # Core statistics
            'total_systems': total_systems,
            'deployed_systems': deployed_systems,
            'published_systems': published_systems,
            'in_dev_systems': in_dev_systems,
            'total_technologies': Technology.objects.count(),
            'total_system_types': SystemType.objects.count(),
            
            # Performance metrics
            'avg_completion': round(avg_completion, 1),
            'avg_performance': round(avg_performance, 1),
            'high_priority_systems': SystemModule.objects.filter(priority__gte=3).count(),
            
            # Content insights
            'popular_technologies': popular_technologies,
            'popular_system_types': popular_system_types,
            
            # Recent activity
            'recent_systems': self.get_queryset(),
            'recent_deployments': recent_deployments,
            'recent_technologies': Technology.objects.order_by('-id')[:5],
            
            # Quick stats for dashboard cards
            'deployment_percentage': round((deployed_systems / total_systems * 100) if total_systems > 0 else 0, 1),
            'completion_percentage': round(avg_completion, 1),
        })
        
        return context


class SystemListAdminView(BaseAdminListView, BulkActionMixin):
    """Enhanced system list view with filtering and bulk actions."""
    
    model = SystemModule
    template_name = 'projects/admin/system_list.html'
    context_object_name = 'systems'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SystemModule.objects.select_related('system_type').prefetch_related('technologies').order_by('-updated_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(subtitle__icontains=search_query)
            )
        
        # Status filtering
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # System type filtering
        system_type_filter = self.request.GET.get('system_type', '')
        if system_type_filter:
            queryset = queryset.filter(system_type__slug=system_type_filter)
        
        # Priority filtering
        priority_filter = self.request.GET.get('priority', '')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Featured filtering
        featured_filter = self.request.GET.get('featured', '')
        if featured_filter == 'true':
            queryset = queryset.filter(featured=True)
        elif featured_filter == 'false':
            queryset = queryset.filter(featured=False)
            
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'title': 'Manage Systems',
            'subtitle': 'All portfolio projects and systems',
            'system_types': SystemType.objects.all(),
            'status_choices': SystemModule.STATUS_CHOICES,
            'priority_choices': SystemModule.PRIORITY_CHOICES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'status': self.request.GET.get('status', ''),
                'system_type': self.request.GET.get('system_type', ''),
                'priority': self.request.GET.get('priority', ''),
                'featured': self.request.GET.get('featured', ''),
            }
        })
        
        return context


class SystemCreateAdminView(BaseAdminCreateView):
    """Create new system."""
    
    model = SystemModule
    form_class = SystemModuleForm
    template_name = 'projects/admin/system_form.html'
    success_url = reverse_lazy('core:admin:projects:system_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create New System',
            'subtitle': 'Add a new portfolio project',
        })
        return context
    
    def form_valid(self, form):
        # Auto-generate system_id if not set
        if not form.instance.system_id:
            # Get next system number
            last_system = SystemModule.objects.aggregate(
                max_id=Max('id')
            )['max_id'] or 0
            form.instance.system_id = f"SYS-{(last_system + 1):03d}"
        
        # Auto-generate slug if not provided
        if not form.instance.slug and form.instance.title:
            form.instance.slug = slugify(form.instance.title)
        
        # Set author to current user
        form.instance.author = self.request.user
        
        # Set default completion based on status
        if not form.instance.completion_percent:
            status_defaults = {
                'draft': 10,
                'in_development': 50,
                'testing': 80,
                'deployed': 95,
                'published': 100,
            }
            form.instance.completion_percent = status_defaults.get(form.instance.status, 0)
        
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'System "{self.object.title}" created successfully!'
        )
        return response


class SystemUpdateAdminView(BaseAdminUpdateView):
    """Edit existing system."""
    
    model = SystemModule
    form_class = SystemModuleForm
    template_name = 'projects/admin/system_form.html'
    success_url = reverse_lazy('core:admin:projects:system_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit System: {self.object.title}',
            'subtitle': 'Update system information',
        })
        return context


class SystemDeleteAdminView(BaseAdminDeleteView):
    """Delete system."""
    
    model = SystemModule
    success_url = reverse_lazy('core:admin:projects:system_list')


# Technology Management Views
class TechnologyListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage technologies."""
    
    model = Technology
    template_name = 'projects/admin/technology_list.html'
    context_object_name = 'technologies'
    
    def get_queryset(self):
        queryset = Technology.objects.annotate(
            system_count=Count('systems')
        ).order_by('category', '-system_count', 'name')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Manage Technologies',
            'subtitle': 'Technology stack and tools',
            'category_choices': Technology.CATEGORY_CHOICES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'category': self.request.GET.get('category', ''),
            }
        })
        return context


class TechnologyCreateAdminView(SlugAdminCreateView):
    """Create new technology."""
    
    model = Technology
    form_class = TechnologyForm
    template_name = 'projects/admin/technology_form.html'
    success_url = reverse_lazy('core:admin:projects:technology_list')


class TechnologyUpdateAdminView(BaseAdminUpdateView):
    """Edit existing technology."""
    
    model = Technology
    form_class = TechnologyForm
    template_name = 'projects/admin/technology_form.html'
    success_url = reverse_lazy('core:admin:projects:technology_list')


class TechnologyDeleteAdminView(BaseAdminDeleteView):
    """Delete technology."""
    
    model = Technology
    success_url = reverse_lazy('core:admin:projects:technology_list')


# System Type Management Views
class SystemTypeListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage system types."""
    
    model = SystemType
    template_name = 'projects/admin/system_type_list.html'
    context_object_name = 'system_types'
    
    def get_queryset(self):
        queryset = SystemType.objects.annotate(
            system_count=Count('systems')
        ).order_by('display_order', 'name')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Manage System Types',
            'subtitle': 'Project categories and types',
        })
        return context


class SystemTypeCreateAdminView(SlugAdminCreateView):
    """Create new system type."""
    
    model = SystemType
    form_class = SystemTypeForm
    template_name = 'projects/admin/system_type_form.html'
    success_url = reverse_lazy('core:admin:projects:system_type_list')


class SystemTypeUpdateAdminView(BaseAdminUpdateView):
    """Edit existing system type."""
    
    model = SystemType
    form_class = SystemTypeForm
    template_name = 'projects/admin/system_type_form.html'
    success_url = reverse_lazy('core:admin:projects:system_type_list')


class SystemTypeDeleteAdminView(BaseAdminDeleteView):
    """Delete system type."""
    
    model = SystemType
    success_url = reverse_lazy('core:admin:projects:system_type_list')


# AJAX API Views for dynamic functionality
class SystemStatusToggleView(BaseAdminUpdateView):
    """AJAX view to toggle system status."""
    
    model = SystemModule
    
    def post(self, request, *args, **kwargs):
        system = self.get_object()
        
        # Cycle through statuses: draft -> in_development -> testing -> deployed -> published
        status_cycle = {
            'draft': 'in_development',
            'in_development': 'testing', 
            'testing': 'deployed',
            'deployed': 'published',
            'published': 'draft'
        }
        
        new_status = status_cycle.get(system.status, 'in_development')
        system.status = new_status
        
        # Update completion percentage based on status
        completion_mapping = {
            'draft': 10,
            'in_development': 50,
            'testing': 80,
            'deployed': 95,
            'published': 100,
        }
        system.completion_percent = completion_mapping.get(new_status, system.completion_percent)
        
        system.save()
        
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'new_status_display': system.get_status_display(),
            'completion_percent': float(system.completion_percent)
        })


class SystemFeatureToggleView(BaseAdminUpdateView):
    """AJAX view to toggle system featured status."""
    
    model = SystemModule
    
    def post(self, request, *args, **kwargs):
        system = self.get_object()
        system.featured = not system.featured
        system.save()
        
        return JsonResponse({
            'success': True,
            'featured': system.featured
        })