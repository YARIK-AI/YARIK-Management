class SPN_Base:
    ACTIVE_DAG_ID = "active_dag_id"


class RIPN_Base:
    """
        Basic Request Input Parameter Names - RIPN.\n
        Names of basic input parameters of received requests.\n
        Must match the parameter names sent from the client using ajax.
    """
    TYPE = "type"
    """
        Name of the input parameter containing the request type.
    """
    PARAM_ID = "param_id"
    """
        Name of the input parameter containing the ID of the parameter being changed.
    """
    PAGE_N = "page_n"
    """
        Name of the input parameter containing the selected page number.
    """
    SEARCH = "search_str"
    """
        The name of the input parameter containing the entered search string.
    """
    PER_PAGE = "params_per_page"
    """
        The name of the input parameter containing the specified number of elements per page.
    """
    

class ROPN_Base:
    """
        Basic Response Output Parameter Names - ROPN_Base.\n
        Names of basic sent response parameters.\n
        Must be consistent with the parameter names received by the client using Ajax.
    """
    TYPE = "type"
    """
        Name of the output parameter containing the request type.
    """
    MSG  = "msg"
    """
        Name of the output parameter containing the message text.
    """
    LIST_EL = "results"
    """
        The name of the output parameter containing the list of items to display.
    """
    CHANGES = "changes"
    """
        Name of the output parameter containing the current changes.
    """
    PAGE_N =  "page_n"
    """
        Name of the output parameter containing the selected page number.
    """
    NUM_PAGES = "num_pages"
    """
        Name of the output parameter containing the total number of pages.
    """
    PREV_VAL = "old_val"
    """
        Name of the output parameter containing the previous value.
    """


class RTYPE_Base:
    """
        Enumeration of Ajax request types.\n
        Must be consistent with the types of requests sent from the client using Ajax.
    """
    CHANGE = 1
    SAVE = 2
    SHOW_CHANGES = 3
    SELECT_PAGE = 4
    SET_PER_PAGE = 5
    SET_SEARCH = 6
    RESET_SEARCH = 7


DAG_ID_FIRST = "export_xml"
DAG_ID_SECOND = "transform_xml"

DAG_ID_LIST = [DAG_ID_FIRST, DAG_ID_SECOND]


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