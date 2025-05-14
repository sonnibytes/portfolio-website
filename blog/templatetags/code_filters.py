from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

register = template.Library()

@register.filter(name='highlight_code')
@stringfilter
def highlight_code(code, language=None):
    try:
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        else:
            lexer = TextLexer
        formatter = HtmlFormatter(style='monokai', cssclass="highlighted")
        return mark_safe(highlight(code, lexer, formatter))
    except:
        # If pygments encounters an error, return the original code
        return code
    
@register.simple_tag
def pygments_css():
    formatter = HtmlFormatter(style='monokai')
    return mark_safe(f"<style>{formatter.get_style_defs(".highlighted")}</style>")
