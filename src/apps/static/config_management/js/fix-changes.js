function fixChange(event) {
    event.preventDefault();

    const action_mapping = {
        ".param-input": "change",
        ".restore-default": "default"
    };
    const is_input_changed = action_mapping[event.handleObj.selector] === 'change';
    const is_btn_clicked = !is_input_changed;

    let input, btn, val, param_id;

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
        coreui.Tooltip.getInstance(btn).hide();
    }

    function afterResponseChangeParam(resp) {
        function fn(
            old_val, default_value, is_valid, status_dict,
            filter_status, results, num_pages, page_n, changes
        ) {
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

            let new_status = null;
            if(filter_status !== null) {
                if(!status_dict[filter_status].cnt) {
                    $(`#collapseListStatus button#${filter_status}`).click();
                } else {  
                    new_status = filter_status;
                }
                updateTable(results, changes);
                updatePageSelector(num_pages, page_n);
                activate_tooltips();
            } 
            
            updateFilterList(status_dict, new_status, 'collapseListStatus');

            if(Object.keys(changes).length !== 0) {
                window.onbeforeunload = ()=>{return "";};
            } else {
                window.onbeforeunload = null;
            }
        };

        const fn_name = 'afterResponseChangeParam';
        const base_msg = 'Error refreshing page after making changes.';
        const code = 4;
        const arg_names = [
            RIPN.PREV_VAL, RIPN.DEFAULT_VAL, RIPN.IS_VALID, RIPN.STATUS_FILTER,
            RIPN.STATUS, RIPN.LIST_EL, RIPN.NUM_PAGES, RIPN.PAGE_N, RIPN.CHANGES
        ];
        const checks = [cUON, cUON, cUON, cUON, cU, cU, cU, cU, cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.CHANGE,
            [ROPN.PARAM_ID]: param_id,
            [ROPN.VALUE]: val
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: afterResponseChangeParam,
        error: commonHandler
    });
};

