import sanity_check
import os
import yosys_formal
import time

def print_info(info_str):
    print("[INFO] [ic3-simple] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [ic3-simple] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [ic3-simple] -- {}".format(info_str))

class ic3_simple_checker:
    """wrapper for ic3 simple checker
    only checks prove / disprove without any other information
    """
    def __init__(self,
                 is_verbose:bool = False,
                 is_print_statistic:bool = False
                 ):
        sanity_check.sanity_check_type(is_verbose, bool)
        sanity_check.sanity_check_type(is_print_statistic,bool)
        self._is_verbose = is_verbose
        self._is_print_statistic = is_print_statistic

        ssmmhhddmmyy_str = time.strftime("%d%m%y_%H%M%S")
        self._ic3_folder_path = f"ic3_simple_checker_{ssmmhhddmmyy_str}"
        if not os.path.exists(self._ic3_folder_path):
            os.makedirs(self._ic3_folder_path)

        index = 0
        self._aag_file_path = \
            os.path.join(self._ic3_folder_path, 
                         f"ic3_simple_checker_{index}.aag")
        self._ic3_check_log_file_path = os.path.join(self._ic3_folder_path, 
                         f"ic3_simple_checker_{index}.log")
        self._ic3_invariant_path = os.path.join(self._ic3_folder_path,
                         f"ic3_simple_checker_{index}.inv")

    def _run_ic3(self, verilog_file_path:str,
                top_module_name:str,
                clock_name:str,
                reset_name:str,
                time_out:int = -1,
                index:int = 0,
                delete_failed_aag:bool = True,
                delete_failed_log:bool = True,
                delete_failed_inv:bool = True):
        """run ic3 simple checker"""
    
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.santiy_check_not_empty_str(top_module_name)
        sanity_check.santiy_check_not_empty_str(clock_name)
        sanity_check.santiy_check_not_empty_str(reset_name)

        if index != 0:
            self._aag_file_path = \
            os.path.join(self._ic3_folder_path, 
                         f"ic3_simple_checker_{index}.aag")
            self._ic3_check_log_file_path = os.path.join(self._ic3_folder_path, 
                         f"ic3_simple_checker_{index}.log")
            self._ic3_invariant_path = os.path.join(self._ic3_folder_path,
                         f"ic3_simple_checker_{index}.inv")

        yosys_formal_instance = yosys_formal.yosys_formal_execution(
            cmd_list=[
                f"read -sv {verilog_file_path}",
                f"prep -top {top_module_name}",
                "flatten",
                "memory -nordff",
                "setundef -undriven -init -expose",
                f"sim -clock {clock_name} -reset {reset_name}"+\
                f" -rstlen 1 "+\
                f" -n 1 -w {top_module_name}",
                "delete -output",
                "techmap",
                "abc -fast -g AND",
                f"write_aiger -ascii -symbols -zinit {self._aag_file_path}"
            ],
            debug_log="yosys_formal.log"
        )
        ret_code = yosys_formal_instance.execute()
        if ret_code != 0:
            print_warning_info("yosys formal compile failed")
            return -1, 0
        print_info("ic3 simple start")
        verbose_str = "-v" if self._is_verbose else ""
        print_statistic_str = "-s" if self._is_print_statistic else ""
        invariant_str = f"-d {self._ic3_invariant_path}"
        time_out_str = f"-t {time_out}" if time_out != -1 else ""

        cmd_str = f"cat {self._aag_file_path} |"+\
            f" IC3 {verbose_str} {print_statistic_str} {invariant_str} {time_out_str}"+\
                f" > {self._ic3_check_log_file_path}"
        print_info("ic3 cmd_str: {}".format(cmd_str))
        start_time = time.time()
        return_code = os.system(cmd_str)
        end_time = time.time()
        ic3_execution_time = end_time - start_time
        print_info("ic3 simple execution time: {}".format(end_time - start_time))
        print_info("ic3 simple end")
        return_code = return_code >> 8
        if return_code != 1:
            print_info("ic3 simple check failed")
            if delete_failed_aag and os.path.exists(self._aag_file_path):
                os.remove(self._aag_file_path)
            if delete_failed_log and \
                os.path.exists(self._ic3_check_log_file_path):
                os.remove(self._ic3_check_log_file_path)
            if delete_failed_inv and os.path.exists(self._ic3_invariant_path):
                os.remove(self._ic3_invariant_path)
        else:
            print_info("ic3 simple check success")
            

        return return_code, ic3_execution_time
    
    def run_ic3(self, verilog_file_path:str,
                top_module_name:str,
                clock_name:str,
                reset_name:str,
                index:int = 0,
                time_out:int = -1,
                delete_failed_aag:bool = True,
                delete_failed_log:bool = True,
                delete_failed_inv:bool = True):
        return_code, ic3_execution_time = \
            self._run_ic3(verilog_file_path=verilog_file_path,
            top_module_name=top_module_name,
            clock_name=clock_name,
            reset_name=reset_name,
            index=index,
            time_out=time_out,
            delete_failed_aag=delete_failed_aag,
            delete_failed_log=delete_failed_log,
            delete_failed_inv=delete_failed_inv)
        
        sanity_check.sanity_check_type(return_code, int)
        print_info("return code = " + str(return_code))
        if return_code == 1:
            return "proved", ic3_execution_time
        elif return_code == 0:
            return "cex",ic3_execution_time
        else:
            return "error",ic3_execution_time
        
    def is_ic3_proved(self, ic3_result:str):
        sanity_check.santiy_check_not_empty_str(ic3_result)
        return ic3_result == "proved"
    
    def is_ic3_cex(self, ic3_result:str):
        sanity_check.santiy_check_not_empty_str(ic3_result)
        return ic3_result == "cex"
    
    def is_ic3_error(self, ic3_result:str):
        sanity_check.santiy_check_not_empty_str(ic3_result)
        return ic3_result == "error"