"""
Blog Admin URL patterns
"""

from django.urls import path
from . import admin_views

app_name = "blog_admin"

urlpatterns = [
    # Dashboard
    path("", admin_views.BlogAdminDashboardView.as_view(), name="dashboard"),
    # Post Management
    path("posts/", admin_views.PostListAdminView.as_view(), name="post_list"),
    path(
        "posts/create/", admin_views.PostCreateAdminView.as_view(), name="post_create"
    ),
    path(
        "posts/<slug:slug>/edit/",
        admin_views.PostUpdateAdminView.as_view(),
        name="post_update",
    ),
    path(
        "posts/<slug:slug>/delete/",
        admin_views.PostDeleteAdminView.as_view(),
        name="post_delete",
    ),
    # Category Management
    path(
        "categories/", admin_views.CategoryListAdminView.as_view(), name="category_list"
    ),
    path(
        "categories/create/",
        admin_views.CategoryCreateAdminView.as_view(),
        name="category_create",
    ),
    path(
        "categories/<slug:slug>/edit/",
        admin_views.CategoryUpdateAdminView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<slug:slug>/delete/",
        admin_views.CategoryDeleteAdminView.as_view(),
        name="category_delete",
    ),
    # Tag Management
    path("tags/", admin_views.TagListAdminView.as_view(), name="tag_list"),
    path("tags/create/", admin_views.TagCreateAdminView.as_view(), name="tag_create"),
    # path(
    #     "tags/<slug:slug>/edit/",
    #     admin_views.TagUpdateAdminView.as_view(),
    #     name="tag_update",
    # ),
    # path(
    #     "tags/<slug:slug>/delete/",
    #     admin_views.TagDeleteAdminView.as_view(),
    #     name="tag_delete",
    # ),
    # Series Management
    path("series/", admin_views.SeriesListAdminView.as_view(), name="series_list"),
    path(
        "series/create/",
        admin_views.SeriesCreateAdminView.as_view(),
        name="series_create",
    ),
    path(
        "series/<slug:slug>/edit/",
        admin_views.SeriesUpdateAdminView.as_view(),
        name="series_update",
    ),
    path(
        "series/<slug:slug>/delete/",
        admin_views.SeriesUpdateAdminView.as_view(),
        name="series_delete",
    ),
    # System Connections
    path(
        "connections/",
        admin_views.SystemConnectionAdminView.as_view(),
        name="system_connections",
    ),
]
