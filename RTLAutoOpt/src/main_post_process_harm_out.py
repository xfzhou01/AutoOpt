import argparse
import expr_formal_checker
import sanity_check
import harm_post_processer
import os
import re
from tqdm import tqdm
import verilog_tb_generator
import iverilog
import waveform_parser
import expr_filter
import str_to_expr_parser

def get_parser():
    parser = argparse.ArgumentParser(
        description="prove HARM assertion with ic3"
    )
    parser.add_argument(
        "--FILE",
        type=str,
        required=True,
        help="verilog file path"
    )
    parser.add_argument(
        "--TOP",
        type=str,
        required=True,
        help="top module name"
    )
    parser.add_argument(
        "--A",
        type=str,
        required=True,
        help="assertion file path"
    )
    return parser

def print_info(info_str):
    print("[INFO] [main-post-process-harm-out] -- {}".format(info_str))
def print_warning_info(info_str):
    print("[WARNING] [main-post-process-harm-out] -- {}".format(info_str))
def print_err_info(info_str):
    print("[ERROR] [main-post-process-harm-out] -- {}".format(info_str))

def main():
    parser = get_parser()
    args = parser.parse_args()
    verilog_file_path = args.FILE
    top_module_name = args.TOP
    assertion_file_path = args.A

    clock_name = "ap_clk"
    rst_name = "ap_rst"

    hpp_instance = harm_post_processer.harm_post_processor(
        harm_assertion_file_path=assertion_file_path
    )
    hpp_instance.write_to_file()
    standardized_assertion_file_path = hpp_instance.get_std_file_path()
    print("standardized assertion file path: {}".format(
        standardized_assertion_file_path))

    # read the standardized assertion file line by line into a list
    assertion_expr_list = []
    with open(standardized_assertion_file_path, "r") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            assertion_expr_list.append(line)
    print_info("number of assertions: {}".format(
        len(assertion_expr_list)))
    
    exit()

    # convert assertion str to expr
    assertion_expr_list = [
        str_to_expr_parser.str_to_expr_parser().parse(expr_str=expr_str)
        for expr_str in assertion_expr_list
    ]
    assertion_expr_list = [expr for expr in assertion_expr_list
                            if expr is not None]

    # filter the assertion expr list with simulation result
    tb_file_path = "tb.v"
    # Generate the testbench, by default
    # the signal result will written to txt file
    tb_generator = verilog_tb_generator.verilog_tb_generator(
        verilog_file_path=verilog_file_path,
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
        verilog_file_path=verilog_file_path,
        tb_file_path=tb_file_path,
        compiled_file_name="a.out"
    )
    compile_ret_code = iverilog_inst.run_compile()
    if compile_ret_code != 0:
        print_err_info("iverilog compile failed")
        exit(1)
    iverilog_inst.run_sim()

    # filter the assertion expr list with simulation result
    signal_output_file_path = tb_generator.get_signal_output_file_path()
    waveform_parser_inst = waveform_parser.waveform_parser(signal_output_file_path)
    waveform_bit_level_data = waveform_parser_inst.get_bit_level_data()
    waveform_bit_level_variable = waveform_parser_inst.get_bit_level_signal_name_list()
    expr_filter_inst = expr_filter.expr_filter()
    expr_filter_inst.set_waveform_list(waveform_bit_level_data)
    filtered_expr_list = expr_filter_inst.filter_expr_list(
        assertion_expr_list)

    efc_instance = expr_formal_checker.expr_formal_checker(
        verilog_file_path=verilog_file_path,
        top_module_name=top_module_name,
        clk_name=clock_name,
        rst_name=rst_name,
        ic3_timeout=1000
    )


    for i in tqdm(range(len(filtered_expr_list)), desc="Checking expressions"):
        efc_instance.check_expr(expr=filtered_expr_list[i], index=i)
    print("expr check finished")

if __name__ == "__main__":
    main()