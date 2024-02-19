from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.http import HttpResponse, JsonResponse, HttpRequest

from apps.config_management.models import Parameter
from .globals import SPN, RIPN, ROPN, RTYPE, PERMS

import logging

logger = logging.getLogger(__name__)


@staff_member_required(login_url=reverse_lazy("auth:login"))
@login_required(login_url=reverse_lazy("auth:login"))
def permissions(request: HttpRequest):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        status=200

        perm_changes_dict: dict[str, dict] = request.session.get(SPN.CHANGES)

        if request.method == 'POST':

            ajax_type = int(request.POST.get(RIPN.TYPE, "0"))

            match ajax_type:
                case RTYPE.CHANGE:
                    group_id = request.POST.get(RIPN.GROUP_ID)
                    param_id = request.POST.get(RIPN.PARAM_ID)
                    perm_id = request.POST.get(RIPN.PERM_ID)

                    cur_param = Parameter.objects.get(id=param_id)
                    cur_group = Group.objects.get(id=group_id)
                    cur_perm = cur_param.get_permission_level(cur_group)

                    selected_perm = cur_perm

                    if perm_id:
                        selected_perm = PERMS[int(perm_id)]

                    logger.info(f'Backend recieved group_id={group_id}, param_id={param_id}, perm={perm_id}')
                    
                    perm_changes_dict: dict[str, dict] = request.session.get(SPN.CHANGES)

                    if not perm_changes_dict:
                        perm_changes_dict = {}

                    if group_id not in perm_changes_dict.keys():
                        perm_changes_dict[group_id] = {}
                        perm_changes_dict[group_id]['name'] = cur_group.name
                        perm_changes_dict[group_id]['changes'] = {}
                    
                    if param_id not in perm_changes_dict[group_id]['changes'].keys():
                        perm_changes_dict[group_id]['changes'][param_id] = {}

                    if selected_perm != cur_perm:
                        perm_changes_dict[group_id]['changes'][param_id]['new_value'] = selected_perm
                        perm_changes_dict[group_id]['changes'][param_id]['old_value'] = cur_perm
                        perm_changes_dict[group_id]['changes'][param_id]['name'] = cur_param.name
                    else:
                        perm_changes_dict[group_id]['changes'].pop(param_id)
                        if len(perm_changes_dict[group_id]['changes'].keys()) == 0:
                            perm_changes_dict.pop(group_id)
                    request.session[SPN.CHANGES] = perm_changes_dict

                    changes = {}
                    if group_id in perm_changes_dict.keys():
                        changes = perm_changes_dict[group_id]['changes']

                    resp = {
                        ROPN.PREV_VAL: cur_perm,
                        ROPN.CHANGES: changes,
                    }

                    return JsonResponse(resp)
                
                case RTYPE.SAVE:
                    status = 200
                    msg = "e"

                    if perm_changes_dict and len(perm_changes_dict) > 0:
                        for group_id, group in perm_changes_dict.items():
                            cur_group = Group.objects.get(id=group_id)
                            for param_id, single_change in group['changes'].items():
                                cur_param = Parameter.objects.get(id=param_id)
                                cur_param.set_permission_level(cur_group, single_change['new_value'])
                        msg = "Object permissions for selected groups have been applied."
                    else:
                        msg = "No changes"
                        status = 422

                    request.session[SPN.CHANGES] = None

                    resp = {
                        ROPN.MSG: msg
                    }

                    return JsonResponse(resp, status=status)

                case _: return HttpResponse('resp')
        elif request.method == "GET":

            ajax_type = int(request.GET.get(RIPN.TYPE, "0"))

            page_n = int(request.session.get(SPN.PAGE_N, "1") or "1")
            group_id = request.session.get(SPN.GROUP_ID, None)
            params_per_page = int(request.session.get(SPN.PER_PAGE, "10") or "10")
            search_str = request.session.get(SPN.SEARCH, None)

            match ajax_type:

                case RTYPE.SHOW_CHANGES:
                    changes = request.session.get(SPN.CHANGES, {})
                    if not changes:
                        logger.info('There are no changed permissions yet.')
                        changes = "No changes"
                        resp_type = "no_changes"
                    else:
                        resp_type = "ok"
                        logger.info('A list of permission changes will be returned.')
                    
                    resp = {
                        ROPN.CHANGES: changes,
                        ROPN.TYPE: resp_type
                    }

                    return JsonResponse(resp)

                case RTYPE.SELECT_GROUP:
                    group_id = request.GET.get(RIPN.GROUP_ID)
                    request.session[SPN.GROUP_ID] = group_id
                    page_n = 1
                    request.session[SPN.PAGE_N] = 1

                
                case RTYPE.SELECT_PAGE:
                    page_n = int(request.GET.get(RIPN.PAGE_N, "1") or "1")
                    request.session[SPN.PAGE_N] = page_n
                    logger.info(f'Page {page_n} selected.')

                case RTYPE.SET_SEARCH:
                    search_str = request.GET.get(RIPN.SEARCH, None)
                    request.session[SPN.SEARCH] = search_str
                    logger.info('Search string set.')

                case RTYPE.RESET_SEARCH:
                    request.session[SPN.SEARCH] = search_str = None

                case RTYPE.SET_PER_PAGE:
                    params_per_page = request.GET.get(RIPN.PER_PAGE, "10")
                    request.session[SPN.PER_PAGE] = params_per_page
                    logger.info('The number of parameters per page is set.')

                case _: 
                    return HttpResponse('resp')

            group = None
            if group_id:
                group = Group.objects.get(id=group_id)

            params = Parameter.objects.all().order_by("id") if group else Parameter.objects.none()

            if search_str:
                q1 = params.filter(name__icontains=search_str)
                q2 = params.filter(id__icontains=search_str)
                params = q1.union(q2).order_by("id")


            try:
                paginatorr = Paginator(params, params_per_page)
                logger.info('Parameters page has been created.')
            except Exception as e:
                    logger.error(f'Error generating parameters page! {e}')
        
            if page_n > paginatorr.num_pages:
                page_n = paginatorr.num_pages
                request.session[SPN.PAGE_N] = page_n

            dict_par_perm: list[str, dict[str, str]] = []

            for par in paginatorr.page(page_n).object_list:
                td = {"id": par.id, "name": par.name, "description": par.description, "perm": None, "perm_is_changed": False}
                if perm_changes_dict is not None and group_id in perm_changes_dict.keys() and str(par.id) in perm_changes_dict[group_id]["changes"].keys():
                    td["perm"] = perm_changes_dict[group_id]["changes"][str(par.id)]["new_value"]
                    td["perm_is_changed"] = True
                else:
                    td["perm"] = par.get_permission_level(group)
                dict_par_perm.append(td)


            resp = {
                ROPN.LIST_EL: dict_par_perm,
                ROPN.PAGE_N: page_n,
                ROPN.NUM_PAGES: paginatorr.num_pages,
            }

            return JsonResponse(resp)

    else:
        group_id = request.session.get(SPN.GROUP_ID, None)
        page_n = int(request.session.get(SPN.PAGE_N, "1") or "1")
        params_per_page = int(request.session.get(SPN.PER_PAGE, "10") or "10")
        search_str = request.session.get(SPN.SEARCH, None)


        request.session[SPN.CHANGES] = None

        group = None
        if group_id:
            group = Group.objects.get(id=group_id)

        groups = Group.objects.all()

        params = Parameter.objects.all().order_by("id") if group else Parameter.objects.none()

        try:
            paginatorr = Paginator(params, params_per_page)
            logger.info('Parameters page has been created.')
        except Exception as e:
                logger.error(f'Error generating parameters page! {e}')
    
        if page_n > paginatorr.num_pages:
            page_n = paginatorr.num_pages
            request.session[SPN.PAGE_N] = page_n

        context = {
            "page_obj": paginatorr.page(page_n),
            "groups": groups,
            "group": group,
            "params_per_page": str(params_per_page),
            "search_str": search_str,
        }

        return render(request, "permission_management/permissions.html", context)
