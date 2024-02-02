function selectPage(event){
    event.preventDefault();
    const page_n = $(this).attr('href');
    const elem = $(`ul.pagination#upd2 li#${page_n}.page-item`)[0];

    function updateDataArea(resp) {
        const fn_name = 'updateDataArea';
        const base_msg = 'Error selecting page.'
        try {
            if (typeof resp.results === 'undefined') {
                throw new MissingFunctionParameterException('results', fn_name, 3);
            } else if(typeof resp.changes === 'undefined') {
                throw new MissingFunctionParameterException('changes', fn_name, 3);
            }
            else { // if ok
                updateTable(resp.results, resp.changes);
                let active = $('ul.pagination#upd2 li.page-item.active')[0];
                let selected = $(`ul.pagination#upd2 li#${page_n}.page-item`)[0];
                active.classList.remove('active');
                selected.classList.add('active');
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

    if (elem.classList.contains('active')) { 
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