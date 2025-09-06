# blog/admin_views.py
"""
Blog Admin Views - DataLogs Management Interface
Extends the global admin system with blog-specific functionality
Version 2.0
"""

from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg, Sum
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView
from django.db import models

from datetime import timedelta

from core.admin_views import (
    BaseAdminListView,
    BaseAdminCreateView, 
    BaseAdminUpdateView,
    BaseAdminDeleteView,
    SlugAdminCreateView,
    AuthorAdminCreateView,
    StatusAdminCreateView,
    BulkActionMixin,
    BaseAdminView,
    AdminAccessMixin
)
from .models import Post, Category, Tag, Series, SeriesPost, SystemLogEntry
from projects.models import SystemModule
from .forms import PostForm, CategoryForm, TagForm, SeriesForm


class BlogAdminDashboardView(BaseAdminListView):
    """Main DataLogs admin dashboard with enhanced metrics."""
    
    model = Post
    template_name = 'blog/admin/dashboard.html'
    context_object_name = 'recent_posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('tags').order_by('-created_at')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        total_posts = Post.objects.count()
        published_posts = Post.objects.filter(status='published').count()
        draft_posts = Post.objects.filter(status='draft').count()
        
        # Calculate totals and averages
        avg_reading_time = Post.objects.aggregate(avg_time=Avg('reading_time'))['avg_time'] or 0
        total_reading_time = Post.objects.aggregate(total_time=Sum('reading_time'))['total_time'] or 0
        
        # Popular content
        popular_categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).order_by('-post_count')[:5]
        
        popular_tags = Tag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).order_by('-post_count')[:5]
        
        context.update({
            'title': 'DataLogs Command Center',
            'subtitle': 'Manage technical logs and documentation',
            
            # Core statistics
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'featured_posts': Post.objects.filter(featured=True).count(),
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),
            'total_series': Series.objects.count(),
            
            # Content metrics
            'avg_reading_time': round(avg_reading_time, 1),
            'total_reading_time': total_reading_time,
            'total_words': sum(len(post.content.split()) for post in Post.objects.all()),
            
            # Popular content
            'popular_categories': popular_categories,
            'popular_tags': popular_tags,
            
            # Recent activity
            'recent_posts': self.get_queryset(),
            'recent_categories': Category.objects.order_by('-id')[:3],
            'recent_tags': Tag.objects.order_by('-id')[:5],
            
            # Quick stats for dashboard cards
            'published_percentage': round((published_posts / total_posts * 100) if total_posts > 0 else 0, 1),
            'featured_percentage': round((Post.objects.filter(featured=True).count() / total_posts * 100) if total_posts > 0 else 0, 1),
        })
        
        return context


class PostListAdminView(BaseAdminListView, BulkActionMixin):
    """Enhanced post list view with filtering and bulk actions."""
    
    model = Post
    template_name = 'blog/admin/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        # Status filtering
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Category filtering
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category__slug=category_filter)
        
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
            'title': 'DataLogs Management',
            'subtitle': 'Manage your datalog entries across projects',
            'categories': Category.objects.all(),
            'categories_count': self.get_post_categories(),
            'series': Series.objects.all(),
            'status_choices': Post.STATUS_CHOICES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'status': self.request.GET.get('status', ''),
                'category': self.request.GET.get('category', ''),
                'featured': self.request.GET.get('featured', ''),
            }
        })
        
        return context
    
    def get_post_categories(self):
        """Get posts grouped by category"""
        cats = Category.objects.all()


class PostCreateAdminView(BaseAdminCreateView):
    """Create new DataLog entry."""
    
    model = Post
    form_class = PostForm
    template_name = 'blog/admin/post_form.html'
    success_url = reverse_lazy('aura_admin:blog:post_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create New DataLog',
            'subtitle': 'Add a new technical log entry',
        })
        return context
    
    def form_valid(self, form):
        #  # Debug logging
        # print(f"DEBUG: User is authenticated: {self.request.user.is_authenticated}")
        # print(f"DEBUG: Current user: {self.request.user}")
        # print(f"DEBUG: Form instance author before: {getattr(form.instance, 'author', 'NO AUTHOR FIELD')}")
        
        # Auto-assign author - CRITICAL
        form.instance.author = self.request.user
        
        # print(f"DEBUG: Form instance author after: {form.instance.author}")
        
        # Auto-generate slug if not provided
        if not form.instance.slug and form.instance.title:
            form.instance.slug = slugify(form.instance.title)
            # print(f"DEBUG: Generated slug: {form.instance.slug}")
        
        # Auto-calculate reading time if not set
        if not form.instance.reading_time and form.instance.content:
            content_words = len(form.instance.content.split())
            form.instance.reading_time = max(1, content_words // 200)  # 200 WPM
            # print(f"DEBUG: Calculated reading time: {form.instance.reading_time}")
        
        # Handle save button actions
        if 'save_draft' in self.request.POST:
            form.instance.status = 'draft'
            # print("DEBUG: Setting status to draft")
        elif 'save_publish' in self.request.POST:
            form.instance.status = 'published'
            # print("DEBUG: Setting status to published")
        
        # Set published_date when publishing for the first time
        if form.instance.status == 'published' and not form.instance.published_date:
            form.instance.published_date = timezone.now()
        
        # print(f"DEBUG: About to save with author: {form.instance.author}")
        
        try:
            response = super().form_valid(form)
            # print("DEBUG: Save successful!")
            messages.success(
                self.request, 
                f'DataLog "{self.object.title}" created successfully!'
            )
            return response
        except Exception as e:
            print(f"DEBUG: Save failed with error: {e}")
            print(f"DEBUG: Form instance dict: {form.instance.__dict__}")
            raise


class PostUpdateAdminView(BaseAdminUpdateView):
    """Edit existing DataLog entry."""
    
    model = Post
    form_class = PostForm
    template_name = 'blog/admin/post_form.html'
    success_url = reverse_lazy('aura_admin:blog:post_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit DataLog: {self.object.title}',
            'subtitle': 'Update technical log entry',
        })
        return context
    
    def form_valid(self, form):
        # Ensure author is preserved or set
        if not form.instance.author:
            form.instance.author = self.request.user
        
        # Store the old status to check if we're publishing for the first time
        old_status = None
        if form.instance.pk:
            try:
                old_post = Post.objects.get(pk=form.instance.pk)
                old_status = old_post.status
            except Post.DoesNotExist:
                old_status = 'draft'
        
        # Handle save button actions
        if 'save_draft' in self.request.POST:
            form.instance.status = 'draft'
        elif 'save_publish' in self.request.POST:
            form.instance.status = 'published'
        
        # Set published_date when publishing for the first time
        if (form.instance.status == 'published' and 
            old_status != 'published' and 
            not form.instance.published_date):
            form.instance.published_date = timezone.now()
        
        # Auto-calculate reading time if not set
        if not form.instance.reading_time:
            content_words = len(form.instance.content.split())
            form.instance.reading_time = max(1, content_words // 200)  # 200 WPM
        
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'DataLog "{self.object.title}" updated successfully!'
        )
        return response


class PostDeleteAdminView(BaseAdminDeleteView):
    """Delete DataLog entry."""
    
    model = Post
    success_url = reverse_lazy('aura_admin:blog:post_list')


# Category Management Views
class CategoryListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage DataLog categories."""
    
    model = Category
    template_name = 'blog/admin/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        queryset = Category.objects.annotate(
            post_count=Count('posts')
        ).order_by('name')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_posts = Post.objects.filter(status='published').count()
        active_categories = self.get_queryset().filter(post_count__gt=0).count()
        avg_posts_per_category = total_posts // active_categories if active_categories > 0 else 0

        context.update({
            'total_posts': total_posts,
            'active_categories': active_categories,
            'avg_posts_per_category': avg_posts_per_category,
        })
        return context


class CategoryCreateAdminView(SlugAdminCreateView):
    """Create new category."""
    
    model = Category
    form_class = CategoryForm
    template_name = 'blog/admin/category_form.html'
    success_url = reverse_lazy('aura_admin:blog:category_list')


class CategoryUpdateAdminView(BaseAdminUpdateView):
    """Edit existing category."""
    
    model = Category
    form_class = CategoryForm
    template_name = 'blog/admin/category_form.html'
    success_url = reverse_lazy('aura_admin:blog:category_list')


class CategoryDeleteAdminView(BaseAdminDeleteView):
    """Delete category."""
    
    model = Category
    success_url = reverse_lazy('aura_admin:blog:category_list')


# Tag Management Views
class TagListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage DataLog tags."""
    
    model = Tag
    template_name = 'blog/admin/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        queryset = Tag.objects.annotate(
            post_count=Count('posts')
        ).order_by('-post_count', 'name')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        popular_tags = Tag.objects.annotate(
                post_count=Count('posts', filter=Q(posts__status='published'))
            ).filter(post_count__gt=3).order_by('-post_count')
        
        posts = Post.objects.annotate(
            tag_count=Count("tags", filter=Q(status="published"))
        )
        
        total_tag_usage = posts.aggregate(usage=Sum("tag_count"))["usage"] or 0

        avg_tags_per_post = posts.aggregate(avg=Avg("tag_count"))["avg"] or 0


        context.update({
            'popular_tags': popular_tags[:10],
            'total_tag_usage': total_tag_usage,
            'popular_tags_count': len(popular_tags) if popular_tags else 0,
            'avg_tags_per_post': avg_tags_per_post,

        })
        return context


class TagCreateAdminView(SlugAdminCreateView):
    """Create new tag."""
    
    model = Tag
    form_class = TagForm
    template_name = 'blog/admin/tag_form.html'
    success_url = reverse_lazy('aura_admin:blog:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For new tags, set stats to 0
        context.update({
            'tag_total_posts': 0,
            'tag_published_posts': 0,
            'tag_first_post': None,
        })
        return context


class TagUpdateAdminView(BaseAdminUpdateView):
    """Edit existing tag."""
    
    model = Tag
    form_class = TagForm
    template_name = 'blog/admin/tag_form.html'
    success_url = reverse_lazy('aura_admin:blog:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add Tag stats
        if self.object:
            total_posts = Post.objects.filter(tags=self.object).count()
            published_posts = Post.objects.filter(tags=self.object, status='published').count()
            first_post = Post.objects.filter(tags=self.object).order_by('created_at').first()

            context.update({
                'tag_total_posts': total_posts,
                'tag_published_posts': published_posts,
                'tag_first_post': first_post,
            })
        return context


class TagDeleteAdminView(BaseAdminDeleteView):
    """Delete tag."""
    
    model = Tag
    success_url = reverse_lazy('aura_admin:blog:tag_list')


# Series Management Views
class SeriesListAdminView(BaseAdminListView, BulkActionMixin):
    """Manage DataLog series."""
    
    model = Series
    template_name = 'blog/admin/series_list.html'
    context_object_name = 'series_list'
    
    def get_queryset(self):
        return Series.objects.annotate(
            actual_post_count=Count('posts')
        ).order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Manage Series',
            'subtitle': 'DataLog series and collections',
        })
        return context


class SeriesCreateAdminView(SlugAdminCreateView):
    """Create new series."""
    
    model = Series
    form_class = SeriesForm
    template_name = 'blog/admin/series_form.html'
    success_url = reverse_lazy('aura_admin:blog:series_list')


class SeriesUpdateAdminView(BaseAdminUpdateView):
    """Edit existing series."""
    
    model = Series
    form_class = SeriesForm
    template_name = 'blog/admin/series_form.html'
    success_url = reverse_lazy('aura_admin:blog:series_list')


class SeriesDeleteAdminView(BaseAdminDeleteView):
    """Delete series."""
    
    model = Series
    success_url = reverse_lazy('aura_admin:blog_series_list')


class SeriesPostsManageView(AdminAccessMixin, BaseAdminView, TemplateView):
    """Manage posts within a series - add, remove, reorder."""
    
    model = Series
    template_name = 'blog/admin/series_posts_manage.html'
    
    def get_object(self):
        return get_object_or_404(Series, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.get_object()
        
        # Get current posts in series (ordered)
        series_posts = series.posts.all().order_by('order')
        
        # Get all published posts not in this series
        available_posts = Post.objects.filter(
            status='published'
        ).exclude(
            id__in=series_posts.values_list('post__id', flat=True)
        ).order_by('-published_date')
        
        context.update({
            'series': series,
            'series_posts': series_posts,
            'available_posts': available_posts,
            'title': f'Manage Posts: {series.title}',
            'subtitle': 'Add, remove, and reorder posts in this series',
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle adding/removing posts from series."""
        series = self.get_object()
        action = request.POST.get('action')
        
        if action == 'add_post':
            post_id = request.POST.get('post_id')
            try:
                post = Post.objects.get(id=post_id, status='published')
                # Get the next order number
                last_order = series.posts.aggregate(
                    max_order=models.Max('order')
                )['max_order'] or 0
                
                # Add post to series
                from .models import SeriesPost
                SeriesPost.objects.create(
                    series=series,
                    post=post,
                    order=last_order + 1
                )
                
                messages.success(request, f'Added "{post.title}" to series.')
                
            except Post.DoesNotExist:
                messages.error(request, 'Post not found.')
        
        elif action == 'remove_post':
            series_post_id = request.POST.get('series_post_id')
            try:
                from .models import SeriesPost
                series_post = SeriesPost.objects.get(id=series_post_id, series=series)
                post_title = series_post.post.title
                series_post.delete()
                
                # Reorder remaining posts
                self._reorder_series_posts(series)
                
                messages.success(request, f'Removed "{post_title}" from series.')
                
            except SeriesPost.DoesNotExist:
                messages.error(request, 'Series post not found.')
        
        elif action == 'reorder_posts':
            # Handle reordering via AJAX
            post_orders = request.POST.getlist('post_orders')
            print(f"DEBUG: Received post_orders: {post_orders}")  # Debug log
            
            try:
                from .models import SeriesPost

                # Update each post's order
                for i, series_post_id in enumerate(post_orders, 1):
                    updated_count = SeriesPost.objects.filter(
                        id=series_post_id, series=series
                    ).update(order=i)
                    print(
                        f"DEBUG: Updated SeriesPost {series_post_id} to order {i}, affected rows: {updated_count}"
                    )

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Updated order for {len(post_orders)} posts",
                    }
                )

            except Exception as e:
                print(f"DEBUG: Error in reorder_posts: {e}")
                return JsonResponse({"success": False, "error": str(e)})
        
        return redirect('aura_admin:blog:series_posts_manage', pk=series.pk)
    
    def _reorder_series_posts(self, series):
        """Reorder series posts to fill gaps."""
        from .models import SeriesPost
        series_posts = SeriesPost.objects.filter(series=series).order_by('order')
        for i, series_post in enumerate(series_posts, 1):
            if series_post.order != i:
                series_post.order = i
                series_post.save()


# AJAX API Views for dynamic functionality
class PostStatusToggleView(BaseAdminUpdateView):
    """AJAX view to toggle post status."""
    
    model = Post
    
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        old_status = post.status
        new_status = 'published' if post.status == 'draft' else 'draft'
        
        # Handle published_date when changing status
        if new_status == 'published' and not post.published_date:
            post.published_date = timezone.now()
        elif new_status == 'draft':
            post.published_date = None
        
        post.status = new_status
        post.save()
        
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'new_status_display': post.get_status_display(),
            'published_date': post.published_date.isoformat() if post.published_date else None
        })


class PostFeatureToggleView(BaseAdminUpdateView):
    """AJAX view to toggle post featured status."""
    
    model = Post
    
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        post.featured = not post.featured
        post.save()
        
        return JsonResponse({
            'success': True,
            'featured': post.featured
        })


# ==== RESTRUCTURE for Learning Journey Storytelling ====
# - Admin-Facing Learning Metrics with Improvements and Gap Analysis
# - GOAL: Personal Learning Management System
# ==== Will Replace Scattered DataLogs Admin Suite Flow ====
class LearningJourneyDashboardView(AdminAccessMixin, TemplateView):
    """Main Learning Journeys Dashboard - replaces BlogAdminDashboardView"""

    template_name = "blog/admin/learning_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Learning Journey Metrics
        active_journeys = Series.objects.filter(is_complete=False).count()
        completed_journeys = Series.objects.filter(is_complete=True).count()
        total_discoveries = Post.objects.count()
        published_discoveries = Post.objects.filter(status='published').count()

        
        # Calculate avg journey completion
        journeys_with_posts = Series.objects.annotate(
            completion_rate=Count('posts') * 100.0 / models.F('post_count')
        )
        avg_journey_completion = journeys_with_posts.aggregate(
            avg_completion=Avg('completion_rate')
        )['avg_completion'] or 0

        
        # Recent learning activity
        recent_discoveries = Post.objects.select_related(
            'category', 'author'
        ).prefetch_related('tags').order_by('-created_at')[:8]

        
        # Active learning journeys with recent posts
        active_learning_journeys = Series.objects.filter(
            is_complete=False
        ).annotate(
            post_count_actual=Count('posts')
        ).prefetch_related('posts__post')[:6]


        # System-knowledge connections
        system_knowledge_connections = SystemLogEntry.objects.select_related(
            'system', 'post'
        ).values('system__id', 'system__title').annotate(
            post_count=Count('post'),
            recent_discovery=models.Max('post__created_at')
        ).order_by('-post_count')[:6]


        # Knowledge domains (Categories) with Stats
        knowledge_domain_stats = Category.objects.annotate(
            post_count=Count('posts'),
            journey_count=Count('posts__series_associations__series', distinct=True)
        ).filter(post_count__gt=0).order_by('-post_count')

        context.update({
            'title': 'Learning Journeys Dashboard',
            'subtitle': 'Personal knowledge management and learning progress',

            # Main metrics
            'active_journeys': active_journeys,
            'completed_journeys': completed_journeys,
            'total_discoveries': total_discoveries,
            'published_discoveries': published_discoveries,
            'avg_journey_completion': avg_journey_completion,

            # Learning data
            'active_learning_journeys': active_learning_journeys,
            'recent_discoveries': recent_discoveries,
            'system_knowledge_connections': system_knowledge_connections,
            'knowledge_domain_stats': knowledge_domain_stats,

            # Additional metrics
            'knowledge_domains': Category.objects.count(),
            'active_domains': Category.objects.filter(posts__isnull=False).distinct().count(),
            'system_connections': SystemLogEntry.objects.count(),
            'connected_systems': SystemLogEntry.objects.values('system').distinct().count(),
            'discoveries_this_month': Post.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'avg_reading_time': Post.objects.aggregate(
                avg_time=Avg('reading_time')
            )['avg_time'] or 0,
        })

        return context


class EnhancedPostCreateView(StatusAdminCreateView):
    """Learning-first post creation with journey integration"""

    model = Post
    form_class = PostForm
    template_name = "blog/admin/post_form_enhanced.html"
    success_url = reverse_lazy('aura_admin:blog:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        
        # Add Journey suggestions based on recent activity
        recent_journeys = Series.objects.filter(
            is_complete=False
        ).order_by('-updated_at')[:5]

        
        # Add System suggestions for connections
        active_systems = SystemModule.objects.filter(
            status__in=['deployed', 'published', 'in_development']
        ).order_by('-updated_at')[:8]

        
        # Add Category suggestions with post counts
        popular_categories = Category.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0).order_by('-post_count')[:6]


        context.update({
            'title': 'Document New Discovery',
            'subtitle': 'Capture what you learned and connect it to your learning journey',
            'recent_journeys': recent_journeys,
            'active_systems': active_systems,
            'popular_categories': popular_categories,
            # Allow inline journey creation
            'journey_creation_enabled': True,
        })
        return context

    def form_valid(self, form):
        # Handle journey assignment during post creation
        journey_id = self.request.POST.get('learning_journey')
        if journey_id:
            try:
                journey = Series.objects.get(id=journey_id)
                # Create the post first
                response = super().form_valid(form)

                # Then add to journey
                from .models import SeriesPost
                last_order = journey.posts.aggregate(
                    max_order=models.Max('order')
                )['max_order'] or 0

                SeriesPost.objects.create(
                    series=journey,
                    post=self.object,
                    order=last_order + 1
                )

                messages.success(
                    self.request,
                    f'Discovery added to learning journey: {journey.title}'
                )
                return response
            except Series.DoesNotExist:
                pass
        
        return super().form_valid(form)


class LearningJourneyListView(BaseAdminListView):
    """Enhanced series list focused on learning progression"""

    model = Series
    template_name = "blog/admin/learning_journey_list.html"
    context_object_name = 'learning_journeys'

    def get_queryset(self):
        return Series.objects.annotate(
            actual_post_count=Count('posts'),
            completion_percentage=models.Case(
                models.When(post_count=0, then=0),
                default=Count('posts') * 100 / models.F('post_count'),
                output_field=models.IntegerField()
            ),
            last_activity=models.Max('posts__post__updated_at')
        ).order_by('-last_activity', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add learning-focused stats
        total_journeys = self.get_queryset().count()
        active_journeys = self.get_queryset().filter(is_complete=False).count()
        completed_journeys = self.get_queryset().filter(is_complete=True).count()

        context.update({
            'title': 'Learning Journeys',
            'subtitle': 'Manage your knowledge building paths and learning progression',
            'total_journeys': total_journeys,
            'active_journeys': active_journeys,
            'completed_journeys': completed_journeys,
            'learning_velocity': Post.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        })
        return context


class LearningJourneyDetailView(BaseAdminView, DetailView):
    """Enhanced journey management with inline post organization"""

    model = Series
    template_name = 'blog/admin/learning_journey_detail.html'
    context_object_name = 'learning_journey'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        journey = self.object

        # Get Journey posts with order
        journey_posts = SeriesPost.objects.filter(
            series=journey
        ).select_related('post').order_by('order')


        # Get available posts for adding to journey
        available_posts = Post.objects.filter(
            status='published'
        ).exclude(
            id__in=journey_posts.values_list('post__id', flat=True)
        ).order_by('-created_at')[:20]


        # Calculate journey metrics
        total_reading_time = sum(
            jp.post.reading_time for jp in journey_posts if jp.post.reading_time
        )


        # System connections for this journey
        system_connections = SystemLogEntry.objects.filter(
            post__in=[jp.post for jp in journey_posts]
        ).select_related('system').values(
            'system__id', 'system__title'
        ).annotate(
            connection_count=Count('id')
        ).order_by('-connection_count')


        context.update({
            'title': f'Learning Journey: {journey.title}',
            'subtitle': 'Organize and track your learning progression',
            'journey_posts': journey_posts,
            'available_posts': available_posts,
            'total_reading_time': total_reading_time,
            'system_connections': system_connections,
            'completion_percentage': journey.get_progress_percentage(),
            'knowledge_domains': Category.objects.filter(
                posts__in=[jp.post for jp in journey_posts]
            ).distinct(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle journey management actions"""

        journey = self.get_object()
        action = request.POST.get('action')

        if action == 'add_post':
            post_id = request.POST.get('post_id')
            try:
                post = Post.objects.get(id=post_id, status='published')
                last_order = journey.posts.aggregate(
                    max_order=models.Max('order')
                )['max_order'] or 0

                SeriesPost.objects.create(
                    series=journey,
                    post=post,
                    order=last_order + 1
                )

                messages.success(
                    request,
                    f'Added "{post.title}" to learning journey'
                )
            except Post.DoesNotExist:
                messages.error(request, 'Post not found')
        
        elif action == 'mark_complete':
            journey.is_complete = not journey.is_complete
            journey.save()

            status = 'completed' if journey.is_complete else 'reopened'
            messages.success(
                request,
                f'Learning journey {status}: {journey.title}'
            )

        elif action == 'reorder_posts':
            # Handle AJAX reordering
            post_orders = request.POST.getList('post_orders')
            for i, series_post_id in enumerate(post_orders, 1):
                SeriesPost.objects.filter(
                    id=series_post_id, series=journey
                ).update(order=i)
            
            return JsonResponse({
                'success': True,
                'message': f'Reordered {len(post_orders)} posts'
            })
        
        return redirect('aura_admin:blog:learning_journey_detail', pk=journey.pk)
