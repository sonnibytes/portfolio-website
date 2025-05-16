from django.urls import path
from . import views

urlpatterns = [
    # Post views
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/create/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("upload/image/", views.ImageUploadView.as_view(), name="upload_image"),
    # Category view
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
    # Tags views
    path("tags/", views.TagListView.as_view(), name="tags"),
    path("tags/<slug:slug>/", views.TagView.as_view(), name="tag"),
    path("tags/suggestions/", views.TagSuggestionsView.as_view(), name="tag_suggestions"),
    # Archive views
    path("archive/", views.ArchiveView.as_view(), name="archive"),
    path("archive/<int:year>/", views.ArchiveView.as_view(), name="archive_year"),
    path(
        "archive/<int:year>/<int:month>/",
        views.ArchiveView.as_view(),
        name="archive_month",
    ),
    # Search view
    path("search/", views.SearchView.as_view(), name="search"),
]

app_name = 'blog'
