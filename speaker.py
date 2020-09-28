from typing import Union, Callable

from dictionaries.resultive_dictionary import *


def add_info_about_args(info : List[str], param_list : List[str], param_names : Dict[str, str], param_description : Dict[str, str], add_descriptions, **kwargs):
    for param in param_list:
        name = param_names[param]

        param_value = kwargs.get(param, None)
        info.append("____________________________________")
        if param_value is None:
            this_appendix = f"Аргумент \"{name}\" пока не указан."
            if add_descriptions:
                this_appendix += f" Вот его описание: \n\"{param_description[param]}\""
            info.append(this_appendix)
        else:
            info.append(f"Вы указали такое значение параметра \"{name}\": \n\"{param_value}\". Вы можете его поменять.")

    info.append("____________________________________")


# Info about many arguments
def add_info_about_optimizing_args(info : List[str], add_descriptions, **kwargs):
    add_info_about_args(info, function_optimization_parameters, function_optimization_parameter_names, function_optimization_parameter_description, add_descriptions, **kwargs)

def add_info_about_solving_args(info : List[str], add_descriptions, **kwargs):
    add_info_about_args(info, equation_solving_parameters, equation_solving_parameter_names, equation_solving_parameter_description, add_descriptions, **kwargs)

def add_info_about_plotting_args(info : List[str], add_descriptions, **kwargs):
    add_info_about_args(info, plotting_parameters, plotting_parameter_names, plotting_parameter_description, add_descriptions, **kwargs)

#######################

def get_some_info_with_given_args(russian_command_name : str, adding_function : Callable, add_descriptions = False, **kwargs):
    res = [f"Вы выбрали опцию \"{russian_command_name}\". Вам нужно указать все необходимые аргументы:"]

    adding_function(res, add_descriptions, **kwargs)

    for i in range(1, len(res)):
        if res[i][0] != "_":
            res[i] = "\t" + res[i]
    return "\n".join(res)

def get_solving_info_with_given_args(add_descriptions = False, **kwargs):
    return get_some_info_with_given_args(solve_equation_text, add_info_about_solving_args, add_descriptions, **kwargs)

def get_optimizing_info_with_given_args(add_descriptions = False, **kwargs):
    # res = ["Вы выбрали опцию \"Оптимизировать функцию\". Вам нужно указать все необходимые аргументы:"]
    #
    # add_info_about_optimizing_args(res, add_descriptions, **kwargs)
    #
    # for i in range(1, len(res)):
    #     if res[i][0] != "_":
    #         res[i] = "\t" + res[i]
    # return "\n".join(res)

    return get_some_info_with_given_args(optimize_function_text, add_info_about_optimizing_args, add_descriptions, **kwargs)

def get_plotting_info_with_given_args(add_descriptions = False, **kwargs):
    return get_some_info_with_given_args(plot_text, add_info_about_plotting_args, add_descriptions, **kwargs)

############################################################################################################################################################

def has_all_args(target_args, **kwargs) -> bool:
    for param_name in target_args:
        if param_name not in kwargs:
            return False

    return True


def get_human_readable_optimizing_args_info():
    pass  # TODO!


# Info about one argument
def get_one_argument_info(param_name, reversed_param_names, param_descriptions, param_examples, first_time : bool) -> str:
    param = reversed_param_names[param_name]

    if first_time:
        res = f"Информация об аргументе \"{param_name}\": \n "
    else:
        res = f"Вы должны указать корректное значение аргумента \"{param_name}\"! \n"
    res += f"\"{param_descriptions[param]}\". \n\nВот корректный пример использования: \"{param_examples[param]}\""
    return res


# For convenience: specializations:

# Info about one argument
def get_optimizing_argument_info(param_name : str, first_time : bool) -> str:
    return get_one_argument_info(param_name, reversed_function_optimization_parameter_names, function_optimization_parameter_description, function_optimizing_parameter_examples, first_time)

def get_solving_argument_info(param_name : str, first_time : bool) -> str:
    return get_one_argument_info(param_name, reversed_equation_solving_parameter_names, equation_solving_parameter_description, equation_solving_parameter_examples, first_time)

def get_plotting_argument_info(param_name : str, first_time : bool) -> str:
    return get_one_argument_info(param_name, reversed_plotting_parameter_names, plotting_parameter_description, plotting_parameter_examples, first_time)



# ABOUT SUBSCRIBING:
def get_group_link(group_id : Union[str, int]) -> str:
    return "https://vk.com/" + (group_id if isinstance(group_id, str) else ("club" + str(group_id)))

def get_text_for_non_subscribed(group_id : Union[str, int]) -> str:
    return f"Упс... Кажется, Вы не подписаны на нашу группу: {get_group_link(group_id)}. Подпишитесь, там много всего интересного - тогда поговорим 😉"

if __name__ == '__main__':
    print(get_group_link("math_jokes00") + ".")
    print(get_group_link(158141262) + ".")
