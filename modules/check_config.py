#import from another dir(lib)
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '../lib')))
from ReadConfig import ReadConfig

if len(sys.argv) < 2:
    print(f"usages : {sys.argv[0]} <config_file_path>")
    exit()
filepath = sys.argv[1]
is_success, msg = ReadConfig(filepath)
if is_success:
    print(f":: Read Config is Success!")
else:
    print(f":: Read Config is Failed...\n{msg}")