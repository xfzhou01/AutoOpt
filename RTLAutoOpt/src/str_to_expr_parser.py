import re
import ast
import sanity_check
import expr
import copy

def print_info(info_str):
    print("[INFO] [str-to-expr-parser] -- {}".format(info_str))
def print_error_info(info_str):
    print("[ERROR] [str-to-expr-parser] -- {}".format(info_str))
def print_warning_info(info_str):
    print("[WARNING] [str-to-expr-parser] -- {}".format(info_str))


is_debug = True if __name__ == "__main__" else False    

class ASTVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self._expr_from_assertion = expr.expr()
        self._should_add_left = dict()
        self._should_add_right = dict()
        self._expr_stack = []
        self._expr_stack.append(self._expr_from_assertion)


    def visit_ast_to_construct_expr(self, parsed_ast):
        self.visit(parsed_ast)
        return copy.deepcopy(self._expr_from_assertion)

    def _is_op_not(self, node):
        return type(node.op).__name__ == "Not"

    def _generate_op_str(self, node):
        return type(node.op).__name__

    def visit_Module(self, node):
        # print(f"Visiting Module: {node}")
        self.generic_visit(node)  

    def visit_Assign(self, node):
        raise NotImplementedError("Assign node is not supported")
        self.generic_visit(node)

    def visit_BinOp(self, node):
        raise NotImplementedError("BinOp node is not supported")
        print(f"Visiting binary op: {node.op} {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_Name(self, node):
        if is_debug:
            print_info(f"Visiting Name: {node.id}")
            print_info(f"current stack len: {len(self._expr_stack)}")

        self._expr_under_construction = self._expr_stack[-1]
        sanity_check.sanity_check_type(self._expr_under_construction, 
                                            expr.expr)
        self._expr_under_construction:expr.expr
        if self._expr_under_construction.is_expr_empty():
            self._expr_under_construction.set_name(str(node.id))
            self._should_add_left[self._expr_under_construction] = False
            self._should_add_right[self._expr_under_construction] = False
        else:
            expr_created = expr.expr(name=str(node.id))
            if self._should_add_left[self._expr_under_construction]:
                self._expr_under_construction.set_left_expr(
                    left_expr=expr_created, no_check=True)
                self._should_add_left[self._expr_under_construction] = False
            elif self._should_add_right[self._expr_under_construction]:
                self._expr_under_construction.set_right_expr(
                    right_expr=expr_created, no_check=True)
                self._should_add_right[self._expr_under_construction] = False
            else:
                raise ValueError("Unexpected state: neither left nor right operand is set.")
        
        # if not self._should_add_left[self._expr_under_construction] and \
        #     not self._should_add_right[self._expr_under_construction]:
        #     self._expr_stack.pop()

    def visit_Constant(self, node):
        if is_debug:
            print_info(f"Visiting Constant: {node.value}")
            print_info(f"current stack len: {len(self._expr_stack)}")
        self._expr_under_construction = self._expr_stack[-1]
        self._expr_under_construction:expr.expr
        if self._expr_under_construction.is_expr_empty():
            self._expr_under_construction.set_name(int(node.value))
            self._should_add_left[self._expr_under_construction] = False
            self._should_add_right[self._expr_under_construction] = False
        else:
            expr_created = expr.expr(name=int(node.value))
            if self._should_add_left[self._expr_under_construction]:
                self._expr_under_construction.set_left_expr(expr_created)
                self._should_add_left[self._expr_under_construction] = False
            elif self._should_add_right[self._expr_under_construction]:
                self._expr_under_construction.set_right_expr(expr_created)
                self._should_add_right[self._expr_under_construction] = False
            else:
                raise ValueError("Unexpected state: neither left nor right operand is set.")
            
        # if not self._should_add_left[self._expr_under_construction] and \
        #     not self._should_add_right[self._expr_under_construction]:
        #     if self._expr_under_construction == self._expr_stack[-1]:
        #         self._expr_stack.pop()

    def visit_UnaryOp(self, node):
        if is_debug:
            print_info(f"Visiting unary op: {node.op} {type(node.op).__name__}")
            print_info(f"current stack len: {len(self._expr_stack)}")
        len_stack_before = len(self._expr_stack)
        is_stack_push = False
        if self._is_op_not(node):
            self._expr_under_construction = self._expr_stack[-1]
            self._expr_under_construction:expr.expr
            if self._expr_under_construction.is_expr_empty():
                self._expr_under_construction.set_op(op="!", no_check=True)
                self._should_add_left[self._expr_under_construction] = True
                self._should_add_right[self._expr_under_construction] = False
            else:
                expr_created = expr.expr(op="!",no_check=True)
                self._should_add_left[expr_created] = True
                self._should_add_right[expr_created] = False
                self._expr_stack.append(expr_created)
                is_stack_push = True
                if self._should_add_left[self._expr_under_construction]:
                    self._expr_under_construction.set_left_expr(
                        left_expr=expr_created, no_check=True)
                    self._should_add_left[self._expr_under_construction] = False
                elif self._should_add_right[self._expr_under_construction]:
                    assert(not self._expr_under_construction.is_left_expr_empty())
                    self._expr_under_construction.set_right_expr(
                        right_expr=expr_created, no_check=True)
                    self._should_add_right[self._expr_under_construction] = False
                else:
                    print_error_info("expr under construction op: {}".format(
                        self._expr_under_construction.get_op()))
                    raise ValueError("Unexpected state: neither left nor right operand is set.")
        else:
            raise NotImplementedError("Other UnaryOp node is not supported: {}".format(type(node.op).__name__))
        
        self.generic_visit(node)
        if is_debug:
            print_info(f"stack len after: {len(self._expr_stack)}, stack before: {len_stack_before}")
        if is_stack_push:
            self._expr_stack.pop()
        # if not self._should_add_left[self._expr_under_construction] and \
        #     not self._should_add_right[self._expr_under_construction]:
        #     if self._expr_under_construction == self._expr_stack[-1]:
        #         self._expr_stack.pop()

    def visit_BoolOp(self, node):
        if is_debug:
            print_info(f"Visiting BoolOp: {node}")
            print_info(f"current stack len: {len(self._expr_stack)}")
        
        if len(node.values) > 2:
            left = node.values[0]
            right = ast.BoolOp(op=node.op, values=node.values[1:])
            new_node = ast.BoolOp(op=node.op, values=[left, right])
            self.visit(new_node)
            return
            
        
        is_stack_push = False
        len_stack_before = len(self._expr_stack)
        self._expr_under_construction = self._expr_stack[-1]
        self._expr_under_construction:expr.expr
        if self._expr_under_construction.is_expr_empty():
            if node.op.__class__.__name__ == "Or":
                self._expr_under_construction.set_op(op="||", no_check=True)
            elif node.op.__class__.__name__ == "And":
                self._expr_under_construction.set_op(op="&&", no_check=True)
            else:
                raise NotImplementedError("Only Or and And are supported")
            self._should_add_left[self._expr_under_construction] = True
            self._should_add_right[self._expr_under_construction] = True
        else:
            if node.op.__class__.__name__ == "Or":
                expr_created = expr.expr(op="||",no_check=True)
            elif node.op.__class__.__name__ == "And":
                expr_created = expr.expr(op="&&",no_check=True)
            else:
                raise NotImplementedError("Only Or and And are supported")
            self._should_add_left[expr_created] = True
            self._should_add_right[expr_created] = True
            self._expr_stack.append(expr_created)
            is_stack_push = True
            
            if self._should_add_left[self._expr_under_construction]:
                self._expr_under_construction.set_left_expr(
                    left_expr=expr_created, no_check=True)
                self._should_add_left[self._expr_under_construction] = False
            elif self._should_add_right[self._expr_under_construction]:
                assert(not self._expr_under_construction.is_left_expr_empty())
                self._expr_under_construction.set_right_expr(
                    right_expr=expr_created, no_check=True)
                self._should_add_right[self._expr_under_construction] = False
            else:
                print_info("expr under construction op: {}".format(
                    self._expr_under_construction.get_op()))
                print_info("expr under construction: {}".format(
                    self._expr_under_construction.__str__()))
                print_info("left expr: {}".format(self._expr_under_construction._left_expr))
                print_info("right expr: {}".format(self._expr_under_construction._right_expr))
                raise ValueError("Unexpected state: neither left nor right operand is set.")

        self.generic_visit(node)
        if is_debug:
            print_info(f"stack len after: {len(self._expr_stack)}, stack before: {len_stack_before}")
        # if not (len(self._expr_stack) == len_stack_before):
        #     for _ in self._expr_stack:
        #         print_error_info("stack expr: {}".format(_))
        #     raise ValueError()
        # if not self._should_add_left[self._expr_under_construction] and \
        #     not self._should_add_right[self._expr_under_construction]:
        #     if self._expr_under_construction == self._expr_stack[-1]:
        if is_stack_push:
            self._expr_stack.pop()

    def visit_Or(self, node):
        self.generic_visit(node)

    def visit_And(self, node):
        self.generic_visit(node)

    def visit_Compare(self, node):
        if is_debug:
            print_info(f"Visiting Compare: {node}")
            print_info(f"current stack len: {len(self._expr_stack)}")
        is_stack_push = False
        len_stack_before = len(self._expr_stack)
        self._expr_under_construction = self._expr_stack[-1]
        self._expr_under_construction:expr.expr
        if self._expr_under_construction.is_expr_empty():
            if len(node.ops) != 1:
                raise NotImplementedError("Only one comparison is supported")
            if node.ops[0].__class__.__name__ == "Eq":
                self._expr_under_construction.set_op("==",no_check=True)
            elif node.ops[0].__class__.__name__ == "NotEq":
                self._expr_under_construction.set_op("!=",no_check=True)
            else:
                raise NotImplementedError("Only == and != are supported")
            self._should_add_left[self._expr_under_construction] = True
            self._should_add_right[self._expr_under_construction] = True
        else:
            if len(node.ops) != 1:
                raise NotImplementedError("Only one comparison is supported")
            if node.ops[0].__class__.__name__ == "Eq":
                expr_created = expr.expr(op="==",no_check=True)
            elif node.ops[0].__class__.__name__ == "NotEq":
                expr_created = expr.expr(op="!=",no_check=True)
            else:
                raise NotImplementedError("Only == and != are supported")
            self._should_add_left[expr_created] = True
            self._should_add_right[expr_created] = True
            self._expr_stack.append(expr_created)
            is_stack_push = True
            if self._should_add_left[self._expr_under_construction]:
                self._expr_under_construction.set_left_expr(
                    left_expr=expr_created, no_check=True)
                self._should_add_left[self._expr_under_construction] = False
            elif self._should_add_right[self._expr_under_construction]:
                assert(not self._expr_under_construction.is_left_expr_empty())
                self._expr_under_construction.set_right_expr(
                    right_expr=expr_created, no_check=True)
                self._should_add_right[self._expr_under_construction] = False
            else:
                print_error_info("expr under construction: {}".format(
                    self._expr_under_construction.__str__()))
                print_error_info("operation: {}".format(
                    self._expr_under_construction.get_op()))
                raise ValueError("Unexpected state: neither left nor right operand is set.")

        self.generic_visit(node)
        if is_debug:
            print_info(f"stack len after: {len(self._expr_stack)}, stack before: {len_stack_before}")
        if is_stack_push:
            self._expr_stack.pop()

    def visit_Eq(self, node):
        self.generic_visit(node)

    def visit_NotEq(self, node):
        self.generic_visit(node)

    def visit_Subscript(self, node):
        if is_debug:
            print_info(f"Visiting Subscript: {node.value.id}, {node.slice.value}")
            print_info(f"current stack len: {len(self._expr_stack)}")
            

        self._expr_under_construction = self._expr_stack[-1]
        sanity_check.sanity_check_type(self._expr_under_construction, 
                                            expr.expr)
        self._expr_under_construction:expr.expr
        if is_debug:
            print_info("expr under construction op: {}".format(self._expr_under_construction.get_op()))
        if self._expr_under_construction.is_expr_empty():
            self._expr_under_construction.set_name(
                f"{node.value.id}[{node.slice.value}]", no_check=True)
            self._should_add_left[self._expr_under_construction] = False
            self._should_add_right[self._expr_under_construction] = False
        else:
            expr_created = expr.expr(
                name=f"{node.value.id}[{node.slice.value}]", no_check=True)
            if self._should_add_left[self._expr_under_construction]:
                self._expr_under_construction.set_left_expr(
                    left_expr=expr_created, no_check=True)
                self._should_add_left[self._expr_under_construction] = False
            elif self._should_add_right[self._expr_under_construction]:
                self._expr_under_construction.set_right_expr(
                    right_expr=expr_created, no_check=True)
                self._should_add_right[self._expr_under_construction] = False
            else:
                raise ValueError("Unexpected state: neither left nor right operand is set.")

    
class str_to_expr_parser:
    def __init__(self):
        pass

    def _santilize_expr(self, expr_str:str):
        expr_str = expr_str.replace("(!)||", "")
        return expr_str.strip()
    
    def _standardize_operand(self, expr_str:str):
        sanity_check.santiy_check_not_empty_str(expr_str)
        expr_str = expr_str.replace(".", "____DOT____")
        expr_str = expr_str.replace("||", " or ")
        expr_str = expr_str.replace("&&", " and ")
        expr_str = expr_str.replace("!", " not ")
        expr_str = expr_str.replace("not =", " != ")
        expr_str = expr_str.replace("~", " not ")
        return expr_str.strip()
    
    def _standardize_expr(self, expr_str:str):

        pass

    def _do_parse(self, expr_str):
        sanity_check.santiy_check_not_empty_str(expr_str)
        expr_str = self._santilize_expr(expr_str)
        expr_str_std = self._standardize_operand(expr_str)
        try:
            parsed = ast.parse(expr_str_std)
        except SyntaxError as e:
            return None
            print_error_info("Error in parsing expression: {}".format(expr_str))
            print_error_info("Standardized expression: {}".format(expr_str_std))
            print_error_info("Error message: {}".format(e))
            raise e
        # print(ast.dump(parsed, indent=4))
        try:
            return ASTVisitor().visit_ast_to_construct_expr(parsed)
        except ValueError as e:
            print_error_info("Error in parsing expression: {}".format(expr_str))
            print_error_info(ast.dump(parsed, indent=4))
            raise e
        except NotImplementedError as nie:
            return None
    
    def parse(self, expr_str):
        e = self._do_parse(expr_str)
        if e is None:
            return None
        e.convert_DOT_to_dot()
        return e


# Example usage
def main():
    expression = "((B_d1[350] && fifo_C_drain_C_drain_IO_L1_out_1_1_dout[14]) != (! (C_d0[215] && B_PE_dummy_in_U0_ap_done)))"
    expression = " ~((grp_ss_sort_fu_78.trunc_ln86_6_fu_765_p1 == 0)||((grp_ss_sort_fu_78.bucket_addr_32_reg_2113 == 0)))"
    expression = "~((!(grp_ss_sort_fu_78.bucket_addr_18_reg_1951 == 0))||((grp_ss_sort_fu_78.bucket_addr_10_reg_1940 == 1)))"
    expression = "~(((!ap_idle && !grp_ss_sort_fu_78.tmp_reg_1773 && grp_ss_sort_fu_78.bucket_addr_39_reg_2193 == 1))||((ap_NS_fsm == 2)))"
    expr_obj = str_to_expr_parser().parse(expression)
    print_info("expression: "+expression)
    print_info("result: "+expr_obj.__str__())
    # parsed = ast.parse(expression)
    # visitor = ASTVisitor()
    # visitor.visit(parsed)
    # print(parsed)
    # print(ast.dump(parsed, indent=4))


if __name__ == "__main__":
    main()
