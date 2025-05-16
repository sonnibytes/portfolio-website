# blog/context_processors.py

from blog.models import Post, Category


def blog_context(request):
    """
    Add blog-related context variables to all templates.
    """
    return {
        "categories": Category.objects.all(),
        "total_logs_count": Post.objects.filter(status="published").count(),
    }
