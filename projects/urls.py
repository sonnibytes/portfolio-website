from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # ================= MAIN VIEWS =================
    # Systems overview and dashboard
    path("", views.SystemModuleListView.as_view(), name="system_list"),
    path("dashboard/", views.SystemsDashboardView.as_view(), name="systems_dashboard"),
    path("featured/", views.FeaturedSystemsView.as_view(), name="featured_systems"),
    path("timeline/", views.SystemTimelineView.as_view(), name="system_timeline"),
    # Individual system detail
    path(
        "system/<slug:slug>/",
        views.SystemModuleDetailView.as_view(),
        name="system_detail",
    ),
    # System types
    path("type/<slug:slug>/", views.SystemTypeDetailView.as_view(), name="system_type"),
    # Technologies
    path(
        "technology/<slug:slug>/",
        views.TechnologyDetailView.as_view(),
        name="technology_detail",
    ),
    # Search and filtering
    path("search/", views.SystemSearchView.as_view(), name="system_search"),
    # ================= ADMIN/MANAGEMENT =================
    path(
        "admin/system/create/",
        views.SystemModuleCreateView.as_view(),
        name="system_create",
    ),
    path(
        "admin/system/<slug:slug>/edit/",
        views.SystemModuleUpdateView.as_view(),
        name="system_edit",
    ),
    path(
        "admin/system/<slug:slug>/delete/",
        views.SystemModuleDeleteView.as_view(),
        name="system_delete",
    ),
    # ================= API ENDPOINTS =================
    path(
        "api/system/<slug:slug>/metrics/",
        views.SystemMetricsAPIView.as_view(),
        name="system_metrics_api",
    ),
    path(
        "api/technologies/usage/",
        views.TechnologyUsageAPIView.as_view(),
        name="technology_usage_api",
    ),
]
