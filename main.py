import os

from config import OS, MathBot_root_dir
import bot

###########################################################
###                     MAIN                            ###
###########################################################

if __name__ == '__main__':
	if OS == "windows":
		interpreter_name = "python"
	else:
		interpreter_name = "python3"

	while True:
		os.system(interpreter_name + " " + str(MathBot_root_dir / "MathBotFrontend" / "bot.py"))
		print("[MAIN]: NOT CAUGHT EXCEPTION IN MAIN ==> Rerunning…")
