"""
AURA Portfolio - Global Template Components
Advanced User Repository & Archive - Reusable UI components and complex template tags
Version: 1.0.2 - Fine-Tuned Alert Boxes & Progress Bars, add section header handling
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
    value,
    total,
    css_class="",
    show_text=True,
    color="teal",
    height="8px",
    label="",
    size="md",
):
    """
    Generate enhanced AURA-style progress bar HTML.
    Usage: {% progress_bar 75 100 css_class="system-progress" show_text=True color="teal" label="Development Progress" %}
    """
    try:
        percentage = min(100, max(0, (float(value) / float(total)) * 100))

        # Size classes
        size_classes = {"sm": "progress-sm", "md": "", "lg": "progress-lg"}
        size_class = size_classes.get(size, "")

        # Color classes
        color_class = f"progress-{color}"

        # Label HTML
        label_html = f'<div class="progress-label">{label}</div>' if label else ""

        # Text HTML with charcoal styling
        text_html = (
            f'<div class="progress-text">{percentage:.1f}%</div>' if show_text else ""
        )

        html = f'''
        <div class="aura-progress-container {size_class} {css_class}">
            {label_html}
            <div class="aura-progress-wrapper">
                <div class="aura-progress-track"></div>
                <div class="aura-progress-bar {color_class}" 
                     style="width: {percentage}%;" 
                     data-percentage="{percentage}"
                     data-color="{color}">
                    <div class="progress-glow"></div>
                </div>
            </div>
            {text_html}
        </div>
        '''
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe(f"""
        <div class="aura-progress-container {css_class}">
            <div class="aura-progress-wrapper">
                <div class="aura-progress-track"></div>
                <div class="aura-progress-bar progress-{color}" style="width: 0%;">
                    <div class="progress-glow"></div>
                </div>
            </div>
            {f'<div class="progress-text">0%</div>' if show_text else ""}
        </div>
        """)


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
def progress_bar_with_icon(
    value, total, icon="fas fa-tasks", label="Progress", color="teal", show_text=True
):
    """
    Generate progress bar with icon and label.
    Usage: {% progress_bar_with_icon 75 100 icon="fas fa-code" label="Development" color="teal" %}
    """
    try:
        percentage = min(100, max(0, (float(value) / float(total)) * 100))
        color_class = f"progress-{color}"

        html = f'''
        <div class="progress-with-icon">
            <div class="progress-icon">
                <i class="{icon}"></i>
            </div>
            <div class="progress-content">
                <div class="progress-label">{label}</div>
                <div class="aura-progress-container">
                    <div class="aura-progress-wrapper">
                        <div class="aura-progress-track"></div>
                        <div class="aura-progress-bar {color_class}" 
                             style="width: {percentage}%;" 
                             data-percentage="{percentage}">
                            <div class="progress-glow"></div>
                        </div>
                    </div>
                    {f'<div class="progress-text">{percentage:.1f}%</div>' if show_text else ""}
                </div>
            </div>
        </div>
        '''
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe('<div class="progress-with-icon">Error loading progress</div>')


@register.simple_tag
def indeterminate_progress(color="teal", label="Loading..."):
    """
    Generate indeterminate/loading progress bar.
    Usage: {% indeterminate_progress color="teal" label="Processing data..." %}
    """
    color_class = f"progress-{color}"

    html = f"""
    <div class="aura-progress-container">
        {f'<div class="progress-label">{label}</div>' if label else ""}
        <div class="aura-progress-wrapper">
            <div class="aura-progress-track"></div>
            <div class="aura-progress-bar {color_class} indeterminate">
                <div class="progress-glow"></div>
            </div>
        </div>
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def progress_steps(current_step, total_steps, step_labels=""):
    """
    Generate step progress indicator.
    Usage: {% progress_steps 2 4 step_labels="Setup,Config,Deploy,Complete" %}
    """
    try:
        current = int(current_step)
        total = int(total_steps)
        labels = step_labels.split(",") if step_labels else []

        steps_html = ""
        for i in range(1, total + 1):
            if i < current:
                step_class = "completed"
            elif i == current:
                step_class = "active"
            else:
                step_class = ""

            label = labels[i - 1] if i <= len(labels) else f"Step {i}"

            steps_html += f"""
            <div class="progress-step-item">
                <div class="progress-step {step_class}"></div>
                <div class="step-label">{label}</div>
            </div>
            """

        html = f"""
        <div class="progress-steps-container">
            <div class="progress-steps">
                {steps_html}
            </div>
        </div>
        """
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe('<div class="progress-steps-error">Invalid step data</div>')


@register.simple_tag
def system_progress_card(title, systems_data):
    """
    Generate a card showing multiple system progress bars.
    Usage: {% system_progress_card "Development Status" systems_list %}
    """
    html = f"""
    <div class="system-progress-card glass-card">
        <div class="card-header">
            <h3 class="card-title">{title}</h3>
        </div>
        <div class="card-content">
    """

    try:
        for system in systems_data:
            name = system.get("name", "Unknown System")
            progress = system.get("progress", 0)
            status = system.get("status", "in_development")

            color_map = {
                "deployed": "mint",
                "testing": "coral",
                "in_development": "teal",
                "published": "lavender",
            }
            color = color_map.get(status, "teal")

            html += f"""
            <div class="system-progress-item">
                <div class="system-info">
                    <span class="system-name">{name}</span>
                    <span class="system-status">{status.replace("_", " ").title()}</span>
                </div>
                <div class="aura-progress-container progress-sm">
                    <div class="aura-progress-wrapper">
                        <div class="aura-progress-track"></div>
                        <div class="aura-progress-bar progress-{color}" style="width: {progress}%;">
                            <div class="progress-glow"></div>
                        </div>
                    </div>
                    <div class="progress-text">{progress}%</div>
                </div>
            </div>
            """
    except (TypeError, AttributeError):
        html += '<div class="error">Unable to load system data</div>'

    html += """
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


# @register.inclusion_tag("components/glass_card.html")
# def glass_card(title="", content="", footer="", css_class="", with_header=True):
#     """
#     Render a glass-morphism card component.
#     Usage: {% glass_card title="System Status" content="..." css_class="dashboard-card" %}
#     """
#     return {
#         "title": title,
#         "content": content,
#         "footer": footer,
#         "css_class": css_class,
#         "with_header": with_header,
#     }

# Better Glass Card Handling
@register.simple_block_tag(takes_context=True)
def glass_card(
    context,
    content,  # This is the block content between {% glass_card %} and {% endglass_card %}
    title="",
    subtitle="",
    icon="",
    css_class="",
    with_header=True,
    header_style="default",
    footer="",
    with_footer=False,
    size="md",
    variant="default",
    with_border=True,
    with_glow=False,
    collapsible=False,
    expanded=True,
    card_id="",
    data_attributes="",
    show_metrics=False,
    metric_1_value="",
    metric_1_label="",
    metric_1_icon="fas fa-chart-line",
    metric_2_value="",
    metric_2_label="",
    metric_2_icon="fas fa-check-circle",
    metric_3_value="",
    metric_3_label="",
    metric_3_icon="fas fa-clock",
    metric_4_value="",
    metric_4_label="",
    metric_4_icon="fas fa-star",
):
    """
    BLOCK TAG version of glass card - supports {% glass_card %}...{% endglass_card %} syntax.
    """

    # Generate unique ID if not provided
    if not card_id:
        import uuid

        generated_id = f"glass-card-{uuid.uuid4().hex[:8]}"
    else:
        generated_id = card_id

    # Build CSS classes
    css_classes = ["glass-card"]

    # Size classes
    size_classes = {
        "xs": "glass-card-xs",
        "sm": "glass-card-sm",
        "md": "glass-card-md",
        "lg": "glass-card-lg",
        "xl": "glass-card-xl",
    }
    if size in size_classes:
        css_classes.append(size_classes[size])

    # Variant classes
    variant_classes = {
        "default": "",
        "featured": "glass-card-featured",
        "warning": "glass-card-warning",
        "success": "glass-card-success",
        "error": "glass-card-error",
        "info": "glass-card-info",
    }
    if variant in variant_classes and variant_classes[variant]:
        css_classes.append(variant_classes[variant])

    # Header style classes
    header_classes = {
        "default": "card-header",
        "compact": "card-header card-header-compact",
        "minimal": "card-header card-header-minimal",
    }
    header_class = header_classes.get(header_style, "card-header")

    # Additional classes
    if with_border:
        css_classes.append("glass-card-bordered")
    if with_glow:
        css_classes.append("glass-card-glow")
    if collapsible:
        css_classes.append("glass-card-collapsible")
        if not expanded:
            css_classes.append("glass-card-collapsed")
    if css_class:
        css_classes.append(css_class)

    # Parse data attributes
    data_attrs = ""
    if data_attributes:
        # Convert string like "key1:value1,key2:value2" to data attributes
        try:
            pairs = data_attributes.split(",")
            for pair in pairs:
                key, value = pair.split(":")
                data_attrs += f' data-{key.strip()}="{value.strip()}"'
        except:
            pass

    # Build the card HTML
    card_html = f'<div class="{" ".join(css_classes)}" id="{generated_id}"{data_attrs}>'

    # Header
    if with_header and (title or subtitle or icon):
        card_html += f'<header class="glass-card-header">'

        # Main header content (similar to section_header)
        card_html += '<div class="card-header-main">'
        card_html += '<div class="card-header-left">'

        # Simple icon (not holographic like section_header)
        if icon:
            card_html += (
                f'<div class="card-icon-simple"><i class="fas {icon}"></i></div>'
            )

        # Title and subtitle section
        if title or subtitle:
            card_html += '<div class="card-text-section">'
            if title:
                # Style title like section_header
                card_html += f'<h3 class="card-main-title">{title}</h3>'
            if subtitle:
                # Smaller subtitle
                card_html += f'<p class="card-subtitle-text">{subtitle}</p>'
            card_html += "</div>"

        # End card-header-left
        card_html += "</div>"

        # Right side (collapse button if needed)
        card_html += '<div class="card-header-right">'
        if collapsible:
            card_html += f'<button class="card-collapse-btn" data-target="#{generated_id}"><i class="fas fa-chevron-down"></i></button>'
        card_html += "</div>"

        card_html += "</div>"  # End card-header-main

        # Metrics grid (like section_header)
        if show_metrics and any(
            [metric_1_value, metric_2_value, metric_3_value, metric_4_value]
        ):
            card_html += '<div class="card-metrics-bar">'
            card_html += '<div class="card-metrics-grid">'

            # Add metrics that have values
            for i, (value, label, icon_class) in enumerate(
                [
                    (metric_1_value, metric_1_label, metric_1_icon),
                    (metric_2_value, metric_2_label, metric_2_icon),
                    (metric_3_value, metric_3_label, metric_3_icon),
                    (metric_4_value, metric_4_label, metric_4_icon),
                ]
            ):
                if value:
                    card_html += f'''
                    <div class="card-metric-item">
                        <div class="metric-icon">
                            <i class="{icon_class}"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">{value}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                    </div>
                    '''

            card_html += "</div>"  # End card-metrics-grid
            card_html += "</div>"  # End card-metrics-bar

        card_html += "</header>"

    # Content
    content_class = "card-content"
    if collapsible:
        content_class += " card-collapsible-content"
        if not expanded:
            content_class += " card-content-collapsed"

    card_html += f'<div class="{content_class}">{content}</div>'

    # Footer
    if with_footer and footer:
        card_html += f'<div class="card-footer">{footer}</div>'

    card_html += "</div>"

    # ✅ FIXED: Return the HTML directly, not a function!
    return mark_safe(card_html)


@register.inclusion_tag("components/glass_card.html", takes_context=True)
def glass_card_include(
    context,
    title="",
    subtitle="",
    content="",
    footer="",
    css_class="",
    with_header=True,
    header_style="default",
    with_footer=False,
    size="md",
    variant="default",
    icon="",
    with_border=True,
    with_glow=False,
    collapsible=False,
    expanded=True,
    card_id="",
    show_metrics=False,
    metric_1_value="",
    metric_1_label="",
    metric_1_icon="fas fa-chart-line",
    metric_2_value="",
    metric_2_label="",
    metric_2_icon="fas fa-check-circle",
    metric_3_value="",
    metric_3_label="",
    metric_3_icon="fas fa-clock",
    metric_4_value="",
    metric_4_label="",
    metric_4_icon="fas fa-star",
):
    """
    INCLUSION TAG version of glass card - for simple content passing.

    Usage Examples:
    {% glass_card_include title="Simple Card" content="<p>Hello World</p>" %}
    {% glass_card_include title="Status" content=status_html icon="fas fa-check" variant="success" %}

    This version uses a template file for rendering.
    Use the block tag version (glass_card) for complex content.
    """
    # Generate unique ID if not provided
    if not card_id:
        import uuid

        card_id = f"glass-card-{uuid.uuid4().hex[:8]}"

    return {
        "title": title,
        "subtitle": subtitle,
        "content": content,
        "footer": footer,
        "css_class": css_class,
        "with_header": with_header,
        "header_style": header_style,
        "with_footer": with_footer,
        "size": size,
        "variant": variant,
        "icon": icon,
        "with_border": with_border,
        "with_glow": with_glow,
        "collapsible": collapsible,
        "expanded": expanded,
        "card_id": card_id,
        "show_metrics": show_metrics,
        "metric_1_value": metric_1_value,
        "metric_1_label": metric_1_label,
        "metric_1_icon": metric_1_icon,
        "metric_2_value": metric_2_value,
        "metric_2_label": metric_2_label,
        "metric_2_icon": metric_2_icon,
        "metric_3_value": metric_3_value,
        "metric_3_label": metric_3_label,
        "metric_3_icon": metric_3_icon,
        "metric_4_value": metric_4_value,
        "metric_4_label": metric_4_label,
        "metric_4_icon": metric_4_icon,
        "request": context.get("request"),
    }


# Additional helper tags for glass cards


@register.simple_tag
def glass_card_opener(
    title="",
    subtitle="",
    icon="",
    css_class="",
    with_header=True,
    header_style="default",
    size="md",
    variant="default",
    with_border=True,
    with_glow=False,
    collapsible=False,
    expanded=True,
    card_id="",
    data_attributes="",
):
    """
    Generate just the opening tag for a glass card (for manual control).
    Usage: {% glass_card_opener title="My Card" %}...your content...{% glass_card_closer %}
    """
    # Generate unique ID if not provided
    if not card_id:
        import uuid

        card_id = f"glass-card-{uuid.uuid4().hex[:8]}"

    # Build CSS classes (same logic as block tag)
    css_classes = ["glass-card"]

    size_classes = {
        "xs": "glass-card-xs",
        "sm": "glass-card-sm",
        "md": "glass-card-md",
        "lg": "glass-card-lg",
        "xl": "glass-card-xl",
    }
    if size in size_classes:
        css_classes.append(size_classes[size])

    variant_classes = {
        "featured": "glass-card-featured",
        "warning": "glass-card-warning",
        "success": "glass-card-success",
        "error": "glass-card-error",
        "info": "glass-card-info",
    }
    if variant in variant_classes:
        css_classes.append(variant_classes[variant])

    if with_border:
        css_classes.append("glass-card-bordered")
    if with_glow:
        css_classes.append("glass-card-glow")
    if collapsible:
        css_classes.append("glass-card-collapsible")
        if not expanded:
            css_classes.append("glass-card-collapsed")
    if css_class:
        css_classes.append(css_class)

    # Parse data attributes
    data_attrs = ""
    if data_attributes:
        try:
            pairs = data_attributes.split(",")
            for pair in pairs:
                key, value = pair.split(":")
                data_attrs += f' data-{key.strip()}="{value.strip()}"'
        except:
            pass

    # Build header
    header_html = ""
    if with_header and (title or subtitle or icon):
        header_classes = {
            "default": "card-header",
            "compact": "card-header card-header-compact",
            "minimal": "card-header card-header-minimal",
        }
        header_class = header_classes.get(header_style, "card-header")

        header_html = f'<div class="{header_class}"><div class="card-header-content">'
        if icon:
            header_html += f'<div class="card-icon"><i class="{icon}"></i></div>'
        if title or subtitle:
            header_html += '<div class="card-text">'
            if title:
                title_tag = "h4" if header_style == "compact" else "h3"
                header_html += f'<{title_tag} class="card-title">{title}</{title_tag}>'
            if subtitle:
                header_html += f'<p class="card-subtitle">{subtitle}</p>'
            header_html += "</div>"
        if collapsible:
            header_html += f'<button class="card-collapse-btn" data-target="#{card_id}"><i class="fas fa-chevron-down"></i></button>'
        header_html += "</div></div>"

    # Content div opener
    content_class = "card-content"
    if collapsible:
        content_class += " card-collapsible-content"
        if not expanded:
            content_class += " card-content-collapsed"

    html = f'<div class="{" ".join(css_classes)}" id="{card_id}"{data_attrs}>{header_html}<div class="{content_class}">'

    return mark_safe(html)


@register.simple_tag
def glass_card_closer(footer="", with_footer=False):
    """
    Generate the closing tags for a glass card.
    Usage: {% glass_card_opener %}...content...{% glass_card_closer %}
    """
    html = "</div>"  # Close content div

    if with_footer and footer:
        html += f'<div class="card-footer">{footer}</div>'

    html += "</div>"  # Close card div

    return mark_safe(html)


@register.simple_tag
def glass_card_variants():
    """
    Return available glass card variants for dynamic usage.
    Usage: {% glass_card_variants as variants %}
    """
    return {
        "sizes": ["xs", "sm", "md", "lg", "xl"],
        "variants": ["default", "featured", "warning", "success", "error", "info"],
        "header_styles": ["default", "compact", "minimal"],
    }


@register.inclusion_tag("components/section_header.html")
def section_header(
    title="",
    subtitle="",
    icon="",
    show_metrics=False,
    metric_1_value="",
    metric_1_label="",
    metric_1_icon="fas fa-chart-line",
    metric_2_value="",
    metric_2_label="",
    metric_2_icon="fas fa-check-circle",
    metric_3_value="",
    metric_3_label="",
    metric_3_icon="fas fa-clock",
    metric_4_value="",
    metric_4_label="",
    metric_4_icon="fas fa-star",
    status="",
    status_text="",
    action_url="",
    action_text="",
    action_icon="",
    animated=True,
    title_prefix=True,
):
    """
    Render AURA section header with metrics and status.
    Usage: {% section_header title="Systems Overview" subtitle="Active Projects" icon="fas fa-project-diagram" show_metrics=True %}
    """
    return {
        "title": title,
        "subtitle": subtitle,
        "icon": icon,
        "show_metrics": show_metrics,
        "metric_1_value": metric_1_value,
        "metric_1_label": metric_1_label,
        "metric_1_icon": metric_1_icon,
        "metric_2_value": metric_2_value,
        "metric_2_label": metric_2_label,
        "metric_2_icon": metric_2_icon,
        "metric_3_value": metric_3_value,
        "metric_3_label": metric_3_label,
        "metric_3_icon": metric_3_icon,
        "metric_4_value": metric_4_value,
        "metric_4_label": metric_4_label,
        "metric_4_icon": metric_4_icon,
        "status": status,
        "status_text": status_text,
        "action_url": action_url,
        "action_text": action_text,
        "action_icon": action_icon,
        "animated": animated,
        "title_prefix": title_prefix,
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
    Usage: {% chart_container "systems-chart" "bar" height="400px"
    data_url="/api/systems/metrics/" %}
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
        """
    <button class="alert-dismiss" onclick="this.parentElement.style.display='none'">
        <i class="fas fa-times"></i>
    </button>
    """
        if dismissible
        else ""
    )

    html = f'''
    <div class="aura-alert alert-{alert_type} {"alert-dismissible" if dismissible else ""}">
        <div class="alert-main">
            <div class="alert-icon-wrapper">
                <i class="{alert_icon} alert-icon"></i>
            </div>
            <div class="alert-content">
                <span class="alert-text">{message}</span>
            </div>
            {f'<div class="alert-actions">{dismiss_html}</div>' if dismissible else ""}
        </div>
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
