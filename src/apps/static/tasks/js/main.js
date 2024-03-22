$('#tasks-list').on('click', 'button.abort-task-btn, button.restart-task-btn', manageTask);
function updState() {
    if(!request_has_been_sent) updateState();
}

let updIntervalId = window.setInterval(updState, 1000);

let watchIntervalId = window.setInterval(function() {
    if(!is_survey_required) { 
        if(updIntervalId !== null) {
            clearInterval(updIntervalId);
            updIntervalId = null;
            // bind
            $('div.collapseLogs').on('show.coreui.collapse', showLogs);
        }

    }
    if(is_survey_required) {
        if(updIntervalId === null) {
            upd_in_progress = true;
            updIntervalId = window.setInterval(updState, 1000);
            // unbind
            $('div.collapseLogs').on('show.coreui.collapse', function(event){});
        }
    }
}, 250);
