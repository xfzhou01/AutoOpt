
import sys
import os
import time
import re

import pyverilog
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import networkx as nx
import matplotlib.pyplot as plt
import itertools
'''
    remove all reset nodes
'''
def refine_full_dfg_reset(full_dfg, fdc):
    start_time = time.time()

    reset_signal_names = ["ap_rst", "reset"]
    reset_signal_names_contain = ["." + _  for _ in reset_signal_names]
    reset_nodes = []
    for n in full_dfg.nodes(data=True):
        n_label = str(n[1]["label"])
        for rsn in reset_signal_names_contain:
            if rsn in n_label:
                reset_nodes.append(n)
                break
    
    if len(reset_nodes) == 0:
        print("[WARNING] cannot find reset node in the design")
    else:
        print("[INFO] find {} reset nodes in the design".format(len(reset_nodes)))
        print("[INFO] ---------- begin reset nodes list ----------")
        for _ in reset_nodes:
            print("[INFO]       {}".format(_[1]["label"]))
        print("[INFO] ---------- end   reset nodes list ----------")
    
    # find branchs
    # remove_node_list = [_[0] for _ in reset_nodes]
    # for rn in reset_nodes:
    #     eq_node_hs_list = list(full_dfg.successors(rn[0]))
    #     eq_node_hs_list_new = []
    #     for eq_node_hs_tmp in eq_node_hs_list:
    #         eq_node_tmp = fdc.hash_to_node[eq_node_hs_tmp]
    #         eq_node_tmp_label = str(eq_node_tmp)
    #         is_rst = False
    #         for rsn in reset_signal_names_contain:
    #             if rsn in eq_node_tmp_label:
    #                 is_rst = True
    #                 break
    #         if is_rst is False:
    #             eq_node_hs_list_new.append(eq_node_hs_tmp)
        
    #     if len(eq_node_hs_list_new) != 1:
    #         print("")
    #         assert(False)

    #     assert(len(eq_node_hs_list_new) == 1)
    #     eq_node_hs = eq_node_hs_list_new[0]
    #     assert(str(fdc.hash_to_node[eq_node_hs]) == "Eq")
    #     remove_node_list.append(eq_node_hs)
    #     eq_succ_hs_list = list(full_dfg.successors(eq_node_hs))

    #     for eq_succ_hs in eq_succ_hs_list:
    #         eq_succ = fdc.hash_to_node[eq_succ_hs]
    #         eq_succ_label = str(eq_succ)
    #         assert(eq_succ_label == "Branch")
    #         remove_node_list.append(eq_succ_hs)

    #         # add edge to recover the connection
    #         p_list = list(full_dfg.predecessors(eq_succ_hs))
    #         assert(len(p_list) == 3)
    #         # [0]: True, [1]: Cond, [2]: False
    #         n_rst_node = p_list[2]
    #         normal_node_list = list(full_dfg.successors(eq_succ_hs))

    #         for normal_node in normal_node_list:
    #             full_dfg.add_edge(n_rst_node, normal_node)
    # print("[INFO] number of nodes to remove when reset {}".format(len(remove_node_list)))

    # for rm_n in remove_node_list:
    #     full_dfg.remove_node(rm_n)
    
    end_time = time.time()
    print("[INFO] refine_full_dfg_reset takes {} Seconds".format(end_time-start_time))



'''
should execute after rst opt
'''
def refine_full_dfg_fifo(full_dfg, fdc):
    print("[ERROR] this function is going to be fixed")
    exit(1)

