from django.urls import path

from . import views

app_name="config_management"
urlpatterns = [
    path("configuration/", views.configuration, name="configuration"),
]
