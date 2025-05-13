from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/",
         views.PostDetailView.as_view(), name="post_detail"),
    path("category/<slug:slug>/",
         views.CategoryView.as_view(), name="category"),
    path("tag/<slug:slug>/", views.TagView.as_view(), name="tag"),
    path("archive/", views.ArchiveView(), name="archive"),
]
