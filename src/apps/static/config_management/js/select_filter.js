$('.scopeList').on('click', function(event){
    event.preventDefault();
    var arr = $('.scopeList');
    var cur = this;

    function activate_tooltips () {
        const tooltipTriggerList = document.querySelectorAll('[data-coreui-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new coreui.Tooltip(tooltipTriggerEl));
    };

    function updatePageSelector(num_pages, page_n) {
        $('#upd2').html('');
        for(var i = 1; i <= num_pages; i++) {
            $('#upd2').append(
                '<li class="page-item ' + (i==page_n?'active':'') + '" id="' + i  + '">' +
                '<button type="button" class="page-link" href="' + i + '">' + i + '</button>' +
                '</li>'
            );
        }
    };

    function updateTable(resp) {
        $('#upd').html('');
        $.each(resp.results, function(i, val) {
            $('#upd').append(
            '<tr>' +
                '<td>' + val.name + '</td>' +
                '<td>' +
                (val.input_type=='checkbox'? 
                '<input type="' + val.input_type + '" value="true" name="' +  val.id  + (val.value=='true'? '" checked="1"/>': '/>'): 
                    '<input class="form-control" type="' + val.input_type + '" value="' + val.value.replaceAll('"', '&quot;') + '" name="' +  val.id  + '"/>') +
                '</td>' +
                '<td>' + 
                '<span class="d-inline-block" tabindex="0" data-coreui-toggle="tooltip" title="' + val.description + '">' +
                    '<button class="btn btn-secondary" type="button" disabled>?</button>' + 
                '</span>' + 
                '</td>' +
            '</tr>'
            );
        });
        updatePageSelector(resp.num_pages, resp.page_n)
        activate_tooltips();
    }

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
            success: updateTable,
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
            success: updateTable,
            error: function () {}
        });
    } 
});