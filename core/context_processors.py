from .models import SocialLink


def global_context(request):
    """Add global context variables to all templates."""
    return {
        'social_links': SocialLink.objects.all().order_by('display_order'),
    }


def admin_context(request):
    """Add global admin context to all templates."""

    context = {}

    # Check if user is in admin area
    if request.path.startswith("/aura-admin/"):
        context["in_admin"] = True

        # Add admin navigation data
        if request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        ):
            from blog.models import Post, Category
            from projects.models import SystemModule, Technology

            context.update(
                {
                    "admin_stats": {
                        "total_posts": Post.objects.count(),
                        "total_systems": SystemModule.objects.count(),
                        "total_categories": Category.objects.count(),
                        "total_technologies": Technology.objects.count(),
                    },
                    "admin_quick_links": [
                        {
                            "name": "DataLogs",
                            "url": "/aura-admin/blog/",
                            "icon": "fas fa-database",
                            "color": "lavender",
                        },
                        {
                            "name": "Systems",
                            "url": "/aura-admin/projects/",
                            "icon": "fas fa-microchip",
                            "color": "cyan",
                        },
                    ],
                }
            )

    return context
