from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Public blog urls - Post views
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    # Category view
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
    # Tags views
    path("tags/", views.TagListView.as_view(), name="tags"),
    path("tags/<slug:slug>/", views.TagView.as_view(), name="tag"),
    # Archive views
    path("archive/", views.ArchiveIndexView.as_view(), name="archive"),
    path("archive/<int:year>/", views.ArchiveYearView.as_view(), name="archive_year"),
    path(
        "archive/<int:year>/<int:month>/",
        views.ArchiveMonthView.as_view(),
        name="archive_month",
    ),
    # Search view
    path("search/", views.SearchView.as_view(), name="search"),

    # Admin/Management URLs
    path("admin/dashboard/", views.DashboardView.as_view(), name="dashboard"),

    # Post Management
    path("admin/post/new/", views.PostCreateView.as_view(), name="post_create"),
    path("admin/post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("admin/post/<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),

    # Category Management
    path("admin/categories/", views.CategoryListView.as_view(), name="category_list"),
    path("admin/category/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("admin/category/<slug:slug>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("admin/category/<slug:slug>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Test DataLog Features
    path("test-features/", TemplateView.as_view(template_name='blog/test_features.html'), name='test_features'),
    # path("test/posts/", views.PostEnhList2.as_view(), name="post_enh2"),
]

app_name = 'blog'
