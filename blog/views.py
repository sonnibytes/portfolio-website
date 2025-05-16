from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from .models import Post, Category, Tag
from datetime import datetime
import calendar


class PostListView(ListView):
    """View for the blog homepage showing latest posts."""
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6  # 6 posts per page (2 rows of 3)

    def get_queryset(self):
        return Post.objects.filter(
            status="published").order_by("-published_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['featured_post'] = Post.objects.filter(
            status='published',
            featured=True
            ).first()
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

        context.update({
            'related_posts': related_posts,
            'previous_post': previous_post,
            'next_post': next_post,
        })

        return context


class CategoryView(ListView):
    """View for posts filtered by category."""
    model = Post
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category,
            status="published").order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
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


class ArchiveView(ListView):
    """View for archive page showing posts by year/month."""
    template_name = "blog/archive.html"
    context_object_name = 'posts'
    paginate_by = 6

    # Define the start date for timeline (April 2025)
    start_year = 2024
    start_month = 11

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # If no year provided, show all posts
        if not year:
            return Post.objects.filter(
                status='published').order_by('-published_date')

        # If month provided, filter by year and month
        if month:
            return Post.objects.filter(
                published_date__year=year,
                published_date__month=month,
                status='published'
            ).order_by('-published_date')

        # If only year provided, filter by year
        return Post.objects.filter(
            published_date__year=year,
            status='published'
        ).order_by('-published_date')

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

        # Get current date info
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Get year and month from kwargs
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # Convert to integers if present
        if year:
            year = int(year)
        if month:
            month = int(month)
            month_name = calendar.month_name[month]
        else:
            month_name = None

        # Generate all years from start date to current date
        years = list(range(self.start_year, current_year + 1))

        # Generate all months for selected year
        if year:
            # For start year, only include months from start_month onward
            if year == self.start_year:
                month_range = range(self.start_month, 13)
            # For the current year, only include months up to current_month
            elif year == current_year:
                month_range = range(1, current_month + 1)
            # For other years, include all months
            else:
                month_range = range(1, 13)

            months = [(m, calendar.month_name[m]) for m in month_range]
        else:
            months = []

        # Get post counts for each year/month if desired
        year_counts = {}
        for yr in years:
            year_counts[yr] = Post.objects.filter(
                status='published',
                published_date__year=yr
            ).count()

        month_counts = {}
        if year:
            for m, _ in months:
                month_counts[m] = Post.objects.filter(
                    status='published',
                    published_date__year=year,
                    published_date__month=m
                ).count()

        # Add all context data
        context.update({
            'years': years,
            'year': year,
            'months': months,
            'month': month,
            'month_name': month_name,
            'start_year': self.start_year,
            'start_month': self.start_month,
            'current_year': current_year,
            'current_month': current_month,
            'year_counts': year_counts,
            'month_counts': month_counts,
        })

        return context


class SearchView(ListView):
    """View for search results."""
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
                title__icontains=query
            ) | Post.objects.filter(
                content__icontains=query
            ) | Post.objects.filter(
                tags__name__icontains=query
            ).distinct().filter(
                status='published'
            ).order_by('-published_date')
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
