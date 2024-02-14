function MissingFunctionParameterException(par_name, fn_name, code) {
    this.name = par_name;
    this.where = fn_name;
    this.code = code;
    this.msg = `Missing "${par_name}" parameter in "${fn_name}" function!`;
};