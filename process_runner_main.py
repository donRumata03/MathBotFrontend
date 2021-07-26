import sys
import subprocess

from config import max_query_processing_time_sec
from mylang import print_red

output_path = sys.argv[1]
command_parts = sys.argv[2:]
print(f"output_path: {output_path}")
print(f"command_parts: {command_parts}")


try:
    subprocess.run(command_parts, timeout=max_query_processing_time_sec)
except subprocess.TimeoutExpired:
    print_red(f"Execution of program {' '.join(command_parts)} took too long (> {max_query_processing_time_sec} seconds) "
              f"=> write about it to file: {output_path}")
    out_file = open(output_path, "w")
    out_file.write("You query processing is timed out: it ran > " + str(max_query_processing_time_sec) + " seconds!")
    out_file.close()



"""
Test:

"C:\Program Files (x86)\Python37-32\python.exe" D:/Projects/MathBot/Math_bot_frontend/process_runner_main.py 

"""