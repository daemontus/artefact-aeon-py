# AEON.py Benchmarks

This repository is configured to allow painless running of non-trivial benchmarks of the AEON.py software.

The `all-models` directory contains 145 non-trivial real-world Boolean networks, which you can run experiments on. Furthermore, you can customise the models directly in Python (`utils.py` has some examples on how to e.g. fix all logical inputs to `true`).

The `run.py` script ("runner") makes it possible to run a particular python script for each model ("experiment") in a directory (e.g. `all-models`). The runner then makes sure that each experiment runs within a specified timeout, that the runtime is measured, and that the output is saved to a separate file.

The runner can operate in three modes:

1. Interactive: Before each experiment is started, you are prompted to either run it or skip it. You can also abort the whole run.
2. Sequential: Experiments run automatically one after the other.
3. Parallel: Up to `N` (user provided) experiments are executed in parallel (as separate processes).

For each run, runner creates a new output directory whose name contains the name of the benchmarked Python script, model directory, timestamp, and flag whether the run was parallel. Additionally, runner compiles a `.csv` file with runtimes for each benchmark, and an aggregated `.csv` file with "instances completed before time".

Before starting, make sure:
 - You have AEON.py installed (`pip install biodivine_aeon`). 
 - On macOS, you'll also need `gtimeout` (available in coreutils). 
 - AEON.py should be fully multiplatform, other tools were only tested on Linux. 
 - However, they should also work on other systems -- you may need to switch binaries in the scripts to the appropriate OS tohugh. 
 - `CABEAN` and `iFVS` are provided in the repository. 
 - `pystablemotifs` must be installed according to instructions provided [here](https://github.com/jcrozum/pystablemotifs).
 - Also, make sure you have Z3 installed, as it is used by `iFVS`.

Runner invocation:

```
python3 run.py TIMEOUT BENCH_DIR SCRIPT [-i/-p N]
```

 - `TIMEOUT` is a standard UNIX timeout string. E.g. `1h`, `10s`, etc.
 - `BENCH_DIR` is a path to a directory that will be scanned to obtain the list of experiments (`.aeon` files).
 - `SCRIPT` is a path to a Python script that will be started by the runner, with an experiment file (`.aeon` file) as the first argument. Naturally, this script can then start other native processes if necessary, or modify the model as desired.
 - Add `-i` if you want to use the interactive mode.
 - Add `-p N` if you want to run up to `N` experiments in parallel.

> WARNING: The script does not respond particularly well to keyboard interrupts. If you kill the benchmark runner (e.g. `Ctrl+C`), you may also need to manually terminate some of the unfinished experiments.

> ANOTHER WARNING: For some reason, not all exit codes are always propagated correctly through the whole `python <-> timeout <-> time <-> python` chain. For this reason, an error in the benchmark script can still result in a "successful" measurement (successful in the sense that it finished before timeout). When using the final results, always make sure there is no segfault or out-of-memory hidden somewhere in the results. In particular, this can occur for `pystablemotifs` and `CABEAN`, where you should always additionally check if the returned results are fully computed.

## Prepared Benchmarks

There are several pre-configured benchmark scripts that you can use. Of course, you can add `-p N` or `-i` to each command to run it in parallel or interactive mode.

### Attractors (inputs fixed to true)

```
# Generate models with inputs fixed to true for each network (.aeon format)
python3 fix-inputs-true.py all-models
# Also create .bnet versions of those models (other tools need them)
python3 aeon-to-bnet.py all-models-inputs-true

# Use AEON.py
python3 run.py 1h all-models-inputs-true attractors-aeon-basic.py
# Use CABEAN
python3 run.py 1h all-models-inputs-true attractors-cabean-basic.py
# Use iFVS
python3 run.py 1h all-models-inputs-true attractors-ifvs-basic.py
# Use pystablemotifs
python3 run.py 1h all-models-inputs-true attractors-pystable-basic.py
```

### Attractor scan of all parametrisations of a particular model

```
# Substitute model_path and model_name for actual names

# Generate model file for each parametrisation of the given network
python3 generate-parametrizations.py model_path
# Create also bnet versions of those models (other tools need them)
python3 aeon-to-bnet.py all-parametrizations/model_name

# Use AEON.py
python3 run.py 1h all-parametrizations/model_name attractors-aeon-basic.py
# Use CABEAN
python3 run.py 1h all-parametrizations/model_name attractors-cabean-basic.py
# Use iFVS
python3 run.py 1h all-parametrizations/model_name attractors-ifvs-basic.py
# Use pystablemotifs
python3 run.py 1h all-parametrizations/model_name attractors-pystable-basic.py

```

### Attractors scan of random sample of parametrizations of particular model

For models with a large number of parametrisations, a complete scan may not be feasible. Instead, you can sample a smaller subset of parametrisations:

```
# Substitute model_path, model_name, sample_size for actual names/values

# Generate number of networks with randomly fixed inputs from the given model
python3 generate-parametrizations.py model_path -random sample_size
# Create also bnet versions of those models (other tools need them)
python3 aeon-to-bnet.py random-parametrizations/model_name

# Use AEON.py
python3 run.py 1h random-parametrizations/model_name attractors-aeon-basic.py
# Use CABEAN
python3 run.py 1h random-parametrizations/model_name attractors-cabean-basic.py
# Use iFVS
python3 run.py 1h random-parametrizations/model_name attractors-ifvs-basic.py
# Use pystablemotifs
python3 run.py 1h random-parametrizations/model_name attractors-pystable-basic.py

```

### Source-target control benchmark

Finally, you can also benchmark different types of source-target control algorithms for a particular model using the following command:

```
# Generate source-target combinations for a particular model:
python3 generate-control.py path/to/model-name.aeon

# Run control experiments for the generated source-target pairs:
python3 run.py 1h run.py control-inputs/model-name control-one-step.py
python3 run.py 1h run.py control-inputs/model-name control-permanent.py
python3 run.py 1h run.py control-inputs/model-name control-temporary.py

# Of course, you can also use control-one-step.py, control-permanent.py and control-temporary.py
# to run experiments on specific generated models in the control-inputs directory separately.
```


### Example results

Some performance results obtained using the commands presented above are available in the `raw-results` directory. Though keep in mind that the performance on your machine may differ significantly.