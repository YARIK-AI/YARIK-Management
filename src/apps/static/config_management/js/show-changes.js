function showChanges(event) {
    event.preventDefault();
    const table_template = `
        <table class="table">
            <thead class="table-light">
                <tr>
                    <th>Name</th>
                    <th>Old value</th>
                    <th>New value</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    `

    function insertDataToModal(resp) {
        const fn_name = 'insertDataToModal';
        const base_msg = 'Error displaying changes.'
        try {
            if (typeof resp.type === 'undefined' || resp.type === null) {
                throw new MissingFunctionParameterException('type', fn_name, 5);
            } else if(typeof resp.changes === 'undefined') {
                throw new MissingFunctionParameterException('changes', fn_name, 5);
            }
            else { // if ok
                let modal_body = $('#changes-modal-list .modal-body');
                let modal_title = $('#changes-modal-list .modal-header .modal-title');
                let save_btn = $('#changes-modal-list #save-changes-btn');

                modal_body.html(''); // clear modal
                save_btn.addClass('disabled'); // disable btn

                let class_color = '';

                switch(resp.type) {
                    case "no_changes":{
                        modal_title.html("No changes to save!");
                        modal_body.append('<span>No changes</span>');
                        return;
                    }
                    case "errors":{
                        modal_title.html("Correct these errors before saving!");
                        modal_body.append(table_template);
                        class_color = 'class="table-danger"';
                        break;
                    }
                    case "ok":{
                        modal_title.html("Save changes?");
                        modal_body.append(table_template);
                        save_btn.removeClass('disabled') // enable btn
                        break;
                    }
                }

                $.each(resp.changes, function(i, val) {
                    modal_body.find("tbody").append(
                        `<tr>
                            <td>${val.name}</td>
                            <td>${val.old_value}</td>
                            <td ${class_color}>${val.new_value}</td>
                        </tr>`
                    );
                });
            }
        } catch(e) {
            let msg;
            if (e instanceof MissingFunctionParameterException) {
                msg = `${base_msg} Error code: ${e.code}.`;
                console.log(e.msg);
            }
            else {
                msg = `${base_msg} Unknown error.`;
                console.log(e);
            }
            showToastMsg(msg);
        }
    };

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : {
            type: "show_changes"
        },
        success: insertDataToModal,
        error: commonHandler
    });
};