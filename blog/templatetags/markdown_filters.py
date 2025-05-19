from django import template
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify as md

register = template.Library()

@register.filter
def markdownify(text):
    """Filter to convert markdown text to HTML using markdownx util"""
    return mark_safe(md(text))
