function setParamsPerPage(event){
    event.preventDefault();
    let cur = this;
    const params_per_page = cur.value;

    function updateBodyData(resp) {
        const fn_name = 'updateBodyData';
        const base_msg = 'Error displaying parameters after setting a new value for "parameters per page".'
        try {
            if (typeof resp.dict_par_perm === 'undefined') {
                throw new MissingFunctionParameterException('dict_par_perm', fn_name, 8);
            } else if(typeof resp.num_pages === 'undefined' || resp.num_pages === null) {
                throw new MissingFunctionParameterException('num_pages', fn_name, 8);
            } else if(typeof resp.page_n === 'undefined' || resp.page_n === null) {
                throw new MissingFunctionParameterException('page_n', fn_name, 8);
            }
            else { // if ok
                updateTable(resp.dict_par_perm);
                updatePageSelector(resp.num_pages, resp.page_n);
                activate_tooltips();
            }
        } catch(e) {
            let msg;
            if (e instanceof MissingFunctionParameterException) {
                msg = `${base_msg} Error code: ${e.code}.`;
                console.log(e.msg);
            }
            else {
                msg = `${base_msg} Unknown error.`;
                console.log(e);
            }
            showToastMsg(msg);
        }
    };

    $.ajax({
        type: "GET",
        url: "/permissions/",
        data : {
            type: RTYPE.SET_PER_PAGE,
            params_per_page: params_per_page
        },
        success: updateBodyData,
        error: commonHandler
    });
};