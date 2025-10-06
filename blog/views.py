from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
# from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.html import escape
from django.utils.crypto import get_random_string
from django.db.models import Count, Q, Avg, Sum, Case, When, IntegerField, Value
from django.db.models.functions import Extract, Length
from markdownx.utils import markdownify
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings


from datetime import datetime, timedelta, date
import calendar
import os
import re
from uuid import uuid4
import pprint
from collections import defaultdict, OrderedDict
import json

from .models import Post, Category, Tag, Series, SeriesPost, PostView, Subscriber
from .forms import PostForm, CategoryForm, TagForm, SeriesForm
from .templatetags.datalog_tags import datalog_search_suggestions


class PostListView(ListView):
    """Enhanced post list view with search integration."""
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6  # 6 posts per page (2 rows of 3)

    def get_queryset(self):
        """Get posts, potentially filtered by search or category."""
        queryset = Post.objects.filter(
            status="published").select_related('category', 'author').prefetch_related('tags').order_by('-published_date')

        # Handle search from unified search interface
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )

        # Apply filters
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)

        has_code = self.request.GET.get('has_code')
        if has_code == 'true':
            queryset = queryset.exclude(featured_code__exact='')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # # Helper function for search context
        # context.update(get_search_context(self.request))

        # Existing context
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['featured_post'] = Post.objects.filter(
            status='published',
            featured=True
        ).select_related('category').prefetch_related('tags', 'related_systems').first()

        # Add search context
        query = self.request.GET.get('q', '').strip()

        # Enhanced context for new template
        context.update({
            # Page configuration
            # 'page_title': 'DataLogs Archive',
            # 'page_subtitle': 'Technical Insights and Development Journey',
            'page_icon': 'fas fa-database',
            'show_breadcrumbs': False,
            'show_filters': True,
            'show_stats': False,
            'show_header_metrics': True,

            # Statistics for the interface
            'total_posts': Post.objects.filter(status='published').count(),
            'total_words': sum(post.content.split().__len__() for post in Post.objects.filter(status='published')),
            'avg_reading_time': Post.objects.filter(
                status='published').aggregate(
                avg_time=Avg('reading_time')
            )['avg_time'] or 8,
            'total_views': PostView.objects.count() if hasattr(Post, 'views') else 0,
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),

            # Current context for breadcrumbs/navigation
            'current_category': None,  # Will be set in CategoryView
            'current_post': None,      # Will be set in PostDetailView

            # Enhanced categories with post counts
            'categories_with_counts': Category.objects.annotate(
                post_count=Count('posts', filter=Q(posts__status='published'))
            ).filter(post_count__gt=0).order_by('name'),

            # Popular tags for quick filters
            'popular_tags': Tag.objects.annotate(
                post_count=Count('posts', filter=Q(posts__status='published'))
            ).filter(post_count__gt=0).order_by('-post_count')[:10],

            # Recent activity for analytics
            'recent_posts_count': Post.objects.filter(
                status='published',
                published_date__gte=timezone.now() - timedelta(days=30)
            ).count(),

            # Featured post enhanced data
            'featured_post_data': None,
        })

        # Enhanced featured post data
        if context['featured_post']:
            featured = context['featured_post']
            context['featured_post_data'] = {
                'has_code': bool(featured.featured_code),
                'code_language': featured.featured_code_format,
                'code_lines': len(featured.featured_code.split('\n')) if featured.featured_code else 0,
                'estimated_complexity': 'Beginner' if featured.reading_time < 5 else 'Intermediate' if featured.reading_time < 15 else 'Advanced',
                'related_systems': featured.related_systems.filter(status__in=['deployed', 'published'])[:2],
                'primary_system': featured.get_primary_system() if hasattr(featured, 'get_primary_system') else None,
            }

        return context


class PostDetailView(DetailView):
    """View for a single blog post."""
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Get related posts by tags
        post_tags_ids = post.tags.values_list('id', flat=True)
        related_posts = Post.objects.filter(
            tags__in=post_tags_ids,
            status='published'
        ).exclude(id=post.id).distinct()[:3]

        # Get previous and next posts
        try:
            previous_post = Post.objects.filter(
                published_date__lt=post.published_date,
                status='published'
            ).order_by('-published_date').first()
        except Post.DoesNotExist:
            previous_post = None

        try:
            next_post = Post.objects.filter(
                published_date__gt=post.published_date,
                status='published'
            ).order_by('published_date').first()
        except Post.DoesNotExist:
            next_post = None

        # Get series information if applicable
        series_post = SeriesPost.objects.filter(post=post).first()
        if series_post:
            series = series_post.series
            series_posts = SeriesPost.objects.filter(series=series).order_by('order')

            # Get next and previous posts in series
            next_in_series = series_posts.filter(order__gt=series_post.order).first()
            prev_in_series = series_posts.filter(order__lt=series_post.order).last()

            context.update({
                'in_series': True,
                'series': series,
                'series_post': series_post,
                'next_in_series': next_in_series.post if next_in_series else None,
                'prev_in_series': prev_in_series.post if prev_in_series else None,
                'series_posts': [sp.post for sp in series_posts],
            })

        context.update({
            'related_posts': related_posts,
            'previous_post': previous_post,
            'next_post': next_post,
        })

        # Extract headings for Table of Contents
        headings = self.extract_headings(post.content)
        context['headings'] = headings

        # Additional enhanced context
        context.update({
            'current_post': post,
            'show_breadcrumbs': True,
            'show_terminal_code': bool(post.featured_code),
            'code_complexity': self.get_code_complexity(post),
            'estimated_difficulty': self.get_difficulty_level(post),
            'social_share_data': self.get_social_share_data(post),
        })

        return context

    def extract_headings(self, markdown_content):
        """Extract headings from markdown content for table of contents."""
        headings = []
        # Regular expression to find headings in markdown
        heading_pattern = r'^(#{1,3})\s+(.+)$'

        for line in markdown_content.split('\n'):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                # Create ID from heading text for anchor links
                # Using same splugify function as markdownify filter
                heading_id = slugify(text)
                headings.append({
                    'level': level,
                    'text': text,
                    'id': heading_id
                })
        return headings

    def get_code_complexity(self, post):
        """Analyze code complexity for display (Can enhance later)."""
        if not post.featured_code:
            return None

        code = post.featured_code
        lines = len(code.split('\n'))

        if lines < 10:
            return 'Simple'
        elif lines < 50:
            return 'Moderate'
        else:
            return 'Complex'

    def get_difficulty_level(self, post):
        """Determine content difficulty (can enhance later, maybe even add a vote..?)"""
        if post.reading_time < 5:
            return 'Beginner'
        elif post.reading_time < 15:
            return 'Intermediate'
        else:
            return 'Advanced'

    def get_social_share_data(self, post):
        """Prepare data for social sharing."""
        return {
            'title': post.title,
            'description': post.excerpt or f"Technical insights on {post.title}",
            'image': post.thumbnail.url if post.thumbnail else None,
            'url': self.request.build_absolute_uri(post.get_absolute_url()),
            'tags': [tag.name for tag in post.tags.all()[:5]]
        }


class CategoriesOverviewView(ListView):
    """
    View for categories overview page - shows all categories w stats.
    URL: /datalogs/categories/
    """
    model = Category
    template_name = "blog/category.html"  # Same template as CategoryView, different context
    context_object_name = "categories"
    
    # TODO: Add tags, maybe recent posts to category cards
    def get_queryset(self):
        # Get categories post counts if gt 0
        return Category.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status="published"))
        ).filter(post_count__gt=0).order_by('-post_count', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate overview stats
        categories = context['categories']
        total_posts = Post.objects.filter(status="published").count()
        total_categories = categories.count()

        # Get most popular category
        most_popular = categories.first() if categories else None

        # Get newest category (by first post)
        newest_category = None
        if categories:
            for cat in categories:
                if cat.posts.filter(status="published").exists():
                    newest_category = cat
                    break

        # Calculate avg posts per category
        avg_posts_per_category = round(total_posts / total_categories, 1) if total_categories > 0 else 0

        # Add recent posts to each category
        for category in categories:
            category.recent_posts = category.posts.filter(
                status="published"
            ).order_by('-published_date')[:3]

            # Calculate avg reading time for category
            category.avg_reading_time = category.posts.filter(
                status="published"
            ).aggregate(avg_time=Avg("reading_time"))["avg_time"] or 0

        # Categories w recent activity (posts in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        categories_with_recent_posts = Category.objects.filter(
            posts__published_date__gte=thirty_days_ago,
            posts__status="published"
        ).distinct().count()

        # Calculate total reading time across all categoriess
        total_reading_time = Post.objects.filter(
            status="published"
        ).aggregate(total=Sum("reading_time"))["total"] or 0

        context.update({
            # Clear category to indicate overview mode
            "category": None,

            # Overview page metadata
            "page_title": "Categories Overview",
            "page_subtitle": "Explore technical insights by expertise area",
            "page_icon": "fas fa-th-large",

            # Overview Stats
            "total_categories": total_categories,
            "total_posts": total_posts,
            "avg_posts_per_category": avg_posts_per_category,
            "most_popular_category": most_popular,
            "newest_category": newest_category,
            "categories_with_recent_posts": categories_with_recent_posts,
            "total_reading_time": total_reading_time,

            # Template control flags
            "show_breadcrumbs": True,
            # "show_stats": True,
        })

        return context


class CategoryView(ListView):
    """
    View for posts filtered by category.
    URL: /datalogs/category/<slug>/
    """
    model = Post
    template_name = "blog/category.html"  # Same temp as overview, diff context
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        # Get specific category
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category,
            status="published").order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Category-specific stats
        category_posts = self.get_queryset()
        category_post_count = category_posts.count()
        category_avg_reading_time = category_posts.aggregate(
            avg_time=Avg("reading_time")
        )["avg_time"] or 0

        # Related Categories (excluding current, only those w posts)
        related_categories = Category.objects.exclude(
            id=self.category.id
        ).annotate(
            post_count=Count("posts", filter=Q(posts__status="published"))
        ).filter(post_count__gt=0).order_by("-post_count")[:4]

        context.update({
            # Category-specific data
            "category": self.category,
            "category_slug": self.kwargs['slug'],

            # Page metadata
            "page_title": f"{self.category.name} DataLogs",
            "page_subtitle": f"Technical logs RE: {self.category.name}",
            "page_icon": self.category.icon or "fas fa-folder",

            # Category stats
            "category_post_count": category_post_count,
            "category_avg_reading_time": category_avg_reading_time,
            "related_categories": related_categories,

            # Template control flags
            "show_breadcrumbs": True,
            "show_filters": True,
            "show_stats": False,
        })

        return context


class TagListView(ListView):
    """
    Tags overview page - shows all tags w stats.
    URL: /datalogs/tags/
    """
    model = Tag
    template_name = 'blog/tag.html'  # Same temp as TagView, diff context
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status="published"))
        ).filter(post_count__gt=0).order_by('-post_count', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tags = context['tags']

        # Tag stats
        total_tagged_posts = Post.objects.filter(
            tags__isnull=False, status="published"
        ).distinct().count()
        popular_tags_count = tags.filter(post_count__gte=3).count()

        # Popular tags for cloud (top 20)
        popular_tags = tags[:20]

        # Group tags by category (if tags have category relationship)
        tags_by_category = defaultdict(list)
        for tag in tags:
            # Get the most common category for this tag
            common_category = Category.objects.filter(
                posts__tags=tag,
                posts__status="published"
            ).annotate(
                tag_usage=Count('posts')
            ).order_by('-tag_usage').first()

            # Add metadata to tag
            tag.recent_posts = Post.objects.filter(
                tags=tag, status="published"
            ).order_by('-published_date')[:2]

            tag.latest_post = tag.recent_posts.first() if tag.recent_posts else None
            tag.avg_reading_time = Post.objects.filter(
                tags=tag, status="published"
            ).aggregate(avg_time=Avg("reading_time"))["avg_time"] or 0

            if common_category:
                tags_by_category[common_category].append(tag)
            else:
                tags_by_category[None].append(tag)

        query = self.request.GET.get('q', '').strip()

        context.update({
            'tag': None,  # signals overview in template
            'popular_tags': popular_tags,
            'tags_by_category': dict(tags_by_category),
            'total_tagged_posts': total_tagged_posts,
            'popular_tags_count': popular_tags_count,
            'query': query,
            'page_title': 'Tags Overview',
            'page_subtitle': 'Explore DataLog tags',
            'show_breadcrumbs': True,
        })

        return context


class TagView(ListView):
    """
    Individual tag view - shows posts with specific tag
    URL: /datalogs/tag/<slug>/
    """
    model = Post
    template_name = "blog/tag.html"  # Same temp as TagListView, diff context
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        queryset = Post.objects.filter(
            tags=self.tag,
            status="published"
        ).select_related("category", "author").prefetch_related("tags").order_by('-published_date')

        # Apply search within tag
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']

        # Tag stats
        tag_post_count = self.get_queryset().count()
        tag_avg_reading_time = self.get_queryset().aggregate(
            avg_time=Avg("reading_time")
        )["avg_time"] or 0

        # Get related tags that appear together with this tag
        related_tags = Tag.objects.filter(
            posts__tags=self.tag,
            posts__status="published"
        ).exclude(id=self.tag.id).annotate(
            posts_count=Count('posts')
        ).order_by('-posts_count')[:6]

        # Categories that use this tag
        tag_categories = Category.objects.filter(
            posts__tags=self.tag,
            posts__status="published"
        ).annotate(
            post_count=Count("posts")
        ).order_by('-post_count')[:5]

        # Tag difficulty based on content
        tag_difficulty = 'beginner'  # Default
        if tag_avg_reading_time > 15:
            tag_difficulty = 'advanced'
        elif tag_avg_reading_time > 8:
            tag_difficulty = 'intermediate'

        query = self.request.GET.get('q', '').strip()

        context.update({
            'tag': self.tag,
            'tag_post_count': tag_post_count,
            'tag_avg_reading_time': tag_avg_reading_time,
            'tag_difficulty': tag_difficulty,
            'related_tags': related_tags,
            'tag_categories': tag_categories,
            'query': query,
            'page_title': f"{self.tag.name} Tag",
            'page_subtitle': f"Posts tagged w {self.tag.name}",
            'show_breadcrumbs': True,
            'show_filters': True,
        })

        return context


# Updated with archive_timeline enhancements
class ArchiveIndexView(ListView):
    """
    Main archive view - shows timeline of all posts grouped by date.
    URL: /blog/archive/
    """
    template_name = "blog/archive.html"
    context_object_name = 'all_posts'
    # Show all posts for timeline
    paginate_by = None

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related('category', 'author').prefetch_related('tags').order_by('-published_date')

        # Apply filters from GET params
        year = self.request.GET.get('year')
        category_slug = self.request.GET.get('category')

        if year:
            try:
                queryset = queryset.filter(published_date__year=int(year))
            except ValueError:
                pass
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_posts = self.get_queryset()

        # Group posts by year and month (Python grouping)
        posts_by_year = {}

        for post in all_posts:
            year = post.published_date.year
            month_key = post.published_date.strftime('%Y-%m')

            # Initialize year if not exists
            if year not in posts_by_year:
                posts_by_year[year] = {
                    'year': year,
                    'months': {},
                    'posts': []
                }

            # Initialize month if not exists
            if month_key not in posts_by_year[year]['months']:
                posts_by_year[year]['months'][month_key] = {
                    'month': post.published_date.replace(day=1),
                    'posts': []
                }

            # Add post month and year
            posts_by_year[year]['months'][month_key]['posts'].append(post)
            posts_by_year[year]['posts'].append(post)

        # Convert to list format for template
        formatted_years = []
        for year in sorted(posts_by_year.keys(), reverse=True):
            year_data = posts_by_year[year]

            # Convert monthly dicts to sorted list
            months_list = []
            for month_key in sorted(year_data['months'].keys(), reverse=True):
                months_list.append(year_data['months'][month_key])

            formatted_years.append({
                'year': year,
                'months': months_list,
                'posts': year_data['posts']
            })

        # Archive years for navigation using modern Django
        archive_years = Post.objects.filter(
            status="published"
        ).annotate(
            year=Extract('published_date', 'year')
        ).values('year').annotate(
            count=Count('id')
        ).order_by('-year')

        # Archive Stats
        total_posts = all_posts.count()
        current_year = datetime.now().year
        posts_this_year = all_posts.filter(published_date__year=current_year).count()

        # Date ranges
        if all_posts.exists():
            first_post = all_posts.order_by('published_date').first()
            latest_post = all_posts.order_by('-published_date').first()
            total_reading_time = all_posts.aggregate(
                total=Sum('reading_time')
            )['total'] or 0
        else:
            first_post = None
            latest_post = None
            total_reading_time = 0

        # Categories for filtering
        categories = Category.objects.filter(
            posts__status="published"
        ).annotate(
            post_count=Count('posts')
        ).order_by('name')

        context.update({
            'posts_by_year': formatted_years,
            'archive_years': list(archive_years),
            'total_posts': total_posts,
            'current_year': current_year,
            'posts_this_year': posts_this_year,
            'total_reading_time': total_reading_time,
            'first_post_date': first_post.published_date if first_post else None,
            'latest_post_date': latest_post.published_date if latest_post else None,
            'years_active': len(set(post.published_date.year for post in all_posts)),
            'categories': categories,
            'recent_posts': all_posts[:5],
            'query': self.request.GET.get('q', '').strip(),
            'page_title': 'Archive',
            'page_subtitle': 'Chronological timeline of all entries',
            'show_breadcrumbs': True,
        })

        return context


# # ======================== ENHANCED SEARCH VIEW ===========================


# @require_http_methods(["GET"])
# @cache_page(60 * 5)  # Cache for 5 minutes
# def search_ajax_endpoint(request):
#     """
#     AJAX endpoint for unified search suggestions.
#     Returns JSON w suggestions for real-time search.
#     """
#     query = request.GET.get('q', '').strip()
#     max_suggestions = int(request.GET.get('max', 6))

#     try:
#         if len(query) < 2:
#             # Return popular terms when query is too short
#             suggestions = [
#                 {
#                     "text": "Machine Learning",
#                     "type": "topic",
#                     "icon": "fas fa-brain",
#                     "url": "/datalogs/search/?q=machine+learning",
#                     "description": "AI and ML concepts",
#                 },
#                 {
#                     "text": "Python Development",
#                     "type": "topic",
#                     "icon": "fab fa-python",
#                     "url": "/datalogs/search/?q=python",
#                     "description": "Programming and development",
#                 },
#                 {
#                     "text": "API Design",
#                     "type": "topic",
#                     "icon": "fas fa-plug",
#                     "url": "/datalogs/search/?q=api",
#                     "description": "API design and development",
#                 },
#                 {
#                     "text": "Database",
#                     "type": "topic",
#                     "icon": "fas fa-database",
#                     "url": "/datalogs/search/?q=database",
#                     "description": "Database design and optimization",
#                 },
#                 {
#                     "text": "Neural Networks",
#                     "type": "topic",
#                     "icon": "fas fa-project-diagram",
#                     "url": "/datalogs/search/?q=neural+networks",
#                     "description": "Deep learning and neural networks",
#                 },
#             ]
#         else:
#             suggestions = []
#             query_lower = query.lower()

#             # Search in posts
#             matching_posts = (
#                 Post.objects.filter(
#                     Q(title__icontains=query) | Q(content__icontains=query),
#                     status="published",
#                 )
#                 .select_related("category")
#                 .order_by("-published_date")[:3]
#             )

#             for post in matching_posts:
#                 suggestions.append(
#                     {
#                         "text": post.title,
#                         "type": "post",
#                         "icon": "fas fa-file-alt",
#                         "url": post.get_absolute_url(),
#                         "description": f"Published {post.published_date.strftime('%b %d, %Y')}"
#                         if post.published_date
#                         else "",
#                     }
#                 )

#             # Search in categories
#             matching_categories = (
#                 Category.objects.filter(name__icontains=query)
#                 .annotate(
#                     post_count=Count("posts", filter=Q(posts__status="published"))
#                 )
#                 .filter(post_count__gt=0)[:2]
#             )

#             for category in matching_categories:
#                 suggestions.append(
#                     {
#                         "text": f"{category.name} Category",
#                         "type": "category",
#                         "icon": getattr(category, "icon", "fas fa-folder"),
#                         "url": category.get_absolute_url() if hasattr(category, 'get_absolute_url') else f"/datalogs/category/{category.slug}/",
#                         "description": f"{category.post_count} post{'s' if category.post_count != 1 else ''}",
#                     }
#                 )

#             # Search in tags
#             matching_tags = (
#                 Tag.objects.filter(name__icontains=query)
#                 .annotate(
#                     post_count=Count("posts", filter=Q(posts__status="published"))
#                 )
#                 .filter(post_count__gt=0)[:2]
#             )

#             for tag in matching_tags:
#                 suggestions.append(
#                     {
#                         "text": f"#{tag.name}",
#                         "type": "tag",
#                         "icon": "fas fa-tag",
#                         "url": tag.get_absolute_url() if hasattr(tag, 'get_absolute_url') else f"/datalogs/tag/{tag.slug}/",
#                         "description": f"{tag.post_count} post{'s' if tag.post_count != 1 else ''}",
#                     }
#                 )

#             # Add contextual topic suggestions
#             if "python" in query_lower and not any(
#                 s["text"] == "Python Development" for s in suggestions
#             ):
#                 suggestions.append(
#                     {
#                         "text": "Python Development",
#                         "type": "topic",
#                         "icon": "fab fa-python",
#                         "url": f"/datalogs/search/?q=python",
#                         "description": "Programming and development",
#                     }
#                 )

#             if any(
#                 term in query_lower for term in ["ml", "machine", "learning", "ai"]
#             ) and not any("Machine Learning" in s["text"] for s in suggestions):
#                 suggestions.append(
#                     {
#                         "text": "Machine Learning",
#                         "type": "topic",
#                         "icon": "fas fa-brain",
#                         "url": f"/datalogs/search/?q=machine+learning",
#                         "description": "AI and ML concepts",
#                     }
#                 )

#             if any(
#                 term in query_lower for term in ["api", "rest", "endpoint"]
#             ) and not any("API" in s["text"] for s in suggestions):
#                 suggestions.append(
#                     {
#                         "text": "API Development",
#                         "type": "topic",
#                         "icon": "fas fa-plug",
#                         "url": f"/datalogs/search/?q=api",
#                         "description": "API design and development",
#                     }
#                 )

#         # Limit to max suggestions
#         suggestions = suggestions[:max_suggestions]

#         return JsonResponse(
#             {
#                 "suggestions": suggestions,
#                 "query": query,
#                 "count": len(suggestions),
#                 "status": "success",
#                 # "cached": False,
#             }
#         )

#     except Exception as e:
#         return JsonResponse(
#             {
#                 "suggestions": [],
#                 "query": query,
#                 "count": 0,
#                 "status": "error",
#                 "error": "Search temporarily unavailable",
#             },
#             status=500,
#         )


# @require_http_methods(["GET"])
# def search_autocomplete(request):
#     """
#     Faster autocomplete endpoint that just returns text suggestions.
#     For basic autocomplete functionality without full suggestion objects.
#     """
#     query = request.GET.get("q", "").strip()
#     limit = int(request.GET.get("limit", 5))

#     if len(query) < 2:
#         return JsonResponse({"suggestions": []})

#     try:
#         # Get post titles that match
#         post_titles = Post.objects.filter(
#             title__icontains=query, status="published"
#         ).values_list("title", flat=True)[:limit // 2]

#         # Get category names that match
#         category_names = Category.objects.filter(name__icontains=query).values_list(
#             "name", flat=True
#         )[:limit // 2]

#         # Combine and limit
#         suggestions = list(post_titles) + [f"{name} Category" for name in category_names]
#         suggestions = suggestions[:limit]

#         return JsonResponse(
#             {"suggestions": suggestions, "query": query, "count": len(suggestions)}
#         )

#     except Exception:
#         return JsonResponse({"suggestions": [], "error": "Autocomplete unavailable"})


# def get_search_context(request, query=None):
#     """
#     Get all search-related context data.
#     Use this in your main SearchView and PostListView to keep them clean.
#     """
#     if query is None:
#         query = request.GET.get('q', '').strip()

#     context = {'query': query}

#     if query:
#         # Get search results
#         results = Post.objects.filter(
#             Q(title__icontains=query) |
#             Q(content__icontains=query) |
#             Q(excerpt__icontains=query),
#             status='published'
#         ).select_related('category', 'author').prefetch_related('tags')

#         context.update({
#             'search_results': results,
#             'search_results_count': results.count(),
#             'has_results': results.exists(),
#         })

#     return context


# # Helper function for other views that might need search context
# def add_search_context(context, request):
#     """
#     Add search-related context to any view.
#     Usage: context.update(add_search_context(context, request))
#     """
#     query = request.GET.get('q', '').strip()

#     search_context = {
#         'query': query,
#         'has_search_query': bool(query),
#         'search_enabled': True,
#     }

#     if query:
#         # Add search results count for display
#         search_context['search_results_count'] = Post.objects.filter(
#             Q(title__icontains=query) | Q(content__icontains=query),
#             status='published'
#         ).count()

#     return search_context

# ================ SIMPLIFIED SEARCH VIEW REWORK ================


class SearchView(ListView):
    """
    Enhanced search view with landing page and results.
    URL: /datalogs/search/
    """
    model = Post
    template_name = "blog/search.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()

        if not query:
            return Post.objects.none()

        queryset = Post.objects.filter(
            status="published").select_related("category", "author").prefetch_related("tags")

        # Build search query with relevance
        search_filter = (
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query)
        )

        queryset = queryset.filter(search_filter)

        # Apply additional filters
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)

        # Sort by relevance (title matches first, then content)
        sort_by = self.request.GET.get('sort', 'relevance')
        if sort_by == 'date':
            queryset = queryset.order_by('-published_date')
        elif sort_by == 'reading':
            queryset = queryset.order_by('reading_time')
        else:
            # Simple relevance: title matches first
            queryset = self._apply_relevance_sorting(queryset, query)

        return queryset.distinct()

    def _apply_relevance_sorting(self, queryset, query):
        """
        Apply relevance-based sorting using modern Django ORM methods.
        No .extra() method - uses Case/When for conditional logic.
        """
        # Create relevance score using Case/When (modern alt to .extra())
        relevance_score = Case(
            # Title exact match gets highest score (100)
            When(title__iexact=query, then=Value(100)),
            # Title contains gets high score (80)
            When(title__icontains=query, then=Value(80)),
            # Excerpt contains gets medium score (60)
            When(excerpt__icontains=query, then=Value(60)),
            # Content contains gets lower score (40)
            When(content__icontains=query, then=Value(40)),
            # Category/tag match gets base score (20)
            When(
                Q(category__name__icontains=query) | Q(tags__name__icontains=query),
                then=Value(20)
            ),
            # Default score (10)
            default=Value(10),
            output_field=IntegerField()
        )

        # Apply relevance scoring and sort
        return queryset.annotate(
            relevance=relevance_score
        ).order_by('-relevance', '-published_date')

    def get_context_data(self, **kwargs):
        """Add search-specific context."""
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q", "").strip()
        posts = context['posts'] if query else []

        if not query:
            # Search landing page context
            context.update(self._get_landing_page_context())
        else:
            # Search results page context
            context.update(self._get_results_page_context(posts, query))

        context.update({
            'query': query,
            'page_title': f'Search Parameters: {query}' if query else 'Search',
            'page_subtitle': f'Results for {query}' if query else 'Search DataLog entries',
            'show_breadcrumbs': True,
        })

        return context

    def _get_landing_page_context(self):
        """Get context for search landing if no query"""
        # Search stats
        total_searchable_posts = Post.objects.filter(status="published").count()
        total_searchable_tags = Tag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).count()
        total_categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).count()
        code_entries_count = Post.objects.filter(
            status="published"
        ).exclude(featured_code__exact='').count()

        # Popular searches (can implment analytics for this later)
        # TODO: For now, using static data - replace w real analytics later
        popular_searches = [
            {'term': 'python', 'count': 15},
            {'term': 'django', 'count': 12},
            {'term': 'javascript', 'count': 10},
            {'term': 'react', 'count': 8},
            {'term': 'data science', 'count': 6},
        ]

        # Recent posts
        recent_posts = Post.objects.filter(
            status="published"
        ).order_by('-published_date')[:6]

        # Featured categories for quick access
        featured_categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count')[:6]

        return {
            'total_searchable_posts': total_searchable_posts,
            'total_searchable_tags': total_searchable_tags,
            'total_categories': total_categories,
            'coded_entries_count': code_entries_count,
            'popular_searches': popular_searches,
            'recent_posts': recent_posts,
            'featured_categories': featured_categories,
        }

    def _get_results_page_context(self, posts, query):
        """Get context for search results page."""
        # Count results (handle both QuerySet and list)
        if hasattr(posts, 'count'):
            results_count = posts.count()
        else:
            results_count = len(posts)

        # Calculate estimated reading time for results
        estimated_total_time = 0
        if posts and hasattr(posts, 'aggregate'):
            estimated_total_time = posts.aggregate(
                total_time=Sum("reading_time")
            )["total_time"] or 0
        elif posts:
            # Fallback for list of posts
            estimated_total_time = sum(
                getattr(post, 'reading_time', 0) for post in posts
            )

        # Search performance timing (optional)
        # TODO: Can add timing logic here later
        search_time = None

        # Related content for no results case
        related_posts = []
        if results_count == 0:
            # Get some recent posts as suggestions
            related_posts = Post.objects.filter(
                status="published"
            ).order_by('-published_date')[:3]

        return {
            'results_count': results_count,
            'estimated_total_time': estimated_total_time,
            'search_time': search_time,
            'related_posts': related_posts,
        }


# ===================== SIMPLIFIED AJAX VIEWS FOR ENHANCED FEATURES =====================

def search_suggestions(request):
    """
    AJAX endpoint for search suggestions.
    URL: /datalogs/search/suggestions/
    """
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get("limit", 6))

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    try:
        suggestions = []

        # Get post titles that match
        post_titles = Post.objects.filter(
            title__icontains=query, status="published"
        ).values_list("title", flat=True)[:limit // 2]

        for title in post_titles:
            suggestions.append({
                'type': 'post',
                'text': title,
                'url': title.get_absolute_url(),  # TODO: Build URL
            })

        # Get category names that match
        categories = Category.object.filter(
            name__icontains=query
        ).values('name', 'slug')[:limit // 3]

        for cat in categories:
            suggestions.append({
                'type': 'category',
                'text': cat['name'],
                'url': f'/datalogs/category/{cat["slug"]}/',
            })

        # Get tag names that match
        tags = Tag.objects.filter(
            name__icontains=query
        ).values('name', 'slug')[:limit // 3]

        for tag in tags:
            suggestions.append({
                'type': 'tag',
                'text': tag['name'],
                'url': f'/datalogs/tag/{tag["slug"]}/'
            })

        return JsonResponse({
            "suggestions": suggestions[:limit],
            "query": query
        })

    except Exception as e:
        return JsonResponse({"suggestions": [], "error": str(e)})


# ===================== ADMIN VIEWS FOR POST MANAGEMENT =====================


class PostCreateView(LoginRequiredMixin, CreateView):
    """View for creating new post."""

    model = Post
    form_class = PostForm
    template_name = "blog/admin/post_form.html"

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        # DEBUG: Print form data and POST Data
        # print("=" * 50)
        # print("FORM SUBMITTED")
        # print("POST Data:")
        pprint.pprint(dict(self.request.POST))
        # print("Cleaned Data:")
        pprint.pprint(form.cleaned_data)
        # print("=" * 50)

        # Set the author to current user
        form.instance.author = self.request.user

        # Set publication date if status is published and no date
        if form.instance.status == "published" and not form.instance.published_date:
            form.instance.published_date = timezone.now()

        # If no slug, generate from title
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)

        # Add success message
        messages.success(self.request, "Post created successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Post"
        context["submit_text"] = "Create Post"
        return context

    # def extract_headings(self, markdown_content):
    #     """Extract headings from markdown content for table of contents preview."""
    #     headings = []
    #     # Regular expression to find headings in markdown
    #     heading_pattern = r'^(#{1,3})\s+(.+)$'

    #     for line in markdown_content.split('\n'):
    #         match = re.match(heading_pattern, line.strip())
    #         if match:
    #             level = len(match.group(1))
    #             text = match.group(2).strip()
    #             heading_id = slugify(text)
    #             headings.append({
    #                 'level': level,
    #                 'text': text,
    #                 'id': heading_id
    #             })

    #     return headings


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """View for editing an existing blog post."""

    model = Post
    form_class = PostForm
    template_name = "blog/admin/post_form.html"

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.object.slug})

    def form_valid(self, form):
        # DEBUG: Print the raw reuqest POST data and form cleaned_data
        # print("=" * 50)
        # print("FORM SUBMITTED")
        # print("POST Data:")
        # pprint.pprint(dict(self.request.POST))
        # print("Cleaned Data:")
        # pprint.pprint(form.cleaned_data)
        # print("Content Field BEFORE Save:")
        # print(form.instance.content)
        # print("=" * 50)

        # Set publication date if status is published and doesn't have one
        if form.instance.status == "published" and not form.instance.published_date:
            form.instance.published_date = timezone.now()

        # Save form and redirect & Add success message
        response = super().form_valid(form)

        # DEBUG AFTER SAVE
        # print("Content Field AFTER Save:")
        # print(self.object.content)
        # print("=" * 50)

        messages.success(self.request, "Post updated successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Post"
        context["submit_text"] = "Update Post"

        # Get series info
        post = self.get_object()
        series_post = SeriesPost.objects.filter(post=post).first()
        if series_post:
            context["initial_series"] = series_post.series
            context["initial_series_order"] = series_post.order

        return context

    # def extract_headings(self, markdown_content):
    #     """Extract headings from markdown content for table of contents preview."""
    #     headings = []
    #     # Regex to find headings
    #     heading_pattern = r'^(#{1,3})\s+(.+)$'

    #     for line in markdown_content.split('\n'):
    #         match = re.match(heading_pattern, line.strip())
    #         if match:
    #             level = len(match.group(1))
    #             text = match.group(2).strip()
    #             heading_id = slugify(text)
    #             headings.append({
    #                 'level': level,
    #                 'text': text,
    #                 'id': heading_id
    #             })
    #     return headings

    # def dispatch(self, request, *args, **kwargs):
    #     # Check if user is the author and has permission
    #     self.object = self.get_object()
    #     if self.object.author != request.user and not request.user.is_staff:
    #         messages.error(request, "You don't have permission to edit this post.")
    #         return redirect("blog:post_detail", slug=self.object.slug)
    #     return super().dispatch(request, *args, **kwargs)

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)

    #     # Prepare form initial data from content (for sections)
    #     if self.object and self.object.content:
    #         # Extract sections from markdown content to populate the form
    #         content_lines = self.object.content.split("\n\n")
    #         intro_lines = []
    #         current_section = 0

    #         for i, line in enumerate(content_lines):
    #             # Skip empty lines
    #             if not line.strip():
    #                 continue

    #             # Check if line is a heading
    #             if line.startswith("## "):
    #                 current_section += 1
    #                 if current_section <= 5:
    #                     form.initial[f"section_{current_section}_title"] = line[
    #                         3:
    #                     ].strip()

    #                     # Get the content for this section (all lines until next heading)
    #                     section_content = []
    #                     j = i + 1
    #                     while j < len(content_lines) and not content_lines[
    #                         j
    #                     ].startswith("## "):
    #                         if content_lines[j].strip():  # Skip empty lines
    #                             section_content.append(content_lines[j])
    #                         j += 1

    #                     form.initial[f"section_{current_section}_content"] = (
    #                         "\n\n".join(section_content)
    #                     )

    #             # If we haven't encountered heading yet, it's introduction
    #             elif current_section == 0 and not line.startswith("```"):
    #                 intro_lines.append(line)

    #         # Set intro field
    #         if intro_lines:
    #             form.initial["introduction"] = "\n\n".join(intro_lines)

    #     return form

class PostDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting logs post."""

    model = Post
    template_name = 'blog/admin/post_confirm_delete.html'
    success_url = reverse_lazy('blog:dashboard')

    def test_func(self):
        """Only allows author or admin to delete post."""
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Post'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new category."""

    model = Category
    form_class = CategoryForm
    template_name = 'blog/admin/category_form.html'
    success_url = reverse_lazy('blog:category_list')

    def form_valid(self, form):
        # Generate slug from name if not provided
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.name)

        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Category'
        context['submit_text'] = 'Create Category'
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing category."""

    model = Category
    form_class = CategoryForm
    template_name = 'blog/admin/category_form.html'
    success_url = reverse_lazy('blog:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Category'
        context['submit_text'] = 'Update Category'
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """View for listing all categories with post counts."""

    model = Category
    template_name = 'blog/admin/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count('posts')).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Manage Categories'
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a category."""

    model = Category
    template_name = 'blog/admin/category_confirm_delete.html'
    success_url = reverse_lazy('blog:category_list')

    def test_func(self):
        """Only allows superuser to delete categories."""
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Category'

        # Get posts that would be affected
        affected_posts = Post.objects.filter(category=self.object)
        context['affected_posts'] = affected_posts
        context['affected_count'] = affected_posts.count()

        return context

    def delete(self, request, *args, **kwargs):
        # Check if posts should be reassigned or deleted
        if 'reassign' in request.POST:
            new_category_id = request.POST.get('new_category')
            if new_category_id:
                try:
                    new_category = Category.objects.get(id=new_category_id)
                    Post.objects.filter(category=self.get_object()).update(category=new_category)
                    messages.success(request, f'Posts reassigned to {new_category.name}')
                except Category.DoesNotExist:
                    messages.error(request, 'Selected category does not exist')
                    return redirect(request.path)

        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, ListView):
    """Dashboard view for logs management."""

    model = Post
    template_name = 'blog/admin/dashboard.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'DEVLOGs Dashboard'
        context['post_count'] = Post.objects.count()
        context['published_count'] = Post.objects.filter(status='published').count()
        context['draft_count'] = Post.objects.filter(status='draft').count()
        context['category_count'] = Category.objects.count()
        context['tag_count'] = Tag.objects.count()
        return context


# class ImageUploadView(LoginRequiredMixin, View):
#     """Class-based view for handling image uploads for posts."""

#     @method_decorator(csrf_protect)
#     def post(self, request, *args, **kwargs):
#         if request.FILES.get("image"):
#             image = request.FILES["images"]

#             # Generate a unique filename
#             ext = os.path.splittext(image.name)[1]
#             filename = f"{uuid4().hex}{ext}"

#             # Create the upload path
#             upload_path = os.path.join("blog", "uploads", filename)

#             # Save the file
#             from django.core.files.storage import default_storage

#             file_path = default_storage.save(upload_path, image)

#             # Get the url
#             file_url = default_storage.url(file_path)

#             return JsonResponse({"success": True, "url": file_url, "name": image.name})

#         return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


# class TagSuggestionsView(View):
#     """Class-based view for getting tag suggestions."""

#     def get(self, request, *args, **kwargs):
#         query = request.GET.get("q", "").strip()
#         if query:
#             # Find matching tags
#             tags = Tag.objects.filter(name__icontains=query)[:10]
#             return JsonResponse(
#                 {"tags": [{"id": tag.id, "name": tag.name} for tag in tags]}
#             )
#         return JsonResponse({"tags": []})

# ===================== SUBSCRIPTION VIEWS =====================

@require_POST
def subscribe_email(request):
    """
    AJAX endpoint to subscribe an email address to blog updates.
    
    How it works:
    1. User submits email via AJAX form
    2. We validate the email
    3. Create or update Subscriber record
    4. Send verification email (optional but recommended)
    5. Return JSON response
    
    No authentication needed - just email validation.
    """
    try:
        # Get email from POST data
        email = request.POST.get('email', '').strip().lower()

        # Validate email format
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Email address is required'
            }, status=400)
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address'
            }, status=400)
        
        # Check if already subscribed
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                'verification_token': get_random_string(50),
                'is_active': True,
            }
        )

        if not created:
            # Already subscribed
            if subscriber.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'This email is already subscribed!'
                }, status=400)
            else:
                # Reactivate subscription
                subscriber.is_active = True
                subscriber.verification_token = get_random_string(50)
                subscriber.save()
        
        # Send verification email
        if not subscriber.is_verified:
            send_verification_email(request, subscriber)
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully subscribed! Check your email to verify.',
            'email': email,
            'requires_verification': not subscriber.is_verified
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


def send_verification_email(request, subscriber):
    """
    Send email verification link to new subscriber.
    
    Why we do this:
    - Prevents spam subscriptions
    - Confirms user owns the email
    - Required by email regulations (CAN-SPAM, GDPR)
    """

    verification_url = request.build_absolute_uri(
        reverse('datalogs:verify_subscription', args=[subscriber.verification_token])
    )

    subject = 'Verify your AURA DataLogs subscription'
    message = f"""
    Hi there!
    
    Thanks for subscribing to AURA DataLogs!
    
    Please click the link below to verify your email address:
    {verification_url}
    
    If you didn't subscribe, you can safely ignore this email.
    
    Best regards,
    The AURA Team
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        # Don't crash if email fails
        fail_silently=True,
    )


def verify_subscription(request, token):
    """
    Verify a subscriber's email address via token link.
    
    User clicks link in email → This view → Mark as verified → Redirect
    """
    subscriber = get_object_or_404(Subscriber, verification_token=token)

    if subscriber.is_verified:
        messages.info(request, 'Your email was already verified!')
    else:
        subscriber.verify_email()
        messages.success(request, 'Email verified! You\'re all set to receive updates.')
    
    return redirect('datalogs:post_list')


def unsubscribe(request, token):
    """
    Unsubscribe a user via token link.
    
    This is required by law (CAN-SPAM) - must provide easy unsubscribe.
    """
    subscriber = get_object_or_404(Subscriber, verification_token=token)

    if request.method == 'POST':
        subscriber.unsubscribe()
        messages.success(request, 'You have been unsubscribed. Sorry to see you go!')
        return redirect('datalogs:post_list')
    
    # Show confirmation page
    return render(request, 'blog/unsubscribe_confirm.html', {
        'subscriber': subscriber
    })


# ===================== BOOKMARK VIEWS =====================
def get_bookmarked_posts(request):
    """
    API endpoint to get full post data for bookmarked posts.
    
    How it works:
    1. JavaScript stores bookmark IDs in localStorage
    2. When user visits "My Bookmarks" page, JS sends those IDs here
    3. We fetch the actual Post objects
    4. Return as JSON for display
    
    This is just a helper - the actual bookmark storage is in the browser.
    """
    try:
        # Get post IDs from query params (sent by JS)
        post_ids = request.GET.get('ids', '')

        if not post_ids:
            return JsonResponse({
                'success': True,
                'posts': []
            })
        
        # Convert comma-separated string to list of ints
        id_list = [int(id.strip()) for id in post_ids.split(',') if id.strip().isdigit()]

        # Fetch posts
        posts = Post.objects.filter(
            id__in=id_list,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')

        # Serialize to JSON
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'published_date': post.published_date.isoformat() if post.published_date else None,
                'reading_time': post.reading_time,
                'category': {
                    'name': post.category.name,
                    'slug': post.category.slug,
                } if post.category else None,
                'tags': [{'name': tag.name, 'slug': tag.slug} for tag in post.tags.all()],
                'url': post.get_absolute_url(),
            })
        
        return JsonResponse({
            'success': True,
            'posts': posts_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def bookmarks_page(request):
    """
    Render the "My Bookmarks page.
    
    The actual bookmarks are loaded in via JS from localStorage.
    This view just provides page template.
    """
    return render(request, 'datalogs/bookmarks.html', {
        'page_title': 'My Bookmarks',
    })



# ===================== HELPER FUNCTION FOR SHARE =====================
def get_share_data(request, slug):
    """
    API Enpoint to get post data for sharing.
    
    Returns post title, URL, and excerpt for social sharing.
    This helps when using Web Share API.
    """
    post = get_object_or_404(Post, slug=slug, status='published')

    post_url = request.build_absolute_uri(post.get_absolute_url())

    return JsonResponse({
        'success': True,
        'title': post.title,
        'text': post.excerpt or f'Check out this post: {post.title}',
        'url': post_url,
    })
