function commonHandler(event){
    //event.preventDefault();
    var cur = this;
    
    function onSuccess(resp) {
        updateTable(resp);
        updatePageSelector(resp.num_pages, resp.page_n);
        activate_tooltips();
    };

    const searchText = cur.value;

    if(!!searchText.length) { // if not empty
        $.ajax({
            type: "GET",
            url: "/configuration/",
            data : {
                type: "text_search",
                search_str: searchText,
                csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
            },
            success: onSuccess,
            error: function () {}
        });
    }
    else { // if empty
        // ajax
        $.ajax({
            type: "GET",
            url: "/configuration/",
            data : {
                type: "reset_text_search",
                csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
            },
            success: onSuccess,
            error: function () {}
        });
    } 
};

$('#search-field').on('propertychange input', 'input.form-control.rounded', commonHandler);