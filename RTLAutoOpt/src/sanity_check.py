'''
sanity check: whether the code violates some simple rules
sanity check soft: whether the code violate some simple rule, if violate, print warning only
'''
import traceback

def print_err_info(info_str):
    print("[ERROR] [sanity-check] -- {}".format(info_str))

def print_warning_info(info_str):
    print("[WARNING] [sanity-check] -- {}".format(info_str))

def print_info(info_str):
    print("[INFO] [sanity-check] -- {}".format(info_str))

def print_warning_stack_trace():
    print_warning_info("stack trace: ")
    print_warning_info("".join(traceback.format_stack()))


import os


def sanity_check_onehot_exclude_all_zero(l):
    for e in l:
        sanity_check_type(e,bool)
    s = 0
    for e in l:
        s += int(e)
    if not s == 1:
        print_err_info(f"expected the list to be contain ONE `1` but got {l}")
        raise ValueError()

def sanity_check_type(s, ty):
    if s is None:
        print_err_info(f"expect the value to have {ty} type but got None")
        raise ValueError()

    if not isinstance(s, ty):
        print_err_info(f"expect the value to have {ty} type but got type {type(s)}, value is {s}")
        raise ValueError()

def sanity_check_value_greater_or_equal_to_0(s):
    """check whether the value is greater or equal to 0

    Args:
        s (Any): the value to be checked

    Raises:
        ValueError: the value is less than 0
    """    
    sanity_check_type(s, int)
    if not s >= 0:
        print_err_info(f"expect the value >= 0 but got {s}")
        raise ValueError()
    
def sanity_check_value_greater_or_equal_to_1(s):
    sanity_check_type(s, int)
    if not s >= 1:
        print_err_info(f"expect the value >= 0 but got {s}")
        raise ValueError()
    
def sanity_check_value_less_than_c(s, c):
    sanity_check_type(s, int)
    if not s < c:
        print_err_info(f"expect the value >= 0 but got {s}")
        raise ValueError()
    
def sanity_check_is_none_or_greater_or_equal_to_0(s):
    if s is None:
        return 
    sanity_check_value_greater_or_equal_to_0(s)


def sanity_check_list_eq_length(l1, l2):
    sanity_check_type(l1, list)
    sanity_check_type(l2, list)
    if not len(l1) == len(l2):
        print_err_info(f"expect the two list have equal length, but got l1 length = {len(l1)}, and l2 length = {len(l2)}")
        print_err_info(f"   l1 content = {l1}")
        print_err_info(f"   l2 content = {l2}")
        raise ValueError()
    
def sanity_check_list_is_empty(l1):
    '''
    ensure an empty list
    '''
    sanity_check_type(l1, list)
    if not len(l1) == 0:
        print_err_info(f"expect a empty list but got list with length {len(l1)}, list = {l1}")
        raise ValueError()
    
def sanity_check_list_has_length(l, length):
    '''
    whether a list have certain length
    '''
    sanity_check_type(l, list)
    sanity_check_type(l, int)
    if not len(l) == length:
        print_err_info(f"expect the list to have length: {length}, but got list with length {len(l)}")
        print_err_info(f"content of the list is: {l}")
        raise ValueError()
    
def sanity_check_list_not_empty(l):
    sanity_check_type(l, list)
    if len(l) == 0:
        print_err_info(f"the list is empty")
        raise ValueError()
    
def sanity_check_set_not_empty(s):
    sanity_check_type(s, set)
    if len(s) == 0:
        print_err_info(f"the set is empty")
        raise ValueError()

def sanity_check_dict_not_empty(d):
    sanity_check_type(d,dict)
    if len(d) == 0:
        print_err_info(f"the dict is empty")
        raise ValueError()

    
def sanity_check_is_file_exist(l):
    sanity_check_type(l, str)
    if not os.path.isfile(l):
        print_err_info(f"the file path {l} does not exist")
        raise FileNotFoundError()
    
def santiy_check_not_empty_str(s):
    sanity_check_type(s, str)
    if s == "":
        print_err_info("expect a not empty string but got an empty one")
        raise ValueError()
    
def sanity_check_not_none(s):
    if s is None:
        print_err_info("unexpected None value")
        raise ValueError()
    
def sanity_check_is_none(s):
    if not s is None:
        print_err_info(f"expect None value, but got {s} with type {type(s)}")
        raise ValueError()
    

def sanity_check_is_folder_exists(l):
    sanity_check_type(l, str)
    if not os.path.isdir(l):
        print_err_info(f"the folder path {l} does not exist or is not a folder")
        raise ValueError()
    
def sanity_check_file_postfix(s, p):
    """check whether the file path has certain postfix

    Args:
        s (str): the file path to be checked (should existed)
        p (str): the desired postfix

    Raises:
        ValueError: the file path does not have desired postfix
    """    
    sanity_check_is_file_exist(s)
    if not s.endswith(p):
        print_err_info(f"the file path {s} is expected to ends with postfix {p}")
        raise ValueError()
    
def sanity_check_str_postfix(s, p):
    """check whether the str has certain postfix

    Args:
        s (str): the file path to be checked (should existed)
        p (str): the desired postfix
    """    
    if not s.endswith(p):
        print_err_info(f"the string {s} is expected to ends with postfix {p}")
        raise ValueError()


def sanity_check_str_contain_substr(s, sub_str):
    sanity_check_type(s,str)
    sanity_check_type(sub_str, str)
    if not sub_str in s:
        print_err_info(f"the string {s} is expected to contain substring {sub_str} but not")
        raise ValueError()

def sanity_check_soft_dict_not_empty(s):
    """ check whether a dict is empty, if empty, print warning only
    """
    sanity_check_type(s, dict)
    if len(s) == 0:
        print_warning_info(f"the dict is empty")
        print_warning_stack_trace()

def sanity_check_soft_set_not_empty(s):
    sanity_check_type(s, set)
    if len(s) == 0:
        print_warning_info(f"the set is empty")
        print_warning_stack_trace()


def sanity_check_eq_length_multiple_list(sl):
    sanity_check_list_not_empty(sl)
    for l in sl:
        sanity_check_type(l, list)
    
    ll = None
    for l in sl:
        if not ll is None:
            if len(l) != ll:
                print_err_info(f"the lists are expected to have same length")
                for lll in sl:
                    print_err_info(f"   {lll}")
                raise ValueError()
        ll = len(l)

def sanity_check_str_end_with_line_switch(s):
    sanity_check_type(s, str)
    santiy_check_not_empty_str(s)
    if not s[-1] == "\n":
        print_err_info(f"expect the string to end with line switch char, but got {s}")
        raise ValueError()
    
def sanity_check_list_is_2D_array(l):
    """sanity check whether a list have all element with type list

    Args:
        l (list): the list expected to be a 2D array
    """    
    sanity_check_type(l, list)
    for sl in l:
        sanity_check_type(sl, list)

def sanity_check_folder_not_exist(folder_path):
    """if folder exists, raise valueError

    Args:
        folder_path (str): the folder path to check
    """    
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print_err_info(f"The folder '{folder_path}' already exists.")
        raise ValueError()
    
def sanity_check_folder_exists(folder_path):
    """if folder does not exist, raise valueError

    Args:
        folder_path (str): the folder path to check
    """    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
       print_err_info(f"The folder '{folder_path}' does not exist.")
       raise ValueError()
    
def sanity_check_file_not_exists(file_path:str):
    """
    Checks if the file path is a non-empty string and ensures the file does not exist.

    Args:
        file_path (str): The path of the file to check.

    Raises:
        FileExistsError: If the file already exists.
    """
    santiy_check_not_empty_str(file_path)
    if os.path.exists(file_path):
        print_err_info(f"The file '{file_path}' already exists")
        raise FileExistsError(f"The file '{file_path}' already exists")
    
def sanity_check_only_one_is_not_none(l):
    """
    Ensures that the list has exactly one non-None element.

    Args:
        l (list): The list to be checked.

    Raises:
        ValueError: If the list has more than one non-None element.
        ValueError: If the list does not have exactly one non-None element.
    """
    sanity_check_list_not_empty(l)
    not_none_count = 0
    for ele in l:
        if ele != None:
            not_none_count += 1
        if not_none_count > 1:
            print_err_info(f"expected the list should have only one not None element, but got list: {l}")
            raise ValueError()
    if not_none_count != 1:
        print_err_info(f"expected the list should have only one not None element, but got list: {l}")
        raise ValueError()
    

def sanity_check_both_none_or_not_none(a, b):
    """
    Ensures that both variables are either None or not None.

    Args:
        a (Any): The first variable to be checked.
        b (Any): The second variable to be checked.

    Raises:
        ValueError: If one variable is None and the other is not None.
    """
    if (a is None and b is not None) or (a is not None and b is None):
        print_err_info(f"expected both variables are either None or not None, but got a = {a}, b = {b}")
        raise ValueError()
    
def sanity_check_is_file_encoded_in_binary(file_path):
    """check whether a file is encoded in binary
    * it should be noted that, the check function is only
    * effective when the encoding is only binary|ascii

    Args:
        file_path (str): the file path

    Raises:
        ValueError: the file is encoded in ascii
    """    
    sanity_check_is_file_exist(file_path)
    with open(file_path, 'rb') as file:
        for byte in file.read():
            if byte > 127:
                return 
    try:
        with open(file_path, 'r', encoding='ascii') as file:
            file.read()
    except UnicodeDecodeError:
        # if raise a unicode decode error, it means that the file is not encoded in 
        # ascii (since we only consider the encoding case: binary|ascii here)
        return
    print_err_info(f"expected the file {file_path} to have binary encoding, but got ascii")
    raise ValueError()
    
def sanity_check_is_file_encoded_in_ascii(file_path):
    """check whether a file is encoded in ascii

    Args:
        file_path (str): the file path to be checked

    Raises:
        UnicodeDecodeError: raises when the file is not encoded in ascii
        - commonly, the UnicodeDecodeError is raised when the encoding does not meet
    """    
    try:
        with open(file_path, 'r', encoding='ascii') as file:
            file.read()
    except UnicodeDecodeError as ue:
        print_err_info(f"expected the file: {file_path} to have ascii encoding but got not")
        raise ue
    
def sanity_check_entry_not_exist_in_dict(d, k):
    """check whether the dict does not have an entry

    Args:
        d (dict): the dict to be check
        k (Any): the key to be check

    Raises:
        ValueError: the key is in dict, which is not as expected
    """    
    sanity_check_type(d,dict)
    if k in d:
        print_err_info(f"expect key {k} not in dict: {d}")
        raise ValueError()