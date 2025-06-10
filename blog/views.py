from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
# from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.html import escape
from django.db.models import Count, Q, Avg, Sum
from markdownx.utils import markdownify

from datetime import datetime, timedelta, date
import calendar
import os
import re
from uuid import uuid4
import pprint

from .models import Post, Category, Tag, Series, SeriesPost, PostView
from .forms import PostForm, CategoryForm, TagForm, SeriesForm
from .templatetags.datalog_tags import datalog_search_suggestions


class PostListView(ListView):
    """Enhanced post list view with search integration."""
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 12  # changed from 6 - 6 posts per page (2 rows of 3)

    def get_queryset(self):
        """Get posts, potentially filtered by search or category."""
        queryset = Post.objects.filter(
            status="published").select_related('category', 'author').prefetch_related('tags')

        # Handle search from unified search interface
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        return queryset.order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Helper function for search context
        context.update(get_search_context(self.request))

        # Existing context
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['featured_post'] = Post.objects.filter(
            status='published',
            featured=True
        ).select_related('category').prefetch_related('tags', 'related_systems').first()

        # Add search context
        # context.update(add_search_context(context, self.request))

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
            "show_stats": True,
        })

        return context


class CategoryView(ListView):
    """View for posts filtered by category."""
    model = Post
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        # If no category slug, return empty queryset for overview
        if 'slug' not in self.kwargs:
            return Post.objects.none()

        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category,
            status="published").order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'slug' in kwargs:
            # Focused category view
            context.update(
                {
                    "category": self.category,
                    "category_slug": self.kwargs['slug'],
                    "page_title": f"{self.category.name} DataLogs",
                    "page_subtitle": f"Technical insights in {self.category.name}",
                    "page_icon": self.category.icon or "fas fa-folder",
                    "show_breadcrumbs": True,
                    "show_filters": True,
                    "show_stats": False,
                    # Category-specific stats
                    "category_post_count": self.get_queryset().count(),
                    "category_avg_reading_time": self.get_queryset().aggregate(
                        avg_time=Avg("reading_time")
                    )["avg_time"] or 0,
                    # Related categories
                    "related_categories": Category.objects.exclude(id=self.category.id)
                    .annotate(
                        post_count=Count(
                            "posts", filter=Q(posts__status="published")
                        )
                    )
                    .filter(post_count__gt=0)[:4],
                }
            )
        else:
            # Categories overview
            categories = Category.objects.annotate(
                post_count=Count("posts", filter=Q(posts__status='published'))
            ).filter(post_count__gt=0)

            context.update({
                "categories": categories,
                "total_categories": categories.count(),
                "total_posts": Post.objects.filter(status="published").count(),
                "show_breadscrumbs": True,
                "show_filters": True,
                "show_stats": False,
                # ...other overview stats
            })

        return context


class TagListView(ListView):
    model = Tag
    template_name = 'blog/tags.html'
    context_object_name = 'tags'


class TagView(ListView):
    """View for posts filtered by tag."""
    model = Post
    template_name = "blog/tag.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            tags=self.tag, status="published").order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag

        # Get related tags that appear together with this tag
        tag_posts = Post.objects.filter(tags=self.tag)
        related_tags = Tag.objects.filter(
            posts__in=tag_posts
        ).exclude(id=self.tag.id).annotate(
            posts_count=Count('posts')
        ).order_by('-posts_count')[:3]

        context['related_tags'] = related_tags
        return context


# Updated with archive_timeline enhancements
class ArchiveIndexView(ListView):
    """
    Main archive view - shows timeline of all posts grouped by month.
    URL: /blog/archive/
    """
    template_name = "blog/archive.html"
    context_object_name = 'posts'
    # Show all posts for timeline
    paginate_by = None

    # Define the start date for timeline (April 2025)
    # start_year = 2024
    # start_month = 11

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related('category', 'author').prefetch_related('tags').order_by('-published_date')

        # Apply filters from GET params
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        category = self.request.GET.get('category')


        if year:
            try:
                queryset = queryset.filter(published_date__year=int(year))
            except ValueError:
                pass

            return Post.objects.filter(
                status='published').order_by('-published_date')

        # If month provided, filter by year and month
        if month and year:
            try:
                queryset = queryset.filter(published_date__month=int(month))
            except ValueError:
                pass

        if category:
            queryset = queryset.filter(category__slug=category)

        return queryset

    def get(self, request, *args, **kwargs):
        # Current Date
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Get year and month from kwargs
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # Validate year and month
        if year and (int(year) < self.start_year or int(year) > current_year):
            return redirect('blog:archive')

        if month and year and (
            (int(year) == self.start_year and int(month) > self.start_month) or
            (int(year) == current_year and int(month) > current_month) or
            int(month) < 1 or int(month) > 12
        ):
            return redirect('blog:archive_year', year=year)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filter params
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        category_slug = self.request.GET.get('category')

        # Convert to integers if present
        current_year = int(year) if year else None
        current_month = int(month) if month else None

        # Get category object if filtering
        current_category = None
        if category_slug:
            try:
                current_category = Category.objectcs.get(slug=category_slug)
            except Category.DoesNotExist:
                pass

        # Determine archive style based on data volume and filters
        posts = context['posts']
        total_posts = posts.count()

        # Smart style detection
        if current_year and current_month:
            # Monthly View - use cards
            archive_style = 'cards'
        elif current_year:
            # Yearly View - use compact
            archive_style = 'compact'
        elif total_posts > 50:
            # Large dataset - yearly overview
            archive_style = 'yearly'
        else:
            # Default - full timeline
            archive_style = 'full'

        # Add archive-specific context data
        context.update({
            'current_year': current_year,
            'current_month': current_month,
            'current_category': current_category,
            'archive_style': archive_style,
            'total_posts_in_archive': total_posts,
            'page_title': self.get_page_title(),
            'page_description': self.get_page_description(),
            'show_timeline_stats': True,
            'show_timeline_navigation': True,
            'show_timeline_filters': True,
        })

        return context

    def get_page_title(self):
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        category = self.request.GET.get('category')

        if year and month:
            month_name = calendar.month_name[int(month)]
            return f"DataLogs Archive - {month_name} {year}"
        elif year:
            return f"DataLogs Archive - {year}"
        elif category:
            return f"DataLogs Archive - {category.replace('-', ' ').title()}"
        else:
            return "DataLogs Archive - All Entries"

    def get_page_description(self):
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        if year and month:
            month_name = calendar.month_name[int(month)]
            return f"Browse all DataLog entries published in {month_name} {year}."
        elif year:
            return f"Browse all DataLog entries published in {year}."
        else:
            return "Browse the complete archive of DataLog entries organized by publication date."


class ArchiveYearView(ListView):
    """
    Year-based archive view.
    URL: /blog/archive/<year>/
    """
    model = Post
    template_name = 'blog/archive_year.html'
    context_object_name = 'posts'

    def get_queryset(self):
        year = self.kwargs['year']
        return Post.objects.filter(
            status='published',
            published_date__year=year).select_related(
                'category', 'author').prefetch_related('tags').order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs['year']

        context.update({
            'current_year': year,
            'archive_style': 'compact',
            'page_title': f'DataLogs Archive - {year}',
            'page_description': f'All entries logged in {year}.',
            'show_timeline_stats': True,
            'show_timeline_navigation': True,
        })

        return context


class ArchiveMonthView(ListView):
    """
    Month-based archive view.
    URL: /blog/archive/<year>/<month>/
    """

    model = Post
    template_name = "blog/archive_month.html"
    context_object_name = "posts"

    def get_queryset(self):
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        return (
            Post.objects.filter(
                status="published",
                published_date__year=year,
                published_date__month=month,
            )
            .select_related("category", "author")
            .prefetch_related("tags")
            .order_by("-published_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        month_name = calendar.month_name[month]

        context.update(
            {
                "current_year": year,
                "current_month": month,
                "month_name": month_name,
                "archive_style": "cards",
                "page_title": f"DataLogs Archive - {month_name} {year}",
                "page_description": f"All DataLog entries published in {month_name} {year}.",
                "show_timeline_stats": True,
                "show_timeline_navigation": True,
            }
        )

        return context


# ======================== ENHANCED SEARCH VIEW ===========================


@require_http_methods(["GET"])
@cache_page(60 * 5)  # Cache for 5 minutes
def search_ajax_endpoint(request):
    """
    AJAX endpoint for unified search suggestions.
    Returns JSON w suggestions for real-time search.
    """
    query = request.GET.get('q', '').strip()
    max_suggestions = int(request.GET.get('max', 6))

    try:
        if len(query) < 2:
            # Return popular terms when query is too short
            suggestions = [
                {
                    "text": "Machine Learning",
                    "type": "topic",
                    "icon": "fas fa-brain",
                    "url": "/datalogs/search/?q=machine+learning",
                    "description": "AI and ML concepts",
                },
                {
                    "text": "Python Development",
                    "type": "topic",
                    "icon": "fab fa-python",
                    "url": "/datalogs/search/?q=python",
                    "description": "Programming and development",
                },
                {
                    "text": "API Design",
                    "type": "topic",
                    "icon": "fas fa-plug",
                    "url": "/datalogs/search/?q=api",
                    "description": "API design and development",
                },
                {
                    "text": "Database",
                    "type": "topic",
                    "icon": "fas fa-database",
                    "url": "/datalogs/search/?q=database",
                    "description": "Database design and optimization",
                },
                {
                    "text": "Neural Networks",
                    "type": "topic",
                    "icon": "fas fa-project-diagram",
                    "url": "/datalogs/search/?q=neural+networks",
                    "description": "Deep learning and neural networks",
                },
            ]
        else:
            suggestions = []
            query_lower = query.lower()

            # Search in posts
            matching_posts = (
                Post.objects.filter(
                    Q(title__icontains=query) | Q(content__icontains=query),
                    status="published",
                )
                .select_related("category")
                .order_by("-published_date")[:3]
            )

            for post in matching_posts:
                suggestions.append(
                    {
                        "text": post.title,
                        "type": "post",
                        "icon": "fas fa-file-alt",
                        "url": post.get_absolute_url(),
                        "description": f"Published {post.published_date.strftime('%b %d, %Y')}"
                        if post.published_date
                        else "",
                    }
                )

            # Search in categories
            matching_categories = (
                Category.objects.filter(name__icontains=query)
                .annotate(
                    post_count=Count("posts", filter=Q(posts__status="published"))
                )
                .filter(post_count__gt=0)[:2]
            )

            for category in matching_categories:
                suggestions.append(
                    {
                        "text": f"{category.name} Category",
                        "type": "category",
                        "icon": getattr(category, "icon", "fas fa-folder"),
                        "url": category.get_absolute_url() if hasattr(category, 'get_absolute_url') else f"/datalogs/category/{category.slug}/",
                        "description": f"{category.post_count} post{'s' if category.post_count != 1 else ''}",
                    }
                )

            # Search in tags
            matching_tags = (
                Tag.objects.filter(name__icontains=query)
                .annotate(
                    post_count=Count("posts", filter=Q(posts__status="published"))
                )
                .filter(post_count__gt=0)[:2]
            )

            for tag in matching_tags:
                suggestions.append(
                    {
                        "text": f"#{tag.name}",
                        "type": "tag",
                        "icon": "fas fa-tag",
                        "url": tag.get_absolute_url() if hasattr(tag, 'get_absolute_url') else f"/datalogs/tag/{tag.slug}/",
                        "description": f"{tag.post_count} post{'s' if tag.post_count != 1 else ''}",
                    }
                )

            # Add contextual topic suggestions
            if "python" in query_lower and not any(
                s["text"] == "Python Development" for s in suggestions
            ):
                suggestions.append(
                    {
                        "text": "Python Development",
                        "type": "topic",
                        "icon": "fab fa-python",
                        "url": f"/datalogs/search/?q=python",
                        "description": "Programming and development",
                    }
                )

            if any(
                term in query_lower for term in ["ml", "machine", "learning", "ai"]
            ) and not any("Machine Learning" in s["text"] for s in suggestions):
                suggestions.append(
                    {
                        "text": "Machine Learning",
                        "type": "topic",
                        "icon": "fas fa-brain",
                        "url": f"/datalogs/search/?q=machine+learning",
                        "description": "AI and ML concepts",
                    }
                )

            if any(
                term in query_lower for term in ["api", "rest", "endpoint"]
            ) and not any("API" in s["text"] for s in suggestions):
                suggestions.append(
                    {
                        "text": "API Development",
                        "type": "topic",
                        "icon": "fas fa-plug",
                        "url": f"/datalogs/search/?q=api",
                        "description": "API design and development",
                    }
                )

        # Limit to max suggestions
        suggestions = suggestions[:max_suggestions]

        return JsonResponse(
            {
                "suggestions": suggestions,
                "query": query,
                "count": len(suggestions),
                "status": "success",
                # "cached": False,
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "suggestions": [],
                "query": query,
                "count": 0,
                "status": "error",
                "error": "Search temporarily unavailable",
            },
            status=500,
        )


@require_http_methods(["GET"])
def search_autocomplete(request):
    """
    Faster autocomplete endpoint that just returns text suggestions.
    For basic autocomplete functionality without full suggestion objects.
    """
    query = request.GET.get("q", "").strip()
    limit = int(request.GET.get("limit", 5))

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    try:
        # Get post titles that match
        post_titles = Post.objects.filter(
            title__icontains=query, status="published"
        ).values_list("title", flat=True)[:limit // 2]

        # Get category names that match
        category_names = Category.objects.filter(name__icontains=query).values_list(
            "name", flat=True
        )[:limit // 2]

        # Combine and limit
        suggestions = list(post_titles) + [f"{name} Category" for name in category_names]
        suggestions = suggestions[:limit]

        return JsonResponse(
            {"suggestions": suggestions, "query": query, "count": len(suggestions)}
        )

    except Exception:
        return JsonResponse({"suggestions": [], "error": "Autocomplete unavailable"})


def get_search_context(request, query=None):
    """
    Get all search-related context data.
    Use this in your main SearchView and PostListView to keep them clean.
    """
    if query is None:
        query = request.GET.get('q', '').strip()

    context = {'query': query}

    if query:
        # Get search results
        results = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query),
            status='published'
        ).select_related('category', 'author').prefetch_related('tags')

        context.update({
            'search_results': results,
            'search_results_count': results.count(),
            'has_results': results.exists(),
        })

    return context


# Helper function for other views that might need search context
def add_search_context(context, request):
    """
    Add search-related context to any view.
    Usage: context.update(add_search_context(context, request))
    """
    query = request.GET.get('q', '').strip()

    search_context = {
        'query': query,
        'has_search_query': bool(query),
        'search_enabled': True,
    }

    if query:
        # Add search results count for display
        search_context['search_results_count'] = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        ).count()

    return search_context


class SearchView(ListView):
    """
    Enhanced search view that works with the unified search interface.
    """
    model = Post
    template_name = "blog/search.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        """Get search results with better relevance scoring."""
        query = self.request.GET.get('q', '').strip()

        if not query:
            return Post.objects.none()

        # Base queryset - published posts only
        queryset = (
            Post.objects.filter(status="published")
            .select_related("category", "author")
            .prefetch_related("tags")
        )

        # Build search query
        search_query = self.build_search_query(query)
        queryset = queryset.filter(search_query)

        # Apply additional filters
        queryset = self.apply_filters(queryset)

        # Apply sorting
        queryset = self.apply_sorting(queryset)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        """Add search-specific context."""
        context = super().get_context_data(**kwargs)
        # context.update(get_search_context(self.request))
        
        query = self.request.GET.get("q", "").strip()

        # context.update(
        #     {
        #         "query": query,
        #         "search_results_count": self.get_queryset().count() if query else 0,
        #         "has_results": self.get_queryset().exists() if query else False,
        #         "popular_terms": [
        #             {"term": "Machine Learning", "count": 15},
        #             {"term": "Python", "count": 23},
        #             {"term": "API Development", "count": 12},
        #             {"term": "Database", "count": 8},
        #             {"term": "Django", "count": 18},
        #         ],
        #         'search_suggestions_enabled': True,
        #     }
        # )

        # return context

        # Older, more complex logic
        context["query"] = query
        context["total_results"] = self.get_queryset().count() if query else 0

        # Active filters for display
        context["active_filters"] = self.get_active_filters()

        # Search metadata
        context["search_metadata"] = {
            "query": query,
            "total_results": context["total_results"],
            "filters_applied": self.get_active_filters(),
            "sort_by": self.request.GET.get("sort", "relevance"),
            "has_results": context["total_results"] > 0,
        }

        # Get suggestions for the current query
        if query:
            context["search_suggestions"] = datalog_search_suggestions(query)

        # Filter options for the template
        context["categories"] = Category.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status="pubished"))
        ).filter(post_count__gt=0)

        context["popular_tags"] = (
            Tag.objects.annotate(
                post_count=Count("posts", filter=Q(posts__status="published"))
            )
            .filter(post_count__gt=0)
            .order_by("-post_count")[:10]
        )
       
        return context

    def build_search_query(self, query):
        """Build complex search query for title, content, excerpt, and tags."""
        search_terms = query.split()

        # Start w empty Q object
        search_query = Q()

        for term in search_terms:
            term_query = (
                Q(title__icontains=term) |
                Q(content__icontains=term) |
                Q(excerpt__icontains=term) |
                Q(tags__name__icontains=term) |
                Q(category__name__icontains=term)
            )
            search_query &= term_query

        return search_query

    def apply_filters(self, queryset):
        """Apply additional search filters."""
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Tag filter
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # Reading time filter
        reading_time = self.request.GET.get('reading_time')
        if reading_time:
            if reading_time == '0-5':
                queryset = queryset.filter(reading_time__lte=5)
            elif reading_time == '5-15':
                queryset = queryset.filter(reading_time__gt=5, reading_time__lte=15)
            elif reading_time == '15+':
                queryset = queryset.filter(reading_time__gt=15)

        # Featured filter
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)

        # Date range filter
        date_range = self.request.GET.get('date_range')
        if date_range:
            now = timezone.now()

            if date_range == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(published_date__gte=start_date)
            elif date_range == 'week':
                start_date = now - timedelta(days=7)
                queryset = queryset.filter(published_date__gte=start_date)
            elif date_range == 'month':
                start_date = now - timedelta(days=30)
                queryset = queryset.filter(published_date__gte=start_date)
            elif date_range == 'quarter':
                start_date = now - timedelta(days=90)
                queryset = queryset.filter(published_date__gte=start_date)
            elif date_range == 'year':
                start_date = now - timedelta(days=365)
                queryset = queryset.filter(published_date__gte=start_date)

        return queryset

    def apply_sorting(self, queryset):
        """Apply sorting to search results."""
        sort_by = self.request.GET.get('sort', 'relevance')

        if sort_by == 'newest':
            return queryset.order_by('-published_date')
        elif sort_by == 'oldest':
            return queryset.order_by('published_date')
        elif sort_by == 'title':
            return queryset.order_by('title')
        elif sort_by == 'reading-time':
            return queryset.order_by('reading_time')
        elif sort_by == 'category':
            return queryset.order_by('category__name', '-published_date')
        else:
            # Default relevance sorting (newest first for now)
            # TODO: Implement proper relevance scoring
            return queryset.order_by('-published_date')

    def get_active_filters(self):
        """Get currently active filters for display."""
        filters = {}

        if self.request.GET.get('category'):
            filters['category'] = self.request.GET.get('category')
        if self.request.GET.get('tag'):
            filters['tag'] = self.request.GET.get('tag')
        if self.request.GET.get('reading_time'):
            filters['reading_time'] = self.request.GET.get('reading_time')
        if self.request.GET.get('featured') == 'true':
            filters['featured'] = True
        if self.request.GET.get('date_range'):
            filters['date_range'] = self.request.GET.get('date_range')
        if self.request.GET.get('sort', 'relevance') != 'relevance':
            filters['sort'] = self.request.GET.get('sort')

        return filters

# PREVIOUS SEARCH IMPLEMENTATION
# @require_http_methods(["GET"])
# def search_suggestions_ajax(request):
#     """
#     AJAX endpoint for real-time sesarch suggestions.
#     Returns JSON response with suggestions data.
#     """
#     query = request.GET.get('q', '').strip()
#     max_suggestions = int(request.GET.get('max', 8))

#     # minimum query len
#     if len(query) < 2:
#         return JsonResponse({
#             'suggestions': [],
#             'query': query,
#             'total': 0,
#             'success': True
#         })

#     try:
#         # Use existing template tag function for consistency
#         suggestions = datalog_search_suggestions(query)

#         # Limit suggestions
#         suggestions = suggestions[:max_suggestions]

#         # Add additional metadata for AJAX response
#         enhanced_suggestions = []
#         for suggestion in suggestions:
#             enhanced_suggestion = {
#                 'text': suggestion.get('text', ''),
#                 'type': suggestion.get('type', 'other'),
#                 'icon': suggestion.get('icon', 'fas fa-search'),
#                 'url': suggestion.get('url', '#'),
#                 'description': suggestion.get('description', ''),
#                 'count': suggestion.get('count', 0),
#                 'highlighted_text': highlight_query_in_text(
#                     suggestion.get('text', ''), query
#                 )
#             }
#             enhanced_suggestions.append(enhanced_suggestion)

#         # Add quick actions
#         quick_actions = get_search_quick_actions(query)

#         # Performance hints
#         hints = get_search_performance_hints(len(enhanced_suggestions), len(query))

#         response_data = {
#             'suggestions': enhanced_suggestions,
#             'quick_actions': quick_actions,
#             'hints': hints,
#             'query': query,
#             'total': len(enhanced_suggestions),
#             'success': True,
#             'metadata': {
#                 'query_length': len(query),
#                 'has_results': len(enhanced_suggestions) > 0,
#                 # TODO: add actual timing here
#                 'response_time': 'fast',
#             }
#         }

#         return JsonResponse(response_data)

#     except Exception as e:
#         return JsonResponse({
#             'suggestions': [],
#             'error': 'Search temporarily unavailable',
#             'query': query,
#             'total': 0,
#             'success': False
#         }, status=500)


# def highlight_query_in_text(text, query):
#     """Highlight query terms in text for AJAX response."""
#     if not query or not text:
#         return text

#     # Escape HTML to prevent XSS
#     text = escape(text)
#     query = escape(query)

#     # Simple highlighting - replace with <mark> tags
#     words = query.split()
#     for word in words:
#         pattern = re.compile(re.escape(word), re.IGNORECASE)
#         text = pattern.sub(f'<mark class="search-highlight">{word}</mark>', text)

#     return text


# def get_search_quick_actions(query):
#     """Generate quick actions for AJAX search."""
#     actions = []

#     if query:
#         actions.extend([
#             {
#                 'text': f'Search logs for "{query}"',
#                 'url': f"{reverse('blog:search')}?q={query}",
#                 'icon': 'fas fa-search',
#                 'type': 'action',
#             },
#             {
#                 'text': f'Search logs in specific category',
#                 'url': f"{reverse('blog:search')}?q={query}&show_filters=true",
#                 'icon': 'fas fa-folder-open',
#                 'type': 'action',
#             },
#         ])

#     # Always include browse action
#     actions.append({
#         'text': 'Browse all DataLogs',
#         'url': reverse('blog:post_list'),
#         'icon': 'fas fa-database',
#         'type': 'action',
#     })

#     return actions


# def get_search_performance_hints(suggestion_count, query_length):
#     """Generate performance hints for AJAX search."""
#     hints = []

#     if query_length < 3:
#         hints.append({
#             'type': 'tip',
#             'message': 'Type at least 3 characters for better results',
#             'icon': 'fas fa-into-circle',
#         })

#     if suggestion_count == 0:
#         hints.append({
#             'type': 'help',
#             'message': 'Try shorter keywords or browse categories',
#             'icon': 'fas fa-lightbulb',
#         })

#     elif suggestion_count > 15:
#         hints.append(
#             {
#                 "type": "tip",
#                 "message": "Too many results - narrow parameters",
#                 "icon": "fas fa-filter",
#             }
#         )
#     return hints


# @require_http_methods(["GET"])
# def search_autocomplete(request):
#     """
#     Simple autocomplete endpoint for search input.
#     Returns just the text suggestions for faster autocomplete.
#     """
#     query = request.GET.get("q", "").strip()
#     limit = int(request.GET.get("limit", 5))

#     if len(query) < 2:
#         return JsonResponse({"suggestions": []})

#     try:
#         # Get post titles that match
#         post_titles = Post.objects.filter(
#             title__icontains=query, status="published"
#         ).values_list("title", flat=True)[: limit // 2]

#         # Get category names that match
#         category_names = Category.objects.filter(name__icontains=query).values_list(
#             "name", flat=True
#         )[: limit // 2]

#         # Combine and limit
#         suggestions = list(post_titles) + list(category_names)
#         suggestions = suggestions[:limit]

#         return JsonResponse({"suggestions": suggestions, "query": query})

#     except Exception:
#         return JsonResponse({"suggestions": []})


# # Additional helper views for search functionality
# def search_export(request):
#     """Export search results as JSON (for advanced users)."""
#     if not request.user.is_staff:
#         return JsonResponse({"error": "Permission denied"}, status=403)

#     # Use the same logic as SearchView but return JSON
#     search_view = SearchView()
#     search_view.request = request
#     queryset = search_view.get_queryset()

#     results = []
#     for post in queryset[:100]:  # Limit export to 100 results
#         results.append(
#             {
#                 "id": post.id,
#                 "title": post.title,
#                 "slug": post.slug,
#                 "url": post.get_absolute_url(),
#                 "published_date": post.published_date.isoformat()
#                 if post.published_date
#                 else None,
#                 "category": post.category.name if post.category else None,
#                 "tags": [tag.name for tag in post.tags.all()],
#                 "reading_time": post.reading_time,
#                 "featured": post.featured,
#             }
#         )

#     return JsonResponse(
#         {
#             "results": results,
#             "total": len(results),
#             "query": request.GET.get("q", ""),
#             "exported_at": timezone.now().isoformat(),
#         }
#     )


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
        return Post.objects.all().order_by('-created')[:10]

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
