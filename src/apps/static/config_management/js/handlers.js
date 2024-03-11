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


function saveChanges(event) {
    event.preventDefault();

    function afterResponseSaveChanges(resp) {
        function fn(status_dict, msg) {
            $('#sync-btn svg use')[0].href.baseVal = "/static/assets/icons/configuration-icons.svg#warn";
            $('#sync-btn')[0].href = '/sync/';
            $('#modal-close-btn').click();
            $.each($('#upd tr td .param-input'), function(i, val) {
                val.classList.remove('border-warning');
                val.classList.remove('border-danger');
            });
            updateFilterList(status_dict, null, 'collapseListStatus');
            $('#confirmSaveModal .modal-footer input#commit-msg')[0].value = '';
            window.onbeforeunload = null;
            showToastMsg(msg);
        };

        const fn_name = 'afterResponseSaveChanges';
        const base_msg = 'Error refreshing page after saving.';
        const code = 4;
        const arg_names = [RIPN.STATUS_FILTER, RIPN.MSG];
        const checks = [cU, cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));

    };

    const commit_msg = $('#confirmSaveModal .modal-footer input#commit-msg')[0].value;

    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SAVE,
            [ROPN.COMMIT_MSG]: commit_msg
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: afterResponseSaveChanges,
        error: commonHandler
    });
};


function searchParams(event){
    event.preventDefault();
    let cur = this;

    function afterResponseSearch(resp) {
        function fn(results, changes, num_pages, page_n) {
            updateTable(results, changes);
            updatePageSelector(num_pages, page_n);
            activate_tooltips();
        };

        const fn_name = 'afterResponseSearch';
        const base_msg = 'Error displaying search results.';
        const code = 7;
        const arg_names = [RIPN.LIST_EL, RIPN.CHANGES, RIPN.NUM_PAGES, RIPN.PAGE_N];
        const checks = [cU, cU, cUON, cUON];

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


function selectFilter(event){
    event.preventDefault();
    let arr = $(event.handleObj.selector);
    let cur = this;

    function afterResponseSelectFilter(resp) {
        function fn(results, changes, num_pages, page_n) {
            if(cur.ariaCurrent == "true") {
                cur.classList.remove('active');
                cur.ariaCurrent = null;
            }
            else {
                for(var i = 0; i < arr.length; i++) {
                    arr[i].classList.remove('active')
                    arr[i].ariaCurrent = null;
                }
        
                cur.classList.add('active')
                cur.ariaCurrent = "true";
            }
            updateTable(results, changes);
            updatePageSelector(num_pages, page_n);
            activate_tooltips();

            const cur_filter = class_filter_mapping[event.handleObj.selector];
            
            if(cur_filter === FILTERS.STATUS) {
                showFilter(null, FILTERS.SCOPE);
            } else if(cur_filter === FILTERS.SCOPE) {
                showFilter(null, FILTERS.STATUS);
            }
        };

        function err() {
            cur.classList.remove('active');
            cur.ariaCurrent = null;
        };

        const fn_name = 'afterResponseSelectFilter';
        const base_msg = 'Error applying filter.';
        const code = 1;
        const arg_names = [RIPN.LIST_EL, RIPN.CHANGES, RIPN.NUM_PAGES, RIPN.PAGE_N];
        const checks = [cU, cU, cUON, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]), err);
    };

    const filter_id = class_filter_mapping[event.handleObj.selector];
    let filter_val = null;
    let req_type;

    switch(filter_id) {
        case FILTERS.SCOPE: {
            if(cur.ariaCurrent != "true") {
                req_type = RTYPE.SET_SCOPE;
                filter_val = $(this).attr('href');
            }
            else {
                req_type = RTYPE.RESET_SCOPE;
            }
            break;
        }
        case FILTERS.STATUS: {
            if(cur.ariaCurrent != "true") {
                req_type = RTYPE.SET_STATUS;
                filter_val = $(this).attr('href');
            }
            else {
                req_type = RTYPE.RESET_STATUS;
            }
            break;
        }
    }

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: req_type,
            [ROPN.FILTER_ID]: filter_id,
            [ROPN.FILTER_VALUE]: filter_val,
        },
        success: afterResponseSelectFilter,
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
        function fn(results, changes, num_pages) {
            if( page_n > num_pages) page_n = num_pages;
            updatePageSelector(num_pages, page_n);
            updateTable(results, changes);
            activate_tooltips();
            $('#upd2')[0].scrollIntoView(true);
        };

        const fn_name = 'afterResponseSelectPage';
        const base_msg = 'Error selecting page.';
        const code = 2;
        const arg_names = [RIPN.LIST_EL, RIPN.CHANGES, RIPN.NUM_PAGES];
        const checks = [cU, cU, cUON];

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
        function fn(results, changes, num_pages, page_n) {
            updateTable(results, changes);
            updatePageSelector(num_pages, page_n);
            activate_tooltips();
        };

        const fn_name = 'afterResponseSelectPage';
        const base_msg = 'Error displaying parameters after setting a new value for "parameters per page".';
        const code = 8;
        const arg_names = [RIPN.LIST_EL, RIPN.CHANGES, RIPN.NUM_PAGES, RIPN.PAGE_N];
        const checks = [cU, cU, cUON, cUON];

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


function showFilter(event, filter_id_extra) {
    let filter_id;
    if(typeof filter_id_extra === 'undefined' || filter_id_extra === null) 
        filter_id = this.id;
    else
        filter_id = filter_id_mapping[filter_id_extra];
    
    function afterResponseShowFilter(resp) {
        function fn(filter_items, selected_item) {
            updateFilterList( filter_items, selected_item, filter_id);
        }

        const fn_name = 'afterResponseShowFilter';
        const base_msg = 'Filter display error.';
        const code = 2;
        const arg_names = [RIPN.FILTER_ITEMS, RIPN.SELECTED_ITEM];
        const checks = [cUON, cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SHOW_FILTER,
            [ROPN.FILTER_ID]: id_filter_mapping[filter_id]
        },
        success: afterResponseShowFilter,
        error: commonHandler
    });
}


function updSyncState(event) {   
    function afterUpdSyncState(resp) {
        function fn(state, cnt) {
            let btn = document.getElementById('sync-btn');
            if(state) {
                btn.innerHTML = `
                <div class="spinner-border text-warning" aria-hidden="true" id="in-progress-spinner"></div>
                `;
                btn.href = "/tasks/";
                btn.title = "Synchronization process in progress";
            } else {
                const icon_id = cnt > 0? "warn": "ok";
                btn.innerHTML = `
                <svg class="icon icon-xxl" aria-hidden="true">
                <use href="/static/assets/icons/configuration-icons.svg#${icon_id}"></use>
                </svg>`;
                
                switch(cnt) {
                    case 0: {
                        btn.title = "All resources are synchronized";
                        break;
                    }
                    case 1: {
                        btn.title = `${cnt} resource requires synchronization`;
                        break;
                    }
                    default: {
                        btn.title = `${cnt} resources require synchronization`;
                    }
                }

                if(cnt > 0) {
                    btn.href = "/sync/";
                }
                else {
                    btn.href = "/tasks/";
                }
            }
            refresh_tooltip('sync-btn');
        }
        
        const fn_name = 'afterUpdSyncState';
        const base_msg = 'Error display sync state.';
        const code = 2;
        const arg_names = [RIPN.SYNC_STATE, RIPN.NOT_SYNC_CNT];
        const checks = [cUON, cUON];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
    };

    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.UPD_SYNC_STATE,
        },
        success: afterUpdSyncState,
        error: commonHandler
    });
}

