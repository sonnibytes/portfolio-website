from django.urls import path, include
from . import views
from django.views.generic import TemplateView

app_name = 'projects'

urlpatterns = [
    # ================= MAIN VIEWS =================

  
    path("systems/", views.EnhancedLearningSystemListView.as_view(), name="system_list"),
    path("systems/<slug:slug>/", views.LearningSystemControlInterfaceView.as_view(), name="system_detail"),

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
    path('github/test/', views.GitHubIntegrationTestView.as_view(), name='github_test'),
    path('chartjs-test/', TemplateView.as_view(template_name='projects/chartjs_test.html'), name='chartjs_test'),
]
