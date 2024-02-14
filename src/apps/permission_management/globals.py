PERMS = [
    "change_parameter",
    "view_parameter",
    "no_permissions"
]


class SPN:
    """
        Session Parameter Names - spn.\n
        Name of session parameters for this application.
    """
    CHANGES = "perm_changes_dict" 
    """
        Defines the name of the session parameter in which changes are stored.
    """
    USER_ID = "perm_user_id"
    """
        Defines the name of the session parameter, which stores the selected user's ID.
    """
    PAGE_N =  "perm_page_n"
    """
        Defines the name of the session parameter, which stores the current page number.
    """
    PER_PAGE = "perm_per_page"
    """
        Defines the name of the session parameter, which stores the number of elements per page.
    """
    SEARCH = "perm_search"
    """
        Defines the name of the session parameter in which the entered search string is stored.
    """


class RIPN:
    """
        Request Input Parameter Names - RIPN.\n
        Names of input parameters of received requests for this application.\n
        Must be consistent with the parameter names sent from the client using ajax.
    """
    TYPE = "type"
    """
        Name of the input parameter containing the request type.
    """
    USER_ID = "user_id"
    """
        Name of the input parameter containing the selected user id.
    """
    PARAM_ID = "param_id"
    """
        Name of the input parameter containing the ID of the parameter being changed.
    """
    PERM_ID = "perm_id"
    """
        The name of the input parameter containing the ID of the specified permission for the object.
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
    

class ROPN:
    """
        Response Output Parameter Names - RIPN.\n
        Names of sent response parameters for this application.\n
        Must be consistent with the parameter names received by the client using Ajax.
    """
    TYPE = "type"
    """
        Name of the output parameter containing the request type.
    """
    PREV_VAL = "old_perm_name"
    """
        Name of the output parameter containing the previous value.
    """
    MSG  = "msg"
    """
        Name of the output parameter containing the message text.
    """
    CHANGES = "changes"
    """
        Name of the output parameter containing the current changes.
    """
    LIST_EL = "dict_par_perm"
    """
        The name of the output parameter containing the list of items to display.
    """
    PAGE_N =  "page_n"
    """
        Name of the output parameter containing the selected page number.
    """
    NUM_PAGES = "num_pages"
    """
        Name of the output parameter containing the total number of pages.
    """


class RTYPE:
    """
        Enumeration of Ajax request types.\n
        Must be consistent with the types of requests sent from the client using Ajax.
    """
    CHANGE = 1
    SAVE = 2
    SHOW_CHANGES = 3
    SELECT_USER = 4
    SELECT_PAGE = 5
    SET_PER_PAGE = 6
    SET_SEARCH = 7
    RESET_SEARCH = 8