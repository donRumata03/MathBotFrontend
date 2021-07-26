import json
from typing import Union, Optional, Any
import param_parser
import os
from threading import Thread

import speaker
from config import *

from mylang import to_utf8_json_file

import safe_function_runner

# Argument checking:
def check_function(function : str) -> Union[None, list]:
    """
    :returns: None if not success, otherwise - variables.
    """
    res = param_parser.scrape_function_variables(function)

    return None if not res else res


def check_equation(equation : str) -> Union[None, list]:
    """
    :returns: None if not success, otherwise - variables.
    """
    res = param_parser.scrape_equation_variables(equation)

    return None if not res else res


def check_plotting_functions(functions : str) -> Union[str, list]:
    """
    :returns: None if not success, otherwise - variables.
    """
    res = param_parser.scrape_plotting_function_string_variables(functions)

    if len(res) == 1:
        return res

    return f"There are too {'little' if len(functions) < 1 else 'much'} variables for plotting a graph. Should be: {str(1)}, have: {len(functions)}"


def check_target_minimum(value : str) -> Optional[float]:
    try:
        res = float(value)
        return res
    except:
        return None

def cut_double_quotes(smth : Any):
    if smth[0] == "\"" or smth[0] == "'":
        smth = smth[1:]
    if smth[-1] == "\"" or smth[-1] == "'":
        smth = smth[:-1]
    return smth


##########################################################################

def get_target_and_arg_paths(user_id : int, message_id : int):
    target_dir = os.path.join(results_dir, str(user_id))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    target_path = os.path.join(target_dir, str(message_id) + ".txt")

    arg_dir = os.path.join(query_dir, str(user_id))
    if not os.path.exists(arg_dir):
        os.makedirs(arg_dir)
    arg_path = os.path.join(arg_dir, str(message_id) + ".json")

    return target_path, arg_path


def launch_function_optimization(user_id : int, message_id : int, name : str, iterations = optimizing_iterations,  **kwargs):
    """
    :does: something
    :returns: Nothing
    """
    function = cut_double_quotes(kwargs.get("function"))
    variable_ranges = kwargs.get("variable_ranges")
    variables = kwargs.get("variables")
    target_minimum = kwargs.get("target_minimum")

    target_path, arg_path = get_target_and_arg_paths(user_id, message_id)

    res_json = {
        "identifier" : str(message_id),
        "data" : kwargs,
        "target_path" : target_path,
        "name" : name,
        "iterations" : iterations
    }

    # print(arg_path, target_path)

    # encoding = "cp1251"
    encoding = "utf8"

    open(arg_path, "wb").write(json.dumps(res_json, indent = 4, ensure_ascii = False).encode(encoding, errors = "ignore"))

    command_parts = [solver_path, "optimize", arg_path]
    safe_function_runner.launch_in_new_thread(command_parts, target_path)



def launch_equation_solving(user_id : int, message_id : int, name : str, iterations = solving_iterations, **kwargs):
    """
    :does: Something
    :returns: Nothing
    """

    target_path, arg_path = get_target_and_arg_paths(user_id, message_id)

    res_json = \
        {
            "name": name,
            "identifier": str(message_id),
            "target_path": target_path,
            "iterations": iterations,

            "data": kwargs
        }

    # open(arg_path, "w").write(json.dumps(res_json, indent = 4, ensure_ascii = False))

    to_utf8_json_file(res_json, arg_path)

    command_parts = [solver_path, "solve", arg_path]
    safe_function_runner.launch_in_new_thread(command_parts, target_path)


def extract_function_list_from_string(string : str):
    return list(map(str.strip, string.split("&&")))


def launch_plotting(user_id : int, message_id : int, name : str, **kwargs):
    """
    :does: Something
    :returns: Nothing
    """

    functions = kwargs.get("functions")

    if isinstance(functions, str):
        functions = extract_function_list_from_string(functions)

    if "variable_range" in kwargs:
        variable_range = kwargs.get("variable_range")
        variable = ""
        for i in variable_range.keys():
            variable = i
        real_range = variable_range[variable]
        range_start = real_range[0]
        range_end = real_range[1]
    else:
        range_start = kwargs.get("from")
        range_end = kwargs.get("to")
    steps = kwargs.get("steps") if "steps" in kwargs else 20000

    text_path, arg_path = get_target_and_arg_paths(user_id, message_id)

    target_path = text_path[:-len(".txt")] + ".png"

    res_json = {
        "name" : name,
        "identifier" : str(message_id),
        "target_path" : target_path,
        "text_path" : text_path,

        "data" : {
            "from" : range_start,
            "to" : range_end,
            "steps" : steps,

            "functions" : functions
        }
    }

    to_utf8_json_file(res_json, arg_path)

    command_parts = [solver_path, "plot", arg_path]
    safe_function_runner.launch_in_new_thread(command_parts, text_path)




"""
def start_function_optimization(user_id : int, iterations : int, function_text : str, ranges : List[Tuple[float, float]], min_value : float):
    
    resultive format:
        solver_path optimize |function_text|1,2    4,6   9,4|min_value|iterations|user_id
    
    
    string_ranges = ""
    for r in ranges:
        string_ranges += str(r[0]) + "," + str(r[1]) + " "
    command = "\"" + solver_path + "\"" + " optimize |" + function_text + "|" + string_ranges + "|" + str(min_value) + "|" + str(iterations) + "|" + str(user_id)
    print("Launching " + command)
    launch_in_new_thread(command)

"""


""" <Deprecated>:  """
# def start_solving_equation(user_id : int, iterations : int, equation_text : str):
#     command = solver_path + " solve |" + equation_text + "|" + str(iterations) + "|" + str(user_id)
#     print("Launching " + command)
#     launch_in_new_thread(command)
""" <\\Deprecated>  """


def get_graph_path(user_id : int, message_id : int):
    return os.path.join(results_dir, str(user_id), str(message_id) + ".png")


def get_computational_results(user_id : int, message_id : int, user_process_name : str) -> Optional[str]:
    """
    :returns None if supposed file doesn`t exist else its contents:
    user_process_name: one of { "Решить уравнение", "Оптимизировать функцию", "Построить график" }
    """

    supposed_file = os.path.join(results_dir, str(user_id), str(message_id) + ".txt")
    if os.path.exists(supposed_file):
        file = open(supposed_file, "rb")
        text = file.read().decode("utf8", errors = "ignore")
        file.close()
        return text
    return None


def parser_test():
    print(speaker.get_optimizing_argument_info("Целевая функция", True))
    print(param_parser.scrape_function_variables(
        """
        sqrt(x^2 - 1) / 10^(y - 1) + exp(x*6) - e^2y+10z
        """
    ))


if __name__ == '__main__':
    launch_plotting(1, 1, "Hello!", **{
        # "from" : 1,
        # "to" : 100,
        # "steps" : 10000,
        "variable_range" : {
            "x" : [1, 100]
        },
        "functions" : "x + 100 && 10 * x + 100 ^ 2 / 10000 x"
    })

