import sys
import os

from biodivine_aeon import *
from pathlib import Path
from utils import set_canonical_names, fix_inputs_false, fix_inputs_free, inline_free_inputs

def pick_pairs(attractor_witnesses):
	pairs = []
	for i, target in enumerate(attractor_witnesses):
		for j, source in enumerate(attractor_witnesses):
			if i == j:
				continue
			pairs.append((source, target))
			if len(pairs) >= 100:
				return pairs
	return pairs


if __name__ == "__main__":
	model_path = sys.argv[1]
	print("Model path:", model_path)
	model_string = Path(model_path).read_text()
	nw = BooleanNetwork.from_aeon(model_string)
	print(f"Loaded model with {nw.num_vars()} variables and {nw.num_parameters()} parameters.")

	gr = nw.graph()
	model_inputs = [gr.get_variable_name(v) for v in gr.variables() if not gr.regulators(v)]
	print(f"Model has {len(model_inputs)} inputs: ", model_inputs)

	print("Renaming variables to canonical forms.")
	canonical_network = set_canonical_names(nw)
	fixed_network = inline_free_inputs(canonical_network)

    # This little hack should ensure the network has the same variable ordering
    # as the one we forward to the actual computation, since the source-target vertices
    # are sensitive to variable ordering.
	fixed_network = BooleanNetwork.from_aeon(fixed_network.to_aeon())

	dir_name = f"./control-inputs-free/{Path(model_path).stem}"
	os.makedirs(dir_name, exist_ok=True)

	# Find attractors for the network with all inputs fixed to false.
	# This ensures that for any variation of inputs, we are testing the same attractor states.
	symbolic_graph = SymbolicAsyncGraph(fixed_network)
	attractors = find_attractors(symbolic_graph)
	
	print(attractors)

    # Contains vertices that are guaranteed to be in different attractors.
    # Because inputs are fixed, there should be no colors and each attractor
    # is therefore really a single unique attractor.
	attractor_witnesses = [attr.pick_vertex().vertices().vertices() for attr in attractors]
	attractor_witnesses = sum(attractor_witnesses, [])

	print(f"Creating {len(attractor_witnesses)} (max. 16) control input files in {dir_name}.")

	for i, target in enumerate(attractor_witnesses):
		# Only save the first 10 options
		if i >= 16:
			break
		print("-- Target:", target)
		model_string = ""
		model_string += f"#{target}\n"
		model_string += fixed_network.to_aeon()
		Path(f"{dir_name}/{i+1}.aeon").write_text(model_string)