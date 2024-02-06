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

    function updateDataArea(resp) {
        const fn_name = 'updateDataArea';
        const base_msg = 'Error selecting page.'
        try {
            if (typeof resp.results === 'undefined') {
                throw new MissingFunctionParameterException('results', fn_name, 3);
            } else if(typeof resp.changes === 'undefined') {
                throw new MissingFunctionParameterException('changes', fn_name, 3);
            } else if(typeof resp.num_pages === 'undefined' || resp.num_pages === null) {
                throw new MissingFunctionParameterException('num_pages', fn_name, 3);
            } 
            else { // if ok
                if( page_n > resp.num_pages) page_n = resp.num_pages;
                updatePageSelector(resp.num_pages, page_n);
                updateTable(resp.results, resp.changes);
                activate_tooltips();
                $('#upd2')[0].scrollIntoView(true);
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

    if (cur.parentElement.classList.contains('active')) { 
        return; // if clicked on current page
    };

    // ajax
    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : {  
            type: "page_select",
            page_n : page_n
        },
        success: updateDataArea,
        error: commonHandler
    });
};