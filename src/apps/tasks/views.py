from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpRequest, HttpResponse

from requests.exceptions import ConnectionError

from apps.config_management.models import File
from .globals import SPN, RIPN, ROPN, RTYPE
from .task_manager import TaskManager
from .models import Dag, Queue

from datetime import datetime as dttm

import logging

logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url=reverse_lazy("auth:login"))
def tasks(request: HttpRequest):

    can_manage = TaskManager.can_manage()

    if not can_manage:
        request.session[SPN.ACTIVE_DAG_ID] = None
        request.session[SPN.AIRFLOW_CONN_GOOD] = False
        return render(request, "tasks/page-503.html", status=503)
    elif not request.session.get(SPN.AIRFLOW_CONN_GOOD, False):
        request.session[SPN.AIRFLOW_CONN_GOOD] = True

    status=200
    # 
    active_dag_id: str|None = request.session.get(SPN.ACTIVE_DAG_ID, None)
    dag_run_id_dict: dict = request.session.get(SPN.DAG_RUN_ID_DICT, {})
    dag_run_info_dict: dict = request.session.get(SPN.DAG_RUN_INFO_DICT, {})


    task_manager = TaskManager(active_dag_id, dag_run_id_dict, dag_run_info_dict)
    logger.info(active_dag_id)
    try:
        if active_dag_id:
            active_dag_id = task_manager.manage_dags()
            dag_run_id_dict = task_manager.dag_run_ids
            dag_run_info_dict = task_manager.dag_run_info_dict
        else:
            task_manager.request_latest_state(1)
            active_dag_id = task_manager.current_dag_id
            dag_run_id_dict = task_manager.dag_run_ids
            dag_run_info_dict = task_manager.dag_run_info_dict
    except ConnectionError as e:
        logger.error("Error during task management. Error connecting to Airflow.")
        request.session[SPN.ACTIVE_DAG_ID] = None
        request.session[SPN.AIRFLOW_CONN_GOOD] = False
        return render(request, "tasks/page-503.html", status=503)
    except Exception as e:
        logger.error(e)

    request.session[SPN.ACTIVE_DAG_ID] = active_dag_id
    request.session[SPN.DAG_RUN_ID_DICT] = dag_run_id_dict
    request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:

        
        resp = {}
        if request.method == "POST":
            ajax_type = int(request.POST.get(RIPN.TYPE, None))

            match ajax_type:

                case RTYPE.ABORT: 
                    dag_id = request.POST.get(RIPN.TASK_ID, None)
                    dag = Dag.objects.get(dag_id=dag_id)
                    dag_run_id = request.session.get(SPN.DAG_RUN_ID_DICT, {}).get(dag_id)
                    aborting_status = dag.abort(dag_run_id)
                    request.session[SPN.ACTIVE_DAG_ID] = None
                    resp = {ROPN.STATUS: aborting_status}

                case RTYPE.RESTART: 
                    dag_id = request.POST.get(RIPN.TASK_ID, None)
                    dag = Dag.objects.get(dag_id=dag_id)
                    dag_run_id = request.session.get(SPN.DAG_RUN_ID_DICT, {}).get(dag_id)
                    restarting_status = dag.restart(dag_run_id)
                    logger.info(f"Restart {dag_id} {restarting_status}")
                    if restarting_status:
                        request.session[SPN.ACTIVE_DAG_ID] = dag_id

                    logger.info(f"ACTIVE DAG ID {request.session[SPN.ACTIVE_DAG_ID]}")
                    resp = {ROPN.STATUS: restarting_status}

            return JsonResponse(resp, status=status)
        
        elif request.method == "GET":
            ajax_type = int(request.GET.get(RIPN.TYPE, None))

            match ajax_type:

                case RTYPE.SHOW_LOGS:
                    dag_id = request.GET.get(RIPN.TASK_ID, None)
                    task_id = request.GET.get(RIPN.SUBTASK_ID, None)

                    logs = list(filter(
                        lambda t: t["id"] == task_id,
                        dag_run_info_dict.get(dag_id, {}).get("subtasks", [])
                    ))[0].get("logs")

                    #logs = get_logs(dag_id, dag_run_id, task_id, 1, AUTH).split('\n')

                    resp = {
                        ROPN.LOGS: logs,
                    }
                    return JsonResponse(resp, status=status)

                case RTYPE.UPDATE_STATE:
                    expanded_dag_ids = request.GET.getlist(RIPN.DAG_IDS_EXPD, [])
                    expanded_task_ids = request.GET.getlist(RIPN.TASK_IDS_EXPD, [])

                    if not task_manager.can_manage():
                        status=503

                    tasks = []
                    try:
                        tasks = task_manager.get_info(expanded_dag_ids, expanded_task_ids)
                    except ConnectionError as e:
                        logger.error("Error while requesting task information. Error connecting to Airflow.")
                        request.session[SPN.ACTIVE_DAG_ID] = None
                        request.session[SPN.AIRFLOW_CONN_GOOD] = False
                        return render(request, "tasks/page-503.html", status=503)
                        '''
                        status=503
                        active_dag_id = None
                        request.session[SPN.ACTIVE_DAG_ID] = None
                        resp = {
                            ROPN.LIST_EL: [],
                            ROPN.SURVEY_REQUIRED: False
                        }
                        return JsonResponse(resp, status=status)
                        '''
                    except Exception as e:
                        logger.error(e)

                    request.session[SPN.DAG_RUN_INFO_DICT] = task_manager.dag_run_info_dict

                    active_tasks = list(
                        filter(
                            lambda t: t.get("state") in ["running", "queued", "state_request"],
                            tasks
                        )
                    )
                    is_survey_required = len(active_tasks) > 0
                    #is_survey_required = True

                    resp = {
                        ROPN.LIST_EL: tasks,
                        ROPN.SURVEY_REQUIRED: is_survey_required
                    }

                    return JsonResponse(resp, status=status)
    else:
        if request.method == "GET":
            
            tasks = []
            try:
                tasks = task_manager.get_info()
                request.session[SPN.DAG_RUN_INFO_DICT] = task_manager.dag_run_info_dict
            except ConnectionError as e:
                logger.error("Error while requesting task information. Error connecting to Airflow.")
                request.session[SPN.ACTIVE_DAG_ID] = None
                request.session[SPN.AIRFLOW_CONN_GOOD] = False
                return render(request, "tasks/page-503.html", status=503)
            except Exception as e:
                logger.error(e)
                tasks = None

            return render(request, "tasks/tasks.html", {ROPN.LIST_EL: tasks})


@login_required(login_url=reverse_lazy("auth:login"))
def sync(request: HttpRequest):

    if request.method == "POST":
        active_dag_id = request.session.get(SPN.ACTIVE_DAG_ID, None)
        dag_run_id_dict = {}
        dag_run_info_dict= {}


        # if not active dag id in memory then search for it via API
        try:
            if not active_dag_id: 
                for dag in Dag.objects.all():
                    if dag.is_active():
                        active_dag_id = dag.dag_id
        except ConnectionError as e:
            logger.error("Error while requesting active task. Error connecting to Airflow")
            request.session[SPN.ACTIVE_DAG_ID] = None
            request.session[SPN.AIRFLOW_CONN_GOOD] = False
            return render(request, "tasks/page-503.html", status=503)
        except Exception as e:
            logger.error(e)
        if File.objects.filter(is_sync=False).count() > 0:
            if not active_dag_id:
                # dag launch case
                active_dag_id = Queue.objects.get(queue_id=1).dag_id_begin.dag_id
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
                    dag_run_id = dag.trigger()
                    dag_run_id_dict[dag.dag_id] = dag_run_id
                    if not request.session.get(SPN.AIRFLOW_CONN_GOOD, False):
                        request.session[SPN.AIRFLOW_CONN_GOOD] = True
                except ConnectionError as e:
                    logger.error("Error during task trigger. Error connecting to Airflow")
                    request.session[SPN.ACTIVE_DAG_ID] = None
                    request.session[SPN.AIRFLOW_CONN_GOOD] = False
                    return render(request, "tasks/page-503.html", status=503)
                except NameError as e:
                    logger.error(e)
                    request.session[SPN.ACTIVE_DAG_ID] = None
                    return render(request, "tasks/page-404.html", status=404)
                except Exception as e:
                    logger.error(e.args)
                    active_dag_id = None

            else: # case of a working dag
                task_manager = TaskManager(active_dag_id, {}, {})
                try:
                    task_manager.request_latest_state(1)
                    dag_run_id_dict = task_manager.dag_run_ids
                    dag_run_info_dict = task_manager.dag_run_info_dict
                except ConnectionError as e:
                    logger.error("Error while requesting task information. Error connecting to Airflow")
                    request.session[SPN.ACTIVE_DAG_ID] = None
                    request.session[SPN.AIRFLOW_CONN_GOOD] = False
                    return render(request, "tasks/page-503.html", status=503)
                except Exception as e:
                    logger.error(e)

        request.session[SPN.ACTIVE_DAG_ID] = active_dag_id
        request.session[SPN.DAG_RUN_ID_DICT] = dag_run_id_dict
        request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict

        # redirect
        return redirect(reverse_lazy("tasks:tasks"))
    elif request.method == "GET":
        files = File.objects.filter(is_sync=False).order_by("name")
        configs = []

        for f in files:
            configs.append(
                {
                    "module": f.instance.app.component.module.name,
                    "component": f.instance.app.component.name,
                    "app": f.instance.app.name,
                    "file": f.filename,
                    "description": f.description,
                }
            )

        return render(request, "tasks/sync.html", {"configs": configs})
