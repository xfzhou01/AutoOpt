
import sanity_check
import os
import re
import subprocess
import time

def print_err_info(info_str):
    print("[ERROR] [yosys] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [yosys] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [yosys] -- {}".format(info_str))


class yosys_execution:
    def __init__(self, cmd_list:list, debug_log=None, quick_config=False):
        """Initialize the command processor.

        Args:
            cmd_list (list): List of commands to be processed.
            debug_log (str, optional): Path to the debug log file. Defaults to None.
            quick_config (bool, optional): Flag to enable quick configuration. Defaults to False.

        Raises:
            NotImplementedError: If quick configuration is not implemented.
        """     
        for cmd in cmd_list:
            sanity_check.sanity_check_type(cmd,str)
        if debug_log is not None:
            sanity_check.sanity_check_type(debug_log,str)
        sanity_check.sanity_check_type(quick_config, bool)
        self.execution_time = None
        self.cmd_str = None
        self.debug_log_path = debug_log
        self.generate_cmd_str(cmd_list=cmd_list)
        if quick_config:
            print_err_info("the quick config have not been implemented")
            raise NotImplementedError()

    def get_cmd_str(self):
        """Get the command string.

        Returns:
            str: The command string.
        """   
        sanity_check.sanity_check_not_none(self.cmd_str)
        return self.cmd_str
            
    def generate_cmd_str(self, cmd_list:list):
        """Generate the command string for Yosys.

        Args:
            cmd_list (list): List of commands to be included in the Yosys script.
        """   
        cmd_list = [cmd for cmd in cmd_list if cmd != '']
        yosys_script_cmd_str = "; ".join(cmd_list)
        if self.debug_log_path is not None:
            self.cmd_str = f" ~/oss_cad/oss_cad_2025/oss-cad-suite/bin/yosys -p \"{yosys_script_cmd_str}\" > {self.debug_log_path}"
        else:
            self.cmd_str = f" ~/oss_cad/oss_cad_2025/oss-cad-suite/bin/yosys -p \"{yosys_script_cmd_str}\" > debug_log_yosys_{id(self)}"


    def execute(self):
        """Execute the Yosys command and measure its execution time.
        """        
        try:
            start_time = time.time()
            # Execute the command
            result = subprocess.run(self.cmd_str, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            end_time = time.time()
            execution_time = end_time - start_time
            self.execution_time = execution_time
            # Analyze the return code
            if result.returncode == 0:
                print_info(f"yosys executed successfully. execution time = {execution_time} seconds")
            else:
                print_info(f"yosys failed with return code: {result.returncode}. execution time = {execution_time} seconds")
        except subprocess.CalledProcessError as e:
            print_err_info(f"Command failed with error: '{self.cmd_str}'  error is: {e.stderr.decode()} ")
            print_err_info(f"{self.cmd_str}")

    def get_debug_log_path(self):
        """Get the path to the debug log file.

        Returns:
            str: The path to the debug log file.
        """     
        if self.debug_log_path is not None:
            return self.debug_log_path
        else:
            return f"debug_log_yosys_{id(self)}"


    def get_execution_time(self):
        """Get the execution time of the command.

        Raises:
            ValueError: If the execution time is not a positive float.

        Returns:
            float: The execution time of the command.
        """ 
        sanity_check.sanity_check_type(self.execution_time, float)
        if self.execution_time <= 0:
            print_err_info(f"expected the execution time to be >= 0, but got f{self.execution_time}")
            raise ValueError()
        return self.execution_time