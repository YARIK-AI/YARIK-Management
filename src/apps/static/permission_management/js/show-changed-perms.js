function showPermChanges(event) {
    event.preventDefault();
    const table_template = `
        <table class="table">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Old permission</th>
                    <th>New permission</th>
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
                document.getElementById('commit-msg').classList.add('d-none');
                let modal_body = $('#changes-modal-list .modal-body');
                let modal_title = $('#changes-modal-list .modal-header .modal-title');
                let save_btn = $('#changes-modal-list #save-changes-btn');

                modal_body.html(''); // clear modal
                save_btn.addClass('disabled'); // disable btn

                let class_color = '';

                switch(resp.type) {
                    case "no_changes":{
                        modal_title.html("No changes to apply!");
                        modal_body.append('<span>No changes</span>');
                        return;
                    }
                    case "ok":{
                        modal_title.html("Apply changes?");
                        modal_body.append(table_template);
                        save_btn.removeClass('disabled') // enable btn
                        break;
                    }
                }
                
                for ( const [user_id, user] of Object.entries(resp.changes)) {
                    modal_body.find("tbody").append(
                        `<tr class="table-info">
                            <td colspan="4">${user.username}</td>
                        </tr>`
                    );
                    for (const [param_id, single_change] of Object.entries(user.changes)) {
                        modal_body.find("tbody").append(
                            `<tr>
                                <td>${param_id}</td>
                                <td>${single_change.name}</td>
                                <td>${perm_name[single_change.old_value]}</td>
                                <td ${class_color}>${perm_name[single_change.new_value]}</td>
                            </tr>`
                        );

                    }

                }
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
        url: "/permissions/",
        data : {
            type: RTYPE.SHOW_CHANGES
        },
        success: insertDataToModal,
        error: commonHandler
    });
};