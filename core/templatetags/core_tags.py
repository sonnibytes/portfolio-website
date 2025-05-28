# core/templatetags/core_tags.py
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

# Covered in aura_filters math_filters
# @register.filter
# def multiply(value, arg):
#     """Multiply the value by the argument."""
#     try:
#         return float(value) * float(arg)
#     except (ValueError, TypeError):
#         return value

# ## OUTDATED STYLES
# @register.simple_tag
# def tech_frame(css_class=""):
#     """Render a tech frame with angled corners."""
#     html = f"""
#     <div class="tech-frame {css_class}">
#         <div class="tech-frame-inner">
#             {{ content }}
#         </div>
#     </div>
#     """
#     return mark_safe(html)

# ## OUTDATED STYLES
# @register.simple_tag
# def hud_corner_accents():
#     """Render the HUD corner accents for containers."""
#     html = """
#     <div class="hud-corner hud-corner-tl"></div>
#     <div class="hud-corner hud-corner-tr"></div>
#     <div class="hud-corner hud-corner-bl"></div>
#     <div class="hud-corner hud-corner-br"></div>
#     """
#     return mark_safe(html)


@register.simple_tag
def data_grid(rows=10, cols=10, random=True, animate=True):
    """Render a data grid visualization."""
    html = f'''
    <div class="data-grid" data-random="{str(random).lower()}"
    data-animate="{str(animate).lower()}"
         style="grid-template-columns: repeat({cols}, 1fr);
         grid-template-rows: repeat({rows}, 1fr);">
    '''

    for i in range(rows * cols):
        html += '<div class="data-cell"></div>'

    html += "</div>"
    return mark_safe(html)


@register.simple_tag
def terminal_box(title="terminal", content=""):
    """Render a terminal-style box with the provided content."""
    html = f"""
    <div class="terminal-box">
        <div class="terminal-header">
            <div class="terminal-button red"></div>
            <div class="terminal-button yellow"></div>
            <div class="terminal-button green"></div>
            <span class="terminal-title">{title}</span>
        </div>
        <div class="terminal-content">
            {content}
        </div>
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def terminal_line(command, output=""):
    """Render a terminal command and its output."""
    html = f"""
    <p class="terminal-line">$ {command}</p>
    """
    if output:
        html += f'<p class="terminal-output">{output}</p>'

    return mark_safe(html)


@register.simple_tag
def radar_chart(values, labels, max_value=100):
    """Render a radar chart with the provided values and labels."""
    values_str = ",".join(str(v) for v in values)
    labels_str = ",".join(labels)

    html = f'''
    <div class="radar-chart" data-values="{values_str}"
    data-labels="{labels_str}" data-max="{max_value}"></div>
    '''
    return mark_safe(html)


@register.simple_tag
def progress_bar(value, max_value=100, label="", color=""):
    """Render a progress bar with the provided value."""
    percent = (float(value) / float(max_value)) * 100

    style = ""
    if color:
        style = f' style="background: {color}"'

    html = f'''
    <div class="progress-container">
        <div class="progress-label">{label}</div>
        <div class="progress-indicator">
            <div class="progress-bar"{style} style="width: {percent}%"></div>
        </div>
        <div class="progress-value">{value}/{max_value}</div>
    </div>
    '''
    return mark_safe(html)


@register.simple_tag
def tech_badge(name, color=""):
    """Render a technology badge with the provided name and optional color."""
    style = ""
    if color:
        style = f' style="border-color: {color}; color: {color}"'

    html = f'''
    <span class="tech-tag"{style}>{name}</span>
    '''
    return mark_safe(html)


@register.filter
def format_date_range(start_date, end_date=None):
    """Format a date range for display."""
    if not start_date:
        return ""

    start_str = start_date.strftime("%b %Y")

    if not end_date:
        return f"{start_str} - Present"

    end_str = end_date.strftime("%b %Y")
    return f"{start_str} - {end_str}"


@register.simple_tag
def skill_bar(name, level, max_level=5, color=""):
    """Render a skill bar with the provided name and level."""
    percent = (float(level) / float(max_level)) * 100

    gradient = "var(--gradient-primary)"
    if color:
        gradient = f"linear-gradient(90deg, {color}, {color})"

    html = f"""
    <div class="skill-item">
        <div class="skill-info">
            <div class="skill-name">{name}</div>
            <div class="skill-level">Level {level}/{max_level}</div>
        </div>
        <div class="skill-progress">
            <div class="skill-progress-bar" style="width: {percent}%;
            background: {gradient}"></div>
        </div>
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def hexagon_badge(text, color="var(--color-cyan)", size="medium", icon=""):
    """Render a hexagonal badge with text or icon."""
    sizes = {"small": "40px", "medium": "60px", "large": "80px"}

    size_px = sizes.get(size, sizes["medium"])

    content = text
    if icon:
        content = f'<i class="fas {icon}"></i>'

    html = f"""
    <div class="category-hex" style="--category-color: {color};
    width: {size_px}; height: {size_px}">
        {content}
    </div>
    """
    return mark_safe(html)


@register.filter
def summarize(text, length=150):
    """Truncate text to the specified length and add ellipsis."""
    if not text:
        return ""

    if len(text) <= length:
        return text

    # Try to find a space to break at
    truncated = text[:length]
    last_space = truncated.rfind(" ")

    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + "..."


@register.filter
def format_code(code, language="python"):
    """Format code with syntax highlighting."""
    if not code:
        return ""

    # Escape HTML
    import html

    escaped_code = html.escape(code)

    html_content = f"""
    <div class="code-block">
        <div class="code-header">
            <div class="terminal-button red"></div>
            <div class="terminal-button yellow"></div>
            <div class="terminal-button green"></div>
            <span class="filename">code.{language}</span>
        </div>
        <div class="code-content">
            <pre><code class="language-{language}">{escaped_code}</code></pre>
        </div>
    </div>
    """
    return mark_safe(html_content)


@register.inclusion_tag("core/includes/social_icons.html")
def social_icons(links=None, class_name=""):
    """Render social media icons."""
    from core.models import SocialLink

    if links is None:
        links = SocialLink.objects.all().order_by("display_order")

    return {"social_links": links, "class_name": class_name}


@register.inclusion_tag("core/includes/data_visualization.html")
def data_visualization(type="radar", data=None, options=None):
    """Render various data visualizations."""
    if data is None:
        data = {}

    if options is None:
        options = {}

    return {"type": type, "data": data, "options": options}


@register.inclusion_tag("core/includes/section_header.html")
def section_header(title, subtitle="", alignment="center"):
    """Render a formatted section header."""
    return {"title": title, "subtitle": subtitle, "alignment": alignment}


@register.simple_tag
def timeline_item(date, title, subtitle="", content="", direction="left"):
    """Render a timeline item for experience or education."""
    html = f"""
    <div class="timeline-item {direction}">
        <div class="timeline-content tech-frame">
            <div class="timeline-header">
                <h3 class="timeline-title">{title}</h3>
                {f'<div class="timeline-subtitle">{subtitle}</div>' if subtitle else ""}
            </div>
            
            <div class="timeline-date">
                <span class="date-label">{date}</span>
            </div>
            
            {f'<div class="timeline-body">{content}</div>' if content else ""}
        </div>
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def card(title, content="", image="", link="", link_text="", css_class=""):
    """Render a styled card with optional image and link."""
    image_html = ""
    if image:
        image_html = f'''
        <div class="card-image">
            <img src="{image}" alt="{title}" class="img-fluid">
        </div>
        '''

    link_html = ""
    if link and link_text:
        link_html = f'''
        <a href="{link}" class="card-link">{link_text}
        <i class="fas fa-arrow-right"></i></a>
        '''

    html = f"""
    <div class="card tech-frame {css_class}">
        {image_html}
        <div class="card-body">
            <h3 class="card-title">{title}</h3>
            <div class="card-content">{content}</div>
            {link_html}
        </div>
    </div>
    """
    return mark_safe(html)


@register.simple_tag
def contact_info_item(icon, title, content):
    """Render a contact information item with icon."""
    html = f"""
    <div class="info-item">
        <div class="info-icon">
            <i class="fas {icon}"></i>
        </div>
        <div class="info-content">
            <h3 class="info-label">{title}</h3>
            <p class="info-value">{content}</p>
        </div>
    </div>
    """
    return mark_safe(html)


@register.filter
def get_experience_duration(start_date, end_date=None):
    """Calculate and format duration between two dates in years and months."""
    import datetime

    if not end_date:
        end_date = datetime.date.today()

    # Calculate difference in months
    months = (end_date.year - start_date.year) * 12 + (
        end_date.month - start_date.month
    )

    years = months // 12
    remaining_months = months % 12

    if years > 0 and remaining_months > 0:
        return f"{years} year{'s' if years != 1 else ''}, \
        {remaining_months} month{'s' if remaining_months != 1 else ''}"
    elif years > 0:
        return f"{years} year{'s' if years != 1 else ''}"
    else:
        return f"{remaining_months} \
        month{'s' if remaining_months != 1 else ''}"


@register.filter
def highlight_term(text, term):
    """Highlight a search term in text."""
    if not term or not text:
        return text

    pattern = re.compile(f"({re.escape(term)})", re.IGNORECASE)
    highlighted = pattern.sub(r"<mark>\1</mark>", text)

    return mark_safe(highlighted)


@register.filter
def format_technologies(technologies):
    """Format a comma-separated string of technologies into tech badges."""
    if not technologies:
        return ""

    tech_list = [tech.strip() for tech in technologies.split(",")]
    html = '<div class="tech-tags">'

    for tech in tech_list:
        html += f'<span class="tech-tag">{tech}</span>'

    html += "</div>"
    return mark_safe(html)


@register.simple_tag
def page_navigation(prev_url=None, prev_title=None, next_url=None, next_title=None):
    """Render page navigation links."""
    prev_html = ""
    if prev_url and prev_title:
        prev_html = f'''
        <a href="{prev_url}" class="page-nav-link">
            <span class="page-nav-label">← Previous</span>
            <span class="page-nav-title">{prev_title}</span>
        </a>
        '''
    else:
        prev_html = "<div></div>"

    next_html = ""
    if next_url and next_title:
        next_html = f'''
        <a href="{next_url}" class="page-nav-link text-end">
            <span class="page-nav-label">Next →</span>
            <span class="page-nav-title">{next_title}</span>
        </a>
        '''
    else:
        next_html = "<div></div>"

    html = f"""
    <div class="page-navigation">
        {prev_html}
        {next_html}
    </div>
    """
    return mark_safe(html)


@register.inclusion_tag("core/includes/breadcrumbs.html")
def breadcrumbs(items):
    """Render breadcrumb navigation with the provided items."""
    return {"items": items}


@register.inclusion_tag("core/includes/cta_box.html")
def cta_box(title, content="", button_text="", button_url=""):
    """Render a call-to-action box."""
    return {
        "title": title,
        "content": content,
        "button_text": button_text,
        "button_url": button_url,
    }


@register.filter
def as_range(value):
    """Convert a number to a range for iteration."""
    return range(value)


@register.filter
def get_dict_item(dictionary, key):
    """Get an item from a dictionary."""
    return dictionary.get(key)
