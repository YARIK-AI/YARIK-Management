/* 
    Request types.
*/
const RTYPE_Base = {
    CHANGE: 1,
    SAVE: 2,
    SHOW_CHANGES: 3,
    SELECT_PAGE: 4,
    SET_PER_PAGE: 5,
    SET_SEARCH: 6,
    RESET_SEARCH: 7,
};

/*
    Request Output Parameter Names - ROPN.\n
    Output parameter names of submitted requests for this application.\n
    Must match the parameter names accepted by the server.
*/
const ROPN_Base = {
    TYPE: 'type',
    PARAM_ID: "param_id",
    PAGE_N: "page_n",
    SEARCH: "search_str",
    PER_PAGE: "params_per_page",
};

/*
    Response Input Parameter Names - RIPN.\n
    Names of recieved response parameters for this application.\n
    Must match the parameter names sent from the server.
*/
const RIPN_Base = {
    TYPE: "type",
    PREV_VAL: "old_val",
    MSG: "msg",
    CHANGES: "changes",
    LIST_EL: "results",
    PAGE_N:  "page_n",
    NUM_PAGES: "num_pages",
    AIRFLOW_CONN_GOOD: "airflow_conn_good",
    RESTART_NEEDED: "restart_needed",
};