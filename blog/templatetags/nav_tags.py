from django import template

register = template.Library()


@register.inclusion_tag("components/sub-nav.html", takes_context=True)
def render_subnav(context, links):
    return {"links": links}
