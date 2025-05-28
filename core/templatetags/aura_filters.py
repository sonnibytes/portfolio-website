"""
AURA Portfolio - Global Template Filters
Advanced User Repository & Archive - Mathematical operations, formatting, and AURA utilities
Version 1.0.2: Separated Global TemplateTags, Updated/Enhanced, More Thorough
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
import json
import math

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
def add_filter(value, arg):
    """
    Adds the argument to the value (avoiding conflict with built-in add).
    Usage: {{ value|add_filter:5 }}
    """
    try:
        return float(value) + float(arg)
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
    Calculates width percentage for progress bars (clamped 0-100).
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


@register.filter
def clamp(value, range_str="0,100"):
    """
    Clamps value between min and max.
    Usage: {{ value|clamp:"0,100" }}
    """
    try:
        min_val, max_val = map(float, range_str.split(","))
        return max(min_val, min(max_val, float(value)))
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
    Usage: {{ 1,024,000|file_size }} -> "1.0 MB"
    """
    try:
        bytes_value = float(bytes_value)

        if bytes_value >= 1024**3:  # 1,073,741,824
            return f"{bytes_value / (1024**3):.1f} GB"
        elif bytes_value >= 1024**2:  # 1,048,576
            return f"{bytes_value / (1024**2):.1f} MB"
        elif bytes_value >= 1024:
            return f"{bytes_value / 1024:.1f} KB"
        else:
            return f"{int(bytes_value)} B"
    except (ValueError, TypeError):
        return "0 B"


@register.filter
def format_decimal(value, places=2):
    """
    Formats decimal to specified places.
    Usage: {{ 3.14159|format_decimal:2 }} -> "3.14"
    """
    try:
        return f"{float(value):.{int(places)}f}"
    except (ValueError, TypeError):
        return "0.00"


@register.filter
def format_currency(value, symbol="$"):
    """
    Formats number as currency.
    Usage: {{ 1234.56|format_currency }} -> "$1,234.56"
    """
    try:
        return f"{symbol}{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"


#  ==============  UTILITY FILTERS  ============== #

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
def get_attribute(obj, attr_name):
    """
    Gets an attribute from an object using a variable name.
    Usage: {{ object|get_attribute:"field_name" }}
    """
    try:
        return getattr(obj, attr_name, None)
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
        empty_stars = max_stars - full_stars - half_star

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
    Smart truncation preserving words and avoiding orphaned characters.
    Usage: {{ text|truncate_smart:150 }}
    """
    if not text:
        return ""

    if len(text) <= length:
        return text

    truncated = text[:length]
    # Find last space to avoid cutting words
    last_space = truncated.rfind(" ")
    if last_space > length * 0.8:  # If space is reasonably close to end
        truncated = truncated[:last_space]

    return truncated + "..."


@register.filter
def split_string(value, delimiter=","):
    """
    Splits a string by delimiter.
    Usage: {{ "a,b,c"|split_string:"," }}
    """
    try:
        return value.split(delimiter) if value else []
    except (AttributeError, TypeError):
        return []


@register.filter
def join_with(value, separator=" • "):
    """
    Joins a list with a custom separator.
    Usage: {{ list|join_with:" • " }}
    """
    try:
        return separator.join(str(item) for item in value)
    except (TypeError, AttributeError):
        return ""

# moved back to blog_tags
# @register.filter
# def get_field(form, field_name):
#     """Get a form field by name."""
#     return form[field_name]

# moved back to blog_tags
# # Previously 'add' renaming to avoid namespace issues with add
# @register.filter
# @stringfilter
# def concat(value, arg):
#     """Concatenate strings."""
#     return value + arg


# not on suggested, but leaving here, think it'll come in handy
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
# This is best way, suggested throws errors w naive and aware
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


@register.filter
def format_date_iso(value):
    """
    Formats date in ISO format for JavaScript.
    Usage: {{ date|format_date_iso }}
    """
    try:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)
    except (AttributeError, TypeError):
        return ""


@register.filter
def days_until(value):
    """
    Calculate days until a future date.
    Usage: {{ deadline|days_until }}
    """
    if not value:
        return 0

    try:
        now = timezone.now().date()
        if hasattr(value, "date"):
            target_date = value.date()
        else:
            target_date = value

        diff = target_date - now
        return diff.days
    except (AttributeError, TypeError):
        return 0


#  ==============  AURA-SPECFIC FILTERS  ============== #

@register.filter
def system_id_format(value):
    """
    Format system ID with zero padding.
    Usage: {{ system.id|system_id_format }} -> "SYS-001"
    """
    try:
        return f"SYS-{int(value):03d}"
    except (ValueError, TypeError):
        return "SYS-000"


@register.filter
def datalog_id(value):
    """
    Format datalog ID with zero padding.
    Usage: {{ post.id|datalog_id }} -> "LOG-001"
    """
    try:
        return f"LOG-{int(value):03d}"
    except (ValueError, TypeError):
        return "LOG-000"


@register.filter
def series_id(value):
    """
    Format series ID with zero padding.
    Usage: {{ series.id|series_id }} -> "SER-001"
    """
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
    """
    Get CSS color variable for system status.
    Usage: style="color: {{ system.status|status_color }};"
    """
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
        "info": "var(--color-teal)",
        "inactive": "var(--color-gunmetal)",
    }
    return colors.get(status, "var(--color-teal)")


@register.filter
def complexity_display(complexity):
    """
    Visual complexity indicator using filled/empty circles.
    Usage: {{ system.complexity|complexity_display }}
    """
    try:
        complexity = int(complexity)
        filled = "●" * complexity
        empty = "○" * (5 - complexity)
        return mark_safe(f'<span class="complexity-display">{filled}{empty}</span>')
    except (ValueError, TypeError):
        return mark_safe('<span class="complexity-display">○○○○○</span>')


@register.filter
def priority_class(priority):
    """
    Get CSS class for priority level.
    Usage: class="{{ priority|priority_class }}"
    """
    classes = {
        1: "priority-low",
        2: "priority-normal",
        3: "priority-high",
        4: "priority-critical",
    }
    return classes.get(priority, "priority-normal")


@register.filter
def hex_color_brightness(hex_color):
    """
    Calculate brightness of hex color (0-255).
    Usage: {{ "#ff0000"|hex_color_brightness }}
    """
    try:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Calculate perceived brightness
        return (r * 299 + g * 587 + b * 114) / 1000
    except (ValueError, TypeError):
        return 128


@register.filter
def tech_icon_fallback(tech_name):
    """
    Generate fallback icon class for technologies.
    Usage: {{ tech.name|tech_icon_fallback }}
    """
    fallback_icons = {
        "python": "fab fa-python",
        "javascript": "fab fa-js-square",
        "react": "fab fa-react",
        "django": "fas fa-code",
        "node": "fab fa-node-js",
        "docker": "fab fa-docker",
        "git": "fab fa-git-alt",
        "html": "fab fa-html5",
        "css": "fab fa-css3-alt",
        "sass": "fab fa-sass",
        "vue": "fab fa-vuejs",
        "angular": "fab fa-angular",
        "bootstrap": "fab fa-bootstrap",
        "database": "fas fa-database",
        "api": "fas fa-plug",
        "ml": "fas fa-brain",
        "ai": "fas fa-robot",
    }

    tech_lower = tech_name.lower()
    for key, icon in fallback_icons.items():
        if key in tech_lower:
            return icon

    return "fas fa-code"  # Default fallback

# # moved back to blog_tags
# @register.inclusion_tag("components/pagination.html")
# def render_pagination(page_obj, request):
#     """
#     Renders AURA-styled pagination.
#     Usage: {% render_pagination page_obj request %}
#     """
#     return {
#         "page_obj": page_obj,
#         "request": request,
#     }

# # moved back to blog_tags
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

# # moved back to blog_tags
# @register.simple_tag(takes_context=True)
# def build_url(context, **kwargs):
#     """
#     Builds URL with current GET params plus new ones.
#     Usage: {% build_url sort='title' page=2 %}
#     """
#     request = context["request"]
#     params = request.GET.copy()

#     for key, value in kwargs.items():
#         if value is None:
#             params.pop(key, None)
#         else:
#             params[key] = value

#     if params:
#         return f"?{params.urlencode()}"
#     return ""

#  ==============  CONTENT PROCESSING  ============== #


@register.filter
def extract_first_paragraph(content):
    """
    Extract first paragraph from HTML or markdown content.
    Usage: {{ content|extract_first_paragraph }}
    """
    if not content:
        return ""

    # Remove markdown headers and code blocks
    content = re.sub(r"^#+\s+.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

    # Split by paragraphs and get first non-empty one
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    return paragraphs[0] if paragraphs else ""


@register.filter
def count_words(content):
    """
    Count words in content.
    Usage: {{ content|count_words }}
    """
    if not content:
        return 0

    # Remove markdown/html and count words
    clean_content = re.sub(r"<[^>]+>", "", content)
    clean_content = re.sub(r"[#*`_\[\]()]", "", clean_content)
    words = re.findall(r"\b\w+\b", clean_content)
    return len(words)


@register.filter
def reading_time(content, wpm=200):
    """
    Calculate reading time in minutes.
    Usage: {{ content|reading_time }} or {{ content|reading_time:250 }}
    """
    word_count = count_words(content)
    minutes = math.ceil(word_count / wpm)
    return max(1, minutes)  # Minimum 1 minute


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
            "power": val1**val2,
            "modulo": val1 % val2 if val2 != 0 else 0,
        }

        result = operations.get(operation, 0)
        # Return integer if it's a whole number, else float
        return int(result) if result == int(result) else round(result, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def random_choice(*choices):
    """
    Returns a random choice from the given options.
    Usage: {% random_choice "red" "blue" "green" %}
    """
    import random

    return random.choice(choices) if choices else ""


@register.simple_tag
def current_timestamp():
    """
    Returns current timestamp in ISO format.
    Usage: {% current_timestamp %}
    """
    return timezone.now().isoformat()


@register.simple_tag
def json_encode(value):
    """
    Encode value as JSON for JavaScript.
    Usage: var data = {{ data|json_encode }};
    """
    try:
        return mark_safe(json.dumps(value))
    except (TypeError, ValueError):
        return mark_safe("null")


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """
    Build query string with current GET parameters plus new ones.
    Usage: {% query_string page=2 sort="name" %}
    """
    request = context.get("request")
    if not request:
        return ""

    get_params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            get_params.pop(key, None)
        else:
            get_params[key] = value

    return f"?{get_params.urlencode()}" if get_params else ""


@register.simple_tag
def percentage_of(value, total):
    """
    Calculate percentage and return formatted string.
    Usage: {% percentage_of 25 100 %} -> "25.0%"
    """
    try:
        if float(total) == 0:
            return "0%"
        result = (float(value) / float(total)) * 100
        return f"{result:.1f}%"
    except (ValueError, TypeError):
        return "0%"


# moved to aura_components
# @register.simple_tag
# def progress_bar(value, total, css_class="", show_text=True):
#     """Generate progress bar HTML"""
#     try:
#         percentage = min(100, max(0, (float(value) / float(total)) * 100))

#         html = f"""
#         <div class="progress-container {css_class}">
#             <div class="progress-bar" style="width: {percentage}%;"></div>
#             {f'<span class="progress-text">{percentage:.1f}%</span>'
#              if show_text else ""}
#         </div>
#         """
#         return mark_safe(html)
#     except (ValueError, TypeError):
#         return mark_safe(
#             '<div class="progress-container"><div class="progress-bar" ' \
#             'style="width: 0%;"></div></div>'
#         )

# moved to aura_components
# @register.simple_tag
# def system_status_indicator(status, size="md"):
#     """Generate status indicator HTML"""
#     sizes = {
#         "sm": "status-indicator-sm", "md": "", "lg": "status-indicator-lg"}

#     size_class = sizes.get(size, "")

#     html = f'''
#     <div class="status-indicator {status} {size_class}"
#     title="{status.replace("_", " ").title()}"></div>
#     '''
#     return mark_safe(html)

#  ==============  DEBUGGING FILTERS  ============== #

@register.filter
def debug_type(value):
    """
    Returns the type of the value (for debugging).
    Usage: {{ value|debug_type }}
    """
    return type(value).__name__


@register.filter
def debug_dir(value):
    """
    Returns the dir() of the value (for debugging).
    Usage: {{ value|debug_dir }}
    """
    return mark_safe(f"<pre>{dir(value)}</pre>")


@register.simple_tag
def debug_context(context_var):
    """
    Debug template context variable.
    Usage: {% debug_context variable_name %}
    """
    return mark_safe(f"<pre>{repr(context_var)}</pre>")



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
