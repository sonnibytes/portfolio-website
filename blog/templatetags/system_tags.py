from django import template
from django.utils.safestring import mark_safe
from projects.models import SystemModule

# register = template.Library()


# Moved to global aura_filters
# @register.simple_tag
# def system_status_indicator(system):
#     """Render a HUD-style status indicator for a system."""
#     color = system.get_status_color()
#     status_text = system.get_status_display()

#     html = f'''
#     <div class="system-status-indicator">
#         <div class="status-dot" style="background-color: {color};"></div>
#         <span class="status-text">{status_text}</span>
#     </div>
#     '''
#     return mark_safe(html)

# @register.simple_tag
# def system_progress_bar(system):
#     """Render a progress bar for system development."""
#     progress = system.get_development_progress()

#     html = f'''
#     <div class="system-progress-container">
#         <div class="progress-bar-bg">
#             <div class="progress-bar-fill" style="width: {progress}%"></div>
#         </div>
#         <span class="progress-text">{progress}%</span>
#     </div>
#     '''
#     return mark_safe(html)

# ============Dont think being used?..==============

# @register.filter
# def system_connection_color(connection):
#     """Get the color for a system connection."""
#     return connection.get_status_color()

# @register.filter
# def system_connection_icon(connection):
#     """Get the icon for a system connection."""
#     return connection.get_connection_icon()

# @register.inclusion_tag("blog/includes/system_connection_card.html")
# def system_connection_card(system_connection):
#     """Render a HUD-style system connection card."""
#     return {
#         'connection': system_connection,
#         'system': system_connection.system,
#     }
