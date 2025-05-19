from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key."""
    return dictionary.get(key)


@register.filter
def get_field(form, field_name):
    """Get a form field by name."""
    return form[field_name]


@register.filter
@stringfilter
def add(value, arg):
    """Concatenate strings."""
    return value + arg
