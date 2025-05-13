import sanity_check
import yosys
import os
import argparse

def print_err_info(info_str):
    print("[ERROR] [verilog-expr-optimizer] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [verilog-expr-optimizer] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [verilog-expr-optimizer] -- {}".format(info_str))


class verilog_expr_optimizer:

    def __init__(self, 
                 verilog_file_path, 
                 top_module_name, 
                 output_verilog_file_path = None):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.santiy_check_not_empty_str(top_module_name)
        self._verilog_file_path = verilog_file_path
        self._top_module_name = top_module_name
        self._output_verilog_file_path = ""
        self._gen_output_verilog_file_path(output_verilog_file_path)
        

        self._cmd_list = [
            f"read_verilog {self._verilog_file_path}",
            f"prep -top {self._top_module_name}",

            "flatten",
            "opt_expr",
            "opt_clean -purge",
            f"write_verilog -noattr -noparallelcase -simple-lhs {self._output_verilog_file_path}"
        ]
        self._yosys_instance = yosys.yosys_execution(cmd_list=self._cmd_list,
                                                     debug_log="yosys_compile.log")
        
    def launch_opt(self):
        self._yosys_instance.execute()

    def get_output_verilog_file_path(self):
        return self._output_verilog_file_path
    
    def get_top_module_name(self):
        return self._top_module_name
    
    def get_verilog_file_path(self):
        return self._verilog_file_path

    def _gen_output_verilog_file_path(self, output_verilog_file_path):
        if output_verilog_file_path is None:
            base_name = os.path.splitext(
                os.path.basename(self._verilog_file_path))[0]
            self._output_verilog_file_path = f"{base_name}_opt.v"
        else:
            self._output_verilog_file_path = output_verilog_file_path
        print_info(f"the output file will be written to"+\
                   f" {self._output_verilog_file_path}")
        
# 

def get_parser():
    parser = argparse.ArgumentParser(description="verilog expr optimizer")
    parser.add_argument("--FILE", type=str, help="the input file", required=True)
    parser.add_argument("--TOP", type=str, help="the top function name",required=True)
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    a = verilog_expr_optimizer(verilog_file_path=args.FILE,
                           top_module_name=args.TOP)
    a.launch_opt()
    
if __name__ == "__main__":
    main()