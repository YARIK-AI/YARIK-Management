/* 
    RTYPE.
*/
const RTYPE = {
    ...RTYPE_Base,
    SHOW_FILTER: 50,
    SET_SCOPE: 51,
    RESET_SCOPE: 52,
    SET_STATUS: 53,
    RESET_STATUS: 54,
    UPD_SYNC_STATE: 55,
};

/* 
    ROPN.
*/
const ROPN = {
    ...ROPN_Base,
    VALUE: "value",
    COMMIT_MSG: "commit_msg",
    FILTER_ID: "filter_id",
    FILTER_VALUE: "filter_value",
};

/* 
    RIPN.
*/
const RIPN = {
    ...RIPN_Base,
    IS_VALID: "is_valid",
    STATUS_FILTER: "status_dict",
    DEFAULT_VAL: "default_value",
    STATUS: "filter_status",
    FILTER_ITEMS: "filter_items",
    SELECTED_ITEM: "selected_item",
    SYNC_STATE: "sync_state",
    NOT_SYNC_CNT: "not_sync_cnt",
};


/* 
    Specific globals.
*/
const URL_SLUG = "/configuration/";

const FILTERS = {
    SCOPE: 1,
    STATUS: 2,
}


const class_filter_mapping = {
    ".scopeList": FILTERS.SCOPE,
    ".statusList": FILTERS.STATUS
};

const filter_id_mapping = {
    [FILTERS.SCOPE]: "collapseListScope",
    [FILTERS.STATUS]: "collapseListStatus"
};

const id_filter_mapping = {
    "collapseListScope": FILTERS.SCOPE,
    "collapseListStatus": FILTERS.STATUS
};