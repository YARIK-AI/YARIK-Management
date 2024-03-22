from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpRequest

from .globals import RTYPE
from .request_handler import ConfigurationRequestHandler
from apps.decorators import finish_queue_required

import logging

logger = logging.getLogger(__name__)

@login_required(login_url=reverse_lazy("auth:login"))
def index(request: HttpRequest):
    return redirect(reverse_lazy("cfg:configuration"))


@login_required(login_url=reverse_lazy("auth:login"))
@finish_queue_required(redirect_url=reverse_lazy("tasks:tasks"))
def configuration(request: HttpRequest):
    request_handler = ConfigurationRequestHandler(request)
    w_request = request_handler.w_request

    if w_request.is_ajax and w_request.method_is_post:

        match w_request.ajax_type:
            
            case RTYPE.CHANGE:
                request_handler.handle_change()

            case RTYPE.SAVE:
                request_handler.handle_save()
            
            case _:
                request_handler.handle_unknown_request_type()

    elif w_request.is_ajax and w_request.method_is_get:

        match w_request.ajax_type:

            case RTYPE.SHOW_CHANGES:
                request_handler.handle_show_changes()

            case RTYPE.SHOW_FILTER:
                request_handler.handle_show_filter()

            case RTYPE.SET_SCOPE | RTYPE.SET_STATUS:
                request_handler.handle_set_filter()

            case RTYPE.RESET_SCOPE | RTYPE.RESET_STATUS:
                request_handler.handle_reset_filter()

            case RTYPE.SELECT_PAGE:
                request_handler.handle_select_page()

            case RTYPE.SET_SEARCH:
                request_handler.handle_set_search()

            case RTYPE.RESET_SEARCH:
                request_handler.handle_reset_search()

            case RTYPE.SET_PER_PAGE:
                request_handler.handle_set_per_page()
            
            case _:
                request_handler.handle_unknown_request_type()

    elif not w_request.is_ajax and w_request.method_is_get:
        request_handler.handle_get()

    else:
        request_handler.handle_not_implemented()
    
    return request_handler.response
