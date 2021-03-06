import sys

from biodivine_aeon import *
from pathlib import Path


model_path = sys.argv[1]
print("Model path", model_path)

model_string = Path(model_path).read_text()
model = BooleanNetwork.from_aeon(model_string)

print("Loaded model with", model.num_vars(), "variables.")

graph = SymbolicAsyncGraph(model)

attractors = find_attractors(graph)

total = 0.0
for attr in attractors:
	total = total + attr.cardinality()

print("Total attractor state-colour pairs:", total)
