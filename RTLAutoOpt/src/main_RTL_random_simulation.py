

import iverilog
import os
import verilog_tb_generator
import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        description="RTL random simulation script for Verilog modules."
    )
    parser.add_argument(
        "--TOP",
        type=str,
        help="Top module name for the simulation.",
        required=True
    )
    parser.add_argument(
        "--FILE",
        type=str,
        help="Verilog file to be simulated.",
        required=True
    )
    return parser



def main():
    parser = get_parser()
    args = parser.parse_args()
    top_module = args.TOP
    file_path = args.FILE
    tb_file_path = f"{top_module}_tb.v"
    signal_output_file = f"{top_module}_signal_output.vcd"

    tb_gen_inst = verilog_tb_generator.verilog_tb_generator(
        verilog_file_path=file_path,
        top_module_name=top_module,
        test_bench_file_path=tb_file_path,
        clock_signal_name="ap_clk",
        reset_signal_name="ap_rst",
        cycle_num=10000,
        signal_output_file=signal_output_file,
        is_dump_txt=False,
        is_dump_vcd=True
    )
    tb_top_module = tb_gen_inst.get_tb_top_name()
    
    iverilog_inst = iverilog.iverilog(
        compiled_file_name="a.out",
        top_module_name=top_module,
        tb_top_module_name=tb_top_module,
        verilog_file_path=file_path,
        tb_file_path=tb_file_path
    )
    iverilog_inst.run_compile()
    iverilog_inst.run_sim()


if __name__ == "__main__":
    # Run the main function
    main()