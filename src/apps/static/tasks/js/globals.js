/* 
    RTYPE.
*/
const RTYPE = {
    ...RTYPE_Base,
    UPDATE_STATE: 150,
    ABORT: 151,
    SHOW_LOGS: 152,
};

/* 
    ROPN.
*/
const ROPN = {
    ...ROPN_Base,
    TASK_IDS_EXPD: "task_ids_expanded",
    SUBTASK_IDS_EXPD: "subtask_ids_expanded",
    TASK_ID: "task_id",
    SUBTASK_ID: "subtask_id",
};

/* 
    RIPN.
*/
const RIPN = {
    ...RIPN_Base,
    LIST_EL: "tasks",
    SURVEY_REQUIRED: "survey_required",
    LOGS: "logs",
    STATUS: "status",
};


/* 
    Specific globals.
*/

const URL_SLUG = "/tasks/";

let is_survey_required = true;
