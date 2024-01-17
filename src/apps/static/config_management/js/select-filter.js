$('.scopeList').on('click', function(event){
    event.preventDefault();
    var arr = $('.scopeList');
    var cur = this;

    function onSuccess(resp) {
        updateTable(resp);
        updatePageSelector(resp.num_pages, resp.page_n);
        activate_tooltips();
      };

    if(cur.ariaCurrent == "true") { // deactivation
        cur.classList.remove('active')
        cur.ariaCurrent = null;

        $.ajax({
            type: "POST",
            url: "/configuration/",
            data : {
                type: "reset_scope",
                csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
            },
            success: onSuccess,
            error: function () {}
        });
    }
    else { // activation
        for(var i = 0; i < arr.length; i++) {
        arr[i].classList.remove('active')
        arr[i].ariaCurrent = null;
        }
        
        cur.classList.add('active')
        cur.ariaCurrent = "true";

        // ajax
        $.ajax({
            type: "POST",
            url: "/configuration/",
            data : {
                type: "set_scope",
                component_id: $(this).attr('href'),
                csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
            },
            success: onSuccess,
            error: function () {}
        });
    } 
});