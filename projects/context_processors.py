from projects.models import SystemModule, Technology
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone


def systems_context(request):
    """
    System-related context variables available across all templates.
    """
    all_systems = SystemModule.objects.all()
    active_systems = SystemModule.objects.filter(status__in=['deployed', 'published'])
    total_tech = Technology.objects.count()

    return {
        'total_systems': all_systems.count(),
        'active_systems': active_systems.count(),
        'total_technologies': total_tech,
    }
