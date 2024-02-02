function searchParams(event){
    event.preventDefault();
    let cur = this;

    function updateBodyData(resp) {
        const fn_name = 'updateBodyData';
        const base_msg = 'Error displaying search results.'
        try {
            if (typeof resp.results === 'undefined') {
                throw new MissingFunctionParameterException('results', fn_name, 7);
            } else if(typeof resp.changes === 'undefined') {
                throw new MissingFunctionParameterException('changes', fn_name, 7);
            } else if(typeof resp.num_pages === 'undefined' || resp.num_pages === null) {
                throw new MissingFunctionParameterException('num_pages', fn_name, 7);
            } else if(typeof resp.page_n === 'undefined' || resp.page_n === null) {
                throw new MissingFunctionParameterException('page_n', fn_name, 7);
            }
            else { // if ok
                updateTable(resp.results, resp.changes);
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

    const searchText = cur.value;
    let data;

    if(!!searchText.length) { // if not empty
        data = {
            type: "text_search",
            search_str: searchText
        }
    }
    else { // if empty
        data = {
            type: "reset_text_search"
        }
    }  

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : data,
        success: updateBodyData,
        error: commonHandler
    });
};