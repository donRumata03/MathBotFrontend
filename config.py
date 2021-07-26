import os
import pathlib
from enum import Enum

from inspect import getsourcefile
from os.path import abspath
from pathlib import Path

from vk_api.keyboard import VkKeyboardColor

MathBot_root_dir = Path(abspath(getsourcefile(lambda: 0))).parent.parent.absolute()
print("MathBot_root_dir is:", MathBot_root_dir)


class BotInstance(Enum):
	MAIN_MATH_BOT = 1
	TEST_MATH_BOT = 2
	TEST_TEST_MATH_BOT = 3

######################################################################################################
bot_instance = BotInstance.TEST_MATH_BOT       ###### <-- The thing to change          ##########
######################################################################################################


""" Settings depending on bot instance """
if bot_instance == BotInstance.MAIN_MATH_BOT:
	print("?")
	exit(3)

elif bot_instance == BotInstance.TEST_MATH_BOT:
	print("Running Test MathBot...")
	default_key = "f25ac6c094ecc9bfc1a7e0f37b739a800bca9dd5db3fa00b1c1d18dcf671c5d25951159fc4c966e5da7ba" ## <- for test math bot
	default_filename = "test_bot_temp.json"
	group_with_messages_for_admins_id = 2 + 2000000000
	MY_ID = -158141262


elif bot_instance == BotInstance.TEST_TEST_MATH_BOT:
	print("Running TestTest MathBot...")
	default_key = "55d251c9afe9dc58169766e04fd96b3629a179575f03b0de437f047aa2030273af044ca531d2f2f9cc66f" ## <- for test test math bot
	default_filename = "test_test_bot_temp.json"
	group_with_messages_for_admins_id = 1 + 2000000000
	MY_ID = -199959551


mainloop_delay_sec = 0.1
OUTPUT_DEBUG_INFORMATION = True

OS = None

if os.name == "posix":
	# There are no .exe's in linux...
	OS = "linux"
	executable_name = "Math_bot_backend"
elif os.name == "nt":
	OS = "windows"
	executable_name = "Math_bot_backend.exe"
else:
	print(f"Unknown system name: {os.name}")
	exit(3)

solver_path = f"{MathBot_root_dir}/MathBotBackend/cmake-build-release/{executable_name}"

results_dir = f"{MathBot_root_dir}/results"
query_dir = f"{MathBot_root_dir}/queries"

default_subscribe_check_group_name = "math_jokes00"

intelligent_mode_on = True


# User states:
USER_STATE_NOTHING = 0
USER_STATE_PROCESSING_ARGS = 1
USER_STATE_IN_PROCESS = 2

# Appearance:
MAX_COMMANDS_IN_KEYBOARD_ROW = 2
command_button_color = VkKeyboardColor.PRIMARY  # It`s blue, green might be even better

# System-specific library:

if os.name == "posix":
	white_button_coloring = VkKeyboardColor.SECONDARY
elif os.name == "nt":
	white_button_coloring = VkKeyboardColor.DEFAULT

# Regulating performance
optimizing_iterations = solving_iterations = 1000000
max_query_processing_time_sec = 30
