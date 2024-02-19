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