from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('developer-profile/', views.DeveloperProfileView.as_view(), name='about'),
    path('communication/', views.CommTerminalView.as_view(), name='contact'),
    path('communication/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('resume/', views.ResumeView.as_view(), name='resume'),
    # Static pages
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    # Dynamic page from database
    path('page/<slug:slug>/', views.CorePageView.as_view(), name='page'),
]
