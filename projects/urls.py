from django.urls import path, include
from . import views

app_name = 'projects'

urlpatterns = [
    # ================= MAIN VIEWS =================

  
    path("systems/", views.EnhancedLearningSystemListView.as_view(), name="system_list"),
    path("systems/<slug:slug>/", views.LearningSystemControlInterfaceView.as_view(), name="system_detail"),
    # Testing new interface w GitHub Data
    path("test/<slug:slug>/", views.SystemControlInterfaceView.as_view(), name="system_detail_test"),

    # path("systems/dashboard/", views.SystemsDashboardView.as_view(), name="systems_dashboard"),

    # System Detail and management
    # Handled by aura-admin
    # path("systems/create/", views.SystemModuleCreateView.as_view(), name="system_create"),
    # path("systems/<slug:slug>/edit/", views.SystemModuleUpdateView.as_view(), name="system_update"),
    # path("systems/<slug:slug>/delete/", views.SystemModuleDeleteView.as_view(), name="system_delete"),

    # System type and technology views
    path("types/", views.SystemTypesOverviewView.as_view(), name="system_types_overview"),
    path("types/<slug:slug>/", views.SystemTypeDetailView.as_view(), name="system_type"),
    path("technologies/", views.TechnologiesOverviewView.as_view(), name="technologies_overview"),
    path("technologies/<slug:slug>/", views.TechnologyDetailView.as_view(), name="technology_detail"),

    # Showcase and presentation views
    path("featured/", views.FeaturedSystemsView.as_view(), name="featured_systems"),

    # GitHub Integration URLs
    path('github/', views.GitHubIntegrationView.as_view(), name='github_integration'),
    path('github/sync/', views.GitHubSyncView.as_view(), name='github_sync'),
    # path('github/repository/<str:repo_name>/', views.GitHubRepositoryDetailView.as_view(), name='github_repo_detail'),


    # Dashboard views to dial in for later enhancement
    path("dashboard/", views.EnhancedSystemsDashboardView.as_view(), name="systems_dashboard"),
    path("learning/", views.LearningJourneyDashboardView.as_view(), name="learning_dashboard"),
    path("landing/", views.PortfolioLandingDashboardView.as_view(), name="landing_dashboard"),
]
