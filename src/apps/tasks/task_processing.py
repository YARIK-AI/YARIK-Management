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


'''
def get_logs(dag_id, dag_run_id, task_id, try_num=1, out='str'):
    serializer = URLSafeSerializer(secret_key)
    token = serializer.dumps({"log_pos": 5})

    formats = ['str', 'list']
    if out not in formats:
        raise ValueError(f'The get_logs function only supports the following output formats: {formats}.')

    h = {"Accept": "text/plain"}
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_num}?token={token}"
    if out=="list":
        logs = get_request(url, headers=headers, out='json')
        logger.info(logs)
        ct = logs["continuation_token"]
        metadata = URLSafeSerializer(secret_key).loads(ct)
        log_pos = metadata["log_pos"]
        end_of_log = metadata["end_of_log"]
        logger.info(log_pos)
        logger.info(end_of_log)
        logger.info(logs["content"].removeprefix("[(").removesuffix(")]").replace('\\\'', '\'').replace('\\\\', '\\').split('\n'))
        return logs["content"].removeprefix("[(").removesuffix(")]").replace('\\\'', '\'').replace('\\\\', '\\').split('\n')
    else:
        return get_request(url, headers=h, out='text')
'''


def get_last_dag_run(dag_id, after_date=datetime.datetime.fromisoformat("2023-01-01T00:00:00Z")):
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns?limit=1"
    total_dag_runs = int(get_request(url)["total_entries"])
    last_dag_run = get_request(url+f"&offset={total_dag_runs-1}")["dag_runs"][-1]
    logger.info(datetime.datetime.fromisoformat(last_dag_run["logical_date"]))
    logger.info(after_date)
    if datetime.datetime.fromisoformat(last_dag_run["logical_date"]) < after_date:
        last_dag_run = {}
    return last_dag_run


def get_last_dag_run_id(dag_id, after_date=datetime.datetime.fromisoformat("2023-01-01T00:00:00Z")):
    last_dag_run = get_last_dag_run(dag_id, after_date)
    dag_run_id = None
    if last_dag_run:
        dag_run_id = last_dag_run.get("dag_run_id")
        after_date = datetime.datetime.fromisoformat(last_dag_run.get("logical_date"))
    return (dag_run_id, after_date)


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


def is_active(dag_id, after_date=datetime.datetime.fromisoformat("2023-01-01T00:00:00Z")) -> bool:
    return get_last_dag_run(dag_id, after_date).get("state") in ["queued", "running"]


def get_dag_info(dag_id, dag_run_id, ext_dag_ids=[], ext_task_ids=[]):
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


def pause_dag(dag_id):
    payload = {
        "is_paused": True,
    }
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}"
    
    response = requests.patch(url, headers=headers, auth=AUTH, json=payload)

    if response.status_code != requests.codes.ok:
        return False
    
    is_paused = json.loads(response.text)["is_paused"]

    while not is_paused:
        response = requests.patch(url, headers=headers, auth=AUTH, json=payload)
        if response.status_code != requests.codes.ok:
            return False
        is_paused = json.loads(response.text)["is_paused"]
    
    return True


def resume_dag(dag_id):
    payload = {
        "is_paused": False,
    }
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}"
    
    response = requests.patch(url, headers=headers, auth=AUTH, json=payload)

    if response.status_code != requests.codes.ok:
        return False
    
    is_paused = json.loads(response.text)["is_paused"]

    while is_paused:
        response = requests.patch(url, headers=headers, auth=AUTH, json=payload)
        if response.status_code != requests.codes.ok:
            return False
        is_paused = json.loads(response.text)["is_paused"]
    
    return True


def exec_dag(dag_id, conf={}):
    payload = {
        "conf": conf,
    }

    resume_dag(dag_id)

    # run dag
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    response = requests.post(url, headers=headers, auth=AUTH, json=payload)
    
    if response.status_code != requests.codes.ok:
        raise Exception(json.loads(response.text)["detail"])

    dag_run_id = json.loads(response.text)["dag_run_id"]
    
    return dag_run_id


def clear_dag_run(dag_id, dag_run_id) -> bool:
    payload = {
        "dry_run": False,
    }
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/clear"
    response = requests.post(url, headers=headers, auth=AUTH, json=payload)
    if response.status_code != requests.codes.ok:
        return False
    return True


def abort_dag_run(dag_id, dag_run_id) -> bool:

    if get_dag_run(dag_id, dag_run_id)["state"] == "success":
        return False

    clear_dag_run(dag_id, dag_run_id)
    pause_dag(dag_id)
    
    payload = {
        "state": "failed",
    }
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"

    response = requests.patch(url, headers=headers, auth=AUTH, json=payload)
    if response.status_code != requests.codes.ok:
        return False
    state = json.loads(response.text)["state"]

    while state != "failed":
        response = requests.patch(url, headers=headers, auth=AUTH, json=payload)
        if response.status_code != requests.codes.ok:
            return False
        state = json.loads(response.text)["state"]
        if state == "success":
            return False

    return True


def restart_dag_run(dag_id, dag_run_id) -> bool:

    if get_dag_run(dag_id, dag_run_id)["state"] in ["running", "queued"]:
        return False

    payload = {
        "dry_run": False,
    }
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/clear"
    response = requests.post(url, headers=headers, auth=AUTH, json=payload)
    if response.status_code != requests.codes.ok:
        return False
    
    resume_dag(dag_id)

    return True