import csv
import logging
import sys
import time
from pathlib import Path
from statistics import mean

from utils import fix_inputs_false
from biodivine_aeon import *


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def attractor_colors(vertex: [bool], perturbation_graph: PerturbationGraph):
    graph = perturbation_graph.as_perturbed()
    colored_vertex = graph.fix_vertex(vertex)
    fwd = reach_fwd(graph, colored_vertex)
    bwd = reach_bwd(graph, colored_vertex)
    scc = fwd.intersect(bwd)
    print("SCC", scc)
    not_attractor_colors = fwd.minus(scc).colors()
    return scc.minus_colors(not_attractor_colors).colors()


def measure(fun, target_ix, source_ix):
    logging.info(f"Starting measuring from {source_ix} to {target_ix}")
    start = time.time()
    result = fun()
    print("Result:",result.as_colored_vertices())
    end = time.time()
    logging.info(f"Measuring from {source_ix} to {target_ix} finished. ")
    return end - start


def benchmark_model(model_file_path):
    results = []
    logging.info(model_file_path)
    model_string = model_file_path.read_text()
    boolean_network = BooleanNetwork.from_aeon(model_string)
    vars_count = boolean_network.num_vars()
    logging.info(f"vars count: {vars_count}")
    try:
        symbolic_async_graph = SymbolicAsyncGraph(boolean_network)
    except Exception as e:
        print(e)
        return []

    logging.info(f"colors count: {symbolic_async_graph.unit_colored_vertices().cardinality() / vars_count}")
    logging.info(f"total cardinality: {symbolic_async_graph.unit_colored_vertices().cardinality()}")

    logging.info(find_attractors(symbolic_async_graph))
    #witness = SymbolicAsyncGraph(symbolic_async_graph.pick_witness(symbolic_async_graph.unit_colors()))
    witness = SymbolicAsyncGraph(fix_inputs_false(symbolic_async_graph.network()))
    attractor_vertices = [a.pick_vertex().vertices().vertices()[0] for a in find_attractors(witness)]
    logging.info(f"attractor count: {len(attractor_vertices)}")

    for i, target in enumerate(attractor_vertices[:8]):
        perturbation_graph = PerturbationGraph(witness.network())
        colors = perturbation_graph.mk_unit_colored_vertices().colors() #attractor_colors(target, perturbation_graph)
        print("Colors", colors)
        for j, source in enumerate(attractor_vertices[:8]):
            if i == j:
                continue
            print("Source", source)
            print("Target", target)
            print(witness.network().to_aeon())
            one_step_time = measure(lambda: perturbation_graph.one_step_control(source, target, colors), i, j)
            permanent_time = measure(lambda: perturbation_graph.permanent_control(source, target, colors), i, j)
            temporary_time = measure(lambda: perturbation_graph.temporary_control(source, target, colors), i, j)
            results.append((model_file_path, i, j, one_step_time, permanent_time, temporary_time))

    logging.info(f"Average model one-step control time: {mean([x[-3] for x in results])}")
    logging.info(f"Average model permanent control time: {mean([x[-2] for x in results])}")
    logging.info(f"Average model temporary control time: {mean([x[-1] for x in results])}")
    return results


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    model_path = Path(sys.argv[1])
    logging.info("Model path %s", model_path)
    results = benchmark_model(model_path)

    header = [('model', 'target_ix', 'source_ix', 'one_step_time', 'permanent_time', 'temporary_time')]
    all_results = header + results
    with open(f"{model_path.parts[-1]}_control_out.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(all_results)
