import sys

from biodivine_aeon import *
from pathlib import Path
from utils import inline_free_inputs, set_canonical_names

model_path = sys.argv[1]
print("Model path", model_path)

model_string = Path(model_path).read_text()
model = BooleanNetwork.from_aeon(model_string)
model = inline_free_inputs(model)
model = set_canonical_names(model)

print("Loaded model with", model.num_vars(), "variables and", model.num_parameters(), "parameters.")

graph = SymbolicAsyncGraph(model)

attractors = find_attractors(graph)

total = 0.0
for attr in attractors:
	total = total + attr.cardinality()	

print("Total attractor state-colour pairs:", total)