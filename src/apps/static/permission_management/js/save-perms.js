function savePerms(event) {
    event.preventDefault();

    function afterResponseSavePerms(resp) {
        function fn(msg) {
            $('#modal-close-btn').click();
            $.each($('#upd tr td'), function(i, val) {
                val.classList.remove('bg-warning');
            });
            window.onbeforeunload = null;
            showToastMsg(msg);
        };

        const fn_name = 'afterResponceSavePerms';
        const base_msg = 'Error refreshing page after saving.';
        const code = 6;
        const arg_names = [RIPN.MSG,];
        const checks = [cU,];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));
        
    };

    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SAVE
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: afterResponseSavePerms,
        error: commonHandler
    });
};

