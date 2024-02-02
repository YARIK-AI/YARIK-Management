function fixChange(event) {
    const action_mapping = {
        ".param-input": "change",
        ".restore-default": "default"
    };

    //event.handleObj.selector
    event.preventDefault();
    const is_input_changed = action_mapping[event.handleObj.selector] === 'change';
    const is_btn_clicked = !is_input_changed;

    let input;
    let btn;
    let val;
    let param_id;

    if(is_input_changed) { // if value in input changes
        input = this;
        val = input.value;
        param_id = input.name;
        btn = $(`#upd button.restore-default#${param_id}`)[0];
        if(typeof input.attributes.type !== 'undefined' && input.attributes.type.value == 'checkbox') {
            val = input.checked;
        }
    } else if(is_btn_clicked) { // if restore default value button clicked
        btn = $(this);
        param_id = btn.attr('href');
        input = $(`#upd input.param-input[name='${param_id}']`)[0];
    }

    function updateElements(resp) {
        const fn_name = 'updateElements';
        const base_msg = 'Error refreshing page after making changes.'
        try {
            if (typeof resp.old_val === 'undefined' || resp.old_val === null) {
                throw new MissingFunctionParameterException('old_val', fn_name, 4);
            } else if(typeof resp.default_value === 'undefined' || resp.default_value === null) {
                throw new MissingFunctionParameterException('default_value', fn_name, 4);
            } else if(typeof resp.is_valid === 'undefined' || resp.is_valid === null) {
                throw new MissingFunctionParameterException('is_valid', fn_name, 4);
            } else if(typeof resp.status_dict === 'undefined' || resp.status_dict === null) {
                throw new MissingFunctionParameterException('status_dict', fn_name, 4);
            }
            else { // if ok
                const old_val = resp.old_val;
                const default_value = resp.default_value;
                const is_valid = resp.is_valid;

                if(is_btn_clicked) { // if restore default value button clicked
                    val = default_value;
                }

                input.classList.remove('border-warning');
                input.classList.remove('border-danger');         
                
                if(old_val!=String(val)) { // setting the border color of a input
                    if(is_valid) {
                        input.classList.add('border-warning');
                    } else {
                        input.classList.add('border-danger');
                    }
                };

                if(is_input_changed) { // if value in input changes
                    if(String(val)!=default_value) { // enable button if value is not default
                        btn.classList.remove('disabled');
                    } else {
                        btn.classList.add('disabled');
                    }
                } else if(is_btn_clicked) { // if restore default value button clicked
                    if(typeof input.attributes.type !== 'undefined' && input.attributes.type.value == 'checkbox') {
                        input.checked = default_value=="true" ? true : false;
                    } else {
                        input.value = default_value;
                    }
                    btn.addClass('disabled');
                }

                updateFilterList(resp.status_dict, null, 'collapseListStatus');
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
        type: "POST",
        url: "/configuration/",
        data : {
            type: "change_param",
            param_id: param_id,
            value: val
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: updateElements,
        error: commonHandler
    });
};

