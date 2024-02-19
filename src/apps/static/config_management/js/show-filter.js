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

