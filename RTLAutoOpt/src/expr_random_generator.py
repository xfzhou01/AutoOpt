

import sanity_check
import expr
import random
import re

def print_info(info_str):
    print("[INFO] [expr-random-generator] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [expr-random-generator] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [expr-random-generator] -- {}".format(info_str))

class expr_random_generator:
    def __init__(self,
                 var_dict:dict[str, int],
                 const_str_list:list[str],
                 layer_num:int = 4,
                 ):
        sanity_check.sanity_check_value_greater_or_equal_to_1(layer_num)
        sanity_check.sanity_check_dict_not_empty(var_dict)
        sanity_check.sanity_check_list_not_empty(const_str_list)
        self._layer_num = layer_num
        self._var_dict = var_dict
        self._const_str_list = const_str_list

        self._supported_binary_op_list = ["&&", "||",  "==", "!="]
        self._supported_unary_op_list = ["!"]

    def _generate_random_variable_name(self):
        # generate random variable name
        while True:
            var_name = random.choice(list(self._var_dict.keys()))
            if re.match("_\d+_", var_name) is  None:
                break
        return var_name
    
    def _generate_random_const_str(self):
        # generate random const str
        const_str = random.choice(self._const_str_list)
        return const_str

    def _generate_random_expr_layer(self, layer):
        # generate random expr with layer
        sanity_check.sanity_check_value_greater_or_equal_to_0(layer)
        # if layer > self._layer_num:
        #     print_err_info(f"layer {layer} > layer_num {self._layer_num}")
        #     raise ValueError()

        # tmp layer number = random.randint(0, self._layer_num)
        tmp_layer_num = random.randint(0, self._layer_num)
        if layer >= tmp_layer_num:
            var_name = self._generate_random_variable_name()
            const_name = self._generate_random_const_str()
            if random.choice([True, False]):
                return expr.expr(name=var_name)
            else:
                return expr.expr(name=var_name)
        else:
            op = random.choice(self._supported_binary_op_list +\
                    self._supported_unary_op_list)
            if op in self._supported_binary_op_list:
                left_expr = self._generate_random_expr_layer(layer + 1)
                right_expr = self._generate_random_expr_layer(layer + 1)
                return expr.expr(left_expr=left_expr, 
                                 right_expr=right_expr, op=op)
            elif op in self._supported_unary_op_list:
                left_expr = self._generate_random_expr_layer(layer + 1)
                return expr.expr(left_expr=left_expr, op=op)
            else:
                raise ValueError(f"unsupported op {op}")

    def get_random_expr(self):
        return self._generate_random_expr_layer(0)
    
    def get_random_expr_list(self, num):
        sanity_check.sanity_check_value_greater_or_equal_to_1(num)
        return [self.get_random_expr() for _ in range(num)]