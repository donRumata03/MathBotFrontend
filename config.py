from vk_api.keyboard import VkKeyboardColor


# default_key = "b8e34ba2603a410e101f19797d1ef3c412fb8c52a78580c05d7a20ac48e3a8ba1294dcba4ebf2cd9dcf9e"
default_key = "f25ac6c094ecc9bfc1a7e0f37b739a800bca9dd5db3fa00b1c1d18dcf671c5d25951159fc4c966e5da7ba"
# manage_key = "82066d27a1bd4961a16bf1cbf9a2ba48bbb55bd38a5340ce01db2f5e5b11b328b0d8de7c7f584d5e2b04a"

mainloop_delay_sec = 0.1
debug = True
default_filename = "bot_temp.json"

# solver_path = r"D:\Projects\Math_Bot\optimizer.exe"
solver_path = r"D:\Projects\Math_bot\Math_bot_backend\cmake-build-release\Math_bot_backend.exe"

results_dir = r"D:\Projects\Math_Bot\results"
query_dir = r"D:\Projects\Math_Bot\queries"

MY_ID = -158141262
default_subscribe_check_group_name = "math_jokes00"
# group_with_messages_for_admins_id = 447186473 + 2000000000
group_with_messages_for_admins_id = 2 + 2000000000

intelligent_mode_on = True


# User states:
USER_STATE_NOTHING = 0
USER_STATE_PROCESSING_ARGS = 1
USER_STATE_IN_PROCESS = 2

# Appearance:
MAX_COMMANDS_IN_KEYBOARD_ROW = 2
command_button_color = VkKeyboardColor.PRIMARY  # It`s blue, green might be even better
