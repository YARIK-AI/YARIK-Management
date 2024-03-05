function updateTaskInfos(tasks, survey_required) {
    function displayByTask (i, task) {
        let start_time_indicator = document.getElementById(`${task.id}-logical-time`);
        document.getElementById(`collapse-steps-btn-${task.id}`).innerText = `Completed ${task.completed_steps} of ${task.total_steps} step(s).`;

        let paste_html;
        let state_indicator = document.getElementById(`${task.id}-task-status`);

        switch(task.state) {
            case "running":
            case "queued": {
                let spinner = document.getElementById(`run-task-spinner-${task.id}`);
                if(spinner === null) {
                    state_indicator.innerHTML = `
                        <span class="me-4">Status</span>
                        <div class="spinner-border" aria-hidden="true" id="run-task-spinner-${task.id}"></div>
                        <strong class="ms-1" role="status" id="${task.id}-cur-state">${task.state}</strong>
                    `;
                } else {
                    document.getElementById(`${task.id}-cur-state`).innerText = task.state;
                }
                break;
            }
            case "success":
            case "failed":
            case "upstream_failed":
            case "skipped":
            case "no_status":  {
                state_indicator.innerHTML = `
                    <span class="me-4">Status</span>
                    <svg class="icon icon-xxl" aria-hidden="true">
                        <use href="/static/assets/icons/tasks-icons.svg#${task.state}"></use>
                    </svg>
                    <strong class="ms-1" role="status" id="${task.id}-cur-state">${task.state}</strong>
                `;
                break;
            }
            default: {
                state_indicator.innerHTML = `
                    <span class="me-4">Status</span>
                    <svg class="icon icon-xxl" aria-hidden="true">
                        <use href="/static/assets/icons/tasks-icons.svg#default"></use>
                    </svg>
                    <strong class="ms-1" role="status" id="${task.id}-cur-state">Waiting</strong>
                `;
                break;
            }
        }

        if(task.state === "success") {
            $(`#duration-or-abort[name="${task.id}"]`)[0].innerHTML = `
            <svg class="icon icon-xxl" aria-hidden="true">
                <use href="/static/assets/icons/tasks-icons.svg#duration"></use>
            </svg>
            <strong class="ms-1">${task.duration}</strong>
            `
        }
        
        start_time_indicator.innerText = task.time;

        paste_html = null;

        function displayBySubtask(i, subtask) {
            let btn = document.getElementById(`collapseBtn-${subtask.id}`);

            switch(subtask.state) {
                case "running":
                case "queued": {
                    let spinner = document.getElementById(`run-spinner-${subtask.id}`);
                    if(spinner === null) {
                        paste_html = `
                            <div class="spinner-border" aria-hidden="true" id="run-spinner-${subtask.id}"></div>
                            <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask.name} - ${subtask.state}</strong>
                        `;
                    } else {
                        document.getElementById(`${subtask.id}-sub-cur-state`).innerText = `${subtask.name} - ${subtask.state}`;
                    }
                    break;
                }
                case "success":
                case "failed":
                case "upstream_failed":
                case "skipped":
                case "no_status": {
                    paste_html = `
                        <svg class="icon icon-xxl" aria-hidden="true">
                            <use href="/static/assets/icons/tasks-icons.svg#${subtask.state}"></use>
                        </svg>
                        <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask.name} - ${subtask.duration}</strong>
                    `;
                    break;
                }
                default: {
                    paste_html = `
                        <svg class="icon icon-xxl" aria-hidden="true">
                            <use href="/static/assets/icons/tasks-icons.svg#default"></use>
                        </svg>
                        <strong class="ms-1" role="status" id="${subtask.id}-sub-cur-state">${subtask.name} - waiting</strong>
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
                    buf = buf.concat('\n', `<p class="mb-0">${log}</p>`);
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
};