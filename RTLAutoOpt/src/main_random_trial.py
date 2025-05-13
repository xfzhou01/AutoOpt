

import sanity_check
import os
import argparse
import verilog_expr_optimizer
import verilog_abstractor
import verilog_syntax_rewriter
import verilog_tb_generator
import iverilog
import time
import waveform_parser
import expr_random_generator
import expr_filter
import expr_formal_checker
from tqdm import tqdm 
import sys

def print_info(info_str):
    print("[INFO] [random-trial-main] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [random-trial-main] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [random-trial-main] -- {}".format(info_str))


def get_parser():
    parser = argparse.ArgumentParser(description="verilog expr optimizer")
    parser.add_argument("--FILE", type=str, required=True,
                        help="The path to the input verilog file")
    parser.add_argument("--TOP", type=str, required=True,
                        help="The top module name")
    return parser



def main():
    parser = get_parser()
    args = parser.parse_args()

    output_verilog_file_path = "opt_expr_output.v"
    abstracted_verilog_file_path = "abstracted_output.v"
    tb_file_path = "tb.v"

    # Optimize the expressions
    optimizer = verilog_expr_optimizer.verilog_expr_optimizer(
        verilog_file_path=args.FILE,
        top_module_name=args.TOP,
        output_verilog_file_path=output_verilog_file_path
    )
    optimizer.launch_opt()

    # abstract the optimized verilog file
    abstractor = verilog_abstractor.verilog_abstractor(
        verilog_file_path=output_verilog_file_path,
        top_module_name=args.TOP
    )
    abstractor.write_abstracted_ast_to_verilog_file(
        abstracted_verilog_file_path
    )

    # Rewrite the syntax
    rewriter = verilog_syntax_rewriter.verilog_syntax_rewriter(
        verilog_file_path=abstracted_verilog_file_path,
    )
    rewriter.write_rewrited_verilog(abstracted_verilog_file_path)

    # Generate the testbench
    tb_generator = verilog_tb_generator.verilog_tb_generator(
        verilog_file_path=abstracted_verilog_file_path,
        top_module_name=args.TOP,
        test_bench_file_path=tb_file_path,
        clock_signal_name="ap_clk",
        reset_signal_name="ap_rst",
        cycle_num=1000
    )
    
    # Simulate the testbench
    iverilog_inst = iverilog.iverilog(
        top_module_name=args.TOP,
        tb_top_module_name=tb_generator.get_tb_top_name(),
        verilog_file_path=abstracted_verilog_file_path,
        tb_file_path=tb_file_path,
        compiled_file_name="a.out"
    )
    compile_ret_code = iverilog_inst.run_compile()
    if compile_ret_code != 0:
        print_err_info("iverilog compile failed")
        exit(1)
    iverilog_inst.run_sim()

    # parse the waveform
    signal_output_file_path = tb_generator.get_signal_output_file_path()
    waveform_parser_inst = waveform_parser.waveform_parser(signal_output_file_path)
    waveform_bit_level_data = waveform_parser_inst.get_bit_level_data()
    waveform_bit_level_variable = waveform_parser_inst.get_bit_level_signal_name_list()

    # randomly generate the assertions
    print_info("random assertion generation start")
    # var_dict = {rn:d["width"] for rn, 
    #             d in rewriter.get_variable_dict().items()}
    var_dict = {rn:1 for rn in waveform_bit_level_variable}

    # heuristicly
    # -- hard to filter out, need a co-design of filtering and candidate generation
    # owing to heuristics, miss the invariant hard to catch
    # remove the nosiy invariant
    # 1147 clauses
    # left the ones speed up verification
    # hybrid (heruistic + random)
    random_gen = expr_random_generator.expr_random_generator(
        var_dict=var_dict,
        const_str_list=[0,1],
        layer_num=3
    )

    expr_random_gen_list = random_gen.get_random_expr_list(
        num=1000000
    )
    print_info("random assertion generation done")


    # filter the assertions
    # 1M candidate
    # if the candidtae violate the sim. result, then filter it
    # to what extend the filtering is better.
    # 1M --> ic3_simple_checker_636.aag
    # iteratively run the sim until converge
    expr_filter_inst = expr_filter.expr_filter()
    expr_filter_inst.set_waveform_list(waveform_bit_level_data)
    filtered_expr_list = expr_filter_inst.filter_expr_list(
        expr_random_gen_list)


    # formally check the filtered assertions
    expr_fc = expr_formal_checker.expr_formal_checker(
        verilog_file_path=abstracted_verilog_file_path,
        top_module_name=args.TOP,
        clk_name="ap_clk",
        rst_name="ap_rst",
        ic3_timeout=100
    )

    

    expr_correct_count = 0
    formal_check_index = 0
    for expr in tqdm(filtered_expr_list, desc="Processing", file=sys.stderr):
        is_correct = expr_fc.check_expr(expr, formal_check_index)
        formal_check_index += 1
        if is_correct:
            print_info(f"assertion passed formal: {expr}")
            expr_correct_count += 1
        else:
            print_warning_info(f"assertion failed: {expr}")
        
    print(f"correct assertion count: {expr_correct_count}", file=sys.stderr)
    print(f"total assertion count: {len(filtered_expr_list)}", file=sys.stderr)
    print("filtering done", file=sys.stderr)
    


if __name__ == "__main__":
    main()