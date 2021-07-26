# Stoppers:
to_main_menu_text = "В главное меню"
aborting_texts = {
    "стоп",
    "начать",
    "хватит",
    "стой",
    "остановись",
    "перестань",
    "прекратить",

    "остановить",
    "остановить вычисления",
    "остановить вычисление",

    "всё заново",
    "сбросить операции",
    to_main_menu_text.lower(),
    "stop",
    "return"
}

# Commands
optimize_function_text = "Оптимизировать функцию"
solve_equation_text = "Решить уравнение"
plot_text = "Построить график"

command_texts = [
    optimize_function_text,
    solve_equation_text,
    plot_text,
    # "test1",
    # "test2",
    # "test3",
    # "test4",
    # "test5",
    # "test6",
]


###################################################################################################################################
# Parsing:

reserved_identifier_names = {
    # Constants:
    "e",
    "pi",
    "fi",
    "Fi",
    "inf",
    "Inf",
    "INF",

    # Usual math:
    "exp",
    "ln",
    "lg",
    "log",
    "root",

    "sqrt",
    "cbrt",
    "pow",

    "abs",
    "max",
    "min",
    "sgn",
    "sign",

    # Trigonometry:
    "sin",
    "cos",
    "tg",
    "ctg",
    "tan",
    "cot",
}


