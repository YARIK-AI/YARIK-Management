from django.urls import path

from . import views

app_name="tasks"
urlpatterns = [
    path("sync/", views.sync, name="sync"),
    path("tasks/", views.tasks, name="tasks"),
]
