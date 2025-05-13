import verilog_abstractor
import verilog_expr_optimizer
import verilog_tb_generator

import argparse
import iverilog
import verilog_syntax_rewriter

def print_err_info(info_str):
    print("[ERROR] [main] -- {}".format(info_str))

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
        reset_signal_name="ap_rst"
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

if __name__ == "__main__":
    main()