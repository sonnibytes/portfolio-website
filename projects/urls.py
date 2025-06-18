from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # ================= MAIN VIEWS =================

    path("dashboard/", views.EnhancedSystemsDashboardView.as_view(), name="systems_dashboard"),
    path("systems/", views.EnhancedLearningSystemListView.as_view(), name="system_list"),
    path("systems/<slug:slug>/", views.LearningSystemControlInterfaceView.as_view(), name="system_detail"),

    # path("systems/dashboard/", views.SystemsDashboardView.as_view(), name="systems_dashboard"),

    # System Detail and management

    path("systems/create/", views.SystemModuleCreateView.as_view(), name="system_create"),
    path("systems/<slug:slug>/edit/", views.SystemModuleUpdateView.as_view(), name="system_update"),
    path("systems/<slug:slug>/delete/", views.SystemModuleDeleteView.as_view(), name="system_delete"),

    # System type and technology views
    path("types/<slug:slug>/", views.SystemTypeDetailView.as_view(), name="system_type"),
    path("technologies/<slug:slug>/", views.TechnologyDetailView.as_view(), name="technology_detail"),

    # Showcase and presentation views
    path("featured/", views.FeaturedSystemsView.as_view(), name="featured_systems"),

    # Learning Journey
    path("learning/", views.LearningJourneyDashboardView.as_view(), name="learning_dashboard"),
    # path("learning/systems/", views.EnhancedLearningSystemListView.as_view(), name="learning_system_list"),
    # path("learning/systems/<slug:slug>/", views.LearningSystemControlInterfaceView.as_view(), name="learning_system_detail"),
    path("landing/", views.PortfolioLandingDashboardView.as_view(), name="landing_dashboard"),

]
