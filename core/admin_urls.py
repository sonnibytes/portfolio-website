"""
Core Admin URL Configuration
Main admin dashboard and global admin functionality
Version 2.0
"""

from django.urls import path, include
from .admin_views import MainAdminDashboardView

app_name = "admin"

urlpatterns = [
    # Main admin dashboard
    path("", MainAdminDashboardView.as_view(), name="dashboard"),
    # Blog admin (add this line)
    path("blog/", include("blog.admin_urls", namespace="blog")),
    # Projects/Systems admin
    path("projects/", include("projects.admin_urls", namespace="projects")),
]
