"""
AURA Portfolio - Mathematical Template Filters
Custom template filters for mathematical operations in templates
Version 1.0.1: Separated Global TemplateTags
"""

from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.html import escape
from django.urls import reverse
from django.db.models import Count, Q, Avg

from datetime import datetime, timedelta
import re

register = template.Library()

#  ==============  MATHEMATICAL OPERATIONS  ============== #

@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument.
    Usage: {{ value|mul:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """
    Divides the value by the argument.
    Usage: {{ value|div:2 }}
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def subtract(value, arg):
    """
    Subtracts the argument from value.
    Usage: {{ value|subtract:5 }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """
    Calculates percentage of value from total.
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0


@register.filter
def progress_width(value, total):
    """
    Calculates width percentage for progress bars.
    Usage: style="width: {{ current|progress_width:total }}%"
    """
    try:
        if float(total) == 0:
            return 0
        percentage = (float(value) / float(total)) * 100
        # Clamp between 0-100
        return min(100, max(0, percentage))
    except (ValueError, TypeError):
        return 0


#  ==============  NUMBER FORMATTING  ============== #

@register.filter
def format_duration(minutes):
    """
    Formats duration in minutes to human-readable format.
    Usage: {{ 125|format_duration }} -> "2h 5m"
    """
    try:
        minutes = int(minutes)
        if minutes < 60:
            return f"{minutes}m"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}m"
    except (ValueError, TypeError):
        return "0m"


@register.filter
def format_number(value):
    """
    Formats large numbers with K/M suffixes.
    Usage: {{ 1500|format_number }} -> "1.5k"
    """
    try:
        value = float(value)
        if value >= 1000000:
            return f"{value / 1000000:.1f}M"
        elif value >= 1000:
            return f"{value / 1000:.1f}k"
        else:
            return str(int(value))
    except (ValueError, TypeError):
        return "0"


@register.filter
def file_size(bytes_value):
    """
    Converts bytes to human-readable file size.
    Usage: {{ 1024000|file_size }} -> "1.0 MB"
    """
    try:
        bytes_value = float(bytes_value)

        if bytes_value >= 1024**3:
            return f"{bytes_value / (1024**3):.1f} GB"
        elif bytes_value >= 1024**2:
            return f"{bytes_value / (1024**2):.1f} MB"
        elif bytes_value >= 1024:
            return f"{bytes_value / 1024:.1f} KB"
        else:
            return f"{int(bytes_value)} B"
    except (ValueError, TypeError):
        return "0 B"


#  ==============  UTILITY FIELDS  ============== #

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using variable key.
    Usage: {{ dict|get_item:key }}
    """
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter
def range_filter(value):
    """
    Creates a range from 0 to value.
    Usage: {% for i in 5|range_filter %}
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def star_rating(value, max_stars=5):
    """
    Converts numeric rating to star display.
    Usage: {{ 4.5|star_rating }} -> "★★★★⯪"
    """
    try:
        value = float(value)
        max_stars = int(max_stars)

        full_stars = int(value)
        half_star = 1 if value - full_stars >= 0.5 else 0
        empty_stars = max_stars = full_stars - half_star

        stars = "★" * full_stars
        if half_star:
            stars += "⯪"
        stars += "☆" * empty_stars

        return stars
    except (ValueError, TypeError):
        return "☆" * 5


@register.filter
def truncate_smart(text, length=150):
    """
    Smart truncation that doesn't cut off in the middle of words.
    Usage: {{ text|truncate_smart:100 }}
    """
    if not text or len(text) <= length:
        return text

    truncated = text[:length].rsplit(" ", 1)[0]
    return truncated + "..."


@register.filter
def get_field(form, field_name):
    """Get a form field by name."""
    return form[field_name]


# Previously 'add' renaming to avoid namespace issues with add
@register.filter
@stringfilter
def concat(value, arg):
    """Concatenate strings."""
    return value + arg


@register.filter
def highlight_search(text, query):
    """
    Highlights search terms in text.
    Usage: {{ text|highlight_search:query }}
    """
    if not query or not text:
        return text

    escaped_text = escape(text)
    escaped_query = escape(query)

    # Highlight each word in query
    words = escaped_query.split()
    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        escaped_text = pattern.sub(
            f'<mark class="search-highlight">{word}</mark>', escaped_text
        )
    return mark_safe(escaped_text)


#  ==============  TIME UTILITIES  ============== #

@register.filter
def time_since_published(published_date):
    """
    Returns human-readable time since publication.
    Usage: {{ post.published_date|time_since_published }}
    """
    if not published_date:
        return "Unknown"

    now = datetime.now()
    if published_date.tzinfo:
        now = timezone.now()

    diff = now - published_date

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


#  ==============  AURA-SPECFIC FILTERS  ============== #

@register.filter
def system_id_format(value):
    """Format system ID: {{ system.id|system_id_format }} -> "SYS-001" """
    try:
        return f"SYS-{int(value):03d}"
    except (ValueError, TypeError):
        return "SYS-000"


@register.filter
def datalog_id(value):
    """Format datalog ID: {{ post.id|datalog_id }} -> "LOG-001" """
    try:
        return f"LOG-{int(value):03d}"
    except (ValueError, TypeError):
        return "LOG-000"


@register.filter
def series_id(value):
    """Format series ID: {{ series.id|series_id }} -> "SER-001" """
    try:
        return f"SER-{int(value):03d}"
    except (ValueError, TypeError):
        return "SER-000"


@register.filter
def metric_color(value, thresholds="50,80"):
    """
    Returns color class based on metric value and thresholds.
    Usage: {{ cpu_usage|metric_color:"60,85" }}
    """
    try:
        value = float(value)
        low, high = map(float, thresholds.split(","))

        if value >= high:
            # Red/Warning
            return "metric-high"
        elif value >= low:
            # Yellow/Caution
            return "metric-medium"
        else:
            # Green/Good
            return "metric-low"
    except (ValueError, TypeError):
        return "metric-unknown"


@register.filter
def status_color(status):
    """Get color for system status"""
    colors = {
        "draft": "var(--color-gunmetal)",
        "in_development": "var(--color-yellow)",
        "testing": "var(--color-coral)",
        "deployed": "var(--color-mint)",
        "published": "var(--color-teal)",
        "archived": "var(--color-gunmetal)",
        "operational": "var(--color-mint)",
        "warning": "var(--color-yellow)",
        "error": "var(--color-coral)",
    }
    return colors.get(status, "var(--color-teal)")


@register.inclusion_tag("components/pagination.html")
def render_pagination(page_obj, request):
    """
    Renders AURA-styled pagination.
    Usage: {% render_pagination page_obj request %}
    """
    return {
        "page_obj": page_obj,
        "request": request,
    }


@register.simple_tag(takes_context=True)
def active_nav(context, url_name):
    """
    Returns 'active' if current URL matches the given URL name.
    Usage: {% active_nav 'blog:post_list' %}
    """
    request = context["request"]
    if request.resolver_match and request.resolver_match.url_name == url_name:
        return "active"
    return ""


@register.simple_tag(takes_context=True)
def build_url(context, **kwargs):
    """
    Builds URL with current GET params plus new ones.
    Usage: {% build_url sort='title' page=2 %}
    """
    request = context["request"]
    params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value

    if params:
        return f"?{params.urlencode()}"
    return ""


#  ==============  COMPLEX TAG FUNCTIONS  ============== #

@register.simple_tag
def calculate(operation, value1, value2):
    """
    Performs calcculations in templates.
    Usage: {% calculate "mul" 2 5 %} -> 10
    """
    try:
        val1 = float(value1)
        val2 = float(value2)

        operations = {
            "add": val1 + val2,
            "subtract": val1 - val2,
            "multiply": val1 * val2,
            "divide": val1 / val2 if val2 != 0 else 0,
            "percentage": (val1 / val2 * 100) if val2 != 0 else 0,
        }

        result = operations.get(operation, 0)
        return round(result, 2) if isinstance(result, float) else result
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def progress_bar(value, total, css_class="", show_text=True):
    """Generate progress bar HTML"""
    try:
        percentage = min(100, max(0, (float(value) / float(total)) * 100))

        html = f"""
        <div class="progress-container {css_class}">
            <div class="progress-bar" style="width: {percentage}%;"></div>
            {f'<span class="progress-text">{percentage:.1f}%</span>'
             if show_text else ""}
        </div>
        """
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe(
            '<div class="progress-container"><div class="progress-bar" ' \
            'style="width: 0%;"></div></div>'
        )


@register.simple_tag
def system_status_indicator(status, size="md"):
    """Generate status indicator HTML"""
    sizes = {
        "sm": "status-indicator-sm", "md": "", "lg": "status-indicator-lg"}

    size_class = sizes.get(size, "")

    html = f'''
    <div class="status-indicator {status} {size_class}"
    title="{status.replace("_", " ").title()}"></div>
    '''
    return mark_safe(html)

#  ==============  PLACEHOLDER  ============== #



# @register.simple_tag
# def system_progress_bar(system):
#     """Render a progress bar for system development."""
#     progress = system.get_development_progress()

#     html = f"""
#     <div class="system-progress-container">
#         <div class="progress-bar-bg">
#             <div class="progress-bar-fill" style="width: {progress}%"></div>
#         </div>
#         <span class="progress-text">{progress}%</span>
#     </div>
#     """
#     return mark_safe(html)
