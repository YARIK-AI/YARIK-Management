from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpRequest

# Create your views here.
@login_required(login_url=reverse_lazy("auth:login"))
def tasks(request: HttpRequest):
    return render(request, "tasks/tasks.html")
