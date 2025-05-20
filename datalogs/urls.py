from django.urls import path
from . import views

urlpatterns = [
    # Public blog urls - Post views
    # path("", views.PostListView.as_view(), name="post_list"),
    # path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    # # Category view
    # path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
    # # Tags views
    # path("tags/", views.TagListView.as_view(), name="tags"),
    # path("tags/<slug:slug>/", views.TagView.as_view(), name="tag"),
    # # Archive views
    # path("archive/", views.ArchiveView.as_view(), name="archive"),
    # path("archive/<int:year>/", views.ArchiveView.as_view(), name="archive_year"),
    # path(
    #     "archive/<int:year>/<int:month>/",
    #     views.ArchiveView.as_view(),
    #     name="archive_month",
    # ),
    # # Search view
    # path("search/", views.SearchView.as_view(), name="search"),

    # # Admin/Management URLs
    # path("admin/dashboard/", views.DashboardView.as_view(), name="dashboard"),

    # # Post Management
    # path("admin/post/new/", views.PostCreateView.as_view(), name="post_create"),
    # path("admin/post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    # path("admin/post/<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),

    # # Category Management
    # path("admin/categories/", views.CategoryListView.as_view(), name="category_list"),
    # path("admin/category/new/", views.CategoryCreateView.as_view(), name="category_create"),
    # path("admin/category/<slug:slug>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    # path("admin/category/<slug:slug>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
]

app_name = 'datalogs'

    # path("post/create/", views.PostCreateView.as_view(), name="post_create"),
    # path("post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    # path("upload/image/", views.ImageUploadView.as_view(), name="upload_image"),
    # path("tags/suggestions/", views.TagSuggestionsView.as_view(), name="tag_suggestions"),