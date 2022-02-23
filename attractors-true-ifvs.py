import sys
import os

from biodivine_aeon import *
from pathlib import Path
from utils import fix_inputs_true, set_canonical_names

model_path = sys.argv[1]
print("Model path", model_path)

model_string = Path(model_path).read_text()
model = BooleanNetwork.from_aeon(model_string)
model = fix_inputs_true(model)
model = set_canonical_names(model)

print("Loaded model with", model.num_vars(), "variables")

name = os.path.basename(model_path)
Path("./iFVS-ABN-v0.1/networks/"+name.replace("aeon", "bnet")).write_text(model.to_bnet())

os.chdir('iFVS-ABN-v0.1')
os.system('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:'+os.getcwd())
code = os.system('java -jar iFVS-ABN.jar '+name.replace("aeon", "bnet"))
print("Exit code", code)
exit(code)