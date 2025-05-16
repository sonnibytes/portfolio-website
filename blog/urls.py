from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/",
         views.PostDetailView.as_view(), name="post_detail"),
    path("category/<slug:slug>/",
         views.CategoryView.as_view(), name="category"),
    path("tag/<slug:slug>/", views.TagView.as_view(), name="tag"),
    path("archive/", views.ArchiveView.as_view(), name="archive"),
    path("archive/<int:year>/",
         views.ArchiveView.as_view(), name="archive_year"),
    path(
        "archive/<int:year>/<int:month>/",
        views.ArchiveView.as_view(),
        name="archive_month",
    ),
    path("search/", views.SearchView.as_view(), name="search"),
]

app_name = 'blog'
