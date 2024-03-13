from .models import Dag

import logging

logger = logging.getLogger(__name__)


class TaskManager:

    def __init__(self, active_dag_id, dag_run_ids, dag_run_info_dict):
        self.current_dag_id = active_dag_id
        self.dag_run_ids = dag_run_ids
        self.dag_run_info_dict = dag_run_info_dict


    def manage_dags(self) -> str:
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
            #request.session[SPN.DAG_RUN_INFO_DICT] = dag_run_info_dict
            
            new_active_dag_id = None
        
        if dag_run.state == "success":
            next_dags = dag.next_dags
            logger.info(next_dags)
            if len(next_dags) > 0:
                next_dag = next_dags[0]
                dag_run_id = next_dag.trigger()

                logger.info("Next task triggered.")

                self.dag_run_ids[next_dag.dag_id] = dag_run_id
                new_active_dag_id = next_dag.dag_id

                #request.session[SPN.DAG_RUN_ID_DICT] = dag_run_id_dict
        
        #request.session[SPN.ACTIVE_DAG_ID] = new_active_dag_id
        active_dag_id = new_active_dag_id

        return active_dag_id

