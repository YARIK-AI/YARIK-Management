function selectFilter(event){
    const filter_mapping = {
        ".scopeList": "scope",
        ".statusList": "status"
    };

    event.preventDefault();
    let arr = $(event.handleObj.selector);
    let cur = this;

    function updateBody(resp) {
        const fn_name = 'updateBody';
        const base_msg = 'Error applying filter.'
        try {
            if (typeof resp.results === 'undefined') {
                throw new MissingFunctionParameterException('results', fn_name, 1);
            } else if(typeof resp.changes === 'undefined') {
                throw new MissingFunctionParameterException('changes', fn_name, 1);
            } else if(typeof resp.num_pages === 'undefined' || resp.num_pages === null) {
                throw new MissingFunctionParameterException('num_pages', fn_name, 1);
            } else if(typeof resp.page_n === 'undefined' || resp.page_n === null) {
                throw new MissingFunctionParameterException('page_n', fn_name, 1);
            }
            else { // if ok
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
                updateTable(resp.results, resp.changes);
                updatePageSelector(resp.num_pages, resp.page_n);
                activate_tooltips();

                if(event.handleObj.selector === '.statusList') {
                    showFilter(null, 'collapseListScope');
                } else if(event.handleObj.selector === '.scopeList') {
                    showFilter(null, 'collapseListStatus');
                }
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
            cur.classList.remove('active');
            cur.ariaCurrent = null;
            showToastMsg(msg);
        }
    };

    const data = {
        type: `${cur.ariaCurrent == "true"? "reset": "set"}_${filter_mapping[event.handleObj.selector]}`,
        filter_name: `filter_${filter_mapping[event.handleObj.selector]}`,
        filter_value: cur.ariaCurrent == "true"? null: $(this).attr('href')
    };

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : data,
        success: updateBody,
        error: commonHandler
    });
};