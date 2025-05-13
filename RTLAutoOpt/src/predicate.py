
import sanity_check
import re
import expr

def print_info(info_str):
    print("[INFO] [predicate] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [predicate] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [predicate] -- {}".format(info_str))

class predicate:

    def __init__(self, expr_obj:expr.expr):
        sanity_check.sanity_check_not_none(expr_obj)
        self._expr_obj = expr_obj
        self._expr_obj:expr.expr

        self._check()

        self._cal_eval_predicate()
        self._cal_score_predicate()

    def _check(self):
        if not (self._expr_obj.is_op_logical() or self._expr_obj.is_op_compare()):
            raise ValueError(f"predicate should be logical or cmp op,"+\
                             f" but got {self._expr_obj.__str__()}")

    def _cal_eval_predicate(self, data_dict:dict):
        return self._expr_obj.cal_eval_expr(data_dict)

    def _cal_score_predicate(self, score_dict:dict):
        return self._expr_obj.cal_score_expr(score_dict)

    def __str__(self):
        return self._expr_obj.__str__()