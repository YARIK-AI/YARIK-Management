from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .models import Components, Parameters
from . import functions as fn

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count


@login_required(login_url=reverse_lazy("auth:login"))
def configuration(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    n_pages = 15
    if is_ajax:
        status=200
        if request.method == 'POST':
            ajax_type = request.POST.get('type', None)
            match ajax_type:

                case "change_param":
                    param_id = request.POST.get('param_id', None)

                    param = Parameters.objects.get(id=param_id)
                    default_value = param.default_value
                    old_value = param.value
                    
                    new_value = request.POST.get('value', default_value)

                    is_valid = fn.validate_parameter(request.session, param, new_value)

                    if not request.session.get("changes_dict", None):
                        request.session["changes_dict"] = {}

                    changes_dict = request.session.get("changes_dict", None)
                    if new_value == old_value:
                        changes_dict.pop(param_id)
                    else:
                        changes_dict[param_id] = {
                            "id": param_id,
                            "name": param.name,
                            "new_value": new_value,
                            "old_value": old_value,
                            "is_valid": is_valid,
                            "default_value": default_value 
                        }

                    request.session["changes_dict"] = changes_dict

                    status_dict = fn.get_status_filter_items(request.session.get("filter_scope", None), changes_dict)

                    resp = {
                        "old_val": old_value,
                        "is_valid": is_valid, 
                        "status_dict": status_dict, 
                        "default_value": default_value
                    }
                
                case "save_changes":
                    is_good = True
                    changes = []
                    if not request.session.get("changes_dict", None):
                        is_good = False
                    else:
                        changes = request.session.get("changes_dict", None)
                        for key in changes.keys():
                            if not changes[key]["is_valid"]:
                                is_good = False
                                break
                    if is_good:
                        changes_dict = {}
                        if request.session.get("changes_dict", None):
                            changes_dict = request.session.get("changes_dict", None)
                        commit_msg = request.POST.get('commit_msg', None)
                        msg = fn.save_changes(request.session, changes_dict, commit_msg)

                        request.session["changes_dict"] = None

                        status_dict = fn.get_status_filter_items()
                    else:
                        msg = "Error: some of the parameters are not valid!"
                        status_dict = fn.get_status_filter_items(request.session.get("filter_scope", None), request.session.get("changes_dict", None))
                        status = 422
                    resp = {
                        "msg": msg,
                        "status_dict": status_dict
                    }

            return JsonResponse(resp, status=status)
        
        elif request.method == "GET":
            ajax_type = request.GET.get('type', None)
            page_n = 1
            match ajax_type:

                case "show_changes":
                    changes = []
                    if not request.session.get("changes_dict", None):
                        changes = "No changes"
                        resp_type = "no_changes"
                    else:
                        resp_type = "ok"
                        changes = request.session.get("changes_dict", None)
                        wrong_changes_dict = {}
                        for key in changes.keys():
                            if not changes[key]["is_valid"]:
                                wrong_changes_dict[key] = changes[key]

                        if len(wrong_changes_dict) > 0:
                            resp_type = "errors"
                            changes = wrong_changes_dict
                    
                    resp = {"changes": changes, "type": resp_type}

                    return JsonResponse(resp)
                
                case "show_filter_list": # need refactoring
                    filter_items = None
                    selected_item = None
                    if not request.GET.get('filter_id', None):
                        status = 422
                    if request.GET.get('filter_id', None) == 'collapseListScope':
                        filter_items = fn.get_scope_filter_items(request.session.get("filter_status", None), request.session.get("changes_dict", None))
                        selected_item = request.session.get("filter_scope", None)
                    elif request.GET.get('filter_id', None) == 'collapseListStatus':
                        filter_items = fn.get_status_filter_items(request.session.get("filter_scope", None), request.session.get("changes_dict", None))
                        selected_item = request.session.get("filter_status", None)

                    resp = {"filter_items": filter_items, "selected_item": selected_item}
                    return JsonResponse(resp, status=status)

                case "set_scope" | "set_status":
                    filter_name = request.GET.get('filter_name', None)
                    filter_value = request.GET.get('filter_value', None)
                    if filter_name and filter_value:
                        request.session[filter_name] = filter_value

                case "reset_scope" | "reset_status":
                    filter_name = request.GET.get('filter_name', None)
                    if filter_name:
                        request.session[filter_name] = None
                
                case "page_select":
                    page_n = request.GET.get('page_n', 1)

                case "text_search":
                    request.session["search_str"] = request.GET.get('search_str', None)

                case "reset_text_search":
                    request.session["search_str"] = None

                case "set_params_per_page":
                    request.session["params_per_page"] = request.GET.get('params_per_page', "10")
            
            changes = request.session.get("changes_dict", None) 

            paginatorr = fn.get_paginator(request.session)

            results = []

            for par in paginatorr.page(page_n).object_list:
                results.append(par.get_dict_with_all_relative_fields())

            return JsonResponse({"results":results, "num_pages": paginatorr.num_pages, "page_n": page_n, "changes": changes, }, status=status)

    else:
        request.session["changes_dict"] = None
        
        paginatorr = fn.get_paginator(request.session)
    
        context = {
        'page_obj': paginatorr.page(1),
        'params': paginatorr.page(1).object_list,
        'components': (
                    Components.objects
                    .values("id", "name")
                    .annotate(cnt=Count("applications__instances__files__parameters"))
                    .filter(cnt__gt=0)
                    .order_by("-cnt")
                ),
        'filter_scope': int(request.session.get("filter_scope", "0") or "0"),
        'filter_status': request.session.get("filter_status", None),
        'search_str': request.session.get("search_str", None),
        'params_per_page': request.session.get("params_per_page", "10") or "10",
        }
        
        return render(request, "config_management/configuration.html", context)

