"""
Core Admin URL Configuration
Main admin dashboard and global admin functionality
Version 2.0
"""

from django.urls import path
from .admin_views import MainAdminDashboardView

app_name = "core_admin"

urlpatterns = [
    # Main admin dashboard
    path("", MainAdminDashboardView.as_view(), name="dashboard"),
]
