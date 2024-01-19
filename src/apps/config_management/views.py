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

                case "change_param":
                    new_value = request.POST.get('value', None)
                    param_id = request.POST.get('param_id', None)
                    param = Parameters.objects.get(id=param_id)
                    old_value = param.value

                    is_valid = fn.validate_parameter(request, param, new_value)

                    if "changes_dict" not in request.session.keys() or not request.session["changes_dict"]:
                        request.session["changes_dict"] = {}

                    changes_dict = request.session["changes_dict"]
                    if new_value == old_value:
                        changes_dict.pop(param_id)
                    else:
                        changes_dict[param_id] = { "id": param_id, "name": param.name, "new_value": new_value, "old_value": old_value, "is_valid": is_valid }

                    request.session["changes_dict"] = changes_dict

                    return JsonResponse({"old_val": old_value, "is_valid": is_valid})
                
                case "save_changes":
                    changes_dict = {}
                    if "changes_dict" in request.session.keys() and request.session["changes_dict"]:
                        changes_dict = request.session["changes_dict"]
                    msg = fn.save_changes(request, changes_dict)

                    request.session["changes_dict"] = None

                    resp = {"msg": msg}
                    return JsonResponse(resp)

        elif request.method == "GET":
            ajax_type = request.GET.get('type', None)
            page_n = 1
            match ajax_type:

                case "show_changes":
                    changes = []
                    if "changes_dict" not in request.session.keys() or not request.session["changes_dict"]:
                        changes = "No changes"
                        resp_type = "no_changes"
                    else:
                        resp_type = "ok"
                        changes = request.session["changes_dict"]
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
                    if "changes_dict" not in request.session.keys() or not request.session["changes_dict"]:
                        is_good = False
                    else:
                        changes = request.session["changes_dict"]
                        for key in changes.keys():
                            if not changes[key]["is_valid"]:
                                is_good = False
                                break
                    
                    resp = {"is_good": is_good}

                    return JsonResponse(resp)

                case "set_scope":
                    component_id = request.GET.get('component_id', None)
                    request.session["filter_scope"] = component_id

                case "reset_scope":
                    request.session["filter_scope"] = None

                case "page_select":
                    page_n = request.GET.get('page_n', 1)

                case "text_search":
                    request.session["search_str"] = request.GET.get('search_str', None)

                case "reset_text_search":
                    request.session["search_str"] = None
            
            params = None
            changes = None

            if "filter_scope" in request.session.keys() and request.session["filter_scope"]:
                component_id = request.session["filter_scope"]
                params = Parameters.objects.filter(file__instance__app__component_id=component_id).order_by("name")
            else: 
                params = Parameters.objects.all().order_by("name")
            
            if "search_str" in request.session.keys() and request.session["search_str"]:
                search_str = request.session["search_str"]
                params = params.filter(name__icontains=search_str).order_by("name")

            if "changes_dict" in request.session.keys() and request.session["changes_dict"]:
                changes = request.session["changes_dict"]

            paginatorr = Paginator(params, n_pages)

            results = []

            for par in paginatorr.page(page_n).object_list:
                results.append(par.get_dict_with_all_relative_fields())

            return JsonResponse({"results":results, "num_pages": paginatorr.num_pages, "page_n": page_n, "changes": changes})

    else:
        filter_scope = None
        search_str = None
        request.session["changes_dict"] = None
        if "filter_scope" in request.session.keys() and request.session["filter_scope"]:
            filter_scope = int(request.session["filter_scope"])
            component_id = request.session["filter_scope"]
            params = Parameters.objects.filter(file__instance__app__component_id=component_id).order_by("name")
        else: 
            params = Parameters.objects.all().order_by("name")

        if "search_str" in request.session.keys() and request.session["search_str"]:
                search_str = request.session["search_str"]
                params = params.filter(name__icontains=search_str).order_by("name")
        
        paginatorr = Paginator(params, n_pages)

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
        'filter_scope': filter_scope,
        'search_str': search_str,
        }

        return render(request, "config_management/configuration.html", context)

