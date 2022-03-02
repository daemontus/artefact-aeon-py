from biodivine_aeon import *


def fix_inputs_free(network):
    graph = network.graph()
    for v in graph.variables():
        # For parameters, remove update function and replace with true
        if len(graph.regulators(v)) == 0:
            name = graph.get_variable_name(v)
            print("Found parameter", name, "-- set to free.")
            network.set_update_function(v, None)  # Set to true
    return network

def fix_inputs_false(network):
    graph = network.graph()
    for v in graph.variables():
        # For parameters, remove update function and replace with true
        if len(graph.regulators(v)) == 0:
            name = graph.get_variable_name(v)
            print("Found parameter", name, "-- Fixed to false.")
            network.set_update_function(v, "false")  # Set to true
    return network


# Ensures that every logical input has its value fixed to true.
def fix_inputs_true(network):
    graph = network.graph()
    for v in graph.variables():
        # For parameters, remove update function and replace with true
        if len(graph.regulators(v)) == 0:
            name = graph.get_variable_name(v)
            print("Found parameter", name, "-- Fixed to true.")
            network.set_update_function(v, "true")  # Set to true
    return network


# Ensures network variables are named x1...xN.
def set_canonical_names(network):
    i = 1
    graph = network.graph()
    for v in graph.variables():
        print("Rename", graph.get_variable_name(v), "to", "x"+str(i))
        network.set_variable_name(v, "x"+str(i))
        i = i + 1
    return network


# Ensures that logical inputs are not network variables,
# but only instead appear as free nullary uninterpreted
# functions within the network.
def inline_free_inputs(network):
    variables = []
    params = []
    graph = network.graph()
    for v in graph.variables():
        if len(graph.regulators(v)) == 0:
            params.append(graph.get_variable_name(v))
        else:
            variables.append(graph.get_variable_name(v))

    inlined_rg = RegulatoryGraph(variables)
    for reg in graph.regulations():
        old_source = graph.get_variable_name(reg['source'])
        old_target = graph.get_variable_name(reg['target'])
        if old_source in variables:
            # Only copy regulations if they are for variables
            reg['source'] = inlined_rg.find_variable(old_source)
            reg['target'] = inlined_rg.find_variable(old_target)
            # This is necessary because fixing parameters can make
            # other variables "technically" non-observable.
            reg['observable'] = False
            inlined_rg.add_regulation(reg)

    inlined_bn = BooleanNetwork(inlined_rg)
    for param in params:
        inlined_bn.add_parameter({'name': param, 'arity': 0})

    for var_name in variables:
        old_function = network.get_update_function(var_name)
        inlined_bn.set_update_function(var_name, old_function)

    return inlined_bn

