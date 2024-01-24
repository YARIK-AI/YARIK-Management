$('#save-changes-btn').on('click', function(event){
    event.preventDefault();
    var cur = this;

    //$('#modal-close-btn').click()
    function onSuccess2(resp) { 
        $('#modal-close-btn').click();
        $('#result-message-toast .toast-body').html(resp.msg);

        $.each($('#upd tr td .param-input'), function(i, val) {
            val.classList.remove('border-warning');
            val.classList.remove('border-danger');
        });

        updateStatusList(resp);

        $('#confirmSaveModal .modal-footer input#commit-msg')[0].value = '';

        const toast = document.getElementById('result-message-toast');
        const toastCoreUI = coreui.Toast.getOrCreateInstance(toast);
        toastCoreUI.show();
    };

    function onSuccess1(resp) {
        if(resp.is_good) {
            $.ajax({
                type: "POST",
                url: "/configuration/",
                data : {
                    type: "save_changes",
                    commit_msg: $('#confirmSaveModal .modal-footer input#commit-msg')[0].value,
                    csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
                },
                success: onSuccess2,
                error: function () {}
            });
        }
        else {
            $('#changes-modal-list #save-changes-btn').addClass('disabled');
        }
    };

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : {
            type: "check_for_errors",
            csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
        },
        success: onSuccess1,
        error: function () {}
    });
});