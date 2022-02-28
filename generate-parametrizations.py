import sys
import os

from biodivine_aeon import *
from pathlib import Path
from utils import set_canonical_names


# fix input values of @network according to @input_val_dict dictionary
def fix_inputs(network, input_val_dict):
    bool_str_dict = {True: "true", False: "false"}  # we will need values as lower-case strings

    graph = network.graph()
    for v in graph.variables():
        # For parameters, remove update function and replace with chosen value
        if len(graph.regulators(v)) == 0:
            name = graph.get_variable_name(v)
            value_str = bool_str_dict[input_val_dict[name]]  # we need value as string
            # print(f"Parameter {name} fixed to {value_str}.")
            network.set_update_function(v, value_str)
    return network


# generates lists of binary values (of given length), by incrementing
def generate_bool_vectors(size):
    bool_vector = [False for _ in range(size)]
    total_num = 2 ** size
    while total_num > 0:
        yield bool_vector

        for i in range(len(bool_vector)):
            if bool_vector[i]:
                bool_vector[i] = False
            else:
                bool_vector[i] = True
                break

        total_num -= 1


# converts list of booleans to a string with 0/1
def bool_vec_to_str(bool_vector):
    return "".join([f"{int(b)}" for b in bool_vector])


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
    fixed_network = set_canonical_names(nw)
    gr = nw.graph()
    model_inputs = [gr.get_variable_name(v) for v in gr.variables() if not gr.regulators(v)]

    dir_name = f"./all-parametrizations/{Path(model_path).stem}"
    os.makedirs(dir_name, exist_ok=True)
    print(f"Creating {2 ** len(model_inputs)} files in {dir_name}.")

    for bool_vec in generate_bool_vectors(len(model_inputs)):
        name = f"{bool_vec_to_str(bool_vec)}"
        input_dict = {in_name: in_val for (in_name, in_val) in zip(model_inputs, bool_vec)}
        fixed_network = fix_inputs(nw, input_dict)
        Path(f"{dir_name}/{name}.aeon").write_text(fixed_network.to_aeon())

