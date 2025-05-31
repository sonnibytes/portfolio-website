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
from django.db.models import Count, Q, Avg

from datetime import datetime, timedelta
import re
import json

from bs4 import BeautifulSoup
from markdownx.utils import markdownify as md
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from ..models import Post, Category, Tag

register = template.Library()


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


# ========== DATALOG TEMPLATE TAGS ==========


# Formerly blog_stats
@register.simple_tag
def datalog_stats():
    """
    Generate DataLog statistics for dashboard display
    Usage: {% datalog_stats %}
    """
    try:
        total_posts = Post.objects.filter(status="published").count()
        total_categories = Category.objects.count()
        total_tags = Tag.objects.count()
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
def get_datalog_categories(popular_only=False):
    """
    Get post count by category sorted by post count
    Usage: {% get_datalog_categories %}
    """
    try:
        categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by("-post_count")

        if popular_only:
            return categories[:5]
        return categories
    except Exception:
        return []


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

# Enhanced and Fixed Color Scheme and Glow for Category Hexes
@register.filter
def category_color_scheme(category):
    """
    Generate comprehensive color scheme for category display with proper RGBA conversion
    Usage: {% with color_scheme=category|category_color_scheme %}
    """
    if not category:
        return {
            "primary": "#26c6da",
            "secondary": "rgba(38, 198, 218, 0.1)",
            "glow": "rgba(38, 198, 218, 0.4)"
        }

    # Get primary color from category
    primary_color = getattr(category, 'color', '#26c6da')

    # Ensure color starts with #
    if not primary_color.startswith('#'):
        primary_color = '#' + primary_color

    # Convert hex to RGB for RGBA calculations
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            try:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                # Fallback to teal
                return (38, 198, 218)
        # Fallback to Teal
        return (38, 198, 218)

    try:
        r, g, b = hex_to_rgb(primary_color)

        # Generate comprehensive color scheme
        color_scheme = {
            'primary': primary_color,
            'secondary': f'rgba({r}, {g}, {b}, 0.1)',
            'glow': f'rgba({r}, {g}, {b}, 0.4)',
            'border': f'rgba({r}, {g}, {b}, 0.3)',
            'hover': f'rgba({r}, {g}, {b}, 0.2)',
            'active': f'rgba({r}, {g}, {b}, 0.15)',
            'shadow': f'rgba({r}, {g}, {b}, 0.25)',
            'text': primary_color,
            # Additional utility colors
            'rgb': f'{r}, {g}, {b}',
            'light': f'rgba({r}, {g}, {b}, 0.05)',
            'medium': f'rgba({r}, {g}, {b}, 0.2)',
            'strong': f'rgba({r}, {g}, {b}, 0.6)',
        }

        return color_scheme

    except Exception:
        # Fallback to color scheme if anything goes wrong
        return {
            "primary": "#26c6da",
            "secondary": "rgba(38, 198, 218, 0.1)",
            "glow": "rgba(38, 198, 218, 0.4)",
            "border": "rgba(38, 198, 218, 0.3)",
            "hover": "rgba(38, 198, 218, 0.2)",
            "active": "rgba(38, 198, 218, 0.15)",
            "shadow": "rgba(38, 198, 218, 0.25)",
            "text": "#26c6da",
            "rgb": "38, 198, 218",
            "light": "rgba(38, 198, 218, 0.05)",
            "medium": "rgba(38, 198, 218, 0.2)",
            "strong": "rgba(38, 198, 218, 0.6)",
        }


@register.filter
def hex_to_rgba(hex_color, alpha=1.0):
    """
    Convert hex color to RGBA
    Usage: {{ "#ff0000"|hex_to_rgba:0.5 }}
    """
    if not hex_color or not hex_color.startswith('#'):
        return f"rgba(38, 198, 218, {alpha})"

    try:
        hex_color = hex_color.lstrip('#')

        # Convert hex to rgb and add alpha
        if len(hex_color) == 6:  # rrggbb format
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"

    except ValueError:
        pass

    return f"rgba(38, 198, 218, {alpha})"


@register.simple_tag
def generate_category_css_vars(category):
    """
    Generate CSS custom properties for a category
    Usage: {% generate_category_css_vars category %}
    """
    color_scheme = category_color_scheme(category)

    css_vars = []
    for key, value in color_scheme.items():
        css_vars.append(f"--category-{key}: {value};")

    return mark_safe(' '.join(css_vars))


@register.filter
def adjust_color_brightness(hex_color, factor=1.2):
    """
    Adjust the brightness of a hex color
    Usage: {{ "#ff0000"|adjust_color_brightness:1.5 }}
    factor > 1 makes it brighter, < 1 makes it darker
    """
    if not hex_color or not hex_color.startswith('#'):
        return hex_color

    try:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Adjust brightness
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))

            return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        pass

    return hex_color


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


# =========== Enhanced Inclusion Tags (added w rework to combine various tag files) =========== #

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

# =========== Enhanced Filters (added w rework to combine various tag files) =========== #

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
    Returns years that have published posts.
    Usage: {% archive_years %}
    """
    return Post.objects.filter(
        status='published'
    ).dates('published_date', 'year', order='DESC')


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


# =========== Markdown (Markdownx - bs4) Filter (formerly markdown_filters) =========== #

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

        # Set the ID attribute on the heading element
        heading["id"] = heading_id

    # Return modified HTML
    return mark_safe(str(soup))

# =========== Code Formating (Pygments) Filter (formerly code_filters) =========== #

# Register a new filter named 'highlight_code'
@register.filter(name="highlight_code")
# Mark the function as a string filter (operates on strings)
@stringfilter
def highlight_code(code, language=None):
    try:
        # If a language is specified, get the appropriate lexer
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        # Otherwise, use a simple text lexer with no highlighting
        else:
            lexer = TextLexer()

        # Create an HTML formatter with a 'monokai' style
        # This is a dark style that works well with your theme
        # 'cssclass' sets the CSS class that will be applied to the wrapper
        formatter = HtmlFormatter(style="monokai", cssclass="highlighted")

        # Perform the actual highlighting
        # This takes the code string, lexer for parsing, and formatter for output
        # Returns HTML with appropriate spans for syntax highlighting
        highlighted_code = highlight(code, lexer, formatter)

        # Mark the output as safe for rendering in the template
        # This tells Django not to escape the HTML tags in the output
        return mark_safe(highlighted_code)
    except:
        # If any error occurs, return the original code unchanged
        # This provides a fallback if Pygments can't handle the code
        return code


# Register a simple tag to generate CSS for Pygments
@register.simple_tag
def pygments_css():
    # Create a formatter to get CSS rules
    formatter = HtmlFormatter(style="monokai")

    # Get CSS style definitions for the specified style
    # 'get_style_defs()' returns CSS rules for the given selector
    # '.highlighted' matches the cssclass we set in highlight_code
    css_rules = formatter.get_style_defs(".highlighted")

    # Wrap the CSS in a style tag and mark it as safe for rendering
    return mark_safe(f"<style>{css_rules}</style>")


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


# @register.simple_tag
# def datalog_status_badge(post):
#     """Generate status badge for datalog posts"""
#     if post.featured:
#         return mark_safe('<span class="datalog-badge featured">Featured</span>')
#     elif post.created > timezone.now() - timedelta(days=7):
#         return mark_safe('<span class="datalog-badge new">New</span>')
#     else:
#         return ""

# Combined w popular_datalog_categories into one get_datalog_categories function
# @register.simple_tag
# def get_post_count_by_category():
#     """
#     Returns post count grouped by category.
#     Usage: {% get_post_count_by_category %}
#     """
#     return Category.objects.annotate(
#         post_count=Count("posts", filter=Q(posts__status="published"))
#     ).filter(post_count__gt=0)

# # Combined w get_post_by_category into one get_datalog_categories function
# @register.simple_tag
# def popular_datalog_categories(limit=5):
#     """
#     Get most popular categories by post count
#     Usage: {% popular_datalog_categories 5 %}
#     """
#     try:
#         categories = (
#             Category.objects.annotate(
#                 post_count=Count("posts", filter=Q(posts__status="published"))
#             )
#             .filter(post_count__gt=0)
#             .order_by("-post_count")[:limit]
#         )

#         return categories
#     except Exception:
#         return []
# Moved to global - aura_filters
# @register.filter
# def highlight_search(text, query):
#     """
#     Highlights search terms in text.
#     Usage: {{ text|highlight_search:query }}
#     """
#     if not query or not text:
#         return text

#     escaped_text = escape(text)
#     escaped_query = escape(query)

#     # Highlight each word in query
#     words = escaped_query.split()
#     for word in words:
#         pattern = re.compile(re.escape(word), re.IGNORECASE)
#         escaped_text = pattern.sub(
#             f'<mark class="search-highlight">{word}</mark>',
#             escaped_text
#         )
#     return mark_safe(escaped_text)

# In aura_filters under split_string
# @register.simple_tag
# def split_by_comma(value):
#     """
#     Split string by comma for template iteration
#     Usage: {{ "tag1,tag2,tag3"|split_by_comma }}
#     """
#     if not value:
#         return []
#     return [item.strip() for item in value.split(",")]