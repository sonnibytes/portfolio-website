# core/admin_urls.py
"""
Global Admin URL patterns - Step 2: Add both includes back
"""

from django.urls import path, include
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="admin/main_dashboard.html"),
        name="admin_dashboard",
    ),
    # Both includes restored
    path("blog/", include("blog.admin_urls")),
    path("projects/", include("projects.admin_urls")),
]
