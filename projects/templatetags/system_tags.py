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
from django.template.loader import render_to_string
import re
import colorsys


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
    """Convert hex color to RGB values for CSS custom properties."""
    if not hex_color or not hex_color.startswith("#"):
        return "38, 198, 218"  # Default teal RGB

    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    if len(hex_color) != 6:
        return "38, 198, 218"  # Default teal RGB

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    except ValueError:
        return "38, 198, 218"  # Default teal RGB


# Usage in templates:
# Original color: {{ technology.color }}
# Lightened version: {{ technology.color|lighten_if_dark }}
# Readable text version: {{ technology.color|readable_color }}
# RGB values: {{ technology.color|hex_to_rgb }}
# Check if dark: {% if technology.color|is_dark_color %}...{% endif %}

@register.filter
def lighten_if_dark(hex_color, lightness_threshold=0.4):
    """
    Check if a hex color is too dark for readability on dark background.
    If too dark, return a lightened version. If light enough, return original.

    lightness_threshold: 0.0 (black) to 1.0 (white), default 0.4 (40%)
    """
    if not hex_color or not hex_color.startswith("#"):
        return "#26c6da"  # Default teal

    # Remove # and handle 3-digit hex
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    if len(hex_color) != 6:
        return "#26c6da"  # Default teal

    try:
        # Convert hex to RGB (0-255)
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        # Convert RGB to HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # If lightness is below threshold, lighten it
        if l < lightness_threshold:
            # Increase lightness to make it more readable
            # We want it bright enough to read, but not washed out
            new_lightness = max(
                0.6, lightness_threshold + 0.2
            )  # At least 60% lightness

            # Convert back to RGB
            new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_lightness, s)

            # Convert to hex
            new_hex = "#{:02x}{:02x}{:02x}".format(
                int(new_r * 255), int(new_g * 255), int(new_b * 255)
            )
            return new_hex
        else:
            # Color is light enough, return original
            return f"#{hex_color}"

    except (ValueError, OverflowError):
        return "#26c6da"  # Default teal on any error


@register.filter
def readable_color(hex_color):
    """
    Return a readable version of a color for text/stats display.
    This is a more aggressive lightening specifically for text readability.
    """
    return lighten_if_dark(hex_color, lightness_threshold=0.3)


@register.filter
def is_dark_color(hex_color, threshold=0.4):
    """
    Check if a color is considered "dark" (returns True/False).
    Useful for conditional styling in templates.
    """
    if not hex_color or not hex_color.startswith("#"):
        return False

    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    if len(hex_color) != 6:
        return False

    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return l < threshold
    except (ValueError, OverflowError):
        return False


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


# =========== Dashboard Panel Component  =========== #


# @register.inclusion_tag('projects/components/dashboard_panel.html', takes_context=True)
# def dashboard_panel(context, style='dashboard', color='teal', title=None, subtitle=None, icon=None, **kwargs):
#     """
#     Flexible dashboard panel wrapper for systems app content.

#     Usage:
#     {% dashboard_panel style="dashboard" color="purple" %}
#         <h3>System Health</h3>
#         <p>All systems operational</p>
#     {% enddashboard_panel %}

#     Parameters:
#     - style: dashboard, grid, activity, component, chart, alert, metric, status
#     - color: teal, purple, coral, lavender, mint, yellow, navy, gunmetal
#     - title: Override auto-detected title
#     - subtitle: Optional subtitle
#     - icon: Optional icon class
#     """

#     # Get nodelist content
#     nodelist = kwargs.get('nodelist', '')

#     # Auto-detect title and content if not provided
#     if not title and nodelist:
#         title = _extract_title_from_content(nodelist)

#     # Determine panel config based on style
#     panel_config = _get_panel_config(style, color)

#     return {
#         'content': nodelist,
#         'title': title,
#         'subtitle': subtitle,
#         'icon': icon,
#         'style': style,
#         'color': color,
#         'panel_config': panel_config,
#         'css_classes': _build_css_classes(style, color),
#         'data_attributes': _build_data_attributes(style, **kwargs),
#     }


@register.tag('dashboard_panel')
def do_dashboard_panel(parser, token):
    """
    Parse the dashboard_panel template tag.

    Usage:
    {% dashboard_panel style="dashboard" color="teal" %}
        <h3>Content</h3>
    {% enddashboard_panel %}
    """
    bits = token.split_contents()
    tag_name = bits[0]

    # Parse arguments
    kwargs = {}
    for bit in bits[1:]:
        if '=' in bit:
            key, value = bit.split('=', 1)
            # Remove quotes from value
            value = value.strip('"\'')
            kwargs[key] = value

    # Parse until end tag
    nodelist = parser.parse(('enddashboard_panel'))
    parser.delete_first_token()

    return DashboardPanelNode(nodelist, **kwargs)


class DashboardPanelNode(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        # Render the content inside the tag
        content = self.nodelist.render(context)

        # Get the parameters w defaults
        style = self.kwargs.get('style', 'dashboard')
        color = self.kwargs.get('color', 'teal')
        title = self.kwargs.get('title')
        subtitle = self.kwargs.get('subtitle')
        icon = self.kwargs.get('icon')

        # Auto-detect title if not provided
        if not title:
            title = _extract_title_from_content(content)

        # Create a clean kwargs dict without style and color to avoid conflicts
        clean_kwargs = {k: v for k, v in self.kwargs.items() if k not in ['style', 'color']}

        # Use the template to render the final output
        return render_to_string('projects/components/dashboard_panel.html', {
            'content': content,
            'title': title,
            'subtitle': subtitle,
            'icon': icon,
            'style': style,
            'color': color,
            'panel_config': _get_panel_config(style, color),
            'css_classes': _build_css_classes(style, color),
            'data_attributes': _build_data_attributes(style, color, **clean_kwargs),
        }, context.request)


def _extract_title_from_content(content):
    """
    Auto-extract title from content (looks for h1-h6 tags).
    """

    # Look for heading tags
    heading_match = re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>", content, re.IGNORECASE | re.DOTALL)
    if heading_match:
        # Strip HTML tags from heading content
        title = re.sub(r'<[^>]+>', '', heading_match.group(1))
        return title.strip()

    # Look for elements w title-like classes
    title_match = re.search(r'<[^>]+class="[^"]*(?:title|heading|header)[^"]*"[^>]*>(.*?)</[^>]+>', content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1))
        return title.strip()

    return None


def _get_panel_config(style, color):
    """
    Returns config dict for different panel styles.
    """
    configs = {
        "dashboard": {
            "layout": "standard",
            "padding": "xl",
            "header_style": "prominent",
            "content_style": "standard",
            "animations": ["fade-in", "slide-up"],
        },
        "grid": {
            "layout": "grid",
            "padding": "lg",
            "header_style": "compact",
            "content_style": "grid",
            "animations": ["fade-in"],
        },
        "activity": {
            "layout": "timeline",
            "padding": "md",
            "header_style": "compact",
            "content_style": "timeline",
            "animations": ["slide-in-left"],
        },
        "component": {
            "layout": "component-list",
            "padding": "lg",
            "header_style": "standard",
            "content_style": "component-grid",
            "animations": ["fade-in", "scale-in"],
        },
        "chart": {
            "layout": "chart-container",
            "padding": "lg",
            "header_style": "chart-header",
            "content_style": "chart-content",
            "animations": ["fade-in", "chart-draw"],
        },
        "alert": {
            "layout": "alert",
            "padding": "md",
            "header_style": "alert-header",
            "content_style": "alert-content",
            "animations": ["pulse", "slide-down"],
        },
        "metric": {
            "layout": "metric-display",
            "padding": "lg",
            "header_style": "metric-header",
            "content_style": "metric-content",
            "animations": ["counter-up", "glow"],
        },
        "status": {
            "layout": "status-display",
            "padding": "md",
            "header_style": "status-header",
            "content_style": "status-content",
            "animations": ["status-pulse"],
        },
    }

    return configs.get(style, configs["dashboard"])


def _build_css_classes(style, color):
    """
    Build CSS class string based on style and color.
    """
    base_classes = ['dashboard-panel', 'glass-card']

    # Style-specific classes
    style_classes = {
        'dashboard': ['panel-standard'],
        'grid': ['panel-grid'],
        'activity': ['panel-activity', 'timeline-container'],
        'component': ['panel-component', 'component-grid'],
        'chart': ['panel-chart', 'chart-container'],
        'alert': ['panel-alert', 'alert-container'],
        'metric': ['panel-metric', 'metric-display'],
        'status': ['panel-status', 'status-display'],
    }

    # Color classes
    color_classes = {
        'teal': ['accent-teal'],
        'purple': ['accent-purple'],
        'coral': ['accent-coral'],
        'lavender': ['accent-lavender'],
        'mint': ['accent-mint'],
        'yellow': ['accent-yellow'],
        'navy': ['accent-navy'],
        'gunmetal': ['accent-gunmetal'],
    }

    # Combine all classess
    all_classes = base_classes + style_classes.get(style, []) + color_classes.get(color, ['accent-teal'])

    return ' '.join(all_classes)


def _build_data_attributes(style, color, **kwargs):
    """
    Build data attributes for Javascript interaction.
    Fixed to use _ for parsing
    """
    data_attrs = {
        'data-panel-style': style,
        'data-panel-color': color,
    }

    # Add style-specific data attributes
    if style == 'chart':
        data_attrs['data-chart-type'] = kwargs.get('chart_type', 'line')
        data_attrs['data-chart-animate'] = 'true'

    elif style == 'activity':
        data_attrs['data-activity-realtime'] = kwargs.get('realtime', 'false')
        data_attrs['data-activity-limit'] = kwargs.get('limit', '10')

    elif style == 'metric':
        data_attrs['data-metric-animate'] = 'true'
        data_attrs['data-metric-precision'] = kwargs.get('precision', '2')

    elif style == 'alert':
        data_attrs['data-alert-level'] = kwargs.get('level', 'info')
        data_attrs['data-alert-dismissible'] = kwargs.get('dismissible', 'false')
        # Template-friendly versions w underscores
        data_attrs['alert_level'] = kwargs.get('level', 'info')
        data_attrs['alert_dismissible'] = kwargs.get('dismissible', 'false')

    return data_attrs


@register.simple_tag
def panel_icon(style, custom_icon=None):
    """
    Return appropriate icon for panel style.
    """
    if custom_icon:
        return custom_icon

    icons = {
        'dashboard': 'dashboard',
        'grid': 'grid_view',
        'activity': 'timeline',
        'component': 'widgets',
        'chart': 'analytics',
        'alert': 'notification_important',
        'metric': 'speed',
        'status': 'health_and_safety',
    }

    return icons.get(style, 'dashboard')


@register.filter
def panel_color_var(color):
    """
    Convert color name to CSS variable.
    """
    color_vars = {
        "teal": "var(--color-teal)",
        "purple": "var(--color-purple)",
        "coral": "var(--color-coral)",
        "lavender": "var(--color-lavender)",
        "mint": "var(--color-mint)",
        "yellow": "var(--color-yellow)",
        "navy": "var(--color-navy)",
        "gunmetal": "var(--color-gunmetal)",
    }

    return color_vars.get(color, "var(--color-teal)")
