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
        if request.method == 'POST':
            ajax_type = request.POST.get('type', None)
            match ajax_type:

                case "change_param" | "restore_default":
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
                        changes_dict[param_id] = { "id": param_id, "name": param.name, "new_value": new_value, "old_value": old_value, "is_valid": is_valid }

                    request.session["changes_dict"] = changes_dict

                    status_dict = fn.get_status_dict(changes_dict)

                    resp = {"old_val": old_value, "is_valid": is_valid, "status_dict": status_dict, "default_value": default_value}
                
                case "save_changes":
                    changes_dict = {}
                    if request.session.get("changes_dict", None):
                        changes_dict = request.session.get("changes_dict", None)
                    commit_msg = request.POST.get('commit_msg', None)
                    msg = fn.save_changes(request.session, changes_dict, commit_msg)

                    request.session["changes_dict"] = None

                    status_dict = fn.get_status_dict(None)

                    resp = {"msg": msg, "status_dict": status_dict}

            return JsonResponse(resp)
        
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
                
                case "check_for_errors":
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
                    
                    resp = {"is_good": is_good}

                    return JsonResponse(resp)
                
                case "show_status":
                    status_dict = fn.get_status_dict(request.session.get("changes_dict", None))
                    resp = {"status_dict": status_dict, "cur_status": request.session.get("filter_status", None)}
                    return JsonResponse(resp)

                case "set_scope":
                    component_id = request.GET.get('component_id', None)
                    request.session["filter_scope"] = component_id

                case "reset_scope":
                    request.session["filter_scope"] = None

                case "set_status":
                    request.session["filter_status"] = request.GET.get('filter_status', None)

                case "reset_status":
                    request.session["filter_status"] = None
                
                case "page_select":
                    page_n = request.GET.get('page_n', 1)

                case "text_search":
                    request.session["search_str"] = request.GET.get('search_str', None)

                case "reset_text_search":
                    request.session["search_str"] = None
            
            changes = request.session.get("changes_dict", None) 

            paginatorr = fn.get_paginator(request.session)

            results = []

            for par in paginatorr.page(page_n).object_list:
                results.append(par.get_dict_with_all_relative_fields())

            return JsonResponse({"results":results, "num_pages": paginatorr.num_pages, "page_n": page_n, "changes": changes, })

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
        }
        
        return render(request, "config_management/configuration.html", context)

