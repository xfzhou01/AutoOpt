import sanity_check
import re
import expr

def print_info(info_str):    
    print("[INFO] [verilog-assertion-adder] -- {}".format(info_str))
def print_warning_info(info_str):
    print("[WARNING] [verilog-assertion-adder] -- {}".format(info_str))
def print_err_info(info_str):
    print("[ERROR] [verilog-assertion-adder] -- {}".format(info_str))


class verilog_assertion_adder:
    def __init__(self, verilog_file_path, 
                 top_module_name,
                 clock_name = "ap_clk"):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.santiy_check_not_empty_str(top_module_name)
        sanity_check.santiy_check_not_empty_str(clock_name)

        self._verilog_file_path = verilog_file_path
        self._top_module_name = top_module_name
        self._clock_name = clock_name
        self._verilog_file_lines = self._read_verilog_file()
        self._verilog_file_lines_new = []
        self._assertion_expr_list = []

    def _read_verilog_file(self):
        with open(self._verilog_file_path, "r") as f:
            return f.readlines()

    def _add_assertion_to_verilog_content(self, assertion_str_list):
        new_verilog_content = []
        is_entering_top_module = False
        for line in self._verilog_file_lines:
            line = line.strip()
            # print_info(f"line: {line}, is_entering_top_module: {is_entering_top_module}")
            
            if line.startswith(f"module {self._top_module_name} ("):
                is_entering_top_module = True
                new_verilog_content.append(line+ "\n")
                continue

            if is_entering_top_module and "endmodule" in line:
                is_entering_top_module = False
                for assertion_str in assertion_str_list:
                    print_info(f"add assertion: {assertion_str}")
                    new_verilog_content.append(assertion_str + "\n")
                new_verilog_content.append(line + "\n")
            else:
                new_verilog_content.append(line + "\n")
        self._verilog_file_lines_new = new_verilog_content


    def _add_assertion_expr_to_verilog(self):
        assertion_str_list = []
        for assertion_expr in self._assertion_expr_list:
            assertion_expr: expr.expr
            assertion_str_list.append(
                f"assert property (@(posedge {self._clock_name})"+\
                f" {assertion_expr.__str__()});")
        # print_info(f"assertion_str_list: {assertion_str_list}")
        # exit(0)
        self._add_assertion_to_verilog_content(assertion_str_list)
            

    # public method
    def set_assertion_str_list(self, assertion_str_list):
        sanity_check.sanity_check_list_not_empty(assertion_str_list)
        self._assertion_expr_list = assertion_str_list

    def set_assertion_expr_list(self, assertion_expr_list):
        sanity_check.sanity_check_list_not_empty(assertion_expr_list)
        # for assertion_expr in assertion_expr_list:
        #     sanity_check.sanity_check_type(assertion_expr, expr.expr)
        self._assertion_expr_list = assertion_expr_list

    def add_assertion_expr_to_assertion_str_list(self, assertion_expr):
        self._assertion_expr_list.append(assertion_expr)

    def write_to_file(self, output_file_path):
        print_info(f"write to file assertion count:"+\
                   f" {len(self._assertion_expr_list)}")
        self._add_assertion_expr_to_verilog()
        with open(output_file_path, "w") as f:
            f.writelines(self._verilog_file_lines_new)
        print_info(f"write to file {output_file_path} done")