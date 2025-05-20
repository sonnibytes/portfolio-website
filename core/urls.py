from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("developer-profile/", views.DeveloperProfileView.as_view(), name="about"),
    path("comm-terminal/", views.CommTerminalView.as_view(), name="contact"),
]
