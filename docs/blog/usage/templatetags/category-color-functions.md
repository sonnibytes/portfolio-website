# ========== IMPROVED COLOR FUNCTIONS FOR DATALOG TAGS ==========

@register.filter
def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple - SIMPLIFIED and more reliable
    Usage: {{ "#ff0000"|hex_to_rgb }} -> "255, 0, 0"
    """
    if not hex_color:
        return "179, 157, 219"  # Default lavender
    
    # Clean the hex color
    hex_color = hex_color.strip()
    if not hex_color.startswith('#'):
        hex_color = '#' + hex_color
    
    # Remove # and ensure 6 characters
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "179, 157, 219"  # Fallback
    
    try:
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)  
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    except ValueError:
        return "179, 157, 219"  # Fallback


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
    
    # Ensure it's a valid hex color
    if not color.startswith('#'):
        color = '#' + color
    
    # Basic validation
    if len(color) == 7 and all(c in '0123456789abcdefABCDEF' for c in color[1:]):
        return color
    else:
        return fallback


@register.filter  
def category_rgb_values(category, fallback="179, 157, 219"):
    """
    Get category RGB values as string for CSS custom properties
    Usage: {{ post.category|category_rgb_values }}
    """
    color = category_safe_color(category)
    return hex_to_rgb(color)


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
    if not category:
        # Default theme
        rgb = "179, 157, 219"
        color = "#b39ddb"
    else:
        color = category_safe_color(category) 
        rgb = category_rgb_values(category)
    
    # Theme variations
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
        rgb = "38, 198, 218"   # Teal
        color = "#26c6da"
    
    css_vars = f"""
        --container-category-rgb: {rgb};
        --container-category-color: {color};
        --container-bg: rgba({rgb}, 0.08);
        --container-border: rgba({rgb}, 0.25);
        --container-glow: rgba({rgb}, 0.12);
    """.strip()
    
    return mark_safe(css_vars)


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
        r, g, b = map(int, rgb.split(', '))
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
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
        r, g, b = map(int, rgb.split(', '))
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
        r, g, b = map(int, rgb.split(', '))
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
    category_name = getattr(category, 'name', '').lower()
    category_code = getattr(category, 'code', '').lower()
    
    theme_map = {
        'ml': 'theme-purple',
        'ai': 'theme-purple', 
        'machine learning': 'theme-purple',
        'dev': 'theme-green',
        'development': 'theme-green',
        'coding': 'theme-green',
        'data': 'theme-orange',
        'analytics': 'theme-orange',
        'visualization': 'theme-orange',
        'system': 'theme-teal',
        'infrastructure': 'theme-teal',
        'devops': 'theme-teal',
    }
    
    # Check code first, then name
    theme = theme_map.get(category_code) or theme_map.get(category_name)
    return theme or "theme-lavender"


# ========== REMOVE/REPLACE OLD FUNCTIONS ==========

# REMOVE the old complex category_color_scheme function
# REMOVE the old generate_category_css_vars function  
# REMOVE the old hex_to_rgba function (replace with hex_to_rgb)

# ========== USAGE EXAMPLES ==========

"""
Template Usage Examples:

1. Simple category color:
   {{ post.category|category_safe_color }}

2. RGB values for CSS:
   style="color: rgb({{ post.category|category_rgb_values }});"

3. Complete CSS variables:
   <div style="{% category_css_vars post.category %}">

4. Unified container variables:
   <div style="{% unified_container_vars post.category %}">

5. Theme classes:
   <div class="{% category_theme_classes post.category %}">

6. Color adjustments:
   background: {{ post.category.color|darken_color:0.8 }};
   border: {{ post.category.color|lighten_color:1.2 }};

7. Smart contrast:
   <div class="text-{{ post.category.color|smart_color_contrast }}">
"""

You're absolutely right! Looking at the `category_color_scheme` function and related color functions in the datalog_tags, there are some issues. Let me create a cleaner, more reliable implementation.Now let's update the post detail template to use these improved functions:Let's also update the CSS debugging section to use the new variables:## 🎯 **Key Improvements Made:**

### **✅ Simplified Color Functions:**

1. **`hex_to_rgb`** - Clean, reliable hex to RGB conversion
2. **`category_safe_color`** - Safe color extraction with fallbacks
3. **`category_rgb_values`** - Direct RGB string for CSS
4. **`unified_container_vars`** - Complete CSS variable generation
5. **`category_theme_classes`** - Automatic theme class assignment

### **🔧 What to Do:**

1. **Replace the old functions** in your `datalog_tags.py`:
   - Remove `category_color_scheme`
   - Remove `generate_category_css_vars`
   - Remove old `hex_to_rgba`
   - Add all the new functions from the artifact

2. **Update any existing templates** that use the old functions:
   ```django
   <!-- OLD -->
   {{ post.category|category_color_scheme.rgb }}
   
   <!-- NEW -->
   {{ post.category|category_rgb_values }}
   ```

3. **The new template** now uses:
   ```django
   style="{% unified_container_vars post.category %}"
   ```

### **🎨 Benefits:**

- **More reliable** - Better error handling and fallbacks
- **Cleaner syntax** - Simpler template usage
- **Better performance** - Less complex calculations
- **Automatic theming** - Smart theme class assignment
- **Consistent colors** - All components use same functions

### **🔍 Debug Test:**

Add this temporarily to verify it's working:
```html
<!-- Debug info -->
<div style="background: red; color: white; padding: 10px;">
    Category: {{ post.category.name|default:"None" }}<br>
    Color: {{ post.category|category_safe_color }}<br>
    RGB: {{ post.category|category_rgb_values }}<br>
    Theme: {% category_theme_classes post.category %}
</div>
```

**The new color system should be much more reliable!** 🎨✨