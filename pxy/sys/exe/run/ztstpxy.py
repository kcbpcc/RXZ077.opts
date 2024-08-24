import py_compile
import os

# Get the current directory
current_dir = os.getcwd()

# Loop through all files in the current directory
for filename in os.listdir(current_dir):
    # Check if the file ends with .py and is not the compilation script itself
    if filename.endswith(".py") and filename != "compile_all.py":
        # Compile the file and save it in the same directory
        py_compile.compile(os.path.join(current_dir, filename))
        print(f"Compiled {filename}")
