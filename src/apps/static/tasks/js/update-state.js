function updateState() {
    function afterResponseUpdateState(resp) {
        function fn(tasks) {
            updateTaskInfos(tasks)
        };

        const fn_name = 'afterResponseUpdateState';
        const base_msg = 'Error displaying state after update.';
        const code = 4;
        const arg_names = [RIPN.LIST_EL];
        const checks = [cU];

        fn = checkInput(fn, checks, fn_name, base_msg, arg_names, code)
        fn(resp[RIPN.LIST_EL]);
        
    };

    // ajax
    $.ajax({
        type: "GET",
        url: URL_SLUG,
        data : {  
            [ROPN.TYPE]: RTYPE.UPDATE_STATE,
        },
        success: afterResponseUpdateState,
        error: commonHandler
    });
};