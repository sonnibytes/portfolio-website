"""
 * Systems-specific template tags and filters
 * Version 1.0.1: New w Global aura_filters
"""

from django import template
from django.utils.safestring import mark_safe
from ..models import SystemModule, Technology, SystemType

register = template.Library()


@register.simple_tag
def system_complexity_display(complexity):
    """Visual complexity indicator"""
    filled = "●" * complexity
    empty = "○" * (5 - complexity)
    return mark_safe(f'<span class="complexity-display">{filled}{empty}</span>')


@register.inclusion_tag("projects/components/tech_badges.html")
def tech_badges(system, limit=4):
    """Render technology badges for a system"""
    technologies = system.technologies.all()[:limit]
    remaining = max(0, system.technologies.count() - limit)
    return {
        "technologies": technologies,
        "remaining_count": remaining,
        "system": system,
    }


@register.simple_tag
def system_metrics_json(system):
    """Export system metrics as JSON for JavaScript"""
    import json

    metrics = {
        "completion": system.completion_percent,
        "complexity": system.complexity,
        "status": system.status,
        "technologies_count": system.technologies.count(),
    }
    return mark_safe(json.dumps(metrics))
