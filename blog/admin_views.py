"""
Blog Admin Views - DataLogs Management Interface
Extends the global admin system with blog-specific functionality
"""

from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg, Sum
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify

from core.admin_views import (
    BaseAdminListView,
    BaseAdminCreateView,
    BaseAdminUpdateView,
    BaseAdminDeleteView,
    SlugAdminCreateView,
    AuthorAdminCreateView,
    StatusAdminCreateView,
    BulkActionMixin,
)
from .models import Post, Category, Tag, Series, SystemLogEntry
from .forms import PostForm, CategoryForm, TagForm, SeriesForm


class BlogAdminDashboardView(BaseAdminListView):
    """Main DataLogs admin dashboard with enhanced metrics."""

    model = Post
    template_name = 'blog/admin/dashboard.html'
    context_object_name = 'recent_posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').order_by('-created_at')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard statistics
        context.update(
            {
                "title": "DataLogs Dashboard",
                "total_posts": Post.objects.count(),
                "published_posts": Post.objects.filter(status="published").count(),
                "draft_posts": Post.objects.filter(status="draft").count(),
                "featured_posts": Post.objects.filter(featured=True).count(),
                "total_categories": Category.objects.count(),
                "total_tags": Tag.objects.count(),
                "total_series": Series.objects.count(),
                "system_connections": SystemLogEntry.objects.count(),
                # Recent activity
                "recent_posts": self.get_queryset(),
                "popular_categories": Category.objects.annotate(
                    post_count=Count("posts")
                ).order_by("-post_count")[:5],
                "popular_tags": Tag.objects.annotate(
                    post_count=Count("posts")
                ).order_by("-post_count")[:5],
                # Content insights
                "avg_reading_time": Post.objects.aggregate(
                    avg_time=Avg("reading_time")
                )["avg_time"]
                or 0,
                "total_reading_time": Post.objects.aggregate(
                    total_time=Sum("reading_time")
                )["total_time"]
                or 0,
            }
        )

        return context


class PostListAdminView(BaseAdminListView, BulkActionMixin):
    """Enhanced post list view with filtering and bulk actions."""

    model = Post
    template_name = "blog/admin/post_list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        queryset = Post.objects.select_related("author", "category").prefetch_related(
            "tags"
        )

        # Apply filters
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        category_filter = self.request.GET.get("category")
        if category_filter:
            queryset = queryset.filter(category__slug=category_filter)

        featured_filter = self.request.GET.get("featured")
        if featured_filter:
            queryset = queryset.filter(featured=True)

        return queryset.order_by("-created_at")

    def filter_queryset(self, queryset, search_query):
        """Enhanced search across multiple fields."""
        return queryset.filter(
            Q(title__icontains=search_query)
            | Q(excerpt__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(tags__name__icontains=search_query)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Manage DataLog Entries",
                "create_url": reverse_lazy("blog:post_create_admin"),
                "edit_url_name": "blog:post_update_admin",
                "delete_url_name": "blog:post_delete_admin",
                "categories": Category.objects.all(),
                "current_filters": {
                    "status": self.request.GET.get("status"),
                    "category": self.request.GET.get("category"),
                    "featured": self.request.GET.get("featured"),
                },
            }
        )

        return context

    def handle_bulk_action(self, action, selected_ids):
        """Handle blog-specific bulk actions."""
        queryset = Post.objects.filter(id__in=selected_ids)

        if action == "publish":
            count = queryset.filter(status="draft").update(
                status="published", published_date=timezone.now()
            )
            messages.success(self.request, f"Successfully published {count} posts.")
        elif action == "draft":
            count = queryset.update(status="draft")
            messages.success(
                self.request, f"Successfully moved {count} posts to draft."
            )
        elif action == "feature":
            count = queryset.update(featured=True)
            messages.success(self.request, f"Successfully featured {count} posts.")
        elif action == "unfeature":
            count = queryset.update(featured=False)
            messages.success(self.request, f"Successfully unfeatured {count} posts.")
        else:
            return super().handle_bulk_action(action, selected_ids)

        return self.get(self.request)


class PostCreateAdminView(
    SlugAdminCreateView, AuthorAdminCreateView, StatusAdminCreateView
):
    """Create new DataLog entry with enhanced features."""

    model = Post
    form_class = PostForm
    template_name = "blog/admin/post_form.html"
    success_url = reverse_lazy("blog:post_list_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Create New DataLog Entry",
                "submit_text": "Create DataLog",
                "icon": "fas fa-plus-circle",
                "available_categories": Category.objects.all(),
                "available_tags": Tag.objects.all(),
                "available_series": Series.objects.all(),
            }
        )

        return context

    def form_valid(self, form):
        # Calculate reading time before saving
        if form.instance.content:
            word_count = len(form.instance.content.split())
            form.instance.reading_time = max(1, word_count // 200)  # ~200 WPM

        return super().form_valid(form)


class PostUpdateAdminView(BaseAdminUpdateView):
    """Update existing DataLog entry."""

    model = Post
    form_class = PostForm
    template_name = "blog/admin/post_form.html"
    success_url = reverse_lazy("blog:post_list_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": f"Edit DataLog: {self.object.title}",
                "submit_text": "Update DataLog",
                "icon": "fas fa-edit",
                "available_categories": Category.objects.all(),
                "available_tags": Tag.objects.all(),
                "available_series": Series.objects.all(),
                "system_connections": SystemLogEntry.objects.filter(post=self.object),
            }
        )

        return context

    def form_valid(self, form):
        # Recalculate reading time on update
        if form.instance.content:
            word_count = len(form.instance.content.split())
            form.instance.reading_time = max(1, word_count // 200)

        return super().form_valid(form)


class PostDeleteAdminView(BaseAdminDeleteView):
    """Delete DataLog entry with safety checks."""

    model = Post
    success_url = reverse_lazy("blog:post_list_admin")

    def get_delete_warning(self):
        return f"This will permanently delete the DataLog entry '{self.object.title}' and all associated data."

    def get_related_objects(self):
        """Show related objects that will be affected."""
        related = []

        # System connections
        connections = SystemLogEntry.objects.filter(post=self.object)
        if connections.exists():
            related.append(f"{connections.count()} system connection(s)")

        # Comments (if implemented)
        # comments = Comment.objects.filter(post=self.object)
        # if comments.exists():
        #     related.append(f"{comments.count()} comment(s)")

        return related


# Category Management Views


class CategoryListAdminView(BaseAdminListView, BulkActionMixin):
    """Category management with post counts."""

    model = Category
    template_name = "blog/admin/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count("posts")).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Manage Categories",
                "create_url": reverse_lazy("blog:category_create_admin"),
                "edit_url_name": "blog:category_update_admin",
                "delete_url_name": "blog:category_delete_admin",
            }
        )

        return context


class CategoryCreateAdminView(SlugAdminCreateView):
    """Create new category."""

    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("blog:category_list_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Create Category",
                "icon": "fas fa-tag",
            }
        )
        return context


class CategoryUpdateAdminView(BaseAdminUpdateView):
    """Update existing category."""

    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("blog:category_list_admin")


class CategoryDeleteAdminView(BaseAdminDeleteView):
    """Delete category with post reassignment."""

    model = Category
    success_url = reverse_lazy("blog:category_list_admin")

    def get_related_objects(self):
        post_count = self.object.posts.count()
        if post_count > 0:
            return [f"{post_count} DataLog entries will need reassignment"]
        return []


# Tag Management Views


class TagListAdminView(BaseAdminListView, BulkActionMixin):
    """Tag management interface."""

    model = Tag
    template_name = "blog/admin/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.annotate(post_count=Count("posts")).order_by(
            "-post_count", "name"
        )


class TagCreateAdminView(SlugAdminCreateView):
    """Create new tag."""

    model = Tag
    form_class = TagForm
    success_url = reverse_lazy("blog:tag_list_admin")


# Series Management Views


class SeriesListAdminView(BaseAdminListView):
    """Series management interface."""

    model = Series
    template_name = "blog/admin/series_list.html"
    context_object_name = "series_list"

    def get_queryset(self):
        return Series.objects.prefetch_related("posts__post").order_by("-created_at")


class SeriesCreateAdminView(SlugAdminCreateView):
    """Create new series."""

    model = Series
    form_class = SeriesForm
    success_url = reverse_lazy("blog:series_list_admin")


class SeriesUpdateAdminView(BaseAdminUpdateView):
    """Update existing series."""

    model = Series
    form_class = SeriesForm
    success_url = reverse_lazy("blog:series_list_admin")


# System Connection Management


class SystemConnectionAdminView(BaseAdminListView):
    """Manage connections between DataLogs and Systems."""

    model = SystemLogEntry
    template_name = "blog/admin/system_connections.html"
    context_object_name = "connections"

    def get_queryset(self):
        return SystemLogEntry.objects.select_related("post", "system").order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "System Connections",
                "total_connections": SystemLogEntry.objects.count(),
                "connection_types": SystemLogEntry.CONNECTION_TYPE_CHOICES,
            }
        )

        return context