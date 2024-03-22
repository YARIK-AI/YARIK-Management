from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpRequest, HttpResponse

from requests.exceptions import ConnectionError

from apps.config_management.models import File
from .request_handler import SyncRequestHandler, TasksRequestHandler
from .globals import SPN, RIPN, ROPN, RTYPE, QUEUE_ID
from .task_manager import TaskManager
from .models import Dag, Queue
from apps.decorators import no_running_tasks_required

from datetime import datetime as dttm

import logging

logger = logging.getLogger(__name__)


@login_required(login_url=reverse_lazy("auth:login"))
def page_503(request: HttpRequest):
    return render(request, "tasks/page-503.html")

@login_required(login_url=reverse_lazy("auth:login"))
def page_404(request: HttpRequest):
    return render(request, "tasks/page-404.html", status=404)


@login_required(login_url=reverse_lazy("auth:login"))
def tasks(request: HttpRequest):
    request_handler = TasksRequestHandler(request)
    w_request = request_handler.w_request

    if w_request.is_ajax and w_request.method_is_post:

        match w_request.ajax_type:

            case RTYPE.ABORT | RTYPE.RESTART: 
                request_handler.handle_task_action(w_request.ajax_type)

            case _:
                request_handler.handle_unknown_request_type()

    elif w_request.is_ajax and w_request.method_is_get:

        match w_request.ajax_type:

            case RTYPE.SHOW_LOGS:
                request_handler.handle_show_logs()

            case RTYPE.UPDATE_STATE:
                request_handler.handle_update_state() 

            case _:
                request_handler.handle_unknown_request_type()

    elif not w_request.is_ajax and w_request.method_is_post:
        request_handler.handle_post()

    elif not w_request.is_ajax and w_request.method_is_get:
        request_handler.handle_get()
        
    else:
        request_handler.handle_not_implemented()

    return request_handler.response


@login_required(login_url=reverse_lazy("auth:login"))
@no_running_tasks_required(redirect_url=reverse_lazy("tasks:tasks"))
def sync(request: HttpRequest):
    request_handler = SyncRequestHandler(request)
    w_request = request_handler.w_request

    if w_request.method_is_post:
        request_handler.handle_post()
    elif w_request.method_is_get:
        request_handler.handle_get()
    else:
        request_handler.handle_not_implemented()

    return request_handler.response
