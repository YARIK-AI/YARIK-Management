from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.db.models import F, Q, Count

from apps.config_management.models import Module,Component,Application,Instance,File,Parameter
from apps.tasks.models import Dag

from .task_manager import TaskManager
from .globals import ROPN, RTYPE, SPN, RIPN, QUEUE_ID
from apps.request_interface import BaseRequestHandler
from .models import Dag, Queue

from requests.exceptions import ConnectionError

import logging

logger = logging.getLogger(__name__)


class RequestHandler(BaseRequestHandler):

    task_manager:TaskManager = None

    def __init__(self, request: HttpRequest):
        super().__init__(request)

    def __reset_sync_state(self) -> None:
        self.w_request.set_sesh_par(SPN.ACTIVE_DAG_ID, None)
        self.w_request.set_sesh_par(SPN.SYNC_IN_PROGRESS, False)
        self.w_request.set_sesh_par(SPN.SYNC_SUCCESS, False)
        self.w_request.set_sesh_par(SPN.ALLOW_VIEW_TASKS, False)

    def _render_503(self) -> HttpResponse:
        self.__reset_sync_state()
        # The response code is not set because it does not allow saving session parameters
        return redirect(reverse_lazy("tasks:tasks-503"))

    def _render_404(self) -> HttpResponse:
        self.__reset_sync_state()
        return redirect(reverse_lazy("tasks:tasks-404"))


class TasksRequestHandler(RequestHandler):

    def __init__(self, request: HttpRequest):
        super().__init__(request)
        
    
    def _handle_common_before(self) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect | None):
        """
        General actions when processing requests.
        The following is done here:
        1. Checking for connection, presence of Dags and permission to view tasks
        2. Managing the task queue
        3. Saving task states in session parameters
        """
        is_conn_good = TaskManager.is_conn_good()
        has_dags = TaskManager.has_dags_from_queue(QUEUE_ID)

        if not is_conn_good: # Lost connection with airflow
            return self._render_503()
        
        if not has_dags: # Lost one of sync dag
            logger.error("Synchronization dags not found.")
            return self._render_404()

        allow_view_tasks = bool(self.w_request.get_sesh_par(SPN.ALLOW_VIEW_TASKS, False))
        # If synchronization has already completed, there is nothing to do here
        logger.info(f"Common view call: value is {allow_view_tasks}")
        if not allow_view_tasks: # Cannot view tasks
            return redirect(reverse_lazy("cfg:configuration"))
        
        active_dag_id: str|None = self.w_request.get_sesh_par(SPN.ACTIVE_DAG_ID)
        dag_run_id_dict: dict = self.w_request.get_sesh_par(SPN.DAG_RUN_ID_DICT, {})
        dag_run_info_dict: dict = self.w_request.get_sesh_par(SPN.DAG_RUN_INFO_DICT, {})


        task_manager = TaskManager(active_dag_id, dag_run_id_dict, dag_run_info_dict)
        sync_success = False
        try:
            if active_dag_id: # if active dag id in sesh params, then manage
                sync_success = task_manager.manage_dags()
                active_dag_id = task_manager.current_dag_id
                dag_run_id_dict = task_manager.dag_run_ids
                dag_run_info_dict = task_manager.dag_run_info_dict
            else: # if active dag id not in sesh params, then request latest state
                sync_success = task_manager.request_latest_state(QUEUE_ID)
                active_dag_id = task_manager.current_dag_id
                dag_run_id_dict = task_manager.dag_run_ids
                dag_run_info_dict = task_manager.dag_run_info_dict
        except ConnectionError as e:
            logger.error("Error during task management. Error connecting to Airflow.")
            return self._render_503() # Lost connection with airflow
        except Exception as e:
            logger.error(f"Unknown error:  {e}")
            self.status = 500
            return HttpResponse("Unknown server error", status=self.status)

        self.w_request.set_sesh_par(SPN.ACTIVE_DAG_ID, active_dag_id)
        self.w_request.set_sesh_par(SPN.DAG_RUN_ID_DICT, dag_run_id_dict)
        self.w_request.set_sesh_par(SPN.DAG_RUN_INFO_DICT, dag_run_info_dict)

            # Sync in progress
        if active_dag_id:
            self.w_request.set_sesh_par(SPN.SYNC_IN_PROGRESS, True)
        else:
            self.w_request.set_sesh_par(SPN.SYNC_IN_PROGRESS, False)

        self.w_request.set_sesh_par(SPN.SYNC_SUCCESS, sync_success)

        self.task_manager = task_manager

        return None

    def handle_task_action(self, action) -> None:
        """
        Handler for requests to stop and restart tasks. 
        If the response is generated, it returns true, otherwise false.
        """

        if action not in [RTYPE.ABORT, RTYPE.RESTART]:
            self.handle_unknown_request_type()
            return 

        resp = self._handle_common_before()
        if resp:
            self.response = resp
            return

        dag_id = self.w_request.get_par(RIPN.TASK_ID)
        dag = Dag.objects.get(dag_id=dag_id)
        dag_run_id = self.w_request.get_sesh_par(SPN.DAG_RUN_ID_DICT, {}).get(dag_id)

        action_status:str
        active_dag_id = dag_id
        if action == RTYPE.ABORT:
            action_status = dag.abort(dag_run_id)
            active_dag_id = None
        elif action == RTYPE.RESTART:
            action_status = dag.restart(dag_run_id)

        if action_status:
            self.w_request.set_sesh_par(SPN.ACTIVE_DAG_ID, active_dag_id)

        resp = {ROPN.STATUS: action_status}

        self.response = JsonResponse(resp, status=self.status)

        return

    def handle_show_logs(self) -> None:
        """
        
        If the response is generated, it returns true, otherwise false.
        """
        resp = self._handle_common_before()
        if resp:
            self.response = resp
            return

        dag_id = self.w_request.get_par(RIPN.TASK_ID)
        task_id = self.w_request.get_par(RIPN.SUBTASK_ID)

        dag_run_info_dict:dict = self.w_request.get_sesh_par(SPN.DAG_RUN_INFO_DICT, {})

        logs = list(filter(
            lambda t: t["id"] == task_id,
            dag_run_info_dict.get(dag_id, {}).get("subtasks", [])
        ))[0].get("logs")

        resp = {ROPN.LOGS: logs}

        self.response = JsonResponse(resp, status=self.status)

        return

    def handle_update_state(self) -> None:
        """
        
        If the response is generated, it returns true, otherwise false.
        """
        resp = self._handle_common_before()
        if resp:
            self.response = resp
            return
        
        
        expanded_dag_ids = self.w_request.get_list(RIPN.DAG_IDS_EXPD)
        expanded_task_ids = self.w_request.get_list(RIPN.TASK_IDS_EXPD)

        tasks = []
        task_manager = self.task_manager
        try:
            tasks = task_manager.get_info(expanded_dag_ids, expanded_task_ids)
        except ConnectionError as e:
            logger.error("Error while requesting task information. Error connecting to Airflow.")
            resp = self._render_503()
            return
        except Exception as e:
            logger.error(f"Unknown error:  {e}")
            self.status = 500
            self.response = HttpResponse("Unknown server error", status=self.status)
            return

        self.w_request.set_sesh_par(SPN.DAG_RUN_INFO_DICT, task_manager.dag_run_info_dict)
        is_survey_required = self.w_request.get_sesh_par(SPN.SYNC_IN_PROGRESS, False)
        is_finish = not self.w_request.get_sesh_par(SPN.SYNC_IN_PROGRESS, False) \
            and self.w_request.get_sesh_par(SPN.SYNC_SUCCESS, False)
        is_terminated = not self.w_request.get_sesh_par(SPN.SYNC_IN_PROGRESS, False) \
            and not self.w_request.get_sesh_par(SPN.SYNC_SUCCESS, False)

        resp = {
            ROPN.LIST_EL: tasks,
            ROPN.SURVEY_REQUIRED: is_survey_required,
            ROPN.IS_FINISH: is_finish,
            ROPN.IS_TERMINATED: is_terminated,
        }

        self.response = JsonResponse(resp, status=self.status)

        return
    
    def handle_post(self) -> None:
        """
        
        If the response is generated, it returns true, otherwise false.
        """
        resp = self._handle_common_before()
        if resp:
            self.response = resp
            return


        request_type = self.w_request.get_par("type", "")
        sync_in_progress = self.w_request.get_sesh_par(SPN.SYNC_IN_PROGRESS, False) 
        sync_success = self.w_request.get_sesh_par(SPN.SYNC_SUCCESS, False)

        if request_type == "finish":

            # If synchronization is in progress or not successful, then stay here
            if sync_in_progress or not sync_success:
                self.response = redirect(reverse_lazy("tasks:tasks"))
                return
            
            self.w_request.set_sesh_par(SPN.ACTIVE_DAG_ID, None)
            self.w_request.set_sesh_par(SPN.DAG_RUN_ID_DICT, {})
            self.w_request.set_sesh_par(SPN.DAG_RUN_INFO_DICT, {})
            self.w_request.set_sesh_par(SPN.ALLOW_VIEW_TASKS, False)

            self.response = redirect(reverse_lazy("cfg:configuration"))
            return
        elif request_type == "back":

            if sync_in_progress:
                self.response = redirect(reverse_lazy("tasks:tasks"))
                return
            
            self.w_request.set_sesh_par(SPN.ACTIVE_DAG_ID, None)
            self.w_request.set_sesh_par(SPN.DAG_RUN_ID_DICT, {})
            self.w_request.set_sesh_par(SPN.DAG_RUN_INFO_DICT, {})
            self.w_request.set_sesh_par(SPN.ALLOW_VIEW_TASKS, False)

            if sync_success:
                self.response = redirect(reverse_lazy("cfg:configuration"))
            else:
                self.response = redirect(reverse_lazy("tasks:sync"))
                
            return       
        else:
            self.handle_unknown_request_type()
            return
        
    def handle_get(self) -> None:

        resp = self._handle_common_before()
        if resp:
            self.response = resp
            return

        tasks = []
        task_manager = self.task_manager
        try:
            tasks = task_manager.get_info()
            self.w_request.set_sesh_par(SPN.DAG_RUN_INFO_DICT, task_manager.dag_run_info_dict)
        except ConnectionError as e:
            logger.error("Error while requesting task information. Error connecting to Airflow.")
            self.response = self._render_503()
            return
        except Exception as e:
            tasks = None
            logger.error(f"Unknown error:  {e}")
            self.status = 500
            self.response = HttpResponse("Unknown server error", status=self.status)
            return 

        context =  {ROPN.LIST_EL: tasks,}

        self.response = render(self.w_request.request, "tasks/tasks.html", context)
        return
    

class SyncRequestHandler(RequestHandler):

    def __init__(self, request: HttpRequest):
        super().__init__(request)

    def __handle_common(self) -> (HttpResponseRedirect | HttpResponsePermanentRedirect | None):
        # Checking: are there resources to synchronize?
        if File.objects.filter(is_sync=False).count() == 0:
            return redirect(reverse_lazy("cfg:configuration"))
        else:
            return None
        
    def handle_post(self):
        """
        
        If the response is generated, it returns true, otherwise false.
        """

        resp = self.__handle_common()
        if resp:
            self.response = resp
            return

        active_dag_id = self.w_request.get_sesh_par(SPN.ACTIVE_DAG_ID)
        dag_run_id_dict = {}
        dag_run_info_dict= {}


        # Search for active dag if not stored in memory
        try:
            if not active_dag_id: 
                for dag in Dag.objects.all():
                    if dag.is_active():
                        active_dag_id = dag.dag_id
        except ConnectionError as e:
            logger.error("Error while requesting active task. Error connecting to Airflow")
            self.response = self._render_503()
            return
        except Exception as e:
            logger.error(f"Unknown error:  {e}")
            self.status = 500
            self.response = HttpResponse("Unknown server error", status=self.status)
            return

        if not active_dag_id: # If there is no running dag (launch)

            # Selecting the first dag in the queue as active
            active_dag_id = Queue.objects.get(queue_id=QUEUE_ID).dag_id_begin.dag_id

            # Initializing dictionaries with information about dag runs
            for dag in Dag.objects.all():
                dag_run_info_dict[dag.dag_id] = {
                    "id": dag.dag_id,
                    "name": dag.name,
                    "state": "state_request",
                    "total_steps": dag.tasks.count(),
                    "completed_steps": 0,
                    "subtasks": [
                        { 
                            "id": task.task_id, 
                            "name": task.name,
                        } for task in dag.tasks
                    ]
                }
                dag_run_id_dict[dag.dag_id] = None

            try:
                dag = Dag.objects.get(dag_id=active_dag_id)
                dag_run_id = dag.trigger() # launch dag
                dag_run_id_dict[dag.dag_id] = dag_run_id # save dag run id
            except ConnectionError as e:
                logger.error("Error during task trigger. Error connecting to Airflow")
                self.response = self._render_503()
                return
            except NameError as e:
                logger.error("Synchronization dags not found")
                self.response = self._render_404()
                return
            except Exception as e:
                active_dag_id = None
                logger.error(f"Unknown error:  {e}")
                self.status = 500
                self.response = HttpResponse("Unknown server error", status=self.status)
                return

        else: # If there is a running dag (get state)
            task_manager = TaskManager(active_dag_id, {}, {})
            try:
                # Get the last state of the running dag
                task_manager.request_latest_state(1)
                # Save info
                active_dag_id = task_manager.current_dag_id
                dag_run_id_dict = task_manager.dag_run_ids
                dag_run_info_dict = task_manager.dag_run_info_dict
            except ConnectionError as e:
                logger.error("Error while requesting task information. Error connecting to Airflow")
                self.response = self._render_503()
                return
            except Exception as e:
                logger.error(f"Unknown error:  {e}")
                self.status = 500
                self.response = HttpResponse("Unknown server error", status=self.status)
                return

        # Saving information about running dags in session parameters
        self.w_request.set_sesh_par(SPN.ACTIVE_DAG_ID, active_dag_id)
        self.w_request.set_sesh_par(SPN.DAG_RUN_ID_DICT, dag_run_id_dict)
        self.w_request.set_sesh_par(SPN.DAG_RUN_INFO_DICT, dag_run_info_dict)

        # Setting a flag in the session parameter: is sync in progress?
        if active_dag_id:
            self.w_request.set_sesh_par(SPN.SYNC_IN_PROGRESS, True)
            self.w_request.set_sesh_par(SPN.ALLOW_VIEW_TASKS, True)
        else:
            self.w_request.set_sesh_par(SPN.SYNC_IN_PROGRESS, False)
            self.w_request.set_sesh_par(SPN.ALLOW_VIEW_TASKS, False)

        self.w_request.set_sesh_par(SPN.SYNC_SUCCESS, False)

        self.response = redirect(reverse_lazy("tasks:tasks"))
        return
        
    def handle_get(self):

        resources = Parameter.objects.filter(~Q(value=F("prev_value"))).filter(file__is_sync=False) \
        .select_related("file", "instance", "app", "component", "module") \
        .annotate(
            module_name=F('file__instance__app__component__module__name'),
            component_name=F('file__instance__app__component__name'),
            app_name=F('file__instance__app__name'),
            instance_name=F('file__instance__name'),
            fileid=F('file__id'),
            filename=F('file__filename'),
            desc=F('file__description')
        ) \
        .values("module_name", "component_name", "app_name", "instance_name", "fileid", "filename", "desc") \
        .annotate(cnt=Count("*")) \
        .filter(file__instance__app__component__module__id__isnull=False)

        configs = {}


        for res in resources:
            module_name = res["module_name"]
            component_name = res["component_name"]
            app_name = res["app_name"]
            instance_name = res["instance_name"]
            file_id=res["fileid"]
            filename = res["filename"]
            desc=res["desc"]
            cnt = res["cnt"]

            if not ((module_name,component_name) in configs):
                configs[(module_name,component_name)] = []

            r = {
                "app_name": app_name,
                "instance_name": instance_name,
                "file_id": file_id,
                "filename": filename, 
                "desc": desc,
                "cnt": cnt,
                "params": Parameter.objects.filter(Q(file__id=file_id)&~Q(prev_value=F("value"))).values("name", "description", "prev_value", "value"),
            }
            configs[(module_name,component_name)].append(r)

            

        logger.info(configs)

        is_conn_good = TaskManager.is_conn_good()
        has_dags = False
        if is_conn_good:
            has_dags = TaskManager.has_dags_from_queue(QUEUE_ID)

        '''
        files = File.objects.filter(is_sync=False).order_by("name")

            
        configs = []



        

        for f in files:
            configs.append(
                {
                    "id": f.id,
                    "module": f.instance.app.component.module.name,
                    "component": f.instance.app.component.name,
                    "app": f.instance.app.name,
                    "file": f.filename,
                    "description": f.description,
                    "total": f.parameters.filter(~Q(value=F("prev_value"))).count(),
                }
            )
        '''

        context = {
            "configs": configs, 
            "is_conn_good": is_conn_good,
            "has_dags": has_dags,
        }

        self.response = render(self.w_request.request, "tasks/sync.html", context)
        return

