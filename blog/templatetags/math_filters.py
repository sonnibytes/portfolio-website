"""
AURA Portfolio - Mathematical Template Filters
Custom template filters for mathematical operations in templates
"""

from django import template

register = template.Library()


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
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}k"
        else:
            return str(int(value))
    except (ValueError, TypeError):
        return "0"


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
def metric_color(value, thresholds="50,80"):
    """
    Returns color class based on metric value and thresholds.
    Usage: {{ cpu_usage|metric_color:"60,85" }}
    """
    try:
        value = float(value)
        low, high = map(float, thresholds.split(','))

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
            'add': val1 + val2,
            'subtract': val1 - val2,
            'multiply': val1 * val2,
            'divide': val1 / val2 if val2 !=0 else 0,
            'percentage': (val1 / val2 * 100) if val2 != 0 else 0, 
        }

        return operations.get(operation, 0)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
