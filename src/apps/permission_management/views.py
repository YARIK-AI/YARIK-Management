from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from django.http import HttpResponse, JsonResponse, HttpRequest

import logging

logger = logging.getLogger(__name__)

@login_required(login_url=reverse_lazy("auth:login"))
def permissions(request: HttpRequest):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        status=200
        if request.method == 'POST':

            ajax_type = request.POST.get('type', None)
            match ajax_type:
                case _: return HttpResponse('resp')
        elif request.method == "GET":

            ajax_type = request.GET.get('type', None)
            match ajax_type:
                case _: return HttpResponse('resp')

    else:
        return HttpResponse('resp')