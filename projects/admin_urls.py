"""
Projects Admin URL patterns
"""

from django.urls import path
from . import admin_views

app_name = "projects_admin"

urlpatterns = [
    # Dashboard
    path("", admin_views.SystemsAdminDashboardView.as_view(), name="dashboard"),
    # System Management
    path("systems/", admin_views.SystemListAdminView.as_view(), name="system_list"),
    path(
        "systems/create/",
        admin_views.SystemCreateAdminView.as_view(),
        name="system_create",
    ),
    path(
        "systems/<slug:slug>/edit/",
        admin_views.SystemUpdateAdminView.as_view(),
        name="system_update",
    ),
    path(
        "systems/<slug:slug>/delete/",
        admin_views.SystemDeleteAdminView.as_view(),
        name="system_delete",
    ),
    # Technology Management
    path(
        "technologies/",
        admin_views.TechnologyListAdminView.as_view(),
        name="technology_list",
    ),
    path(
        "technologies/create/",
        admin_views.TechnologyCreateAdminView.as_view(),
        name="technology_create",
    ),
    path(
        "technologies/<slug:slug>/edit/",
        admin_views.TechnologyUpdateAdminView.as_view(),
        name="technology_update",
    ),
    path(
        "technologies/<slug:slug>/delete/",
        admin_views.TechnologyDeleteAdminView.as_view(),
        name="technology_delete",
    ),
    # System Type Management
    path(
        "types/", admin_views.SystemTypeListAdminView.as_view(), name="system_type_list"
    ),
    path(
        "types/create/",
        admin_views.SystemTypeCreateAdminView.as_view(),
        name="system_type_create",
    ),
    path(
        "types/<slug:slug>/edit/",
        admin_views.SystemTypeUpdateAdminView.as_view(),
        name="system_type_update",
    ),
    path(
        "types/<slug:slug>/delete/",
        admin_views.SystemTypeDeleteAdminView.as_view(),
        name="system_type_delete",
    ),
    # API Endpoints
    path(
        "api/metrics/", admin_views.SystemMetricsAPIView.as_view(), name="metrics_api"
    ),
    path(
        "api/metrics/<slug:slug>/",
        admin_views.SystemMetricsAPIView.as_view(),
        name="system_metrics_api",
    ),
    path(
        "api/health-check/",
        admin_views.SystemHealthCheckAPIView.as_view(),
        name="health_check_api",
    ),
]
