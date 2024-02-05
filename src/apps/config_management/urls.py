from django.urls import path

from . import views

app_name="config_management"
urlpatterns = [
    path("", views.index, name="index"),
    path("configuration/", views.configuration, name="configuration"),
]
