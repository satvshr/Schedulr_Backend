from django.urls import path

from . import views

urlpatterns = [
    path("", views.auth, name="auth"),
    path("api", views.api, name="api"),
    path("get", views.get_events, name="get_events"),
]