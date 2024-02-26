from django.urls import path

from . import views

app_name="tasks"
urlpatterns = [
    path("tasks/", views.tasks, name="tasks"),
]
