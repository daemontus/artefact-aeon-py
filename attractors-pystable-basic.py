import sys
import os

import pystablemotifs as sm
from pathlib import Path

model_path = sys.argv[1]
print("Model path", model_path)

primes = sm.format.create_primes(Path(model_path.replace("aeon", "bnet")).read_text())

ar = sm.AttractorRepertoire.from_primes(primes)
ar.summary()
