
import sanity_check

def print_info(info_str):
    print("[INFO] [expr] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [expr] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [expr] -- {}".format(info_str))

class expr:
    binary_op_list = ["&&", "||", "+", "-", "*", "/",\
                       "%", "==", "!=", ">", "<", ">=", "<="]
    unary_op_list = ["!"]

    logical_op_list = ["&&", "||", "!"]
    compare_op_list = ["==", "!=", ">", "<", ">=", "<="]
    arith_op_list = ["+", "-", "*", "/", "%"]

    def __init__(self, 
                 name = None, 
                 left_expr = None,
                 right_expr= None,
                 op = None,
                 no_check = False):
        self._name = name
        self._left_expr = left_expr
        self._right_expr = right_expr
        self._op = op

        if not no_check:
            self._check()
    
    def get_name(self):
        return self._name
    
    def _is_op_binary(self):
        return self._op in self.binary_op_list
    
    def _is_op_unary(self):
        return self._op in self.unary_op_list

    def is_op_and(self):
        return self._op == "&&"
    
    def is_op_or(self):
        return self._op == "||"
    
    def is_op_not(self):
        return self._op == "!"
    
    def is_op_eq(self):
        return self._op == "=="
    
    def is_op_neq(self):
        return self._op == "!="

    def is_op_arith(self):
        return self._op in self.arith
    
    def is_op_logical(self):
        return self._op in self.logical_op_list
    
    def is_op_compare(self):
        return self._op in self.compare_op_list
    
    def is_expr_empty(self):
        return self._name is None and self._left_expr is None and\
            self._right_expr is None and self._op is None
    
    def is_left_expr_empty(self):
        return self._left_expr is None
    def is_right_expr_empty(self):
        return self._right_expr is None
    
    def _check(self):
        if self._name is not None:
            # constant / variable should not have left / right op
            sanity_check.sanity_check_is_none(self._left_expr)
            sanity_check.sanity_check_is_none(self._right_expr)
            sanity_check.sanity_check_is_none(self._op)
        if self._op is not None:
            sanity_check.sanity_check_is_none(self._name)
            if self._is_op_unary():
                # not op should not have right op
                sanity_check.sanity_check_is_none(self._right_expr)
            elif self._is_op_binary():
                # and / or op should have left and right op
                sanity_check.sanity_check_not_none(self._left_expr)
                sanity_check.sanity_check_not_none(self._right_expr)

    def _util_is_str_x_value(self, s):
        if not isinstance(s,str):
            return False
        return s == "x" or s == "X"
    
    def _util_is_str_z_value(self, s):
        if not isinstance(s,str):
            return False
        return s == "z" or s == "Z"

    def _cal_eval_expr_and(self, eval_result_left, eval_result_right):
        if self._util_is_str_x_value(eval_result_left):
            if eval_result_right == 0:
                return 0
            return "x"
        elif self._util_is_str_x_value(eval_result_right):
            if eval_result_left == 0:
                return 0
            return "x"
        elif self._util_is_str_z_value(eval_result_left):
            if eval_result_right == 0:
                return 0
            return "z"
        elif self._util_is_str_z_value(eval_result_right):
            if eval_result_left == 0:
                return 0
            return "z"
        return eval_result_left and eval_result_right
    
    def _cal_eval_expr_or(self, eval_result_left, eval_result_right):
        if self._util_is_str_x_value(eval_result_left):
            if eval_result_right == 1:
                return 1
            return "x"
        elif self._util_is_str_x_value(eval_result_right):
            if eval_result_left == 1:
                return 1
            return "x"
        elif self._util_is_str_z_value(eval_result_left):
            if eval_result_right == 1:
                return 1
            return "z"
        elif self._util_is_str_z_value(eval_result_right):
            if eval_result_left == 1:
                return 1
            return "z"
        return eval_result_left or eval_result_right
    
    def _cal_eval_expr_eq(self, eval_result_left, eval_result_right):
        if self._util_is_str_x_value(eval_result_left) or\
            self._util_is_str_x_value(eval_result_right):
            return "x"
        elif self._util_is_str_z_value(eval_result_left) or\
            self._util_is_str_z_value(eval_result_right):
            return "z"
        return eval_result_left == eval_result_right
    
    def _cal_eval_expr_neq(self, eval_result_left, eval_result_right):
        if self._util_is_str_x_value(eval_result_left) or\
            self._util_is_str_x_value(eval_result_right):
            return "x"
        elif self._util_is_str_z_value(eval_result_left) or\
            self._util_is_str_z_value(eval_result_right):
            return "z"
        return eval_result_left != eval_result_right
    
    def _cal_eval_expr_not(self, eval_result_left):
        if self._util_is_str_x_value(eval_result_left):
            return "x"
        elif self._util_is_str_z_value(eval_result_left):
            return "z"
        return not eval_result_left

    def _cal_eval_expr(self, data_dict:dict, is_print=False):
        sanity_check.sanity_check_dict_not_empty(data_dict)
        result = None
        if self._name is not None:
            if isinstance(self._name, int):
                result = int(self._name)
            elif self._name in data_dict:
                result_val = data_dict[self._name]
                if result_val.isdigit():
                    result = int(result_val)
                elif result_val == "x" or result_val == "X":
                    result = "x"
                elif result_val == "z" or result_val == "Z":
                    result = "z"
                else:    
                    raise ValueError(f"unknown value {result_val}")
            else:
                index_cnt = 0
                value_list = []
                while True:
                    name_with_index = f"{self._name}[{index_cnt}]"
                    if name_with_index not in data_dict:
                        break
                    value_list.append(data_dict[name_with_index])
                    index_cnt += 1
                # if value dict contains 'x' or 'z', return 'x' or 'z'
                if 'x' in value_list or 'X' in value_list:
                    result = "x"
                elif 'z' in value_list or 'Z' in value_list:
                    result = "z"
                elif len(value_list) > 0:
                    result = int("".join(value_list[::-1]), 2)
                else:
                    # for key in data_dict.keys():
                    #     print_err_info(f"key: {key} value: {data_dict[key]}")
                    raise ValueError(f"unknown var {self._name}")
        elif self._op is not None:
            if self._is_op_unary():
                if self.is_op_not():
                    # print_info(f"left expr: {self._left_expr} " +\
                    #            f"left expr val: {self._left_expr.cal_eval_expr(data_dict)}")
                    left_expr_val = self._left_expr.cal_eval_expr(data_dict,
                                                                is_print)
                    result = self._cal_eval_expr_not(left_expr_val)
                else:
                    raise ValueError(f"unknown unary op {self._op}")
            elif self._is_op_binary():
                left_expr_val = self._left_expr.cal_eval_expr(data_dict, 
                                                              is_print)
                right_expr_val = self._right_expr.cal_eval_expr(data_dict, 
                                                                is_print)
                if self.is_op_and():
                    result = self._cal_eval_expr_and(left_expr_val, right_expr_val)
                elif self.is_op_or():
                    result = self._cal_eval_expr_or(left_expr_val, right_expr_val)
                elif self.is_op_eq():
                    result = self._cal_eval_expr_eq(left_expr_val, right_expr_val)
                elif self.is_op_neq():
                    result = self._cal_eval_expr_neq(left_expr_val, right_expr_val)
                else:
                    raise ValueError(f"unknown binary op {self._op}")
        else:
            raise ValueError("unknown expr format")
        if is_print:
            print_info(f"expr: {self} --  eval result: {result}")
        return result
        
    def cal_eval_expr(self, data_dict:dict, is_print=False):
        eval_result = self._cal_eval_expr(data_dict, is_print)
        return eval_result
        
    def cal_score_expr(self, score_dict:dict):
        if self._name is not None:
            if self._name in score_dict:
                return score_dict[self._name]
            else:
                raise ValueError(f"unknown var {self._name}")
        elif self._op is not None:
            if self._is_op_unary():
                return self._left_expr.cal_score_expr(score_dict)
            elif self._is_op_binary():
                if self.is_op_and():
                    return self._left_expr.cal_score_expr(score_dict) +\
                        self._right_expr.cal_score_expr(score_dict)
                elif self.is_op_or():
                    return min(self._left_expr.cal_score_expr(score_dict),
                        self._right_expr.cal_score_expr(score_dict))
                elif self.is_op_eq():
                    return self._left_expr.cal_score_expr(score_dict) *\
                        self._right_expr.cal_score_expr(score_dict)
                elif self.is_op_neq():
                    return self._left_expr.cal_score_expr(score_dict) +\
                        self._right_expr.cal_score_expr(score_dict)
                else:
                    raise NotImplementedError(
                        f"unsupported binary op {self._op}")
        else:
            raise ValueError("unknown expr format")

    def __str__(self):
        if self._name is not None:
            return str(self._name)
        elif self._op is not None:
            if self._is_op_unary():
                return f"({self._op} {self._left_expr})"
            elif self._is_op_binary():
                return f"({self._left_expr} {self._op} {self._right_expr})"
        else:
            raise ValueError("unknown expr format")
        
    def is_expr_all_const(self):
        if self._name is not None:
            if isinstance(self._name, int) or self._name.isdigit():
                return True
            elif isinstance(self._name, str):
                return False
        elif self._op is not None:
            if self._is_op_unary():
                return self._left_expr.is_expr_all_const()
            elif self._is_op_binary():
                return self._left_expr.is_expr_all_const() and\
                    self._right_expr.is_expr_all_const()
            else:
                raise ValueError(f"unknown op {self._op}")
        else:
            raise ValueError("unknown expr format")
        
    def set_left_expr(self, left_expr, no_check = False):
        # the original left expr should be unmodified
        sanity_check.sanity_check_is_none(self._left_expr)
        sanity_check.sanity_check_type(left_expr, expr)
        self._left_expr = left_expr
        if not no_check:
            self._check()

    def set_right_expr(self, right_expr, no_check = False):
        # the original left expr should be unmodified
        sanity_check.sanity_check_is_none(self._right_expr)
        sanity_check.sanity_check_type(right_expr, expr)
        self._right_expr = right_expr
        if not no_check:
            self._check()
    
    def set_op(self, op, no_check = False):
        sanity_check.sanity_check_is_none(self._op)
        sanity_check.sanity_check_type(op, str)
        if op not in self.binary_op_list and\
            op not in self.unary_op_list:
            raise ValueError(f"unknown op {op}")
        self._op = op
        if not no_check:
            self._check()

    def set_name(self, name, no_check = False):
        sanity_check.sanity_check_is_none(self._name)
        if not (isinstance(name, str) or isinstance(name, int)):
            raise ValueError(f"unknown name {name} with unexpected type {type(name)}")
        self._name = name
        if not no_check:
            self._check()
    
    def get_op(self):
        return self._op
    
    def convert_DOT_to_dot(self):
        if self._name is not None:
            if isinstance(self._name, str):
                self._name = self._name.replace("____DOT____", ".")
            elif isinstance(self._name, int):
                pass
            else:
                raise ValueError(f"unknown name {self._name} with unexpected type {type(self._name)}")
        if self._left_expr is not None:
            self._left_expr.convert_DOT_to_dot()
        if self._right_expr is not None:
            self._right_expr.convert_DOT_to_dot()
            