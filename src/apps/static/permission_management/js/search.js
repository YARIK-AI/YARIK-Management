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