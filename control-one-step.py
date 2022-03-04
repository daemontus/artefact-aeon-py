import sys
import os
import ast

from biodivine_aeon import *
from pathlib import Path
from utils import set_canonical_names, fix_inputs_false

model_path = sys.argv[1]
print("Model path", model_path)

model_string = Path(model_path).read_text()
model = BooleanNetwork.from_aeon(model_string)

print("Loaded model with", model.num_vars(), "variables.")

lines = model_string.splitlines()

# Expects that first line is the target state
target = ast.literal_eval(lines[0][1:])
source = [not x for x in target]

print("Source:", source)
print("Target:", target)

graph = PerturbationGraph(model)

all_colors = graph.mk_unit_colored_vertices().colors()
print("Colors:", all_colors)

control_map = graph.one_step_control(source, target, all_colors)
print("Control map computed:", control_map.as_colored_vertices())
