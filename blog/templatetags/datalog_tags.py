"""
AURA Portfolio - Blog Template Tags
Custom template tags and filters for the blog/datalogs system
Version 2.0.2: Separated Out Global TemplateTags to aura_filters, added enhanced filters
"""

from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.html import escape, format_html
from django.urls import reverse
from django.db.models import Count, Q, Avg, Sum
from django.db.models.functions import Extract
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from datetime import datetime, timedelta, date
import re
import json
from collections import Counter, defaultdict
from itertools import groupby
import calendar
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from markdownx.utils import markdownify as md
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from ..models import Post, Category, Tag
from core.templatetags.aura_filters import status_color, time_since_published, format_duration, format_number, truncate_smart, highlight_search

register = template.Library()


# ===================== TEMPLATE TAGS FOR VIEW CONTEXT =====================


@register.simple_tag(takes_context=True)
def current_url_with_params(context, **kwargs):
    """
    Get current URL with modified parameters.
    Usage: {% current_url_with_params sort='date' %}
    """
    request = context["request"]
    params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value

    if params:
        return f"{request.path}?{params.urlencode()}"
    return request.path


@register.simple_tag
def query_string(**kwargs):
    """
    Build a query string from keyword arguments.
    Usage: {% query_string q=query sort=sort_by %}
    """
    from urllib.parse import urlencode

    # Filter out None and empty values
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None and v != ""}

    if filtered_kwargs:
        return "?" + urlencode(filtered_kwargs)
    return ""


# ===================== DEBUG/DEVELOPMENT HELPERS =====================


@register.simple_tag
def debug_context(context_var):
    """
    Debug helper to inspect context variables during development.
    Usage: {% debug_context some_variable %}
    """
    import json

    try:
        if hasattr(context_var, "__dict__"):
            # For model instances
            return json.dumps(str(context_var.__dict__), indent=2)
        elif isinstance(context_var, (list, dict)):
            # For collections
            return json.dumps(str(context_var), indent=2)
        else:
            # For simple values
            return str(context_var)
    except Exception as e:
        return f"Debug error: {str(e)}"


@register.filter
def model_name(obj):
    """
    Get the model name of an object.
    Usage: {{ object|model_name }}
    """
    if hasattr(obj, "_meta"):
        return obj._meta.model_name
    return str(type(obj).__name__).lower()


# ========== DATALOG SPECIFIC FILTERS ==========

@register.filter
def code_line_count(code_content):
    """
    Count lines in code content for terminal display
    Usage: {{ post.featured_code|code_line_count }}
    """
    if not code_content:
        return 0
    return len(code_content.strip().split("\n"))


@register.filter
def code_complexity(code_content):
    """
    Analyze code complexity for display
    Usage: {{ post.featured_code|code_complexity }}
    """
    if not code_content:
        return "None"

    lines = len(code_content.strip().split('\n'))

    if lines < 10:
        return "Simple"
    elif lines < 30:
        return "Moderate"
    elif lines < 100:
        return "Complex"
    else:
        return "Advanced"


@register.filter
def datalog_difficulty(post):
    """
    Determine content difficulty based on multiple factors
    Usage: {{ post|datalog_difficulty }}
    """
    difficulty_score = 0

    # Reading time factor
    if post.reading_time > 15:
        difficulty_score += 2
    elif post.reading_time > 8:
        difficulty_score += 1

    # Code presence factor
    if hasattr(post, 'featured_code') and post.featured_code:
        code_lines = len(post.featured_code.split('\n'))
        if code_lines > 50:
            difficulty_score += 2
        elif code_lines > 20:
            difficulty_score += 1

    # Category factor (some categories inherently more complex)
    if hasattr(post, 'category') and post.category:
        # TODO: Adjust based on categories once defined in staging
        complex_categories = ['ML', 'AI', 'DATA', 'SYS']
        if post.category.code in complex_categories:
            difficulty_score += 1

    # Tag factor
    if hasattr(post, 'tags'):
        # TODO: Adjust based on tags once defined in staging, 
        # TODO: maybe prepopulate this list so don't have to adjust
        complex_tags = ['machine-learning', 'neural-networks', 'algorithms', 'system-design']
        tag_names = [tag.name.lower() for tag in post.tags.all()]
        if any(tag in complex_tags for tag in tag_names):
            difficulty_score += 1

    # Return difficulty level
    if difficulty_score <= 1:
        return "Beginner"
    elif difficulty_score <= 3:
        return "Intermediate"
    else:
        return "Advanced"


@register.filter
def extract_code_language_from_content(content):
    """
    Extract code language from markdown content
    Usage: {{ post.content|extract_code_language_from_content }}
    """
    if not content:
        return "text"

    # Look for code blocks with language specification
    pattern = r'```(\w+)'
    matches = re.findall(pattern, content)

    if matches:
        # return first found language
        # can later enhance for mult code blocks in datalogs?
        return matches[0]

    return "text"


# Formerly extract_code_blocks
@register.filter
def count_code_blocks(content):
    """Count code blocks in markdown content"""
    pattern = r"```(\w+)?\n(.*?)\n```"
    matches = re.findall(pattern, content, re.DOTALL)
    return len(matches)


# Formerly reading_level (maybe?)
@register.filter
def datalog_reading_level(post):
    """
    Return reading level indicator
    Usage: {{ post|datalog_reading_level }}
    """
    if not post.content:
        return "Quick"

    word_count = len(post.content.split())
    # code_blocks = count_code_blocks(post)

    if word_count < 500:
        return "Quick Read"
    elif word_count < 1500:
        return "Medium Read"
    # elif code_blocks > 3:
    #     return "Technical Deep Dive"
    else:
        return "Long Read"


@register.filter
def has_system_connection(post):
    """
    Check if post has system connections
    Usage: {{ post|has_system_connection }}
    """
    if hasattr(post, 'related_systems'):
        return post.related_systems.exists()
    if hasattr(post, 'system_connections'):
        return post.system_connections.exists()
    return False


@register.filter
def scale_tag_size(count):
    """
    Scale tag size for tag cloud based on usage count.
    Usage: {{ tag.post_count|scale_tag_size }}
    """
    if count <= 1:
        return 0.8
    elif count <= 3:
        return 0.9
    elif count <= 5:
        return 1.0
    elif count <= 10:
        return 1.2
    elif count <= 15:
        return 1.4
    elif count <= 20:
        return 1.6
    else:
        return 1.8


@register.filter
def total_views(posts):
    """
    Calculate total views for a collection of posts.
    Usage: {{ posts|total_views }}
    """
    if not posts:
        return 0

    total = 0
    for post in posts:
        if hasattr(post, "views") and hasattr(post.views, "count"):
            total += post.views.count()
        elif hasattr(post, "views_count"):
            total += post.views_count

    return total


@register.filter
def total_reading_time(posts):
    """
    Calculate total reading time for a collection of posts.
    Usage: {{ posts|total_reading_time }}
    """
    if not posts:
        return 0

    total = 0
    for post in posts:
        if hasattr(post, "reading_time"):
            total += post.reading_time or 0

    return total


@register.inclusion_tag("blog/includes/category_hexagon_single.html")
def category_hexagon_single(category, size="md", show_label=True):
    """
    Render a single category hexagon.
    Usage: {% category_hexagon_single category size="sm" show_label=False %}
    """
    return {
        "category": category,
        "size": size,
        "show_label": show_label,
    }


# ========== DATALOG TEMPLATE TAGS ==========


@register.simple_tag
def datalog_stats():
    """
    Get general DataLog statistics for overview pages.
    Usage: {% datalog_stats as stats %}
    Usage: {% datalog_stats %}
    """
    try:
        total_posts = Post.objects.filter(status="published").count()
        total_categories = Category.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status="published"))
        ).filter(post_count__gt=0).count()
        total_tags = Tag.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status="published"))
        ).filter(post_count__gt=0).count()
        total_reading_time = Post.objects.filter(
            status="published"
        ).aggregate(total=Sum('reading_time'))['total'] or 0
        total_words = sum(
            len(post.content.split()) for post in Post.objects.filter(status='published')
        )
        avg_reading_time = Post.objects.filter(status="published").aggregate(
            avg_time=Avg("reading_time"))["avg_time"] or 0,
        posts_with_code = Post.objects.filter(
            status='published',
            featured_code__isnull=False
        ).exclude(featured_code='').count()

        stats = {
            'total_posts': total_posts,
            'total_categories': total_categories,
            'total_tags': total_tags,
            'total_words': total_words,
            'avg_reading_time': round(avg_reading_time, 1),
            'posts_with_code': posts_with_code,
            'total_reading_time': total_reading_time,
        }

        return stats

    except Exception:
        return {
            "total_posts": 0,
            "total_categories": 0,
            "total_tags": 0,
            "total_words": 0,
            "avg_reading_time": 0,
            "posts_with_code": 0,
            "total_reading_time": 0,
        }


# Combined enhanced with former get_recent_posts tag
# Splitting back up to fetch by limit or by cutoff date, may rework later
@register.simple_tag
def recent_datalog_activity(days=30):
    """
    Get recent DataLog activity for dashboard
    Usage: {% recent_datalog_activity 30 %}
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        recent_posts = Post.objects.filter(
            status='published',
            published_date__gte=cutoff_date
        ).order_by('-published_date')

        # if exclude_id:
        #     recent_posts = recent_posts.exclude(id=exclude_id)

        return {
            'posts': recent_posts,
            'count': recent_posts.count(),
            'days': days
        }
    except Exception:
        return {
            'posts': [],
            'count': 0,
            'days': days
        }


@register.simple_tag
def get_recent_posts(limit=5, exclude_id=None):
    """
    Returns recently published posts.
    Usage: {% get_recent_posts 3 %}
    """
    posts = Post.objects.filter(status='published').order_by('-published_date')

    if exclude_id:
        posts = posts.exclude(id=exclude_id)

    return posts[:limit]


@register.simple_tag
def get_datalog_categories(popular_only=False, limit=None):
    """
    Get categories with post counts for various contexts.
    Usage: {% get_datalog_categories 6 as categories %}
    Usage: {% get_datalog_categories %}
    """
    try:
        categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by("-post_count")

        if popular_only:
            return categories[:5]

        if limit:
            return categories[:limit]
        return categories

    except Exception:
        return []


# Think can replace with new search_ajax_suggestions as part of unified
@register.simple_tag
def datalog_search_suggestions(query=""):
    """
    Generate search suggestions for the enhanced search
    Usage: {% datalog_search_suggestions query %}
    """
    suggestions = []

    if not query or len(query) < 2:
        # Return popular searches when no query
        return [
            {'text': 'Machine Learning', 'type': 'topic', 'icon': 'fas fa-brain'},
            {'text': 'Python Development', 'type': 'topic', 'icon': 'fab fa-python'},
            {'text': 'API Design', 'type': 'topic', 'icon': 'fas fa-plug'},
            {'text': 'Database', 'type': 'topic', 'icon': 'fas fa-database'},
            {'text': 'Neural Networks', 'type': 'topic', 'icon': 'fas fa-project-diagram'},
        ]

    try:
        query_lower = query.lower()

        # Search in post titles
        matching_posts = Post.objects.filter(
            title__icontains=query,
            status='published'
        )[:3]

        for post in matching_posts:
            suggestions.append({
                'text': post.title,
                'type': 'post',
                'icon': 'fas fa-file-alt',
                'url': post.get_absolute_url()
            })

        # Search in categories
        matching_categories = Category.objects.filter(
            name__icontains=query
        )[:2]

        for category in matching_categories:
            suggestions.append({
                'text': f"{category.name} Category",
                'type': 'category',
                'icon': 'fas fa-folder',
                'url': category.get_absolute_url()
            })

        # Search in tags
        matching_tags = Tag.objects.filter(
            name__icontains=query
        )[:2]

        for tag in matching_tags:
            suggestions.append({
                'text': f"#{tag.name}",
                'type': 'tag',
                'icon': 'fas fa-tag',
                'url': tag.get_absolute_url()
            })

    except Exception:
        pass

    return suggestions[:5]  # Limit to 5 suggestions


@register.simple_tag
def datalog_terminal_info(post):
    """
    Generate terminal information for code display
    Usage: {% datalog_terminal_info post %}
    """
    if not hasattr(post, 'featured_code') or not post.featured_code:
        return None

    code = post.featured_code
    language = getattr(post, 'featured_code_format', 'text')

    return {
        'filename': post.get_code_filename() if hasattr(post, 'get_code_filename') else f"code.{language}",
        'language': language.upper(),
        'line_count': len(code.split('\n')),
        'char_count': len(code),
        'complexity': code_complexity(code),
        'size': f"{len(code.encode('utf-8'))} bytes"
    }

# ========== IMPROVED COLOR FUNCTIONS FOR DATALOG TAGS ==========

@register.filter
def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple - SIMPLIFIED and more reliable
    Usage: {{ "#ff0000"|hex_to_rgb }} -> "255, 0, 0"
    """
    if not hex_color:
        # Default to lavendar
        return "179, 157, 219"

    # Clean hex_color
    hex_color = hex_color.strip()

    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        # Fallback
        return "179, 157, 219"

    try:
        # Convert to RBG
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    except ValueError:
        return "179, 157, 219"


@register.filter
def category_safe_color(category, fallback="#b39ddb"):
    """
    Get category color safely with fallback
    Usage: {{ post.category|category_safe_color }}
    """
    if not category:
        return fallback

    # Try to get color from category
    color = getattr(category, 'color', None)
    if not color:
        return fallback

    # Clean color
    color = str(color).strip()

    # Ensure it's valid hex color
    if not color.startswith('#'):
        color = '#' + color

    # Basic validation
    if len(color) == 7:
        try:
            # Try to convert to int to validate
            int(color[1:], 16)
            return color
        except ValueError:
            pass
    # if len(color) == 7 and all(c in '0123456789abcdefABCDEF' for c in color[:1]):
    #     return color
    return fallback


@register.filter
def category_rgb_values(category, fallback="179, 157, 219"):
    """
    Get category RGB values as string for CSS custom properties
    Usage: {{ post.category|category_rgb_values }}
    """
    if not category:
        return fallback

    color = category_safe_color(category)
    rgb = hex_to_rgb(color)

    # Double check valid result
    if rgb == "179, 157, 219" and hasattr(category, 'color') and category.color:
        # Category has color but conversion failed, try direct approach
        try:
            hex_color = category.color.strip().lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return f"{r}, {g}, {b}"
        except:
            pass

    return rgb


@register.simple_tag
def category_css_vars(category):
    """
    Generate CSS custom properties for a category - SIMPLIFIED
    Usage: {% category_css_vars category %}
    """
    if not category:
        return mark_safe(
            "--category-color: #b39ddb; "
            "--category-rgb: 179, 157, 219; "
            "--category-bg: rgba(179, 157, 219, 0.1); "
            "--category-border: rgba(179, 157, 219, 0.3);"
        )

    # Get safe color
    color = category_safe_color(category)
    rgb = hex_to_rgb(color)

    # Generate CSS variables
    css_vars = f"""
        --category-color: {color};
        --category-rgb: {rgb};
        --category-bg: rgba({rgb}, 0.1);
        --category-border: rgba({rgb}, 0.3);
        --category-hover: rgba({rgb}, 0.2);
        --category-active: rgba({rgb}, 0.15);
        --category-glow: rgba({rgb}, 0.4);
    """.strip()

    return mark_safe(css_vars)


@register.simple_tag
def unified_container_vars(category=None, theme="default"):
    """
    Generate CSS variables for unified container theming
    Usage: {% unified_container_vars post.category %}
    """
    # If we have category, use its color directly
    if category and hasattr(category, 'color') and category.color:
        color = category_safe_color(category)
        rgb = category_rgb_values(category)
    else:
        # Theme variations if no category
        if theme == "featured":
            rgb = "255, 245, 157"  # Gold
            color = "#fff59d"
        elif theme == "success":
            rgb = "165, 214, 167"  # Mint
            color = "#a5d6a7"
        elif theme == "warning":
            rgb = "255, 138, 128"  # Coral
            color = "#ff8a80"
        elif theme == "info":
            rgb = "38, 198, 218"  # Teal
            color = "#26c6da"
        else:
            # Default Lavender
            rgb = "179, 157, 219"
            color = "#b39ddb"

    css_vars = f"""
        --container-category-rgb: {rgb};
        --container-category-color: {color};
        --container-bg: rgba({rgb}, 0.08);
        --container-border: rgba({rgb}, 0.25);
        --container-glow: rgba({rgb}, 0.12);
        --container-hover-bg: rgba({rgb}, 0.15);
        --container-active-bg: rgba({rgb}, 0.2);
    """.strip()

    return mark_safe(css_vars)


@register.simple_tag
def category_debug_info(category):
    """
    Debug function to see what's happening with category colors
    Usage: {% category_debug_info post.category %}
    """
    if not category:
        return mark_safe("No category provided")

    debug_info = f"""
    <div style="background: #333; color: #fff; padding: 10px; margin: 10px 0; font-family: monospace; font-size: 12px;">
        <strong>CATEGORY DEBUG:</strong><br>
        Name: {getattr(category, "name", "N/A")}<br>
        Slug: {getattr(category, "slug", "N/A")}<br>
        Code: {getattr(category, "code", "N/A")}<br>
        Color (raw): {getattr(category, "color", "N/A")}<br>
        Color (safe): {category_safe_color(category)}<br>
        RGB: {category_rgb_values(category)}<br>
        Theme Class: {category_theme_classes(category)}<br>
    </div>
    """
    return mark_safe(debug_info)


@register.simple_tag
def smart_unified_container_vars(post=None, category=None, tag=None, archive=None, search=None, theme="auto"):
    """
    Generate CSS custom properties for unified containers based on content type.
    Usage:
    {% smart_unified_container_vars post=post %}
    {% smart_unified_container_vars category=category %}
    {% smart_unified_container_vars theme="featured" %}
    {% smart_unified_container_vars tag=tag %}
    {% smart_unified_container_vars archive=True %}
    {% smart_unified_container_vars search=True %}
    """
    # Get category from post if provided
    if post and hasattr(post, "category"):
        category = post.category

    # Special theme override for featured posts
    if post and hasattr(post, "featured") and post.featured and theme == "auto":
        theme = "featured"

    # Working in from view updates, may need more elegant solution later
    # Can return unified_container_vars, just need rgb, but all work too
    # category may conflict, others are new and should be fine
    # wait can use themes above kind of, category already defaults to lavender, just adding others
    # elif category:
    #     # Lavender for categories (if not overruled)
    #     return "--container-category-rgb: 179, 157, 219;"
    elif category:
        category=category
    elif not category and tag:
        # Teal theme for tags
        # return "--container-category-rgb: 38, 198, 218;"
        theme = "info"
    elif not category and archive:
        # Yellow theme for archive
        # return "--container-category-rgb: 255, 193, 7;"
        theme = "featured"
    elif not category and search:
        # Coral theme for search 
        # return "--container-category-rgb: 38, 198, 218;"
        theme = "warning"

    return unified_container_vars(category, theme)


@register.filter
def smart_color_contrast(hex_color, light_threshold=150):
    """
    Determine if text should be light or dark based on background color
    Usage: {{ category.color|smart_color_contrast }}
    Returns: "light" or "dark"
    """
    if not hex_color:
        return "light"

    rgb = hex_to_rgb(hex_color)
    try:
        r, g, b = map(int, rgb.split(", "))
        # Calculate luminance
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "dark" if luminance > light_threshold else "light"
    except:
        return "light"


@register.filter
def darken_color(hex_color, factor=0.8):
    """
    Darken a hex color by a factor
    Usage: {{ category.color|darken_color:0.7 }}
    """
    if not hex_color:
        return "#b39ddb"

    rgb = hex_to_rgb(hex_color)
    try:
        r, g, b = map(int, rgb.split(", "))
        # Darken each component
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color


@register.filter
def lighten_color(hex_color, factor=1.2):
    """
    Lighten a hex color by a factor
    Usage: {{ category.color|lighten_color:1.3 }}
    """
    if not hex_color:
        return "#b39ddb"

    rgb = hex_to_rgb(hex_color)
    try:
        r, g, b = map(int, rgb.split(", "))
        # Lighten each component
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color


@register.simple_tag
def category_theme_classes(category):
    """
    Generate theme classes based on category
    Usage: {% category_theme_classes post.category %}
    """
    if not category:
        return "theme-lavender"

    # Map common category types to themes
    category_name = getattr(category, "name", "").lower()
    category_code = getattr(category, "code", "").lower()

    theme_map = {
        "ml": "theme-purple",
        "ai": "theme-purple",
        "machine learning": "theme-purple",
        "dev": "theme-green",
        "development": "theme-green",
        "coding": "theme-green",
        "data": "theme-orange",
        "analytics": "theme-orange",
        "visualization": "theme-orange",
        "system": "theme-teal",
        "infrastructure": "theme-teal",
        "devops": "theme-teal",
    }

    # Check code first, then name
    theme = theme_map.get(category_code) or theme_map.get(category_name)
    return theme or "theme-lavender"


# Replaced with hex_to_rgb and other above, leaving for ref for now
# @register.filter
# def hex_to_rgba(hex_color, alpha=1.0):
#     """
#     Convert hex color to RGBA
#     Usage: {{ "#ff0000"|hex_to_rgba:0.5 }}
#     """
#     if not hex_color or not hex_color.startswith('#'):
#         return f"rgba(38, 198, 218, {alpha})"

#     try:
#         hex_color = hex_color.lstrip('#')

#         # Convert hex to rgb and add alpha
#         if len(hex_color) == 6:  # rrggbb format
#             r = int(hex_color[0:2], 16)
#             g = int(hex_color[2:4], 16)
#             b = int(hex_color[4:6], 16)
#             return f"rgba({r}, {g}, {b}, {alpha})"

#     except ValueError:
#         pass

#     return f"rgba(38, 198, 218, {alpha})"




@register.simple_tag
def json_ld_datalog(post):
    """
    Generate JSON-LD structured data for DataLog posts
    Usage: {% json_ld_datalog post %}
    """
    if not post:
        return ""

    structured_data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": getattr(post, "excerpt", ""),
        "datePublished": post.published_date.isoformat()
        if hasattr(post, "published_date") and post.published_date
        else "",
        "dateModified": post.updated.isoformat() if hasattr(post, "updated") else "",
        "author": {
            "@type": "Person",
            "name": post.author.get_full_name()
            if post.author.get_full_name()
            else post.author.username,
        },
        "publisher": {"@type": "Organization", "name": "AURA Development"},
    }

    if hasattr(post, "thumbnail") and post.thumbnail:
        structured_data["image"] = post.thumbnail.url

    if hasattr(post, "category") and post.category:
        structured_data["about"] = post.category.name

    if hasattr(post, "tags"):
        structured_data["keywords"] = [tag.name for tag in post.tags.all()]

    return mark_safe(
        f'<script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>'
    )


# ========== DATALOG INCLUSIONS ==========

# Redundant to breadcrumb_nav in aura_components.py?
@register.inclusion_tag('blog/includes/datalog_breadcrumb.html')
def datalog_breadcrumb(current_page=None, current_category=None, current_post=None):
    """
    Render DataLog breadcrumb navigation
    Usage: {% datalog_breadcrumb current_page="list" current_category=category %}
    """
    breadcrumbs = [{"title": "AURA", "url": "/", "icon": "fas fa-home"}]

    if current_page != "home":
        breadcrumbs.append(
            {
                "title": "DataLogs",
                "url": "/datalogs/",  # Adjust URL as needed
                "icon": "fas fa-database",
            }
        )

    if current_category:
        breadcrumbs.append(
            {
                "title": current_category.name,
                "url": current_category.get_absolute_url(),
                "icon": getattr(current_category, "icon", "fas fa-folder"),
            }
        )

    if current_post:
        breadcrumbs.append(
            {
                "title": current_post.title,
                "url": current_post.get_absolute_url(),
                "icon": "fas fa-file-alt",
                "current": True,
            }
        )

    return {"breadcrumbs": breadcrumbs}


# ========== DATALOG UTILITY FUNCTIONS ==========


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


@register.simple_tag
def get_reading_progress_color(reading_time):
    """
    Get color for reading time indicator
    Usage: {% get_reading_progress_color post.reading_time %}
    """
    if reading_time < 5:
        return "#a5d6a7"  # Green - quick read
    elif reading_time < 15:
        return "#26c6da"  # Teal - medium read
    else:
        return "#b39ddb"  # Lavender - long read


@register.simple_tag
def datalog_meta_tags(post, request=None):
    """
    Generate meta tags for DataLog posts
    Usage: {% datalog_meta_tags post request %}
    """
    if not post:
        return ""

    meta_tags = []

    # Basic meta tags
    if hasattr(post, "excerpt") and post.excerpt:
        meta_tags.append(f'<meta name="description" content="{post.excerpt[:160]}">')

    # Open Graph tags
    meta_tags.append(f'<meta property="og:title" content="{post.title}">')
    meta_tags.append(f'<meta property="og:type" content="article">')

    if hasattr(post, "excerpt") and post.excerpt:
        meta_tags.append(
            f'<meta property="og:description" content="{post.excerpt[:300]}">'
        )

    if request:
        full_url = request.build_absolute_uri(post.get_absolute_url())
        meta_tags.append(f'<meta property="og:url" content="{full_url}">')

    if hasattr(post, "thumbnail") and post.thumbnail:
        meta_tags.append(f'<meta property="og:image" content="{post.thumbnail.url}">')

    # Twitter Card tags
    meta_tags.append('<meta name="twitter:card" content="summary_large_image">')
    meta_tags.append(f'<meta name="twitter:title" content="{post.title}">')

    if hasattr(post, "excerpt") and post.excerpt:
        meta_tags.append(
            f'<meta name="twitter:description" content="{post.excerpt[:200]}">'
        )

    return mark_safe("\n".join(meta_tags))


# =========== Enhanced Inclusion Tags =========== #

@register.inclusion_tag('blog/includes/post_card.html')
def render_post_card(post, show_excerpt=True, card_type='default'):
    """
    Renders a post card with AURA styling.
    Usage: {% render_post_card post %}
    """
    return {
        'post': post,
        'show_excerpt': show_excerpt,
        'card_type': card_type,
    }


@register.inclusion_tag('blog/includes/category_nav.html')
def render_category_nav(current_category=None):
    """
    Renders the category hexagon navigation.
    Usage: {% render_category_nav current_category %}
    """
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)

    return {
        'categories': categories,
        'current_category': current_category,
    }


# Moved back
@register.inclusion_tag('components/pagination.html')
def render_pagination(page_obj, request):
    """
    Renders AURA-styled pagination.
    Usage: {% render_pagination page_obj request %}
    """
    return {
        'page_obj': page_obj,
        'request': request,
    }


@register.inclusion_tag('blog/includes/social_share.html', takes_context=True)
def social_share(context, post):
    """
    Renders social sharing buttons for a post.
    Usage: {% social_share post %}
    """
    request = context['request']
    post_url = request.build_absolute_uri(post.get_absolute_url())

    return {
        'post': post,
        'post_url': post_url,
        'site_name': 'AUA DataLogs',
    }

# =========== Enhanced Filters =========== #


@register.filter
def reading_time(content):
    """
    Calculates estimated reading time for content.
    Usage: {{ post.content|reading_time }}
    """
    if not content:
        return 0

    # Strip HTML and markdown
    text = re.sub(r'<[^>]+>', '', content)
    text = re.sub(r'[#*`\[\]()_]', '', content)

    word_count = len(text.split())
    # Average reading speed: 200 words per minute
    minutes = max(1, round(word_count / 200))
    return minutes


@register.filter
def markdown_headings(content):
    """
    Extracts headings from markdown content for table of contents.
    Usage: {{ post.content|markdown_headings }}
    """
    if not content:
        return []

    headings = []
    heading_pattern = r'^(#{1,3})\s+(.+)$'

    for line in content.split('\n'):
        match = re.match(heading_pattern, line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            # Create ID from heading
            heading_id = slugify(text)
            headings.append({
                'level': level,
                'text': text,
                'id': heading_id
            })

            return headings


@register.filter
def category_icon(category, default="fas fa-book-open"):
    """
    Return category icon code or default.
    Usage: {{ post.category|category_icon }}
    """
    if hasattr(category, 'icon') and category.icon:
        return f"fas {category.icon}"
    return default


@register.filter
def post_status_color(status):
    """
    Returns color for post status.
    Usage: {{ post.status|post_status_color }}
    """
    colors = {
        'draft': '#808080',
        'published': '#27c93f',
    }
    return colors.get(status, '#26c6da')


@register.simple_tag
def get_popular_tags(limit=10):
    """
    Returns most popular tags by post count.
    Usage: {% get_popular_tags %}
    Usage: {% get_popular_tags 5 as popular_tags %}
    """
    return Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:limit]


@register.simple_tag
def get_featured_post():
    """
    Returns the featured post if any.
    Usage: {% get_featured_post %}
    """
    return Post.objects.filter(
        status='published',
        featured=True
    ).first()


@register.simple_tag
def archive_years():
    """
    Get all years that have published posts for archive navigation.
    Usage: {% archive_years as years %}
    """
    years = Post.objects.filter(
        status="published"
    ).annotate(
        year=Extract('published_date', 'year')
    ).values('year').annotate(
        count=Count('id')
    ).order_by('-year')

    return list(years)


@register.simple_tag
def posts_by_month(year):
    """
    Returns posts grouped by month for a given year.
    Usage: {% posts_by_month 2024 %}
    """
    return Post.objects.filter(
        status='published',
        published_date__year=year
    ).dates('published_date', 'month', order='DESC')


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

# =========== CODE FORMATTING w PYGMENTS / TERMINAL COMPONENT =========== #


@register.filter(name="highlight_code")
@stringfilter
def highlight_code(code, language=None):
    try:
        # If lang is specified, get appropriate lexer
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        # Else, use simple txt lexer w no highlighting
        else:
            lexer = TextLexer()

        # Create HTML formatter w 'monokai' style
        # 'cssclass' sets CSS class that will be applied to wrapper
        formatter = HtmlFormatter(style="monokai", cssclass="highlighted")

        # Perform actual highlighting
        # Take code string, lexer for parsing, and formatter for output
        # Returns HTML w appropriate spans for syntax highlighting
        highlighted_code = highlight(code, lexer, formatter)

        # Mark output safe for rendering in template
        # Tells Django not to escape HTML tags in output
        return mark_safe(highlighted_code)
    except:
        # If any error occurs, return original code unchanged
        return code


@register.simple_tag
def pygments_css():
    # Create formatter to get CSS rules
    formatter = HtmlFormatter(style="monokai")

    # Get CSS style defs for specified style
    # 'get_style_defs()' returns CSS rules for given selector
    # '.highlighted' matches cssclass set in highlight_code
    css_rules = formatter.get_style_defs(".highlighted")

    # Wrap CSS in style tag, mark safe for rendering
    return mark_safe(f"<style>{css_rules}</style>")


@register.inclusion_tag("blog/includes/terminal_code_display.html")
def terminal_display(post, style='default'):
    """
    Renders a terminal code display with syntax highlighting.

    Usage:
    {% terminal_display post=post %}  # default style
    {% terminal_display post=post style="compact" %}
    {% terminal_display post=post style="minimal" %}
    {% terminal_display post=post style="fullscreen" %}

    Args:
        post: post
        style: 'default', 'compact', 'minimal', 'fullscreen'
    """
    return {
        "post": post,
        "code": post.featured_code,
        "language": post.featured_code_format,
        "filename": post.get_code_filename(),
        "style": style,
    }


# =========== ADDED AFTER GLOBAL FILTERS =============#


@register.filter
def category_color(category, default="#b39ddb"):
    """
    Returns category color or default.
    Usage: {{ post.category|category_color }}
    """
    if hasattr(category, "color") and category.color:
        return category.color
    return default

# =========== TIMELINE COMPONENTS TAGS & FILTERS =============#


@register.inclusion_tag("blog/includes/timeline_section.html")
def timeline_section(posts, style="timeline", group_by="month"):
    """
    Renders a timeline section with posts grouped by date.

    Usage:
    {% timeline_section posts=month_posts style="timeline" %}
    {% timeline_section posts=recent_posts style="compact" %}
    {% timeline_section posts=daily_posts style="vertical" %}

    Args:
        posts: QuerySet or list of posts
        style: 'timeline', 'compact', 'minimal', 'vertical'
        group_by: 'month', 'day', 'none' (for grouping)
    """
    return {
        "posts": posts,
        "style": style,
        "group_by": group_by,
    }


@register.simple_tag
def timeline_navigation(posts, current_year=None, current_month=None):
    """
    Generate timeline navigation data for year/month selection.

    Usage: {% timeline_navigation posts=all_posts current_year=year %}
    """
    # Group posts by year and month
    timeline_data = defaultdict(lambda: defaultdict(int))
    years = set()

    for post in posts:
        if hasattr(post, "published_date") and post.published_date:
            year = post.published_date.year
            month = post.published_date.month
            timeline_data[year][month] += 1
            years.add(year)

    # Convert to sorted lists
    year_data = []
    for year in sorted(years, reverse=True):
        months = []
        for month in range(1, 13):
            if timeline_data[year][month] > 0:
                months.append(
                    {
                        "number": month,
                        "name": calendar.month_name[month],
                        "short_name": calendar.month_name[month][:3],
                        "count": timeline_data[year][month],
                        "is_current": (year == current_year and month == current_month),
                    }
                )

        year_data.append(
            {
                "year": year,
                "total_posts": sum(timeline_data[year].values()),
                "months": months,
                "is_current": (year == current_year),
            }
        )

    return {
        "years": year_data,
        "total_posts": sum(sum(months.values()) for months in timeline_data.values()),
    }


@register.simple_tag
def timeline_stats(posts, period="all"):
    """
    Calculate timeline statistics for display.

    Usage: {% timeline_stats posts=posts period="month" %}
    """
    if not posts:
        return {
            "total_posts": 0,
            "total_reading_time": 0,
            "avg_reading_time": 0,
            "most_active_period": "N/A",
            "period_label": period,
        }

    # Calculate totals
    total_posts = len(posts)
    total_reading_time = sum(getattr(post, "reading_time", 0) for post in posts)
    avg_reading_time = total_reading_time / total_posts if total_posts > 0 else 0

    # Find most active period
    if period == "month":
        month_counts = Counter()
        for post in posts:
            if hasattr(post, "published_date") and post.published_date:
                month_year = post.published_date.strftime("%B %Y")
                month_counts[month_year] += 1

        most_active_period = (
            month_counts.most_common(1)[0][0] if month_counts else "N/A"
        )
    else:
        most_active_period = "All Time"

    return {
        "total_posts": total_posts,
        "total_reading_time": total_reading_time,
        "avg_reading_time": round(avg_reading_time, 1),
        "most_active_period": most_active_period,
        "period_label": period,
    }


@register.filter
def group_by_date(posts, group_type="month"):
    """
    Group posts by date period.
    Usage: {{ posts|group_by_date:"month" }}
    """
    if not posts:
        return []

    # Sort posts by date first
    sorted_posts = sorted(
        posts, key=lambda p: getattr(p, "published_date", timezone.now()), reverse=True
    )

    if group_type == "month":
        # Group by year-month
        def date_key(post):
            if hasattr(post, "published_date") and post.published_date:
                return (post.published_date.year, post.published_date.month)
            return (2024, 1)  # fallback

        grouped = []
        for key, group in groupby(sorted_posts, key=date_key):
            year, month = key
            posts_list = list(group)
            grouped.append(
                {
                    "date_key": f"{year}-{month:02d}",
                    "year": year,
                    "month": month,
                    "month_name": calendar.month_name[month],
                    "posts": posts_list,
                    "count": len(posts_list),
                }
            )
        return grouped

    elif group_type == "day":
        # Group by year-month-day
        def date_key(post):
            if hasattr(post, "published_date") and post.published_date:
                return post.published_date.date()
            return timezone.now().date()

        grouped = []
        for key, group in groupby(sorted_posts, key=date_key):
            posts_list = list(group)
            grouped.append(
                {
                    "date": key,
                    "posts": posts_list,
                    "count": len(posts_list),
                }
            )
        return grouped

    # Default: return as-is
    return sorted_posts


@register.filter
def timeline_date_range(posts):
    """
    Get the date range for a set of posts.
    Usage: {{ posts|timeline_date_range }}
    """
    if not posts:
        return {"start": None, "end": None, "span_days": 0}

    dates = []
    for post in posts:
        if hasattr(post, "published_date") and post.published_date:
            dates.append(post.published_date.date())

    if not dates:
        return {"start": None, "end": None, "span_days": 0}

    start_date = min(dates)
    end_date = max(dates)
    span_days = (end_date - start_date).days

    return {
        "start": start_date,
        "end": end_date,
        "span_days": span_days,
    }

# =========== CATEGORY HEXAGON COMPONENT TAGS/FILTERS =============#


@register.inclusion_tag("blog/includes/category_hexagon_nav.html", takes_context=True)
def category_hexagon_nav(
        context, style="full", current_category=None, show_all=True, limit=None):
    """
    Render category hexagon navigation with different styles.

    Usage:
    {% category_hexagon_nav style="full" current_category=category %}
    {% category_hexagon_nav style="compact" limit=6 %}
    {% category_hexagon_nav style="minimal" show_all=False %}
    {% category_hexagon_nav style="filter" %}

    Args:
        style (str): Navigation style - 'full', 'compact', 'minimal', 'filter'
        current_category (Category): Currently selected category
        show_all (bool): Whether to show "All Categories" option
        limit (int): Limit number of categories shown (for compact/minimal)
    """
    # Get categories w post counts
    categories = (
        Category.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status="published"))
        )
        .filter(post_count__gt=0)
        .order_by("-post_count", "name")
    )

    # Apply limit if specified
    if limit:
        categories = categories[:limit]

    # Get total posts count for "All" option
    total_posts = Post.objects.filter(status="published").count()

    # Get request for filter state
    request = context.get("request")

    return {
        "style": style,
        "current_category": current_category,
        "categories": categories,
        "show_all": show_all,
        "total_posts": total_posts,
        "request": request,
    }


@register.simple_tag
def category_hexagon_styles():
    """
    Include category hexagon CSS styles.
    Usage: {% category_hexagon_styles %}
    """
    return mark_safe("""
    <style>
    /* Category hexagon component styles are included in the component template */
    .category-hexagon-navigation {
        /* Component styles are self-contained */
    }
    </style>
    """)


@register.simple_tag
def category_scroll_controls(container_id="categoriesGrid"):
    """
    Generate scroll control buttons for category navigation.
    Usage: {% category_scroll_controls 'myContainerId' %}
    """
    return mark_safe(f"""
    <button class="category-scroll-btn category-scroll-left" 
            data-target="#{container_id}" 
            aria-label="Scroll categories left">
        <i class="fas fa-chevron-left"></i>
    </button>
    <button class="category-scroll-btn category-scroll-right" 
            data-target="#{container_id}" 
            aria-label="Scroll categories right">
        <i class="fas fa-chevron-right"></i>
    </button>
    """)


@register.filter
def category_hex_color(category, fallback="#26c6da"):
    """
    Get category color for hexagon styling.
    Usage: {{ category|category_hex_color }}
    """
    if hasattr(category, "color") and category.color:
        return category.color
    return fallback


@register.filter
def category_hex_code(category, fallback="LOG"):
    """
    Get category code for hexagon display.
    Usage: {{ category|category_hex_code }}
    """
    if hasattr(category, "code") and category.code:
        return category.code.upper()[:3]  # Ensure max 3 characters
    return fallback


@register.simple_tag(takes_context=True)
def is_category_active(context, category):
    """
    Check if a category is currently active.
    Usage: {% is_category_active category %}
    """
    current_category = context.get("current_category")
    if not current_category:
        return False

    if hasattr(category, "slug"):
        return current_category.slug == category.slug

    return False


@register.simple_tag
def category_nav_analytics(categories, style="full"):
    """
    Generate analytics data for category navigation.
    Usage: {% category_nav_analytics categories 'compact' as analytics %}
    """
    if not categories:
        return {}

    total_categories = len(categories)
    total_posts = sum(getattr(cat, "post_count", 0) for cat in categories)
    most_popular = (
        max(categories, key=lambda c: getattr(c, "post_count", 0))
        if categories
        else None
    )

    analytics = {
        "total_categories": total_categories,
        "total_posts": total_posts,
        "most_popular_category": most_popular,
        "average_posts_per_category": round(total_posts / total_categories, 1)
        if total_categories > 0
        else 0,
        "style": style,
    }

    # Add style-specific analytics
    if style == "compact":
        analytics["display_limit"] = min(6, total_categories)
        analytics["hidden_categories"] = max(0, total_categories - 6)
    elif style == "minimal":
        analytics["display_limit"] = min(4, total_categories)
        analytics["hidden_categories"] = max(0, total_categories - 4)

    return analytics


@register.inclusion_tag("blog/includes/category_hexagon_single.html")
def category_hexagon_single(category, size="md", show_label=True, link=True):
    """
    Render a single category hexagon.

    Usage:
    {% category_hexagon_single category size="lg" %}
    {% category_hexagon_single category show_label=False %}

    Args:
        category: Category object
        size (str): Hexagon size - 'sm', 'md', 'lg', 'xl'
        show_label (bool): Whether to show category name label
        link (bool): Whether to make hexagon clickable
    """
    size_map = {
        "xs": "24px",
        "sm": "32px",
        "md": "40px",
        "lg": "48px",
        "xl": "60px",
    }

    return {
        "category": category,
        "hex_size": size_map.get(size, "40px"),
        "show_label": show_label,
        "link": link,
        "size_class": f"hex-{size}",
    }


@register.simple_tag
def category_distribution_data(categories, format="json"):
    """
    Generate category distribution data for charts.
    Usage: {% category_distribution_data categories 'json' %}
    """
    if not categories:
        return "[]" if format == "json" else []

    data = []
    for category in categories:
        post_count = getattr(category, "post_count", 0)
        if post_count > 0:
            data.append(
                {
                    "name": category.name,
                    "code": getattr(category, "code", category.name[:3].upper()),
                    "color": getattr(category, "color", "#26c6da"),
                    "count": post_count,
                    "url": category.get_absolute_url()
                    if hasattr(category, "get_absolute_url")
                    else "#",
                }
            )

    if format == "json":
        return mark_safe(json.dumps(data))

    return data


@register.simple_tag
def category_quick_stats(categories):
    """
    Generate quick statistics for category navigation.
    Usage: {% category_quick_stats categories as stats %}
    """
    if not categories:
        return {
            "total_categories": 0,
            "total_posts": 0,
            "avg_posts": 0,
            "most_active": None,
            "least_active": None,
        }

    post_counts = [
        getattr(cat, "post_count", 0)
        for cat in categories
        if getattr(cat, "post_count", 0) > 0
    ]

    if not post_counts:
        return {
            "total_categories": len(categories),
            "total_posts": 0,
            "avg_posts": 0,
            "most_active": None,
            "least_active": None,
        }

    total_posts = sum(post_counts)
    most_active = max(categories, key=lambda c: getattr(c, "post_count", 0))
    least_active = min(categories, key=lambda c: getattr(c, "post_count", 0))

    return {
        "total_categories": len(categories),
        "total_posts": total_posts,
        "avg_posts": round(total_posts / len(categories), 1),
        "most_active": most_active,
        "least_active": least_active,
        "max_posts": getattr(most_active, "post_count", 0),
        "min_posts": getattr(least_active, "post_count", 0),
    }

# =========== POST DETAIL PAGE TAGS/FILTERS =============#


@register.simple_tag
def get_related_posts(post, limit=3):
    """
    Get related posts based on tags and category.
    Usage: {% get_related_posts post 3 as related_posts %}
    """
    if not post:
        return Post.objects.none()

    try:
        # Get posts with same tags or category
        related_posts = Post.objects.filter(status="published").exclude(id=post.id)

        # Filter by same category first
        same_category = related_posts.filter(category=post.category)

        # If we have enough from same category, use those
        if same_category.count() >= limit:
            return same_category.order_by("-published_date")[:limit]

        # Otherwise, get posts with similar tags
        if post.tags.exists():
            tag_ids = post.tags.values_list("id", flat=True)
            similar_tags = (
                related_posts.filter(tags__in=tag_ids)
                .annotate(tag_count=Count("tags"))
                .order_by("-tag_count", "-published_date")
            )

            # Combine same category and similar tags
            combined = list(same_category) + list(similar_tags)
            seen_ids = set()
            unique_posts = []

            for p in combined:
                if p.id not in seen_ids:
                    unique_posts.append(p)
                    seen_ids.add(p.id)
                if len(unique_posts) >= limit:
                    break

            return unique_posts

        # Fallback to recent posts from same category
        return same_category.order_by("-published_date")[:limit]

    except Exception:
        return (
            Post.objects.filter(status="published")
            .exclude(id=post.id)
            .order_by("-published_date")[:limit]
        )


@register.simple_tag
def get_previous_next_posts(post):
    """
    Get previous and next posts in chronological order.
    Usage: {% get_previous_next_posts post as nav_posts %}
    """
    try:
        # Get previous post (older)
        previous_post = (
            Post.objects.filter(
                status="published", published_date__lt=post.published_date
            )
            .order_by("-published_date")
            .first()
        )

        # Get next post (newer)
        next_post = (
            Post.objects.filter(
                status="published", published_date__gt=post.published_date
            )
            .order_by("published_date")
            .first()
        )

        return {"previous": previous_post, "next": next_post}
    except Exception:
        return {"previous": None, "next": None}


# ================= PHASE 2 CLEANUP ENHANCEMENTS =================

# Helper Post Color Scheme Getter
def get_post_color_scheme(post, color_scheme='auto'):
    # Determine color scheme
    if color_scheme == "auto":
        if hasattr(post, "featured") and post.featured:
            primary_color = "var(--color-yellow)"
            secondary_color = "rgba(255, 245, 157, 0.1)"
        elif (hasattr(post, "category") and post.category and hasattr(post.category, "color")):
            primary_color = post.category.color
            secondary_color = f'rgba({hex_to_rgb(post.category.color)}, 0.1)'
        else:
            primary_color = "var(--color-lavendar)"
            secondary_color = "rgba(179, 157, 219, 0.1)"
    elif color_scheme == "category" and hasattr(post, "category") and post.category:
        primary_color = getattr(post.category, "color", "var(--color-lavendar)")
        secondary_color = f'rgba({hex_to_rgb(primary_color)}, 0.1)'
    elif color_scheme == "featured":
        primary_color = "var(--color-yellow)"
        secondary_color = "rgba(255, 245, 157, 0.1)"
    elif color_scheme == "status":
        status = getattr(post, "status", "published")
        primary_color = status_color(status)
        secondary_color = f"rgba({hex_to_rgb(primary_color)}, 0.1)"
    else:
        primary_color = "var(--color-lavendar)"
        secondary_color = "rgba(179, 157, 219, 0.1)"
    return {
        'primary_color': primary_color,
        'secondary_color': secondary_color
    }


# ================= META  DISPLAY =================


@register.inclusion_tag('blog/includes/datalog_meta_display.html', takes_context=True)
def datalog_meta_display(
        context, post, style='full', show_category=True, show_tags=True,
        show_reading_time=True, show_date=True, show_author=False,
        show_status=False, show_featured=True, show_systems=False,
        date_format='relative', max_tags=None, compact_tags=False,
        icon_style='auto', alignment='left', size='md', color_scheme='auto'):

    """
    Display post metadata with multiple style options and extensive customization.

    Usage Examples:
    {% datalog_meta_display post style='full' %}
    {% datalog_meta_display post style='compact' show_tags=False %}
    {% datalog_meta_display post style='minimal' show_category=False %}
    {% datalog_meta_display post style='inline' date_format='short' %}
    {% datalog_meta_display post style='detailed' show_author=True show_systems=True %}
    {% datalog_meta_display post style='card' max_tags=3 compact_tags=True %}
    {% datalog_meta_display post style='breadcrumb' show_reading_time=False %}

    Args:
        post: Post object
        style (str): Display style - 'full', 'compact', 'minimal', 'inline', 'detailed', 'card', 'breadcrumb'
        show_category (bool): Show category information
        show_tags (bool): Show post tags
        show_reading_time (bool): Show estimated reading time
        show_date (bool): Show publication date
        show_author (bool): Show post author
        show_status (bool): Show post status (draft/published)
        show_featured (bool): Show featured indicator
        show_systems (bool): Show related systems
        date_format (str): Date format - 'relative', 'short', 'long', 'iso'
        max_tags (int): Maximum number of tags to show (None = all)
        compact_tags (bool): Use compact tag display
        icon_style (str): Icon style - 'auto', 'minimal', 'full', 'none'
        alignment (str): Content alignment - 'left', 'center', 'right'
        size (str): Overall size - 'xs', 'sm', 'md', 'lg', 'xl'
        color_scheme (str): Color scheme - 'auto', 'category', 'featured', 'status'
    """

    # Get request for context-aware features
    request = context.get('request')

    # Determine color scheme with helper
    colors = get_post_color_scheme(post, color_scheme=color_scheme)
    primary_color = colors.get('primary_color')
    secondary_color = colors.get('secondary_color')

    # Format date based on format preference
    if show_date and hasattr(post, 'published_date') and post.published_date:
        match date_format:
            case 'relative':
                formatted_date = time_since_published(post.published_date)
            case 'short':
                formatted_date = post.published_date.strftime('%b %d, %Y')
            case 'long':
                formatted_date = post.published_date.strftime('%B %d, %Y')
            case 'iso':
                formatted_date = post.published_date.isoformat()
            case _:
                formatted_date = time_since_published(post.published_date)
    else:
        formatted_date = None

    # Process tags w limits
    post_tags = []
    if show_tags and hasattr(post, 'tags'):
        try:
            all_tags = post.tags.all()
            if max_tags:
                post_tags = list(all_tags[:max_tags])
                remaining_tags = max(0, all_tags.count() - max_tags)
            else:
                post_tags = list(all_tags)
                remaining_tags = 0
        except:
            post_tags = []
            remaining_tags = 0
    else:
        remaining_tags = 0

    # Get system connections if requested
    related_systems = []
    if show_systems and hasattr(post, 'related_systems'):
        try:
            # Limit to 3 for display
            related_systems = post.related_systems.all()[:3]
        except:
            related_systems = []

    # Determine icon visibility based on style and preference
    match icon_style:
        case 'auto':
            show_icons = style in ['full', 'detailed', 'card']
        case 'minimal':
            show_icons = style in ['full', 'detailed']
        case 'full':
            show_icons = True
        # None/else
        case _:
            show_icons = False

    # Calculate reading time display
    reading_time_display = None
    if show_reading_time and hasattr(post, 'reading_time'):
        reading_time = getattr(post, 'reading_time', 0)
        if reading_time:
            reading_time_display = format_duration(reading_time)
        else:
            # Fallback calculation if reading_time not set
            content = getattr(post, 'content', '')
            if content:
                word_count = len(content.split())
                estimated_minutes = max(1, word_count // 200)
                reading_time_display = format_duration(estimated_minutes)

    # Get author info
    author_info = None
    if show_author and hasattr(post, 'author'):
        author = post.author
        author_info = {
            'name': author.get_full_name() if author.get_full_name() else author.username,
            'username': author.username
        }

    # Status Info
    status_info = None
    if show_status and hasattr(post, 'status'):
        status_info = {
            'status': post.status,
            'display': post.get_status_display() if hasattr(post, 'get_status_display') else post.status.replace('_', ' ').title(),
            'color': status_color(post.status)
        }

    # Featured indicator
    is_featured = show_featured and hasattr(post, 'featured') and post.featured

    # Build CSS classes
    css_classes = [
        'datalog-meta-display',
        f'meta-style-{style}',
        f'meta-size-{size}',
        f'meta-align-{alignment}',
    ]

    if is_featured:
        css_classes.append('meta-featured')

    if hasattr(post, 'category') and post.category:
        css_classes.append(f'meta-category-{post.category.slug}')

    return {
        'post': post,
        'style': style,
        'size': size,
        'alignment': alignment,
        'css_classes': ' '.join(css_classes),

        # Display flags
        'show_category': show_category,
        'show_tags': show_tags,
        'show_reading_time': show_reading_time,
        'show_date': show_date,
        'show_author': show_author,
        'show_status': show_status,
        'show_featured': show_featured,
        'show_systems': show_systems,
        'show_icons': show_icons,

        # Processed data
        'formatted_date': formatted_date,
        'post_tags': post_tags,
        'remaining_tags': remaining_tags,
        'compact_tags': compact_tags,
        'related_systems': related_systems,
        'reading_time_display': reading_time_display,
        'author_info': author_info,
        'status_info': status_info,
        'is_featured': is_featured,

        # Theming
        'primary_color': primary_color,
        'secondary_color': secondary_color,
        'date_format': date_format,

        # Context
        'request': request,
    }


# Additional helper tags for meta display
@register.simple_tag
def meta_separator(style='default', color='auto'):
    """
    Generate a separator for meta elements.
    Usage: {% meta_separator style='dot' color='teal' %}
    """
    separators = {
        'default': '•',
        'dot': '•',
        'pipe': '|',
        'slash': '/',
        'arrow': '→',
        'chevron': '›',
        'diamond': '◆',
        'bullet': '▸'
    }

    separator_char = separators.get(style, '•')

    if color == 'auto':
        color_class = 'meta-separator-auto'
    else:
        color_class = f'meta-separator-{color}'

    return mark_safe(f'<span class="meta-separator {color_class}">{separator_char}</span>')


@register.filter
def meta_truncate_title(title, style='full'):
    """
    Truncate post title based on meta display style or context.
    Usage: {{ post.title|meta_truncate_title:style }}
    """
    if not title:
        return ''

    truncate_limits = {
        "minimal": 30,
        "compact": 40,
        "inline": 35,
        "card": 45,
        "breadcrumb": 25,
        "full": 80,
        "detailed": 100,

        # context limits
        "mobile": 25,
        "compact": 40,
        "sidebar": 35,
        "default": 50,
    }

    limit = truncate_limits.get(style, 80)
    return truncate_smart(title, limit)


@register.simple_tag
def meta_category_display(
        category, style='default', show_icon=True, show_code=True, show_name=True):
    """
    Display category information with consistent styling.
    Usage: {% meta_category_display post.category style='compact' %}
    """
    if not category:
        return ''

    parts = []

    # Icon
    if show_icon and hasattr(category, 'icon') and category.icon:
        parts.append(f'<i class="fas {category.icon}"></i>')

    # Code
    if show_code and hasattr(category, 'code') and category.code:
        # Ensure max 3 chars
        code = category.code.upper()[:3]
        parts.append(f'<span class="category-code">{code}</span>')

    # Name
    if show_name:
        name = category.name
        if style in ["compact", "minimal"]:
            name = truncate_smart(name, 20)
        parts.append(f'<span class="category-name">{name}</span>')

    # Get category color
    color = getattr(category, "color", "#b39ddb")

    category_content = " ".join(parts)

    html = f'''
    <span class="meta-category meta-category-{style}" 
          style="--category-color: {color};" 
          data-category="{category.slug}">
        {category_content}
    </span>
    '''

    return mark_safe(html)


@register.filter
def meta_reading_difficulty(post):
    """
    Calculate and display reading difficulty indicator for meta display.
    Usage: {{ post|meta_reading_difficulty }}
    """
    difficulty = datalog_difficulty(post)

    difficulty_config = {
        "Beginner": {
            "icon": "fas fa-leaf",
            "color": "var(--color-mint)",
            "class": "difficulty-beginner",
        },
        "Intermediate": {
            "icon": "fas fa-fire",
            "color": "var(--color-coral)",
            "class": "difficulty-intermediate",
        },
        "Advanced": {
            "icon": "fas fa-bolt",
            "color": "var(--color-yellow)",
            "class": "difficulty-advanced",
        },
    }

    config = difficulty_config.get(difficulty, difficulty_config["Beginner"])

    html = f'''
    <span class="meta-difficulty {config["class"]}" 
          style="--difficulty-color: {config["color"]};"
          title="Difficulty: {difficulty}">
        <i class="{config["icon"]}"></i>
        <span class="difficulty-text">{difficulty}</span>
    </span>
    '''

    return mark_safe(html)


# ================= CONTENT NAVIGATION =================


@register.inclusion_tag('blog/includes/content_navigator.html', takes_context=True)
def content_navigator(
        context, post, style='sidebar', show_toc=True, show_progress=True,
        show_stats=False, show_navigation=True, toc_depth=3, position='sticky'):
    """
    STREAMLINED content navigator using existing AURA components.

    Usage Examples:
    {% content_navigator post %}
    {% content_navigator post style='full' show_stats=True %}
    {% content_navigator post style='floating' %}
    {% content_navigator post style='minimal' show_toc=False %}

    Args:
        post: Post object
        style: 'sidebar', 'full', 'floating', 'minimal', 'compact'
        show_toc: Generate TOC from content
        show_progress: Show reading progress bar
        show_stats: Show reading statistics
        show_navigation: Show prev/next navigation
        toc_depth: Maximum heading depth (1-6)
        position: 'sticky', 'static', 'floating'
    """
    # Reuse: Get stats from existing tag
    existing_stats = datalog_stats() if show_stats else {}

    # Reuse: Get nav from existing tag
    nav_data = get_previous_next_posts(post) if show_navigation else {}

    # Generate TOC
    toc_data = generate_toc_from_content(post.content, toc_depth) if show_toc else []

    # Get reading time from post or calculate
    reading_time = getattr(post, 'reading_time', 0)
    if not reading_time and hasattr(post, 'content'):
        word_count = len(post.content.split())
        reading_time = max(1, word_count // 200)

    # Build config for JavaScript
    navigator_config = {
        'id': f'content-navigator-{post.id}',
        'target_content': 'postContent',
        'toc_depth': toc_depth,
        'smoot_scroll': True,
    }

    # Build CSS classes
    css_classes = [
        'content-navigator',
        f'navigator-{style}',
        f'navigator-{position}',
    ]

    return {
        "post": post,
        "style": style,
        "position": position,
        "css_classes": " ".join(css_classes),

        # Feature flags
        "show_toc": show_toc,
        "show_progress": show_progress,
        "show_stats": show_stats,
        "show_navigation": show_navigation,

        # REUSED DATA: No recalculation needed!
        "toc_data": toc_data,
        "existing_stats": existing_stats,
        "nav_data": nav_data,
        "navigator_config": navigator_config,

        # Simple values
        "total_reading_time": reading_time,
        "initial_progress": 0,  # JS will update this
        "toc_depth": toc_depth,

        # Context
        "request": context.get("request"),
    }


def generate_toc_from_content(content, max_depth=3):
    """
    Generate table of contents from markdown content.
    """
    if not content:
        return []

    # Find all markdown headings - replace/call markdown_headings tag?
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    headings = []

    for line_num, line in enumerate(content.split('\n')):
        match = re.match(heading_pattern, line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()

            # skip if too deep
            if level > max_depth:
                continue

            # Generate unique ID
            heading_id = generate_unique_heading_id(text, headings)

            headings.append({
                'level': level,
                'text': text,
                'id': heading_id,
                'line_number': line_num,
            })

    return headings


def generate_unique_heading_id(text, existing_headings):
    """Generate unique heading ID from text."""
    base_id = slugify(text)
    heading_id = base_id

    # Ensure uniqueness
    counter = 1
    existing_ids = {h['id'] for h in existing_headings if 'id' in h}

    while heading_id in existing_ids:
        heading_id = f"{base_id}-{counter}"
        counter += 1

    return heading_id


# 🔄 REUSE: Simple filter for TOC accessibility
# Noted as reuse, but not sure from where..?
@register.filter
def toc_accessibility_label(heading):
    """Generate accessibility label for TOC links."""
    level_names = {
        1: "Main section",
        2: "Subsection",
        3: "Sub-subsection",
        4: "Fourth level",
        5: "Fifth level",
        6: "Sixth level",
    }

    level_name = level_names.get(heading.get("level", 1), "Section")
    heading_text = heading.get("text", "Unknown")

    return f"{level_name}: {heading_text}"


# Reuse: JSON config helper - may be able to combine w json_encode in aura_filters
# other return None from ex and is a simple_tag
@register.filter
def navigator_json_config(config):
    """Convert config to JSON for JavaScript."""
    try:
        return mark_safe(json.dumps(config))
    except (TypeError, ValueError):
        return mark_safe('{}')

# ================= ARCHIVE TIMELINE =================


@register.inclusion_tag('blog/includes/archive_timeline.html', takes_context=True)
def archive_timeline(
        context, posts=None, style='full', group_by='month',
        show_stats=True, show_navigation=True, show_filters=False,
        year=None, month=None, auto_expand=False, max_posts_per_group=None, compact_threshold=10):
    """
    STREAMLINED archive timeline using existing AURA components.

    Usage Examples:
    {% archive_timeline posts style='full' group_by='month' %}
    {% archive_timeline posts style='compact' year=2024 %}
    {% archive_timeline posts style='minimal' show_stats=False %}
    {% archive_timeline posts style='yearly' group_by='year' %}
    {% archive_timeline posts style='cards' max_posts_per_group=5 %}

    Args:
        posts: QuerySet of posts (if None, gets all published)
        style: 'full', 'compact', 'minimal', 'yearly', 'cards'
        group_by: 'month', 'year', 'quarter', 'week'
        show_stats: Show timeline statistics
        show_navigation: Show year/month navigation
        show_filters: Show filtering options
        year: Filter to specific year
        month: Filter to specific month (requires year)
        auto_expand: Auto-expand current period
        max_posts_per_group: Limit posts shown per group
        compact_threshold: Switch to compact if more than X groups
    """

    # REUSE: Get posts using existing patterns
    if posts is None:
        posts = Post.objects.filter(status='published').order_by('-published_date')

    # Apply year/month filtering if specified
    if year:
        posts = posts.filter(published_date__year=year)
        if month:
            posts = posts.filter(published_date__month=month)

    # REUSE: Group posts using existing filter
    grouped_posts = group_by_date(posts, group_by)

    # Auto-switch to compact if too many groups
    if len(grouped_posts) > compact_threshold and style == 'full':
        style = 'compact'

    # REUSE: Get timeline nav using existing tag
    timeline_nav = timeline_navigation(posts, year, month) if show_navigation else {}

    # REUSE: Get stats using existing tag
    timeline_statistics = timeline_stats(posts, group_by) if show_stats else {}

    # Get current period for auto-expansion
    now = timezone.now()
    current_period = None
    if auto_expand:
        if group_by == 'month':
            current_period = f"{now.year}-{now.month:02d}"
        elif group_by == 'year':
            current_period = str(now.year)

    # Limit posts per group if specified
    if max_posts_per_group:
        for group in grouped_posts:
            if 'posts' in group and len(group['posts']) > max_posts_per_group:
                group['posts'] = group['posts'][:max_posts_per_group]
                group['has_more'] = True
                group['remaining_count'] = len(group['posts']) - max_posts_per_group

    # Build CSS classes
    css_classes = [
        'archive-timeline',
        f'timeline-style-{style}',
        f'timeline-group-{group_by}',
    ]

    if auto_expand:
        css_classes.append('timeline-auto-expand')

    if show_filters:
        css_classes.append('timeline-with-filters')

    # Determine if we should show year selector
    years_available = list(posts.dates('published_date', 'year', order='DESC'))

    return {
        'posts': posts,
        'grouped_posts': grouped_posts,
        'style': style,
        'group_by': group_by,
        'css_classes': ' '.join(css_classes),

        # Feature flags
        'show_stats': show_stats,
        'show_navigation': show_navigation,
        'show_filters': show_filters,
        'auto_expand': auto_expand,

        # REUSED DATA: No recalculation needed
        'timeline_nav': timeline_nav,
        'timeline_statistics': timeline_statistics,

        # Current state
        'current_year': year or now.year,
        'current_month': month,
        'current_period': current_period,
        'years_available': years_available,

        # Configuration
        'max_posts_per_group': max_posts_per_group,
        'compact_threshold': compact_threshold,

        # Context
        'request': context.get('request'),
    }

# Helper tags for archive timeline
@register.simple_tag
def archive_period_display(group_data, group_by='month'):
    """
    Generate display text for archive periods.
    Usage: {% archive_period_display group 'month' %}
    """
    if group_by == "month":
        month_name = getattr(group_data, "month_name", "Unknown")
        year = getattr(group_data, "year", 2024)
        return f"{month_name} {year}"
    elif group_by == "year":
        return str(getattr(group_data, "year", 2024))
    elif group_by == "quarter":
        quarter = getattr(group_data, "quarter", 1)
        year = getattr(group_data, "year", 2024)
        return f"Q{quarter} {year}"
    elif group_by == "week":
        week = getattr(group_data, "week", 1)
        year = getattr(group_data, "year", 2024)
        return f"Week {week}, {year}"

    return "Unknown Period"

# Can I pass this and make it work...?
@register.filter
def archive_period_disp_filter(group_data, group_by='month'):
    """
    Helper to pass to archive_period_display if included in another simple block or tag.
    Usage: {{ group_data|archive_period_disp_filter:group_by='month' }}
    """
    return archive_period_display(group_data, group_by)


@register.simple_tag
def archive_period_url(group_data, group_by="month"):
    """
    Generate URL for archive period filtering.
    Usage: {% archive_period_url group 'month' %}
    """
    try:
        year = getattr(group_data, "year")
        month = getattr(group_data, "month")

        if group_by == "month" and year and month:
            return reverse("blog:archive_month", kwargs={"year": year, "month": month})
        elif group_by == "year" and year:
            return reverse("blog:archive_year", kwargs={"year": year})

        return reverse("blog:archive")
    except:
        # Fallback to archive main page
        return reverse("blog:post_list")


@register.filter
def archive_group_icon(group_by):
    """
    Get icon for archive group type.
    Usage: {{ 'month'|archive_group_icon }}
    """
    icons = {
        "month": "fas fa-calendar-alt",
        "year": "fas fa-calendar",
        "quarter": "fas fa-calendar-week",
        "week": "fas fa-calendar-day",
        "day": "fas fa-clock",
    }
    return icons.get(group_by, "fas fa-calendar")


@register.simple_tag
def archive_breadcrumb_data(year=None, month=None, group_by="month"):
    """
    Generate breadcrumb data for archive pages.
    Usage: {% archive_breadcrumb_data year month 'month' as breadcrumb_data %}
    """
    breadcrumbs = [
        {
            "title": "DataLogs",
            "url": reverse("blog:post_list"),
            "icon": "fas fa-database",
        },
        {
            "title": "Archive",
            "url": reverse("blog:post_list"),
            "icon": "fas fa-archive",
        },  # Fallback URL
    ]

    if year:
        breadcrumbs.append(
            {
                "title": str(year),
                "url": reverse("blog:post_list")
                + f"?year={year}",  # Fallback with query param
                "icon": "fas fa-calendar",
            }
        )

        if month and group_by == "month":
            month_name = calendar.month_name[month]
            breadcrumbs.append(
                {
                    "title": month_name,
                    "url": reverse("blog:post_list")
                    + f"?year={year}&month={month}",  # Fallback with query params
                    "icon": "fas fa-calendar-alt",
                    "current": True,
                }
            )

    return breadcrumbs


@register.simple_tag
def archive_summary_stats(grouped_posts, group_by="month"):
    """
    Generate summary statistics for archive timeline.
    Usage: {% archive_summary_stats grouped_posts 'month' as summary %}
    """
    if not grouped_posts:
        return {
            "total_periods": 0,
            "total_posts": 0,
            "avg_posts_per_period": 0,
            "most_active_period": None,
            "least_active_period": None,
        }

    total_periods = len(grouped_posts)
    total_posts = sum(getattr(group, "count", 0) for group in grouped_posts)
    avg_posts = round(total_posts / total_periods, 1) if total_periods > 0 else 0

    # Find most/least active periods
    most_active = (
        max(grouped_posts, key=lambda g: getattr(g, "count", 0)) if grouped_posts else None
    )
    least_active = (
        min(grouped_posts, key=lambda g: getattr(g, "count", 0)) if grouped_posts else None
    )

    return {
        "total_periods": total_periods,
        "total_posts": total_posts,
        "avg_posts_per_period": avg_posts,
        "most_active_period": most_active,
        "least_active_period": least_active,
        "most_posts_in_period": getattr(most_active, "count", 0) if most_active else 0,
        "least_posts_in_period": getattr(least_active, "count", 0) if least_active else 0,
        "group_by": group_by,
    }


@register.filter
def archive_activity_level(post_count, avg_posts=5):
    """
    Determine activity level for styling.
    Usage: {{ group.count|archive_activity_level:avg_posts }}
    """
    if post_count >= avg_posts * 2:
        return "high-activity"
    elif post_count >= avg_posts:
        return "normal-activity"
    elif post_count > 0:
        return "low-activity"
    else:
        return "no-activity"


# Enhanced version of exisiting functions for archive use
# May be able to rework/consolidate later


@register.filter
def group_by_quarter(posts):
    """
    Group posts by quarter.
    Usage: {{ posts|group_by_quarter }}
    """
    if not posts:
        return []

    # Sort posts by date first
    sorted_posts = sorted(
        posts, key=lambda p: getattr(p, 'published_date', timezone.now()), reverse=True
    )

    def quarter_key(post):
        if hasattr(post, 'published_date') and post.published_date:
            quarter = (post.published_date.month - 1) // 3 + 1
            return (post.published_date.year, quarter)
        # Fallback
        return (2024, 1)

    grouped = []
    for key, group in groupby(sorted_posts, key=quarter_key):
        year, quarter = key
        posts_lists = list(group)

        # Get quarter months for display
        quarter_months = {
            1: "Jan-Mar",
            2: "Apr-Jun",
            3: "Jul-Sep",
            4: "Oct-Dec"
        }

        grouped.append({
            'date_key': f'{year}-Q{quarter}',
            'year': year,
            'quarter': quarter,
            'quarter_name': f"Q{quarter}",
            'quarter_months': quarter_months[quarter],
            'posts': posts_lists,
            'count': len(posts_lists),
        })

    return grouped


@register.simple_tag
def archive_filter_options(posts, current_year=None, current_month=None):
    """
    Generate filter options for archive timeline.
    Usage: {% archive_filter_options posts current_year current_month as filter_options %}
    """
    # Get available years
    years = posts.dates('published_date', 'year', order='DESC')

    # Get available months for current year
    months = []
    if current_year:
        year_posts = posts.filter(published_date__year=current_year)
        month_dates = year_posts.dates('published_date', 'month', order='DESC')

        for date in month_dates:
            months.append({
                'number': date.month,
                'name': calendar.month_name[date.month],
                'short_name': calendar.month_name[date.month][:3],
                'year': date.year,
                'count': year_posts.filter(published_date__month=date.month).count(),
                'is_current': date.month == current_month,
            })

    # Get available categories
    categories = (
        Category.objects.annotate(
            archive_post_count=Count("posts", filter=Q(posts__in=posts))
        )
        .filter(archive_post_count__gt=0)
        .order_by("-archive_post_count")
    )

    return {
        "years": [
            {"year": y.year, "is_current": y.year == current_year} for y in years
        ],
        "months": months,
        "categories": categories,
        "has_filters": bool(years or months or categories),
    }


@register.simple_tag
def archive_smart_grouping(posts, max_groups=12):
    """
    Automatically determine the best grouping for archive display.
    Usage: {% archive_smart_grouping posts 10 as smart_group %}
    """
    if not posts:
        return {"group_by": "month", "posts": []}

    # Get date range
    date_range = timeline_date_range(posts)
    span_days = getattr(date_range, "span_days", 0)

    # Determine best grouping based on span
    if span_days <= 90:  # 3 months or less
        group_by = "week"
    elif span_days <= 730:  # 2 years or less
        group_by = "month"
    else:  # More than 2 years
        group_by = "year"

    # Group and check if we have too many groups
    grouped = group_by_date(posts, group_by)

    # If still too many groups, switch to larger grouping
    if len(grouped) > max_groups:
        if group_by == "week":
            group_by = "month"
            grouped = group_by_date(posts, group_by)
        elif group_by == "month":
            group_by = "year"
            grouped = group_by_date(posts, group_by)

    return {
        "group_by": group_by,
        "grouped_posts": grouped,
        "total_groups": len(grouped),
        "span_days": span_days,
    }


@register.filter
def archive_period_progress(group_data, group_by="month"):
    """
    Calculate how much of the period has passed (for current periods).
    Usage: {{ group|archive_period_progress:'month' }}
    """
    now = timezone.now()

    try:
        if group_by == "month":
            year = getattr(group_data, "year", now.year)
            month = getattr(group_data, "month", now.month)

            if year == now.year and month == now.month:
                # Current month - calculate progress

                days_in_month = calendar.monthrange(year, month)[1]
                current_day = now.day
                return round((current_day / days_in_month) * 100, 1)

        elif group_by == "year":
            year = getattr(group_data, "year", now.year)

            if year == now.year:
                # Current year - calculate progress

                start_of_year = datetime.date(year, 1, 1)
                end_of_year = datetime.date(year, 12, 31)
                current_date = now.date()

                total_days = (end_of_year - start_of_year).days + 1
                elapsed_days = (current_date - start_of_year).days + 1

                return round((elapsed_days / total_days) * 100, 1)
    except:
        pass

    return 100  # Period is complete or error occurred


@register.simple_tag
def archive_navigation_data(posts, current_year=None, current_month=None):
    """
    Generate comprehensive navigation data for archive pages.
    Enhanced version of timeline_navigation.
    Usage: {% archive_navigation_data posts current_year current_month as nav_data %}
    """
    # Group posts by year and month
    nav_data = defaultdict(lambda: defaultdict(int))
    years = set()

    for post in posts:
        if hasattr(post, "published_date") and post.published_date:
            year = post.published_date.year
            month = post.published_date.month
            nav_data[year][month] += 1
            years.add(year)

    # Convert to sorted structure
    year_data = []
    for year in sorted(years, reverse=True):
        months = []
        for month in range(1, 13):
            if nav_data[year][month] > 0:
                months.append(
                    {
                        "number": month,
                        "name": calendar.month_name[month],
                        "short_name": calendar.month_name[month][:3],
                        "count": nav_data[year][month],
                        "is_current": (year == current_year and month == current_month),
                        "url": reverse("blog:post_list")
                        + f"?year={year}&month={month}",  # Fallback URL
                    }
                )

        year_data.append(
            {
                "year": year,
                "total_posts": sum(nav_data[year].values()),
                "months": months,
                "is_current": (year == current_year),
                "url": reverse("blog:post_list") + f"?year={year}",  # Fallback URL
            }
        )

    return {
        "years": year_data,
        "total_posts": sum(sum(months.values()) for months in nav_data.values()),
        "current_year": current_year,
        "current_month": current_month,
        "has_navigation": bool(year_data),
    }


# ================= READING PROGRESS INDICATOR =================


@register.inclusion_tag(
    "blog/includes/reading_progress_indicator.html", takes_context=True)
def reading_progress_indicator(
    context,
    post=None,
    style="bar",
    position="top",
    size="md",
    color="auto",
    show_percentage=True,
    show_time=False,
    show_position=False,
    animate=True,
    threshold=0.1,
    smooth=True,
    responsive=True,
):
    """
    STREAMLINED reading progress indicator using existing AURA components.

    Usage Examples:
    {% reading_progress_indicator post style='bar' position='top' %}
    {% reading_progress_indicator post style='circle' size='lg' show_time=True %}
    {% reading_progress_indicator post style='minimal' show_percentage=False %}
    {% reading_progress_indicator post style='floating' position='bottom-right' %}
    {% reading_progress_indicator post style='sidebar' show_position=True %}

    Args:
        post: Post object (optional - if None, tracks whole page)
        style: 'bar', 'circle', 'minimal', 'floating', 'sidebar', 'corner'
        position: 'top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'sidebar'
        size: 'xs', 'sm', 'md', 'lg', 'xl'
        color: 'auto', 'teal', 'lavender', 'coral', 'mint', 'category'
        show_percentage: Show percentage text
        show_time: Show elapsed/remaining time
        show_position: Show current position indicator
        animate: Enable animations and transitions
        threshold: Minimum scroll to start showing (0.0-1.0)
        smooth: Use smooth animations
        responsive: Responsive size adjustments
    """

    request = context.get("request")

    # Determine color scheme
    # TODO: convert to use reusable helper get_post_color_scheme() above
    # colors = get_post_color_scheme(post, color_scheme=color)

    if color == 'auto':
        if post and hasattr(post, 'featured') and post.featured:
            primary_color = 'var(--color-yellow)'
            progress_color = 'yellow'
        elif post and hasattr(post, 'category') and post.category and hasattr(post.category, 'color'):
            primary_color = post.category.color
            progress_color = 'category'
        else:
            primary_color = 'var(--color-lavender)'
            progress_color = 'lavender'
    elif color == 'category' and post and hasattr(post, 'category') and post.category:
        primary_color = getattr(post.category, 'color', 'var(--color-lavender)')
        progress_color = 'category'
    else:
        primary_color = f'var(--color-{color})'
        progress_color = color

    # Calculate reading data (REUSE existing calculations)
    reading_data = {}
    if post:
        reading_data = {
            "total_reading_time": getattr(post, "reading_time", 0),
            "word_count": len(post.content.split()) if hasattr(post, "content") else 0,
            "target_element": "postContent",  # Standard post content ID
            "post_id": post.id,
        }

        # Fallback reading time calculation if not set
        if not reading_data["total_reading_time"] and reading_data["word_count"]:
            reading_data["total_reading_time"] = max(
                1, reading_data["word_count"] // 200
            )
    else:
        # Whole page tracking
        reading_data = {
            "total_reading_time": 0,
            "word_count": 0,
            "target_element": "body",
            "post_id": None,
        }
    # Build configuration for JavaScript (🔄 REUSE pattern from content_navigator)
    progress_config = {
        'id': f'reading-progress-{reading_data.get("post_id", "page")}',
        'target_element': reading_data['target_element'],
        'style': style,
        'position': position,
        'threshold': threshold,
        'smooth': smooth,
        'animate': animate,
        'show_percentage': show_percentage,
        'show_time': show_time,
        'show_position': show_position,
        'update_frequency': 50,  # ms
        'color': progress_color,
    }

    # Build CSS classes using existing patterns
    css_classes = [
        'reading-progress-indicator',
        f'progress-style-{style}',
        f'progress-position-{position}',
        f'progress-size-{size}',
        f'progress-color-{progress_color}',
    ]

    if animate:
        css_classes.append('progress-animated')
    if smooth:
        css_classes.append('progress-smooth')
    if responsive:
        css_classes.append('progress-responsive')
    if not show_percentage and not show_time:
        css_classes.append('progress-minimal')

    # Size configuration
    size_config = {
        'xs': {'height': '2px', 'circle_size': '30px', 'font_size': '0.7rem'},
        'sm': {'height': '3px', 'circle_size': '40px', 'font_size': '0.75rem'},
        'md': {'height': '4px', 'circle_size': '50px', 'font_size': '0.8rem'},
        'lg': {'height': '6px', 'circle_size': '60px', 'font_size': '0.9rem'},
        'xl': {'height': '8px', 'circle_size': '80px', 'font_size': '1rem'},
    }

    current_size_config = size_config.get(size, size_config['md'])

    return {
        'post': post,
        'style': style,
        'position': position,
        'size': size,
        'css_classes': ' '.join(css_classes),

        # Configuration
        'progress_config': progress_config,
        'reading_data': reading_data,
        'size_config': current_size_config,

        # Display settings
        'show_percentage': show_percentage,
        'show_time': show_time,
        'show_position': show_position,
        'animate': animate,
        'smooth': smooth,
        'responsive': responsive,

        # Theming (REUSE existing color system)
        'primary_color': primary_color,
        'progress_color': progress_color,
        'threshold': threshold,

        # Context
        'request': request,
    }


# Helper tags for reading progress


@register.simple_tag
def progress_time_display(elapsed_minutes=0, total_minutes=0, format_type="both"):
    """
    Format time display for reading progress.
    Usage: {% progress_time_display elapsed total 'remaining' %}
    """
    elapsed_time = format_duration(elapsed_minutes)
    total_time = format_duration(total_minutes)
    remaining_time = format_duration(max(0, total_minutes - elapsed_minutes))

    if format_type == "elapsed":
        return elapsed_time
    elif format_type == "remaining":
        return f"{remaining_time} left"
    elif format_type == "total":
        return total_time
    elif format_type == "both":
        return f"{elapsed_time} / {total_time}"
    elif format_type == "remaining_only":
        return remaining_time
    else:
        return f"{elapsed_time} of {total_time}"


@register.filter
def progress_color_for_percentage(percentage, thresholds="25,50,75"):
    """
    Get progress color based on completion percentage.
    Usage: {{ progress_percentage|progress_color_for_percentage }}
    """
    try:
        percentage = float(percentage)
        low, medium, high = map(float, thresholds.split(','))

        if percentage >= high:
            # Green for near completion
            return 'mint'
        elif percentage >= medium:
            # Teal for good progress
            return 'teal'
        elif percentage >= low:
            # Coral for started
            return 'coral'
        else:
            # Lavendar on load
            return 'lavender'
    except (ValueError, TypeError):
        return 'lavendar'


@register.simple_tag
def progress_motivation_message(percentage):
    """
    Generate motivational messages based on progress.
    Usage: {% progress_motivation_message 75 %}
    """
    try:
        percentage = float(percentage)

        if percentage >= 90:
            messages = [
                "Almost there! 🎉",
                "You're crushing it! 💪",
                "Final stretch! 🚀",
                "Nearly complete! ⭐",
            ]
        elif percentage >= 75:
            messages = [
                "Great progress! 🔥",
                "You're on fire! 💫",
                "Keep it up! 📈",
                "Awesome job! ⚡",
            ]
        elif percentage >= 50:
            messages = [
                "Halfway there! 🎯",
                "Making good time! ⏰",
                "Solid progress! 💎",
                "Keep going! 🌟",
            ]
        elif percentage >= 25:
            messages = [
                "Good start! 🌱",
                "Building momentum! 🔄",
                "Nice pace! 👍",
                "Making headway! 📊",
            ]
        else:
            messages = [
                "Let's dive in! 🏊‍♂️",
                "Just getting started! 🚀",
                "Ready to learn! 📚",
                "Adventure begins! 🗺️",
            ]

        import random

        return random.choice(messages)
    except (ValueError, TypeError):
        return "Let's go! 🚀"


@register.filter
def progress_json_config(config):
    """
    Convert progress configuration to JSON for JavaScript.
    Usage: {{ progress_config|progress_json_config }}
    """
    try:
        return mark_safe(json.dumps(config))
    except (TypeError, ValueError):
        return mark_safe("{}")


@register.simple_tag
def reading_session_stats(post=None):
    """
    Generate reading session statistics.
    Usage: {% reading_session_stats post as session_stats %}
    """
    stats = {
        "avg_reading_speed": 200,  # words per minute
        "difficulty_multiplier": 1.0,
        "estimated_breaks": 0,
        "focus_score": "High",
    }

    if post:
        # Calculate difficulty multiplier based on content
        if hasattr(post, "content") and post.content:
            # Check for code blocks (slower reading)
            code_blocks = count_code_blocks(post.content)
            if code_blocks > 0:
                stats["difficulty_multiplier"] = 1.0 + (code_blocks * 0.2)
                stats["avg_reading_speed"] = int(200 / stats["difficulty_multiplier"])
                stats["focus_score"] = "High (Technical)"

        # Calculate estimated breaks for longer content
        reading_time = getattr(post, "reading_time", 0)
        if reading_time > 15:
            stats["estimated_breaks"] = max(1, reading_time // 10)
            stats["focus_score"] = "Medium (Long Read)"
        elif reading_time > 30:
            stats["estimated_breaks"] = max(2, reading_time // 8)
            stats["focus_score"] = "Intensive"

    return stats


@register.filter
def progress_accessibility_label(style, percentage=0):
    """
    Generate accessibility labels for progress indicators.
    Usage: {{ 'bar'|progress_accessibility_label:percentage }}
    """
    style_labels = {
        "bar": "Reading progress bar",
        "circle": "Circular reading progress",
        "minimal": "Reading progress indicator",
        "floating": "Floating progress display",
        "sidebar": "Sidebar progress tracker",
        "corner": "Corner progress indicator",
    }

    base_label = style_labels.get(style, "Reading progress")

    if percentage > 0:
        return f"{base_label}: {percentage:.0f}% complete"
    else:
        return base_label


# ================= ENHANCED SEARCH SUGGESTIONS =================

@register.inclusion_tag('blog/includes/search_suggestions.html', takes_context=True)
def search_suggestions(
    context,
    query="",
    style="full",
    max_suggestions=8,
    show_icons=True,
    show_counts=True,
    show_descriptions=False,
    enable_ajax=True,
    group_by_type=True,
    include_recent=True,
    include_popular=True,
    debounce_delay=300,
    min_query_length=2,
    highlight_matches=True,
    position="below",
    width="auto",
    responsive=True,
):
    """
    STREAMLINED enhanced search suggestions using existing AURA components.

    Usage Examples:
    {% search_suggestions query style='full' %}
    {% search_suggestions query style='compact' max_suggestions=5 %}
    {% search_suggestions query style='minimal' show_icons=False %}
    {% search_suggestions query style='dropdown' position='overlay' %}
    {% search_suggestions query style='sidebar' enable_ajax=False %}

    Args:
        query (str): Current search query
        style (str): Display style - 'full', 'compact', 'minimal', 'dropdown', 'sidebar'
        max_suggestions (int): Maximum number of suggestions to show
        show_icons (bool): Show type icons for suggestions
        show_counts (bool): Show result counts
        show_descriptions (bool): Show suggestion descriptions
        enable_ajax (bool): Enable real-time AJAX suggestions
        group_by_type (bool): Group suggestions by type (posts, categories, tags)
        include_recent (bool): Include recent searches
        include_popular (bool): Include popular searches when no query
        debounce_delay (int): AJAX debounce delay in milliseconds
        min_query_length (int): Minimum query length for suggestions
        highlight_matches (bool): Highlight matching text
        position (str): Position relative to search input - 'below', 'overlay', 'sidebar'
        width (str): Width of suggestions panel - 'auto', 'full', 'fixed'
        responsive (bool): Enable responsive behavior
    """
    request = context.get("request")

    # REUSE: Get suggestions using existing function
    if len(query) >= min_query_length:
        suggestions_data = datalog_search_suggestions(query)
    elif include_popular:
        # REUSE: Get popular items when no query
        suggestions_data = []

        # Add popular categories
        popular_categories = get_datalog_categories(popular_only=True)
        for cat in popular_categories[:3]:
            suggestions_data.append(
                {
                    "text": f"{cat.name} Category",
                    "type": "category",
                    "icon": getattr(cat, "icon", "fas fa-folder"),
                    "url": cat.get_absolute_url()
                    if hasattr(cat, "get_absolute_url")
                    else "#",
                    "count": getattr(cat, "post_count", 0),
                    "description": f"{getattr(cat, 'post_count', 0)} posts",
                }
            )

        # Add popular tags
        popular_tags = get_popular_tags(5)
        for tag in popular_tags[:3]:
            suggestions_data.append(
                {
                    "text": f"#{tag.name}",
                    "type": "tag",
                    "icon": "fas fa-tag",
                    "url": tag.get_absolute_url()
                    if hasattr(tag, "get_absolute_url")
                    else "#",
                    "count": getattr(tag, "post_count", 0),
                    "description": f"{getattr(tag, 'post_count', 0)} posts",
                }
            )

        # Add recent popular searches
        if include_recent:
            suggestions_data.extend(
                [
                    {
                        "text": "Machine Learning",
                        "type": "topic",
                        "icon": "fas fa-brain",
                        "url": "#",
                    },
                    {
                        "text": "Python Development",
                        "type": "topic",
                        "icon": "fab fa-python",
                        "url": "#",
                    },
                ]
            )
    else:
        suggestions_data = []

    # Limit to max suggestions
    suggestions_data = suggestions_data[:max_suggestions]

    # Group by type if requested
    grouped_suggestions = {}
    if group_by_type and suggestions_data:
        for suggestion in suggestions_data:
            suggestion_type = suggestion.get("type", "other")
            if suggestion_type not in grouped_suggestions:
                grouped_suggestions[suggestion_type] = []
            grouped_suggestions[suggestion_type].append(suggestion)

    # Get search context
    search_context = {
        'total_posts': Post.objects.filter(status='published').count(),
        'total_categories': Category.objects.count(),
        'total_tags': Tag.objects.count(),
    }

    # AJAX configuration
    ajax_config = (
        {
            "enabled": enable_ajax,
            "url": reverse("blog:search_ajax") if enable_ajax else None,  # Fallback URL
            "debounce_delay": debounce_delay,
            "min_query_length": min_query_length,
            "highlight_matches": highlight_matches,
        }
        if enable_ajax
        else {}
    )

    # Build CSS classes
    css_classes = [
        "search-suggestions-container",
        f"suggestions-style-{style}",
        f"suggestions-position-{position}",
        f"suggestions-width-{width}",
    ]

    if enable_ajax:
        css_classes.append("suggestions-ajax-enabled")
    if group_by_type:
        css_classes.append("suggestions-grouped")
    if responsive:
        css_classes.append("suggestions-responsive")
    if highlight_matches:
        css_classes.append("suggestions-highlight")

    # Type config for icons and styling
    type_config = {
        'post': {
            'icon': 'fas fa-file-alt',
            'label': 'Posts',
            'color': 'var(--color-lavender)',
            'priority': 1,
        },
        'category': {
            'icon': 'fas fa-folder',
            'label': 'Categories',
            'color': 'var(--color-teal)',
            'priority': 2,
        },
        'tag': {
            'icon': 'fas fa-lightbulb',
            'label': 'Tags',
            'color': 'var(--color-coral)',
            'priority': 3,
        },
        'topic': {
            'icon': 'fas fa-lightbulb',
            'label': 'Topics',
            'color': 'var(--color-mint)',
            'priority': 4,
        },
        'system': {
            'icon': 'fas fa-project-diagram',
            'label': 'Systems',
            'color': 'var(--color-yellow)',
            'priority': 5,
        },
    }

    # Generate search analytics
    search_analytics = {
        'query_length': len(query),
        'suggestion_count': len(suggestions_data),
        'has_results': len(suggestions_data) > 0,
        'query_type': 'search' if query else 'browse',
        'grouped_count': len(grouped_suggestions) if group_by_type else 0,
    }

    return {
        "query": query,
        "style": style,
        "position": position,
        "width": width,
        "css_classes": " ".join(css_classes),

        # Suggestion data (REUSED from existing functions)
        "suggestions": suggestions_data,
        "grouped_suggestions": grouped_suggestions,
        "group_by_type": group_by_type,

        # Configuration
        "max_suggestions": max_suggestions,
        "show_icons": show_icons,
        "show_counts": show_counts,
        "show_descriptions": show_descriptions,
        "highlight_matches": highlight_matches,
        "responsive": responsive,

        # AJAX (REUSES existing patterns)
        "enable_ajax": enable_ajax,
        "ajax_config": ajax_config,
        "debounce_delay": debounce_delay,
        "min_query_length": min_query_length,

        # Context (REUSED from existing functions)
        "search_context": search_context,
        "type_config": type_config,
        "search_analytics": search_analytics,

        # Request context
        "request": request,
    }


# Helper tags for search suggestions
@register.filter
def search_suggestion_highlight(text, query):
    """
    Highlight matching text in search suggestions.
    Usage: {{ suggestion.text|search_suggestion_highlight:query }}
    """
    if not query or not text:
        return text

    # REUSE: Use existing highlight_search filter
    return highlight_search(text, query)


@register.filter
def suggestion_relevance_score(suggestion, query):
    """
    Calculate relevance score for suggestion sorting.
    Usage: {{ suggestion|suggestion_relevance_score:query }}
    """
    if not query:
        return 0

    text = suggestion.get('text', '').lower()
    query_lower = query.lower()

    score = 0

    # Exact match gets highest score
    if text == query_lower:
        score += 100

    # Starts with query gets high score
    elif text.startswith(query_lower):
        score += 50

    # Contain query gets medium score
    elif query_lower in text:
        score += 25

    # Add type priority bonus (posts > categories > tags) may reorder
    type_priority = {
        'post': 10,
        'category': 8,
        'tag': 6,
        'topic': 4,
        'system': 2,
    }
    score += type_priority.get(suggestion.get('type', ''), 0)

    # Add count bonus for popular items
    count = suggestion.get('count', 0)
    if count > 0:
        # Max 10 bonus points
        score += min(10, count // 5)

    return score

@register.simple_tag
def search_quick_actions(query=''):
    """
    Generate quick action suggestions for search.
    Usage: {% search_quick_actions query as quick_actions %}
    """
    actions = []

    if query:
        # Add search in specific contexts
        actions.extend([
            {
                'text': f"Search logs for '{query}'",
                'url': f"{reverse('blog:post_list')}?q={query}",
                'icon': "fas fa-search",
                'type': "action",
            },
            {
                'text': f"Search in category",
                'url': f"{reverse('blog:search')}?q={query}&type=category",
                'icon': "fas fa-folder-open",
                'type': "action",
            },
        ])
    else:
        # Default Quick Actions
        actions.extend(
            [
                {
                    "text": "Browse all posts",
                    "url": reverse("blog:post_list"),
                    "icon": "fas fa-list",
                    "type": "action",
                },
                {
                    "text": "View archive",
                    "url": reverse("blog:archive") if reverse("blog:archive") else "#",
                    "icon": "fas fa-archive",
                    "type": "action",
                },
                {
                    "text": "Popular tags",
                    "url": reverse("blog:post_list") + "?popular=tags",
                    "icon": "fas fa-tags",
                    "type": "action",
                },
            ]
        )

    return actions


@register.simple_tag
def search_performance_hints(suggestion_count, query_length):
    """
    Generate performance hints for search optimization.
    Usage: {% search_performance_hints suggestion_count query_length as hints %}
    """
    hints = []

    if query_length < 3:
        hints.append({
            'type': 'tip',
            'message': 'Type at least 3 characters for better results',
            'icon': 'fas fa-info-circle',
        })

    if suggestion_count == 0:
        hints.append({
            'type': 'help',
            'message': 'Try shorter keywords or browse categories',
            'icon': 'fas fa-lightbulb',
        })

    elif suggestion_count > 20:
        hints.append({
            'type': 'tip',
            'message': 'Too many results - narrow parameters',
            'icon': 'fas fa-funnel-dollar',
        })

    return hints


@register.filter
def search_suggestion_preview(suggestion):
    """
    Generate preview content for suggestion hover.
    Usage: {{ suggestion|search_suggestion_preview }}
    """
    preview = {
        "title": suggestion.get("text", ""),
        "type": suggestion.get("type", "").title(),
        "description": suggestion.get("description", ""),
        "url": suggestion.get("url", "#"),
    }

    # Add type-specific preview enhancements
    suggestion_type = suggestion.get("type", "")

    if suggestion_type == "post":
        preview["preview_text"] = "Click to access this log"
    elif suggestion_type == "category":
        count = suggestion.get("count", 0)
        preview["preview_text"] = f"Browse {count} entries in this category"
    elif suggestion_type == "tag":
        count = suggestion.get("count", 0)
        preview["preview_text"] = f"View {count} entries with this tag"
    else:
        preview["preview_text"] = "Click to view"

    return preview


# ================= DATALOG FILTERS PANEL =================

@register.inclusion_tag("blog/includes/datalog_filters_panel.html", takes_context=True)
def datalog_filters_panel(
    context,
    style="sidebar",
    position="right",
    show_categories=True,
    show_tags=True,
    show_dates=True,
    show_reading_time=True,
    show_difficulty=False,
    show_status=False,
    show_featured=True,
    show_search=True,
    show_sorting=True,
    show_view_options=True,
    collapsible=True,
    responsive=True,
    max_categories=None,
    max_tags=15,
    enable_multi_select=True,
    show_counts=True,
    auto_apply=False,
    reset_option=True,
):
    """
    STREAMLINED comprehensive filtering panel using existing AURA components.

    Usage Examples:
    {% datalog_filters_panel style='sidebar' position='right' %}
    {% datalog_filters_panel style='horizontal' show_difficulty=True %}
    {% datalog_filters_panel style='compact' max_tags=10 %}
    {% datalog_filters_panel style='modal' collapsible=False %}
    {% datalog_filters_panel style='floating' auto_apply=True %}

    Args:
        style (str): Panel style - 'sidebar', 'horizontal', 'compact', 'modal', 'floating'
        position (str): Panel position - 'left', 'right', 'top', 'bottom'
        show_categories (bool): Show category filters
        show_tags (bool): Show tag filters  
        show_dates (bool): Show date range filters
        show_reading_time (bool): Show reading time filters
        show_difficulty (bool): Show difficulty level filters
        show_status (bool): Show post status filters
        show_featured (bool): Show featured filter
        show_search (bool): Show search input
        show_sorting (bool): Show sorting options
        show_view_options (bool): Show view mode toggles
        collapsible (bool): Make filter sections collapsible
        responsive (bool): Enable responsive behavior
        max_categories (int): Limit displayed categories (None = all)
        max_tags (int): Limit displayed tags
        enable_multi_select (bool): Allow multiple selections
        show_counts (bool): Show post counts for filters
        auto_apply (bool): Auto-apply filters without submit button
        reset_option (bool): Show reset/clear filters option
    """

    request = context.get("request")
    current_params = request.GET.copy() if request else {}

    # REUSE: Get filter data using existing functions
    filter_data = {}

    if show_categories:
        # REUSE: Get categories with counts
        categories = get_datalog_categories()
        if max_categories:
            categories = categories[:max_categories]
        filter_data['categories'] = categories

    if show_tags:
        # REUSE: Get popular tags
        tags = get_popular_tags(max_tags)
        filter_data['tags'] = tags

    if show_dates:
        # REUSE: Get date ranges using existing patterns
        filter_data['date_ranges'] = get_date_filter_ranges()
        filter_data['archive_years'] = archive_years()

    if show_reading_time:
        filter_data['reading_time_ranges'] = [
            {'value': '0-5', 'label': 'Quick Read (0-5 min)', 'icon': 'fas fa-bolt'},
            {'value': '5-15', 'label': 'Medium Read (5-15 min)', 'icon': 'fas fa-book'},
            {'value': '15+', 'label': 'Long Read (15+ min)', 'icon': 'fas fa-book-open'},
        ]

    if show_difficulty:
        filter_data['difficulty_levels'] = [
            {'value': 'Beginner', 'label': 'Beginner', 'icon': 'fas fa-leaf', 'color': 'var(--color-mint)'},
            {'value': 'Intermediate', 'label': 'Intermediate', 'icon': 'fas fa-fire', 'color': 'var(--color-coral)'},
            {'value': 'Advanced', 'label': 'Advanced', 'icon': 'fas fa-bolt', 'color': 'var(--color-yellow)'},
        ]

    if show_status:
        filter_data['status_options'] = [
            {'value': 'published', 'label': 'Published', 'icon': 'fas fa-check', 'color': 'var(--color-mint)'},
            {'value': 'draft', 'label': 'Draft', 'icon': 'fas fa-edit', 'color': 'var(--color-coral)'},
        ]

    # Sorting options
    if show_sorting:
        filter_data['sort_options'] = [
            {'value': 'newest', 'label': 'Newest First', 'icon': 'fas fa-sort-amount-down'},
            {'value': 'oldest', 'label': 'Oldest First', 'icon': 'fas fa-sort-amount-up'},
            {'value': 'title', 'label': 'Title A-Z', 'icon': 'fas fa-sort-alpha-down'},
            {'value': 'reading-time', 'label': 'Reading Time', 'icon': 'fas fa-clock'},
            {'value': 'category', 'label': 'By Category', 'icon': 'fas fa-folder'},
        ]

    # View options
    if show_view_options:
        filter_data['view_options'] = [
            {'value': 'grid', 'label': 'Grid View', 'icon': 'fas fa-th'},
            {'value': 'list', 'label': 'List View', 'icon': 'fas fa-list'},
            {'value': 'timeline', 'label': 'Timeline View', 'icon': 'fas fa-stream'},
        ]

    # Current filter state (REUSE existing patterns)
    current_filters = extract_current_filters(current_params)

    # Filter statistics (REUSE existing stats)
    filter_stats = calculate_filter_statistics(filter_data, current_filters)

    # Build CSS classes
    css_classes = [
        "datalog-filters-panel",
        f"filters-style-{style}",
        f"filters-position-{position}",
    ]

    if collapsible:
        css_classes.append("filters-collapsible")
    if responsive:
        css_classes.append("filters-responsive")
    if auto_apply:
        css_classes.append("filters-auto-apply")
    if enable_multi_select:
        css_classes.append("filters-multi-select")

    # Panel configuration for JavaScript
    panel_config = {
        "id": "datalogFiltersPanel",
        "style": style,
        "position": position,
        "auto_apply": auto_apply,
        "multi_select": enable_multi_select,
        "collapsible": collapsible,
        "form_selector": "#filterForm",
        "target_container": "#datalogResults",
    }

    return {
        "style": style,
        "position": position,
        "css_classes": " ".join(css_classes),

        # Filter data (REUSED from existing functions)
        "filter_data": filter_data,
        "current_filters": current_filters,
        "filter_stats": filter_stats,

        # Feature flags
        "show_categories": show_categories,
        "show_tags": show_tags,
        "show_dates": show_dates,
        "show_reading_time": show_reading_time,
        "show_difficulty": show_difficulty,
        "show_status": show_status,
        "show_featured": show_featured,
        "show_search": show_search,
        "show_sorting": show_sorting,
        "show_view_options": show_view_options,
        "show_counts": show_counts,

        # Configuration
        "collapsible": collapsible,
        "responsive": responsive,
        "max_categories": max_categories,
        "max_tags": max_tags,
        "enable_multi_select": enable_multi_select,
        "auto_apply": auto_apply,
        "reset_option": reset_option,
        "panel_config": panel_config,

        # Context
        "request": request,
        "current_params": current_params,
    }


# Helper functions for filters panel
def get_date_filter_ranges():
    """Generate date filter ranges for the panel."""
    return [
        {"value": "today", "label": "Today", "icon": "fas fa-calendar-day"},
        {"value": "week", "label": "This Week", "icon": "fas fa-calendar-week"},
        {"value": "month", "label": "This Month", "icon": "fas fa-calendar-alt"},
        {"value": "quarter", "label": "This Quarter", "icon": "fas fa-calendar"},
        {"value": "year", "label": "This Year", "icon": "fas fa-calendar"},
        {"value": "custom", "label": "Custom Range", "icon": "fas fa-calendar-plus"},
    ]


def extract_current_filters(params):
    """Extract current filter state from request parameters."""
    filters = {
        "categories": params.getlist("category", []),
        "tags": params.getlist("tag", []),
        "date_range": params.get("date_range", ""),
        "reading_time": params.get("reading_time", ""),
        "difficulty": params.get("difficulty", ""),
        "status": params.get("status", ""),
        "featured": params.get("featured", "") == "true",
        "sort": params.get("sort", "newest"),
        "view": params.get("view", "grid"),
        "search": params.get("q", ""),
    }

    # Count active filters
    active_count = 0
    for key, value in filters.items():
        if isinstance(value, list) and value:
            active_count += len(value)
        # Don't count default sort/view
        elif value and key != 'sort' and key != 'view':
            active_count += 1

    filters['active_count'] = active_count
    filters['has_active'] = active_count > 0

    return filters


def calculate_filter_statistics(filter_data, current_filters):
    """Calculate statistics for the filter panel."""
    stats = {
        "total_categories": len(filter_data.get("categories", [])),
        "total_tags": len(filter_data.get("tags", [])),
        "active_filters": current_filters.get("active_count", 0),
        "available_posts": 0,  # Would be calculated from actual query
    }

    # Calculate potential results (simplified)
    if current_filters.get('has_active'):
        stats['filter_mode'] = 'filtered'
        # Would be from actual query
        stats['estimated_results'] = 'Calculating...'
    else:
        stats['filter_mode'] = 'browse'
        # REUSE: Get total from existing stats
        blog_stats = datalog_stats()
        stats['estimated_results'] = blog_stats.get('total_posts', 0)

    return stats

# Helper tags for filters panel
@register.simple_tag
def filter_category_color_vars(category):
    """
    Generate CSS variables for category filter styling.
    Usage: {% filter_category_color_vars category %}
    """
    if not category:
        return ""

    # REUSE: Use existing category color scheme
    color_scheme = category_color_scheme(category)

    vars_list = []
    for key, value in color_scheme.items():
        vars_list.append(f"--filter-{key}: {value};")

    return mark_safe(" ".join(vars_list))


@register.filter
def filter_count_display(count):
    """
    Format filter counts for display.
    Usage: {{ category.post_count|filter_count_display }}
    """
    if not count:
        return ""

    # REUSE: Use existing format_number filter
    return f"({format_number(count)})"


@register.simple_tag
def build_filter_url(current_params, **new_filters):
    """
    Build URL with updated filter parameters.
    Usage: {% build_filter_url current_params category='ml' %}
    """
    # REUSE: Use existing build_url pattern
    params = current_params.copy()

    for key, value in new_filters.items():
        if value is None or value == "":
            params.pop(key, None)
        elif key in ["category", "tag"] and params.get(key):
            # Handle multi-select for categories/tags
            current_values = params.getlist(key)
            if value in current_values:
                current_values.remove(value)
            else:
                current_values.append(value)

            if current_values:
                params.setlist(key, current_values)
            else:
                params.pop(key, None)
        else:
            params[key] = value

    # Remove page when filters change
    params.pop("page", None)

    return f"?{params.urlencode()}" if params else ""


@register.filter
def is_filter_active(current_filters, filter_key):
    """
    Check if a filter is currently active.
    Usage: {{ current_filters|is_filter_active:'featured' }}
    """
    return current_filters.get(filter_key) not in [None, "", [], False]


@register.simple_tag
def filter_reset_url(current_params, keep_search=True):
    """
    Generate URL to reset all filters.
    Usage: {% filter_reset_url current_params keep_search=False %}
    """
    if keep_search and current_params.get("q"):
        return f"?q={current_params.get('q')}"
    return "?"


@register.filter
def filter_option_class(option, current_value):
    """
    Get CSS class for filter option based on current state.
    Usage: {{ option|filter_option_class:current_filters.sort }}
    """
    is_active = option.get("value") == current_value
    base_class = "filter-option"

    if is_active:
        base_class += " active"

    return base_class


@register.simple_tag
def filter_summary_text(current_filters, filter_stats):
    """
    Generate human-readable filter summary.
    Usage: {% filter_summary_text current_filters filter_stats %}
    """
    active_count = current_filters.get("active_count", 0)

    if active_count == 0:
        return f"Showing all {filter_stats.get('estimated_results', 0)} posts"
    elif active_count == 1:
        return f"1 filter applied • {filter_stats.get('estimated_results', 'Loading')} results"
    else:
        return f"{active_count} filters applied • {filter_stats.get('estimated_results', 'Loading')} results"

@register.filter
def json_config(config):
    """
    Convert configuration to JSON for JavaScript.
    Usage: {{ panel_config|json_config }}
    """
    try:
        return mark_safe(json.dumps(config))
    except (TypeError, ValueError):
        return mark_safe("{}")

# ================= UNIFIED SEARCH INTERFACE =================


@register.inclusion_tag('blog/includes/unified_search_interface.html', takes_context=True)
def unified_search_interface(
    context,
    query="",
    style="full",
    show_quick_filters=True,
    enable_ajax=True,
    placeholder="Search DataLog entries, code snippets, and technical insights...",
    max_suggestions=6,
    debounce_delay=300,
    show_stats=True,
):
    """
    UNIFIED search interface that combines search bar + suggestions + filters.
    This replaces both enhanced_search_interface and search_suggestions.

    Usage Examples:
    {% unified_search_interface query=query %}
    {% unified_search_interface query=query style='compact' %}
    {% unified_search_interface query=query show_quick_filters=False %}

    Args:
        query (str): Current search query
        style (str): Display style - 'full', 'compact', 'minimal'
        show_quick_filters (bool): Show quick filter tags
        enable_ajax (bool): Enable real-time suggestions
        placeholder (str): Custom placeholder text
        max_suggestions (int): Max suggestions to show
        debounce_delay (int): AJAX delay in milliseconds
        show_stats (bool): Show search statistics when there's a query
    """
    request = context.get('request')

    # Get search results count if query
    search_results_count = 0
    if query:
        try:
            search_results_count = Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                status='published'
            ).count()
        except:
            search_results_count = 0

    # Build AJAX config
    ajax_config = {
        "enabled": enable_ajax,
        "url": reverse("blog:search_ajax") if enable_ajax else None,
        "debounce_delay": debounce_delay,
        "max_suggestions": max_suggestions,
    } if enable_ajax else {}

    return {
        "query": query,
        "style": style,
        "show_quick_filters": show_quick_filters,
        "enable_ajax": enable_ajax,
        "placeholder": placeholder,
        "show_stats": show_stats,
        "search_results_count": search_results_count,
        "ajax_config": ajax_config,
        "request": request,
    }


@register.simple_tag
def search_ajax_suggestions(query, max_results=6):
    """
    Generate AJAX search suggestions for real-time search.
    Used by the JavaScript to get suggestions via AJAX.

    Usage: Called by AJAX endpoint
    """
    suggestions = []

    if not query or len(query) < 2:
        # Return popular/recent items when no query
        return [
            {
                "text": "Machine Learning",
                "type": "topic",
                "icon": "fas fa-brain",
                "url": "#",
            },
            {
                "text": "Python Development",
                "type": "topic",
                "icon": "fab fa-python",
                "url": "#",
            },
            {"text": "API Design", "type": "topic", "icon": "fas fa-plug", "url": "#"},
            {
                "text": "Database",
                "type": "topic",
                "icon": "fas fa-database",
                "url": "#",
            },
            {
                "text": "Neural Networks",
                "type": "topic",
                "icon": "fas fa-project-diagram",
                "url": "#",
            },
        ]
    try:
        query_lower = query.lower()

        # Search in posts
        matching_posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published',
        ).order_by('-published_date')[:3]

        for post in matching_posts:
            suggestions.append({
                'text': post.title,
                'type': 'post',
                'icon': 'fas fa-file-alt',
                'url': post.get_absolute_url(),
                'description': f"Published {post.published_date.strftime('%b %d, %Y')}" if post.published_date else ""
            })

        # Search in categories
        matching_categories = Category.objects.filter(
            name__icontains=query
        )[:2]

        for category in matching_categories:
            post_count = category.posts.filter(status='published').count()
            suggestions.append({
                'text': f"{category.name} Category",
                'type': 'category',
                'icon': getattr(category, 'icon', 'fas fa-folder'),
                'url': category.get_absolute_url() if hasattr(category, 'get_absolute_url') else f"/datalogs/category/{category.slug}/",
                'description': f"{post_count} post{'s' if post_count != 1 else ''}"
            })

        # Search in tags
        matching_tags = Tag.objects.filter(
            name__icontains=query
        ).annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0)[:2]

        for tag in matching_tags:
            suggestions.append({
                'text': f"#{tag.name}",
                'type': 'tag',
                'icon': 'fas fa-tag',
                'url': tag.get_absolute_url() if hasattr(tag, 'get_absolute_url') else f"/datalogs/tag/{tag.slug}/",
                'description': f"{tag.post_count} post{'s' if tag.post_count != 1 else ''}"
            })

        # Add topic suggestions based on content
        if "python" in query_lower:
            suggestions.append(
                {
                    "text": "Python Development",
                    "type": "topic",
                    "icon": "fab fa-python",
                    "url": f"/datalogs/search/?q=python",
                    "description": "Programming and development",
                }
            )

        if any(term in query_lower for term in ["ml", "machine", "learning", "ai"]):
            suggestions.append(
                {
                    "text": "Machine Learning",
                    "type": "topic",
                    "icon": "fas fa-brain",
                    "url": f"/datalogs/search/?q=machine+learning",
                    "description": "AI and ML concepts",
                }
            )

        if any(term in query_lower for term in ["api", "rest", "endpoint"]):
            suggestions.append(
                {
                    "text": "API Development",
                    "type": "topic",
                    "icon": "fas fa-plug",
                    "url": f"/datalogs/search/?q=api",
                    "description": "API design and development",
                }
            )

    except Exception as e:
        # Log error in production, return empty for now
        pass

    return suggestions[:max_results]


@register.simple_tag
def search_performance_metrics(query):
    """
    Generate search performance metrics for analytics.
    Usage: {% search_performance_metrics query as metrics %}
    """
    if not query:
        return {}

    try:
        start_time = timezone.now()

        # Get basic search results
        results = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query),
            status='published'
        )

        total_results = results.count()

        # Calculate metrics
        end_time = timezone.now()
        # Calculate, convert to ms
        search_time = (end_time - start_time).total_seconds() * 1000

        return {
            'query': query,
            'total_results': total_results,
            'search_time_ms': round(search_time, 2),
            'has_results': total_results > 0,
            'query_length': len(query),
            'word_count': len(query.split()),
        }
    except Exception:
        return {
            'query': query,
            'total_results': 0,
            'search_time_ms': 0,
            'has_results': False,
            'query_length': len(query),
            'word_count': len(query.split()),
        }


# Replacing w global highlight_search in aura_filters
# Just leaving here for ref until entire search comp done
# @register.filter
# def highlight_search_term(text, query):
#     pass

# Replace/combine w build_url later?
@register.simple_tag
def search_url_builder(**kwargs):
    """
    Build search URLs with parameters.
    Usage: {% search_url_builder q="python" category="dev" %}
    """
    # Filter out empty values
    params = {k: v for k, v in kwargs.items() if v}

    base_url = reverse('blog:search')
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url


@register.simple_tag
def popular_search_terms(limit=5):
    """
    Get popular search terms based on content analysis.
    Usage: {% popular_search_terms as popular_terms %}
    """
    # TODO: In real implementation, track actual search queries
    # For now, return popular topics based on your content

    popular_terms = [
        {
            "term": "Machine Learning",
            "count": 15,
            "url": "/datalogs/search/?q=machine+learning",
        },
        {"term": "Python", "count": 23, "url": "/datalogs/search/?q=python"},
        {"term": "API Development", "count": 12, "url": "/datalogs/search/?q=api"},
        {"term": "Database", "count": 8, "url": "/datalogs/search/?q=database"},
        {
            "term": "Neural Networks",
            "count": 6,
            "url": "/datalogs/search/?q=neural+networks",
        },
        {"term": "Django", "count": 18, "url": "/datalogs/search/?q=django"},
        {"term": "Data Analysis", "count": 10, "url": "/datalogs/search/?q=data+analysis"},
    ]

    return popular_terms[:limit]
