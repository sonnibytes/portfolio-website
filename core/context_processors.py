from .models import SocialLink


def global_context(request):
    """Add global context variables to all templates."""
    return {
        'social_links': SocialLink.objects.all().order_by('display_order'),
    }
