function checkInput(fn, checks, fn_name, base_msg, arg_names, code, additionalOnErrorActions) {
    return function() {
        try {
            for(let i = 0; i < checks.length; i++) {
                if(checks[i](arguments[i])) {
                    throw new MissingFunctionParameterException(
                        arg_names[i], 
                        fn_name, 
                        code
                    );
                }
            }
            return fn.apply(this, arguments)
        } catch(e) {
            let msg;
            if (e instanceof MissingFunctionParameterException) {
                msg = `${base_msg} Error code: ${e.code}.`;
                console.log(e.msg);
            }
            else {
                msg = `${base_msg} Unknown error.`;
                console.log(e);
            }
            showToastMsg(msg);
            if(typeof additionalOnErrorActions !== 'undefined')
                return additionalOnErrorActions.apply(this, arguments)
            return;
        }
    }
};