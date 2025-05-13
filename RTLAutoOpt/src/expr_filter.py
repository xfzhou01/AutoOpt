
import sanity_check
import expr
import re
from tqdm import tqdm
import sys

def print_err_info(info_str):
    print("[ERROR] [expr-filter] -- {}".format(info_str))
def print_info(info_str):
    print("[INFO] [expr-filter] -- {}".format(info_str))
def print_warning_info(info_str):
    print("[WARNING] [expr-filter] -- {}".format(info_str))


class expr_filter:
    def __init__(self):
        self._waveform_list = []
    
    def _filter_expr_list(self, expr_list:list[expr.expr]):

        statistics = {
            "total_expr_num": len(expr_list),
            "filtered_expr_num": 0,
            "expr_not_logical_num": 0,
            "expr_not_correct_num": 0,
            "kept_expr_num": 0,
            "expr_const_num": 0
        }

        sanity_check.sanity_check_list_not_empty(expr_list)
        filtered_expr_list = []
        
        for expr_obj in tqdm(expr_list, desc="Processing", file=sys.stderr):
            expr_obj:expr.expr
            expr_obj_success = True
            # if not expr_obj.is_op_logical():
            #     statistics["expr_not_logical_num"] += 1
            #     statistics["filtered_expr_num"] += 1
            #     continue
            if expr_obj.is_expr_all_const():
                statistics["filtered_expr_num"] += 1
                statistics["expr_const_num"] += 1
                continue
            for timestamp_waveform in self._waveform_list:
                timestamp_waveform:dict
                # print_info(expr_obj.cal_eval_expr(data_dict=timestamp_waveform))
                eval_expr_value = expr_obj.cal_eval_expr(data_dict=timestamp_waveform)
                if eval_expr_value != 1:
                    expr_obj_success = False
                    statistics["expr_not_correct_num"] += 1
                    statistics["filtered_expr_num"] += 1
                    break
            if expr_obj_success:    
                filtered_expr_list.append(expr_obj)
        # print statistics
        statistics["kept_expr_num"] = len(filtered_expr_list)
        print_info("filter expr statistics:")
        for key, value in statistics.items():
            print_info(f"{key}: {value}")

        # for expr_obj in filtered_expr_list:
        #     for timestamp_waveform in self._waveform_list:
        #         print_info(f"kept expr: {expr_obj.cal_eval_expr(data_dict=timestamp_waveform,is_print=True)}")
        #     exit()
        return filtered_expr_list

    # public
    def add_waveform_timestamp(self, waveform:dict):
        sanity_check.sanity_check_dict_not_empty(waveform)
        self._waveform_list.append(waveform)

    def set_waveform_list(self, waveform_list:list[dict]):
        sanity_check.sanity_check_list_not_empty(waveform_list)
        self._waveform_list = waveform_list

    def filter_expr_list(self, expr_list:list[expr.expr]):
        return self._filter_expr_list(expr_list)


    