
import sys
import os
import time
import re

import pyverilog
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import sanity_check


def print_err_info(info_str):
    print("[ERROR] [graph-constructor] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [graph-constructor] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [graph-constructor] -- {}".format(info_str))

class full_dfg_constructor:

    def __init__(self) -> None:
        self.node_cnt = 0
        self.hash_to_node = dict()
        self.signal_name_to_hash = dict()
        self.node_to_dict_scope_chain = dict()
        self.hash_to_is_reg = dict()

        self.constant_zero_node = []
        self.constant_one_node = []

        self.var_name_to_width = dict()
        
        self.aig_obj = None
        self.debugging = False

    def set_aig_obj(self, aig_obj):
        self.aig_obj = aig_obj

    def dfg_add_node(self, bind_dict, full_dfg, n):
        if hash(n) not in full_dfg.nodes():
            is_reg_n = self.is_node_reg_node(bind_dict=bind_dict, n=n)
            fill_color_n = "white"
            if is_reg_n:
                fill_color_n = "red"
            full_dfg.add_node(hash(n), label = n, 
                              is_reg = is_reg_n, 
                              fillcolor = fill_color_n, style = "filled")
            if self.debugging is True:
                print_info("add node: {}".format(n))
                print_info("\t add node hash: {}".format(hash(n)))
            self.hash_to_node[hash(n)] = n
            self.node_cnt += 1
            self.signal_name_to_hash[str(n)] = hash(n)

            if str(n) == "1'b0":
                self.constant_zero_node.append(hash(n))
            
            if str(n) == "0":
                self.constant_zero_node.append(hash(n))

            if str(n) == "1'b1":
                self.constant_one_node.append(hash(n))

            if str(n) == "1":
                self.constant_one_node.append(hash(n))
            
            self.hash_to_is_reg[hash(n)] = is_reg_n
    
    def dfg_add_edge(self, full_dfg, fn, tn):
        if not full_dfg.has_edge(hash(fn),hash(tn)):
            full_dfg.add_edge(hash(fn),hash(tn))
            if self.debugging is True:
                print_info("add edge: {} ----> {}".format(fn,tn))
                print_info("\t add edge hash: {} ----> {}".format(hash(fn),hash(tn)))
            
    def construct_dfg_node(self, bind_dict, full_dfg, n):
        self.dfg_add_node(full_dfg=full_dfg, bind_dict=bind_dict, n=n)
        
        if "DFTerminal" in str(type(n)) or "ScopeChain" in str(type(n)):
            return

        for c in n.children():
            self.dfg_add_node(full_dfg=full_dfg, bind_dict=bind_dict, n=c)
            self.dfg_add_edge(full_dfg, c, n)
            self.construct_dfg_node(full_dfg=full_dfg, bind_dict=bind_dict, n=c)

    def get_term_width_all(self, terms, full_dfg):

        const_value_name_to_int_number = dict()
        # get the int value of all int constants
        while True:
            prev_len = len(const_value_name_to_int_number)
            for n in full_dfg.nodes(data=True):
                if full_dfg.in_degree(n[0]) == 1:
                    pn0_l = list(full_dfg.predecessors(n[0]))
                    pn0 = pn0_l[0]
                    pn0_str = str(full_dfg.nodes[pn0]["label"])
                    if "'" in pn0_str:
                        base_map = {"b": 2, "d": 10, "h": 16}
                        _,  base_number = pn0_str.split("'")
                        base = base_number[0]
                        number = base_number[1:]
                        
                        if not number.isdigit():
                            # all the characters in number str should be x or z
                            if not (all([_ == "x" or _ == "z" for _ in number])):
                                print_err_info(f"expect the value to be x|z, "+\
                                               f"but got {number}")
                                raise ValueError()

                        if number.isdigit():
                            v = int(number, base_map[base.lower()])
                        else:
                            v = number
                        const_value_name_to_int_number[str(n[1]["label"])] = v
                    if pn0_str.isdigit():
                        const_value_name_to_int_number[str(n[1]["label"])] = int(pn0_str)

                    if pn0_str in const_value_name_to_int_number:
                        const_value_name_to_int_number[str(n[1]["label"])] = const_value_name_to_int_number[pn0_str]
            if prev_len == len(const_value_name_to_int_number):
                break

        for t in terms.values():
            # print_info(t)
            if t is not None:
                is_msb_int_const = isinstance(t.msb, pyverilog.dataflow.dataflow.DFIntConst) 
                is_lsb_int_const = isinstance(t.lsb, pyverilog.dataflow.dataflow.DFIntConst) 

                is_msb_terminal = isinstance(t.msb, pyverilog.dataflow.dataflow.DFTerminal) 
                is_lsb_terminal = isinstance(t.lsb, pyverilog.dataflow.dataflow.DFTerminal)

                is_msb_operator = isinstance(t.msb, pyverilog.dataflow.dataflow.DFOperator) 
                is_lsb_operator = isinstance(t.lsb, pyverilog.dataflow.dataflow.DFOperator) 
                
                if is_msb_int_const and is_lsb_int_const:
                    self.var_name_to_width[str(t)] = int(t.msb.value) - int(t.lsb.value) + 1
                    continue
                if is_msb_int_const and is_lsb_terminal:
                    w = int(t.msb.value) - const_value_name_to_int_number[t.lsb] + 1
                    assert(w >= 1)
                    self.var_name_to_width[str(t)] = w
                    continue
                if is_msb_terminal and is_lsb_int_const:
                    print()
                    w = const_value_name_to_int_number[str(t.msb)] - int(t.lsb.value) + 1
                    assert(w >= 1)
                    self.var_name_to_width[str(t)] = w
                    continue
                
                msb_v = None
                lsb_v = None

                if is_msb_operator:
                    assert(str(t.msb) == "Minus")
                    # print(type(t.msb))
                    # mp = list(full_dfg.predecessors(hash(t.msb)))
                    # assert(len(mp) == 2)
                    # mp_0_n = full_dfg.nodes[mp[0]]["label"]
                    # mp_1_n = full_dfg.nodes[mp[1]]["label"]
                    mp_0_n = t.msb.children()[0]
                    mp_1_n = t.msb.children()[1]
                    try:
                        sanity_check.sanity_check_type(mp_0_n,
                            pyverilog.dataflow.dataflow.DFTerminal)
                        sanity_check.sanity_check_type(mp_1_n,
                            pyverilog.dataflow.dataflow.DFIntConst)
                    except Exception as e:
                        print_err_info(f"mp_0_n = {mp_0_n}; mp_1_n = {mp_1_n}")
                        raise e
                    msb_v = const_value_name_to_int_number[str(mp_0_n)] - int(mp_1_n.value)
                    assert(msb_v is not None)

                if is_lsb_operator:
                    # most of the times lsb = 0
                    assert(False)
                lsb_v = 0
                w = msb_v - lsb_v + 1
                self.var_name_to_width[str(t)] = w
                    

    def construct_full_dfg(self, bind_dict, terms):
        start_time = time.time()
        full_dfg = nx.DiGraph()
        for bk, bv in sorted(bind_dict.items(), key=lambda x: str(x[0])):
            self.dfg_add_node(full_dfg=full_dfg, bind_dict=bind_dict, n=bk)
            for bv_i in bv:
                t = bv_i.tree
                self.dfg_add_node(full_dfg=full_dfg, bind_dict=bind_dict, n=t)
                self.dfg_add_edge(full_dfg, t, bk)
                self.construct_dfg_node(full_dfg=full_dfg, bind_dict=bind_dict, n=t)
        end_time = time.time()
        print_info("construct full dfg from dataflow takes time: {} Seconds".format(end_time-start_time))
        print_info("full dfg statistic: {}".format(full_dfg))


        print_info("start generation term width")
        self.get_term_width_all(terms=terms, full_dfg=full_dfg)
        # for n in full_dfg.nodes(data=True):
        #     if str(n[1]["label"]) in self.var_name_to_width:
        #         w = self.var_name_to_width[str(n[1]["label"])]
        #         full_dfg.nodes[n[0]]["width"] = w
        # 
        # print("[INFO] finished data width analyze")
        return full_dfg
    
    def dump_nodes_information(self, full_dfg):
        for n_hs in full_dfg.nodes():
            print("node: {}".format(self.hash_to_node[n_hs]))
    
    
    def is_node_reg_node(self, bind_dict, n):
        
        # print("[INFO] is node reg node working on {} with type {}".format(n, type(n)))
        clock_name = [".clk", ".ap_clk", ".clock"]
        if not (type(n) == pyverilog.dataflow.dataflow.DFTerminal or type(n) == pyverilog.utils.scope.ScopeChain):
            return False

        bind_obj = []
        for bd_key in bind_dict.keys():
            if str(bd_key) == str(n):
                bind_obj = bind_dict[bd_key]
                break

        if len(bind_obj) == 0:
            # print("[WARNING] the bind obj have zero length when judge is reg, current node: {}".format(n))
            return False
        for clk_n in clock_name:
            if clk_n in str(bind_obj[0].getClockName()):
                print_info(f"detected as register: {n}")
                return True
        if self.aig_obj is not None:
            if self.aig_obj is None:
                print_err_info("the aig obj is None")
                raise ValueError()
            if self.aig_obj.get_is_latch(name=".".join(str(n).split(".")[1:])):
                print_info(f"detected as register: {n}")
                return True
        else:
            print_warning_info("cannot find an aig for judgement of reg")
        
        # print("[INFO] not detected as register: {}, clk name is: {}".format(n, str(bind_obj[0].getClockName())))
        return False
    
    def is_node_reg_hash(self, bind_dict, hn):
        return self.is_node_reg_node(bind_dict=bind_dict, n=self.hash_to_node[hn])