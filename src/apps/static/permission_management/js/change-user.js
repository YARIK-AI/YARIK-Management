function changeUsername(event){
    event.preventDefault();
    const selected = this.options[this.selectedIndex];
    const selected_value = selected.value=="---"? null: selected.value;
    
    function Success(resp) {
        updatePageSelector(resp.num_pages, page_n);
        updateTable(resp.dict_par_perm);
        activate_tooltips();
    };

    // ajax
    $.ajax({
        type: "GET",
        url: "/permissions/",
        data : {  
            type: RTYPE.SELECT_USER,
            user_id : selected_value
        },
        success: Success,
        error: function(){}
    });
};