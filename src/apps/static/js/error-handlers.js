function commonHandler(jqXHR, exception) {
    let msg;
    const base_msg = 'Response error.'
    try {
        if (jqXHR.status === 422 && typeof jqXHR.responseJSON.msg === 'undefined') {
            msg = jqXHR.responseJSON.msg;
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