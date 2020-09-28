from solver import *

from typing import *

def process_fast_optimizing_args(function : str, args : List[str], user_id : int, message_id : int, name : str) -> Optional[Dict[str, Any]]:
    """
            Processes args and either launches the corresponding process and returns True or returns False
    """
    variables = param_parser.scrape_function_variables(function)

    if not variables:
        return None

    # Require "for" and "where":
    ranges_data = None
    minorant_data : Optional[float] = None

    for arg in args:
        stripped = arg.strip()
        if stripped.startswith("for"):
            for_ranges = stripped[len("for"):]
            ranges_scrape_try = param_parser.scrape_ranges(for_ranges, variables)

            if isinstance(ranges_scrape_try, str):
                return None

            ranges_data = ranges_scrape_try

        elif stripped.startswith("minorant"):
            for_minorant = stripped[len("minorant"):].replace("=", " ").strip()
            min_check = check_target_minimum(for_minorant)

            if min_check is None:
                return None

            minorant_data = min_check

        else:
            return None

    if minorant_data is None or ranges_data is None:
        return None

    optimization_params = {
        "variables" : variables,
        "variable_ranges" : ranges_data,
        "function" : function,
        "target_minimum" : minorant_data
    }

    print("Fast mode succeed! Launching OPTIMIZATION process!")
    launch_function_optimization(user_id, message_id, name, **optimization_params)

    return optimization_params


def process_fast_plotting_args(functions : List[str], args : List[str], user_id : int, message_id : int, name : str) -> Optional[Dict[str, Any]]:
    """
            Processes args and either launches the corresponding process and returns True or returns False
    """

    variable : Optional[str] = None

    for function_text in functions:
        this_variables = param_parser.scrape_function_variables(function_text)

        if not this_variables:
            continue

        if len(this_variables) > 1:
            return None

        this_variable = this_variables[0]

        if variable is not None and variable != this_variable:
            return None

        variable = this_variable

    if variable is None:
        return None

    # The only arg should be ranges param:
    if len(args) != 1:
        return None

    for_range_with_for = args[0].strip()

    if not for_range_with_for.startswith("for"):
        return None

    range_params = param_parser.scrape_ranges(for_range_with_for[len("for"):], [variable])

    if isinstance(range_params, str):
        return None

    range_start = range_params[variable][0]
    range_end = range_params[variable][1]

    params = {
        "from" : range_start,
        "to" : range_end,
        "functions" : functions
    }

    launch_plotting(user_id, message_id, name, **params)
    return params


def process_fast_solving_args(equation : str, args : List[str], user_id : int, message_id : int, name : str) -> Optional[Dict[str, Any]]:
    """
        Processes args and either launches the corresponding process and returns True or returns False
    """

    if equation.count("=") != 1:
        return None

    # Scrape variables from equation:
    variables = param_parser.scrape_equation_variables(equation)  # Definitely list, not None because rhe check is already performed

    if len(args) != 1:
        return None

    assumed_range = args[0].strip()
    if not assumed_range.startswith("for"):
        return None

    range_raw_data = assumed_range[len("for"):]
    ranges_scrape_try = param_parser.scrape_ranges(range_raw_data, variables)

    if isinstance(ranges_scrape_try, str):
        return None

    ranges_data = ranges_scrape_try

    solving_params = {
        "variables": variables,
        "variable_ranges": ranges_data,
        "function": equation
    }

    print("Fast mode succeed! Launching SOLVING process with these params:", solving_params)
    launch_equation_solving(user_id, message_id, name, **solving_params)

    return solving_params


def process_fast_input(input_string : str, user_id : int, message_id : int, name : str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
        Processes input and either launches the corresponding process and returns the process name or returns None

        :returns:
                    None
                    "optimize"
                    "plot"
                    "solve"
    """

    def get_rightest_non_space_index(string : str, start_index : int) -> int:
        for i in range(start_index, -1, -1):
            if not str.isspace(string[i]):
                return i
        return -1

    for_find_attempt = input_string.find("for")
    if for_find_attempt != -1:
        if for_find_attempt != 0 and for_find_attempt + len("for") < len(input_string):
            if not str.isalnum(input_string[for_find_attempt - 1]) and not str.isalnum(input_string[for_find_attempt + len("for")]):
                rnsi = get_rightest_non_space_index(input_string, for_find_attempt - 1)
                if rnsi != -1 and input_string[rnsi] != '|':
                    # add missing "|" here:
                    temp_input_string = input_string
                    input_string = temp_input_string[:for_find_attempt] + " | " + temp_input_string[for_find_attempt:]

                    print("Added missing \"|\": ", input_string)

    splitted = input_string.split("|")

    if not splitted:
        return None

    first_part = splitted[0].strip()

    if first_part.startswith("optimize") or first_part.startswith("optimise") or first_part.startswith("Optimize") or first_part.startswith("Optimise"):  # But not optimise!!!
        function_data = first_part[len("optimize"):].strip()

        output = process_fast_optimizing_args(function_data, splitted[1:], user_id, message_id, name)

        if output is None:
            return None
        return "optimize", output



    elif first_part.startswith("plot") or first_part.startswith("Plot"):
        functions_data = first_part[len("plot"):]
        functions = list(map(str.strip, functions_data.split("&&")))

        output = process_fast_plotting_args(functions, splitted[1:], user_id, message_id, name)
        if output is None:
            return None
        return "plot", output


    elif first_part.startswith("solve") or first_part.startswith("Solve"):
        equation_text = first_part[len("solve"):].strip()
        output = process_fast_solving_args(equation_text, splitted[1:], user_id, message_id, name)
        if output is None:
            return None
        return "solve", output


    else:
        return None



##############################################################
#######                     Tests                    #########
##############################################################

def test_fast_optimizing():
    test1 = "optimize x + y^2 - 1000.5 | for x in [1; 100], y in (10.3e-100, 123] | minorant 10"
    test2 = "optimize x^2 for x in [-3, 0.5] | minorant = -100"

    # print(process_fast_input(test1, 1, 1, ""))
    print(process_fast_input(test2, 1, 1, ""))


def test_fast_plotting():

    # test1 = "plot 0.5x + 5 && 3sin(x) && 5sqrt(abs(x) - 5) && 10sgn(x) * sqrt(x) | for x in [-10; 10]"
    # test1 = "plot хрень ^ 2 for хрень in [-6, 6]"
    test1 = "plot x ^ 2 for x in [-6, 6]"


    # test2 = "plot x + 1 && x^2 + 332 | for x in [10; 100]"
    # test3 = "plot x + 1 && y^2 + 332 | for x in [10; 100]"
    # test4 = "plot x + 1 && x^2 + 332 | for y in [10; 100]"

    print("test1", process_fast_input(test1, 1, 1, ""))
    # print("test2", process_fast_input(test2, 1, 1, ""))
    # print("test3", process_fast_input(test3, 1, 1, ""))
    # print("test4", process_fast_input(test4, 1, 1, ""))


def test_fast_solving():
    test0 = "solve x = lg(-x) for x from -10 to 0.01"
    print("test0", process_fast_input(test0, 1, 1, ""))

    exit(0)

    test1 = "solve x ^ 2 = -y ^ 2 | for x in [-10, 10], y in [-100, 1]"
    print("test1", process_fast_input(test1, 1, 1, ""))

    test2 = "solve x ^ 2 = -y ^ 2 for x in [-10, 10], y in [-100, 1]"
    print("test2", process_fast_input(test2, 1, 1, ""))



# In perspective:
def test_equation_system_solving():
    test11 = "solve x + y = 2 && x ^ 2 + y ^ 2 = 44 | for x  "


if __name__ == '__main__':
    # test_fast_optimizing()
    test_fast_plotting()
    # test_fast_solving()

