from django.urls import path, include
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Public blog urls - Post views
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    
    # Category views
    path(
        "categories/",
        views.CategoriesOverviewView.as_view(),
        name="categories_overview",
    ),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
    
    # Tags views
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tag/<slug:slug>/", views.TagView.as_view(), name="tag"),
    
    # Archive views
    path("archive/", views.ArchiveIndexView.as_view(), name="archive"),
    
    # Search views w AJAX
    path("search/", views.SearchView.as_view(), name="search"),
    path("search/ajax/", views.search_suggestions, name="search_ajax"),
    # path("search/autocomplete/", views.search_autocomplete, name="search_autocomplete"),
    # path("search/export/", views.search_export, name="search_export"),
    
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

    # ===== INTERACTION ENDPOINTS =====
    
    # Subscribe
    path('subscribe/', views.subscribe_email, name='subscribe'),
    path('verify/<str:token>/', views.verify_subscription, name='verify_subscription'),
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
    
    # Bookmarks
    path('bookmarks/', views.bookmarks_page, name='bookmarks'),
    path('api/bookmarks/', views.get_bookmarked_posts, name='api_bookmarks'),
    
    # Share (helper endpoint)
    path('api/share/<slug:slug>/', views.get_share_data, name='api_share'),
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
