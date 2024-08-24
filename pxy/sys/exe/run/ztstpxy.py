import py_compile
import os

# Get the current directory
current_dir = os.getcwd()

# Loop through all files in the current directory
for filename in os.listdir(current_dir):
    # Check if the file ends with .py and is not the compilation script itself
    if filename.endswith(".py") and filename != "compile_files.py":
        # Define the name of the .pyc file to be the same as the .py file but with .pyc extension
        compiled_file_name = filename + 'c'
        compiled_file_path = os.path.join(current_dir, compiled_file_name)
        
        # Compile the file and save the .pyc in the same directory
        py_compile.compile(os.path.join(current_dir, filename), cfile=compiled_file_path)
        print(f"Compiled {filename} to {compiled_file_path}")
