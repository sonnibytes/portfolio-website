"""
Global Admin URL patterns
"""

from django.urls import path, include
from django.views.generic import TemplateView

app_name = "admin"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="admin/main_dashboard.html"),
        name="main_dashboard",
    ),
    path("blog/", include("blog.admin_urls")),
    path("projects/", include("projects.admin_urls")),
]
