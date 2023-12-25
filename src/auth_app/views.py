from .forms import LoginForm
from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy


def login(request):
    next = ""
    if request.method == "POST":
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            login = loginform.cleaned_data["login"]
            pswd = loginform.cleaned_data["pswd"]
            user = auth.authenticate(username=login, password=pswd)
            next = loginform.cleaned_data["next"]
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect(next if len(next) else reverse("auth:profile"))
        return render(request, "login.html", {"form": loginform, "wrong": True})
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("auth:profile"))
        loginform = LoginForm(request.GET if request.GET else None)
        return render(request, "login.html", {"form": loginform, "wrong": False})


@login_required(login_url=reverse_lazy("auth:login"))
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("auth:login"))


@login_required(login_url=reverse_lazy("auth:login"))
def profile(request):
    return render(request, "profile.html", {"username": request.user.username})