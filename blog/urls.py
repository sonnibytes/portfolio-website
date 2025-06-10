from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Public blog urls - Post views
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    # Category views
    path("categories/", views.CategoriesOverviewView.as_view(), name="categories_overview"),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
    # Tags views
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tag/<slug:slug>/", views.TagView.as_view(), name="tag"),
    # Archive views
    path("archive/", views.ArchiveIndexView.as_view(), name="archive"),
    # Search views w AJAX
    path("search/", views.SearchView.as_view(), name="search"),
    path("search/suggestions/", views.search_suggestions, name="search_suggestions"),
    # path("search/autocomplete/", views.search_autocomplete, name="search_autocomplete"),
    # path("search/export/", views.search_export, name="search_export"),
    # Admin/Management URLs
    path("admin/dashboard/", views.DashboardView.as_view(), name="dashboard"),
    # Post Management
    path("admin/post/new/", views.PostCreateView.as_view(), name="post_create"),
    path(
        "admin/post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"
    ),
    path(
        "admin/post/<slug:slug>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    # Category Management
    path("admin/categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "admin/category/new/",
        views.CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "admin/category/<slug:slug>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_edit",
    ),
    path(
        "admin/category/<slug:slug>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # Test DataLog Features
    path(
        "test-features/",
        TemplateView.as_view(template_name="blog/debug/test_features.html"),
        name="test_features",
    ),
    # path("test/posts/", views.PostEnhList2.as_view(), name="post_enh2"),
    path(
        "test-search/",
        TemplateView.as_view(template_name="blog/debug/test_search.html"),
        name="test-search",
    ),
    path(
        "test-base/",
        TemplateView.as_view(template_name="blog/debug/test_datalog_base.html"),
        name="test-base",
    ),
    path(
        "test-inherit/",
        TemplateView.as_view(template_name="blog/debug/test_inheritance.html"),
        name="test-inherit",
    ),
    path(
        "test-glass-card/",
        TemplateView.as_view(template_name="blog/debug/test_glass_card.html"),
        name="test-glass-card",
    ),
]

app_name = 'blog'

"""
# If you need API endpoints for mobile or other integrations
api_urlpatterns = [
    path('api/search/', views.search_suggestions_ajax, name='api_search'),
    path('api/autocomplete/', views.search_autocomplete, name='api_autocomplete'),
]

# Add API patterns if needed
# urlpatterns += api_urlpatterns
"""
