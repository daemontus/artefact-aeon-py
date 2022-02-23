import sys
import os

from biodivine_aeon import *
import pystablemotifs as sm
from pathlib import Path
from utils import fix_inputs_true, set_canonical_names

model_path = sys.argv[1]
print("Model path", model_path)

model_string = Path(model_path).read_text()
model = BooleanNetwork.from_aeon(model_string)
model = fix_inputs_true(model)
model = set_canonical_names(model)

print("Loaded model with", model.num_vars(), "variables.")


primes = sm.format.create_primes(model.to_bnet())

ar = sm.AttractorRepertoire.from_primes(primes)
ar.summary()