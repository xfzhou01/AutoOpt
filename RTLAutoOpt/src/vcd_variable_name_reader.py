


import sanity_check

class vcd_variable_name_reader:
    def __init__(self, vcd_file_path):
        self.vcd_file_path = vcd_file_path
        self.variable_name_dict = {}
        
        self._scope_stack = []

    def _read_single_var(self, line):
        """
        Read a single var line and extract the variable name and its corresponding index.
        """
        # Example line: $var wire 1 a clk $end
        #               $var wire 2 t addr1 [1:0] $end
        # Extracting variable type, size, name, and index
        parts = line.split()
        var_type = parts[1]
        size = int(parts[2])
        var_name = parts[4]
        
        # Storing the variable name and its index in the dictionary
        return (var_name, size)
    
    def _read_vcd_file(self):
        """
        Read the VCD file and extract variable names and their corresponding indices.
        """
        with open(self.vcd_file_path, 'r') as vcd_file:
            for line in vcd_file:
                if line.startswith("$scope"):
                    # Push the current scope onto the stack
                    self._scope_stack.append(line.strip().split()[2])
                elif line.startswith("$upscope"):
                    # Pop the last scope from the stack
                    if self._scope_stack:
                        self._scope_stack.pop()
                elif line.startswith("$var"):
                    var_name, size = self._read_single_var(line)
                    var_name_with_scope = '.'.join(self._scope_stack[2:] +\
                                                    [var_name])
                    self.variable_name_dict[var_name_with_scope] = size
                elif line.startswith("$enddefinitions"):
                    # End of variable definitions
                    break

    def get_variable_name_dict(self):
        """
        Get the dictionary of variable names and their corresponding indices.
        """
        if not self.variable_name_dict:
            self._read_vcd_file()
        return self.variable_name_dict