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
from .models import SystemModule, Technology, SystemType, ArchitectureComponent, ArchitectureConnection
from .forms import SystemModuleForm, TechnologyForm, SystemTypeForm, ArchitectureComponentForm, ArchitectureConnectionForm


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
    success_url = reverse_lazy('aura_admin:projects:system_list')
    
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
    success_url = reverse_lazy('aura_admin:projects:system_list')
    
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
    success_url = reverse_lazy('aura_admin:projects:system_list')


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
            # TODO: Fix categories count so badges have counts on page
            'categories_count': self.get_technology_categories(),
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'category': self.request.GET.get('category', ''),
            }
        })
        return context
    
    def get_technology_categories(self):
        """Get technologies grouped by category"""

        tech = Technology.objects.all()
        
        categories = {}
        for t in tech:
            tech_cat = t.category
            if tech_cat not in categories:
                categories[tech_cat] = []
            categories[tech_cat].append(t)
        return categories


class TechnologyCreateAdminView(SlugAdminCreateView):
    """Create new technology."""
    
    model = Technology
    form_class = TechnologyForm
    template_name = 'projects/admin/technology_form.html'
    success_url = reverse_lazy('aura_admin:projects:technology_list')


class TechnologyUpdateAdminView(BaseAdminUpdateView):
    """Edit existing technology."""
    
    model = Technology
    form_class = TechnologyForm
    template_name = 'projects/admin/technology_form.html'
    success_url = reverse_lazy('aura_admin:projects:technology_list')


class TechnologyDeleteAdminView(BaseAdminDeleteView):
    """Delete technology."""
    
    model = Technology
    success_url = reverse_lazy('aura_admin:projects:technology_list')


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
    success_url = reverse_lazy('aura_admin:projects:system_type_list')


class SystemTypeUpdateAdminView(BaseAdminUpdateView):
    """Edit existing system type."""
    
    model = SystemType
    form_class = SystemTypeForm
    template_name = 'projects/admin/system_type_form.html'
    success_url = reverse_lazy('aura_admin:projects:system_type_list')


class SystemTypeDeleteAdminView(BaseAdminDeleteView):
    """Delete system type."""
    
    model = SystemType
    success_url = reverse_lazy('aura_admin:projects:system_type_list')


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


# ============================================================================
# ARCHITECTURE COMPONENT MANAGEMENT VIEWS
# ============================================================================

class ArchitectureComponentListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage architecture components with AURA styling"""
    
    model = ArchitectureComponent
    template_name = 'projects/admin/architecture_component_list.html'
    context_object_name = 'components'
    paginate_by = 20

    def get_queryset(self):
        queryset = ArchitectureComponent.objects.select_related(
            'system', 'technology'
        ).order_by('system__title', 'display_order', 'name')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(system__title__icontains=search_query)
            )
        
        # System filtering
        system_filter = self.request.GET.get('system', '')
        if system_filter:
            queryset = queryset.filter(system__slug=system_filter)
        
        # Component type filtering
        type_filter = self.request.GET.get('component_type', '')
        if type_filter:
            queryset = queryset.filter(component_type=type_filter)
        
        # Core component filter
        core_filter = self.request.GET.get('is_core', '')
        if core_filter == 'true':
            queryset = queryset.filter(is_core=True)
        elif core_filter == 'false':
            queryset = queryset.filter(is_core=False)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'title': 'Architecture Components',
            'subtitle': 'Manage system architecture components and diagrams',
            'systems': SystemModule.objects.all().order_by('title'),
            'component_types': ArchitectureComponent.COMPONENT_TYPES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'system': self.request.GET.get('system', ''),
                'component_type': self.request.GET.get('component_type', ''),
                'is_core': self.request.GET.get('is_core', ''),
            },
            'stats': {
                'total_components': ArchitectureComponent.objects.count(),
                'systems_with_architecture': SystemModule.objects.filter(
                    architecture_components__isnull=False
                ).distinct().count(),
                'core_components': ArchitectureComponent.objects.filter(is_core=True).count(),
                'total_connections': ArchitectureConnection.objects.count(),
            }
        })

        return context


class ArchitectureComponentCreateAdminView(BaseAdminCreateView):
    """Create new architecture component"""

    model = ArchitectureComponent
    form_class = ArchitectureComponentForm
    template_name = 'projects/admin/architecture_component_form.html'
    success_url = reverse_lazy('aura_admin:projects:architecture_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create Architecture Component',
            'subtitle': 'Add new component to system architecture',
        })
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Architecture component '{self.object.name}' created succesfully!")
        return response


class ArchitectureComponentUpdateAdminView(BaseAdminUpdateView):
    """Edit existing architecture component"""
    
    model = ArchitectureComponent
    form_class = ArchitectureComponentForm
    template_name = 'projects/admin/architecture_component_form.html'
    success_url = reverse_lazy('aura_admin:projects:architecture_component_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit Component: {self.object.name}',
            'subtitle': f'Update architecture component for {self.object.system.title}',
        })
        return context


class ArchitectureComponentDeleteAdminView(BaseAdminDeleteView):
    """Delete architecture component"""
    
    model = ArchitectureComponent
    success_url = reverse_lazy('aura_admin:projects:architecture_component_list')


# ============================================================================
# ARCHITECTURE CONNECTION MANAGEMENT VIEWS  
# ============================================================================

class ArchitectureConnectionListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage architecture connections"""
    
    model = ArchitectureConnection
    template_name = 'projects/admin/architecture_connection_list.html'
    context_object_name = 'connections'
    paginate_by = 20

    def get_queryset(self):
        return ArchitectureConnection.objects.select_related(
            'from_component', 'to_component', 'from_component__system',
            'to_component__system'
        ).order_by('from_component__system__title', 'from_component__name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'title': 'Architecture Connection',
            'subtitle': 'Manage component relationships and data flow',
            'connection_types': ArchitectureConnection.CONNECTION_TYPES,
            'stats': {
                'total_connections': ArchitectureConnection.objects.count(),
                'bidirectional_connections': ArchitectureConnection.objects.filter(
                    is_bidirectional=True
                ).count(),
                'systems_connected': ArchitectureConnection.objects.values(
                    'from_component__system'
                ).distinct().count(),
            }
        })

        return context


class ArchitectureConnectionCreateAdminView(BaseAdminCreateView):
    """Create new architecture connection"""
    
    model = ArchitectureConnection
    form_class = ArchitectureConnectionForm
    template_name = 'projects/admin/architecture_connection_form.html'
    success_url = reverse_lazy('aura_admin:projects:architecture_connection_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create Architecture Connection',
            'subtitle': 'Connect system components with data flow relationship',
        })
        return context


# ============================================================================
# AJAX UTILITY VIEWS
# ============================================================================

class ArchitecturePreviewView(BaseAdminUpdateView):
    """AJAX view to generate architecture diagram preview"""
    
    model = SystemModule
    
    def post(self, request, *args, **kwargs):
        system = self.get_object()
        
        if system.has_architecture_diagram():
            try:
                diagram_html = system.get_architecture_diagram()
                return JsonResponse({
                    'success': True,
                    'diagram_html': diagram_html,
                    'component_count': system.architecture_components.count(),
                    'connection_count': ArchitectureConnection.objects.filter(
                        from_component__system=system
                    ).count()
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No architecture components defined for this system.'
            })


class CreateDefaultArchitectureView(BaseAdminUpdateView):
    """AJAX view to create default architecture for a system"""
    
    model = SystemModule
    
    def post(self, request, *args, **kwargs):
        system = self.get_object()
        arch_type = request.POST.get('architecture_type', 'web_app')
        
        try:
            from .services.architecture_service import ArchitectureDiagramService
            
            # Clear existing architecture if requested
            if request.POST.get('clear_existing') == 'true':
                system.architecture_components.all().delete()
            
            # Create default architecture
            ArchitectureDiagramService.create_default_architecture(system, arch_type)
            
            return JsonResponse({
                'success': True,
                'message': f'Created {arch_type} architecture for {system.title}',
                'component_count': system.architecture_components.count(),
                'redirect_url': reverse_lazy('aura_admin:projects:system_architecture', kwargs={'pk': system.pk})
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
