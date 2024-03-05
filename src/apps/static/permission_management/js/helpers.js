function updateRadioButtons(param_perms) {

    $.each(param_perms, function(i, param) {
        let radio = $(`#upd div.input-group [name="radio-${param.id}"]`);
        const idx = perm_code[param.perm]

        for(let i = 0; i < radio.length; i++) {
            radio[i].checked = false;
        };

        radio[idx].checked = true;
    });

};


function updateTable(param_perms) {
    $('#upd').html('');
    if(param_perms.length > 0) {
        $.each(param_perms, function(i, param) {
            const color_class = param.perm_is_changed? 'bg-warning': '';

            const undo_btn = `
                <button class="col-auto text-end btn btn-link btn-sm undo ${param.perm_is_changed?'':' disabled'}" data-coreui-toggle="tooltip" data-coreui-placement="top" title="Undo" type="button" id="${param.id}" href="${param.id}">
                    <svg class="icon icon-xl" aria-hidden="true">
                        <use href="/static/assets/icons/permissions-icons.svg#undo"></use>
                    </svg>
                </button>`

            $('#upd').append(
            `<tr>
                <td class="align-top col-1">${param.id}</td>
                <td class="align-top col-2">${param.name}</td>
                <td class="align-top col-5">${param.description}</td>
                <td class="align-top col-auto ${color_class}">
                    <div class="input-group justify-content-between" id="igroup-${param.id}">
                        <div class="form-check form-check-inline">
                            <input type="radio" class="form-check-input" name="radio-${param.id}" id="c-${param.id}" value="0" data-param-id="${param.id}"${"change_parameter"===param.perm? ' checked':''}>
                            <label class="form-check-label" for="c-${param.id}">Change</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input type="radio" class="form-check-input" name="radio-${param.id}" id="v-${param.id}" value="1" data-param-id="${param.id}"${"view_parameter"===param.perm? ' checked':''}>
                            <label class="form-check-label" for="v-${param.id}">View</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input type="radio" class="form-check-input" name="radio-${param.id}" id="n-${param.id}" value="2" data-param-id="${param.id}"${"no_permissions"===param.perm? ' checked':''}>
                            <label class="form-check-label" for="n-${param.id}">No permissions</label>
                        </div>
                    </div>
                </td>
                <td class="align-bottom text-center col-1">${undo_btn}</td>
            </tr>`
            );
        });
    } else {
        $('#upd').append('<tr><td colspan="5"><span>Empty result</span></td></tr>')
    }
}