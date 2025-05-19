from django import template
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify as md
from bs4 import BeautifulSoup
from django.utils.text import slugify

register = template.Library()

@register.filter
def markdownify(text):
    """
    Filter to convert markdown text to HTML using markdownx util,
    and add IDs to headings for table of contents links to work.
    """
    # First convert markdown to HTML
    html_content = md(text)

    # Use BeautifulSoup to parse and modify HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all heading elements (h1, h2, h3, etc.)
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        # Create an ID from heading text
        heading_id = slugify(heading.get_text())

        # Set the ID attribute on the heading element
        heading['id'] = heading_id

    # Return modified HTML
    return mark_safe(str(soup))
