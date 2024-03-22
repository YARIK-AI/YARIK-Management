from functools import wraps
from django.http import HttpResponseRedirect
from .globals import SPN_Base

import logging

logger = logging.getLogger(__name__)


def no_running_tasks_required(redirect_url='/'):
    def decorator(view_function):
        @wraps(view_function)
        def _wrapped_view(request, *args, **kwargs):
            if not bool(request.session.get(SPN_Base.SYNC_IN_PROGRESS, False)):
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(redirect_url)
        return _wrapped_view
    return decorator


def finish_queue_required(redirect_url='/'):
    def decorator(view_function):
        @wraps(view_function)
        def _wrapped_view(request, *args, **kwargs):
            if not bool(request.session.get(SPN_Base.SYNC_IN_PROGRESS, False)) and not bool(request.session.get(SPN_Base.ALLOW_VIEW_TASKS, False)):
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(redirect_url)
        return _wrapped_view
    return decorator