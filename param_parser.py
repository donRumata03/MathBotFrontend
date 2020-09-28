from typing import *
from mylang import split_if

from dictionaries.resultive_dictionary import *


# Parsing arguments:
def is_identifier_symbol(char: str):
    return char.isalpha()  # not str.isspace(char) and


def scrape_function_variables(function: str) -> List[str]:
    """
    Variables are ordered properly!
    """

    identifiers = split_if(function, lambda c: not is_identifier_symbol(c))
    good_identifiers = filter(lambda identifier: identifier != "" and identifier not in reserved_identifier_names,
                              identifiers)
    variable_set = set()
    res = []
    for v in good_identifiers:
        if v not in variable_set:
            res.append(v)
        variable_set.add(v)
    return res


def scrape_equation_variables(equation_text: str) -> Optional[List[str]]:
    if equation_text.count("=") != 1:
        return None

    eq_parts = equation_text.split("=")

    left_vars = scrape_function_variables(eq_parts[0])
    right_vars = scrape_function_variables(eq_parts[1])

    res = left_vars
    existing_variables = set(res)

    for new_var in right_vars:
        if new_var not in existing_variables:
            res.append(new_var)
            existing_variables.add(new_var)

    return res


def scrape_plotting_function_string_variables(functions_string: str) -> List[str]:
    functions = list(map(str.strip, functions_string.split("&&")))
    non_unique_variables = sum([scrape_function_variables(function) for function in functions], [])

    taken_variables = set()
    res = []

    for var in non_unique_variables:
        if var not in taken_variables:
            res.append(var)
            taken_variables.add(var)

    return res

#################################################

def is_float(val: str):
    try:
        res = float(val)
        return True
    except:
        return False


def count_floats(arr: List[str]):
    counter = 0
    for val in arr:
        if is_float(val):
            counter += 1
    return counter


def get_not_floats(arr: List[str]):
    res = []
    for val in arr:
        if str.isalpha(val):
            res.append(val)
    return res


def get_floats(arr: List[str]):
    res = []
    for val in arr:
        if is_float(val):
            res.append(float(val))
    return res


def scrape_ranges(ranges: str, variables: List[str]) -> Union[str, Dict[str, Tuple[float, float]]]:
    identifiers = list(filter(lambda x: x and x != "in" and x != "from" and x != "to",
                              split_if(ranges, lambda x: not x.isalnum() and x != "." and x != "-")))

    # Check numbers` number:
    floats = get_floats(identifiers)
    float_number = len(floats)
    if float_number != len(variables) * 2:
        error_message = f"Количество переменных: {len(variables)}; Найдено чисел в записи диапазонов переменных: {float_number};\nКаждой переменной должно соответствовать 2 числа: верхняя и нижняя границы поиска. Проверьте корректность ввода!\nУбедитесь, что вы используете точку, а не запятую для разделения целой и дробной части числа!"
        return error_message

    # Check variables`s number and names:
    needed_variables_set = set(variables)
    have_variables = get_not_floats(identifiers)
    have_variables_set = set(have_variables)

    if have_variables_set != needed_variables_set:
        # Return Error message (bad variables):
        redundant_var_set = have_variables_set - needed_variables_set
        required_var_set = needed_variables_set - have_variables_set

        redundant_vars = []
        required_vars = []

        for red_var in have_variables:
            if red_var in redundant_var_set:
                redundant_vars.append(red_var)

        for req_var in variables:
            if req_var in required_var_set:
                required_vars.append(req_var)

        error_message = f"Вы неправильно указали диапазоны переменных, так как в них либо присутствуют лишние переменные, и / или не присутствуют те, которые Вы указали в функции / уравнении.\n"

        if redundant_vars:
            error_message += f"Эти переменные лишние: {redundant_vars}! "
        if required_vars:
            error_message += f"Диапазонов этих переменных не хватает: {required_vars}! "

        return error_message

    res = {}
    for index in range(len(variables)):
        res[variables[index]] = (floats[index * 2], floats[index * 2 + 1])

        if floats[index * 2] >= floats[index * 2 + 1]:
            # Return Error message (bad range!):
            error_message = f"Bad range: {floats[index * 2]} >= {floats[index * 2 + 1]}"
            return error_message

    return res


def test_ranges():
    variables_example = ["x", "y", "z"]

    easy_ranges_example = "x -1; 10; y: 30.6 100., 10 < z <= 11"
    good_ranges_example = "x ∈ (-1; 10]; y: -> 30.6 100., 10 < z <= 11e1"
    in_ranges_example = "x ∈ (-1; 10]; y in [30.6; 100.), 10 < z <= 11e1"
    awful_ranges_example = "z 10 1 x 10000 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; 100900 ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,y -101010332323,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;; 324987"
    bad_float_format_ranges = "x -1 10; y: 30,6 100., 10 < z <= 11e-100"
    bad_variables = "a <= 1, 1; b >= 19, 0; i < 0; 1"
    bad_variable_ranges = "x ∈ (-1; 10]; y: -> 30.6 100., 10e100 < z <= 11e1"

    for this_ranges in (
            easy_ranges_example, good_ranges_example, in_ranges_example, awful_ranges_example, bad_float_format_ranges,
            bad_variables, bad_variable_ranges):
        print(scrape_ranges(this_ranges, variables_example), "\n___________________________________________")


if __name__ == '__main__':
    test_ranges()
