import subprocess

# subprocess.run(["python", "D:/Projects/MathBot/Math_bot_frontend/different_scripts/timeout_producer.py"], timeout=1.2)
subprocess.run(["D:/Projects/MathBot/MathBotBackend/cmake-build-release/Math_bot_backend.exe", "solve", "D:/Projects/MathBot/queries/215659697/565.json"], timeout=5)

