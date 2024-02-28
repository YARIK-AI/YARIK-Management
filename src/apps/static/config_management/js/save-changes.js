function saveChanges(event) {
    event.preventDefault();

    function afterResponseSaveChanges(resp) {
        function fn(status_dict, msg) {
            $('#sync-btn svg use')[0].href.baseVal = "/static/assets/icons/sync.svg#warn";
            $('#modal-close-btn').click();
            $.each($('#upd tr td .param-input'), function(i, val) {
                val.classList.remove('border-warning');
                val.classList.remove('border-danger');
            });
            updateFilterList(status_dict, null, 'collapseListStatus');
            $('#confirmSaveModal .modal-footer input#commit-msg')[0].value = '';
            window.onbeforeunload = null;
            showToastMsg(msg);
        };

        const fn_name = 'afterResponseSaveChanges';
        const base_msg = 'Error refreshing page after saving.';
        const code = 4;
        const arg_names = [RIPN.STATUS_FILTER, RIPN.MSG];
        const checks = [cU, cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn( ...arg_names.map((k) => resp[k]));

    };

    const commit_msg = $('#confirmSaveModal .modal-footer input#commit-msg')[0].value;

    $.ajax({
        type: "POST",
        url: URL_SLUG,
        data : {
            [ROPN.TYPE]: RTYPE.SAVE,
            [ROPN.COMMIT_MSG]: commit_msg
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: afterResponseSaveChanges,
        error: commonHandler
    });
};

