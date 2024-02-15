function savePerms(event) {
    event.preventDefault();

    function handleErrors(jqXHR, exception) {
        let msg;
        const base_msg = 'Response error.'
        try {
            if (jqXHR.status === 422) {
                if (typeof jqXHR.responseJSON.msg === 'undefined') {
                    msg = `${base_msg} [${jqXHR.status}]`
                }
                else {
                    msg = jqXHR.responseJSON.msg;
                }
            } else {
                msg = `${base_msg} [${jqXHR.status}]`
            }
        } catch(e) {
            msg = `${base_msg} Unknown error.`;
            console.log(e);
        }
        finally {
            showToastMsg(msg);
        }
    };

    function updatePageAfterSaving(resp) {
        let msg;
        const fn_name = 'updatePageAfterSaving';
        const base_msg = 'Error refreshing page after saving.'
        try {
            if (typeof resp.msg === 'undefined') {
                throw new MissingFunctionParameterException('msg', fn_name, 6);
            }
            else { // if ok
                $('#modal-close-btn').click();
                $.each($('#upd tr td'), function(i, val) {
                    val.classList.remove('bg-warning');
                });
                msg = resp.msg;
                window.onbeforeunload = null;
            }
        } catch(e) {
            if (e instanceof MissingFunctionParameterException) {
                msg = `${base_msg} Error code: ${e.code}.`;
                console.log(e.msg);
            }
            else {
                msg = `${base_msg} Unknown error.`;
                console.log(e);
            }
        } finally {
            showToastMsg(msg);
        }
        
    };

    $.ajax({
        type: "POST",
        url: "/permissions/",
        data : {
            type: RTYPE.SAVE
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
        },
        success: updatePageAfterSaving,
        error: handleErrors
    });
};

