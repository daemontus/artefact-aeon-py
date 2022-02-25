import sys
import os

from biodivine_aeon import *
from pathlib import Path
from utils import fix_inputs_true, set_canonical_names


def is_aeon(file):
    return file.endswith(".aeon")


if __name__ == "__main__":
    print("Converting models form aeon format to bnet")
    input_dir = sys.argv[1].strip("/")
    print("Directory with models:", input_dir)

    model_files = filter(is_aeon, os.listdir(input_dir))
    model_files = sorted(model_files)

    for model_file in model_files:
        print("Converting model: ", model_file)
        output_file = model_file.replace("aeon", "bnet")
        output_path_ifvs = "./iFVS-ABN-v0.1/networks/" + output_file

        model_string = Path(f"{input_dir}/{model_file}").read_text()
        model = BooleanNetwork.from_aeon(model_string)
        fixed_network = fix_inputs_true(model)

        # TODO: enable this after problem problem with canonization is fixed
        # fixed_network = set_canonical_names(fixed_network)

        Path(f"{input_dir}/{output_file}").write_text(fixed_network.to_bnet())
        print("Saving output to: ", f"{input_dir}/{output_file}")
        Path(output_path_ifvs).write_text(fixed_network.to_bnet())
        print("Saving output to: ", output_path_ifvs)

