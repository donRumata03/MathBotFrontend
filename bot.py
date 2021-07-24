import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import api_wrapper
from api_wrapper import get_name_by_id, get_chat_info

from threading import Timer


from mylang import *

from speaker import *
from fast_input_processor import *


class Bot:
    key: str = ""
    vk: vk_api.vk_api.VkApiMethod = None
    uploader: vk_api.upload.VkUpload
    my_id = 0
    cached_names = {}
    subscribe_check_group_name: str

    # User states
    user_states = defaultdict(int)  # Contains the states of users

    processing_user_ids = {}  # To understand which files to look for

    user_anger_state = defaultdict(int)  # To determine, how much anger to express
    user_anger_bad_args = defaultdict(int)  #

    user_last_message_indexes = {}  # To understand which messages are processed

    user_query_name = {}  # It might be nothing or a command name which args are being scraper from user`s head
    user_query_args = {}  # The args for operation being scraped
    user_argument_names = {}  # If user is supposed to write the argument, argument`s name will be situated here.

    user_operation_identifiers = {}  # Each operation has its own identifier

    print_buffer = []  # Lines to be printed at the end of the next iteration of mainloop

    def __init__(self, key: str, filename: str = default_filename,
                 subscribe_check_group_name: str = default_subscribe_check_group_name):
        self.session = vk_api.VkApi(token = key)
        self.vk = self.session.get_api()

        self.my_id = MY_ID
        self.subscribe_check_group_name = subscribe_check_group_name

        self.uploader = vk_api.VkUpload(self.session)

        if os.path.exists(filename):
            self.deserialize(filename)

    def reset_user(self, user_id):
        """
        It doesn't delete all info about user. It only sets the dialog state to default
        """
        self.user_states[user_id] = USER_STATE_NOTHING
        self.processing_user_ids.pop(user_id, "I don`t need value, but I also don`t need exception")

        self.user_anger_state.pop(user_id, "I don`t need value, but I also don`t need exception")
        self.user_anger_bad_args.pop(user_id, "I don`t need value, but I also don`t need exception")

        self.user_query_args.pop(user_id, "I don`t need value, but I also don`t need exception")
        self.user_query_name.pop(user_id, "I don`t need value, but I also don`t need exception")

        self.user_argument_names.pop(user_id, "I don`t need value, but I also don`t need exception")

        self.alert_good_option(user_id)

    ################################
    ###     Working with api     ###
    ################################

    def get_name(self, user_id):
        if user_id in self.cached_names:
            return self.cached_names[user_id]
        username = get_name_by_id(user_id, self.vk)
        self.cached_names[user_id] = username
        return username

    def send_message(self, user_id: int, message: str, **kwargs):
        keyboard = kwargs.get("keyboard", None)
        func_kwargs = {}
        if keyboard is not None:
            func_kwargs["keyboard"] = keyboard.get_keyboard()

        self.vk.messages.send(
            message = message,
            peer_id = user_id,  # Could be user id, but to be more generic...
            random_id = vk_api.utils.get_random_id(),
            **func_kwargs
        )

    def send_image(self, user_id: int, image_path: str):
        photo_container = self.uploader.photo_messages(photos = image_path, peer_id = user_id)[0]
        attachments = [f"photo{photo_container['owner_id']}_{photo_container['id']}"]

        self.vk.messages.send(
            user_id = user_id,
            attachment = ",".join(attachments),
            random_id = vk_api.utils.get_random_id()
        )

    def show_command_keyboard(self, user_id: int):
        self.print(f"Sending command keyboard to {self.get_name(user_id)}")

        keyboard = VkKeyboard(one_time = True)

        #
        # keyboard.add_button(optimize_function_text, color = VkKeyboardColor.POSITIVE)
        # keyboard.add_button(solve_equation_text, color = VkKeyboardColor.NEGATIVE)
        #

        total_commands = len(command_texts)
        for command_index in range(total_commands):
            keyboard.add_button(command_texts[command_index], color = command_button_color)
            if command_index != 0 and not (command_index + 1) % MAX_COMMANDS_IN_KEYBOARD_ROW and command_index != total_commands - 1:
                keyboard.add_line()

        self.send_message(
            user_id,
            "В данный момент Вы не находитесь ни в одном особенном виде общения, причём Ваше сообщение не является корректной командой Quick Input Mode. "
            "Пожалуйста, выберите необходимую опцию на клавиатуре, введите её самостоятельно, или же исползуйте команды Quick Input Mode.",
            keyboard = keyboard
        )

    def default_can_be_set(self, user_id, button_label: str) -> bool:
        if user_id not in self.user_query_name:
            return False

        command_name = self.user_query_name[user_id]

        if command_name == optimize_function_text:
            if "variables" in self.user_query_args[user_id]:
                return True
            return button_label != "variable_ranges"

        elif command_name == solve_equation_text:
            if "variables" in self.user_query_args[user_id]:
                return True
            return button_label != "variable_ranges"

        elif command_name == plot_text:
            if "functions" in self.user_query_args[user_id]:
                return True
            return button_label != "variable_range"

        else:
            print(console_color.RED + "Unknown command name:", command_name + console_color.END)

    def show_argument_keyboard(self, user_id: int, arguments: List[str], argument_names: Dict[str, str], can_be_set: Callable = default_can_be_set):
        self.print(f"Sending argument keyboard to \"{self.get_name(user_id)}\"")

        keyboard = VkKeyboard(one_time = True)

        color_set = VkKeyboardColor.NEGATIVE
        color_not_set = VkKeyboardColor.POSITIVE
        color_first_not_set = VkKeyboardColor.PRIMARY

        def get_color(arg, is_first: bool = False) -> VkKeyboardColor:
            return VkKeyboardColor.NEGATIVE if not can_be_set(self, user_id, arg) else (
                color_set if arg in self.user_query_args[user_id] else (
                    color_not_set if not is_first else color_first_not_set))

        first_arg = arguments[0]
        keyboard.add_button(argument_names[first_arg], color = get_color(first_arg, True))
        keyboard.add_line()
        for this_arg in arguments[1:]:
            keyboard.add_button(argument_names[this_arg], color = get_color(this_arg, False))

        keyboard.add_line()
        keyboard.add_button(to_main_menu_text, color = VkKeyboardColor.SECONDARY)

        self.send_message(
            user_id,
            "Выберите аргумент, значение которого хотите установить / изменить.",
            keyboard = keyboard
        )

    def send_stop_button(self, user_id, stop_or_main_menu = True):
        keyboard = VkKeyboard(one_time = True)
        keyboard.add_button("Стоп" if stop_or_main_menu else "В главное меню", VkKeyboardColor.NEGATIVE)
        self.send_message(user_id, "Вы можете остановить процесс...", keyboard = keyboard)

    def send_argument_description(self, user_id, argument: str, argument_names: Dict[str, str], argument_descriptions: Dict[str, str], argument_samples: Dict[str, str]):
        message = f"Аргумент \"{argument_names[argument]}\": \"{argument_descriptions[argument]}\". Пример использования: {argument_samples[argument]}"
        self.send_message(user_id, message)


    ################################
    ######      Printing        ####
    ################################

    def print(self, something: Any):
        self.print_buffer.append(something)

    def flush(self):
        for line in self.print_buffer:
            print(line)
        self.print_buffer.clear()

    ################################
    ###    Message managing      ###
    ################################

    def get_unread_messages(self, user_id: int, messages: list):
        last_message_id = max([message["id"] for message in messages])
        last_prev_id = self.user_last_message_indexes[user_id] if user_id in self.user_last_message_indexes else -228

        res = []
        for message in reversed(messages):
            if message["id"] > last_prev_id and message["from_id"] != self.my_id:
                res.append(message)

        self.user_last_message_indexes[user_id] = last_message_id
        return res

    ################################
    ###         Anger            ###
    ################################

    # No waiting Anger:
    def update_user_waiting_anger_state(self, user_id: int) -> str:
        user_state_now = self.user_anger_state[user_id]
        max_anger = max(waiting_angry_phrases.keys())
        if user_state_now != max_anger:
            self.user_anger_state[user_id] += 1
        return waiting_angry_phrases[user_state_now]

    def express_waiting_anger(self, user_id: int):
        angry_message = self.update_user_waiting_anger_state(user_id)
        self.send_message(user_id, angry_message)

    # Bad commands anger:
    def alert_bad_option(self, user_id: int):
        self.print(f"Bad option for user {self.get_name(user_id)}")
        angers = bad_commands_angry_phrases.keys()
        max_anger = max(angers)
        min_anger = min(angers)

        this_anger = self.user_anger_bad_args[user_id]

        if this_anger >= min_anger:
            self.send_message(user_id, bad_commands_angry_phrases[this_anger])

        if this_anger < max_anger:
            self.user_anger_bad_args[user_id] = this_anger + 1

    def alert_good_option(self, user_id: int):
        self.print(f"Good option for user {self.get_name(user_id)}")
        self.user_anger_bad_args[user_id] = 0


    ###########################################################
    ###                 Working with optimizer              ###
    ###########################################################

    def launch_process(self, user_id: int, chat_message_id: int):
        self.alert_good_option(user_id)
        process_name = self.user_query_name[user_id]
        args = self.user_query_args[user_id]
        self.send_message(user_id, f"Вы выбрали опцию {process_name}. Аргументы: \"{args}\". Процесс запущен.")

        if process_name == optimize_function_text:
            launch_function_optimization(user_id, chat_message_id, self.get_name(user_id), **args)

        elif process_name == solve_equation_text:
            launch_equation_solving(user_id, chat_message_id, self.get_name(user_id), **args)

        elif process_name == plot_text:
            launch_plotting(user_id, chat_message_id, self.get_name(user_id), **args)

        self.user_states[user_id] = USER_STATE_IN_PROCESS
        self.processing_user_ids[user_id] = chat_message_id
        self.send_stop_button(user_id)

    def answer_results(self):
        temp_processing = self.processing_user_ids.copy()
        for user_id in temp_processing:
            message_id = self.processing_user_ids[user_id]
            # print(f"Answering: {user_id, message_id}")
            ans_data = get_computational_results(user_id, message_id, self.user_query_name[user_id])
            if ans_data is None:
                # print("No data for user:", self.get_name(user_id))
                continue

            # Change user state:
            user_process = self.user_query_name[user_id]
            del self.user_query_name[user_id]

            # Actual answering:
            res_message : str = f"_____________________________________________________\nУважаемый {self.get_name(user_id)}, "

            if user_process == optimize_function_text or user_process == solve_equation_text:
                res_message += f"вот ответ на Ваш запрос " \
                              f"{'об оптимизации функции' if user_process == optimize_function_text else 'о решении уравнения'}" \
                              f" (\"{self.user_query_args[user_id]['function']}\") : \n{ans_data}"
            elif user_process == plot_text:
                if not ans_data:  # Empty string => no errors
                    res_message += f"вот Ваш график, который Вы просили:"
                else:
                    res_message += f"к Великому сожалению, у меня не получилось построить запрошенный график функций {self.user_query_args[user_id]['functions']}. Возникла эта ошибка: {ans_data}"


            self.print("Answering: \"" + res_message + "\"")

            self.send_message(user_id, res_message)

            if user_process == plot_text and not ans_data:
                # Send the graph image:
                graph_path = get_graph_path(user_id, message_id)
                self.print(f"Sending photo from path \"{graph_path}\" to user \"{self.get_name(user_id)}\"")
                self.send_image(user_id, image_path = get_graph_path(user_id, message_id))

            self.reset_user(user_id)


    ###########################################################
    ###                 Processing args                     ###
    ###########################################################
    def process_eq_solving_args(self, user_id: int, text: str, chat_message_id: int):
        if OUTPUT_DEBUG_INFORMATION:
            self.print("Processing equation solving command args...")

        # Useful functions:
        def has_this_all_args():
            return has_all_args(equation_solving_parameters, **self.user_query_args[user_id])

        def try_end_args_processing():
            if has_this_all_args():
                self.launch_process(user_id, chat_message_id)
                return True
            return False



        if user_id in self.user_argument_names:
            """ User is supposed to write the argument value """

            this_arg_name = self.user_argument_names[user_id]
            this_arg = reversed_equation_solving_parameter_names[this_arg_name]
            raw_text = text
            # Validation:
            ok: bool = False
            argument_value = None

            if this_arg == "function":
                this_res = check_equation(raw_text)
                self.print("Variables are: " + str(this_res))
                if this_res is None:
                    ok = False
                else:
                    ok = True
                    self.user_query_args[user_id]["variables"] = this_res
                    argument_value = raw_text
                    self.send_message(user_id, f"Уравнение принято. Переменные в Вашем уравнении: {this_res}")

            elif this_arg == "variable_ranges":
                ranges = param_parser.scrape_ranges(raw_text, self.user_query_args[user_id]["variables"])
                ok = not isinstance(ranges, str)
                if ok:
                    self.send_message(user_id, f"Диапазоны переменных установлены! Вот они: {ranges}")
                    argument_value = ranges
                else:
                    self.send_message(user_id, ranges)  # There is an error message in the string

            if ok:
                # User has given a correct argument value:
                self.user_query_args[user_id][this_arg] = argument_value
                really_has_this_all_args = try_end_args_processing()
                if really_has_this_all_args:
                    return
                # So, not all args are processed, show keyboard!
                self.send_message(user_id, "Отлично! Но Вы указали не все аргументы.")
                self.alert_good_option(user_id)
                self.show_argument_keyboard(user_id, equation_solving_parameters,
                                            equation_solving_parameter_names)
                self.user_argument_names.pop(user_id)

            else:
                # User has given an incorrect argument value:

                self.send_message(user_id,
                                  "Вы допустили ошибку при указании значения аргумента. Пожалуйста, повторите попытку!")
                argument_info = get_solving_argument_info(this_arg_name, False)
                self.send_message(user_id, argument_info)
                self.alert_bad_option(user_id)

        else:
            """ User is supposed to write the argument name """

            info_text = get_solving_info_with_given_args(False, **self.user_query_args[user_id])

            if text not in reversed_equation_solving_parameter_names:
                self.alert_bad_option(user_id)
                self.send_message(user_id,
                                  f"Нет аргумента комманды {self.user_query_name[user_id]} с таким именем (\"{text}\")! Выберите из предложеных.")
                self.send_message(user_id, info_text)
                self.show_argument_keyboard(user_id, equation_solving_parameters, equation_solving_parameter_names)

            elif text == equation_solving_parameter_names["variable_ranges"] and "variables" not in self.user_query_args[user_id]:
                self.send_message(user_id, "Пожалуйста, сначала укажите само уравнение, а потом уже - диапазоны переменных! (Чтобы можно было проверить эти диапазоны).")
                self.show_argument_keyboard(user_id, equation_solving_parameters, equation_solving_parameter_names)
                self.alert_bad_option(user_id)

            else:
                self.alert_good_option(user_id)
                self.user_argument_names[user_id] = text

                if reversed_equation_solving_parameter_names[text] in self.user_query_args[user_id] and text == equation_solving_parameter_names["function"]:
                    # If we change function, delete ranges to check them
                    self.print("Deleting ranges!")
                    self.user_query_args[user_id].pop("variable_ranges", None)

                argument_info = get_solving_argument_info(text, True)

                self.send_message(user_id,
                                  f"Отлично! Теперь укажите значение этого аргумента." if reversed_equation_solving_parameter_names[text] not in self.user_query_args[user_id]
                                  else "Хорошо. Вы решили поменять значение этого аргумента...")

                self.send_message(user_id, argument_info)

        try_end_args_processing()

    # Function Optimization Arguments:
    def process_func_optimizing_args(self, user_id : int, text: str, chat_message_id: int):
        if OUTPUT_DEBUG_INFORMATION:
            self.print("Processing function optimizing command args...")

        def has_this_all_args():
            return has_all_args(function_optimization_parameters, **self.user_query_args[user_id])

        def try_end_args_processing():
            if has_this_all_args():
                self.launch_process(user_id, chat_message_id)
                return True
            return False

        if user_id in self.user_argument_names:
            # User is supposed to write the argument value
            this_arg_name = self.user_argument_names[user_id]
            this_arg = reversed_function_optimization_parameter_names[this_arg_name]
            raw_value = text
            # Validation:
            ok: bool = False
            value = None

            if this_arg == "function":
                self.print("Processing argument: function...")
                this_res = check_function(raw_value)
                self.print("Variables are: " + str(this_res))
                if this_res is None:
                    ok = False
                else:
                    ok = True
                    self.user_query_args[user_id]["variables"] = this_res
                    value = raw_value
                    self.send_message(user_id, f"Функция принята. Переменные в Вашей функции: {this_res}")

            elif this_arg == "variable_ranges":
                ranges = param_parser.scrape_ranges(raw_value, self.user_query_args[user_id]["variables"])
                ok = not isinstance(ranges, str)
                value = ranges
                if ok:
                    self.send_message(user_id, f"Диапазоны переменных установлены! Вот они: {ranges}")
                else:
                    self.send_message(user_id, ranges)  # There is an error message in the string

            elif this_arg == "target_minimum":
                check_res = check_target_minimum(raw_value)
                ok = check_res is not None
                value = check_res
                if ok:
                    self.send_message(user_id, f"Предполагаемый минимум установлен! Вот он: {value}")

            if ok:
                self.user_query_args[user_id][this_arg] = value
                really_has_this_all_args = try_end_args_processing()
                if really_has_this_all_args:
                    return
                # So, not all args are processed, show keyboard!
                self.send_message(user_id, "Отлично! Но Вы указали не все аргументы.")
                self.alert_good_option(user_id)
                self.show_argument_keyboard(user_id, function_optimization_parameters,
                                            function_optimization_parameter_names)
                self.user_argument_names.pop(user_id)

            else:
                self.send_message(user_id,
                                  "Вы допустили ошибку при указании значения аргумента. Пожалуйста, повторите попытку!")
                argument_info = get_optimizing_argument_info(this_arg_name, False)
                self.send_message(user_id, argument_info)
                self.alert_bad_option(user_id)


        else:
            # User is supposed to write the argument name
            # self.print("User is supposed to write the argument name now...")
            info_text = get_optimizing_info_with_given_args(False, **self.user_query_args[user_id])

            if text not in reversed_function_optimization_parameter_names:
                self.alert_bad_option(user_id)
                self.send_message(user_id,
                                  f"Нет аргумента комманды {self.user_query_name[user_id]} с таким именем (\"{text}\")! Выберите из предложеных.")
                self.send_message(user_id, info_text)
                self.show_argument_keyboard(user_id, function_optimization_parameters,
                                            function_optimization_parameter_names)

            elif text == function_optimization_parameter_names["variable_ranges"] and "variables" not in \
                    self.user_query_args[user_id]:
                self.send_message(user_id,
                                  "Пожалуйста, сначала укажите саму функцию, а потом уже - диапазоны переменных! (Чтобы можно было проверить эти диапазоны).")
                self.show_argument_keyboard(user_id, function_optimization_parameters,
                                            function_optimization_parameter_names)
                self.alert_bad_option(user_id)

            else:
                self.alert_good_option(user_id)
                self.user_argument_names[user_id] = text
                if reversed_function_optimization_parameter_names[text] in self.user_query_args[user_id] and text == \
                        function_optimization_parameter_names["function"]:  # If we change function, delete ranges to check them
                    self.print("Deleting ranges!")
                    self.user_query_args[user_id].pop("variable_ranges", None)

                argument_info = get_optimizing_argument_info(text, True)
                self.send_message(user_id, f"Отлично! Теперь укажите значение этого аргумента." if
                reversed_function_optimization_parameter_names[text] not in self.user_query_args[
                    user_id] else "Хорошо. Вы решили поменять значение этого аргумента...")
                self.send_message(user_id, argument_info)

        try_end_args_processing()


    # Plotting Arguments:
    def process_plotting_args(self, user_id: int, text: str, chat_message_id: int):
        if OUTPUT_DEBUG_INFORMATION:
            self.print("Processing plotting command args...")

        # Useful functions:
        def has_this_all_args():
            return has_all_args(plotting_parameters, **self.user_query_args[user_id])

        def try_end_args_processing():
            if has_this_all_args():
                self.launch_process(user_id, chat_message_id)
                return True
            return False

        if user_id in self.user_argument_names:
            """ User is supposed to write the argument value """

            this_arg_name = self.user_argument_names[user_id]
            this_arg = reversed_plotting_parameter_names[this_arg_name]
            raw_text = text
            # Validation:
            ok: bool = False
            argument_value = None

            if this_arg == "functions":
                this_res = check_plotting_functions(raw_text)
                self.print("Variables are: " + str(this_res))
                if isinstance(this_res, str):
                    ok = False
                    self.send_message(user_id, "There`s an error with the total number of variables in your functions: " + this_res)

                else:
                    ok = True
                    self.user_query_args[user_id]["variables"] = this_res
                    argument_value = raw_text
                    self.send_message(user_id, f"Ваши функции приняты. Переменная в них: {this_res[0]}")

            elif this_arg == "variable_range":
                ranges = param_parser.scrape_ranges(raw_text, self.user_query_args[user_id]["variables"])
                ok = not isinstance(ranges, str)
                if ok:
                    self.send_message(user_id, f"Диапазон переменной установлен! Вот он: {ranges}")
                    argument_value = ranges
                else:
                    self.send_message(user_id, ranges)  # There is an error message in the string

            if ok:
                # User has given a correct argument value:
                self.user_query_args[user_id][this_arg] = argument_value
                really_has_this_all_args = try_end_args_processing()
                if really_has_this_all_args:
                    return
                # So, not all args are processed, show keyboard!
                self.send_message(user_id, "Отлично! Но Вы указали не все аргументы.")
                self.alert_good_option(user_id)
                self.show_argument_keyboard(user_id, plotting_parameters,
                                            plotting_parameter_names)
                self.user_argument_names.pop(user_id)

            else:
                # User has given an incorrect argument value:

                self.send_message(user_id,
                                  "Вы допустили ошибку при указании значения аргумента. Пожалуйста, повторите попытку!")
                argument_info = get_plotting_argument_info(this_arg_name, False)
                self.send_message(user_id, argument_info)
                self.alert_bad_option(user_id)

        else:
            """ User is supposed to write the argument name """

            info_text = get_plotting_info_with_given_args(False, **self.user_query_args[user_id])

            if text not in reversed_plotting_parameter_names:
                self.alert_bad_option(user_id)
                self.send_message(user_id,
                                  f"Нет аргумента комманды {self.user_query_name[user_id]} с таким именем (\"{text}\")! Выберите из предложеных.")
                self.send_message(user_id, info_text)
                self.show_argument_keyboard(user_id, plotting_parameters, plotting_parameter_names)

            elif text == plotting_parameter_names["variable_range"] and "variables" not in self.user_query_args[user_id]:
                self.send_message(user_id,
                                  "Пожалуйста, сначала укажите сами функции, а потом уже - диапазон переменной! (Чтобы можно было проверить этот диапазон).")
                self.show_argument_keyboard(user_id, plotting_parameters, plotting_parameter_names)
                self.alert_bad_option(user_id)

            else:
                self.alert_good_option(user_id)
                self.user_argument_names[user_id] = text

                if reversed_plotting_parameter_names[text] in self.user_query_args[user_id] and text == \
                        plotting_parameter_names["functions"]:
                    # If we change function, delete ranges to check them
                    self.print("Deleting variable range!")
                    self.user_query_args[user_id].pop("variable_range", None)

                argument_info = get_plotting_argument_info(text, True)

                self.send_message(user_id,
                                  f"Отлично! Теперь укажите значение этого аргумента." if
                                  reversed_plotting_parameter_names[text] not in self.user_query_args[user_id]
                                  else "Хорошо. Вы решили поменять значение этого аргумента...")

                self.send_message(user_id, argument_info)

        try_end_args_processing()

    ###########################################################
    ###             Processing command name                 ###
    ###########################################################
    def process_command_name(self, user_id: int, command: str):
        """
        command should be one of known!
        """

        self.user_query_name[user_id] = command
        self.user_query_args[user_id] = {}
        self.user_states[user_id] = USER_STATE_PROCESSING_ARGS

        info_text = ""

        if command == optimize_function_text:
            info_text = get_optimizing_info_with_given_args(True, **self.user_query_args[user_id])
        elif command == solve_equation_text:
            info_text = get_solving_info_with_given_args(True, **self.user_query_args[user_id])
        elif command == plot_text:
            info_text = get_plotting_info_with_given_args(True, **self.user_query_args[user_id])

        self.send_message(user_id, info_text)

        if command == optimize_function_text:
            self.show_argument_keyboard(user_id, function_optimization_parameters, function_optimization_parameter_names)
        elif command == solve_equation_text:
            self.show_argument_keyboard(user_id, equation_solving_parameters, equation_solving_parameter_names)
        elif command == plot_text:
            self.show_argument_keyboard(user_id, plotting_parameters, plotting_parameter_names)

    ###########################################################
    ###             Message processing routine              ###
    ###########################################################
    def process_message(self, message_data: dict, user_id: int):
        text: str = message_data["text"]
        chat_message_id: int = message_data["conversation_message_id"]

        if OUTPUT_DEBUG_INFORMATION:
            username = self.get_name(user_id)
            self.print(f"Processing message \"{text}\" from user: \"{username}\"")


        if text.startswith("[[ask]]") or text.startswith("[ask]"):
            naked_message = text[len("[[ask]]"):].strip() if text.startswith("[[ask]]") else text[len("[ask]"):].strip()
            self.print(console_color.BLUE + "Message to ADMINS detected: " + naked_message + console_color.END)
            self.send_message(group_with_messages_for_admins_id, f"Message from a subscriber {self.get_name(user_id)} (https://vk.com/id{str(user_id)}): \"" + naked_message + "\"")
            self.send_message(user_id, "Спасибо за активность! Ваше сообщение будет отправленно админам. Ждите ответа!")
            return

        # is_subscribed: bool = api_wrapper.user_is_in_community(self.vk, user_id, self.subscribe_check_group_name)
        # if not is_subscribed:
        #     self.send_message(user_id, speaker.get_text_for_non_subscribed(self.subscribe_check_group_name))
        #     return

        if text in aborting_texts:
            self.reset_user(user_id)
            self.show_command_keyboard(user_id)
            return

        if self.user_states[user_id] == USER_STATE_NOTHING:
            fast_input_try = process_fast_input(text, user_id, chat_message_id, self.get_name(user_id))
            if fast_input_try is not None:
                # It`s a correct fast input expression:
                received_command_name = fast_input_try[0]
                received_args = fast_input_try[1]

                # Modify the flags:
                self.user_states[user_id] = USER_STATE_IN_PROCESS
                self.processing_user_ids[user_id] = chat_message_id

                if received_command_name == "optimize":
                    self.user_query_name[user_id] = optimize_function_text
                elif received_command_name == "solve":
                    self.user_query_name[user_id] = solve_equation_text
                if received_command_name == "plot":
                    self.user_query_name[user_id] = plot_text

                self.user_query_args[user_id] = received_args

                # Inform the user, that the process is already launched:
                self.send_message\
                    (user_id,
                        f"Уважаемый {self.get_name(user_id)}, кажется, Ваше сообщение \"{text}\" является корректной командой Quick Input Mode, поэтому запущен процесс "
                        f"\"{received_command_name}\" с аргументами: \n{json.dumps(received_args, indent = 4, ensure_ascii = False)}\n Ждите завершения обраБОТки запроса."
                    )
                print(f"{self.get_name(user_id)}`s message is QIM!")

                return


        splitted_text = text.lower().split()
        if splitted_text and splitted_text[0] == "я" and splitted_text[1] == "дарт":
            self.print(console_color.BLUE + "Пасхалка найдена!" + console_color.END)
            self.send_message(user_id, "А я император Палпатин!")
            return

        if self.user_states[user_id] == USER_STATE_IN_PROCESS:
            self.express_waiting_anger(user_id)
            return

        if self.user_states[user_id] == USER_STATE_NOTHING:
            if text in command_texts:
                self.process_command_name(user_id, text)
                self.alert_good_option(user_id)
                return
            else:
                self.alert_bad_option(user_id)
                self.show_command_keyboard(user_id)
                return

        # USER STATE IS DEFINITELY USER_STATE_PROCESSING_ARGS, so the action depends on the number :

        if self.user_query_name[user_id] == optimize_function_text:
            self.process_func_optimizing_args(user_id, text, chat_message_id)
            return

        if self.user_query_name[user_id] == solve_equation_text:
            self.process_eq_solving_args(user_id, text, chat_message_id)
            return

        if self.user_query_name[user_id] == plot_text:
            self.process_plotting_args(user_id, text, chat_message_id)
            return


    ###########################################################
    ###                         Mainloop                    ###
    ###########################################################
    def mainloop(self):
        self.print("__________________________________________________________________")
        self.answer_results()

        chats = self.vk.messages.getConversations(filter = "unread")["items"]
        to_utf8_json_file(chats, "test_messages.json")

        for chat in chats:
            chat_info = chat["conversation"]
            user_info = chat_info["peer"]
            if "id" not in user_info:
                continue
            user_id = user_info["id"]
            chat_info = get_chat_info(user_id, self.vk)

            to_utf8_json_file(chat_info, "test_chat.json")

            unread_messages = self.get_unread_messages(user_id, chat_info)

            if OUTPUT_DEBUG_INFORMATION and unread_messages:
                self.print(f"Got {len(unread_messages)} messages from user \"{self.get_name(user_id)}\"")

            for message in unread_messages:
                self.process_message(message, user_id)

        self.serialize()

        self.print("__________________________________________________________________")
        if len(self.print_buffer) > 2:  # If there is something useful - something but the two stripes...
            self.flush()
        self.print_buffer.clear()

        t = Timer(mainloop_delay_sec, self.mainloop)
        t.start()


    ###########################################################
    ###########           Working with database         #######
    ###########################################################

    def serialize(self, filename: str = default_filename):
        result = {
            'cached_names': self.cached_names,
            'user_last_message_indexes': self.user_last_message_indexes,
            'user_states': self.user_states,

            'processing_user_ids': self.processing_user_ids,
            'user_anger_state': self.user_anger_state,
            'user_anger_bad_args': self.user_anger_bad_args,

            'user_query_name': self.user_query_name,
            'user_query_args': self.user_query_args,
            'user_argument_names': self.user_argument_names
        }
        to_utf8_json_file(result, filename)

    def deserialize(self, filename: str = default_filename):
        resource = from_utf8_json_file(filename)

        cached_names = resource["cached_names"] if "cached_names" in resource else {}
        user_last_message_indexes = resource[
            "user_last_message_indexes"] if "user_last_message_indexes" in resource else {}
        processing_user_ids = resource["processing_user_ids"] if "processing_user_ids" in resource else {}
        user_anger_bad_args = resource["user_anger_bad_args"] if "user_anger_bad_args" in resource else {}
        user_anger_state = resource["user_anger_state"] if "user_anger_state" in resource else {}
        user_query_name = resource["user_query_name"] if "user_query_name" in resource else {}
        user_query_args = resource["user_query_args"] if "user_query_args" in resource else {}
        user_states = resource["user_states"] if "user_states" in resource else {}
        user_argument_names = resource["user_argument_names"] if "user_argument_names" in resource else {}

        self.cached_names = {int(i): cached_names[i] for i in cached_names}
        self.user_states = defaultdict(int, {int(i): user_states[i] for i in user_states})
        self.user_last_message_indexes = {int(i): user_last_message_indexes[i] for i in user_last_message_indexes}
        self.user_anger_state = defaultdict(int, {int(i): user_anger_state[i] for i in user_anger_state})
        self.user_query_args = {int(i): user_query_args[i] for i in user_query_args}
        self.user_query_name = {int(i): user_query_name[i] for i in user_query_name}
        self.user_argument_names = {int(i): user_argument_names[i] for i in user_argument_names}
        self.user_anger_bad_args = defaultdict(int, {int(i): user_anger_bad_args[i] for i in user_anger_bad_args})
        self.processing_user_ids = {int(i): processing_user_ids[i] for i in processing_user_ids}

    def get_all_usernames(self):
        return [self.cached_names[i] for i in self.cached_names]

    def get_user_number(self):
        return len(self.get_all_usernames())

    def print_users(self):
        user_names = self.get_all_usernames()
        print(f"At the moment I have {len(user_names)} user{'s' if len(user_names) != 1 else ''}:")
        print_as_json(user_names)


###########################################################
###                     MAIN                            ###
###########################################################
if __name__ == '__main__':
    bot = Bot(default_key)
    bot.print_users()
    # bot.reset_user(215659697)
    bot.mainloop()
