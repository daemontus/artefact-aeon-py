import sys
import os

from pathlib import Path


model_path = sys.argv[1]
print("Model path", model_path)

name = os.path.basename(model_path)

os.chdir('iFVS-ABN-v0.1')
#os.system('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:'+os.getcwd())
#code = os.system('java -jar iFVS-ABN.jar '+name.replace("aeon", "bnet"))
code = os.system('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:'+os.getcwd()+'; '+'java -jar iFVS-ABN.jar '+name.replace("aeon", "bnet"))
print("Exit code", code)
exit(code)
