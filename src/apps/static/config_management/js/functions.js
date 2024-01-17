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
        '<tr class="container flex-row">' +
            '<td class="col-2 align-top">' + val.file.instance.app.name + ': '+ val.name + '</td>' +
            '<td class="container flex-column col-5 align-top">' + '<span class="row">' + val.file.instance.app.component.name +'</span>' +
            (val.input_type=='checkbox'? 
            '<input class="row" type="' + val.input_type + '" value="true" name="' +  val.id  + (val.value=='true'? '" checked="1"/>': '/>'): 
                '<input class="form-control row" type="' + val.input_type + '" value="' + val.value.replaceAll('"', '&quot;') + '" name="' +  val.id  + '"/>') +
            '</td>' +
            '<td class="col-1 align-bottom text-center">' + 
            '<span class="d-inline-block" tabindex="0" data-coreui-toggle="tooltip" title="' + val.description + '">' +
                '<button class="btn btn-secondary" type="button" disabled>?</button>' + 
            '</span>' + 
            '</td>' +
        '</tr>'
        );
    });
}

activate_tooltips();