import json
import datetime
import requests
import logging

from .globals import DAG_NAMES, TASK_DICT, TASK_NAMES
from core.settings import AIRFLOW_HOST, AIRFLOW_PORT

logger = logging.getLogger(__name__)


headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

AIRFLOW_URL = f"http://{AIRFLOW_HOST}:{AIRFLOW_PORT}"

AUTH = ('admin', 'admin')


def exec_dag(dag_id, conf={}):
    payload = {
        "conf": conf,
    }

    # run dag
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    response = requests.post(url, headers=headers, auth=AUTH, json=payload)
    
    if response.status_code != requests.codes.ok:
        raise Exception(json.loads(response.text)["detail"])

    dag_run_id = json.loads(response.text)["dag_run_id"]
    
    return dag_run_id


def modify_dag_run(dag_id, dag_run_id, new_state):
    payload = {
        "state": new_state,
    }
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"

    response = requests.patch(url, headers=headers, auth=AUTH, json=payload)

    if response.status_code != requests.codes.ok:
        return False
    
    return True


def abort_dag_run(dag_id, dag_run_id) -> bool:
    return modify_dag_run(dag_id, dag_run_id, "failed")


def restart_dag_run(dag_id, dag_run_id):
    return modify_dag_run(dag_id, dag_run_id, "queued")


def get_request(url, headers=headers, out='json'):
    formats = ['text', 'json']
    if out not in formats:
        raise ValueError(f'The get_request function only supports the following output formats: {formats}.')

    response = requests.get(url, headers=headers, auth=AUTH) # request
    if response.status_code != requests.codes.ok: # check responce
        raise Exception(json.loads(response.text)["detail"])
    
    if out=='text':
        return response.text
    else:
        return json.loads(response.text)


def get_logs(dag_id, dag_run_id, task_id, try_num=1, out='str'):
    formats = ['str', 'list']
    if out not in formats:
        raise ValueError(f'The get_logs function only supports the following output formats: {formats}.')

    h = {"Accept": "text/plain"}
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_num}"
    if out=="list":
        return get_request(url, headers=h, out='text').split('\n')
    else:
        return get_request(url, headers=h, out='text')



def get_last_dag_run(dag_id):
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    last_dag_run = get_request(url)["dag_runs"][-1]
    dag_run_id = None
    if last_dag_run:
        dag_run_id = last_dag_run["dag_run_id"]
    return dag_run_id


def get_dag_run(dag_id, dag_run_id):
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
    return get_request(url)


def get_tasks_for_dag(dag_id) -> list:
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/tasks" 
    return get_request(url)["tasks"]


def get_tis_for_dag_run(dag_id, dag_run_id) -> list:
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances"
    return get_request(url)["task_instances"]


def get_ti(dag_id, dag_run_id, task_id):
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}"
    return get_request(url)



def get_task_info(dag_id, dag_run_id, ext_dag_ids=[], ext_task_ids=[]):
    dag_runs_info = get_dag_run(dag_id, dag_run_id)
    start_time = datetime.datetime.fromisoformat(dag_runs_info["logical_date"])

    tasks_total = len(get_tasks_for_dag(dag_id))

    ti_total = len(
        list(
            filter(
                lambda ti: ti["state"] == "success", 
                get_tis_for_dag_run(dag_id, dag_run_id)
            )
        )
    )

    subtasks = []
    dag_duration = 0.0
    
    if dag_id in ext_dag_ids:
        for task_id in TASK_DICT[dag_id]:
            task_name = TASK_NAMES[task_id]
            
            ti_info = get_ti(dag_id, dag_run_id, task_id)

            duration = ti_info["duration"]
            state = ti_info["state"]
            if state is None:
                state = "no_status"
            if duration:
                dag_duration += float(duration)
                duration = f"{round(float(duration), 2)}s"

            logs = ["Waiting for logs", ]
            logger.info(ext_task_ids)
            if task_id in ext_task_ids:
                logs = get_logs(dag_id, dag_run_id, task_id, try_num=1, out='list')

            subtasks.append({
                "id": task_id,
                "name": task_name,
                "state": state,
                "duration": duration,
                "logs": logs,
            })
    else:
        for task_id in TASK_DICT[dag_id]:
            subtasks.append({ "id": task_id })

    task = {
        "id": dag_id,
        "name": DAG_NAMES[dag_id],
        "state": dag_runs_info["state"], 
        "time": start_time.strftime("%b %d, %Y, %I:%M:%S %p"), 
        "duration": f"{round(dag_duration, 2)}s",
        "total_steps": tasks_total,
        "completed_steps": ti_total,
        "subtasks": subtasks
    }

    return task

