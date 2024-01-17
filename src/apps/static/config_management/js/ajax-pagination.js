$('#upd2').on('click', '.page-link', function(event){
  event.preventDefault();
  var page_n = $(this).attr('href');

  if ($('.pagination li#'+page_n)[0].classList.contains('active')) {
    return;
  };

  function onSuccess(resp) {
    updateTable(resp);
    $('.pagination li.page-item.active').removeClass('active');
    $('.pagination li#'+page_n).addClass('active');
    activate_tooltips();
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
    success: onSuccess,
    error: function () {}
  });
}); 