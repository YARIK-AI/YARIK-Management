from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpRequest

from apps.config_management.models import File
from .globals import SPN, RIPN, ROPN, RTYPE, DAG_NAMES, TASK_DICT, DAG_ID_FIRST, DAG_ID_SECOND, TASK_NAMES
from .task_manager import TaskManager
from .models import Dag, DagsQueue

from datetime import datetime as dttm

import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required(login_url=reverse_lazy("auth:login"))
def tasks(request: HttpRequest):

    # 
    active_dag_id: str|None = request.session.get(SPN.ACTIVE_DAG_ID, None)
    dag_run_id_dict: dict = request.session.get(SPN.DAG_RUN_ID_DICT, {})
    dag_run_info_dict: dict = request.session.get(SPN.DAG_RUN_INFO_DICT, {})


    if active_dag_id:
        task_manager = TaskManager(active_dag_id, dag_run_id_dict, dag_run_info_dict)

        active_dag_id = task_manager.manage_dags()
        dag_run_id_dict = task_manager.dag_run_ids
        dag_run_info_dict = task_manager.dag_run_info_dict

        request.session[SPN.ACTIVE_DAG_ID] = active_dag_id
        request.session[SPN.DAG_RUN_ID_DICT] = dag_run_id_dict    
        request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
    


    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:

        status=200
        resp = {}
        if request.method == "POST":
            ajax_type = int(request.POST.get(RIPN.TYPE, None))

            match ajax_type:
                case RTYPE.ABORT: 
                    dag_id = request.POST.get(RIPN.TASK_ID, None)
                    dag = Dag.objects.get(dag_id=dag_id)
                    dag_run_id = request.session.get(SPN.DAG_RUN_ID_DICT, {}).get(dag_id)
                    aborting_status = dag.abort(dag_run_id)
                    resp = {ROPN.STATUS: aborting_status}
                case RTYPE.RESTART: 
                    dag_id = request.POST.get(RIPN.TASK_ID, None)
                    dag = Dag.objects.get(dag_id=dag_id)
                    dag_run_id = request.session.get(SPN.DAG_RUN_ID_DICT, {}).get(dag_id)
                    restarting_status = dag.restart(dag_run_id)
                    if restarting_status:
                        request.session[SPN.ACTIVE_DAG_ID] = dag_id
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

                    tasks = []

                    for dag in Dag.objects.all():
                        task = {}
                        if dag.dag_id == active_dag_id:
                            task = dag.get_target_info(
                                dag_run_id_dict[dag.dag_id],
                                ext_dag_ids=expanded_dag_ids, 
                                ext_task_ids=expanded_task_ids
                            )
                            dag_run_info_dict[dag.dag_id] = task
                            request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
                        else:
                            task = dag_run_info_dict[dag.dag_id]
                        tasks.append(task)

                    active_tasks = list(
                        filter(
                            lambda t: t["state"] in ["running", "queued", "wait"],
                            tasks
                        )
                    )
                    is_survey_required = len(active_tasks) > 0

                    resp = {
                        ROPN.LIST_EL: tasks,
                        ROPN.SURVEY_REQUIRED: is_survey_required
                    }

                    return JsonResponse(resp, status=status)
    else:
        if request.method == "GET":

            tasks = []

            for dag in Dag.objects.all():
                if dag.dag_id == active_dag_id:
                    task = dag.get_target_info(dag_run_id_dict[dag.dag_id])
                    dag_run_info_dict[dag.dag_id] = task
                    request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
                else:
                    task = dag_run_info_dict[dag.dag_id]
                tasks.append(task)

            return render(request, "tasks/tasks.html", {ROPN.LIST_EL: tasks})


@login_required(login_url=reverse_lazy("auth:login"))
def sync(request: HttpRequest):

    if request.method == "POST":
        # run export task
        active_dag_id = request.session.get(SPN.ACTIVE_DAG_ID, None)

        # if not active dag id in memory then search for it via API
        if not active_dag_id: 
            for dag in Dag.objects.all():
                if dag.is_active():
                    active_dag_id = dag.dag_id

        if File.objects.filter(is_sync=False).count() > 0 and not active_dag_id:
            # dag launch case
            active_dag_id = DagsQueue.objects.filter(dag_id_previous=None).first().dag_id_next.dag_id
            logger.info(active_dag_id)
            dag_run_info_dict = {}
            for dag in Dag.objects.all():
                dag_run_info_dict[dag.dag_id] = {
                    "id": dag.dag_id,
                    "name": dag.name,
                    "state": "wait",
                    "total_steps": dag.tasks.count(),
                    "completed_steps": 0,
                    "subtasks": [
                        { 
                            "id": task.task_id, 
                            "name": task.name,
                        } for task in dag.tasks
                    ]
                }
            try:
                dag = Dag.objects.get(dag_id=active_dag_id)
                dag_run_id = dag.trigger()
            except Exception as e:
                logger.error(e)
                dag_run_id = None
            finally:
                dag_run_id_dict = {
                    DAG_ID_FIRST: dag_run_id,
                    DAG_ID_SECOND: None
                }
        else: # case of a working dag
            dag_run_id_dict = {}
            after_date = dttm.fromisoformat("2023-01-01T00:00:00Z")
            for dag in Dag.objects.all():
                try:
                    last_dag_run = dag.get_last_dag_run(after_date)
                    after_date = dttm.fromisoformat(last_dag_run.logical_date)
                    last_dag_run_id = last_dag_run.dag_run_id
                except Exception as e:
                    logger.error(e)
                    last_dag_run_id = None
                finally:
                    dag_run_id_dict[dag.dag_id] = last_dag_run_id

            dag_run_info_dict = {}
            for dag in Dag.objects.all():
                try:
                    dag_info = dag.get_target_info(
                        dag_run_id_dict.get(dag.dag_id, None),
                        ext_dag_ids=[dag.dag_id,],
                        ext_task_ids=[task.task_id for task in dag.tasks]
                    )
                except Exception as e:
                    logger.error(e)
                    dag_info = {
                        "id": dag.dag_id,
                        "name": dag.name,
                        "state": "wait",
                        "total_steps": dag.tasks.count(),
                        "completed_steps": 0,
                        "subtasks": [
                            { 
                                "id": task.task_id, 
                                "name": task.name,
                            } for task in dag.tasks
                        ]
                    }
                finally:
                    dag_run_info_dict[dag.dag_id] = dag_info
            
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
                    "total": 0,
                }
            )

        return render(request, "tasks/sync.html", {"configs": configs})
