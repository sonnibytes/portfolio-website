from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

# Create a template library to register filters
register = template.Library()


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
         
        print(f"LANGUAGE: {language} - Lexer: {lexer}")

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