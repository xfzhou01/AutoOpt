import sanity_check
import graph_refine
import graph_constructor
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import networkx as nx
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Assign, Identifier, IntConst
import copy
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from networkx.drawing.nx_pydot import write_dot
import time
import pyverilog.vparser.ast as vast




def print_err_info(info_str):
    print("[ERROR] [verilog-abstractor] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [verilog-abstractor] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [verilog-abstractor] -- {}".format(info_str))

def is_under_unit_test():
    return __name__ == "__main__"




class verilog_abstractor:

    def __init__(self, verilog_file_path, top_module_name):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.santiy_check_not_empty_str(top_module_name)
        self._top_module_name = top_module_name
        self._verilog_file_path = verilog_file_path
        self._full_dfg = None
        self._full_dfg_constructor = None
        self._verilog_ast = None
        self._construct_and_refine_full_dfg()
        
        self.debug_write_full_dfg_to_dot("fft.dot")

        self._verilog_ast:vast.Source

        sanity_check.sanity_check_not_none(self._full_dfg)
        sanity_check.sanity_check_not_none(self._full_dfg_constructor)
        sanity_check.sanity_check_not_none(self._verilog_ast)
        
        self._verilog_ast_in_progress = None
        self._reset_ast()

        # record the original content before abstraction for abstracted signals
        self._signal_abstract_record_in_progress = dict()

        # threshold
        self._add_abstraction_threshold = 8
        self._mul_abstraction_threshold = 4
        self._sub_abstraction_threshold = 8
        self._div_abstraction_threshold = 1
    
    def _dfs_node_and_replace_to_x(self, 
                                   node, 
                                   replace_set, 
                                   replace_all_r_val=False,
                                   replace_set_backup_to_check=None):
        """replace node to `x` for abstraction
        - the replacement is conducted to node with type: 
        `vast.Assign` or `vast.NonblockingSubstitution`
        - if the l-value of node (`node.left.var`) is found in `replace_set`,
        the corresponding r-value (`node.right.var`) is replaced

        Args:
            node (vast.Node): the root node to be replaced, \
            as it is a recursive function, \
            the caller should make it the root node of ast 
            replace_set (set[str]): set of node names that should be replaced
            replace_all_r_val (bool, optional): whether should replace all, if \
            True should happen in debug mode (unit test) only. \
            Defaults to False.
            replace_set_backup_to_check (set|None): the set to check

        Raises:
            PermissionError: the debug flag is set in non-debug mode
        """     
        if isinstance(node, vast.Assign) or\
              isinstance(node, vast.NonblockingSubstitution):
            left_var_name = str(node.left.var)
            if replace_all_r_val:
                if not is_under_unit_test():
                    print_err_info("the all replace is only permitted under"+\
                                   " unit test")
                    raise PermissionError()
                node.right.var = IntConst("1024'bx")
            else:
                if left_var_name in replace_set:
                    if replace_set_backup_to_check is not None:
                        replace_set_backup_to_check.remove(left_var_name)
                    print_info(f"abstract signal: {left_var_name}")
                    node.right.var = IntConst("1024'bx")
        for c in node.children():
            self._dfs_node_and_replace_to_x(c, 
                                            replace_set, 
                                            replace_all_r_val,
                                            replace_set_backup_to_check)

    def _reset_ast(self):
        """reset `_signal_abstract_record_in_progress` and
        `_verilog_ast_in_progress` (this will create one copy of ast)
        """        
        self._signal_abstract_record_in_progress = dict()
        self._verilog_ast_in_progress = copy.deepcopy(self._verilog_ast)

    def _util_deep_equal(self, ast1, ast2):
        sanity_check.sanity_check_not_none(ast1)
        sanity_check.sanity_check_not_none(ast2)
        return copy.deepcopy(ast1) == copy.deepcopy(ast2)


    def _construct_and_refine_full_dfg(self):
        start_time = time.time()
        filelist = [self._verilog_file_path]
        analyzer = VerilogDataflowAnalyzer(filelist, 
                                           self._top_module_name,
                                           noreorder=False,
                                           nobind=False)
        analyzer.generate()
        ast, directives = parse(filelist=filelist)
        binddict = analyzer.getBinddict()
        terms = analyzer.getTerms()
        instances = analyzer.getInstances()
        signals = analyzer.getSignals()
        ft = analyzer.getFrameTable()
        fdc = graph_constructor.full_dfg_constructor()
        full_dfg = fdc.construct_full_dfg(bind_dict=binddict, terms=terms)
        graph_refine.refine_full_dfg_reset(full_dfg, fdc)

        self._full_dfg = full_dfg
        self._full_dfg_constructor = fdc
        self._verilog_ast = ast

        end_time = time.time()
        print_info(f"construct and refine full dfg takes"+\
                   f" {end_time - start_time} seconds")

    def _find_node_hash_given_signal_name(self, signal_name:str):
        """given signal name, find node hash

        Args:
            signal_name (str): the signal name

        Returns:
            int: hash of node with corresponding signal name
        """        
        sanity_check.santiy_check_not_empty_str(signal_name)
        return self._full_dfg_constructor.signal_name_to_hash[signal_name]
    
    def _find_width_given_signal_name(self, signal_name:str):
        """given signal name, find node width

        Args:
            signal_name (str): the signal name

        Returns:
            int: the width of node
        """        
        sanity_check.santiy_check_not_empty_str(signal_name)
        try:
            return self._full_dfg_constructor.var_name_to_width[signal_name]
        except KeyError as e:
            print_err_info(f"fail to find width for var: {signal_name}")
            print_err_info(f"the variable name to width dict content:")
            for vn, w in self._full_dfg_constructor.var_name_to_width:
                print_err_info(f"-- {vn} : {w}")
            raise e
    
    def _find_signal_name_given_node(self, node_hash:int):
        """given node hash, find signal name

        Args:
            node_hash (int): the node hash

        Returns:
            str: the name of signal
        """        
        sanity_check.sanity_check_type(node_hash, int)
        try:
            return str(self._full_dfg.nodes[node_hash]["label"])
        except KeyError as ke:
            print_info(f"cannot find attr `label` in node,"+\
                       f" node_hash = {node_hash},"+\
                       f" attr = {self._full_dfg[node_hash]}")
            raise ke
    


    def _abstract_target_signal_set(self, signal_name_set:set[str]):
        """abstract away the signals in signal name set away from working ast
        `_verilog_ast_in_progress`. It will maintain the dict: 
        `_signal_abstract_record_in_progress` to record the original right item
        of abstracted signals

        Args:
            signal_name_set (set[str]): the signal names that are required to be
            abstracted away
        Raises:
            ValueError: fail to abstract some of the signals
        """     
        sanity_check.sanity_check_not_none(self._verilog_ast_in_progress)
        if not self._util_deep_equal(ast1=self._verilog_ast_in_progress,
                                     ast2=self._verilog_ast):
            print_warning_info("try to abstract from a modified ast")
        if len(signal_name_set) == 0:
            print_warning_info("nothing to abstracted")
            return
        
        signal_name_set_backup = signal_name_set.copy()   
        # for item in self._verilog_ast.children():
        #     print_info(item)
        #     if isinstance(item, Assign):
        #         if isinstance(item.left, Identifier) and\
        #               item.left.name in signal_name_set:
        #             self._signal_abstract_record_in_progress[item.left.name] =\
        #                   item.right
        #             item.right = IntConst('x')  
        #             signal_name_set_backup.remove(item.left.name)

        print_info("signal_name_set_backup: " + str(signal_name_set_backup))
        self._dfs_node_and_replace_to_x(node=self._verilog_ast_in_progress,
            replace_set=signal_name_set, replace_all_r_val=False,
            replace_set_backup_to_check=signal_name_set_backup
        )




        # do check
        if len(signal_name_set_backup) != 0:
            for failed_signal_names in signal_name_set_backup:
                print_err_info(f"the signal: {failed_signal_names} " +\
                               "can not find a corresponding item to remove "+\
                                "in ast")
                self.debug_print_all_stuffs_in_ast(self._verilog_ast_in_progress)
            raise ValueError()
        
    def _recover_target_signal_set(self, signal_name_set:set[str]):
        """recover the abstracted signal in signal name set into the working 
        ast `_verilog_ast_in_progress`.  It will maintain the dict: 
        `_signal_abstract_record_in_progress` to delete the original right item
        of abstracted signals, if the signal is recovered.

        Args:
            signal_name_set (set[str]):the signal names that are required to be
            recovered

        Raises:
            ValueError: the signal provided is not abstracted away
            ValueError: fail to recover the signal in ast
        """        
        sanity_check.sanity_check_not_none(self._verilog_ast_in_progress)
        if not isinstance(signal_name_set, set):
            signal_name_set = set(signal_name_set)
        if len(signal_name_set) == 0:
            print_warning_info("nothing to abstracted")
            return

        signal_name_set_backup = signal_name_set.copy()   
        signal_abstract_record = self._signal_abstract_record_in_progress

        # do sanity check
        for signal_name in signal_name_set:
            if signal_name not in self._signal_abstract_record_in_progress:
                print_err_info(f"cannot find signal: {signal_name} to be"+\
                               " recovered in "+\
                                "`_signal_abstract_record_in_progress` "+\
                                "whose content is shown as follows:"+\
                                f"{self._signal_abstract_record_in_progress}")
                raise ValueError()
        
        # operate
        # for item in self._verilog_ast.children():
        #     if isinstance(item, Assign):
        #         if isinstance(item.left, Identifier) and\
        #               item.left.name in signal_name_set:
        #             item.right = signal_abstract_record[item.left.name]
        #             signal_abstract_record.pop(item.left.name)
        #             signal_name_set_backup.remove(item.left.name)

        # self._dfs_node_and_replace_to_x(node=self._verilog_ast_in_progress,
        #                                 replace_set=signal_name_set)

        # do sanity check
        if len(signal_name_set_backup) != 0:
            for failed_signal_names in signal_name_set_backup:
                print_err_info(f"the signal: {failed_signal_names} " +\
                               "can not find a corresponding item to remove "+\
                                "in ast")
            raise ValueError()
        
    def _is_node_arithmetic(self, node):
        """whether the given dfg node represents an arithmetic operation

        Args:
            node (int): hash value of node
        """        
        signal_name_node = self._find_signal_name_given_node(node_hash=node)
        return signal_name_node == "Plus" or \
            signal_name_node == "Minus" or \
            signal_name_node == "Divide" or \
            signal_name_node == "Times"

    def _find_all_arithmetic_nodes(self):
        return [n for n in self._full_dfg if self._is_node_arithmetic(n)]
    
    def _find_result_signal_name_of_arithmetic_node(self, a_node):
        """get the result signal name of an arithmetic operation,
        for example, in verilog code `assign res = a + b`, the arithmetic 
        node will be `Plus`, this function is targeted to find the result 
        node with name `res`

        Args:
            a_node (int): the hash of node

        Raises:
            ValueError: the node is not arithmetic
            ValueError: node have multiple successors
        """     
        # check   
        if is_under_unit_test():
            if not self._is_node_arithmetic(a_node):
                print_err_info(f"expected the node to be arithmetic but got"+\
                               f" {self._find_signal_name_given_node(a_node)}")
                raise ValueError()
        a_node_successors = list(self._full_dfg.successors(a_node))

        # check
        if not len(a_node_successors) == 1:
            if len(a_node_successors) == 0:
                print_err_info(f"the node "+\
                               f"{self._find_signal_name_given_node(a_node)}"+\
                                "does not have any successors")
            else:
                print_err_info(f"the node "+\
                               f"{self._find_signal_name_given_node(a_node)}"+\
                                "have multiple successors: ")
                for a_node_successor in a_node_successors:
                    print_err_info(f"-- "+\
                    f"{self._find_signal_name_given_node(a_node_successor)}")
            raise ValueError()
        
        result_signal_name_with_top =\
            self._find_signal_name_given_node(a_node_successors[0])
        if result_signal_name_with_top.startswith(f"{self._top_module_name}."):
            result_signal_name_with_top = result_signal_name_with_top[
                len(f"{self._top_module_name}."):]
        return result_signal_name_with_top
    
    def _is_node_constant(self, node):
        """judge whether a node is a constant

        Args:
            node (int): the node hash
        """        
        return self._util_is_string_verilog_constant(
            verilog_name=self._find_signal_name_given_node(node)
        )

    def _util_is_string_verilog_constant(self, verilog_name:str):
        """whether a verilog name is a constant or not like `3'd1`

        Args:
            verilog_name (str): the verilog name in verilog string
        """        
        sanity_check.santiy_check_not_empty_str(verilog_name)
        return "'d" in verilog_name or "'b" in verilog_name or\
              verilog_name.isdigit()
    
    def _is_arithmetic_node_has_constant_operand(self, a_node):
        if not self._is_node_arithmetic(a_node):
            print_err_info(f"expected the node "+\
                           f"{self._find_signal_name_given_node(a_node)}"+\
                           f" to be arithmetic")
            raise ValueError()
        
        a_node_predecessors = list(self._full_dfg.predecessors(a_node))
        for predecessor_node in a_node_predecessors:
            if self._is_node_constant(predecessor_node):
                return True
        return False
    
    def _util_is_node_name_variable_name(self, node_name:str):
        """judge whether a string of node name represents an variable, 
        such as `const_example.\\adder_inst.c`

        Args:
            node_name (str): the node name in string
        """        
        sanity_check.sanity_check_type(node_name, str)
        return "." in node_name and\
            node_name.startswith(f"{self._top_module_name}.")
    
    def _find_arithmetic_node_operand_width(self, a_node):
        """for an arithmetic node, find the node operand width

        Args:
            a_node (int): the node hash for an arithmetic node

        Raises:
            ValueError: raises when the node does not have a direct predecessor
            of variable name 

        Returns:
            dict: the key is variable name, the value is width
        """        
        a_node_predecessor_list = self._full_dfg.predecessors(a_node)
        name_list = [self._find_signal_name_given_node(n) \
                     for n in a_node_predecessor_list]
        width_dict = {name : self._find_width_given_signal_name(name) \
                      for name in name_list \
                      if self._util_is_node_name_variable_name(name)}
        
        if len(width_dict) == 0:
            n = a_node
            print_err_info(f"the node {self._find_signal_name_given_node(n)}"+\
                           f" does not have an variable predecessor, node id"+\
                           f" {a_node}")
            raise NotImplementedError()
        return width_dict
    
    def _is_arithmetic_node_add(self, a_node):
        signal_name_node = self._find_signal_name_given_node(node_hash=a_node)
        return signal_name_node == "Plus"
    
    def _is_arithmetic_node_sub(self, a_node):
        signal_name_node = self._find_signal_name_given_node(node_hash=a_node)
        return signal_name_node == "Minus"
    
    def _is_arithmetic_node_mul(self, a_node):
        signal_name_node = self._find_signal_name_given_node(node_hash=a_node)
        return signal_name_node == "Divide"
    
    def _is_arithmetic_node_div(self, a_node):
        signal_name_node = self._find_signal_name_given_node(node_hash=a_node)
        return signal_name_node == "Times"

    def _is_arithmetic_node_abstracted_initial(self, a_node):
        """judge whether a node should be abstracted in the initial round of
        optimization iteration. 
        The nodes to be abstracted out: 
        - width > width threshold

        Args:
            node (int): the hash of a node to be judged
        """        
        if not self._is_node_arithmetic(a_node):
            return False
        if self._is_arithmetic_node_has_constant_operand(a_node):
            return False
        width_dict = self._find_arithmetic_node_operand_width(a_node)
        for variable_name, width in width_dict.items():
            if self._is_arithmetic_node_add(a_node):
                return width > self._add_abstraction_threshold
            elif self._is_arithmetic_node_sub(a_node):
                return width > self._sub_abstraction_threshold
            elif self._is_arithmetic_node_mul(a_node):
                return width > self._mul_abstraction_threshold
            elif self._is_arithmetic_node_div(a_node):
                return width > self._div_abstraction_threshold
        return True

    def _util_node_signal_name_to_verilog_name(self, node_name:str):
        """convert node name to verilog name (remove top modules)
        . for example, `const_example.\\adder_inst.c` -> 
        `\\adder_inst.`

        Args:
            node_name (str): the input node name

        Raises:
            ValueError: the node name is too short 

        Returns:
            str: the verilog name
        """        
        if (not len(node_name) > len(self._top_module_name) + 1) or\
           (not node_name.startswith(f"{self._top_module_name}.")):
            print_err_info(f"received an node name that cannot convert to" +\
                           f"verilog name, node name = {node_name}")
            raise ValueError()
        return node_name[len(self._top_module_name)+1]

    def _find_signals_to_be_abstracted_initial(self):
        """in the initial iteration, find signal to be abstracted
        """        
        initial_abstract_signal_name_set = set()
        arithmetic_nodes = self._find_all_arithmetic_nodes()
        for a_node in arithmetic_nodes:
            if self._is_arithmetic_node_abstracted_initial(a_node):
                rn = self._find_result_signal_name_of_arithmetic_node(a_node)
                initial_abstract_signal_name_set.add(rn)
        return initial_abstract_signal_name_set

    # public:

    def debug_all_rvalues_replace_with_x(self):
        """for debug use only: 
        replace all R-values of assignments and `=` in always blocks
        in to `x` signal for abstraction test
        """        
        self._reset_ast()
        self._dfs_node_and_replace_to_x(node=self._verilog_ast_in_progress,
                                        replace_all_r_val=True,
                                        replace_set={})
        
    def debug_print_all_stuffs_in_ast(self, ast_to_dump):
        print_info("start dump ast information")
        def dfs_debug_print(node):
            print_info(f"node type: {type(node)}; node: {node}")
            for n in node.children():
                dfs_debug_print(n)

        dfs_debug_print(ast_to_dump)

    def debug_dump_signal_names_to_stdout(self):
        signal_name_list = [self._find_signal_name_given_node(node_hash)\
                             for node_hash in self._full_dfg]
        for signal_name in signal_name_list:
            print_info(signal_name)

    def debug_write_full_dfg_to_dot(self, dot_file_path):
        sanity_check.sanity_check_str_postfix(dot_file_path, ".dot")
        write_dot(self._full_dfg, dot_file_path)

    def set_add_abstraction_threshold(self, add_abstraction_threshold):
        sanity_check.sanity_check_value_greater_or_equal_to_1(
            add_abstraction_threshold)
        self._add_abstraction_threshold = add_abstraction_threshold

    def set_sub_abstraction_threshold(self, sub_abstraction_threshold):
        sanity_check.sanity_check_value_greater_or_equal_to_1(
            sub_abstraction_threshold)
        self._sub_abstraction_threshold = sub_abstraction_threshold

    def set_mul_abstraction_threshold(self, mul_abstraction_threshold):
        sanity_check.sanity_check_value_greater_or_equal_to_1(
            mul_abstraction_threshold)
        self._mul_abstraction_threshold = mul_abstraction_threshold

    def set_div_abstraction_threshold(self, div_abstraction_threshold):
        sanity_check.sanity_check_value_greater_or_equal_to_1(
            div_abstraction_threshold)
        self._div_abstraction_threshold = div_abstraction_threshold

    def get_add_abstraction_threshold(self):
        return self._add_abstraction_threshold
    
    def get_sub_abstraction_threshold(self):
        return self._sub_abstraction_threshold
    
    def get_mul_abstraction_threshold(self):
        return self._mul_abstraction_threshold
    
    def get_div_abstraction_threshold(self):
        return self._div_abstraction_threshold

    def get_number_of_abstracted_signals(self):
        return len(self._signal_abstract_record_in_progress)
    
    def initial_abstraction(self):
        print_info("start initial abstraction")
        print_info(f"-- add width threshold: {self._add_abstraction_threshold}")
        print_info(f"-- sub width threshold: {self._sub_abstraction_threshold}")
        print_info(f"-- mul width threshold: {self._mul_abstraction_threshold}")
        print_info(f"-- div width threshold: {self._div_abstraction_threshold}")


        start_time = time.time()
        sg_name_set = self._find_signals_to_be_abstracted_initial()
        self._abstract_target_signal_set(sg_name_set)
        end_time = time.time()
        print_info(f"finish initial abstraction, takes {end_time-start_time}"+\
                   " seconds")
    
    def write_abstracted_ast_to_verilog_file(self, abstracted_file_path:str):
        """write the `_verilog_ast_in_progress` into verilog file

        Args:
            abstracted_file_path (str): the abstracted file to be written into
        """        
        sanity_check.santiy_check_not_empty_str(abstracted_file_path)
        codegen = ASTCodeGenerator()
        new_verilog_code = codegen.visit(self._verilog_ast_in_progress)
        with open(abstracted_file_path, 'w') as f:
            f.write(new_verilog_code)
        print_info(f"the abstraction result have been written into file"+\
                   f" {abstracted_file_path}")

    
    
# test
import argparse
def get_parser():
    parser = argparse.ArgumentParser(description="verilog expr optimizer")
    parser.add_argument("--FILE", type=str, help="the input file",
                        required=True)
    parser.add_argument("--TOP", type=str, help="the top function name",
                        required=True)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    a = verilog_abstractor(verilog_file_path=args.FILE,
                           top_module_name=args.TOP)
    a.debug_write_full_dfg_to_dot(f"{args.TOP}.dot")
    a.debug_dump_signal_names_to_stdout()
    #a.debug_all_rvalues_replace_with_x()
    #a.write_abstracted_ast_to_verilog_file(abstracted_file_path="abstracted_x.v")
    a.initial_abstraction()
    a.write_abstracted_ast_to_verilog_file(abstracted_file_path="abstracted_x_1.v")
    
if __name__ == "__main__":
    main()