# AEON.py Benchmarks

This repository is configured to allow painless running of non-trivial benchmarks of the AEON.py software.

The `all-models` directory contains 145 non-trivial real-world Boolean networks, which you can run experiments on. Furthermore, you can customise the models directly in Python (`utils.py` has some examples on how to e.g. fix all logical inputs to `true`).

The `run.py` script ("runner") makes it possible to run a particular python script for each model ("experiment") in a directory (e.g. `all-models`). The runner then makes sure that each experiment runs within a specified timeout, that the runtime is measured, and that the output is saved to a separate file.

The runner can operate in three modes:

1. Interactive: Before each experiment is started, you are prompted to either run it or skip it. You can also abort the whole run.
2. Sequential: Experiments run automatically one after the other.
3. Parallel: Up to `N` (user provided) experiments are executed in parallel (as separate processes).

For each run, runner creates a new output directory whose name contains the name of the benchmarked python script, model directory, timestamp, and flag whether the run was parallel. Additionally, runner compiles a `.csv` file with runtimes for each benchmark, and an aggregated `.csv` file with "instances completed before time".

Before starting, make sure:
 - You have AEON.py installed (`pip install biodivine_aeon`). 
 - On macOS, you'll also need `gtimeout` (coreutils). 
 - AEON.py should be fully multiplatform, other tools were only tested on Linux. 
 - But they should also work on other systems in theory -- you may need to switch binaries in the scripts to the appropriate OS tohugh. 
 - `CABEAN` and `iFVS` are provided in the repository. 
 - `pystablemotifs` must be installed according to instructions provided [here](https://github.com/jcrozum/pystablemotifs).
 - Also, make sure you have Z3 installed.

Runner invocation:

```
python3 run.py TIMEOUT BENCH_DIR SCRIPT [-i/-p N]
```

 - `TIMEOUT` is a standard timeout string. E.g. `1h`, `10s`, etc.
 - `BENCH_DIR` is a path to a directory which will be scanned to obtain the list of experiments (`.aeon` files).
 - `SCRIPT` is a path to a Python script which will be started by the runner, with an experiment file (`.aeon` file) as the first argument. Naturally, this script can then start other native processes if necessary, or modify the model as desired.
 - Add `-i` if you want to use the interactive mode.
 - Add `-p N` if you want to run up to `N` experiments in parallel.

> WARNING: The script does not respond particularly well to keyboard interrupts. If you kill the benchmark runner (e.g. `Ctrl+C`), you may need to manually terminate some of the unfinished experiments.

> ANOTHER WARNING: For some reason, not all exit codes are always propagated correctly through the whole `python <-> timeout <-> time <-> python` chain. For this reason, an error in the benchmark script can still result in a "successful" measurement (successful in the sense that it finished before timeout). When using the final results, always make sure there is no segfault or out-of-memory hidden somewhere in the results.

## Prepared Benchmarks

There are several pre-configured benchmark scripts which you can use. Of course, you can add `-p N` or `-i` to each command to run it in parallel or interactive mode.

### Attractors (inputs fixed to true)

```
# Use AEON.py
python3 run.py 1h all-models attractors-true-aeon.py
# Use CABEAN
python3 run.py 1h all-models attractors-true-cabean.py
# Use iFVS
python3 run.py 1h all-models attractors-true-ifvs.py
# Use pystablemotifs
python3 run.py 1h all-models attractors-true-pystable.py
```