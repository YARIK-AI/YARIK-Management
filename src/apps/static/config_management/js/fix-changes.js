$('#upd').on('change', '.param-input', function(event){
    event.preventDefault();
    var cur = this;
    var val = cur.value;
    const id = cur.name;


    if(!!cur.attributes.type && cur.attributes.type.value == 'checkbox') {
        val = cur.checked;
    }


    function onSuccess(resp) {
        const old_val = resp.old_val;
        const default_value = resp.default_value;
        const is_valid = resp.is_valid;

        cur.classList.remove('border-warning');
        cur.classList.remove('border-danger');
        
        if(old_val!=String(val)) {
            if(is_valid) {
                cur.classList.add('border-warning');
            }
            else {
                cur.classList.add('border-danger');
            }
        };

        var btn = $(`#upd button.restore-default#${id}`)[0];

        if(String(val)!=default_value) {
            btn.classList.remove('disabled');
        }
        else {
            btn.classList.add('disabled');
        };
        updateStatusList(resp);
    };


    $.ajax({
        type: "POST",
        url: "/configuration/",
        data : {
            type: "change_param",
            param_id: id,
            value: val,
            csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
        },
        success: onSuccess,
        error: function () {}
    });
});