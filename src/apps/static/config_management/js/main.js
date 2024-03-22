
// bind
$('#search-field').on('propertychange input', 'input.form-control.rounded', searchParams);
$('#collapseListScope').on('click', '.scopeList', selectFilter);
$('#collapseListStatus').on('click', '.statusList', selectFilter);
$('#upd2').on('click', '.page-link', selectPage);
$('#save-changes-btn').on('click', saveChanges);
$('#upd').on('change', '.param-input', fixChange);
$('#upd').on('click', '.restore-default', fixChange);
$('#collapseListStatus').on('show.coreui.collapse', showFilter);
$('#collapseListScope').on('show.coreui.collapse', showFilter);
$('#show-modal-btn').on('click', showChanges);
$('#params-per-page').on('change', setParamsPerPage);
$('#sidebar-toggler').on('click', function(event) {
    let sidebarNode = document.querySelector('#sidebar')
    let sidebar = coreui.Sidebar.getInstance(sidebarNode)
    if(sidebarNode.classList.contains('hide')){
        sidebar.show();
    }
    else{
        sidebar.hide();
    }
});


// init
const page_n = document.currentScript.getAttribute('page_n');
const num_pages = document.currentScript.getAttribute('num_pages');
const task_state_running = document.currentScript.getAttribute('task_state_running');

/*
let updIntervalId;

if(task_state_running) {
    updIntervalId = window.setInterval(updSyncState, 5000);
}*/


if (typeof num_pages !== 'undefined' && num_pages !== null) {
    updatePageSelector(num_pages, typeof page_n === 'undefined' || page_n === null ? 1: page_n);
}

activate_tooltips();
setActiveNavTab();


