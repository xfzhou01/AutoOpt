import sanity_check
import os
import time
def print_info(info_str):
    print("[INFO] [iverilog] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [iverilog] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [iverilog] -- {}".format(info_str))

class iverilog:
    """wrapper for iverilog compiler and simulator
    """    
    def __init__(self, compiled_file_name, 
                 top_module_name, 
                 tb_top_module_name,
                 verilog_file_path,
                 tb_file_path):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.sanity_check_is_file_exist(tb_file_path)
        sanity_check.sanity_check_file_postfix(tb_file_path, ".v")

        sanity_check.santiy_check_not_empty_str(top_module_name)
        sanity_check.santiy_check_not_empty_str(compiled_file_name)
        sanity_check.santiy_check_not_empty_str(tb_top_module_name)


        self._compiled_file_name = compiled_file_name
        self._top_module_name = top_module_name
        self._tb_top_module_name = tb_top_module_name
        self._tb_file_path = tb_file_path
        self._verilog_file_path = verilog_file_path

    def run_compile(self):
        start_time = time.time()
        print_info("iverilog compiler start")
        cmd_str = f"iverilog -o {self._compiled_file_name}"+\
            f" -s {self._tb_top_module_name} "+\
            f"{self._verilog_file_path} {self._tb_file_path}"
        print_info("iverilog compile cmd_str: {}".format(cmd_str))
        return_code = os.system(cmd_str)
        end_time = time.time()
        print_info("iverilog compiler end")
        print_info("iverilog compiler time: {}".format(end_time - start_time))
        return return_code


    def run_sim(self, args=None):
        print_info("iverilog simulator start")
        cmd_str = "./{}".format(self._compiled_file_name)
        if args is not None:
            cmd_str += " " + args
        print_info("iverilog sim cmd_str: {}".format(cmd_str))
        start_time = time.time()
        return_code = os.system(cmd_str)
        end_time = time.time()
        print_info("iverilog simulator time: {}".format(end_time - start_time))
        print_info("iverilog simulator end")
        return return_code