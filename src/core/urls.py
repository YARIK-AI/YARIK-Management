# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.config_management.urls", namespace="cfg")),
    path("", include("apps.permission_management.urls", namespace="perm")),
    path("", include("apps.authentication.urls", namespace="auth")),
]
