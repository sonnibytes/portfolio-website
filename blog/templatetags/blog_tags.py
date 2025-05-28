"""
AURA Portfolio - Blog Template Tags
Custom template tags and filters for the blog/datalogs system
Version 2.0.1: Separated Out Global TemplateTags to aura_filters
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

from bs4 import BeautifulSoup
from markdownx.utils import markdownify as md
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from ..models import Post, Category, Tag

register = template.Library()

### Moved to aura_filters global

# @register.filter
# def get_item(dictionary, key):
#     """
#     Get an item from a dictionary using variable key.
#     Usage: {{ dict|get_item:key }}
#     """
#     try:
#         return dictionary.get(key)
#     except (AttributeError, TypeError):
#         return None


# @register.filter
# def get_field(form, field_name):
#     """Get a form field by name."""
#     return form[field_name]


# # Previously 'add' renaming to avoid namespace issues with add
# @register.filter
# @stringfilter
# def concat(value, arg):
#     """Concatenate strings."""
#     return value + arg


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

# Moved to global aura_filters
# @register.inclusion_tag('components/pagination.html')
# def render_pagination(page_obj, request):
#     """
#     Renders AURA-styled pagination.
#     Usage: {% render_pagination page_obj request %}
#     """
#     return {
#         'page_obj': page_obj,
#         'request': request,
#     }


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

## Moved to global aura_filters
# @register.filter
# def time_since_published(published_date):
#     """
#     Returns human-readable time since publication.
#     Usage: {{ post.published_date|time_since_published }}
#     """
#     if not published_date:
#         return "Unknown"

#     now = datetime.now()
#     if published_date.tzinfo:
#         now = timezone.now()

#     diff = now - published_date

#     if diff.days > 365:
#         years = diff.days // 365
#         return f"{years} year{'s' if years != 1 else ''} ago"
#     elif diff.days > 30:
#         months = diff.days // 30
#         return f"{months} month{'s' if months != 1 else ''} ago"
#     elif diff.days > 0:
#         return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
#     elif diff.seconds > 3600:
#         hours = diff.seconds // 3600
#         return f"{hours} hour{'s' if hours != 1 else ''} ago"
#     elif diff.seconds > 60:
#         minutes = diff.seconds // 60
#         return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
#     else:
#         return "Just now"


@register.filter
def category_color(category, default="#b39ddb"):
    """
    Returns category color or default.
    Usage: {{ post.category|category_color }}
    """
    if hasattr(category, 'color') and category.color:
        return category.color
    return default


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

# moved to global aura_filters
# @register.filter
# def datalog_id(post_id):
#     """
#     Formats post ID as data identifier.
#     Usage: {{ post.id|datalog_id }}
#     """
#     return f"LOG-{post_id:03d}"

# Moved to global aura_filters
# @register.filter
# def truncate_smart(text, length=150):
#     """
#     Smart truncation that doesn't cut off in the middle of words.
#     Usage: {{ text|truncate_smart:100 }}
#     """
#     if not text or len(text) <= length:
#         return text

#     truncated = text[:length].rsplit(' ', 1)[0]
#     return truncated + '...'


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
def get_post_count_by_category():
    """
    Returns post count grouped by category.
    Usage: {% get_post_count_by_category %}
    """
    return Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)


@register.simple_tag
def blog_stats():
    """
    Returns blog stats for dashboard display.
    Usage: {% blog_stats %}
    """
    total_posts = Post.objects.filter(status='published').count()
    total_categories = Category.objects.count()
    total_tags = Tag.objects.count()
    avg_reading_time = Post.objects.filter(status='published').aggregate(
        avg_time=Avg('reading_time')
    )['avg_time'] or 0

    return {
        'total_posts': total_posts,
        'total_categories': total_categories,
        'total_tags': total_tags,
        'avg_reading_time': round(avg_reading_time, 1),
    }


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


# Adding from blog system_tags
@register.inclusion_tag("blog/includes/related_systems.html")
def related_systems(post, limit=3):
    """Show related systems for a blog post."""
    connections = post.system_connections.select_related("system").order_by(
        "-priority"
    )[:limit]
    return {
        "connections": connections,
        "post": post,
    }


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


# @register.simple_tag(takes_context=True)
# def active_nav(context, url_name):
#     """
#     Returns 'active' if current URL matches the given URL name.
#     Usage: {% active_nav 'blog:post_list' %}
#     """
#     request = context['request']
#     if request.resolver_match and request.resolver_match.url_name == url_name:
#         return 'active'
#     return ''


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
