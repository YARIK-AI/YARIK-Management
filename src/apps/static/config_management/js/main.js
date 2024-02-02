
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
activate_tooltips();
setActiveNavTab();
