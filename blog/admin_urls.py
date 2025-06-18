# blog/admin_urls.py
"""
Blog Admin URL patterns - Minimal for testing
"""

from django.urls import path
from django.views.generic import TemplateView

app_name = 'blog_admin'

urlpatterns = [
    # For now, just return placeholder views to avoid URL errors
    path('', TemplateView.as_view(template_name='admin/placeholder.html'), name='dashboard'),
    path('posts/', TemplateView.as_view(template_name='admin/placeholder.html'), name='post_list'),
    path('posts/create/', TemplateView.as_view(template_name='admin/placeholder.html'), name='post_create'),
    path('categories/', TemplateView.as_view(template_name='admin/placeholder.html'), name='category_list'),
]