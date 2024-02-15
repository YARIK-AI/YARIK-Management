function changePermission(event){
    const action_mapping = {
        "tr td div div input.form-check-input": "change",
        "tr td div div button.undo": "undo"
    };
    event.preventDefault();

    const is_input_changed = action_mapping[event.handleObj.selector] === 'change';
    const is_btn_clicked = !is_input_changed;
    const select = document.getElementById('select-user');
    const selected_user_id = select.options[select.selectedIndex].value;

    let selected;
    let btn;
    let selected_param_id;
    let perm_id;



    if(is_input_changed) { // if value in input changes
        selected = this;
        selected_param_id = selected.id;
        perm_id = selected.value;
        btn = $(`button#${selected_param_id}.undo`)[0];


    } else if(is_btn_clicked) { // if restore default value button clicked
        btn = this;
        selected_param_id = btn.id;
        selected = $(`input.form-check-input[name="radio-${selected_param_id}"]`);
        coreui.Tooltip.getInstance(btn).hide();
    }

    
    function updateElements(resp) {
        const fn_name = 'updateElements';
        const base_msg = 'Error refreshing page after making changes.'
        try {
            if (typeof resp.old_perm_name === 'undefined' || resp.old_perm_name === null) {
                throw new MissingFunctionParameterException('old_perm_name', fn_name, 4);
            } else if (typeof resp.changes === 'undefined') {
                throw new MissingFunctionParameterException('changes', fn_name, 4);
            } else { // if ok
                const old_perm_id = perm_code[resp.old_perm_name];

                if(is_btn_clicked) {
                    perm_id = old_perm_id;
                    $.each(selected, function(i, radio) {
                        radio.checked = false;
                        if(radio.value == perm_id) radio.checked = true;
                    });
                    selected[0].parentElement.parentElement.parentElement.classList.remove('bg-warning');
                }
                else {
                    selected.parentElement.parentElement.parentElement.classList.remove('bg-warning');
                }
                
                if(old_perm_id!=perm_id) { // setting the border color of a input
                    selected.parentElement.parentElement.parentElement.classList.add('bg-warning');
                    btn.classList.remove('disabled');
                } else {
                    btn.classList.add('disabled');
                }
                
                if(Object.keys(resp.changes).length !== 0) {
                    window.onbeforeunload = ()=>{return "";};
                } else {
                    window.onbeforeunload = null;
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

    // ajax
    $.ajax({
        type: "POST",
        url: "/permissions/",
        data : {  
            type: RTYPE.CHANGE,
            user_id : selected_user_id,
            param_id: selected_param_id,
            perm_id: perm_id
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: updateElements,
        error: commonHandler
    });
};