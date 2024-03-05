from apps.globals import RIPN_Base, ROPN_Base, RTYPE_Base

class SPN:
    """
        Session Parameter Names - spn.\n
        Name of session parameters for this application.
    """
    DAG_RUN_ID_EXPORT = "export_dag_run_id"
    DAG_RUN_ID_TRANSFORM = "transform_dag_run_id"
    DAG_RUN_ID_DICT = "dag_run_id_list"
    ACTIVE_DAG_ID = "active_dag_id"
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
    

class RTYPE(RTYPE_Base):
    UPDATE_STATE = 150
    ABORT = 151
    SHOW_LOGS = 152


DAG_ID_FIRST = "export_xml"
DAG_ID_SECOND = "transform_xml"


DAG_NAMES = {
    DAG_ID_FIRST: "Export",
    DAG_ID_SECOND: "Transform"
}

TASK_DICT = {
    DAG_ID_FIRST: [ "export_xml_task", "create_bucket_task", "store_to_s3" ],
    DAG_ID_SECOND: [ "transform_task", "sync_db_task" ]
}

TASK_NAMES = { 
    TASK_DICT[DAG_ID_FIRST][0]: "Export XML files from the database", 
    TASK_DICT[DAG_ID_FIRST][1]: "Create bucket on s3 minio", 
    TASK_DICT[DAG_ID_FIRST][2]: "Store xml to bucket on s3 minio", 
    TASK_DICT[DAG_ID_SECOND][0]: "Converting and saving files",
    TASK_DICT[DAG_ID_SECOND][1]: "Sync resources in db",
}
