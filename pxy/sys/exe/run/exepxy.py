
import os
import py_compile

def compile_all(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__init__'):
                full_path = os.path.join(root, file)
                print(f'Compiling {full_path}')
                py_compile.compile(full_path, cfile=None, dfile=None, optimize=-1)

if __name__ == "__main__":
    compile_all('.')
