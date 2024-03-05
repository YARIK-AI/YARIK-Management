$('#tasks-list').on('click', '#abort-task-btn', abortTask);

let updIntervalId = window.setInterval(function() {
    updateState();
}, 1000);

let watchIntervalId = window.setInterval(function() {
    if(!is_survey_required && updIntervalId !== null) {
        clearInterval(updIntervalId);
        updIntervalId = null;
        // bind
        $('div.collapseLogs').on('show.coreui.collapse', showLogs);
    }
}, 1000);