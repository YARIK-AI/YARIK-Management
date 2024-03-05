function changeGroupname(event) {
    event.preventDefault();
    const selected = this.options[this.selectedIndex];
    const selected_value = selected.value=="---"? null: selected.value;
    
    function afterResponseSelectGroup(resp) {
        function fn(dict_par_perm, num_pages, page_n) {
            updatePageSelector(num_pages, page_n);
            updateTable(dict_par_perm);
            activate_tooltips();
        };

        const fn_name = 'afterResponseSelectGroup';
        const base_msg = 'Error displaying parameter permissions after selecting a group.';
        const code = 4;
        const arg_names = [RIPN.LIST_EL, RIPN.NUM_PAGES, RIPN.PAGE_N];
        const checks = [cU, cUON, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn(resp[RIPN.LIST_EL], resp[RIPN.NUM_PAGES], resp[RIPN.PAGE_N]);
        
    };

    // ajax
    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: RTYPE.SELECT_GROUP,
            [ROPN.GROUP_ID] : selected_value
        },
        success: afterResponseSelectGroup,
        error: commonHandler
    });
};


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


function savePerms(event) {
    event.preventDefault();

    function afterResponseSavePerms(resp) {
        function fn(msg) {
            $('#modal-close-btn').click();
            $.each($('#upd tr td'), function(i, val) {
                val.classList.remove('bg-warning');
            });
            window.onbeforeunload = null;
            showToastMsg(msg);
        };

        const fn_name = 'afterResponceSavePerms';
        const base_msg = 'Error refreshing page after saving.';
        const code = 6;
        const arg_names = [RIPN.MSG,];
        const checks = [cU,];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
        
    };

    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SAVE
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: afterResponseSavePerms,
        error: commonHandler
    });
};


function searchParams(event){
    event.preventDefault();
    let cur = this;

    function afterResponseSearch(resp) {
        function fn(dict_par_perm, num_pages, page_n) {
            updateTable(dict_par_perm);
            updatePageSelector(num_pages, page_n);
            activate_tooltips();
        }

        const fn_name = 'afterResponceSearch';
        const base_msg = 'Error displaying search results.';
        const code = 4;
        const arg_names = [RIPN.LIST_EL, RIPN.NUM_PAGES, RIPN.PAGE_N];
        const checks = [cU, cUON, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));

        
    };

    const searchText = cur.value;
    let data;

    if(!!searchText.length) { // if not empty
        data = {
            [ROPN.TYPE]: RTYPE.SET_SEARCH,
            [ROPN.SEARCH]: searchText
        }
    }
    else { // if empty
        data = {
            [ROPN.TYPE]: RTYPE.RESET_SEARCH
        }
    }  

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : data,
        success: afterResponseSearch,
        error: commonHandler
    });
};


function selectPage(event){
    event.preventDefault();
    let cur = this;
    let active = cur.parentElement.parentElement.querySelector('.active');
    const previous = Number(active.attributes.id.value);
    const selected = cur.attributes.href.value;
    const сontextualinfinity = 100000

    let page_n;
    switch (selected) {
        case 'previous': page_n = previous - 1; break;
        case 'first': page_n = 1; break;
        case 'next': page_n = previous + 1; break;
        case 'last': page_n = сontextualinfinity; break;
        default: page_n = Number(selected);
    }
    if(page_n < 1) page_n = 1;

    function afterResponseSelectPage(resp) {
        function fn(dict_par_perm, num_pages) {
            if( page_n > num_pages) page_n = num_pages;
            updatePageSelector(num_pages, page_n);
            updateTable(dict_par_perm);
            activate_tooltips();
            $('#upd2')[0].scrollIntoView(true);
        };

        const fn_name = 'afterResponceSelectPage';
        const base_msg = 'Error selecting page.';
        const code = 4;
        const arg_names = [RIPN.LIST_EL, RIPN.NUM_PAGES];
        const checks = [cU, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    if (cur.parentElement.classList.contains('active')) { 
        return; // if clicked on current page
    };

    // ajax
    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: RTYPE.SELECT_PAGE,
            [ROPN.PAGE_N] : page_n
        },
        success: afterResponseSelectPage,
        error: commonHandler
    });
};


function setParamsPerPage(event){
    event.preventDefault();
    let cur = this;
    const params_per_page = cur.value;

    function afterResponseSetPerPage(resp) {
        function fn(dict_par_perm, num_pages, page_n) {
            updateTable(dict_par_perm);
            updatePageSelector(num_pages, page_n);
            activate_tooltips();
        };

        const fn_name = 'afterResponseSetPerPage';
        const base_msg = 'Error displaying parameters after setting a new value for "parameters per page".';
        const code = 8;
        const arg_names = [RIPN.LIST_EL, RIPN.NUM_PAGES, RIPN.PAGE_N];
        const checks = [cU, cUON, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SET_PER_PAGE,
            [ROPN.PER_PAGE]: params_per_page
        },
        success: afterResponseSetPerPage,
        error: commonHandler
    });
};


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

