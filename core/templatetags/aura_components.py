"""
AURA Portfolio - Global Template Components
Advanced User Repository & Archive - Reusable UI components and complex template tags
Version: 1.0.0
"""

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
import json
import random

register = template.Library()

# ========== PROGRESS BARS AND INDICATORS ==========


@register.simple_tag
def progress_bar(
    value, total, css_class="", show_text=True, color="teal", height="6px"
):
    """
    Generate AURA-style progress bar HTML.
    Usage: {% progress_bar 75 100 css_class="system-progress"
    show_text=True color="teal" %}
    """
    try:
        percentage = min(100, max(0, (float(value) / float(total)) * 100))

        color_vars = {
            "teal": "var(--color-teal)",
            "lavender": "var(--color-lavender)",
            "coral": "var(--color-coral)",
            "mint": "var(--color-mint)",
            "yellow": "var(--color-yellow)",
        }

        bar_color = color_vars.get(color, "var(--color-teal)")

        html = f'''
        <div class="aura-progress-container {css_class}" style="height: {height};">
            <div class="aura-progress-track"></div>
            <div class="aura-progress-bar" 
                 style="width: {percentage}%; background: {bar_color};" 
                 data-percentage="{percentage}">
                <div class="progress-glow"></div>
            </div>
            {f'<span class="progress-text">{percentage:.1f}%</span>'
             if show_text else ""}
        </div>
        '''
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe(
            f'<div class="aura-progress-container {css_class}"> \
            <div class="aura-progress-bar" style="width: 0%;"></div></div>'
        )


@register.simple_tag
def circular_progress(value,
                      total, size="80px", thickness="6px", color="teal"):

    """
    Generate circular progress indicator.
    Usage: {% circular_progress 75 100 size="100px"
    thickness="8px" color="teal" %}
    """
    try:
        percentage = min(100, max(0, (float(value) / float(total)) * 100))
        radius = 40  # SVG coordinate system
        circumference = 2 * 3.14159 * radius
        stroke_offset = circumference - (percentage / 100 * circumference)

        color_vars = {
            "teal": "#26c6da",
            "lavender": "#b39ddb",
            "coral": "#ff8a80",
            "mint": "#a5d6a7",
            "yellow": "#fff59d",
        }

        stroke_color = color_vars.get(color, "#26c6da")

        html = f'''
        <div class="circular-progress" style="width: {size}; height: {size};">
            <svg viewBox="0 0 100 100" class="circular-progress-svg">
                <circle cx="50" cy="50" r="{radius}" 
                        fill="none" 
                        stroke="rgba(255,255,255,0.1)" 
                        stroke-width="{thickness}"/>
                <circle cx="50" cy="50" r="{radius}" 
                        fill="none" 
                        stroke="{stroke_color}" 
                        stroke-width="{thickness}"
                        stroke-linecap="round"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{stroke_offset}"
                        transform="rotate(-90 50 50)"
                        class="progress-circle"/>
            </svg>
            <div class="circular-progress-text">
                <span class="progress-value">{percentage:.0f}</span>
                <span class="progress-unit">%</span>
            </div>
        </div>
        '''
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe(
            f'<div class="circular-progress" style="width: {size}; height: {size};"><span>0%</span></div>'
        )


@register.simple_tag
def status_indicator(status, size="md", with_text=False, pulsing=True):
    """
    Generate AURA status indicator.
    Usage: {% status_indicator "operational" size="lg" with_text=True pulsing=True %}
    """
    sizes = {"sm": "6px", "md": "8px", "lg": "12px", "xl": "16px"}

    size_value = sizes.get(size, "8px")
    pulse_class = "status-pulse" if pulsing else ""

    html = f'''
    <div class="status-indicator-container">
        <div class="status-indicator {status} {pulse_class}" 
             style="width: {size_value}; height: {size_value};" 
             title="{status.replace("_", " ").title()}"></div>
        {f'<span class="status-text">{status.replace("_", " ").upper()}</span>' if with_text else ""}
    </div>
    '''
    return mark_safe(html)


# ========== BADGES AND TAGS ==========


@register.simple_tag
def tech_badge(name, icon="", color="", url="", size="sm"):
    """
    Generate technology badge.
    Usage: {% tech_badge "Python" icon="fab fa-python"
    color="#3776ab" url="/tech/python/" %}
    """
    sizes = {
        "xs": "tech-badge-xs",
        "sm": "tech-badge-sm",
        "md": "tech-badge-md",
        "lg": "tech-badge-lg",
    }

    size_class = sizes.get(size, "tech-badge-sm")
    style = f'style="--tech-color: {color};"' if color else ""

    badge_content = f"""
    <span class="tech-badge {size_class}" {style}>
        {f'<i class="{icon}"></i>' if icon else ""}
        <span class="tech-name">{name}</span>
    </span>
    """

    if url:
        return mark_safe(f'<a href="{url}" \
                         class="tech-badge-link">{badge_content}</a>')
    else:
        return mark_safe(badge_content)


@register.simple_tag
def priority_tag(priority, show_icon=True):
    """
    Generate priority tag.
    Usage: {% priority_tag 3 show_icon=True %}
    """
    priority_config = {
        1: {
            "label": "Low",
            "icon": "fas fa-arrow-down",
            "class": "priority-low"
            },
        2: {
            "label": "Normal",
            "icon": "fas fa-minus",
            "class": "priority-normal"
            },
        3: {
            "label": "High",
            "icon": "fas fa-arrow-up",
            "class": "priority-high"
            },
        4: {
            "label": "Critical",
            "icon": "fas fa-exclamation-triangle",
            "class": "priority-critical",
        },
    }

    config = priority_config.get(priority, priority_config[2])

    html = f"""
    <span class="priority-tag {config["class"]}">
        {f'<i class="{config["icon"]}"></i>' if show_icon else ""}
        <span>{config["label"]}</span>
    </span>
    """
    return mark_safe(html)


@register.simple_tag
def category_hexagon(code, color="", size="md"):
    """
    Generate hexagonal category badge.
    Usage: {% category_hexagon "ML" color="#b39ddb" size="lg" %}
    """
    sizes = {"sm": "24px", "md": "32px", "lg": "40px", "xl": "48px"}

    size_value = sizes.get(size, "32px")
    style = f'style="--hex-color: {color};"' if color else ""

    html = f"""
    <div class="category-hexagon" style="width: {size_value}; \
    height: {size_value};" {style}>
        <div class="hexagon-inner">
            <span class="hexagon-text">{code[:2].upper()}</span>
        </div>
    </div>
    """
    return mark_safe(html)


# ========== METRIC DISPLAYS ==========


@register.simple_tag
def metric_card(value, label, icon="", color="teal", trend="", size="md"):
    """
    Generate metric display card.
    Usage: {% metric_card "1,247" "Active Users" icon="fas fa-users"
    color="teal" trend="+12%" %}
    """
    colors = {
        "teal": "metric-teal",
        "lavender": "metric-lavender",
        "coral": "metric-coral",
        "mint": "metric-mint",
        "yellow": "metric-yellow",
    }

    sizes = {
        "sm": "metric-card-sm", "md": "metric-card-md", "lg": "metric-card-lg"}

    color_class = colors.get(color, "metric-teal")
    size_class = sizes.get(size, "metric-card-md")

    trend_html = ""
    if trend:
        trend_class = "trend-up" if trend.startswith("+") else "trend-down"
        trend_html = f'<span class="metric-trend {trend_class}">{trend}</span>'

    html = f"""
    <div class="metric-card {color_class} {size_class}">
        {f'<div class="metric-icon"><i class="{icon}"></i></div>' if icon else ""}
        <div class="metric-content">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {trend_html}
        </div>
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def system_metrics_grid(*metrics):
    """
    Generate grid of system metrics.
    Usage: {% system_metrics_grid metric1 metric2 metric3 metric4 %}
    """
    html = '<div class="system-metrics-grid">'
    for metric in metrics:
        html += str(metric)
    html += "</div>"
    return mark_safe(html)


# ========== NAVIGATION COMPONENTS ==========


@register.simple_tag(takes_context=True)
def breadcrumb_nav(context, *breadcrumbs):
    """
    Generate AURA breadcrumb navigation.
    Usage: {% breadcrumb_nav "Home:/home/" "Systems:/systems/" "Detail" %}
    """
    request = context.get("request")

    html = '<nav class="aura-breadcrumbs"><div class="breadcrumb-container">'

    for i, breadcrumb in enumerate(breadcrumbs):
        if ":" in breadcrumb:
            label, url = breadcrumb.split(":", 1)
            html += f'''
            <a href="{url}" class="breadcrumb-item">
                <span>{label}</span>
            </a>
            '''
        else:
            html += f"""
            <span class="breadcrumb-item active">
                <span>{breadcrumb}</span>
            </span>
            """

        if i < len(breadcrumbs) - 1:
            html += '<i class="fas fa-chevron-right breadcrumb-separator"></i>'

    html += "</div></nav>"
    return mark_safe(html)


@register.simple_tag(takes_context=True)
def nav_link(context, url_name, label, icon="", css_class=""):
    """
    Generate navigation link with active state.
    Usage: {% nav_link "projects:system_list" "Systems" icon="fas fa-project-diagram" %}
    """
    request = context.get("request")

    try:
        url = reverse(url_name)
        is_active = request.resolver_match.view_name == url_name if request else False
        active_class = "active" if is_active else ""

        html = f'''
        <a href="{url}" class="nav-link {active_class} {css_class}">
            {f'<i class="{icon}"></i>' if icon else ""}
            <span>{label}</span>
        </a>
        '''
        return mark_safe(html)
    except:
        return mark_safe(f'<span class="nav-link-error">{label}</span>')


# ========== CARD COMPONENTS ==========


@register.inclusion_tag("components/glass_card.html")
def glass_card(title="", content="", footer="", css_class="", with_header=True):
    """
    Render a glass-morphism card component.
    Usage: {% glass_card title="System Status" content="..." css_class="dashboard-card" %}
    """
    return {
        "title": title,
        "content": content,
        "footer": footer,
        "css_class": css_class,
        "with_header": with_header,
    }


@register.simple_tag
def system_card_skeleton():
    """
    Generate loading skeleton for system cards.
    Usage: {% system_card_skeleton %}
    """
    html = """
    <div class="system-card skeleton">
        <div class="skeleton-header">
            <div class="skeleton-id"></div>
            <div class="skeleton-status"></div>
        </div>
        <div class="skeleton-image"></div>
        <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
            <div class="skeleton-progress"></div>
            <div class="skeleton-tags">
                <div class="skeleton-tag"></div>
                <div class="skeleton-tag"></div>
                <div class="skeleton-tag"></div>
            </div>
        </div>
    </div>
    """
    return mark_safe(html)


# ========== DATA VISUALIZATION ==========


@register.simple_tag
def chart_container(chart_id, chart_type="line", height="300px", data_url=""):
    """
    Generate chart container for data visualization.
    Usage: {% chart_container "systems-chart" "bar" height="400px" data_url="/api/systems/metrics/" %}
    """
    html = f'''
    <div class="chart-container" style="height: {height};">
        <canvas id="{chart_id}" 
                data-chart-type="{chart_type}"
                {f'data-url="{data_url}"' if data_url else ""}
                class="aura-chart"></canvas>
        <div class="chart-loading">
            <div class="chart-spinner"></div>
            <span>Loading chart data...</span>
        </div>
    </div>
    '''
    return mark_safe(html)


@register.simple_tag
def sparkline(values, color="teal", height="40px"):
    """
    Generate SVG sparkline chart.
    Usage: {% sparkline "10,15,20,18,25,22,30" color="teal" height="40px" %}
    """
    try:
        if isinstance(values, str):
            value_list = [float(x.strip()) for x in values.split(",")]
        else:
            value_list = list(values)

        if not value_list:
            return mark_safe('<div class="sparkline-empty"></div>')

        max_val = max(value_list)
        min_val = min(value_list)
        range_val = max_val - min_val if max_val != min_val else 1

        width = len(value_list) * 8
        points = []

        for i, val in enumerate(value_list):
            x = i * 8
            y = 30 - ((val - min_val) / range_val) * 25  # Invert Y axis
            points.append(f"{x},{y}")

        color_vars = {
            "teal": "#26c6da",
            "lavender": "#b39ddb",
            "coral": "#ff8a80",
            "mint": "#a5d6a7",
            "yellow": "#fff59d",
        }

        stroke_color = color_vars.get(color, "#26c6da")

        html = f'''
        <div class="sparkline-container" style="height: {height};">
            <svg width="{width}" height="40" class="sparkline">
                <polyline points="{" ".join(points)}" 
                          fill="none" 
                          stroke="{stroke_color}" 
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"/>
            </svg>
        </div>
        '''
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe('<div class="sparkline-error">Invalid data</div>')


# ========== ALERT AND NOTIFICATION COMPONENTS ==========


@register.simple_tag
def alert_box(message, alert_type="info", dismissible=True, icon=""):
    """
    Generate AURA alert component.
    Usage: {% alert_box "System updated successfully" "success" dismissible=True icon="fas fa-check" %}
    """
    icons = {
        "success": "fas fa-check-circle",
        "error": "fas fa-exclamation-circle",
        "warning": "fas fa-exclamation-triangle",
        "info": "fas fa-info-circle",
    }

    alert_icon = icon or icons.get(alert_type, "fas fa-info-circle")
    dismiss_html = (
        '<button class="alert-dismiss"><i class="fas fa-times"></i></button>'
        if dismissible
        else ""
    )

    html = f'''
    <div class="aura-alert alert-{alert_type} {"alert-dismissible" if dismissible else ""}">
        <div class="alert-content">
            <i class="{alert_icon} alert-icon"></i>
            <span class="alert-text">{message}</span>
        </div>
        {dismiss_html}
    </div>
    '''
    return mark_safe(html)


@register.simple_tag
def notification_toast(message, toast_type="info", duration="4000"):
    """
    Generate notification toast for JavaScript.
    Usage: {% notification_toast "Data saved" "success" "5000" %}
    """
    toast_data = {
        "message": message, "type": toast_type, "duration": int(duration)}

    return mark_safe(f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        if (typeof showNotification === 'function') {{
            showNotification('{message}', '{toast_type}');
        }}
    }});
    </script>
    """)


# ========== FORM COMPONENTS ==========


@register.simple_tag
def form_field_wrapper(field, label="", help_text="", required=False, css_class=""):
    """
    Wrap form field with AURA styling.
    Usage: {% form_field_wrapper form.title label="System Title" required=True %}
    """
    field_html = str(field)
    required_html = '<span class="required-indicator">*</span>' if required else ""
    help_html = f'<div class="field-help">{help_text}</div>' if help_text else ""

    html = f"""
    <div class="form-field-wrapper {css_class}">
        {f'<label class="form-label">{label}{required_html}</label>' if label else ""}
        <div class="form-input-container">
            {field_html}
        </div>
        {help_html}
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def search_input(name="search", placeholder="Search...", value="", css_class=""):
    """
    Generate AURA search input.
    Usage: {% search_input name="q" placeholder="Search systems..." value=query %}
    """
    html = f'''
    <div class="search-input-container {css_class}">
        <div class="search-icon">
            <i class="fas fa-search"></i>
        </div>
        <input type="text" 
               name="{name}" 
               class="search-input" 
               placeholder="{placeholder}"
               value="{value}"
               autocomplete="off">
        <div class="search-clear" style="display: {"block" if value else "none"};">
            <i class="fas fa-times"></i>
        </div>
    </div>
    '''
    return mark_safe(html)


# ========== LOADING AND SKELETON COMPONENTS ==========


@register.simple_tag
def loading_spinner(size="md", color="teal", text=""):
    """
    Generate loading spinner.
    Usage: {% loading_spinner size="lg" color="teal" text="Loading systems..." %}
    """
    sizes = {"sm": "16px", "md": "24px", "lg": "32px", "xl": "48px"}

    size_value = sizes.get(size, "24px")

    html = f"""
    <div class="loading-spinner-container">
        <div class="loading-spinner" 
             style="width: {size_value}; height: {size_value};">
        </div>
        {f'<span class="loading-text">{text}</span>' if text else ""}
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def skeleton_text(lines=3, width="100%"):
    """
    Generate skeleton text placeholder.
    Usage: {% skeleton_text lines=2 width="80%" %}
    """
    html = f'<div class="skeleton-text-container" style="width: {width};">'
    for i in range(lines):
        line_width = "100%" if i < lines - 1 else f"{random.randint(60, 90)}%"
        html += f'<div class="skeleton-text-line" style="width: {line_width};"></div>'
    html += "</div>"
    return mark_safe(html)


# ========== UTILITY COMPONENTS ==========


@register.simple_tag
def copy_button(text, button_text="Copy", success_text="Copied!"):
    """
    Generate copy-to-clipboard button.
    Usage: {% copy_button "https://example.com" "Copy URL" "URL Copied!" %}
    """
    button_id = f"copy-btn-{random.randint(1000, 9999)}"

    html = f'''
    <button class="copy-button" 
            id="{button_id}"
            data-copy-text="{text}"
            data-original-text="{button_text}"
            data-success-text="{success_text}">
        <i class="fas fa-copy"></i>
        <span>{button_text}</span>
    </button>
    <script>
    document.getElementById('{button_id}').addEventListener('click', function() {{
        const text = this.dataset.copyText;
        const span = this.querySelector('span');
        const originalText = this.dataset.originalText;
        const successText = this.dataset.successText;

        navigator.clipboard.writeText(text).then(() => {{
            span.textContent = successText;
            this.classList.add('copied');
            setTimeout(() => {{
                span.textContent = originalText;
                this.classList.remove('copied');
            }}, 2000);
        }});
    }});
    </script>
    '''
    return mark_safe(html)


@register.simple_tag
def tooltip(content, text, position="top"):
    """
    Generate tooltip component.
    Usage: {% tooltip "This is helpful information" "Hover me" position="bottom" %}
    """
    tooltip_id = f"tooltip-{random.randint(1000, 9999)}"

    html = f'''
    <span class="tooltip-container" 
          id="{tooltip_id}"
          data-tooltip="{content}" 
          data-position="{position}">
        {text}
    </span>
    '''
    return mark_safe(html)


@register.simple_tag
def accordion_item(title, content, expanded=False, css_class=""):
    """
    Generate accordion item.
    Usage: {% accordion_item "System Details" content_html expanded=False %}
    """
    item_id = f"accordion-{random.randint(1000, 9999)}"
    expanded_class = "expanded" if expanded else ""

    html = f'''
    <div class="accordion-item {expanded_class} {css_class}">
        <div class="accordion-header" data-target="#{item_id}">
            <span class="accordion-title">{title}</span>
            <i class="accordion-icon fas fa-chevron-down"></i>
        </div>
        <div class="accordion-content" id="{item_id}" {'style="display: block;"' if expanded else ""}>
            <div class="accordion-body">
                {content}
            </div>
        </div>
    </div>
    '''
    return mark_safe(html)


# ========== JSON DATA COMPONENTS ==========


@register.simple_tag
def json_script_tag(data, element_id):
    """
    Generate JSON script tag for JavaScript consumption.
    Usage: {% json_script_tag chart_data "chart-data" %}
    """
    try:
        json_data = json.dumps(data, indent=2)
        return mark_safe(
            f'<script id="{element_id}" type="application/json">{json_data}</script>'
        )
    except (TypeError, ValueError):
        return mark_safe(
            f'<script id="{element_id}" type="application/json">null</script>'
        )


@register.simple_tag
def data_attributes(**kwargs):
    """
    Generate data attributes string.
    Usage: <div {% data_attributes chart_type="bar" url="/api/data/" %}>
    """
    attrs = []
    for key, value in kwargs.items():
        key = key.replace("_", "-")
        attrs.append(f'data-{key}="{value}"')
    return mark_safe(" ".join(attrs))


# ========== CONDITIONAL RENDERING ==========


@register.simple_tag(takes_context=True)
def render_if(context, condition, true_content, false_content=""):
    """
    Conditional rendering helper.
    Usage: {% render_if user.is_staff "Admin Content" "User Content" %}
    """
    return mark_safe(true_content if condition else false_content)


@register.simple_tag
def pluralize_smart(count, singular, plural=""):
    """
    Smart pluralization.
    Usage: {% pluralize_smart count "system" "systems" %}
    """
    if not plural:
        plural = singular + "s"

    return plural if count != 1 else singular


# ========== PERFORMANCE HELPERS ==========


@register.simple_tag
def preload_image(src, alt=""):
    """
    Generate image preload link.
    Usage: {% preload_image "/static/images/hero.jpg" "Hero Image" %}
    """
    return mark_safe(f'<link rel="preload" as="image" href="{src}" alt="{alt}">')


@register.simple_tag
def critical_css(css_content):
    """
    Inline critical CSS.
    Usage: {% critical_css "body { margin: 0; }" %}
    """
    return mark_safe(f"<style>{css_content}</style>")


# ========== DEBUG AND DEVELOPMENT ==========


@register.simple_tag(takes_context=True)
def debug_info(context, show_request=False, show_user=False):
    """
    Display debug information (only in DEBUG mode).
    Usage: {% debug_info show_request=True show_user=True %}
    """
    from django.conf import settings

    if not settings.DEBUG:
        return ""

    request = context.get("request")
    user = context.get("user")

    debug_data = {
        "timestamp": timezone.now().isoformat(),
        "view_name": getattr(request.resolver_match, "view_name", "Unknown")
        if request
        else "No request",
    }

    if show_request and request:
        debug_data["method"] = request.method
        debug_data["path"] = request.path
        debug_data["GET"] = dict(request.GET)

    if show_user and user:
        debug_data["user"] = {
            "username": getattr(user, "username", "Anonymous"),
            "is_authenticated": getattr(user, "is_authenticated", False),
            "is_staff": getattr(user, "is_staff", False),
        }

    html = f"""
    <div class="debug-info">
        <pre>{json.dumps(debug_data, indent=2)}</pre>
    </div>
    """
    return mark_safe(html)
