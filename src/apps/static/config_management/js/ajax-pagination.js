
// response parameters: page_n, results

$('#upd2').on('click', '.page-link', function(event){
  event.preventDefault();
  const page_n = $(this).attr('href');

  var elem = $(`ul.pagination#upd2 li#${page_n}.page-item`)[0];

  if (elem.classList.contains('active')) {
    return;
  };

  function onSuccess(resp) {
    updateTable(resp);
    var active = $('ul.pagination#upd2 li.page-item.active')[0];
    var selected = $(`ul.pagination#upd2 li#${page_n}.page-item`)[0];
    active.classList.remove('active');
    selected.classList.add('active');
    activate_tooltips();
  };

  // ajax
  $.ajax({
    type: "GET",
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