function updateState() {
    function afterResponseUpdateState(resp) {
        function fn(tasks, survey_required) {
            updateTaskInfos(tasks, survey_required);
        };

        const fn_name = 'afterResponseUpdateState';
        const base_msg = 'Error displaying state after update.';
        const code = 4;
        const arg_names = [RIPN.LIST_EL, RIPN.SURVEY_REQUIRED];
        const checks = [cU, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    const task_btns = document.getElementsByClassName('collapse-steps-btn');
    const sub_btns = document.getElementsByClassName('collapseBtn');
    let task_ids = [];
    let subtask_ids = [];

    $.each(task_btns, function(i, btn) {
        if(btn.ariaExpanded === "true") {
            task_ids.push(btn.name);
        }
    });
    $.each(sub_btns, function(i, btn) {
        if(btn.ariaExpanded === "true") {
            subtask_ids.push(btn.name);
        }
    });


    function errorHandler(jqXHR, exception) {
        let msg;
        const base_msg = 'Response error.'
        try {
            if (jqXHR.status === 503) {
                msg = "Server error. Can't connect to Airflow.";
            } else {
                msg = `${base_msg} [${jqXHR.status}]`
            }
        } catch(e) {
            msg = `${base_msg} Unknown error.`;
            console.log(e);
        }
        finally {
            showToastMsg(msg);
            is_survey_required = false;
            clearInterval(updIntervalId);
            updIntervalId = null;
            location.reload();
        }
    };

    // ajax
    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: RTYPE.UPDATE_STATE,
            [ROPN.TASK_IDS_EXPD]: task_ids,
            [ROPN.SUBTASK_IDS_EXPD]: subtask_ids,
        },
        success: afterResponseUpdateState,
        error: errorHandler
    });
};


function manageTask(event) {
    event.preventDefault();
    const task_id = this.dataset.taskId;
    const op_type = this.dataset.opType;
    let type;
    if(op_type === "restart") {
        type = RTYPE.RESTART;
        is_survey_required = true;
    }
    else if(op_type === "abort") {
        type = RTYPE.ABORT;
    };

    function afterResponseManageTask(resp) {
        function fn(status) {
            if(status === true) showToastMsg(`Task ${op_type} signal sent.`);
            else showToastMsg(`Failed to send task ${op_type} signal`);

        };

        const fn_name = 'afterResponseManageTask';
        const base_msg = `Error displaying after ${op_type}ing task.`;
        const code = 4;
        const arg_names = [RIPN.STATUS];
        const checks = [cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    // ajax
    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: type,
            [ROPN.TASK_ID]: task_id,
        },
        success: afterResponseManageTask,
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        error: commonHandler
    });

};


function showLogs(event) {
    const task_id = this.dataset.taskId;
    const subtask_id = this.dataset.subtaskId;

    function afterResponseShowLogs(resp) {
        function fn(logs) {
            let log_container = document.getElementById(`collapseSubtaskBody-${subtask_id}`);
            let buf = "";
            $.each(logs, function (i, log) {
                buf = buf + `<p class="mb-0">${escapeHTML(log)}</p>`;
            });
            paste_text = `<article class="pt-4 pb-4 bg-white ps-4 pe-4 rounded-2">${buf}</article>`;
            log_container.innerHTML = paste_text;
        }

        const fn_name = 'afterResponseShowLogs';
        const base_msg = 'Error displaying logs.';
        const code = 4;
        const arg_names = [RIPN.LOGS];
        const checks = [cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: RTYPE.SHOW_LOGS,
            [ROPN.TASK_ID]: task_id,
            [ROPN.SUBTASK_ID]: subtask_id,
        },
        success: afterResponseShowLogs,
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        error: commonHandler
    });
}