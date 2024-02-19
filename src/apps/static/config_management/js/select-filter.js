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