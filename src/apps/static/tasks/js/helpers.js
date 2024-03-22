const escapeHTML = str => {
    return str.replace(
        /[&<>'"]/g,
        tag =>
        ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}


function disableBackBtn() {
    document.getElementById('back-btn').classList.add('disabled');
}

function enableBackBtn() {
    document.getElementById('back-btn').classList.remove('disabled');
}

function disableFinishBtn() {
    document.getElementById('finish-btn').classList.add('disabled');
}

function enableFinishBtn() {
    document.getElementById('finish-btn').classList.remove('disabled');
}


function updateTaskInfos(tasks, survey_required, is_finish, is_terminated) {
    
    function displayByTask (i, task) {
        let start_time_indicator = document.getElementById(`${task.id}-logical-time`);
        document.getElementById(`collapse-steps-btn-${task.id}`).innerText = `Completed ${task.completed_steps} of ${task.total_steps} step(s).`;

        let paste_html;
        let state_indicator = document.getElementById(`${task.id}-task-status`);

        let task_state;
        if(typeof task.state !== "undefined" && task.state !== null) {
            task_state = task.state.split('_').join(' ');
            task_state = task_state.charAt(0).toUpperCase() + task_state.slice(1);
        }

        switch(task.state) {
            case "running":
            case "queued": {
                let spinner = document.getElementById(`run-task-spinner-${task.id}`);
                if(spinner === null) {
                    state_indicator.innerHTML = `
                        <div class="me-4">
                            <span>Status</span>
                        </div>
                        <div>
                            <div class="spinner-border" aria-hidden="true" id="run-task-spinner-${task.id}"></div>
                        </div>
                        <div class="ms-1">
                            <strong role="status" id="${task.id}-cur-state">${task_state}</strong>
                        </div>
                    `;
                } else {
                    document.getElementById(`${task.id}-cur-state`).innerText = task_state;
                }
                break;
            }
            case "success":
            case "failed":
            case "upstream_failed":
            case "skipped":
            case "no_status":  {
                state_indicator.innerHTML = `
                    <div class="me-4">
                        <span>Status</span>
                    </div>
                    <div>
                        <svg class="icon icon-xxl" aria-hidden="true">
                            <use href="/static/assets/icons/tasks-icons.svg#${task.state}"></use>
                        </svg>
                    </div>
                    <div class="ms-1">
                        <strong role="status" id="${task.id}-cur-state">${task_state}</strong>
                    </div>
                `;
                break;
            }
            default: {
                state_indicator.innerHTML = `
                    <div class="me-4">
                        <span>Status</span>
                    </div>
                    <div>
                    <svg class="icon icon-xxl" aria-hidden="true">
                        <use href="/static/assets/icons/tasks-icons.svg#default"></use>
                    </svg>
                    </div>
                    <div class="ms-1">
                        <strong class="ms-1" role="status" id="${task.id}-cur-state">Waiting</strong>
                    </div>  
                `;
                break;
            }
        }

        const have_abort_btn = document.getElementById(`abort-task-btn-${task.id}`) !== null;
        const have_restart_btn = document.getElementById(`restart-task-btn-${task.id}`) !== null;

        if(task.state === "success" && (have_abort_btn || have_restart_btn)) {
            $(`#duration-or-abort[name="${task.id}"]`)[0].innerHTML = `
            <svg class="icon icon-xxl" aria-hidden="true">
                <use href="/static/assets/icons/tasks-icons.svg#duration"></use>
            </svg>
            <strong class="ms-1">${task.duration}</strong>
            `
        } else if(task.state === "failed" && !have_restart_btn) {
            $(`#duration-or-abort[name="${task.id}"]`)[0].innerHTML = `
                <button class="btn btn-white btn-outline-dark restart-task-btn" id="restart-task-btn-${task.id}" data-task-id="${task.id}" data-op-type="restart">Restart</button>
            `
        } else if((task.state === "running" || task.state === "queued") && !have_abort_btn) {
            $(`#duration-or-abort[name="${task.id}"]`)[0].innerHTML = `
                <button class="btn btn-white btn-outline-dark abort-task-btn" id="abort-task-btn-${task.id}" data-task-id="${task.id}" data-op-type="abort">Abort</button>
            `
        }
        
        let task_time;
        if(typeof task.time === "undefined") task_time = "Not started";
        else task_time = task.time;
        start_time_indicator.innerText = task_time;

        paste_html = null;

        function displayBySubtask(i, subtask) {
            let btn = document.getElementById(`collapseBtn-${subtask.id}`);

            let subtask_state;
            if(typeof subtask.state !== "undefined" && subtask.state !== null) {
                subtask_state = subtask.state.split('_').join(' ');
                subtask_state = subtask_state.charAt(0).toUpperCase() + subtask_state.slice(1);
            }
            let subtask_duration = subtask.duration;
            if(subtask_duration === null || subtask_duration == 0) subtask_duration = subtask_state;
            
            let subtask_name = "Subtask";
            if(typeof subtask.name !== 'undefined') {
                subtask_name = subtask.name;
            }

            switch(subtask.state) {
                case "running":
                case "queued": {
                    let spinner = document.getElementById(`run-spinner-${subtask.id}`);
                    if(spinner === null) {
                        paste_html = `
                            <div class="spinner-border" aria-hidden="true" id="run-spinner-${subtask.id}"></div>
                            <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask_name} - ${subtask_state}</strong>
                        `;
                    } else {
                        document.getElementById(`${subtask.id}-sub-cur-state`).innerText = `${subtask_name} - ${subtask_state}`;
                    }
                    break;
                }
                case "failed":
                case "upstream_failed":
                case "skipped":
                case "scheduled":
                case "no_status": {
                    paste_html = `
                        <svg class="icon icon-xxl" aria-hidden="true">
                            <use href="/static/assets/icons/tasks-icons.svg#${subtask.state}"></use>
                        </svg>
                        <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask_name} - ${subtask_state}</strong>
                    `;
                    break;
                }
                case "success": {
                    paste_html = `
                        <svg class="icon icon-xxl" aria-hidden="true">
                            <use href="/static/assets/icons/tasks-icons.svg#${subtask.state}"></use>
                        </svg>
                        <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask_name} - ${subtask_duration}</strong>
                    `;
                    break;
                }
                default: {
                    paste_html = `
                        <svg class="icon icon-xxl" aria-hidden="true">
                            <use href="/static/assets/icons/tasks-icons.svg#default"></use>
                        </svg>
                        <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask_name} - waiting</strong>
                    `;
                    break;
                }
            }

            if(paste_html !== null) btn.innerHTML = paste_html;
            paste_html = null;

            const collapse_btn = document.getElementById(`collapseBtn-${subtask.id}`);
            let log_container = document.getElementById(`collapseSubtaskBody-${subtask.id}`);
            let paste_text = `<article class="pt-4 pb-4 bg-white ps-4 pe-4 rounded-2"><p class="mb-0">Waiting for logs<p></article>`;
            if(collapse_btn.ariaExpanded === "true") {
                let buf = "";
                function p (i, log) {
                    buf = buf.concat('\n', `<p class="mb-0">${escapeHTML(log)}</p>`);
                }
                $.each(subtask.logs, p);
                if(buf.length) paste_text = `<article class="pt-4 pb-4 bg-white ps-4 pe-4 rounded-2">${buf}</article>`;
            } 
            log_container.innerHTML = paste_text;

        }
        $.each(task.subtasks, displayBySubtask);
    };
    $.each(tasks, displayByTask);
    is_survey_required = survey_required;

    if(is_finish) {
        enableFinishBtn();
        disableBackBtn();
    } else {
        disableFinishBtn();
    }

    if(is_terminated) {
        enableBackBtn();
        disableFinishBtn();
    }
    else {
        disableBackBtn();
    }
};