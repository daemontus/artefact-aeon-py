import sys
import os

from biodivine_aeon import *
from pathlib import Path
from utils import set_canonical_names


def is_aeon(file):
    return file.endswith(".aeon")


if __name__ == "__main__":
    print("Converting models from aeon format to bnet")
    input_dir = sys.argv[1].strip("/")
    print("Directory with models:", input_dir)

    model_files = filter(is_aeon, os.listdir(input_dir))
    model_files = sorted(model_files)

    for model_file in model_files:
        print("Converting model: ", model_file)
        try:                        
            output_file = model_file.replace("aeon", "bnet")
            output_path_ifvs = "./iFVS-ABN-v0.1/networks/" + output_file

            model_string = Path(f"{input_dir}/{model_file}").read_text()
            model = BooleanNetwork.from_aeon(model_string)

            # Note that this assumes that the names of the network variables
            # are already in canonical format (i.e. x1...xN) to avoid
            # errors in bnet export. This is facilitated by 
            # fix-inputs-true.py and generate-parametrizations.py for now.

            Path(f"{input_dir}/{output_file}").write_text(model.to_bnet())
            print("Saving output to: ", f"{input_dir}/{output_file}")
            Path(output_path_ifvs).write_text(model.to_bnet())
            print("Saving output to: ", output_path_ifvs)
        except Exception as error:
            print("Error:", error)
