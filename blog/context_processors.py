# blog/context_processors.py

from blog.models import Post, Category
from django.urls import reverse


def blog_context(request):
    """
    Add blog-related context variables to all templates.
    """
    categories = Category.objects.all()
    total_logs = Post.objects.filter(status='published').count()
    return {
        "categories": categories,
        "total_logs_count": total_logs,
        "links": [
            {
                "label": "All Logs",
                "href": reverse("blog:post_list"),
                "badge": total_logs
            },
            {
                "label": "Categories",
                "id": "catDrop",
                "dropdown": [
                    {"label": cat.name, "href": reverse("blog:category", args=[cat.slug])} for cat in categories
                ]
            },
            {
                "label": "Archive",
                "href": reverse("blog:archive")
            },
            {
                "label": "Tags",
                "href": reverse("blog:tags")
            },
        ]
    }
