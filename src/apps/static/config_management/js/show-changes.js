$('#show-modal-btn').on('click', function(event){
    event.preventDefault();


   function onSuccess(resp) {
        $('#changes-modal-list .modal-body').html('');

        switch(resp.type) {
            case "no_changes":{
                $('#changes-modal-list .modal-header .modal-title').html("No changes to save!");
                $('#changes-modal-list #save-changes-btn').addClass('disabled');
                $('#changes-modal-list .modal-body').append('<span>No changes</span>');
                return;
            }
            case "errors":{
                $('#changes-modal-list #save-changes-btn').addClass('disabled')
                $('#changes-modal-list .modal-header .modal-title').html("Correct these errors before saving!");
                $('#changes-modal-list .modal-body').append('<table class="table">' +
                    '<thead class="table-light">' +
                    '<tr><th>Name</th>' +
                    '<th>Old value</th>' +
                    '<th>New value</th>' +
                    '</thead>' +
                    '<tbody>' +
                    '</tbody>' +
                    '</table>'
                );
                $.each(resp.changes, function(i, val) {
                    $('#changes-modal-list .modal-body tbody').append(
                        '<tr><td>' + val.name + '</td>' +
                        '<td>' + val.old_value + '</td>' +
                        '<td class="table-danger">' + val.new_value + '</td></tr>'
                    );
                });
                break;
            }
            case "ok":{
                $('#changes-modal-list .modal-header .modal-title').html("Save changes?");
                $('#changes-modal-list #save-changes-btn').removeClass('disabled')
                $('#changes-modal-list .modal-body').append('<table class="table">' +
                    '<thead class="table-light">' +
                    '<tr><th>Name</th>' +
                    '<th>Old value</th>' +
                    '<th>New value</th>' +
                    '</thead>' +
                    '<tbody>' +
                    '</tbody>' +
                    '</table>'
                );
                $.each(resp.changes, function(i, val) {
                    $('#changes-modal-list .modal-body tbody').append(
                        '<tr><td>' + val.name + '</td>' +
                        '<td>' + val.old_value + '</td>' +
                        '<td>' + val.new_value + '</td></tr>' 
                    );
                });
                break;
            }
        }
    };

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : {
            type: "show_changes",
            csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
        },
        success: onSuccess,
        error: function () {}
    });
});