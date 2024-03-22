from django.http import HttpRequest, HttpResponse, JsonResponse

import logging

from apps.apps import RIPN_Base, ROPN_Base

logger = logging.getLogger(__name__)

class WrappedRequest:

    def __init__(self, request: HttpRequest, ajax_type_param_name: str):
        self.request = request
        self.ajax_type_param_name = ajax_type_param_name

    @property
    def method_is_get(self) -> bool:
        return self.request.method == "GET"
    
    @property
    def method_is_post(self) -> bool:
        return self.request.method == "POST"

    @property
    def is_ajax(self) -> bool:
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    @property
    def ajax_type(self) -> int | None:
        if not self.is_ajax:
            return None
        _type = None
        if self.method_is_post:
            _type = self.request.POST.get(self.ajax_type_param_name, None)
        elif self.method_is_get:
            _type = self.request.GET.get(self.ajax_type_param_name, None)
        if _type is None:
            return None
        return int(_type)
    
    @property
    def user_id(self) -> int:
        return self.request.user.id

    def get_par(self, name, default_value=None):
        """
        Get request parameter by name
        """
        if self.method_is_post:
            return self.request.POST.get(name, default_value)
        elif self.method_is_get:
            return self.request.GET.get(name, default_value)   

    def get_list(self, name, default_value=[]):
        if self.method_is_post:
            return self.request.POST.getlist(name, default_value)
        elif self.method_is_get:
            return self.request.GET.getlist(name, default_value)
        
    def has_par(self, name) -> bool:
        if self.method_is_post:
            return name in self.request.POST
        elif self.method_is_get:
            return name in self.request.GET

    def get_sesh_par(self, name, default_value=None):
        """
        Get session parameter by name
        """
        return self.request.session.get(name, default_value)
    
    def sesh_has_par(self, name) -> bool:
        """
        Check if session has parameter with name
        """
        return self.request.session.has_key(name)

    def set_sesh_par(self, name, new_value) -> None:
        """
        Set session parameter by name
        """
        self.request.session[name] = new_value

    def clear_sesh_par(self, name) -> None:
        self.set_sesh_par(name, None)

    def get_or_create_sesh_par(self, name:str, default_value=None):
        """
        Get session parameter by name or create if no exist
        """
        if self.sesh_has_par(name): # get
            return self.get_sesh_par(name, default_value) or default_value
        else: # create
            self.set_sesh_par(name, default_value)
            logger.info(f'Session parameter {name} initialized.')
            return default_value
        

class BaseRequestHandler:

    status = 200
    response = {}

    def __init__(self, request: HttpRequest):
        self.w_request = WrappedRequest(request, RIPN_Base.TYPE)

    def handle_not_implemented(self) -> None:
        self.status = 501
        self.response = HttpResponse("Not implemented", status=self.status)
        return
    
    def handle_unknown_request_type(self) -> None:
        self.status = 422
        self.response = JsonResponse({ ROPN_Base.MSG: "Request type not provided"}, status=self.status)
        return