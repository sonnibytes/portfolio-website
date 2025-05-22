from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import SystemModule, SystemType, Technology
# For related datalogs
from blog.models import Post


class SystemListView(ListView):
    """View for displaying list of all systems/projects."""

    model = SystemModule
    template_name = 'projects/system_list.html'
    context_object_name = 'systems'
    paginate_by = 9

    def get_queryset(self):
        queryset = SystemModule.objects.filter(status='published')

        # Filter by system type if provided
        system_type = self.request.GET.get('type')
        if system_type:
            queryset = queryset.filter(system_type__slug=system_type)

        # Filter by technology if provided
        technology = self.request.GET.get("tech")
        if technology:
            queryset = queryset.filter(technologies__slug=technology)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(subtitle__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            ).distinct()
        
        # Sort functionality
        sort = self.request.GET.get('sort', 'latest')
        if sort == "latest":
            queryset = queryset.order_by("-created")
        elif sort == "oldest":
            queryset = queryset.order_by("created")
        elif sort == "name":
            queryset = queryset.order_by("title")
        elif sort == "complexity":
            queryset = queryset.order_by("-complexity")

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add system types for filtering
        context['system_types'] = SystemType.objects.annotate(
            system_count=Count('systems')
        )

        # Add technologies for filtering
        context['technologies'] = Technology.objects.annotate(
            system_count=Count('systems')
        )

        # Get current filters for navigation
        context['current_type'] = self.request.GET.get('type', '')
        context["current_tech"] = self.request.GET.get("tech", "")
        context["current_sort"] = self.request.GET.get("sort", "latest")
        context["search_query"] = self.request.GET.get("search", "")

        # Get featured systems
        context['featured_systems'] = SystemModule.objects.filter(
            status='published', featured=True
        )[:3]

        return context
    

class SystemDetailView(DetailView):
    """View for displaying details of a specific system/project."""

    model = SystemModule
    template_name = 'projects/system_detail.html'
    context_object_name = 'system'

    def get_queryset(self):
        # Base queryset, including only published systems
        queryset = SystemModule.objects.filter(status='published')

        # If user is logged in and is author/staff, show drafts too
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                queryset = SystemModule.objects.all()
            else:
                queryset = SystemModule.objects.filter(
                    Q(status='published') | Q(author=self.request.user)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.get_object()

        # Get related blog posts - will need to be tweaked with new join model
        context['related_posts'] = Post.objects.filter(
            status='published', related_projects=system
        ).exclude(id=system.id)

        # Get similar systems based on system type and technologies
        similar_systems = SystemModule.objects.filter(
            status='published'
        ).exclude(id=system.id)

        # Filter by same system type if available
        if system.system_type:
            similar_systems = similar_systems.filter(
                system_type=system.system_type
            )
        
        # Filter by shared technologies
        tech_ids = system.technologies.values_list('id', flat=True)
        if tech_ids:
            similar_systems = similar_systems.filter(
                technologies__id__in=tech_ids
            ).distinct()
        
        context['similar_systems'] = similar_systems[:3]

        # Get all images for the gallery
        context['gallery_images'] = system.imgaes.all()

        # Get all features
        context['features'] = system.features/all()

        # Determine if the user is author/staff for edit permissions
        context['is_author'] = (
            self.request.user.is_authenticated and
            (self.request.user == system.author or self.request.user.is_staff)
        )

        return context
    
    