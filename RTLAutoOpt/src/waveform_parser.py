import sanity_check

def print_info(info_str):
    print("[INFO] [waveform-parser] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [waveform-parser] -- {}".format(info_str))

def print_err_info(info_str):
    print("[ERROR] [waveform-parser] -- {}".format(info_str))

class waveform_parser:
    def __init__(self, waveform_file_path):
        sanity_check.sanity_check_is_file_exist(waveform_file_path)
        self._waveform_file_path = waveform_file_path

        # the waveform data
        # each element is a timestamp in dict format
        # the key is the var name, the value is the signal value
        self._data = []

        #
        self._bit_level_data = []
        self._bit_level_signal_name_set = set()

        # 
        self._word_level_data = []
        
        if self._waveform_file_path.endswith(".vcd"):
            self._parse_vcd()
        elif self._waveform_file_path.endswith(".txt"):
            self._parse_txt()
        else:
            raise ValueError(f"unsupported"+\
                f" waveform file format {self._waveform_file_path}")
        
        self._generate_bit_level_data()

    def _parse_vcd(self):
        raise NotImplementedError("not implemented yet")
    
    def _parse_txt(self):
        with open(self._waveform_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                elif line == "new cycle":
                    self._data.append({})
                    continue
                elif "=" in line:
                    # line = var_name=var_value width=var_width
                    var_name, var_value_and_width, var_width = line.split("=")
                    var_value_and_width = var_value_and_width.strip()
                    var_value = var_value_and_width.split(" ")[0]

                    self._data[-1][var_name] = (var_value, var_width)
                else:
                    raise ValueError(f"unsupported line format {line}")
        print_info(f"parse waveform file {self._waveform_file_path} done")

    def _generate_bit_level_data(self):
        for timestamp_data in self._data:
            bit_level_data = {}
            # for signal_name, (signal_value, signal_width) in timestamp_data.items():
            #     print_info(f"signal_name: {signal_name}, signal_value: {signal_value}, signal_width: {signal_width}")
            # exit(0)
            for signal_name, (signal_value, signal_width) in timestamp_data.items():
                # print_info(f"signal_name: {signal_name}, signal_value: {signal_value}, signal_width: {signal_width}")
                signal_width = int(signal_width)
                if signal_value.isdigit():
                    signal_value = int(signal_value)
                    sanity_check.sanity_check_type(signal_value, int)
                    # convert signal_value to a list of binary with width signal_width
                    binary_string = f"{signal_value:0{signal_width}b}"
                else:
                    if signal_value == "x" or signal_value == "X":
                        binary_string = "x" * int(signal_width)
                    elif signal_value == "z" or signal_value == "Z":
                        binary_string = "z" * int(signal_width)
                    else:
                        raise ValueError(f"unsupported signal_value {signal_value}")
                if signal_width > 1:
                    for i in range(int(signal_width)):
                        bit_level_data[f"{signal_name}[{i}]"] = binary_string[-(i+1)]
                        self._bit_level_signal_name_set.add(f"{signal_name}[{i}]")
                else:
                    bit_level_data[signal_name] = binary_string
                    self._bit_level_signal_name_set.add(signal_name)
            self._bit_level_data.append(bit_level_data)
        print_info("generate bit level data done")

    def get_bit_level_data(self) -> list[dict]:
        return self._bit_level_data
    
    def get_bit_level_signal_name_list(self) -> list[str]:
        sanity_check.sanity_check_set_not_empty(
            self._bit_level_signal_name_set)
        return list(self._bit_level_signal_name_set.copy())
    
    def get_word_level_data(self) -> list[dict]:
        raise NotImplementedError()
        return self._word_level_data
    
    def get_word_level_name_list(self):
        raise NotImplementedError()