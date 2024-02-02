function showFilter(event, filter_id_extra){
    const filter_id = typeof filter_id_extra === 'undefined' || filter_id_extra === null ? this.id: filter_id_extra; 
    function updateFilter(resp) {
        const fn_name = 'updateFilter';
        const base_msg = 'Filter display error.'
        try {
            if (typeof resp.filter_items === 'undefined' || resp.filter_items === null) {
                throw new MissingFunctionParameterException('filter_items', fn_name, 2);
            } else if(typeof resp.selected_item === 'undefined') {
                throw new MissingFunctionParameterException('selected_item', fn_name, 2);
            } 
            else { // if ok
                if(filter_id === 'collapseListScope') {
                    updateFilterList( resp.filter_items, resp.selected_item, filter_id);
                } else if(filter_id === 'collapseListStatus') {
                    updateFilterList( resp.filter_items, resp.selected_item, filter_id);
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
            showToastMsg(msg);
        }
    };

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : {
            type: "show_filter_list",
            filter_id: filter_id
        },
        success: updateFilter,
        error: commonHandler
    });
}

