# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

from django.contrib.auth.views import LogoutView

from . import views

app_name="auth_app"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
