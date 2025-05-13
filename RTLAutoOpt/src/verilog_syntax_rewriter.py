import sanity_check 
import re

def print_err_info(info_str):
    print("[ERROR] [verilog-syntax-rewriter] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [verilog-syntax-rewriter] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [verilog-syntaxx-rewriter] -- {}".format(info_str))


class verilog_syntax_rewriter:
    """assign { _001_[0], _040_[2], _041_[11] } = ~ _061_;
    such kind of grammar should be removed from verilog
    """    

    def __init__(self, verilog_file_path):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        self._verilog_file_path = verilog_file_path
        self._verilog_file_content = []

        self._verilog_file_content_new = []
        self._rewrite_counter = 0
        self._read_verilog_file()
        self._detect_and_rewrite()

        self._const_set = set()
        self._var_dict = {}
        self._clk_name = ""
        self._update_clk_name()
        self._update_const_and_var_set()
        
        print_info("finished updating const and var set")
        print_info("finished rewriting")

    def _read_verilog_file(self):
        with open(self._verilog_file_path, 'r') as verilog_file:
            self._verilog_file_content = verilog_file.readlines()


    def _is_line_should_rewrite(self, line:str):
        """whether a line has pattern
        `assign { _001_[0], _040_[2], _041_[11] } = ~ _061_;`

        Args:
            line (str): line in verilog file
        """        
        line = line.strip()
        if not line.startswith("assign"):
            return False
        pattern = "^assign\s+\{.*\}\s+=\s+.*;"
        return re.search(pattern=pattern,
                         string=line) is not None
    
    def _rewrite_line(self, line:str):
        line = line.strip()
        pattern = "^assign\s+\{(.*)\}\s+=\s+(.*);"
        ps =  re.findall(pattern=pattern, string=line) 
        sanity_check.sanity_check_not_none(ps)

        if not len(ps) == 1:
            print_err_info("find multiple matches in line: " +\
                           f"{line}, matches = {ps}")
            raise ValueError()
        
        left_values = ps[0][0]
        right_expression = ps[0][1]

        # get the left values and their widths
        left_values_list, left_value_widths = \
            self._rewrite_line_parse_left_values(left_values)
        
        # get the re-decl of right expression if needed
        decl_right_expr = self._rewrite_line_get_decl_right_expression(
            right_expression=right_expression,
            right_expression_width=sum(left_value_widths))
        rewirte_lines = self._generate_rewrite_line_content(
            left_value_list=left_values_list,
            left_value_widths=left_value_widths,
            decl_right_expr=decl_right_expr,
            right_expression=right_expression
        )

        return rewirte_lines

    def _generate_assign_str(self, 
                             left_value_name:str,
                             righ_value_name:str,
                             high_index_left = None,
                             low_index_left = None,
                             high_index_right = None,
                             low_index_right = None):
        """generate assign string for verilog file,
        will return `assign left_value_name[high_index_left:low_index_left]
        = righ_value_name[high_index_right:low_index_right]`. 
        if no bit selection, the corresponding part will be ignored.

        Args:
            left_value_name (str): the left value name
            righ_value_name (str): the right value name

        Returns:
            str: the assign string
        """
        if high_index_left is not None:
            sanity_check.sanity_check_value_greater_or_equal_to_0(high_index_left)
        if low_index_left is not None:
            sanity_check.sanity_check_value_greater_or_equal_to_0(low_index_left)
        if high_index_right is not None:
            sanity_check.sanity_check_value_greater_or_equal_to_0(high_index_right)
        if low_index_right is not None: 
            sanity_check.sanity_check_value_greater_or_equal_to_0(low_index_right)
        sanity_check.sanity_check_both_none_or_not_none(
            high_index_left, low_index_left
        )
        sanity_check.sanity_check_both_none_or_not_none(
            high_index_right, low_index_right
        )
        left_part_select_str = ""
        if not(high_index_left is None and low_index_left is None):
            if high_index_left == low_index_left:
                left_part_select_str = f"[{high_index_left}]"
            else:
                left_part_select_str = f"[{high_index_left}:{low_index_left}]"
        right_part_select_str = ""
        if not(high_index_right is None and low_index_right is None):
            if high_index_right == low_index_right:
                right_part_select_str = f"[{high_index_right}]"
            else:
                right_part_select_str = f"[{high_index_right}:{low_index_right}]"
        return f"assign {left_value_name}{left_part_select_str} = "+\
            f"{righ_value_name}{right_part_select_str};\n"

    def _generate_rewrite_line_content_assignment(self,
            left_value_list:list[str],
            left_value_widths:list[int],
            right_expression:str):
        rewrite_lines = []
        sanity_check.sanity_check_eq_length_multiple_list(
            sl=[left_value_list, left_value_widths]
        )
        accumulated_index = sum(left_value_widths)-1
        for i in range(len(left_value_list)):
            left_value_name = left_value_list[i]
            left_value_width = left_value_widths[i]
            rewrite_lines.append(
                self._generate_assign_str(
                    left_value_name=left_value_name,
                    righ_value_name=right_expression,
                    high_index_right=accumulated_index,
                    low_index_right=accumulated_index-left_value_width+1
                )
            )
            accumulated_index -= left_value_width
        return rewrite_lines

    def _generate_rewrite_line_content(self,
            left_value_list:list[str],
            left_value_widths:list[int],
            decl_right_expr:tuple,
            right_expression:str):
        """generate the rewrite line content

        Args:
            left_value_list (list[str]): left value list
            left_value_widths (list[int]): the width of each left value
            decl_right_expr (tuple): the re-decl of right expression,\
            contains the re-decl line and the re-decl name, if none, \
            no re-decl, directly use the right expression
            right_expression (str): the right expression used for re-decl.

        Returns:
            list[str]: the rewrite lines
        """        
        rewrite_lines = []
        sanity_check.sanity_check_eq_length_multiple_list(
            sl=[left_value_list, left_value_widths]
        )
        if decl_right_expr is None:
            # the case when no re-decl
            rewrite_lines += self._generate_rewrite_line_content_assignment(
                left_value_list=left_value_list,
                left_value_widths=left_value_widths,
                right_expression=right_expression
            )
        else:
            # the case when re-decl
            re_decl_line, re_decl_name = decl_right_expr
            rewrite_lines.append(re_decl_line)
            rewrite_lines += self._generate_rewrite_line_content_assignment(
                left_value_list=left_value_list,
                left_value_widths=left_value_widths,
                right_expression=re_decl_name
            )
        return rewrite_lines


    def _rewrite_line_parse_left_values(self, left_values:str):
        """the width of each left value in the assigned left values, 
        for example, ` _001_[0], _040_[2], _041_[11]` will return `[1,1,1]`

        Args:
            left_values (str): the string of left values

        Returns:
            list[str],list[int]: the list of names / widths
        """        
        left_values_list = [lv.strip() for lv in left_values.split(",")]
        left_value_width = [self._rewrite_line_parse_left_value(lv) \
                            for lv in left_values_list]
        return left_values_list, left_value_width

    def _rewrite_line_parse_left_value(self, left_value:str):
        """get the bit width of one of the left values, for example, 
        `_001_[0]` have bit width `1`, and `_001_[2:0]` have bit width `3`

        Args:
            left_value (str): the one of left values

        Raises:
            ValueError: found multiple index regions in left value
            NotImplementedError: the case when left value does not contain \
            index selection

        Returns:
            int: bit width of left value
        """        
        left_value = left_value.strip()
        if "[" in left_value and "]" in left_value:
            pattern = ".*\[(.*)\]"
            ps = re.findall(pattern=pattern, string=left_value)
            if not len(ps) == 1:
                print_err_info(f"the left value: {left_value} does not match"+\
                               " expected pattern well, should have only 1 "+\
                               f"match but got match: {ps}")
                raise ValueError()
            index_str = ps[0][0]
            index_str:str
            if ":" in index_str:
                # the case when bit selection
                h_index = index_str.split(":")[0].strip()
                l_index = index_str.split(":")[1].strip()
                return int(h_index) - int(l_index) + 1
            else:
                # the case without bit selection
                return 1
        else:
            print_err_info(f"the left value {left_value} should contain"+\
                           " an pair of `[]` to part select")
            raise NotImplementedError()


    def _rewrite_line_get_decl_right_expression(self, 
                                                right_expression:str,
                                                right_expression_width:int):
        """if the right expression contains more than an variable, for example:
        ` ~ _061_`, need to create a new wire to rewrite for keeping the 
        verilog syntax

        Args:
            right_expression (str): the expression
            right_expression_width (int): the data width of expression

        Returns:
            tuple|None: a tuple contains rewrite line and the name of the 
            rewrite expression
        """        
        sanity_check.santiy_check_not_empty_str(right_expression)
        right_expression = right_expression.strip()
        if re.match(pattern="^\w+$", string=right_expression):
            # in this case, the right expression does not require any re-decl 
            return None
        else:
            # re-decl of right expression
            sanity_check.sanity_check_value_greater_or_equal_to_1(
                right_expression_width
            )
            if right_expression_width == 1:
                re_decl_line = f"wire rewrite_{self._rewrite_counter} ="+\
                    f"{right_expression};\n"
            else:
                re_decl_line = f"wire [{right_expression_width-1}:0]"+\
                    f" rewrite_{self._rewrite_counter} ="+\
                    f" {right_expression};\n"
            rewirte_variable_name = f"rewrite_{self._rewrite_counter}"
            self._rewrite_counter += 1
            return (re_decl_line, rewirte_variable_name)

    def _is_line_should_rewrite_assign(self, line:str):
        """in order to detect errors such as 
        `reg [11:0] ap_CS_fsm;assign ap_CS_fsm = 12'h001;`, rewrite the
        statement into `reg [11:0] ap_CS_fsm = 12'h001;`

        Args:
            line (str): the line in file
        """        
        line = line.strip()
        pattern = r"^reg\s+\[.*\]\s+[\w\.\\]+\s*;\s*assign\s+[\w\.\\]+\s*=.*;"
        return re.search(pattern=pattern, string=line) is not None

    def _rewrite_line_assign(self, line:str):
        line = line.strip()
        pattern = r"^(reg\s+\[.*\]\s+[\w\.\\]+\s*);\s*assign\s+[\w\.\\]+\s*=(.*);"
        ps = re.findall(pattern=pattern, string=line)
        sanity_check.sanity_check_not_none(ps)
        if not len(ps) == 1:
            print_err_info("find multiple matches in line: " +\
                           f"{line}, matches = {ps}")
            raise ValueError()
        
        reg_decl = ps[0][0]
        assign_expr = ps[0][1]
        return [f"{reg_decl} = {assign_expr};\n"]


    def _detect_and_rewrite(self):
        for line in self._verilog_file_content:
            if "\\" in line:
                line = line.replace("\\", "BLACKSLASH_")
            if "." in line:
                line = line.replace(".", "_DOT_")

            if self._is_line_should_rewrite(line):
                new_lines = self._rewrite_line(line)
                sanity_check.sanity_check_list_not_empty(new_lines)
                self._verilog_file_content_new += new_lines
            elif self._is_line_should_rewrite_assign(line):
                new_lines = self._rewrite_line_assign(line)
                sanity_check.sanity_check_list_not_empty(new_lines)
                self._verilog_file_content_new += new_lines
            else:
                self._verilog_file_content_new.append(line)

    def _is_line_contain_const(self, line):
        """check whether a line contains a constant assignment, 
        for example, `parameter CONST_VAL = 32'hDEADBEEF;`

        Args:
            line (str): the line in the verilog file

        Returns:
            bool: True if the line contains a constant assignment, False otherwise
        """
        line = line.strip()
        pattern = r"^(parameter|localparam)\s+[\w\.\\]+\s*=\s*.*;"
        contain_param_def_const =\
              re.search(pattern=pattern, string=line) is not None
        
        pattern_const = "\d+'[bodh][0-9a-fA-F]+"
        contain_const = re.search(pattern=pattern_const, string=line) is not None
        return contain_param_def_const or contain_const
    
    def _add_line_const_to_const_set(self,line):
        """parse a constant assignment line and add it to the constant set

        Args:
            line (str): the line in the verilog file
        """
        line = line.strip()
        pattern = r"^(parameter|localparam)\s+([\w\.\\]+)\s*=\s*(.*);"
        ps = re.findall(pattern=pattern, string=line)
        sanity_check.sanity_check_not_none(ps)

        if len(ps) == 1:        
            const_name = ps[0][1]
            const_value = ps[0][2]
            const_value = self._convert_verilog_const_to_int(const_value)
            self._const_set.add(const_value)
        else:
            if not len(ps) == 0:
                print_err_info("find multiple matches in line: " +\
                       f"{line}, matches = {ps}")
                raise ValueError()
        
        pattern_const = "\d+'[bodh][0-9a-fA-F]+"
        ps = re.findall(pattern=pattern_const, string=line)
        for p in ps:
            p = self._convert_verilog_const_to_int(p)
            self._const_set.add(p)

    def _convert_verilog_const_to_int(self, const_str):
        """convert the verilog constant string to int

        Args:
            const_str (str): the constant string in verilog

        Returns:
            int: the integer value of the constant
        """
        const_str = const_str.strip()
        if const_str.isdigit():
            return int(const_str)
        elif "'h" in const_str:
            return int(const_str.split("'")[1][1:], 16)
        elif "'b" in const_str:
            return int(const_str.split("'")[1][1:], 2)
        elif "'d" in const_str:
            return int(const_str.split("'")[1][1:], 10)
        elif "'o" in const_str:
            return int(const_str.split("'")[1][1:], 8)
        else:
            print_err_info(f"unsupported const_str {const_str}")
            raise ValueError()
        

    def _is_line_variable_definition(self, line):
        # see whether the line is a wire / reg / input / output def.
        line = line.strip()
        pattern = r"^(wire|reg|input|output)\s+(\[.*\]\s+)?[\w\.\\]+(\s*,\s*[\w\.\\]+)*\s*;"
        return re.search(pattern=pattern, string=line) is not None
    
    def _add_line_variable_info_to_var_dict(self, line):
        line = line.strip()
        pattern = r"^(wire|reg|input|output)\s+(\[.*\]\s+)?([\w\.\\]+(\s*,\s*[\w\.\\]+)*)\s*;"
        ps = re.findall(pattern=pattern, string=line)
        sanity_check.sanity_check_not_none(ps)
        if not len(ps) == 1:
            print_err_info("find multiple matches in line: " +\
                   f"{line}, matches = {ps}")
            raise ValueError()
        
        var_type = ps[0][0]
        var_names = ps[0][2].split(",")
        var_names = [vn.strip() for vn in var_names]
        var_width_str = ps[0][1]
        if var_width_str == "" or var_width_str is None:
            var_width = 1
        else:
            var_width_str = var_width_str.split("[")[1].split("]")[0]
            var_width = int(var_width_str.split(":")[0]) - \
                int(var_width_str.split(":")[1]) + 1
        
        for var_name in var_names:
            if var_name == self._clk_name:
                continue
            if var_name in self._var_dict:
                if not self._var_dict[var_name]["width"] == var_width:
                    print_warning_info(f"variable {var_name} is redefined "+\
                                       f"with different width, old width: "+\
                                       f"{self._var_dict[var_name]['width']}, "+\
                                       f"new width: {var_width}")
            self._var_dict[var_name] = {"type": var_type, 
                                        "width": var_width}

    def _update_const_and_var_set(self):
        print_info(f"updating const and var set in file {self._verilog_file_path}")
        sanity_check.sanity_check_list_not_empty(self._verilog_file_content_new)

        is_entering_function = False

        for line in self._verilog_file_content_new:
            if line.strip().startswith("function"):
                is_entering_function = True
            elif line.strip().startswith("endfunction"):
                is_entering_function = False
            if self._is_line_contain_const(line):
                self._add_line_const_to_const_set(line)
            elif self._is_line_variable_definition(line) and not is_entering_function:
                self._add_line_variable_info_to_var_dict(line)

    def _is_line_contain_posedge(self, line):
        line = line.strip()
        pattern = r"posedge\s+[\w\.\\]+"
        return re.search(pattern=pattern, string=line) is not None

    def _extract_clk_name(self, line):
        line = line.strip()
        pattern = r"posedge\s+([\w\.\\]+)"
        ps = re.findall(pattern=pattern, string=line)
        sanity_check.sanity_check_not_none(ps)
        if not len(ps) == 1:
            print_err_info("find multiple matches in line: " +\
                   f"{line}, matches = {ps}")
            raise ValueError()
        return ps[0]

    def _update_clk_name(self):
        for line in self._verilog_file_content:
            if self._is_line_contain_posedge(line):
                self._clk_name = self._extract_clk_name(line)
                break

    def write_rewrited_verilog(self, rewrite_verilog_file_path):
        sanity_check.santiy_check_not_empty_str(rewrite_verilog_file_path)
        sanity_check.sanity_check_list_not_empty(self._verilog_file_content_new
                                                 )
        with open(rewrite_verilog_file_path, 'w+') as rewrite_verilog_file:
            rewrite_verilog_file.write(
                "".join(self._verilog_file_content_new)
            )

    def get_variable_dict(self):
        return self._var_dict.copy()
    
    def get_const_set(self):
        return self._const_set.copy()

# test
import argparse
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--FILE", required=True, help="the verilog file", 
                        type=str)
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    a = verilog_syntax_rewriter(verilog_file_path=args.FILE)
    a.write_rewrited_verilog(rewrite_verilog_file_path="rewrite.v")
if __name__ == "__main__":
    main()