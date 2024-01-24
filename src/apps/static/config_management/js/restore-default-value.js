$('#upd').on('click', '.restore-default', function(event){
    event.preventDefault();
    var btn = $(this);
    var param_id = btn.attr('href');

    var input = $(`#upd input.param-input[name='${param_id}']`)[0];
    var val = input.value;

    if(!!input.attributes.type && input.attributes.type.value == 'checkbox') {
        val = input.checked;
    }

    function onSuccess(resp) {
        const old_val = resp.old_val;
        const is_valid = resp.is_valid;
        const default_value = resp.default_value;

        input.classList.remove('border-warning');
        input.classList.remove('border-danger');
        
        if(old_val!=default_value) {
            if(is_valid) {
                input.classList.add('border-warning');
            }
            else {
                input.classList.add('border-danger');
            }
        };

        input.value = default_value;

        btn.addClass('disabled');

        updateStatusList(resp);
    };

    $.ajax({
        type: "POST",
        url: "/configuration/",
        data : {
            type: "restore_default",
            param_id: param_id,
            csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
        },
        success: onSuccess,
        error: function () {}
    });
});