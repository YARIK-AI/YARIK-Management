from apps.globals import RIPN_Base, ROPN_Base, RTYPE_Base

class SPN:
    """
        Session Parameter Names - spn.\n
        Name of session parameters for this application.
    """
    DAG_RUN_ID_EXPORT = "export_dag_run_id"


class RIPN(RIPN_Base):
    """
        Request Input Parameter Names - RIPN.\n
        Names of input parameters of received requests for this application.\n
        Must match the parameter names sent from the client using ajax.
    """
    


class ROPN(ROPN_Base):
    """
        Response Output Parameter Names - ROPN.\n
        Names of sent response parameters for this application.\n
        Must be consistent with the parameter names received by the client using Ajax.
    """
    LIST_EL = "tasks"
    



class RTYPE(RTYPE_Base):
    UPDATE_STATE = 150
    ABORT = 151

