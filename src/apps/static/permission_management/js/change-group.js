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