
import sanity_check
import argparse
import re
def print_err_info(info_str):
    print("[ERROR] [verilog-simple-parser] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [verilog-simple-parser] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [verilog-simple-parser] -- {}".format(info_str))

class verilog_simple_parser:
    """a parser designed for RTL autoopt
    - responsible to collect the arithmetic information
    - including: operations (+/-/*)
    - including: width
    """    
    def __init__(self, verilog_file_path):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        print_info(f"read verilog file path: {verilog_file_path}")


        self._verilog_file_path = verilog_file_path
        
        # content of verilog file
        self._verilog_content = []

        # for parser use, the iterator of current module
        self._parse_current_module_iterator = ""

        # 
        self._wire_width_info = dict()

        # 
        self._reg_width_info = dict()

        # 
        self._const_value_info = dict()



        self._read_verilog_content()
        self._parse()

    def _read_verilog_content(self):
        with open(self._verilog_file_path, 'r') as verilog_file:
            self._verilog_content = verilog_file.readlines()


    def _is_line_declaration_of_reg(self, line:str):
        """judge whether a line is a reg decl

        Args:
            line (str): a line in file
        """        
        line = line.strip()
        pattern_reg_decl = "^reg\s*\[.+:.+\]\s*\w+"
        return re.search(pattern=pattern_reg_decl, string=line) is not None

    def _is_line_declaration_of_wire(self, line:str):
        """judge whether a line is a wire decl

        Args:
            line (str): a line in file
        """        
        line = line.strip()
        pattern_wire_decl = "^wire\s*\[.+:.+\]\s*\w+"
        return re.search(pattern=pattern_wire_decl, string=line) is not None

    def _is_line_declaration_of_reg_or_wire(self, line:str):
        """judge whether a line is a reg or wire decl

        Args:
            line (str): a line in file
        """        
        return self._is_line_declaration_of_reg(line) or \
            self._is_line_declaration_of_wire(line)

    def _is_line_module_declaration(self, line:str):
        """judge whether a line is decl to a module

        Args:
            line (str): a line in file
        """        
        line = line.strip()
        return line.startswith("module ")

    def _extract_module_name_from_line(self, line:str):
        """extract module name from line

        Args:
            line (str): a line in file
        """        
        line = line.strip()
        line = line[len("module"):]
        line = line.split("(")[0]
        return line.strip()


    def _update_current_module(self, line:str):
        """during iteration of verilog file, update the current module iterator

        Args:
            line (str): a line in file
        """        
        if self._is_line_module_declaration(line):
            self._parse_current_module_iterator = \
                self._extract_module_name_from_line(line)

    
    def _update_const_value_info(self, line:str):
        """update the dict to control constant value
        `self._const_value_info` will be updated by line

        Args:
            line (str): a line in file
        """       
        module_name = self._parse_current_module_iterator

        if self._is_line_const_declaration(line):
            nv_tuple = self._extract_const_name_and_value_from_line(line=line)
            if self._parse_current_module_iterator in self._const_value_info:
                sanity_check.sanity_check_type(
                    self._const_value_info[module_name], dict)
                sanity_check.sanity_check_entry_not_exist_in_dict(
                    d=self._const_value_info[module_name],
                    k=nv_tuple[0]
                )
                self._const_value_info[module_name][nv_tuple[0]] = nv_tuple[1]
            else:
                self._const_value_info[module_name] = {nv_tuple[0]: nv_tuple[1]}
                

    def _extract_const_name_and_value_from_line(self, line:str):
        """extract const value and name from line, for example, 
        `parameter    ap_ST_fsm_state1 = 3'd1;` will return 
        `ap_ST_fsm_state1` and `1`

        Args:
            line (str): _description_
        
        Returns:
            tuple
        """              
        line = line.strip()
        line = line[:-1] if line.endswith(";") else line
        line_assign = line[len("parameter"):].strip()
        const_name = line_assign.split("=")[0].strip()
        value_str = line_assign.split("=")[1]
        if "+" in value_str or "-" in value_str or "*" in value_str:
            return (const_name, self._util_eval_expr_str(value_str))
        else:
            return (const_name, self._util_rtl_number_to_int(value_str))


    def _is_line_const_declaration(self, line:str):
        """judge whether a line a decl for constant value
        for example `parameter    ap_ST_fsm_state1 = 3'd1;`

        Args:
            line (str): a line in file
        """        
        return line.startswith("parameter ") and line.endswith(";")


    def _is_line_contain_arithmetic_operation(self, line):
        """judge whether the line in verilog contain arithmetic operation

        Args:
            line (str): the line in verilog file

        Returns:
            bool: the judge result
        """        
        if self._is_line_contain_arithmetic_symbols(line):
            if self._is_line_comb_always_begin(line):
                return False
            if self._is_line_comment(line):
                return False
            if self._is_line_timescale(line):
                return False
            if self._is_line_macro(line):
                return False
            if self._is_star_symbol_in_macro(line):
                return False
            if self._is_div_symbol_in_comment(line):
                return False
            if self._is_line_arithmetic_symbol_all_in_address(line):
                return False
            if self._is_line_for_loop(line):
                return False
            if self._is_line_arithmetic_symbol_all_width(line):
                return False
            return True
        return False 

    def _is_line_contain_arithmetic_symbols(self, line:str):
        """a simple judge of whether the line contains arithmetic symbols
        only consider `+` `-` `*` `/` symbol is in line or not, a very simple
        filtering

        Args:
            line (str): the line in file
        """        
        return "+" in line or "-" in line or "*" in line or "/" in line

    def _is_line_comment(self, line:str):
        """judge whether the line in python is commented out

        Args:
            line (str): the line in file
        """
        return line.startswith("//")

    def _is_line_comb_always_begin(self, line:str):
        return "always @ (*) begin" in line

    def _is_line_timescale(self, line:str):
        return line.strip().startswith("`timescale")

    def _is_line_macro(self, line:str):
        return line.strip().startswith("(*") and line.strip().endswith("*)")

    def _is_star_symbol_in_macro(self, line:str):
        """check is the line that contain `*` have `*` actually in macro
        - example: 
        Args:
            line (str): the line in verilog file
        """        
        return ("*" not in line.replace("(*", "").replace("*)","")) \
            and "*" in line
    
    def _is_div_symbol_in_comment(self, line:str):
        """check whether the `//` is a comment in line

        Args:
            line (str): the line in file
        """        
        return "/" in line and "//" in line and \
            ("/" not in line.replace("//", ""))
    
    def _is_line_arithmetic_symbol_all_in_address(self, line:str):
        """judge whether the arithmetic symbol in a line all represent address
        for example: `SRL_SIG[i+1] <= SRL_SIG[i];` should return true 

        Args:
            line (str): line in file
        """        
        char_except_square_bracket_pattern = "[^\[\]]"
        char_arithmetic_pattern = "[\+|\-|\*|\/]+"
        arithmetic_symbol_in_address_pattern = (
            f"\[{char_except_square_bracket_pattern}*"
            f"{char_arithmetic_pattern}"
            f"{char_except_square_bracket_pattern}*\]"
        )
        line_no_address = re.sub(pattern=arithmetic_symbol_in_address_pattern,
                                 string=line,
                                 repl="")
        return not self._is_line_contain_arithmetic_symbols(line_no_address)

    def _is_line_for_loop(self, line:str):
        """judge whether a line represents the head of a for loop, for example,
        `for (i=0;i<DEPTH-1;i=i+1)` should return true

        Args:
            line (str): the line in file
        """
        for_loop_pattern = f"for\s*\(.*\)"
        return re.search(string=line, pattern=for_loop_pattern) is not None     

    def _is_line_arithmetic_symbol_all_width(self, line:str):
        """judge whether the arithmetic symbol in a line all represent width
        for example: `~{(ADDR_WIDTH+1){1'b0}};` should return true 

        Args:
            line (str): line in file
        """         
        zero_or_one_pattern = "\d+'b[0|1]"
        big_bracket_zero_or_one_pattern = "\{" + zero_or_one_pattern + "\}"


        prefix_width_pattern = "\(*\w+[\+|\-|\*|\/]\w+\)*"

        expand_width_pattern = prefix_width_pattern + \
        big_bracket_zero_or_one_pattern 
        line = line.strip()
        line_no_const_expand = re.sub(pattern=expand_width_pattern,
                                      string=line,
                                      repl="")
        return not \
            self._is_line_contain_arithmetic_symbols(line_no_const_expand)

    def _util_rtl_number_to_int(self, rtl_number:str):
        """convert `3'd1` to 1

        Args:
            rtl_number (str): the number in rtl format, support `?'d?`, `?'b?`,
            pure digit

        Raises:
            ValueError: the input string is not a rtl number

        Returns:
            int: the value of rtl number
        """        
        sanity_check.santiy_check_not_empty_str(rtl_number)
        if "'d" in rtl_number:
            return int(rtl_number.split('d')[1])
        elif "'b" in rtl_number:
            return int(rtl_number.split('b')[1], 2)
        elif rtl_number.isdigit():
            return int(rtl_number)
        else:
            print_err_info(f"expect the string to be a number in rtl like: " +\
                f"3'd1 but got {rtl_number}")
            raise ValueError()

    def _util_is_str_rtl_number(self, rtl_number:str):
        """judge the string is a rtl number

        Args:
            rtl_number (str): the rtl number string
        """        
        rtl_number_pattern = "^\d+'[d|b|h|o]\d+$"

        return re.match(rtl_number_pattern) is not None or rtl_number.isdigit()

    def _util_eval_expr_str(self, const_expr:str):
        """evaluate expression to calculate a constant

        Args:
            const_expr (str): the constant expression

        Returns:
            int: the eval(expr) value
        """        
        if self._util_is_str_rtl_number(rtl_number=const_expr):
            return self._util_rtl_number_to_int(rtl_number=const_expr)
        else:
            plus_count = const_expr.count("+")
            minus_count = const_expr.count("-")
            mul_count = const_expr.count("*")
            if plus_count + minus_count + mul_count != 1:
                print_err_info("now we only support the case when there is " +\
                    f"only one +|-|*, but got const_expr = {const_expr}")
                raise ValueError()
            if plus_count == 1:
                # eval the value of `a+b`
                const_expr_terms = const_expr.split("+")
                if not len(const_expr_terms) == 2:
                    print_err_info(f"expected the const expr to have format"+\
                        f"like `a+b` but got {const_expr}")
                    raise ValueError()
                term_0 = const_expr_terms[0]
                term_1 = const_expr_terms[1]
                return \
                    self._util_find_const_value_according_to_term(term_0) \
                    + self._util_find_const_value_according_to_term(term_1)
            if minus_count == 1:
                # eval the value of `a-b`
                const_expr_terms = const_expr.split("-")
                if not len(const_expr_terms) == 2:
                    print_err_info(f"expected the const expr to have format"+\
                        f"like `a-b` but got {const_expr}")
                    raise ValueError()
                term_0 = const_expr_terms[0]
                term_1 = const_expr_terms[1]
                return \
                    self._util_find_const_value_according_to_term(term_0) \
                    - self._util_find_const_value_according_to_term(term_1)
            if mul_count == 1:
                # eval the value of `a*b`
                const_expr_terms = const_expr.split("*")
                if not len(const_expr_terms) == 2:
                    print_err_info(f"expected the const expr to have format"+\
                        f"like `a*b` but got {const_expr}")
                    raise ValueError()
                term_0 = const_expr_terms[0]
                term_1 = const_expr_terms[1]
                return \
                    self._util_find_const_value_according_to_term(term_0) \
                    * self._util_find_const_value_according_to_term(term_1)

    def _util_find_const_value_according_to_term(self, term:str):
        """find const value according to a constant string such as 
        `ap_ST_fsm_state1` or number such as `3'd1`

        Args:
            term (str): the term str

        Returns:
            int: value of this term
        """        
        sanity_check.santiy_check_not_empty_str(term)
        if self._util_is_str_rtl_number(rtl_number=term):
            return self._util_rtl_number_to_int(rtl_number=term)
        else:
            return self._util_find_const_value_according_to_name(
                value_name=term,
                module_name=self._parse_current_module_iterator)

    def _util_find_const_value_according_to_name(self, 
        value_name:str, 
        module_name:str):
        """find the const value in verilog that already traversed

        Args:
            value_name (str): the const value name
            module_name (str): the module name
        
        Returns:
            int: the found const value
        """        
        sanity_check.santiy_check_not_empty_str(value_name)
        sanity_check.santiy_check_not_empty_str(module_name)
        try:
            const_value_dict_in_module = self._const_value_info[module_name]
        except Exception as e:
            print_err_info(f"module name: {module_name} does not exists" +\
                " in dict")
            raise e
        sanity_check.sanity_check_dict_not_empty(const_value_dict_in_module)
        try:
            return const_value_dict_in_module[value_name]
        except Exception as e:
            print_err_info(f"module name: {module_name};"+\
                f" value name: {value_name} cannot find a corresponding"+\
                f" const, value_dict_in_module = {const_value_dict_in_module}")
            raise e
        




    def _parse(self):
        """do parse and extract critical information
        """     
        current_module = ""   
        for line in self._verilog_content:
            # if self._is_line_contain_arithmetic_operation(line=line):
            #     print_info(line.strip())
            # if self._is_line_declaration_of_reg_or_wire(line=line):
            #     print_info(line.strip())
            self._update_current_module(line)
            self._update_const_value_info(line)

# -- testing

def get_parser():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--file", type=str, required=True, 
        help="the input verilog file")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    p_instance = verilog_simple_parser(verilog_file_path=args.file)

if __name__=="__main__":
    main()

