from apps.globals import *

PERMS = [
    "change_parameter",
    "view_parameter",
    "no_permissions"
]


class SPN(SPN_Base):
    """
        Session Parameter Names - spn.\n
        Name of session parameters for this application.
    """
    CHANGES = "perm_changes_dict" 
    """
        Defines the name of the session parameter in which changes are stored.
    """
    GROUP_ID = "perm_group_id"
    """
        Defines the name of the session parameter, which stores the selected group's ID.
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


class RIPN(RIPN_Base):
    """
        Request Input Parameter Names - RIPN.\n
        Names of input parameters of received requests for this application.\n
        Must match the parameter names sent from the client using ajax.
    """
    GROUP_ID = "group_id"
    """
        Name of the input parameter containing the selected GROUP id.
    """
    PERM_ID = "perm_id"
    """
        The name of the input parameter containing the ID of the specified permission for the object.
    """


class ROPN(ROPN_Base):
    """
        Response Output Parameter Names - ROPN.\n
        Names of sent response parameters for this application.\n
        Must be consistent with the parameter names received by the client using Ajax.
    """


class RTYPE(RTYPE_Base):
    SELECT_GROUP = 100