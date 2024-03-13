from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.http import HttpRequest

from .models import Parameter, File
from . import functions as fn
from .globals import SPN, RIPN, ROPN, FILTERS
from apps.request_interface import WrappedRequest
from apps.tasks.models import Dag, Task, DagRun, TaskInstance

import logging

logger = logging.getLogger(__name__)


class ConfigurationRequestHandler:

    status = 200
    response = {}

    def __init__(self, request: HttpRequest):
        self.w_request = WrappedRequest(request, RIPN.TYPE)


    def __handle_common(self):
        user_id = self.w_request.user_id

        filter_scope = int(self.w_request.get_sesh_par(SPN.SCOPE, "0") or "0")
        filter_status = self.w_request.get_sesh_par(SPN.STATUS)
        search_str = self.w_request.get_sesh_par(SPN.SEARCH)
        params_per_page = int(self.w_request.get_sesh_par(SPN.PER_PAGE, "10") or "10")
        page_n = int(self.w_request.get_sesh_par(SPN.PAGE_N, "1") or "1")
        changes = self.w_request.get_sesh_par(SPN.CHANGES)

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
            self.w_request.set_sesh_par(SPN.PAGE_N, page_n)

        par:Parameter
        for par in paginatorr.page(page_n).object_list:
            results.append(
                par.get_dict_with_all_relative_fields(
                    User.objects.get(id=user_id)
                )
            )
        self.response = {
            ROPN.LIST_EL: results,
            ROPN.NUM_PAGES: paginatorr.num_pages, 
            ROPN.PAGE_N: page_n, 
            ROPN.CHANGES: changes,
        }


    def handle_change(self):
        user_id = self.w_request.user_id

        status_dict = {}
        is_valid = False

        param_id = self.w_request.get_par(RIPN.PARAM_ID)
        param = Parameter.objects.get(id=param_id)

        if param.can_change(User.objects.get(id=user_id)):

            default_value = param.default_value
            old_value = param.value
            
            new_value = self.w_request.get_par(RIPN.VALUE, default_value)

            try:
                is_valid = fn.validate_parameter(
                    self.w_request.get_sesh_par(SPN.REPO_PATH),
                    param,
                    new_value
                )
                logger.info(
                    'Parameter is valid' if is_valid 
                    else 'The parameter is not valid'
                )
            except Exception as e:
                logger.error(f'Error during parameter validation! {e}')
            
            changes_dict:dict = self.w_request.get_or_create_sesh_par(SPN.CHANGES, {})
            filter_scope = self.w_request.get_sesh_par(SPN.SCOPE)
            filter_status = self.w_request.get_sesh_par(SPN.STATUS)

            if new_value == old_value:
                changes_dict.pop(param_id)
                logger.info(
                    f'''
                        The original value was returned, so the parameter 
                        id={param_id} was removed from the changelog.
                    '''
                )
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

            self.w_request.set_sesh_par(SPN.CHANGES, changes_dict)

            try:
                status_dict = fn.get_status_filter_items(
                    user_id=user_id, 
                    filter_scope=filter_scope, 
                    changes_dict=changes_dict
                )
                logger.info('Status filter updated.')
            except Exception as e:
                logger.error(f'Error while updating status filter! {e}')

            results = []
            paginatorr:Paginator = fn.get_paginator(user_id=user_id)
            page_n = int(self.w_request.get_sesh_par(SPN.PAGE_N, "1") or "1")

            if filter_status:
                
                try:
                    paginatorr = fn.get_paginator(    
                        filter_scope = filter_scope,
                        filter_status = filter_status, 
                        search_str = self.w_request.get_sesh_par(SPN.SEARCH, None),
                        params_per_page = self.w_request.get_sesh_par(SPN.PER_PAGE, "10") or "10", 
                        changes_dict = changes_dict,
                        user_id=user_id,
                    )
                    logger.info('Parameters page has been created.')
                except Exception as e:
                    logger.error(f'Error generating parameters page! {e}')
                    paginatorr = fn.get_paginator(user_id=user_id)
                

                if page_n > paginatorr.num_pages:
                    page_n = paginatorr.num_pages
                    self.w_request.set_sesh_par(SPN.PAGE_N, page_n)

                par: Parameter
                for par in paginatorr.page(page_n).object_list:
                    results.append(par.get_dict_with_all_relative_fields())

            self.response = {
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
            self.status = 422
            self.response = {
                ROPN.MSG: "Changes are not possible without appropriate permission"
            }


    def handle_save(self):
        user_id = self.w_request.user_id
        changes = self.w_request.get_sesh_par(SPN.CHANGES)
        change_manager = fn.ChangeManager(changes)
        
        msg = ""
        status_dict = {}

        if change_manager.is_good:
            logger.info('Saving allowed.')
            repo_path = self.w_request.get_sesh_par(SPN.REPO_PATH)
            commit_msg = self.w_request.get_par(RIPN.COMMIT_MSG)

            try:
                msg = fn.save_changes(repo_path, change_manager.get_dict(), commit_msg)
                logger.info('Changes saved.')
            except Exception as e:
                logger.error(f'Error while saving changes! {e}')
                msg = "Error while saving changes!"

            self.w_request.clear_sesh_par(SPN.CHANGES)
            
            try:
                status_dict = fn.get_status_filter_items(user_id=user_id)
                logger.info('Status filter updated.')
            except Exception as e:
                logger.error(f'Error while updating status filter! {e}')
        else:
            logger.warning('Saving prevented (no changes or some parameter is not valid).')
            filter_scope = self.w_request.get_sesh_par(SPN.SCOPE)
            msg = "Error: some of the parameters are not valid!"
            try:
                status_dict = fn.get_status_filter_items(
                    user_id=user_id, 
                    filter_scope=filter_scope, 
                    changes_dict=change_manager.get_dict()
                )
                logger.info('Status filter updated.')
            except Exception as e:
                logger.error(f'Error while updating status filter! {e}')
            self.status = 422
            
        self.response = {
            ROPN.STATUS_FILTER: status_dict,
            ROPN.MSG: msg,
        }

    
    def handle_sync_state(self):
        not_sync_cnt = File.objects.filter(is_sync=False).count()
        task_state_running = False
        if not_sync_cnt > 0:
            active_dag_id = self.w_request.get_sesh_par(SPN.ACTIVE_DAG_ID)
            if active_dag_id:
                task_state_running = active_dag_id is not None
            else:
                dags = Dag.objects.all()
                task_state_running = any([ dag.is_active() for dag in dags])
                
        self.response = {
            ROPN.SYNC_STATE: task_state_running,
            ROPN.NOT_SYNC_CNT: not_sync_cnt,
        }


    def handle_show_changes(self):
        changes = []
        if not self.w_request.get_sesh_par(SPN.CHANGES):
            logger.info('There are no changed parameters yet.')
            changes = "No changes"
            resp_type = "no_changes"
        else:
            resp_type = "ok"
            changes = self.w_request.get_sesh_par(SPN.CHANGES)
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
        
        self.response = {
            ROPN.CHANGES: changes,
            ROPN.TYPE: resp_type
        }

    
    def handle_show_filter(self):
        user_id = self.w_request.user_id

        filter_items = {}
        selected_item = None

        filter_scope = self.w_request.get_sesh_par(SPN.SCOPE)
        filter_status = self.w_request.get_sesh_par(SPN.STATUS)
        changes_dict = self.w_request.get_sesh_par(SPN.CHANGES)

        if not self.w_request.has_par(RIPN.FILTER_ID):
            logger.error('The filter type was not passed.')
            self.status = 422
            return
        
        filter_id = int(self.w_request.get_par(RIPN.FILTER_ID))
        match filter_id:
            case FILTERS.SCOPE:
                try:
                    filter_items = fn.get_scope_filter_items(
                        user_id=user_id, 
                        filter_status=filter_status, 
                        changes_dict=changes_dict
                    )
                    logger.info('Scope filter generated.')
                except Exception as e:
                    logger.error(f'Error while generating the scope filter! {e}')
                selected_item = filter_scope
            case FILTERS.STATUS:
                try:
                    filter_items = fn.get_status_filter_items(
                        user_id=user_id, 
                        filter_scope=filter_scope, 
                        changes_dict=changes_dict
                    )
                    logger.info('Status filter generated.')
                except Exception as e:
                    logger.error(f'Error while generating the status filter! {e}')
                selected_item = filter_status

        self.response = {
            ROPN.FILTER_ITEMS: filter_items,
            ROPN.SELECTED_ITEM: selected_item
        }


    def handle_set_filter(self):
        filter_ids = {
            1: SPN.SCOPE,
            2: SPN.STATUS
        }

        if not self.w_request.has_par(RIPN.FILTER_ID):
            logger.error('The filter id was not passed.')
            self.status = 422
            return
        
        filter_name = filter_ids[int(self.w_request.get_par(RIPN.FILTER_ID))]
        filter_value = self.w_request.get_par(RIPN.FILTER_VALUE)
        if filter_name and filter_value:
            self.w_request.set_sesh_par(filter_name, filter_value)
        logger.info(f'Filter "{filter_name}" set.')

        self.__handle_common()

    
    def handle_reset_filter(self):
        filter_ids = {
            1: SPN.SCOPE,
            2: SPN.STATUS
        }

        if not self.w_request.has_par(RIPN.FILTER_ID):
            logger.error('The filter id was not passed.')
            self.status = 422
            return

        filter_name = filter_ids[int(self.w_request.get_par(RIPN.FILTER_ID))]
        if filter_name:
            self.w_request.clear_sesh_par(filter_name)
        logger.info(f'Filter "{filter_name}" reset.')

        self.__handle_common()


    def handle_select_page(self):
        page_n = int(self.w_request.get_par(RIPN.PAGE_N, "1") or "1")
        self.w_request.set_sesh_par(SPN.PAGE_N, page_n)
        logger.info(f'Page {page_n} selected.')

        self.__handle_common()


    def handle_set_search(self):
        self.w_request.set_sesh_par(
            SPN.SEARCH, 
            self.w_request.get_par(RIPN.SEARCH)
        )
        logger.info('Search string set.')

        self.__handle_common()


    def handle_reset_search(self):
        self.w_request.clear_sesh_par(SPN.SEARCH)
        logger.info('Search string set.')

        self.__handle_common()


    def handle_set_per_page(self):
        self.w_request.set_sesh_par(
            SPN.PER_PAGE, 
            self.w_request.get_par(RIPN.PER_PAGE, "10")
        )
        logger.info('The number of parameters per page is set.')

        self.__handle_common()


    def handle_get(self):
        self.w_request.clear_sesh_par(SPN.CHANGES)
        
        filter_scope = int(self.w_request.get_sesh_par(SPN.SCOPE, "0") or "0")
        filter_status = self.w_request.get_sesh_par(SPN.STATUS)
        search_str = self.w_request.get_sesh_par(SPN.SEARCH)
        params_per_page = int(self.w_request.get_sesh_par(SPN.PER_PAGE, "10") or "10")
        page_n = int(self.w_request.get_sesh_par(SPN.PAGE_N, "1") or "1")

        user_id = self.w_request.user_id

        status_dict = fn.get_status_filter_items(
            user_id=user_id, 
            filter_scope=filter_scope
        )

        if (
            status_dict.get(filter_status) 
            and status_dict.get(filter_status).get("cnt") == 0
        ):
            filter_status = None
            self.w_request.clear_sesh_par(SPN.STATUS)

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
            page_n = paginatorr.num_pages
            self.w_request.set_sesh_par(SPN.PAGE_N, page_n)

        not_sync_cnt = File.objects.filter(is_sync=False).count()
        task_state_running = False
        if not_sync_cnt > 0:
            active_dag_id = self.w_request.get_sesh_par(SPN.ACTIVE_DAG_ID)
            if active_dag_id:
                task_state_running = active_dag_id is not None
            else:
                dags = Dag.objects.all()
                task_state_running = any([ dag.is_active() for dag in dags])

        self.response = {
            'page_obj': paginatorr.page(page_n),
            'params': paginatorr.page(page_n).object_list,
            'filter_scope': filter_scope,
            'filter_status': filter_status,
            'search_str': search_str,
            'params_per_page': str(params_per_page),
            'not_sync_cnt': not_sync_cnt,
            'task_state_running': task_state_running,
        }

    
    def handle_unknown_request_type(self):
        self.status = 422

