from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404, render
from django.db.models import Count
from .models import Post, Category, Tag


class PostListView(ListView):
    """View for the blog homepage showing latest posts."""
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6 # 6 posts per page (2 rows of 3)

    def get_queryset(self):
        return Post.objects.filter(status="published").order_by("-published_date")

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
        tag_posts = Post.objects.filter(tags=self.tags)
        related_tags = Tag.objects.filter(
            post__in=tag_posts
        ).exclude(id=self.tag.id).annotate(
            post_count=Count('post')
        ).order_by('-post_count')[:3]

        context['related_tags'] = related_tags
        return context


class ArchiveView(ListView):
    """View for archive page showing posts by year/month."""
    template_name = "blog/archive.html"
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        if month:
            return Post.objects.filter(
                published_date__year=year,
                published_date__month=month,
                status='published'
            ).order_by('-published_date')

        return Post.objects.filter(
            published_date__year=year,
            status='published'
        ).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        context['year'] = year
        context['month'] = month
        return context
    
    
