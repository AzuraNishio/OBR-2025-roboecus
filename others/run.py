import subprocess

device_name = "gambare yala"
script_file = "code/main.py"

subprocess.run([
    "pybricksdev", "run", "ble",
    "--name", device_name,
    script_file
])
