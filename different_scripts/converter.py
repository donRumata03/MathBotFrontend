from mylang import *

with open("answers.json") as j:
    to_utf8_json_file(json.loads(j.read()), "new_answers.json")
