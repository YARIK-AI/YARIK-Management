from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpRequest

from apps.config_management.models import File
from .globals import SPN, RIPN, ROPN, RTYPE, DAG_NAMES, TASK_DICT, DAG_ID_FIRST, DAG_ID_SECOND, TASK_NAMES

from . import task_processing as tp

import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required(login_url=reverse_lazy("auth:login"))
def tasks(request: HttpRequest):

    # 
    active_dag_id = request.session.get(SPN.ACTIVE_DAG_ID, None)
    dag_run_id_dict = request.session.get(SPN.DAG_RUN_ID_DICT, {})
    dag_run_info_dict = request.session.get(SPN.DAG_RUN_INFO_DICT, {})
    if active_dag_id:
        state = tp.get_dag_run(
            active_dag_id, 
            dag_run_id_dict[active_dag_id],
        ).get("state", "")
        
        new_active_dag_id = active_dag_id

        if state not in ["queued", "running"]:
            dag_run_info_dict[active_dag_id] = tp.get_task_info(
                active_dag_id, 
                dag_run_id_dict[active_dag_id],
                ext_dag_ids=[active_dag_id,],
                ext_task_ids=TASK_DICT[active_dag_id]
            )
            request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
            
            new_active_dag_id = None
        
        if state == "success" and active_dag_id == DAG_ID_FIRST:
            dag_run_id = tp.exec_dag(DAG_ID_SECOND)
            logger.info("Second task triggered.")
            dag_run_id_dict[DAG_ID_SECOND] = dag_run_id
            new_active_dag_id = DAG_ID_SECOND
            request.session[SPN.DAG_RUN_ID_DICT] = dag_run_id_dict
        
        request.session[SPN.ACTIVE_DAG_ID] = new_active_dag_id
        active_dag_id = new_active_dag_id

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:

        status=200
        resp = {}
        if request.method == "POST":
            ajax_type = int(request.POST.get(RIPN.TYPE, None))

            match ajax_type:
                case RTYPE.ABORT: 
                    dag_id = request.POST.get(RIPN.TASK_ID, None)
                    aborting_status = tp.abort_dag_run(dag_id, request.session.get(SPN.DAG_RUN_ID_DICT, {}).get(dag_id, ""))
                    resp = {ROPN.STATUS: aborting_status}
                case RTYPE.RESTART: 
                    dag_id = request.POST.get(RIPN.TASK_ID, None)
                    restarting_status = tp.restart_dag_run(dag_id, request.session.get(SPN.DAG_RUN_ID_DICT, {}).get(dag_id, ""))
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
                        request.session.get(SPN.DAG_RUN_INFO_DICT, {}).get(dag_id, {}).get("subtasks", [])
                    ))[0]["logs"]

                    #logs = get_logs(dag_id, dag_run_id, task_id, 1, AUTH).split('\n')

                    resp = {
                        ROPN.LOGS: logs,
                    }
                    return JsonResponse(resp, status=status)

                case RTYPE.UPDATE_STATE:
                    expanded_dag_ids = request.GET.getlist(RIPN.DAG_IDS_EXPD, [])
                    expanded_task_ids = request.GET.getlist(RIPN.TASK_IDS_EXPD, [])

                    tasks = []
                    dag_run_id_dict:dict = request.session.get(SPN.DAG_RUN_ID_DICT, {})
                    dag_run_info_dict = request.session.get(SPN.DAG_RUN_INFO_DICT, {})

                    for dag_id in dag_run_id_dict.keys():
                        task = {}
                        if dag_id == active_dag_id:
                            task = tp.get_task_info(
                                dag_id, 
                                dag_run_id_dict[dag_id],
                                ext_dag_ids=expanded_dag_ids, 
                                ext_task_ids=expanded_task_ids
                            )
                            dag_run_info_dict[dag_id] = task
                            request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
                        else:
                            task = dag_run_info_dict[dag_id]
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
            dag_run_id_dict:dict = request.session.get(SPN.DAG_RUN_ID_DICT, {})
            dag_run_info_dict = request.session.get(SPN.DAG_RUN_INFO_DICT, {})

            for dag_id in dag_run_id_dict.keys():
                if dag_id == active_dag_id:
                    task = tp.get_task_info(dag_id, dag_run_id_dict[dag_id])
                    dag_run_info_dict[dag_id] = task
                    request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
                else:
                    task = dag_run_info_dict[dag_id]
                tasks.append(task)

            return render(request, "tasks/tasks.html", {ROPN.LIST_EL: tasks})


@login_required(login_url=reverse_lazy("auth:login"))
def sync(request: HttpRequest):

    if request.method == "POST":
        # run export task
        try:
            if File.objects.filter(is_sync=False).count() > 0:
                active_dag_id = DAG_ID_FIRST
                dag_run_info_dict = {}
                for dag_id in [DAG_ID_FIRST, DAG_ID_SECOND]:
                    dag_run_info_dict[dag_id] = {
                        "id": dag_id,
                        "name": DAG_NAMES[dag_id],
                        "state": "wait",
                        "total_steps": len(TASK_DICT[dag_id]),
                        "completed_steps": 0,
                        "subtasks": [{ "id": task_id, "name": TASK_NAMES[task_id] } for task_id in TASK_DICT[dag_id]]
                    }

                dag_run_id = tp.exec_dag(DAG_ID_FIRST)
                dag_run_id_dict = {
                    DAG_ID_FIRST: dag_run_id,
                    DAG_ID_SECOND: None
                }
            else:
                active_dag_id = None
                dag_run_id_dict = {
                    DAG_ID_FIRST: tp.get_last_dag_run(DAG_ID_FIRST),
                    DAG_ID_SECOND: tp.get_last_dag_run(DAG_ID_SECOND)
                }
                dag_run_info_dict = {}
                for dag_id in [DAG_ID_FIRST, DAG_ID_SECOND]:
                    dag_run_info_dict[dag_id] = tp.get_task_info(
                        dag_id,
                        dag_run_id_dict[dag_id],
                        ext_dag_ids=[dag_id,],
                        ext_task_ids=TASK_DICT[dag_id]
                    )
            request.session[SPN.ACTIVE_DAG_ID] = active_dag_id
            request.session[SPN.DAG_RUN_ID_DICT] = dag_run_id_dict
            request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
        except Exception as e:
            logger.error(e)

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
