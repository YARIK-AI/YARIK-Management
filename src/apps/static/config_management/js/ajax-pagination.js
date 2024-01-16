$('#upd2').on('click', '.page-link', function(event){
    event.preventDefault();
    var page_n = $(this).attr('href');
  
    function activate_tooltips () {
      const tooltipTriggerList = document.querySelectorAll('[data-coreui-toggle="tooltip"]');
      const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new coreui.Tooltip(tooltipTriggerEl));
    };
  
    if ($('.pagination li#'+page_n)[0].classList.contains('active')) {
      return;
    };
  
    // ajax
    $.ajax({
      type: "POST",
      url: "/configuration/",
      data : {  
        type: "page_select",
        page_n : page_n, //page_number
        csrfmiddlewaretoken: $(".input_form input[name='csrfmiddlewaretoken'][type='hidden']").attr('value'),
      },
      success: function (resp) {
        //loop
        $('#upd').html('')
        $.each(resp.results, function(i, val) {
          //apending params
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
        $('.pagination li.page-item.active').removeClass('active');
        $('.pagination li#'+page_n).addClass('active');
        activate_tooltips();
      },
      error: function () {}
    });
  }); 