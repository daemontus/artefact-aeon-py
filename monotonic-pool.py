import sys

from biodivine_aeon import *
from pathlib import Path
from utils import fix_inputs_true, set_canonical_names, inline_free_inputs

model_path = sys.argv[1]
print("Model path", model_path)

model_string = Path(model_path).read_text()
model = BooleanNetwork.from_aeon(model_string)
model = fix_inputs_true(model)

def build_matrix(model):
	matrix = {}
	graph = model.graph()
	for target in graph.variables():
		target_name = graph.get_variable_name(target)
		row = {}		
		for source in graph.variables():
			source_name = graph.get_variable_name(source)
			try:				
				regulation = graph.find_regulation(source, target)				
				if regulation['monotonicity'] == "activation":					
					row[source_name] = True					
				elif regulation['monotonicity'] == "inhibition":
					row[source_name] = False
				else:
					print("Non-monotonous regulation found.")
					sys.exit(10)				
			except:
				row[source_name] = None
		matrix[target_name] = row
	return matrix

matrix = build_matrix(model)

original_graph = model.graph()
variables = []
for var in original_graph.variables():
	variables.append(original_graph.get_variable_name(var))

new_rg = RegulatoryGraph(variables)

input_count = 0

for source in new_rg.variables():
	source_name = new_rg.get_variable_name(source)
	for target in new_rg.variables():
		target_name = new_rg.get_variable_name(target)
		if target_name == source_name:
			continue
		if matrix[target_name][source_name] != None:
			monotonicity = None
			if matrix[target_name][source_name] == True:
				monotonicity = 'activation'
			else:
				monotonicity = 'inhibition'
			new_rg.add_regulation({
				'source': source_name,
				'target': target_name,
				'observable': False,
			})

	try:
		new_rg.find_regulation(source_name, source_name)
	except:
		if len(original_graph.regulators(source_name)) > 0:		
			# Inputs must stay inputs.
			new_rg.add_regulation({
				'source': source_name,
				'target': source_name,
				'observable': False
			})
		else:
			input_count += 1
		
new_bn = BooleanNetwork(new_rg)

def mk_eq(a, b):
	return "(" + a + " <=> " + b + ")"

def mk_xor(a, b):
	return "(" + a + " ^ " + b + ")"

for target in new_rg.variables():
	target_name = new_rg.get_variable_name(target)
	function = "false"
	for source in new_rg.variables():
		source_name = new_rg.get_variable_name(source)		
		if matrix[target_name][source_name] != None:
			if matrix[target_name][source_name] == True:
				function = function + " | " + mk_xor(target_name, source_name)
			else:
				function = function + " | " + mk_eq(target_name, source_name)		
	function = target_name + " ^ (" + function + " | false" + ")"
	print(target_name,"=", function)
	#new_bn.set_update_function(target_name, function)
	if len(original_graph.regulators(target_name)) > 0:
		new_bn.set_update_function(target_name, function)
	else:
		new_bn.set_update_function(target_name, None)

#new_bn = inline_free_inputs(new_bn)

model_original = model
model = new_bn

print("Loaded model with", model.num_vars(), "variables and",  input_count, "inputs.")

graph = SymbolicAsyncGraph(model)

attractors = find_attractors(graph)

print(attractors)
print("Bottom sets:", len(attractors))

for attr in attractors:
	always_true = []
	always_false = []
	unstable = []
	for var in model.variables():
		name = model.graph().get_variable_name(var)
		var_set = graph.fix_variable(var, True)
		attr_true = attr.intersect(var_set).colors()
		attr_false = attr.minus(var_set).colors()
		only_true = attr_true.minus(attr_false)
		only_false = attr_false.minus(attr_true)
		both = attr_true.intersect(attr_false)
		if not only_true.is_empty():
			always_true.append(name)
		if not only_false.is_empty():
			always_false.append(name)
		if not both.is_empty():
			unstable.append(name)

	print("Stability in bottom set:")
	print("Fixed true:", len(always_true), always_true)
	print("Fixed false:", len(always_false), always_false)
	print("Unstable:", len(unstable), unstable)

	rg = model.graph()
	for var in set(always_true + always_false):
		regs = map(lambda x: rg.get_variable_name(x), rg.transitive_regulators(var))
		targets = map(lambda x: rg.get_variable_name(x), rg.transitive_targets(var))
		both = list(set(regs) & set(targets))
		if len(both) > 1:
			print("Interesting:", var)
		#id = graph.find_variable(var)
		#print("Check", var, graph.transitive_regulators(var))
		#for reg in graph.transitive_regulators(var):
		#	if graph.get_variable_name(reg) == var:
		#		print("Interesting:", var)

#predicted = graph.empty_colored_vertices()
#total = 0.0
#for attr in attractors:
#	predicted = predicted.union(attr)
#	total = total + attr.cardinality()	
#predicted = predicted.vertices()

#print("Predicted:")
#for vertex in predicted.vertices():
#	print(vertex)

#graph2 = SymbolicAsyncGraph(model_original)
#attractors2 = find_attractors(graph2)

#actual = graph2.empty_colored_vertices()
#for attr in attractors2:
#	actual = actual.union(attr)
#actual = actual.vertices()

#print("Actual:")
#for vertex in actual.vertices():
#	print(vertex)

#print("Total attractor state-colour pairs:", total)
#print("Vs. all state space:",graph.unit_colored_vertices().cardinality())