from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Parameters
from . import functions as fn

from django.http import JsonResponse, HttpRequest

import logging

logger = logging.getLogger(__name__)

@login_required(login_url=reverse_lazy("auth:login"))
def index(request: HttpRequest):
    return redirect(reverse_lazy("cfg:configuration"))


@login_required(login_url=reverse_lazy("auth:login"))
def configuration(request: HttpRequest):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:

        status=200
        if request.method == 'POST':

            ajax_type = request.POST.get('type', None)
            match ajax_type:

                case "change_param":
                    status_dict = {}
                    is_valid = False
                    param_id = request.POST.get('param_id', None)
                    param = Parameters.objects.get(id=param_id)

                    default_value = param.default_value
                    old_value = param.value
                    
                    new_value = request.POST.get('value', default_value)

                    try:
                        is_valid = fn.validate_parameter(request.session.get('repo_path', None), param, new_value)
                        logger.info('Parameter is valid' if is_valid else 'The parameter is not valid')
                    except Exception as e:
                        logger.error(f'Error during parameter validation! {e}')
                    
                    if not request.session.get("changes_dict", None):
                        request.session["changes_dict"] = {}
                        logger.info(f'Session parameter "changes_dict" initialized.')

                    changes_dict = request.session.get("changes_dict", None)
                    filter_scope = request.session.get("filter_scope", None)
                    filter_status = request.session.get("filter_status", None)

                    if new_value == old_value:
                        changes_dict.pop(param_id)
                        logger.info(f'The original value was returned, so the parameter id={param_id} was removed from the changelog.')
                    else:
                        changes_dict[param_id] = {
                            "id": param_id,
                            "name": param.name,
                            "new_value": new_value,
                            "old_value": old_value,
                            "is_valid": is_valid,
                            "default_value": default_value 
                        }
                        logger.info(f'Change of parameter with id={param_id} recorded.')

                    request.session["changes_dict"] = changes_dict

                    try:
                        status_dict = fn.get_status_filter_items(filter_scope, changes_dict)
                        logger.info('Status filter updated.')
                    except Exception as e:
                        logger.error(f'Error while updating status filter! {e}')

                    results = []
                    paginatorr:Paginator = fn.get_paginator()
                    page_n = int(request.session.get("page_n", "1") or "1")

                    if filter_status:
                        
                        try:
                            paginatorr = fn.get_paginator(    
                                filter_scope = filter_scope,
                                filter_status = filter_status, 
                                search_str = request.session.get("search_str", None),
                                params_per_page = request.session.get("params_per_page", None), 
                                changes_dict = changes_dict,
                            )
                            logger.info('Parameters page has been created.')
                        except Exception as e:
                            logger.error(f'Error generating parameters page! {e}')
                            paginatorr = fn.get_paginator()
                        

                        if page_n > paginatorr.num_pages:
                            page_n = paginatorr.num_pages
                            request.session["page_n"] = page_n

                        for par in paginatorr.page(page_n).object_list:
                            results.append(par.get_dict_with_all_relative_fields())

                    resp = {
                        "old_val": old_value,
                        "is_valid": is_valid, 
                        "status_dict": status_dict, 
                        "default_value": default_value,
                        "filter_status": filter_status,
                        "results": results, 
                        "num_pages": paginatorr.num_pages, 
                        "page_n": page_n, 
                        "changes": changes_dict,
                    }
                
                case "save_changes":
                    msg = ""
                    status_dict = {}
                    changes = []
                    change_manager = fn.ChangeManager(request.session.get("changes_dict", None))
                    is_good = change_manager.is_not_empty and change_manager.is_all_valid

                    if is_good:
                        logger.info('Saving allowed.')
                        repo_path = request.session.get("repo_path", None)
                        commit_msg = request.POST.get('commit_msg', None)

                        try:
                            msg = fn.save_changes(repo_path, change_manager.get_dict(), commit_msg)
                            logger.info('Changes saved.')
                        except Exception as e:
                            logger.error(f'Error while saving changes! {e}')
                            msg = "Error while saving changes!"

                        request.session["changes_dict"] = None
                        try:
                            status_dict = fn.get_status_filter_items()
                            logger.info('Status filter updated.')
                        except Exception as e:
                            logger.error(f'Error while updating status filter! {e}')

                    else:
                        logger.warning('Saving prevented (no changes or some parameter is not valid).')
                        filter_scope = request.session.get("filter_scope", None)
                        msg = "Error: some of the parameters are not valid!"
                        try:
                            status_dict = fn.get_status_filter_items(filter_scope, change_manager.get_dict())
                            logger.info('Status filter updated.')
                        except Exception as e:
                            logger.error(f'Error while updating status filter! {e}')
                        status = 422
                        
                    resp = {
                        "msg": msg,
                        "status_dict": status_dict
                    }

            return JsonResponse(resp, status=status)
        
        elif request.method == "GET":
            ajax_type = request.GET.get('type', None)
            page_n = int(request.session.get("page_n", "1") or "1")

            match ajax_type:

                case "show_changes":
                    changes = []
                    if not request.session.get("changes_dict", None):
                        logger.info('There are no changed parameters yet.')
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
                            logger.info('Some parameter changes are not valid, a list of them will be returned.')
                            resp_type = "errors"
                            changes = wrong_changes_dict
                        else:
                            logger.info('A list of valid changes will be returned.')
                    
                    resp = {"changes": changes, "type": resp_type}

                    return JsonResponse(resp)
                
                case "show_filter_list":
                    filter_items = {}
                    selected_item = None

                    filter_scope = request.session.get("filter_scope", None)
                    filter_status = request.session.get("filter_status", None)
                    changes_dict = request.session.get("changes_dict", None)

                    if not request.GET.get('filter_id', None):
                        logger.error('The filter type was not passed.')
                        status = 422
                    if request.GET.get('filter_id', None) == 'collapseListScope':
                        try:
                            filter_items = fn.get_scope_filter_items(filter_status, changes_dict)
                            logger.info('Scope filter generated.')
                        except Exception as e:
                            logger.error(f'Error while generating the scope filter! {e}')
                        selected_item = filter_scope
                    elif request.GET.get('filter_id', None) == 'collapseListStatus':
                        try:
                            filter_items = fn.get_status_filter_items(filter_scope, changes_dict)
                            logger.info('Status filter generated.')
                        except Exception as e:
                            logger.error(f'Error while generating the status filter! {e}')
                        selected_item = filter_status

                    resp = {"filter_items": filter_items, "selected_item": selected_item}

                    return JsonResponse(resp, status=status)

                case "set_scope" | "set_status":
                    filter_name = request.GET.get('filter_name', None)
                    filter_value = request.GET.get('filter_value', None)
                    if filter_name and filter_value:
                        request.session[filter_name] = filter_value
                    logger.info(f'Filter "{filter_name}" set.')

                case "reset_scope" | "reset_status":
                    filter_name = request.GET.get('filter_name', None)
                    if filter_name:
                        request.session[filter_name] = None
                    logger.info(f'Filter "{filter_name}" reset.')

                case "page_select":
                    page_n = int(request.GET.get('page_n', "1") or "1")
                    request.session["page_n"] = page_n
                    logger.info(f'Page {page_n} selected.')

                case "text_search":
                    request.session["search_str"] = request.GET.get('search_str', None)
                    logger.info('Search string set.')

                case "reset_text_search":
                    request.session["search_str"] = None

                case "set_params_per_page":
                    request.session["params_per_page"] = request.GET.get('params_per_page', "10")
                    logger.info('The number of parameters per page is set.')
            
            filter_scope = int(request.session.get("filter_scope", "0") or "0")
            filter_status = request.session.get("filter_status", None)
            search_str = request.session.get("search_str", None)
            params_per_page = int(request.session.get("params_per_page", "10") or "10")
            changes = request.session.get("changes_dict", None)

            try:
                paginatorr = fn.get_paginator(    
                    filter_scope = filter_scope,
                    filter_status = filter_status, 
                    search_str = search_str,
                    params_per_page = params_per_page, 
                    changes_dict = changes,
                )
                logger.info('Parameters page has been created.')
            except Exception as e:
                logger.error(f'Error generating parameters page! {e}')
                paginatorr = fn.get_paginator()

            results = []

            if page_n > paginatorr.num_pages:
                page_n = paginatorr.num_pages
                request.session["page_n"] = page_n

            for par in paginatorr.page(page_n).object_list:
                results.append(par.get_dict_with_all_relative_fields())

            return JsonResponse({"results":results, "num_pages": paginatorr.num_pages, "page_n": page_n, "changes": changes, }, status=status)

    else:
        request.session["changes_dict"] = None
        
        filter_scope = int(request.session.get("filter_scope", "0") or "0")
        filter_status = request.session.get("filter_status", None)
        search_str = request.session.get("search_str", None)
        params_per_page = int(request.session.get("params_per_page", "10") or "10")
        changes_dict = request.session.get("changes_dict", None)
        page_n = int(request.session.get("page_n", "1") or "1")


        status_dict = fn.get_status_filter_items(filter_scope, changes_dict)

        if status_dict.get(filter_status) and status_dict.get(filter_status).get("cnt") == 0:
            filter_status = None
            request.session["filter_status"] = None


        try:
            paginatorr = fn.get_paginator(    
                filter_scope = filter_scope,
                filter_status = filter_status, 
                search_str = search_str,
                params_per_page = params_per_page, 
                changes_dict = changes_dict,
            )
            logger.info('Parameters page has been created.')
        except Exception as e:
                logger.error(f'Error generating parameters page! {e}')
                paginatorr = fn.get_paginator()
    
        if page_n > paginatorr.num_pages:
            page_n = paginatorr.num_pages
            request.session["page_n"] = page_n


        context = {
            'page_obj': paginatorr.page(page_n),
            'params': paginatorr.page(page_n).object_list,
            'filter_scope': int(request.session.get("filter_scope", "0") or "0"),
            'filter_status': request.session.get("filter_status", None),
            'search_str': request.session.get("search_str", None),
            'params_per_page': request.session.get("params_per_page", "10") or "10",
        }
        
        return render(request, "config_management/configuration.html", context)

