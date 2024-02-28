function updateTaskInfos(tasks) {
    $.each(tasks, function(i, task) {
        let start_time_indicator = document.getElementById(`${task.name}-logical-time`);
        let paste_html;

        if( task.state === "running" || task.state === "queued") {
            document.getElementById(`${task.name}-cur-state`).innerText = task.state;
        } else {
            let state_indicator = document.getElementById(`${task.name}-task-status`);
            const icon_id = task.state === "success" ? "ok" : "failed";
            paste_html = `
                <svg class="icon icon-xxl" aria-hidden="true">
                    <use href="/static/assets/icons/state-icon.svg#${icon_id}"></use>
                </svg>
            `
            state_indicator.innerHTML = `
                <span class="me-4">Status</span>
                ${paste_html}
                <strong class="ms-1" role="status" id="${task.name}-cur-state">${task.state}</strong>
            `;
        }
        
        start_time_indicator.innerText = task.time;
    });
};