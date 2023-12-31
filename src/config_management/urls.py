from django.urls import path

from . import views

app_name="config_management"
urlpatterns = [
    path("", views.index, name="index"),
    path("editparams/", views.editparams, name="editparams"),
    path("configs/", views.configs, name="configs"),
    path("components/", views.components, name="components"),
]
