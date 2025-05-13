
import sanity_check

import os
import sanity_check
import re

import argparse

def print_info(info_str):
    print("[INFO] [harm-post-processor] -- {}".format(info_str))
def print_warning_info(info_str):
    print("[WARNING] [harm-post-processor] -- {}".format(info_str))
def print_err_info(info_str):
    print("[ERROR] [harm-post-processor] -- {}".format(info_str))

class harm_post_processor:
    def __init__(self,harm_assertion_file_path,
                 output_verilog_assertion_file_path = None):
        sanity_check.sanity_check_is_file_exist(
            harm_assertion_file_path)
        if output_verilog_assertion_file_path is not None:
            sanity_check.santiy_check_not_empty_str(
                output_verilog_assertion_file_path
            )
        else:
            output_verilog_assertion_file_path = \
                os.path.splitext(harm_assertion_file_path)[0] + "_std.txt"
        self._harm_assertion_file_path = harm_assertion_file_path
        self._output_verilog_assertion_file_path = \
            output_verilog_assertion_file_path
        self._assertion_list = []
        self._standardized_assertion_list = []

        self._read_harm_assertion_file()
        self._standardize_harm_assertion()

    def _read_harm_assertion_file(self):
        """read harm assertion file"""
        with open(self._harm_assertion_file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    self._assertion_list.append(line)

    def _standardize_harm_assertion(self):
        """standardize harm assertion"""
        for assertion in self._assertion_list:
            assertion:str
            assertion = assertion.strip()
            if assertion.startswith("always"):
                # print_warning_info(
                #     "Assertion {} does not start with always".format(
                #         assertion))
                assertion = assertion[len("always"):].strip()
            elif assertion.startswith("assert property"):
                assertion = assertion[len("assert property"):].strip()
                assertion = assertion.strip()
                pattern = "@\(posedge\s+[\w|:]+\s*\)"
                assertion = re.sub(pattern, "", assertion)
            else:
                print_warning_info(
                    "Assertion {} does not start with assert property".format(
                        assertion))
                print_warning_info(assertion)
                continue
            # print_info(assertion)
            # exit()
            if assertion.startswith("(") and assertion.endswith(")"):
                assertion = assertion[1:-1].strip()
            assertion = assertion.replace("::",".")
            cond_res_list = assertion.split("|->")
            if len(cond_res_list) != 2:
                print_warning_info(
                    "Assertion {} does not have exactly one |->".format(
                        assertion))
                continue
            cond = cond_res_list[0].strip()
            res = cond_res_list[1].strip()

            new_assertion_str = f"~({cond})||({res})"
            words = re.findall(r'\b[a-zA-Z0-9_.]+\b', new_assertion_str)
            for word in words:
                if word.isdigit():
                    continue
                word = word.strip()
                if len(word.split(".")) < 2:
                    print_err_info(
                        "Assertion {} has word {} with less than 2 dots".format(
                            new_assertion_str, word))
                    raise ValueError()
                word_new = ".".join(word.split(".")[2:])
                new_assertion_str = new_assertion_str.replace(word, word_new)
            self._standardized_assertion_list.append(
                new_assertion_str
            )

    def write_to_file(self):    
        """write to "self._output_verilog_assertion_file_path"""
        with open(self._output_verilog_assertion_file_path, 'w') as f:
            for assertion in self._standardized_assertion_list:
                f.write(assertion + "\n")
        print_info("write standardized assertion to {}".format(
            self._output_verilog_assertion_file_path))
        
    def get_std_file_path(self):
        """get standardized file path"""
        return self._output_verilog_assertion_file_path

def get_parser():
    parser = argparse.ArgumentParser(
        description="HARM assertion post processor"
    )
    parser.add_argument(
        "--FILE",
        type=str,
        help="HARM assertion file to be processed.",
        required=True
    )
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    harm_assertion_file_path = args.FILE
    post_processor = harm_post_processor(
        harm_assertion_file_path=harm_assertion_file_path
    )
    post_processor.write_to_file()
    print_info("HARM assertion post process finished")

if __name__ == "__main__":
    main()