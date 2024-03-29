from collections import defaultdict
from typing import List, Dict

import vk_api

# Angry!

waiting_angry_phrases = {
    0 : "Подождите, пожалуйста. Сейчас я обрабатываю ваш предыдущий вопрос. Если вдруг вы сказали что-нибудь дельное, то спросите это попозже...",
    1 : "Подождите, друг мой нетерпелиывй!",
    2 : "Подождите, сказано же Вам!",
    3 : "Ну сколько можно?! Достали!",
    4 : "Тяжёлый случай...",
    5 : "Ещё раз напишете - забаню!",
    6 :  "😡",
    7 :  "😡😡",
    8 :  "😡😡😡😡",
    9 :  "😡😡😡😡😡😡",
    10 : "😡😡😡😡😡😡😡😡",
    11 : "😡😡😡😡😡😡😡😡",
    12 : "😡😡😡😡😡😡",
    13 : "😡😡😡😡",
    14 : "😡😡",
    15 : "😡",
    16 : "..."
}

bad_commands_angry_phrases = {
    3: "Пожалуйста, выберите одну из предложенных опций",
    4: "К сожалению, данная опция мне не известна. Если хотите, чтобы она была добавлена, пишите на wolframalpha@wolframresearch.com",
    5: "Ещё раз введёте неправильную опцию - разозлюсь!",
    6: "АААААААААА!!! Не надо было меня доводить! Как можно быть настолько ... несообразительным, чтобы столько раз подряд не смочь правильно ввести команду???",
    7 :    "😡",
    8 :    "😡",
    9:     "😡😡",
    10 :   "😡😡😡",
    11 :   "😡😡😡😡",
    12 :   "😡😡😡😡",
    13 :   "😡😡😡",
    14 :   "😡😡",
    15 :   "😡",
    16 :   "😡",
    17 :    "..."
}



################################################################################################################################################################################
# Function optimization info:

function_optimization_parameters = \
[
    "function",
    "target_minimum",
    "variable_ranges"
]

function_optimization_parameter_names = \
{
    "function" : "Целевая функция",
    "target_minimum" : "Предполагаемый минимум",
    "variable_ranges" : "Диапазоны переменных"
}

reversed_function_optimization_parameter_names = \
{
    function_optimization_parameter_names[i] : i for i in function_optimization_parameter_names
}

function_optimization_parameter_description = \
{
    "function" : "Объект оптимизации. Разумеется, это обязательный параметр.",

    "target_minimum" : "Подтвердите, что целевая функция ограничена снизу на рассматриваемом множестве. "
                       "Для этого введите произвольную известную Вам нижнюю границу множества значений функции (на данном множестве). "
                       "В случае если введённое число не окажется минорирующим для исходной функции, бот будет работать с заметными погрешностями. "
                       "Ваше число: ",

    "variable_ranges" : "Для каждой переменной в Вашем уравнении нужно указать, на каком множестве её значений следует оптимизировать функцию. \
                        Для этого для каждой из переменных нужно указать её максимальное и минимальное значение. Будет найден максимум в этом диапазоне."
}


function_optimizing_parameter_examples = \
{
    "function" : "0.5 + (cos(sin(abs(x^2 - y^2)))^2 - 0.5) / (1 + 0.001(x^2 + y^2))^2",
    "target_minimum" : "0.1 или -23.9e30",
    "variable_ranges" : "x ∈ (-1; 10]; y: in 30.6 -> 100., 10 < z <= 11e-2"
}

################################################################################################################################################################################



# Solving equations:
################################################################################################################################################################################

equation_solving_parameters = \
[
    "function",
    "variable_ranges"
]

equation_solving_parameter_names = \
{
    "function" : "Уравнение",
    "variable_ranges" : "Диапазоны переменных"
}

reversed_equation_solving_parameter_names = \
{
    equation_solving_parameter_names[i] : i for i in equation_solving_parameter_names
}

equation_solving_parameter_description = \
{
    "function" : "Само уравнение. Разумеется, это обязательный параметр.",

    "variable_ranges" : "Для каждой переменной в Вашем уравнении нужно указать, на каком множестве её значений следует решать уравнение. "
    "Для этого для каждой из переменных нужно указать её максимальное и минимальное значение. Будет найден максимум в этом диапазоне."
}

equation_solving_parameter_examples = \
{
    "function" : "x^2 = -y**2",
    "variable_ranges" : function_optimizing_parameter_examples["variable_ranges"]
}
################################################################################################################################################################################


################################################################################################################################################################################
# Plotting:

plotting_parameters = \
[
    "functions",
    "variable_range"
]

plotting_parameter_names = \
{
    "functions" : "Функции",
    "variable_range" : "Диапазон переменной"
}

reversed_plotting_parameter_names = \
{
    plotting_parameter_names[i] : i for i in plotting_parameter_names
}

plotting_parameter_description = \
{
    "functions" : "Функции для отображения на графике.",

    "variable_range" : "Для переменной нужно указать, на каком множестве её значений следует Строить график. "
    "Для этого для переменной нужно указать её максимальное и минимальное значение."
}

plotting_parameter_examples = \
{
    "functions" : "0.5x + 5 && 3sin(x) && 5sqrt(abs(x) - 5) && 10sgn(x) * sqrt(x)",
    "variable_range" : "x ∈ (-1; 10]"
}




