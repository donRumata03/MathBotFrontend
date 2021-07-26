from threading import Thread
import subprocess

from config import max_query_processing_time_sec

from mylang import print_red


def launch_in_new_thread(command_parts: str, output_path: str):
    print(f"Executing command: \"{' '.join(command_parts)}\" in new thread, output path is: {output_path}")

    def launch_command():
        # os.system(command)
        try:
            subprocess.run(command_parts, timeout=max_query_processing_time_sec)
        except subprocess.TimeoutExpired:
            print_red(f"Execution of program {' '.join(command_parts)} took too long (> {max_query_processing_time_sec} seconds) "
                      "=> write about it to file: {output_path}")
            out_file = open(output_path, "r")
            out_file.write("You query processing is timed out: it ran > " + str(max_query_processing_time_sec) + " seconds!")
            out_file.close()

    t = Thread(target = launch_command, args = ())
    t.daemon = True
    t.start()


if __name__ == '__main__':
    pass
