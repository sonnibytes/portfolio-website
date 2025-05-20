from django.urls import path
from . import views

app_name = 'systems'

urlpatterns = [
    path("", views.SystemListView.as_view(), name="systems"),
    path(
        "category/<slug:category>/",
        views.SystemCategoryView.as_view(),
        name="systems_by_category",
    ),
    path("<slug:slug>/", views.SystemDetailView.as_view(), name="system_detail"),
]
