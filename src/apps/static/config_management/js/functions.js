function activate_tooltips () {
    const tooltipTriggerList = document.querySelectorAll('[data-coreui-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new coreui.Tooltip(tooltipTriggerEl));
};

function updatePageSelector(num_pages, page_n) {
    $('#upd2').html('');
    for(var i = 1; i <= num_pages; i++) {
        $('#upd2').append(
            `<li class="page-item${(i==page_n?' active':'')}" id="${i}">
                <button type="button" class="page-link" href="${i}">${i}</button>
            </li>`
        );
    }
};

function updateTable(resp) {
    $('#upd').html('');
    $.each(resp.results, function(i, val) {
        var color_class = '';
        var value = val.value
        if(!!resp.changes) {
            if(!!resp.changes[val.id]) {
                color_class = resp.changes[val.id].is_valid ? 'border-warning': 'border-danger';
                value = resp.changes[val.id].new_value;
            }
        }
        var input = '';

        switch(val.input_type) {
            case 'checkbox':
                input = `<input class="form-check-input param-input ${color_class}" type="${val.input_type}" value="true" name="${val.id}" ${(value=='true'? 'checked="1"/>': '/>')}`;
                break;
            case 'textarea':
                input = `<textarea class="form-control param-input ${color_class}" placeholder="Enter parameter" id="${val.input_type}_${val.id}" name="${val.id}">${value.replaceAll('"', '&quot;')}</textarea>`;
                break;
            default:
                input = `<input class="form-control param-input ${color_class}" type="${val.input_type}" value="${value.replaceAll('"', '&quot;')}" name="${val.id}"/>`;

        }

        const restore_btn = `
            <span class="col-auto">${val.file.instance.app.component.name}</span>
            <button class="col-auto text-end btn btn-link btn-sm restore-default${(value == val.default_value? ' disabled': '')}" data-coreui-toggle="tooltip" data-coreui-placement="top" title="Restore default" type="button" id="${val.id}" href="${val.id}">
                <svg class="icon icon-xl" aria-hidden="true">
                    <use href="/static/assets/icons/restore-icon.svg#restore"></use>
                </svg>
            </button>`

        const description_block = `
            <span class="d-inline-block" tabindex="0" data-coreui-toggle="tooltip" title="${val.description}">
                <button class="btn btn-link" type="button" disabled>
                    <svg class="icon icon-xxl" aria-hidden="true">
                        <use href="/static/assets/icons/description-icon.svg#description"></use>
                    </svg>
                </button>
            </span>
        `

        $('#upd').append(
        `<tr>
            <td class="align-top col-2">
                ${val.file.instance.app.name}: ${val.name}
            </td>
            <td class="align-top col-5">
                <div class="d-flex flex-column">
                    <div class="d-flex flex-row justify-content-between">
                        ${restore_btn}
                    </div>
                    <div class="flex-fill">
                        ${input}
                    </div>
                </div>
            </td>
            <td class="align-bottom text-center col-1">
                ${description_block}
            </td>
        </tr>`
        );
    });
}

function updateStatusList(resp) {
    $('#collapseListStatus').html('');
    
    const cur_status = resp.cur_status;

    const name_mapping = {
        "edited": "Edited",
        "not_edited": "Not edited",
        "error": "Error",
        "non_default": "Non-default"
    };

    for ( const [key, value] of Object.entries(resp.status_dict)) {
        $('#collapseListStatus').append(
            `<button class="list-group-item list-group-item-secondary list-group-item-action d-inline-flex justify-content-between align-items-center statusList ${(cur_status == key? 'active':'')}"
            type="button" data-coreui-toggle="list" href="${key}" aria-controls="list-home" ${(cur_status == key? 'aria-current="true"':'')}>
            ${name_mapping[key]}<span class="badge bg-info rounded-pill">${value}</span></button>`
        )
    };
};

activate_tooltips();