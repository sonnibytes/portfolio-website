# core/templatetags/admin_filters.py
"""
Template filters for admin interface
Minimal implementation for testing
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def message_icon(tag):
    """Return appropriate icon for message tags."""
    icons = {
        "success": "check-circle",
        "error": "exclamation-circle",
        "warning": "exclamation-triangle",
        "info": "info-circle",
    }
    return icons.get(tag, "info-circle")


@register.filter
def status_color(status):
    """Return color class for status."""
    colors = {
        "published": "success",
        "draft": "warning",
        "deployed": "info",
        "in_development": "primary",
        "healthy": "success",
        "warning": "warning",
        "critical": "danger",
    }
    return colors.get(status, "secondary")


@register.filter
def priority_badge(priority):
    """Return priority badge HTML."""
    if priority is None:
        return mark_safe('<span class="badge bg-secondary">-</span>')

    badges = {
        1: '<span class="badge bg-info">Low</span>',
        2: '<span class="badge bg-primary">Medium</span>',
        3: '<span class="badge bg-warning">High</span>',
        4: '<span class="badge bg-danger">Critical</span>',
    }
    return mark_safe(
        badges.get(priority, '<span class="badge bg-secondary">Unknown</span>')
    )


@register.filter
def completion_bar(percentage):
    """Return completion progress bar HTML."""
    if percentage is None:
        percentage = 0

    color = (
        "success" if percentage >= 80 else "warning" if percentage >= 50 else "danger"
    )

    html = f'''
    <div class="progress" style="height: 8px;">
        <div class="progress-bar bg-{color}" 
             role="progressbar" 
             style="width: {percentage}%" 
             aria-valuenow="{percentage}" 
             aria-valuemin="0" 
             aria-valuemax="100">
        </div>
    </div>
    <small class="text-muted">{percentage}%</small>
    '''
    return mark_safe(html)


@register.simple_tag
def admin_card(*args, **kwargs):
    """
    Generate admin dashboard card HTML.

    Supports both syntaxes:
    {% admin_card "Title" value "icon" "color" %}  (positional)
    {% admin_card title="Title" value=value icon="icon" color="color" %}  (named)
    """
    # Handle named parameters
    if kwargs:
        title = kwargs.get("title", "Metric")
        value = kwargs.get("value", 0)
        icon = kwargs.get("icon", "fas fa-chart-bar")
        color = kwargs.get("color", "primary")
        trend = kwargs.get("trend", None)

    # Handle positional parameters
    elif args:
        title = args[0] if len(args) > 0 else "Metric"
        value = args[1] if len(args) > 1 else 0
        icon = args[2] if len(args) > 2 else "fas fa-chart-bar"
        color = args[3] if len(args) > 3 else "primary"
        trend = args[4] if len(args) > 4 else None

    # Default fallback
    else:
        title = "Metric"
        value = 0
        icon = "fas fa-chart-bar"
        color = "primary"
        trend = None

    # Handle icon name hyphens via lookup for now
    icons = {
        'database': 'fas fa-database',
        'microchip': 'fas fa-microchip',
        'tags': 'fas fa-tags',
        'code_branch': 'fas fa-code-branch',
    }

    clean_icon = icon or icons.get(icon, 'fas fa-chart-bar')

    # Ensure value is not None
    if value is None:
        value = 0

    # Map color names to actual CSS colors for compatibility
    color_map = {
        "primary": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#06b6d4",
        "lavender": "#a855f7",
        "purple": "#8b5cf6",
        "cyan": "#06b6d4",
        "emerald": "#10b981",
        "amber": "#f59e0b",
        "rose": "#f43f5e",
        "blue": "#3b82f6",
        "yellow": "#eab308",
    }

    icon_color = color_map.get(color, color_map["primary"])

    trend_html = ""
    if trend:
        trend_icon = (
            "fa-arrow-up text-success" if trend > 0 else "fa-arrow-down text-danger"
        )
        trend_html = f'<small class="text-muted ms-2"><i class="fas {trend_icon}"></i> {abs(trend)}%</small>'

    html = f'''
    <div class="admin-metric-card glass-card">
        <div class="metric-header">
            <div class="metric-icon" style="color: {icon_color};">
                <i class="{clean_icon}"></i>
            </div>
            <div class="metric-value">
                <span class="value" data-counter="{value}">{value}</span>
                {trend_html}
            </div>
        </div>
        <div class="metric-title">{title}</div>
    </div>
    '''
    return mark_safe(html)


# Add basic widget_tweaks functionality if not available
try:
    from widget_tweaks.templatetags.widget_tweaks import *
except ImportError:

    @register.filter
    def add_class(field, css_class):
        """Add CSS class to form field."""
        return field.as_widget(attrs={"class": css_class})

    @register.filter
    def add_error_class(field, css_class):
        """Add error CSS class to form field if field has errors."""
        if hasattr(field, "errors") and field.errors:
            return field.as_widget(attrs={"class": css_class})
        return field


# Additional admin-specific template tags
@register.filter
def get_item(dictionary, key):
    """Get item from dictionary in template."""
    return dictionary.get(key)


@register.filter
def multiply(value, factor):
    """Multiply two values."""
    try:
        return float(value) * float(factor)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def url_replace(request, field, value):
    """Replace URL parameter while keeping others."""
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
