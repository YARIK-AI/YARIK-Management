from apps.globals import *

class SPN(SPN_Base):
    """
        Session Parameter Names - spn.\n
        Name of session parameters for this application.
    """
    ACTIVE_DAG_ID = "active_dag_id"
    DAG_RUN_ID_DICT = "dag_run_id_list"
    DAG_RUN_INFO_DICT = "dag_run_info_dict"


class RIPN(RIPN_Base):
    """
        Request Input Parameter Names - RIPN.\n
        Names of input parameters of received requests for this application.\n
        Must match the parameter names sent from the client using ajax.
    """
    DAG_IDS_EXPD = "task_ids_expanded[]"
    TASK_IDS_EXPD = "subtask_ids_expanded[]"
    TASK_ID = "task_id"
    SUBTASK_ID = "subtask_id"
    


class ROPN(ROPN_Base):
    """
        Response Output Parameter Names - ROPN.\n
        Names of sent response parameters for this application.\n
        Must be consistent with the parameter names received by the client using Ajax.
    """
    LIST_EL = "tasks"
    SURVEY_REQUIRED = "survey_required"
    LOGS = "logs"
    STATUS = "status"
    IS_FINISH = "is_finish"
    IS_TERMINATED = "is_terminated"
    

class RTYPE(RTYPE_Base):
    UPDATE_STATE = 150
    ABORT = 151
    SHOW_LOGS = 152
    RESTART = 153


QUEUE_ID = 1