$('#collapseListStatus').on('show.coreui.collapse', function(event){
    function onSuccess(resp) {
        updateStatusList(resp);
    };

    $.ajax({
        type: "GET",
        url: "/configuration/",
        data : {
            type: "show_status",
            csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
        },
        success: onSuccess,
        error: function () {}
    });
});