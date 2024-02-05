# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.http import HttpResponseRedirect, HttpRequest
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse, reverse_lazy

import logging

logger = logging.getLogger(__name__)

def login_view(request: HttpRequest):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f'User {user.username} is authenticated.')
                return redirect(reverse_lazy("cfg:configuration"))
            else:
                logger.warning(f'User {user.username} entered incorrect credentials.')
                msg = 'Invalid credentials'
        else:
            logger.info('Login form validation error.')
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


@login_required(login_url=reverse_lazy("auth:login"))
def logout_view(request: HttpRequest):
    user = request.user.username
    logout(request)
    logger.info(f'User {user} logout.')
    return HttpResponseRedirect(reverse("auth:login"))

