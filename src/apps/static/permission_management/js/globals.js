/* 
    RTYPE.
*/
const RTYPE = {
    ...RTYPE_Base,
    SELECT_GROUP: 100,
};

/* 
    ROPN.
*/
const ROPN = {
    ...ROPN_Base,
    GROUP_ID: "group_id",
    PERM_ID: "perm_id",
};

/* 
    RIPN.
*/
const RIPN = {
    ...RIPN_Base,
};


/* 
    Specific globals.
*/

const URL_SLUG = "/permissions/";

const perm_code = {
    'change_parameter': 0,
    'view_parameter': 1,
    'no_permissions': 2,
};

const perm_name = {
    'change_parameter': "Change",
    'view_parameter': "View",
    'no_permissions': "No permissions",
};