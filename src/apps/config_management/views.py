from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest

from .models import Parameter
from . import functions as fn
from .globals import SPN, RIPN, ROPN, RTYPE, FILTERS


import logging

logger = logging.getLogger(__name__)

@login_required(login_url=reverse_lazy("auth:login"))
def index(request: HttpRequest):
    return redirect(reverse_lazy("cfg:configuration"))


@login_required(login_url=reverse_lazy("auth:login"))
def configuration(request: HttpRequest):
    user_id = request.user.id
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:

        status=200
        resp = {}
        if request.method == 'POST':

            ajax_type = int(request.POST.get(RIPN.TYPE, None))
            match ajax_type:

                case RTYPE.CHANGE:
                    status_dict = {}
                    is_valid = False
                    param_id = request.POST.get(RIPN.PARAM_ID, None)
                    param = Parameter.objects.get(id=param_id)

                    if param.can_change(User.objects.get(id=user_id)):

                        default_value = param.default_value
                        old_value = param.value
                        
                        new_value = request.POST.get(RIPN.VALUE, default_value)

                        try:
                            is_valid = fn.validate_parameter(
                                request.session.get(SPN.REPO_PATH, None),
                                param,
                                new_value
                            )
                            logger.info(
                                'Parameter is valid' if is_valid 
                                else 'The parameter is not valid'
                            )
                        except Exception as e:
                            logger.error(f'Error during parameter validation! {e}')
                        
                        if not request.session.get(SPN.CHANGES, None):
                            request.session[SPN.CHANGES] = {}
                            logger.info(f'Session parameter {SPN.CHANGES} initialized.')

                        changes_dict = request.session.get(SPN.CHANGES, None)
                        filter_scope = request.session.get(SPN.SCOPE, None)
                        filter_status = request.session.get(SPN.STATUS, None)

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

                        request.session[SPN.CHANGES] = changes_dict

                        try:
                            status_dict = fn.get_status_filter_items(user_id=user_id, filter_scope=filter_scope, changes_dict=changes_dict)
                            logger.info('Status filter updated.')
                        except Exception as e:
                            logger.error(f'Error while updating status filter! {e}')

                        results = []
                        paginatorr:Paginator = fn.get_paginator(user_id=user_id)
                        page_n = int(request.session.get(SPN.PAGE_N, "1") or "1")

                        if filter_status:
                            
                            try:
                                paginatorr = fn.get_paginator(    
                                    filter_scope = filter_scope,
                                    filter_status = filter_status, 
                                    search_str = request.session.get(SPN.SEARCH, None),
                                    params_per_page = request.session.get(SPN.PER_PAGE, "10") or "10", 
                                    changes_dict = changes_dict,
                                    user_id=user_id,
                                )
                                logger.info('Parameters page has been created.')
                            except Exception as e:
                                logger.error(f'Error generating parameters page! {e}')
                                paginatorr = fn.get_paginator(user_id=user_id)
                            

                            if page_n > paginatorr.num_pages:
                                page_n = paginatorr.num_pages
                                request.session[SPN.PAGE_N] = page_n

                            for par in paginatorr.page(page_n).object_list:
                                results.append(par.get_dict_with_all_relative_fields())

                        resp = {
                            ROPN.PREV_VAL: old_value,
                            ROPN.IS_VALID: is_valid, 
                            ROPN.STATUS_FILTER: status_dict, 
                            ROPN.DEFAULT_VAL: default_value,
                            ROPN.STATUS: filter_status,
                            ROPN.LIST_EL: results, 
                            ROPN.NUM_PAGES: paginatorr.num_pages, 
                            ROPN.PAGE_N: page_n, 
                            ROPN.CHANGES: changes_dict,
                        }
                    else: 
                        status = 422
                        resp = {
                            ROPN.MSG: "Changes are not possible without appropriate permission"
                        }
                
                case RTYPE.SAVE:
                    msg = ""
                    status_dict = {}
                    changes = []
                    change_manager = fn.ChangeManager(request.session.get(SPN.CHANGES, None))
                    is_good = change_manager.is_not_empty and change_manager.is_all_valid

                    if is_good:
                        logger.info('Saving allowed.')
                        repo_path = request.session.get(SPN.REPO_PATH, None)
                        commit_msg = request.POST.get(RIPN.COMMIT_MSG, None)

                        try:
                            msg = fn.save_changes(repo_path, change_manager.get_dict(), commit_msg)
                            logger.info('Changes saved.')
                        except Exception as e:
                            logger.error(f'Error while saving changes! {e}')
                            msg = "Error while saving changes!"

                        request.session[SPN.CHANGES] = None
                        try:
                            status_dict = fn.get_status_filter_items(user_id=user_id)
                            logger.info('Status filter updated.')
                        except Exception as e:
                            logger.error(f'Error while updating status filter! {e}')

                    else:
                        logger.warning('Saving prevented (no changes or some parameter is not valid).')
                        filter_scope = request.session.get(SPN.SCOPE, None)
                        msg = "Error: some of the parameters are not valid!"
                        try:
                            status_dict = fn.get_status_filter_items(user_id=user_id, filter_scope=filter_scope, changes_dict=change_manager.get_dict())
                            logger.info('Status filter updated.')
                        except Exception as e:
                            logger.error(f'Error while updating status filter! {e}')
                        status = 422
                        
                    resp = {
                        ROPN.STATUS_FILTER: status_dict,
                        ROPN.MSG: msg,
                    }

            return JsonResponse(resp, status=status)
        
        elif request.method == "GET":
            ajax_type = int(request.GET.get(RIPN.TYPE, None))
            page_n = int(request.session.get(SPN.PAGE_N, "1") or "1")

            match ajax_type:

                case RTYPE.SHOW_CHANGES:
                    changes = []
                    if not request.session.get(SPN.CHANGES, None):
                        logger.info('There are no changed parameters yet.')
                        changes = "No changes"
                        resp_type = "no_changes"
                    else:
                        resp_type = "ok"
                        changes = request.session.get(SPN.CHANGES, None)
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
                    
                    resp = {
                        ROPN.CHANGES: changes,
                        ROPN.TYPE: resp_type
                    }

                    return JsonResponse(resp)
                
                case RTYPE.SHOW_FILTER:
                    filter_items = {}
                    selected_item = None

                    filter_scope = request.session.get(SPN.SCOPE, None)
                    filter_status = request.session.get(SPN.STATUS, None)
                    changes_dict = request.session.get(SPN.CHANGES, None)

                    if not request.GET.get(RIPN.FILTER_ID, None):
                        logger.error('The filter type was not passed.')
                        status = 422
                    filter_id = int(request.GET.get(RIPN.FILTER_ID, None))
                    match filter_id:
                        case FILTERS.SCOPE:
                            try:
                                filter_items = fn.get_scope_filter_items(user_id=user_id, filter_status=filter_status, changes_dict=changes_dict)
                                logger.info('Scope filter generated.')
                            except Exception as e:
                                logger.error(f'Error while generating the scope filter! {e}')
                            selected_item = filter_scope
                        case FILTERS.STATUS:
                            try:
                                filter_items = fn.get_status_filter_items(user_id=user_id, filter_scope=filter_scope, changes_dict=changes_dict)
                                logger.info('Status filter generated.')
                            except Exception as e:
                                logger.error(f'Error while generating the status filter! {e}')
                            selected_item = filter_status
                    resp = {
                        ROPN.FILTER_ITEMS: filter_items,
                        ROPN.SELECTED_ITEM: selected_item
                    }

                    return JsonResponse(resp, status=status)

                case RTYPE.SET_SCOPE | RTYPE.SET_STATUS:
                    filter_ids = {
                        1: SPN.SCOPE,
                        2: SPN.STATUS
                    }
                    filter_name = filter_ids[int(request.GET.get(RIPN.FILTER_ID, None))]
                    filter_value = request.GET.get(RIPN.FILTER_VALUE, None)
                    if filter_name and filter_value:
                        request.session[filter_name] = filter_value
                    logger.info(f'Filter "{filter_name}" set.')

                case RTYPE.RESET_SCOPE | RTYPE.RESET_STATUS:
                    filter_ids = {
                        1: SPN.SCOPE,
                        2: SPN.STATUS
                    }
                    filter_name = filter_ids[int(request.GET.get(RIPN.FILTER_ID, None))]
                    if filter_name:
                        request.session[filter_name] = None
                    logger.info(f'Filter "{filter_name}" reset.')

                case RTYPE.SELECT_PAGE:
                    page_n = int(request.GET.get(RIPN.PAGE_N, "1") or "1")
                    request.session[SPN.PAGE_N] = page_n
                    logger.info(f'Page {page_n} selected.')

                case RTYPE.SET_SEARCH:
                    request.session[SPN.SEARCH] = request.GET.get(RIPN.SEARCH, None)
                    logger.info('Search string set.')

                case RTYPE.RESET_SEARCH:
                    request.session[SPN.SEARCH] = None

                case RTYPE.SET_PER_PAGE:
                    request.session[SPN.PER_PAGE] = request.GET.get(RIPN.PER_PAGE, "10")
                    logger.info('The number of parameters per page is set.')
            
            filter_scope = int(request.session.get(SPN.SCOPE, "0") or "0")
            filter_status = request.session.get(SPN.STATUS, None)
            search_str = request.session.get(SPN.SEARCH, None)
            params_per_page = int(request.session.get(SPN.PER_PAGE, "10") or "10")
            changes = request.session.get(SPN.CHANGES, None)

            try:
                paginatorr = fn.get_paginator(    
                    filter_scope = filter_scope,
                    filter_status = filter_status, 
                    search_str = search_str,
                    params_per_page = params_per_page, 
                    changes_dict = changes,
                    user_id=user_id,
                )
                logger.info('Parameters page has been created.')
            except Exception as e:
                logger.error(f'Error generating parameters page! {e}')
                paginatorr = fn.get_paginator(user_id=user_id)

            results = []

            if page_n > paginatorr.num_pages:
                page_n = paginatorr.num_pages
                request.session[SPN.PAGE_N] = page_n

            for par in paginatorr.page(page_n).object_list:
                results.append(
                    par.get_dict_with_all_relative_fields(
                        User.objects.get(id=user_id)
                    )
                )
            resp = {
                ROPN.LIST_EL: results,
                ROPN.NUM_PAGES: paginatorr.num_pages, 
                ROPN.PAGE_N: page_n, 
                ROPN.CHANGES: changes,
            }
            return JsonResponse(resp, status=status)

    else:
        request.session[SPN.CHANGES] = None
        
        filter_scope = int(request.session.get(SPN.SCOPE, "0") or "0")
        filter_status = request.session.get(SPN.STATUS, None)
        search_str = request.session.get(SPN.SEARCH, None)
        params_per_page = int(request.session.get(SPN.PER_PAGE, "10") or "10")
        page_n = int(request.session.get(SPN.PAGE_N, "1") or "1")


        status_dict = fn.get_status_filter_items(
            user_id=user_id, 
            filter_scope=filter_scope
        )

        if (
            status_dict.get(filter_status) 
            and status_dict.get(filter_status).get("cnt") == 0
        ):
            request.session[SPN.STATUS] = filter_status = None


        try:
            paginatorr = fn.get_paginator(    
                filter_scope = filter_scope,
                filter_status = filter_status, 
                search_str = search_str,
                params_per_page = params_per_page, 
                user_id=user_id,
            )
            logger.info('Parameters page has been created.')
        except Exception as e:
                logger.error(f'Error generating parameters page! {e}')
                paginatorr = fn.get_paginator(user_id=user_id)
    
        if page_n > paginatorr.num_pages:
            request.session[SPN.PAGE_N] = page_n = paginatorr.num_pages


        context = {
            'page_obj': paginatorr.page(page_n),
            'params': paginatorr.page(page_n).object_list,
            'filter_scope': filter_scope,
            'filter_status': filter_status,
            'search_str': search_str,
            'params_per_page': params_per_page,
        }
        
        return render(request, "config_management/configuration.html", context)

