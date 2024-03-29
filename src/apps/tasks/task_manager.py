from .models import Dag, Queue

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


class TaskManager:

    def __init__(self, active_dag_id, dag_run_ids, dag_run_info_dict):
        self.current_dag_id = active_dag_id
        self.dag_run_ids = dag_run_ids
        self.dag_run_info_dict = dag_run_info_dict


    @classmethod
    def is_conn_good(cls) -> bool:
        try:
            requests.get(f"{AIRFLOW_URL}/api/v1/dags", headers=HEADERS, auth=AUTH, timeout=1)
            return True
        except requests.exceptions.ConnectionError as e:
            return False
        except Exception as e:
            return False
        

    @classmethod
    def has_dags_from_queue(cls, queue_id) -> bool:
        queue = Queue.objects.get(pk=queue_id)
        try:
            for dag_id in queue.get_queue_list():
                Dag.objects.get(pk=dag_id).get_info_about_dag()
        except NameError:
            return False
        except Exception as e:
            return False
        
        return True



    def manage_dags(self) -> bool:
        dag = Dag.objects.get(dag_id=self.current_dag_id)
        active_dag_id = self.current_dag_id

        dag_run = dag.get_dag_run(self.dag_run_ids[active_dag_id])

        new_active_dag_id = active_dag_id

        if dag_run.state not in ["queued", "running"]:
            self.dag_run_info_dict[active_dag_id] = dag.get_target_info(
                self.dag_run_ids[active_dag_id],
                ext_dag_ids=[active_dag_id,],
                ext_task_ids=[task.task_id for task in dag.tasks]
            )
            
            new_active_dag_id = None

        sync_success = False

        if dag_run.state == "success":
            next_dag: Dag = dag.next_dag
            if next_dag:

                if next_dag:
                    dag_run_id = next_dag.trigger()

                    logger.info("Next task triggered.")

                    self.dag_run_ids[next_dag.dag_id] = dag_run_id
                    new_active_dag_id = next_dag.dag_id
                else:
                    new_active_dag_id = None
            else:
                sync_success = True
                logger.info("The dag queue has completed its work.")
        
        active_dag_id = new_active_dag_id
        self.current_dag_id = active_dag_id

        return sync_success
    

    def request_latest_state(self, queue_id):
        self.dag_run_ids = {}
        after_date = dttm.fromisoformat("2023-01-01T00:00:00Z")
        queue = Queue.objects.get(queue_id=queue_id)
        queue_list = queue.get_queue_list()

        sync_success = False

        for dag_id in queue_list:
            last_dag_run_id = None
            try:
                dag = Dag.objects.get(pk=dag_id)
                last_dag_run = dag.get_last_dag_run(after_date)
                if last_dag_run:
                    after_date = dttm.fromisoformat(last_dag_run.logical_date)
                    last_dag_run_id = last_dag_run.dag_run_id
                    if queue.dag_id_end.dag_id == dag_id and last_dag_run.state == "success":
                        sync_success = True
            except Exception as e:
                logger.error(e)
            finally:
                self.dag_run_ids[dag.dag_id] = last_dag_run_id

        self.dag_run_info_dict = {}
        for dag in Dag.objects.all():
            dag_info = {
                "id": dag.dag_id,
                "name": dag.name,
                "state": "waiting",
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
                dag_run_id = self.dag_run_ids.get(dag.dag_id, None)
                if dag_run_id:
                    dag_info = dag.get_target_info(
                        self.dag_run_ids.get(dag.dag_id, None),
                        ext_dag_ids=[dag.dag_id,],
                        ext_task_ids=[task.task_id for task in dag.tasks]
                    )
                if dag.is_active():
                    self.current_dag_id = dag.dag_id
                else:
                    raise ValueError(f"No dag run for dag {dag.dag_id} after {after_date}")
            except ValueError as e:
                logger.info(e)
            except Exception as e:
                logger.error(e)
            finally:
                self.dag_run_info_dict[dag.dag_id] = dag_info

        return sync_success

    
    def get_info(self, expanded_dag_ids=[], expanded_task_ids=[]):
        tasks = []

        for dag in Dag.objects.all():
            task = {}
            if dag.dag_id == self.current_dag_id:
                task = dag.get_target_info(
                    self.dag_run_ids.get(dag.dag_id, None),
                    ext_dag_ids=expanded_dag_ids, 
                    ext_task_ids=expanded_task_ids
                )
                self.dag_run_info_dict[dag.dag_id] = task

                #request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
            else:
                task = self.dag_run_info_dict.get(dag.dag_id, {})
            tasks.append(task)

        return tasks

