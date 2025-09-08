# blog/admin_urls.py
"""
Blog Admin URL Configuration
DataLogs management interface routing
Version 3.0
"""

from django.urls import path
from . import admin_views

app_name = 'blog'

urlpatterns = [
    # ===== Restructured/Replaced URLs for Admin-Facing Learning Journey Focus  =====
    # Dashboard
    path('', admin_views.LearningJourneyDashboardView.as_view(), name='dashboard'),
    # path('', admin_views.BlogAdminDashboardView.as_view(), name='dashboard'),

    # Enhanced Learning Journey (Series) Management
    path('journeys/', admin_views.LearningJourneyListView.as_view(), name='learning_journey_list'),
    path('journeys/<int:pk>/', admin_views.LearningJourneyDetailView.as_view(), name='learning_journey_detail'),

    # Enhanced Post (Discoveries) Creation (Learning Journey Restructure)
    path('discoveries/create/', admin_views.EnhancedPostCreateView.as_view(), name='discovery_create'),
    
    # Post Management (or Discoveries)
    path('posts/', admin_views.PostListAdminView.as_view(), name='post_list'),  # All discoveries
    path('posts/create/', admin_views.EnhancedPostCreateView.as_view(), name='post_create'),  # Use updated post create view
    # path('posts/create/', admin_views.PostCreateAdminView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', admin_views.PostUpdateAdminView.as_view(), name='post_edit'),
    path('posts/<int:pk>/delete/', admin_views.PostDeleteAdminView.as_view(), name='post_delete'),
    
    # Category Management (or Knowledge Domains)
    path('categories/', admin_views.CategoryListAdminView.as_view(), name='category_list'),
    path('categories/create/', admin_views.CategoryCreateAdminView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', admin_views.CategoryUpdateAdminView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', admin_views.CategoryDeleteAdminView.as_view(), name='category_delete'),
    
    # Tag Management
    path('tags/', admin_views.TagListAdminView.as_view(), name='tag_list'),
    path('tags/create/', admin_views.TagCreateAdminView.as_view(), name='tag_create'),
    path('tags/<int:pk>/edit/', admin_views.TagUpdateAdminView.as_view(), name='tag_edit'),
    path('tags/<int:pk>/delete/', admin_views.TagDeleteAdminView.as_view(), name='tag_delete'),
    
    # Series Management (or Learning Journey)
    path('series/', admin_views.LearningJourneyListView.as_view(), name='series_list'),  # Redirect to learning_journey_list
    # path('series/', admin_views.SeriesListAdminView.as_view(), name='series_list'),
    path('series/create/', admin_views.SeriesCreateAdminView.as_view(), name='series_create'),
    path('series/<int:pk>/edit/', admin_views.SeriesUpdateAdminView.as_view(), name='series_edit'),
    path('series/<int:pk>/delete/', admin_views.SeriesDeleteAdminView.as_view(), name='series_delete'),
    path('series/<int:pk>/manage-posts/', admin_views.SeriesPostsManageView.as_view(), name='series_posts_manage'),

    
    # AJAX API endpoints
    path('api/posts/<int:pk>/toggle-status/', admin_views.PostStatusToggleView.as_view(), name='post_toggle_status'),
    path('api/posts/<int:pk>/toggle-feature/', admin_views.PostFeatureToggleView.as_view(), name='post_toggle_feature'),

]
