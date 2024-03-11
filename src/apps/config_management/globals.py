from apps.globals import *

class SPN(SPN_Base):
    """
        Session Parameter Names - spn.\n
        Name of session parameters for this application.
    """
    CHANGES = "conf_changes_dict" 
    """
        Defines the name of the session parameter in which changes are stored.
    """
    PAGE_N =  "conf_page_n"
    """
        Defines the name of the session parameter, which stores the current page number.
    """
    PER_PAGE = "conf_per_page"
    """
        Defines the name of the session parameter, which stores the number of elements per page.
    """
    SEARCH = "conf_search"
    """
        Defines the name of the session parameter in which the entered search string is stored.
    """
    STATUS = "filter_status"
    SCOPE = "filter_scope"
    REPO_PATH = "repo_path"


class RIPN(RIPN_Base):
    """
        Request Input Parameter Names - RIPN.\n
        Names of input parameters of received requests for this application.\n
        Must match the parameter names sent from the client using ajax.
    """
    VALUE = "value"
    COMMIT_MSG = "commit_msg"
    FILTER_ID = "filter_id"
    FILTER_VALUE = "filter_value"


class ROPN(ROPN_Base):
    """
        Response Output Parameter Names - ROPN.\n
        Names of sent response parameters for this application.\n
        Must be consistent with the parameter names received by the client using Ajax.
    """
    IS_VALID = "is_valid"
    STATUS_FILTER = "status_dict"
    DEFAULT_VAL = "default_value"
    STATUS = "filter_status"
    FILTER_ITEMS = "filter_items"
    SELECTED_ITEM = "selected_item"
    SYNC_STATE = "sync_state"
    NOT_SYNC_CNT = "not_sync_cnt"



class RTYPE(RTYPE_Base):
    SHOW_FILTER = 50
    SET_SCOPE = 51
    RESET_SCOPE = 52
    SET_STATUS = 53
    RESET_STATUS = 54
    UPD_SYNC_STATE = 55


class FILTERS:

    SCOPE = 1
    STATUS = 2