from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # ================= MAIN VIEWS =================
    # Main dashboard and systems views
    # path("", views.UnifiedDashboardView.as_view(), name="unified_dashboard"),
    # AURA Enhanced dashboard
    path("dashboard/", views.EnhancedSystemsDashboardView.as_view(), name="systems_dashboard"),
    path("systems/", views.EnhancedSystemListView.as_view(), name="system_list"),
    # path("systems/dashboard/", views.SystemsDashboardView.as_view(), name="systems_dashboard"),

    # System Detail and management
    # path("systems/<slug:slug>/", views.EnhancedSystemModuleDetailView.as_view(), name="system_detail"),
    path("systems/<slug:slug>/", views.SystemModuleDetailView.as_view(), name="system_detail"),
    path("systems/create/", views.SystemModuleCreateView.as_view(), name="system_create"),
    path("systems/<slug:slug>/edit/", views.SystemModuleUpdateView.as_view(), name="system_update"),
    path("systems/<slug:slug>/delete/", views.SystemModuleDeleteView.as_view(), name="system_delete"),

    # System type and technology views
    path("types/<slug:slug>/", views.SystemTypeDetailView.as_view(), name="system_type"),
    path("technologies/<slug:slug>/", views.TechnologyDetailView.as_view(), name="technology_detail"),

    # Showcase and presentation views
    path("featured/", views.FeaturedSystemsView.as_view(), name="featured_systems"),
    # path("timeline/", views.SystemTimelineView.as_view(), name="system_timeline"),
    # Search and filtering
    # path("search/", views.SystemSearchView.as_view(), name="system_search"),

    # ================= API ENDPOINTS =================
    # path("api/dashboard/metrics/", views.DashboardMetricsAPIView.as_view(), name="dashboard_metrics_api"),
    # path("api/dashboard/timeseries/", views.SystemTimeSeriesAPIView.as_view(), name="dashboard_timeseries_api"),
    # path("api/systems/<slug:slug>/metrics/", views.SystemMetricsAPIView.as_view(), name="system_metrics_api"),
    # path("api/technologies/usage/", views.TechnologyUsageAPIView.as_view(), name="technology_usage_api"),
    
    # Rework - Simplified API Endpoints
    # path("api/dashboard/", views.DashboardAPIView.as_view(), name="dashboard_api"),
    # path("api/quick-stats/", ),
]
