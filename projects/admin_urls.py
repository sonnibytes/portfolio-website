"""
Projects Admin URL Configuration
Systems management interface routing
Version 2.0
"""

from django.urls import path
from . import admin_views

app_name = 'projects'

urlpatterns = [
    # Dashboard
    path('', admin_views.ProjectsAdminDashboardView.as_view(), name='dashboard'),
    
    # System Management
    path('systems/', admin_views.SystemListAdminView.as_view(), name='system_list'),
    path('systems/create/', admin_views.SystemCreateAdminView.as_view(), name='system_create'),
    path('systems/<int:pk>/edit/', admin_views.SystemUpdateAdminView.as_view(), name='system_edit'),
    path('systems/<int:pk>/delete/', admin_views.SystemDeleteAdminView.as_view(), name='system_delete'),
    
    # Technology Management
    path('technologies/', admin_views.TechnologyListAdminView.as_view(), name='technology_list'),
    path('technologies/create/', admin_views.TechnologyCreateAdminView.as_view(), name='technology_create'),
    path('technologies/<int:pk>/edit/', admin_views.TechnologyUpdateAdminView.as_view(), name='technology_edit'),
    path('technologies/<int:pk>/delete/', admin_views.TechnologyDeleteAdminView.as_view(), name='technology_delete'),
    
    # System Type Management
    path('system-types/', admin_views.SystemTypeListAdminView.as_view(), name='system_type_list'),
    path('system-types/create/', admin_views.SystemTypeCreateAdminView.as_view(), name='system_type_create'),
    path('system-types/<int:pk>/edit/', admin_views.SystemTypeUpdateAdminView.as_view(), name='system_type_edit'),
    path('system-types/<int:pk>/delete/', admin_views.SystemTypeDeleteAdminView.as_view(), name='system_type_delete'),
    
    # AJAX API endpoints
    path('api/systems/<int:pk>/toggle-status/', admin_views.SystemStatusToggleView.as_view(), name='system_toggle_status'),
    path('api/systems/<int:pk>/toggle-feature/', admin_views.SystemFeatureToggleView.as_view(), name='system_toggle_feature'),

    # ================= NEW ARCHITECTURE MANAGEMENT URLS =================
    
    # Architecture Components
    path('architecture/components/', admin_views.ArchitectureComponentListAdminView.as_view(), name='architecture_component_list'),
    path('architecture/components/create/', admin_views.ArchitectureComponentCreateAdminView.as_view(), name='architecture_component_create'),
    path('architecture/components/<int:pk>/edit/', admin_views.ArchitectureComponentUpdateAdminView.as_view(), name='architecture_component_edit'),
    path('architecture/components/<int:pk>/delete/', admin_views.ArchitectureComponentDeleteAdminView.as_view(), name='architecture_component_delete'),
    
    # Architecture Connections
    path('architecture/connections/', admin_views.ArchitectureConnectionListAdminView.as_view(), name='architecture_connection_list'),
    path('architecture/connections/create/', admin_views.ArchitectureConnectionCreateAdminView.as_view(), name='architecture_connection_create'),
    path('architecture/connections/<int:pk>/edit/', admin_views.ArchitectureConnectionUpdateAdminView.as_view(), name='architecture_connection_edit'),
    path('architecture/connections/<int:pk>/delete/', admin_views.ArchitectureConnectionDeleteAdminView.as_view(), name='architecture_connection_delete'),
    
    # System Architecture Management
    path('systems/<int:pk>/architecture/', admin_views.SystemArchitectureAdminView.as_view(), name='system_architecture'),

    # New Architecture AJAX endpoints
    path('api/systems/<int:pk>/architecture-preview/', admin_views.ArchitecturePreviewView.as_view(), name='architecture_preview'),
    path('api/systems/<int:pk>/create-default-architecture/', admin_views.CreateDefaultArchitectureView.as_view(), name='create_default_architecture'),

    # New SystemSkillGain Views
    path('skill-gains/', admin_views.SystemSkillGainListAdminView.as_view(), name='system_skill_gain_list'),
    path('skill-gains/create/', admin_views.SystemTypeCreateAdminView.as_view(), name='system_skill_gain_create'),
    path('skill-gains/<int:pk>/edit/', admin_views.SystemTypeUpdateAdminView.as_view(), name='system_skill_gain_edit'),
    path('skill-gains/<int:pk>/delete/', admin_views.SystemTypeDeleteAdminView.as_view(), name='system_skill_gain_delete'),
]
