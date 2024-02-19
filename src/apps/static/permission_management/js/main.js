$('#select-group').on('change', changeGroupname);
$('#upd').on('change', 'tr td div div input.form-check-input', changePermission);
$('#upd').on('click', 'tr td button.undo', changePermission);
$('#show-modal-btn').on('click', showPermChanges);
$('#save-changes-btn').on('click', savePerms);
$('#upd2').on('click', '.page-link', selectPage);
$('#params-per-page').on('change', setParamsPerPage);
$('#search-field').on('propertychange input', 'input.form-control.rounded', searchParams);

// init
const page_n = document.currentScript.getAttribute('page_n');
const num_pages = document.currentScript.getAttribute('num_pages');

if (typeof num_pages !== 'undefined' && num_pages !== null) {
    updatePageSelector(num_pages, typeof page_n === 'undefined' || page_n === null ? 1: page_n);
}

activate_tooltips();