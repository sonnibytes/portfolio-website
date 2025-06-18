# projects/admin_urls.py
"""
Projects Admin URL patterns - Minimal for testing
"""

from django.urls import path
from django.views.generic import TemplateView

app_name = 'projects_admin'

urlpatterns = [
    # For now, just return placeholder views to avoid URL errors
    path('', TemplateView.as_view(template_name='admin/placeholder.html'), name='dashboard'),
    path('systems/', TemplateView.as_view(template_name='admin/placeholder.html'), name='system_list'),
    path('systems/create/', TemplateView.as_view(template_name='admin/placeholder.html'), name='system_create'),
    path('technologies/', TemplateView.as_view(template_name='admin/placeholder.html'), name='technology_list'),
]