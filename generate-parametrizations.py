import glob
import os
import random
import sys

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


# generates lists of binary values (of given length), by incrementation
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


# transforms integer to corresponding boolean vector of given size
def int_to_bool_vec(num: int, vec_len: int):
    bool_vec = [False for _ in range(vec_len)]
    index = vec_len - 1
    while num > 0:
        bool_vec[index] = num % 2 != 0
        num //= 2
        index -= 1
    return bool_vec


# common functionality of both generating methods
# prints basic information about input model, extracts BN + input list
def extract_network_and_inputs(model_path: str):
    print("Model path:", model_path)
    model_string = Path(model_path).read_text()
    nw = BooleanNetwork.from_aeon(model_string)
    print(f"Loaded model with {nw.num_vars()} variables and {nw.num_parameters()} parameters.")

    print("Renaming variables to canonical forms.")
    nw = set_canonical_names(nw)
    gr = nw.graph()

    model_inputs = [gr.get_variable_name(v) for v in gr.variables() if not gr.regulators(v)]
    print(f"Model has {len(model_inputs)} inputs: ", model_inputs)
    return nw, model_inputs


# generates network with fixed inputs for every possible valuation
def generate_all_parametrizations(model_path: str):
    nw, model_inputs = extract_network_and_inputs(model_path)

    dir_name = f"./all-parametrizations/{Path(model_path).stem}"
    os.makedirs(dir_name, exist_ok=True)
    print(f"Creating {2 ** len(model_inputs)} files in {dir_name}")

    for bool_vec in generate_bool_vectors(len(model_inputs)):
        name = f"{bool_vec_to_str(bool_vec)}"
        input_dict = {in_name: in_val for (in_name, in_val) in zip(model_inputs, bool_vec)}
        fixed_network = fix_inputs(nw, input_dict)
        Path(f"{dir_name}/{name}.aeon").write_text(fixed_network.to_aeon())


# generates networks with fixed inputs for @sample_size randomly selected valuations
def generate_random_parametrizations(model_path: str, sample_size: int):
    nw, model_inputs = extract_network_and_inputs(model_path)

    dir_name = f"./random-parametrizations/{Path(model_path).stem}"
    # delete previous random networks if some exist (otherwise would mix up)
    if Path(dir_name).exists():
        print(f"Deleting previously generated networks in {dir_name}")
        files = glob.glob(f'{dir_name}/*')
        for f in files:
            os.remove(f)
    else:
        os.makedirs(dir_name, exist_ok=True)

    random_numbers = sorted(random.sample(range(2 ** len(model_inputs)), sample_size))
    numbers_file = f"{dir_name}/generated_indices.txt"
    print(f"Indices of generated models saved to {numbers_file}")
    Path(numbers_file).write_text("\n".join(str(i) for i in random_numbers))

    print(f"Creating {sample_size} model files in {dir_name}")
    for number in random_numbers:
        bool_vec = int_to_bool_vec(number, len(model_inputs))
        name = f"{bool_vec_to_str(bool_vec)}"
        input_dict = {in_name: in_val for (in_name, in_val) in zip(model_inputs, bool_vec)}
        fixed_network = fix_inputs(nw, input_dict)
        Path(f"{dir_name}/{name}.aeon").write_text(fixed_network.to_aeon())


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(f"All parametrizations of model {sys.argv[1]} will be generated.")
        generate_all_parametrizations(sys.argv[1])
    elif len(sys.argv) == 4 and sys.argv[2] == "-random" and sys.argv[3].isdecimal():
        print(f"{sys.argv[3]} random parametrizations of model {sys.argv[1]} will be generated.")
        generate_random_parametrizations(sys.argv[1], int(sys.argv[3]))
    else:
        print("Wrong number of arguments or unexpected argument.")
        print("Usage: generate_parametrizations.py input_file [-random num_samples]")

