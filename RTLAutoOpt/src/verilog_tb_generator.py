import sanity_check
import os
import time
import re
import argparse
import vcd_variable_name_reader
import iverilog
def print_info(info_str):
    print("[INFO] [verilog-tb-generator] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [verilog-tb-generator] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [verilog-tb-generator] -- {}".format(info_str))

class verilog_tb_generator:
    def __init__(self, 
                 verilog_file_path, top_module_name, 
                 test_bench_file_path,
                 clock_signal_name="clk", reset_signal_name="rst",
                 signal_output_file="signals_output.txt",
                 cycle_num=1000,
                 is_dump_vcd = False,
                 is_dump_txt = True):
        sanity_check.sanity_check_is_file_exist(verilog_file_path)
        sanity_check.sanity_check_file_postfix(verilog_file_path, ".v")
        sanity_check.santiy_check_not_empty_str(top_module_name)
        sanity_check.santiy_check_not_empty_str(test_bench_file_path)
        sanity_check.santiy_check_not_empty_str(clock_signal_name)
        sanity_check.santiy_check_not_empty_str(reset_signal_name)
        sanity_check.santiy_check_not_empty_str(signal_output_file)
        sanity_check.sanity_check_type(cycle_num, int)
        sanity_check.sanity_check_value_greater_or_equal_to_0(cycle_num)
        sanity_check.sanity_check_type(is_dump_vcd, bool)
        sanity_check.sanity_check_type(is_dump_txt, bool)
        sanity_check.sanity_check_onehot_exclude_all_zero([is_dump_txt, 
                                                           is_dump_vcd])
        self._is_dump_vcd = is_dump_vcd
        self._is_dump_txt = is_dump_txt
        self._verilog_file_path = verilog_file_path
        self._top_module_name = top_module_name
        self._test_bench_file_path = test_bench_file_path
        self._clock_signal_name = clock_signal_name
        self._reset_signal_name = reset_signal_name
        self._cycle_num = cycle_num

        self._tb_top_name = f"{self._top_module_name}_tb"
        self._vcd_dump_file_name = f"{self._tb_top_name}.vcd" if \
            self._is_dump_vcd else None

        self._observe_signal_dict = dict()
        self._signal_output_file = signal_output_file

        self._port_info_input, self._port_info_output = \
            self._extract_top_module_information()

        self._vcd_dump_file_name_for_signal_extraction = \
            "__signal_extraction__.vcd"
        
        self._observe_signal_dict = \
            self._launch_vcd_simulation_and_get_signal()


        if not self._clock_signal_name in self._port_info_input:
            print_err_info(f"The clock signal {self._clock_signal_name} "+\
                               "is not in the input ports")
            raise ValueError()
        if not self._reset_signal_name in self._port_info_input:
            print_err_info(f"The reset signal {self._reset_signal_name} "+\
                               "is not in the input ports")
            raise ValueError()
        
        print_info(f"Initialized verilog_tb_generator with:")
        print_info(f"  Verilog file path: {verilog_file_path}")
        print_info(f"  Top module name: {top_module_name}")
        print_info(f"  Test bench file path: {test_bench_file_path}")
        print_info(f"  Clock signal name: {clock_signal_name}")
        print_info(f"  Reset signal name: {reset_signal_name}")
        print_info(f"  Signal output file: {signal_output_file}")
        print_info(f"  Cycle number: {cycle_num}")

        print_info("start to generate the test bench file")
        self._generate_test_bench_file()

    def _launch_vcd_simulation_and_get_signal(self):
        """launch the simulation and get the signal values
        """
        # self._vcd_dump_file_name = f"{self._tb_top_name}.vcd" if \
        #     self._is_dump_vcd else None
        # self._generate_test_bench_file()
        self._generate_test_bench_file_for_vcd_extraction()
        print_info("The test bench file for vcd extraction is generated successfully")
        iverilog_instance = iverilog.iverilog(
            compiled_file_name="__signal_extraction__.out",
            top_module_name=self._top_module_name,
            tb_top_module_name=self._tb_top_name,
            verilog_file_path=self._verilog_file_path,
            tb_file_path=self._test_bench_file_path,
        )
        iverilog_instance.run_compile()
        iverilog_instance.run_sim()
        vcd_reader = vcd_variable_name_reader.vcd_variable_name_reader(
            self._vcd_dump_file_name_for_signal_extraction)
        return vcd_reader.get_variable_name_dict()

    def _extract_observe_signal_wire(self, line):
        """extract the observe signal from the line

        Args:
            line (str): the line that contains the observe signal information

        Returns:
            tuple[str,int]: the observe signal name and width
        """
        pattern = r"wire\s+([\\\w\.]+)"
        match = re.match(pattern, line)
        if match is not None:
            return (match.group(1), 1)
        pattern = r"wire\s+\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*([\\\w\.]+)"
        match = re.match(pattern, line)
        if match is not None:
            return (match.group(3), int(match.group(1)) - int(match.group(2)) + 1)
        else:
            print_err_info("The observe signal information is not correct "+\
                           f"line = {line}")
            raise ValueError()
    
    def _extract_observe_signal_reg(self, line):
        """extract the observe signal from the line

        Args:
            line (str): the line that contains the observe signal information
        Returns:
            tuple[str,int]: the observe signal name and width
        """
        pattern = r"reg\s+([\\\w\.]+)"
        match = re.match(pattern, line)
        if match is not None:
            return (match.group(1) ,1)
        pattern = r"reg\s+\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*([\\\w\.]+)"
        match = re.match(pattern, line)
        if match is not None:
            width = int(match.group(1)) - int(match.group(2)) + 1
            return (match.group(3), width)
        else:
            print_err_info("The observe signal information is not correct"+\
                           f" line = {line}")
            raise ValueError()


    def _extract_input_port_info(self, line):
        """extract the input port information from the line

        Args:
            line (str): the line that contains the input port information

        Returns:
            dict: the input port information
        """
        if "[" not in line:
            pattern = "input\s+(\w+)"
            match = re.match(pattern, line)
            if match is not None:
                return {"width": 1, "name": match.group(1)} 

        pattern = "input\s+\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*(\w+)"
        match = re.match(pattern, line)
        if match is None:
            print_err_info("The input port information is not correct")
            return None
        else:
            return {"width": int(match.group(1)) - int(match.group(2)) + 1,
                    "name": match.group(3)}
        
    def _extract_output_port_info(self, line):
        """extract the output port information from the line

        Args:
            line (str): the line that contains the output port information
        """
        if "[" not in line:
            pattern = "output\s+(\w+)"
            match = re.match(pattern, line)
            if match is not None:
                return {"width": 1, "name": match.group(1)} 

        pattern = "output\s+\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*(\w+)"
        match = re.match(pattern, line)
        if match is None:
            print_err_info("The output port information is not correct")
            return None
        else:
            return {"width": int(match.group(1)) - int(match.group(2)) + 1,
                    "name": match.group(3)}
    
    def _extract_observe_signal(self, line):
        pass

    def _extract_top_module_information(self):
        """read through the verilog file and extract the top module information
        , the information should contain the ports definitions and the width of 
        the ports

        Returns:
            dict: the ports information of the top module
        """      
        port_info_input = {}  
        port_info_output = {}
        with open(self._verilog_file_path, "r") as f:
            lines = f.readlines()
            is_entering_top_module = False

            for line in lines:
                line = line.strip()
                if line.startswith("module") and \
                   line.find(f"module {self._top_module_name} (") != -1:
                    is_entering_top_module = True
                if is_entering_top_module and \
                   line.find(f"endmodule") != -1:
                    is_entering_top_module = False
                
                if is_entering_top_module is False:
                    continue

                if line.startswith("function"):
                    print_warning_info("ignore the function definition")
                    break
                
                if line.startswith("input"):
                    input_info = self._extract_input_port_info(line)
                    port_info_input[input_info["name"]] = input_info["width"]
                elif line.startswith("output"):
                    output_info = self._extract_output_port_info(line)
                    port_info_output[output_info["name"]] = \
                        output_info["width"]
                elif line.startswith("wire"):
                    observe_signal_tuple = self._extract_observe_signal_wire(line)
                    self._observe_signal_dict[observe_signal_tuple[0]] = \
                        observe_signal_tuple[1]
                elif line.startswith("reg"):
                    observe_signal_tuple = self._extract_observe_signal_reg(line)
                    self._observe_signal_dict[observe_signal_tuple[0]] = \
                        observe_signal_tuple[1]
                else:
                    continue
        print_info("The input ports information is {}".format(port_info_input))
        print_info("The output ports information is {}".format(port_info_output))
        return port_info_input, port_info_output
    
    def _generate_test_bench_signals_random_input(self, 
                                                  signal_name, 
                                                  file_handler):
        """generate the random input signal for the test bench file"""
        sanity_check.santiy_check_not_empty_str(signal_name)
        file_handler.write(f"always @(posedge {self._clock_signal_name}) begin\n")
        file_handler.write(f"{signal_name} <= $random;\n")
        file_handler.write("end\n")

    def _generate_test_bench_signals_write_to_file(self,
                                               signal_names_and_width,
                                               file_handler):
        """Generate the signal write to file for a group of signals.

        Args:
            signal_names (dict): Dict of signal names to write to the file.\
            the key is the signal name and the value is the width of the signal.
            file_handler: File handler for writing the test bench.
        """
        sanity_check.sanity_check_type(signal_names_and_width, dict)
        file_handler.write(f"integer file;\n")
        file_handler.write(f"initial begin\n")
        file_handler.write(f"file = $fopen(\"signals_output.txt\", \"w\");\n")
        file_handler.write(f"if (file == 0) begin\n")
        file_handler.write(f" $display(\"Error: Cannot open the file signals_output.txt\");\n")
        file_handler.write(f" $finish;\n")
        file_handler.write(f"end\n")
        file_handler.write(f"end\n")

        file_handler.write(f"always @(posedge {self._clock_signal_name}) begin\n")
        file_handler.write(f" $fwrite(file, \"new cycle\\n\");\n")
        for signal_name, signal_width in signal_names_and_width.items():
            signal_name_in_comma = signal_name.replace("\\", "")
            file_handler.write(f" $fwrite(file, "+\
                               f"\"{signal_name_in_comma}=%d "+\
                               f"width={signal_width}\\n\", "+\
                               f"{self._top_module_name}_inst.{signal_name});\n")
        # file_handler.write(f" $fwrite(file, \"Time: %0t\", $time);\n")
        # file_handler.write(f" $fwrite(file, ")
        # file_handler.write("\"")
        # for signal_name in signal_names:
        #     signal_name = signal_name.replace("\\", "\\\\")
        #     file_handler.write(f", {signal_name}=%0d")
        # file_handler.write("\\n\"")
        # for signal_name in signal_names:
        #     file_handler.write(f", {signal_name}")
        # file_handler.write(");\n")
        file_handler.write("end\n")

    def _generate_test_bench_finish(self, file_handler, cycle_num):
        """generate the finish statement for the test bench file"""
        file_handler.write("initial begin\n")
        file_handler.write(f"#{10 * cycle_num}\n")
        file_handler.write("$display(\"Simulation done\");\n")
        file_handler.write("$finish;\n")
        file_handler.write("end\n")

    def _generate_test_bench_file_for_vcd_extraction(self):
        """generate the test bench file for the top module
        """
        with open(self._test_bench_file_path, "w") as f:
            f.write("`timescale 1ns/1ps\n")
            f.write("module {}_tb;\n".format(self._top_module_name))
            f.write(f"reg {self._clock_signal_name};\n")
            f.write(f"reg {self._reset_signal_name};\n")
            for key, value in self._port_info_input.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write("reg [{}:0] {};\n".format(value - 1, key))
            for key, value in self._port_info_output.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write("wire [{}:0] {};\n".format(value - 1, key))

            # generate the instance of the top module
            f.write("{} {}_inst(".format(self._top_module_name, 
                                         self._top_module_name))
            for key, value in self._port_info_input.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write(".{}({}),".format(key, key))
            for key, value in self._port_info_output.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write(".{}({}),".format(key, key))
            f.write(f".{self._clock_signal_name}({self._clock_signal_name}),"+\
                    f" .{self._reset_signal_name}({self._reset_signal_name}));"+\
                    "\n")
            
            # generate the clock and reset signal
            f.write("initial begin\n")

            f.write(f"$dumpfile(\"{self._vcd_dump_file_name_for_signal_extraction}\");\n")
            f.write(f"$dumpvars(0, {self._tb_top_name});\n")

            f.write(f"{self._clock_signal_name} = 0;\n")
            f.write(f"{self._reset_signal_name} = 1;\n")
            f.write("#10\n")
            f.write(f"{self._reset_signal_name} = 0;\n")
            f.write("end\n")
            f.write("always begin\n")
            f.write(f"#5 {self._clock_signal_name} = ~{self._clock_signal_name};\n")
            f.write("end\n")

            # generate the random input signals
            self._generate_test_bench_finish(file_handler=f, cycle_num=10000)

            for signal_name in self._port_info_input.keys():
                if signal_name == self._clock_signal_name or\
                      signal_name == self._reset_signal_name:
                    continue
                self._generate_test_bench_signals_random_input(signal_name, f)
            
            self._observe_signal_dict = {k:v for k,v in \
                        self._observe_signal_dict.items() if \
                        re.match("_\d+_", k) is None}


            f.write("endmodule\n")
        print_info("The test bench file is generated successfully")
        print_info("The test bench file is saved at {}".format(self._test_bench_file_path))


    def _generate_test_bench_file(self):
        """generate the test bench file for the top module
        """
        with open(self._test_bench_file_path, "w") as f:
            f.write("`timescale 1ns/1ps\n")
            f.write("module {}_tb;\n".format(self._top_module_name))
            f.write(f"reg {self._clock_signal_name};\n")
            f.write(f"reg {self._reset_signal_name};\n")
            for key, value in self._port_info_input.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write("reg [{}:0] {};\n".format(value - 1, key))
            for key, value in self._port_info_output.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write("wire [{}:0] {};\n".format(value - 1, key))

            # generate the instance of the top module
            f.write("{} {}_inst(".format(self._top_module_name, self._top_module_name))
            for key, value in self._port_info_input.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write(".{}({}),".format(key, key))
            for key, value in self._port_info_output.items():
                if key == self._clock_signal_name or\
                      key == self._reset_signal_name:
                    continue
                f.write(".{}({}),".format(key, key))
            f.write(f".{self._clock_signal_name}({self._clock_signal_name}),"+\
                    f" .{self._reset_signal_name}({self._reset_signal_name}));"+\
                    "\n")
            
            # generate the clock and reset signal
            f.write("initial begin\n")

            if self._is_dump_vcd:
                f.write(f"$dumpfile(\"{self._vcd_dump_file_name}\");\n")
                f.write(f"$dumpvars(0, {self._tb_top_name});\n")

            f.write(f"{self._clock_signal_name} = 0;\n")
            f.write(f"{self._reset_signal_name} = 1;\n")
            f.write("#10\n")
            f.write(f"{self._reset_signal_name} = 0;\n")
            f.write("end\n")
            f.write("always begin\n")
            f.write(f"#5 {self._clock_signal_name} = ~{self._clock_signal_name};\n")
            f.write("end\n")

            # generate the random input signals
            self._generate_test_bench_finish(file_handler=f, 
                                             cycle_num=self._cycle_num)

            for signal_name in self._port_info_input.keys():
                if signal_name == self._clock_signal_name or\
                      signal_name == self._reset_signal_name:
                    continue
                self._generate_test_bench_signals_random_input(signal_name, f)
            
            self._observe_signal_dict = {k:v for k,v in \
                        self._observe_signal_dict.items() if \
                        re.match("_\d+_", k) is None}

            signal_names_write_to_file = self._observe_signal_dict |\
                self._port_info_output | self._port_info_input
            
            if self._is_dump_txt:
                self._generate_test_bench_signals_write_to_file(
                    signal_names_write_to_file, f)

            f.write("endmodule\n")
        print_info("The test bench file is generated successfully")
        print_info("The test bench file is saved at {}".format(self._test_bench_file_path))

    def get_tb_top_name(self):
        return f"{self._top_module_name}_tb"
    
    def get_signal_output_file_path(self):
        return self._signal_output_file
    
    def get_vcd_dump_file_name(self):
        sanity_check.sanity_check_not_none(self._vcd_dump_file_name)
        return self._vcd_dump_file_name

# test
def get_parser():
    parser = argparse.ArgumentParser(description="Generate the test bench file for the top module")
    parser.add_argument("--FILE", type=str, 
                        help="The path of the verilog file", required=True)
    parser.add_argument("--TOP", type=str, 
                        help="The name of the top module", required=True)
    parser.add_argument("--O", type=str, 
                        help="The path of the test bench file", required=True)
    parser.add_argument("--clock", type=str, 
                        default="clk", help="The name of the clock signal")
    parser.add_argument("--reset", type=str, 
                        default="rst", help="The name of the reset signal")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    verilog_tb_generator(args.FILE, args.TOP, args.O, args.clock, args.reset)

if __name__ == "__main__":
    main()