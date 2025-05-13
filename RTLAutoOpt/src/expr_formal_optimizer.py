

import sanity_check

import os
import expr_formal_checker

def print_info(info_str):
    print("[INFO] [expr-formal-optimizer] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [expr-formal-optimizer] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [expr-formal-optimizer] -- {}".format(info_str))


class expr_formal_optimizer:
    def __init__(self, verilog_file_path:str,
                 top_module_name:str,
                 clk_name:str,
                 rst_name:str):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.santiy_check_not_empty_str(top_module_name)
        sanity_check.santiy_check_not_empty_str(clk_name)
        sanity_check.santiy_check_not_empty_str(rst_name)
        self._top_module_name = top_module_name
        self._clk_name = clk_name
        self._rst_name = rst_name
        self._verilog_file_path = verilog_file_path
        self._expr_list = []
        self._filtered_expr_list = []
        self._expr_formal_checker_instance =\
              expr_formal_checker.expr_formal_checker(
            verilog_file_path=verilog_file_path,
            top_module_name=self._top_module_name,
            clk_name=self._clk_name,
            rst_name=self._rst_name
        )

    def optimize_expr_list(self):
        """optimize expr_list"""

    def _verify_and_filter_expr_list(self):
        """verify and filter expr_list"""
        if len(self._expr_list) == 0:
            print_warning_info("expr_list is empty")
            return
        
        # filter expr_list
        index = 0
        for expr in self._expr_list:
            check_result = self._expr_formal_checker_instance.check_expr(expr,index)
            index += 1
            if check_result:
                self._filtered_expr_list.append(expr)
        
        # 
    
    def set_expr_list(self, expr_list):
        self._expr_list = expr_list.copy()

    