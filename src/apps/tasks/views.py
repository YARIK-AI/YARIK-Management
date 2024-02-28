from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpRequest

from apps.config_management.models import File
from .globals import SPN, RIPN, ROPN, RTYPE

import json
import requests
import datetime

import logging

logger = logging.getLogger(__name__)

AIRFLOW_URL = "http://airflow-web.default.svc.cluster.local:3132"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

DAG_ID = "export_xml"
TASK_ID = "export_xml_task"
AUTH = ('admin', 'admin')

def exec_dag(dag_id, conf={}, auth=None):
    payload = {
        "conf": conf,
    }

    # run dag
    dag_run_url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    dag_run_resp = requests.post(dag_run_url, headers=headers, auth=auth, json=payload)
    
    if dag_run_resp.status_code != 200:
        raise Exception(json.loads(dag_run_resp.text)["detail"])

    dag_run_id = json.loads(dag_run_resp.text)["dag_run_id"]
    
    return dag_run_id


def get_state(dag_id, dag_run_id, conf={}, auth=None, name=None):
    if not name:
        name = dag_id

    payload = {
        "conf": conf,
    }
    get_dag_run_url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"

    dag_run_info_resp = requests.get(get_dag_run_url, headers=headers, auth=auth)

    if dag_run_info_resp.status_code != 200:
        raise Exception(json.loads(dag_run_info_resp.text)["detail"])

    dag_run_info = json.loads(dag_run_info_resp.text)
    logger.info(dag_run_info)

    start_time = datetime.datetime.fromisoformat(dag_run_info["logical_date"])

    return {"name": name, "state": dag_run_info["state"], "time": start_time.strftime("%b %d, %Y, %I:%M:%S %p")}



# Create your views here.
@login_required(login_url=reverse_lazy("auth:login"))
def tasks(request: HttpRequest):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:

        status=200
        resp = {}
        if request.method == "POST":
            ajax_type = int(request.POST.get(RIPN.TYPE, None))

            match ajax_type:
                case RTYPE.ABORT: 
                    pass
        elif request.method == "GET":
            ajax_type = int(request.GET.get(RIPN.TYPE, None))

            match ajax_type:

                case RTYPE.UPDATE_STATE:
                    dag_run_id_export = request.session.get(SPN.DAG_RUN_ID_EXPORT)

                    tasks = []

                    tasks.append(get_state(DAG_ID, dag_run_id_export, {}, AUTH, "Export"))

                    return JsonResponse({"tasks": tasks})
    else:
        if request.method == "GET":
            dag_run_id_export = request.session.get(SPN.DAG_RUN_ID_EXPORT)

            tasks = []

            if dag_run_id_export:
                tasks.append(get_state(DAG_ID, dag_run_id_export, {}, AUTH, "Export"))

            return render(request, "tasks/tasks.html", {"tasks": tasks})


@login_required(login_url=reverse_lazy("auth:login"))
def sync(request: HttpRequest):

    if request.method == "POST":
        # run task
        conf = {}

        try:
            dag_run_id = None
            if File.objects.filter(is_sync=False).count() > 0:
                dag_run_id = exec_dag(DAG_ID, conf, AUTH)
            request.session[SPN.DAG_RUN_ID_EXPORT] = dag_run_id
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
