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

    function afterResponseShowPerms(resp) {
        function fn(type, changes) {
            document.getElementById('commit-msg').classList.add('d-none');
            let modal_body = $('#changes-modal-list .modal-body');
            let modal_title = $('#changes-modal-list .modal-header .modal-title');
            let save_btn = $('#changes-modal-list #save-changes-btn');

            modal_body.html(''); // clear modal
            save_btn.addClass('disabled'); // disable btn

            let class_color = '';

            switch(type) {
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
            
            for ( const [group_id, group] of Object.entries(changes)) {
                modal_body.find("tbody").append(
                    `<tr class="table-info">
                        <td colspan="4">${group.name}</td>
                    </tr>`
                );
                for (const [param_id, single_change] of Object.entries(group.changes)) {
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
        };

        const fn_name = 'afterResponseShowPerms';
        const base_msg = 'Error displaying changes.';
        const code = 5;
        const arg_names = [RIPN.TYPE, RIPN.CHANGES];
        const checks = [cUON, cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn(resp[RIPN.TYPE], resp[RIPN.CHANGES]);
    };

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SHOW_CHANGES
        },
        success: afterResponseShowPerms,
        error: commonHandler
    });
};