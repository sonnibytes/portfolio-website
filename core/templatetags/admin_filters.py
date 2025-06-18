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
def admin_card(title, value, icon, color="primary", trend=None):
    """Generate admin dashboard card HTML."""
    if value is None:
        value = 0

    trend_html = ""
    if trend:
        trend_icon = (
            "fa-arrow-up text-success" if trend > 0 else "fa-arrow-down text-danger"
        )
        trend_html = f'<small class="text-muted ms-2"><i class="fas {trend_icon}"></i> {abs(trend)}%</small>'

    html = f'''
    <div class="admin-metric-card glass-card">
        <div class="metric-header">
            <div class="metric-icon" style="color: var(--{color});">
                <i class="{icon}"></i>
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
