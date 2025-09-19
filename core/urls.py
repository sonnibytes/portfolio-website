# Version 2.0
from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('developer-profile/', views.DeveloperProfileView.as_view(), name='about'),
    path('communication/', views.CommTerminalView.as_view(), name='contact'),
    path('communication/success/', views.ContactSuccessView.as_view(), name='contact_success'),

    # # Resume download routes
    # path('resume/download/', views.ResumeDownloadView.as_view(), name='resume_download'),
    # path('resume/download/<str:format>/', views.ResumeDownloadView.as_view(), name='resume_download_format'),

    # Enhanced Resume System
    path('resume/', views.ResumePreviewView.as_view(), name='resume_preview'),
    path('resume/download/', views.EnhancedResumeDownloadView.as_view(), name='resume_download'),
    path('resume/download/<str:format>/', views.EnhancedResumeDownloadView.as_view(), name='resume_download_format'),

    # Static pages
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),

    # API Endpoint for HUD data
    path('api/metrics/', views.SystemMetricsAPIView.as_view(), name='api_metrics'),
    # Enhanced Resume Download Tracking API route
    path('api/track-download/', views.TrackDownloadAPIView.as_view(), name='track_download'),

    # Dynamic page from database
    path('page/<slug:slug>/', views.CorePageView.as_view(), name='page'),

    # Temp to test error pages
    # path('test-500/', views.test_500, name='test_500'),
    # path('test-403/', views.test_403, name='test_403'),

]
