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
from django.views.generic import TemplateView
from django.db import models

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
from .models import Post, Category, Tag, Series
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
            'title': 'Manage DataLogs',
            'subtitle': 'All technical logs and entries',
            'categories': Category.objects.all(),
            'status_choices': Post.STATUS_CHOICES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'status': self.request.GET.get('status', ''),
                'category': self.request.GET.get('category', ''),
                'featured': self.request.GET.get('featured', ''),
            }
        })
        
        return context


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
        context.update({
            'title': 'Manage Categories',
            'subtitle': 'DataLog organization categories',
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
        context.update({
            'title': 'Manage Tags',
            'subtitle': 'DataLog tagging system',
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
