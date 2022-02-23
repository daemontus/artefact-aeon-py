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

print("Loaded model with", model.num_vars(), "variables.")

# We have to save the file somewhere CABEAN will easily find it
name = os.path.basename(model_path)
Path("./CABEAN-release-2.0.1/"+name.replace("aeon", "bnet")).write_text(model.to_bnet())

os.chdir('CABEAN-release-2.0.1')
code = os.system('./BinaryFile/WindowsLinux/cabean_linux '+name.replace("aeon", "bnet"))
print("Exit code", code)
exit(code)