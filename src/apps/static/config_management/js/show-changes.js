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
    `;

    function afterResponseShowChanges(resp) {
        function fn(type, changes) {
            let modal_body = $('#changes-modal-list .modal-body');
                let modal_title = $('#changes-modal-list .modal-header .modal-title');
                let save_btn = $('#changes-modal-list #save-changes-btn');

                modal_body.html(''); // clear modal
                save_btn.addClass('disabled'); // disable btn

                let class_color = '';

                switch(type) {
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

                $.each(changes, function(i, val) {
                    modal_body.find("tbody").append(
                        `<tr>
                            <td>${val.name}</td>
                            <td>${val.old_value}</td>
                            <td ${class_color}>${val.new_value}</td>
                        </tr>`
                    );
                });
        };

        const fn_name = 'afterResponseShowChanges';
        const base_msg = 'Error displaying changes.';
        const code = 5;
        const arg_names = [RIPN.TYPE, RIPN.CHANGES];
        const checks = [cUON, cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SHOW_CHANGES
        },
        success: afterResponseShowChanges,
        error: commonHandler
    });
};