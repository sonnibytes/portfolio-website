from blog.models import Post, Category, Tag
from django.urls import reverse
from django.utils import timezone


def blog_context(request):
    """
    Add blog-related context variables to all templates.
    """
    categories = Category.objects.all()
    total_logs = Post.objects.filter(status='published').count()
    tags_count = Tag.objects.count()
    return {
        "categories": categories,
        "total_logs_count": total_logs,
        "categories_count": categories.count(),
        "tags_count": tags_count,
        "links": [
            {
                "label": "All Logs",
                "href": reverse("blog:post_list"),
                "badge": total_logs
            },
            {
                "label": "Archive",
                "href": reverse("blog:archive")
            },
            {
                "label": "Tags",
                "href": reverse("blog:tag_list"),
                "badge": tags_count
            },
            {
                "label": "Categories",
                "href": reverse("blog:categories_overview"),
                "badge": categories.count()
            },
        ],
        "datalogs_stats": {
            'total_entries': total_logs,
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),
            'latest_entry': Post.objects.filter(status='published').first(),
            'system_status': 'operational',
            'last_updated': timezone.now(),
        },
    }
