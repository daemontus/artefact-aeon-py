import sys
import os

from biodivine_aeon import *
from pathlib import Path
from utils import fix_inputs_true, set_canonical_names


# Utility function to check if a given path is a benchmark model.
def is_bench(file):
    return file.endswith(".aeon")


if __name__ == "__main__":
    input_dir = sys.argv[1].strip("/")
    print("Directory with models:", input_dir)

    output_dir = input_dir + "-inputs-true"
    os.makedirs(output_dir, exist_ok=True)

    model_files = filter(is_bench, os.listdir(input_dir))
    model_files = sorted(model_files)

    for model_file in model_files:
        output_file = model_file.split(".")[0] + "-inputs-true.aeon"

        print("Fixing inputs for model:", model_file)
        model_string = Path(f"{input_dir}/{model_file}").read_text()
        model = BooleanNetwork.from_aeon(model_string)
        fixed_network = fix_inputs_true(model)
        fixed_network = set_canonical_names(fixed_network)
        Path(f"{output_dir}/{output_file}").write_text(fixed_network.to_aeon())
        print("Saving output to:", f"{output_dir}/{output_file}")

