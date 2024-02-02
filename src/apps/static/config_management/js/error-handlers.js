function commonHandler(jqXHR, exception) {
    let msg;
    const base_msg = 'Response error.'
    try {
        msg = `${base_msg} [${jqXHR.status}]`;

    } catch(e) {
        msg = `${base_msg} Unknown error.`;
        console.log(e);
    }
    finally {
        showToastMsg(msg);
    }
};