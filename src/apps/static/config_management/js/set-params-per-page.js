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