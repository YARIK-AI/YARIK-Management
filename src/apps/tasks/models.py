from django.db import models
from django.db.models.query import QuerySet

from datetime import datetime as dttm
import requests
import logging
import json

from core.settings import AIRFLOW_HOST, AIRFLOW_PORT

logger = logging.getLogger(__name__)

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

AIRFLOW_URL = f"http://{AIRFLOW_HOST}:{AIRFLOW_PORT}"

AUTH = ('admin', 'admin')

CONN_TIMEOUT = 1


class DagRun:
    def __init__(self, dag_run_json):
        self.dag_run_id = dag_run_json.get("dag_run_id")
        self.dag_id = dag_run_json.get("dag_id")
        self.logical_date = dag_run_json.get("logical_date")
        self.start_date = dag_run_json.get("start_date")
        self.end_date = dag_run_json.get("end_date")
        self.data_interval_start = dag_run_json.get("data_interval_start")
        self.data_interval_end = dag_run_json.get("data_interval_end")
        self.last_scheduling_decision = dag_run_json.get("last_scheduling_decision")
        self.run_type = dag_run_json.get("run_type")
        self.state = dag_run_json.get("state")
        self.external_trigger = dag_run_json.get("external_trigger")
        self.conf = dag_run_json.get("conf")
        self.note = dag_run_json.get("note")

    
class TaskInstance:
    def __init__(self, ti_json):
        self.task_id = ti_json.get("task_id")
        self.dag_id = ti_json.get("dag_id")
        self.dag_run_id = ti_json.get("dag_run_id")
        self.execution_date = ti_json.get("execution_date")
        self.start_date = ti_json.get("start_date")
        self.end_date = ti_json.get("end_date")
        self.duration = ti_json.get("duration")
        self.state = ti_json.get("state")
        self.try_number = ti_json.get("try_number")
        self.map_index = ti_json.get("map_index") 
        self.max_tries = ti_json.get("max_tries") 
        self.hostname = ti_json.get("hostname") 
        self.unixname = ti_json.get("unixname") 
        self.pool = ti_json.get("pool") 
        self.pool_slots = ti_json.get("pool_slots") 
        self.queue = ti_json.get("queue") 
        self.priority_weight = ti_json.get("priority_weight") 
        self.operator = ti_json.get("operator")
        self.queued_when = ti_json.get("queued_when")
        self.pid = ti_json.get("pid")
        self.executor_config = ti_json.get("executor_config")
        self.sla_miss = ti_json.get("sla_miss")
        self.rendered_fields = ti_json.get("rendered_fields")
        self.trigger = ti_json.get("trigger")
        self.triggerer_job = ti_json.get("triggerer_job")
        self.note = ti_json.get("note")



def get_request(url, headers=HEADERS, out='json') -> str | dict:
    formats = ['text', 'json']
    if out not in formats:
        raise ValueError(f'The get_request function only supports the following output formats: {formats}.')

    response = requests.get(url, headers=headers, auth=AUTH, timeout=CONN_TIMEOUT) # request


    if response.status_code == requests.codes.not_found:
        raise NameError(json.loads(response.text)["detail"]) 
    elif response.status_code != requests.codes.ok: # check responce
        raise Exception(json.loads(response.text)["detail"]) 
    
    if out=='text':
        return response.text
    else:
        return json.loads(response.text)


class Dag(models.Model):
    dag_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    @property
    def tasks(self) -> QuerySet["Task"]:
        return self.task_set.all()
    

    @property
    def __queue_elements(self) -> QuerySet["QueueElement"]:
        return self.queue_element_set.all()
    

    @property
    def __next_queue_elements(self) -> QuerySet["QueueElement"]:
        return self.queue_element_set_next.all()


    @property
    def next_dag(self):
        queue = self.__queue_elements.first()
        if queue:
            return queue.dag_id_next
        else:
            return None
        
    
    @property
    def prev_dag(self):
        queue = self.__next_queue_elements.first()
        if queue:
            return queue.dag_id_previous
        else:
            return None


    def get_info_about_dag(self):
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}"
        return get_request(url)



    def get_last_dag_run(self, after_date=dttm.fromisoformat("2023-01-01T00:00:00Z")) -> DagRun:
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns?limit=1"
        total_dag_runs = int(get_request(url)["total_entries"])
        
        offset = 0
        if total_dag_runs > 0:
            offset = total_dag_runs - 1

        dag_runs = get_request(url+f"&offset={offset}")["dag_runs"]

        last_dag_run = {}

        if len(dag_runs) > 0:
            last_dag_run = dag_runs[-1]
            if dttm.fromisoformat(last_dag_run["logical_date"]) < after_date:
                return None

        return DagRun(last_dag_run)


    def get_dag_run(self, dag_run_id) -> DagRun:
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns/{dag_run_id}"
        return DagRun(get_request(url))


    def get_task_instances(self, dag_run_id) -> list[TaskInstance]:
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns/{dag_run_id}/taskInstances"
        tis = get_request(url)["task_instances"]
        return list([TaskInstance(ti) for ti in tis])


    def is_active(self, after_date=dttm.fromisoformat("2023-01-01T00:00:00Z")) -> bool:
        return self.get_last_dag_run(after_date).state in ["queued", "running"]


    def get_target_info(self, dag_run_id, ext_dag_ids=[], ext_task_ids=[]):
        dag_run = self.get_dag_run(dag_run_id)
        task_instances = self.get_task_instances(dag_run_id)

        start_time = dttm.fromisoformat(dag_run.logical_date) \
            .strftime("%b %d, %Y, %I:%M:%S %p")
        tasks_total = self.tasks.count()
        ti_total = len(list(
            filter(lambda ti: ti.state == "success", task_instances)
        ))

        tasks = []
        dag_duration = 0.0
        for task in self.tasks:
            task_instance:TaskInstance
            for ti in task_instances:
                if ti.task_id == task.task_id:
                    task_instance = ti
                    break
            duration = task_instance.duration
            if duration:
                dag_duration += float(duration)

        if self.dag_id in ext_dag_ids:
            for task in self.tasks:

                task_instance:TaskInstance
                for ti in task_instances:
                    if ti.task_id == task.task_id:
                        task_instance = ti
                        break

                
                duration = task_instance.duration
                state = task_instance.state
                if state is None:
                    state = "no_status"
                if duration:
                    duration = f"{round(float(duration), 2)}s"

                logs = ["Waiting for logs", ]

                if task.task_id in ext_task_ids:
                    logs = task.get_logs(dag_run_id, try_num=1, out='list')

                tasks.append({
                    "id": task.task_id,
                    "name": task.name,
                    "state": state,
                    "duration": duration,
                    "logs": logs,
                })
        else:
            for task in self.tasks:
                tasks.append({ "id": task.task_id })

        task = {
            "id": self.dag_id,
            "name": self.name,
            "state": dag_run.state, 
            "time": start_time, 
            "duration": f"{round(dag_duration, 2)}s",
            "total_steps": tasks_total,
            "completed_steps": ti_total,
            "subtasks": tasks
        }

        return task


    def pause(self):
        payload = {
            "is_paused": True,
        }
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}"
        is_paused = False

        while not is_paused:
            response = requests.patch(url, headers=HEADERS, auth=AUTH, json=payload)
            if response.status_code == requests.codes.not_found:
                False
            if response.status_code != requests.codes.ok:
                return False
            is_paused = json.loads(response.text)["is_paused"]

        return True
    

    def resume(self):
        payload = {
            "is_paused": False,
        }
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}"
        is_paused = True

        while is_paused:
            response = requests.patch(url, headers=HEADERS, auth=AUTH, json=payload)
            if response.status_code != requests.codes.ok:
                return False
            is_paused = json.loads(response.text)["is_paused"]

        return True
    

    def trigger(self, conf={}) -> str:
        payload = {
            "conf": conf,
        }

        if not self.resume():
            return False

        # trigger dag
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns"
        response = requests.post(url, headers=HEADERS, auth=AUTH, json=payload)
        
        if response.status_code == requests.codes.not_found:
            raise NameError(json.loads(response.text)["detail"]) 
        if response.status_code != requests.codes.ok:
            raise Exception(json.loads(response.text)["detail"])

        dag_run_id = json.loads(response.text)["dag_run_id"]
        
        return dag_run_id


    def clear(self, dag_run_id) -> bool:
        payload = {
            "dry_run": False,
        }
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns/{dag_run_id}/clear"
        response = requests.post(url, headers=HEADERS, auth=AUTH, json=payload)

        if response.status_code == requests.codes.not_found:
            raise NameError(json.loads(response.text)["detail"]) 
        if response.status_code != requests.codes.ok:
            return False
        return True
    

    def abort(self, dag_run_id:str) -> bool:

        if not dag_run_id:
            return False

        if self.get_dag_run(dag_run_id).state == "success":
            return False

        if not self.clear(dag_run_id):
            return False
        
        if not self.pause():
            return False
        
        payload = {
            "state": "failed",
        }
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns/{dag_run_id}"

        response = requests.patch(url, headers=HEADERS, auth=AUTH, json=payload)
        if response.status_code != requests.codes.ok:
            return False
        '''
        state = ""
        while state != "failed":
            response = requests.patch(url, headers=HEADERS, auth=AUTH, json=payload)
            if response.status_code != requests.codes.ok:
                return False
            state = json.loads(response.text)["state"]
            if state == "success":
                return False
        '''

        return True


    def restart(self, dag_run_id) -> bool:

        if self.get_dag_run(dag_run_id).state in ["running", "queued"]:
            return False

        if not self.clear(dag_run_id):
            return False

        if not self.resume():
            return False

        payload = {
            "state": "queued",
        }
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag_id}/dagRuns/{dag_run_id}"

        response = requests.patch(url, headers=HEADERS, auth=AUTH, json=payload)
        if response.status_code != requests.codes.ok:
            return False
        
        return True




    class Meta:
        managed = False
        db_table = 'dags'


class Task(models.Model):
    task_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    dag = models.ForeignKey(Dag, models.DO_NOTHING, blank=True, null=True)


    def get_task_instance(self, dag_run_id) -> TaskInstance:
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag.dag_id}/dagRuns/{dag_run_id}/taskInstances/{self.task_id}"
        return TaskInstance(get_request(url))
    

    def get_logs(self, dag_run_id, try_num=1, out='str'):
        formats = ['str', 'list']
        if out not in formats:
            raise ValueError(f'The get_logs function only supports the following output formats: {formats}.')

        h = {"Accept": "text/plain"}
        url = f"{AIRFLOW_URL}/api/v1/dags/{self.dag.dag_id}/dagRuns/{dag_run_id}/taskInstances/{self.task_id}/logs/{try_num}"
        if out=="list":
            return get_request(url, headers=h, out='text').split('\n')
        else:
            return get_request(url, headers=h, out='text')


    class Meta:
        managed = False
        db_table = 'tasks'


class Queue(models.Model):
    queue_id = models.SmallIntegerField(primary_key=True)
    dag_id_begin = models.ForeignKey(Dag, models.DO_NOTHING, db_column='dag_id_begin', blank=True, null=True)
    dag_id_end = models.ForeignKey(Dag, models.DO_NOTHING, db_column='dag_id_end', related_name='queues_dag_id_end_set', blank=True, null=True)


    @property
    def queue_elements(self) -> QuerySet["QueueElement"]:
        return self.queue_element_set.all()


    def get_queue_list(self) -> list[str]:
        cur_dag = self.dag_id_begin
        queue_list = [cur_dag.dag_id,]
        while cur_dag != self.dag_id_end:
            cur_dag = cur_dag.next_dag
            queue_list.append(cur_dag.dag_id)

        return queue_list


    class Meta:
        managed = False
        db_table = 'queues'


class QueueElement(models.Model):
    queue_element_id = models.SmallIntegerField(primary_key=True)
    dag_id_previous = models.ForeignKey(Dag, models.DO_NOTHING, db_column='dag_id_previous', related_name='queue_element_set', blank=True, null=True)
    dag_id_next = models.ForeignKey(Dag, models.DO_NOTHING, db_column='dag_id_next', related_name='queue_element_set_next', blank=True, null=True)
    queue = models.ForeignKey(Queue, models.DO_NOTHING, related_name='queue_element_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'queue_element'

