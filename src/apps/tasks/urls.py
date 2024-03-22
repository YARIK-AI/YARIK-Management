from django.urls import path

from . import views

app_name="tasks"
urlpatterns = [
    path("sync/", views.sync, name="sync"),
    path("tasks/", views.tasks, name="tasks"),
    path("tasks/503", views.page_503, name="tasks-503"),
    path("tasks/404", views.page_404, name="tasks-404"),
]
