import os
import time
from threading import Thread
import subprocess
from typing import List

from config import max_query_processing_time_sec, MathBot_root_dir

from mylang import print_red


def launch_in_new_thread(command_parts: List[str], output_path: str):
    print(f"Executing command: \"{' '.join(command_parts)}\" in new thread, output path is: {output_path}")

    def launch_command():
        # res_comm = "python" + " " + str(MathBot_root_dir / "MathBotFrontend" / "process_runner_main.py") + " " + output_path + " " + " ".join(command_parts)
        # print("Resultant command:", res_comm)
        # os.system(res_comm)


        try:
            subprocess.run(command_parts, timeout=max_query_processing_time_sec)
        except subprocess.TimeoutExpired:
            print_red(f"Execution of program {' '.join(command_parts)} took too long (> {max_query_processing_time_sec} seconds) "
                      f"=> write about it to file: {output_path}")
            out_file = open(output_path, "w")
            out_file.write("You query processing is timed out: it ran > " + str(max_query_processing_time_sec) + " seconds!")
            out_file.close()

    t = Thread(target = launch_command, args = ())
    t.daemon = True
    t.start()


if __name__ == '__main__':
    launch_in_new_thread(
        ["D:/Projects/MathBot/MathBotBackend/cmake-build-release/Math_bot_backend.exe", "solve", "D:/Projects/MathBot/queries/215659697/562.json"],
        "D:/Projects/MathBot/results/215659697/562.txt"
    )
    time.sleep(10)
    print("Processed everything!")
