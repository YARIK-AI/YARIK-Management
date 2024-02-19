function changePermission(event) {
    event.preventDefault();

    const action_mapping = {
        "tr td div div input.form-check-input": "change",
        "tr td div div button.undo": "undo"
    };

    const is_input_changed = action_mapping[event.handleObj.selector] === 'change';
    const is_btn_clicked = !is_input_changed;
    const select = document.getElementById('select-group');
    const selected_group_id = select.options[select.selectedIndex].value;

    let selected, btn, selected_param_id, perm_id;

    if(is_input_changed) { // if value in input changes
        selected = this;
        selected_param_id = selected.dataset.paramId;
        perm_id = selected.value;
        btn = $(`button#${selected_param_id}.undo`)[0];


    } else if(is_btn_clicked) { // if restore default value button clicked
        btn = this;
        selected_param_id = btn.id;
        selected = $(`input.form-check-input[name="radio-${selected_param_id}"]`);
        coreui.Tooltip.getInstance(btn).hide();
    }

    
    function afterResponseChangePerm(resp) {
        function fn(old_perm_name, changes) {
            const old_perm_id = perm_code[old_perm_name];

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
            
            if(Object.keys(changes).length !== 0) {
                window.onbeforeunload = ()=>{return "";};
            } else {
                window.onbeforeunload = null;
            }
        };

        const fn_name = 'afterResponceChangePerm';
        const base_msg = 'Error refreshing page after making changes.';
        const code = 7;
        const arg_names = [RIPN.PREV_VAL, RIPN.CHANGES];
        const checks = [cUON, cU];
        
        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn(resp[RIPN.PREV_VAL], resp[RIPN.CHANGES]);
    };

    // ajax
    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: RTYPE.CHANGE,
            [ROPN.GROUP_ID] : selected_group_id,
            [ROPN.PARAM_ID]: selected_param_id,
            [ROPN.PERM_ID]: perm_id
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: afterResponseChangePerm,
        error: commonHandler
    });
};