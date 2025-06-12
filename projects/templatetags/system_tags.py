"""
 * Systems-specific template tags and filters
 * Version 1.0.1: New w Global aura_filters
"""

from django import template
from django.utils.safestring import mark_safe
from ..models import SystemModule, Technology, SystemType
from bs4 import BeautifulSoup
from markdownx.utils import markdownify as md
from django.utils.text import slugify


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


@register.filter
def hex_to_rgb(hex_color):
    """Convert hex color to RGB values for CSS variables"""
    if not hex_color or not hex_color.startswith("#"):
        return "0, 240, 255"  # Default teal

    hex_color = hex_color.lstrip("#")
    try:
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        return f"{rgb[0]}, {rgb[1]}, {rgb[2]}"
    except:
        return "0, 240, 255"  # Default teal
    
# =========== Markdown (Markdownx - bs4) Filter  =========== #


@register.filter
def markdownify(text):
    """
    Filter to convert markdown text to HTML using markdownx util,
    and add IDs to headings for table of contents links to work.
    """
    # First convert markdown to HTML
    html_content = md(text)

    # Use BeautifulSoup to parse and modify HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all heading elements (h1, h2, h3, etc.)
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        # Create an ID from heading text
        heading_id = slugify(heading.get_text())

        # Set ID attr on heading element
        heading["id"] = heading_id

    # Return modified HTML
    return mark_safe(str(soup))
