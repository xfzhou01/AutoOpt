
import sanity_check
import os
import yosys_formal
import ic3_simple
import verilog_assertion_adder

def print_info(info_str):
    print("[INFO] [expr-formal-checker] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [expr-formal-checker] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [expr-formal-checker] -- {}".format(info_str))

class expr_formal_checker:
    def __init__(self, verilog_file_path:str,
                 top_module_name:str,
                 clk_name:str,
                 rst_name:str,
                 ic3_timeout:int = 1000,
                 too_easy_assertion_file_path:str = "too_easy_assertion.txt",
                 moderate_assertion_file_path:str = "moderate_assertion.txt",
                 too_hard_assertion_file_path:str = "too_hard_assertion.txt"):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.santiy_check_not_empty_str(top_module_name)
        sanity_check.santiy_check_not_empty_str(clk_name)
        sanity_check.santiy_check_not_empty_str(rst_name)
        sanity_check.sanity_check_type(ic3_timeout, int)
        sanity_check.sanity_check_value_greater_or_equal_to_1(ic3_timeout)

        sanity_check.santiy_check_not_empty_str(
            too_easy_assertion_file_path)
        sanity_check.santiy_check_not_empty_str(
            moderate_assertion_file_path)
        sanity_check.santiy_check_not_empty_str(
            too_hard_assertion_file_path)

        self._top_module_name = top_module_name
        self._clk_name = clk_name
        self._rst_name = rst_name
        self._verilog_file_path = verilog_file_path
        self._ic3_timeout = ic3_timeout
        self._ic3_instance = ic3_simple.ic3_simple_checker(
            is_verbose=True, is_print_statistic=True
        )
        self._verilog_assertion_adder = \
            verilog_assertion_adder.verilog_assertion_adder(
                verilog_file_path=self._verilog_file_path,
                top_module_name=self._top_module_name, 
                clock_name=self._clk_name
            )
        self._output_verilog_file_path = "expr_check.v"
        self._too_easy_assertion_file_path = too_easy_assertion_file_path
        self._moderate_assertion_file_path = moderate_assertion_file_path
        self._too_hard_assertion_file_path = too_hard_assertion_file_path

        self._easy_assertion_threshold = 100
        self._moderate_assertion_threshold = 600


    def check_expr(self, expr, index):
        """check expr with ic3"""
        self._verilog_assertion_adder.set_assertion_expr_list(
            [expr])
        
        self._verilog_assertion_adder.write_to_file(
            output_file_path=self._output_verilog_file_path
        )
        ic3_result, ic3_execution_time = self._ic3_instance.run_ic3(
            verilog_file_path=self._output_verilog_file_path,
            top_module_name=self._top_module_name,
            clock_name=self._clk_name,
            reset_name=self._rst_name,
            index=index,
            time_out=self._ic3_timeout,
            delete_failed_aag=True,
            delete_failed_inv=True,
            delete_failed_log=True
        )

        is_proved = self._ic3_instance.is_ic3_proved(ic3_result)
        is_unkown = self._ic3_instance.is_ic3_error(ic3_result)
        is_failed = self._ic3_instance.is_ic3_cex(ic3_result)

        if is_proved:
            if ic3_execution_time < self._moderate_assertion_threshold and\
                  ic3_execution_time > self._easy_assertion_threshold:
                # append the expr into moderate assertion file thtough writing
                with open(self._moderate_assertion_file_path, "a") as f:
                    f.write(expr.__str__() + f" $${ic3_execution_time}\n")
            elif ic3_execution_time <= self._easy_assertion_threshold:
                # append the expr into too easy assertion file thtough writing
                with open(self._too_easy_assertion_file_path, "a") as f:
                    f.write(expr.__str__() + f" $${ic3_execution_time}\n")
            else:
                # append the expr into too hard assertion file thtough writing
                with open(self._too_hard_assertion_file_path, "a") as f:
                    f.write(expr.__str__() + f" $${ic3_execution_time}\n")
        elif is_failed:
            print_warning_info(f"assertion failed: {expr}")
        elif is_unkown:
            print_warning_info(f"assertion unknown: {expr}")
            if ic3_execution_time > 10:
                with open(self._too_hard_assertion_file_path, "a") as f:
                    f.write(expr.__str__() + f" $${ic3_execution_time}\n")
        return is_proved
    

    def set_easy_assertion_threshold(self, threshold:int):
        sanity_check.sanity_check_value_greater_or_equal_to_1(threshold)
        self._easy_assertion_threshold = threshold
        print_info("easy assertion threshold set to {}".format(threshold))

    def set_moderate_assertion_threshold(self, threshold:int):
        sanity_check.sanity_check_value_greater_or_equal_to_1(threshold)
        self._moderate_assertion_threshold = threshold
        print_info("moderate assertion threshold set to {}".format(threshold))

    def get_verification_verilog_file_path(self):
        return self._output_verilog_file_path