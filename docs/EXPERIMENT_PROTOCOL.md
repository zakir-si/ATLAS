# Benchmark protocol

## Before running

- Declare task, model revision, dataset revision, split strategy, seeds and evaluation metric.
- Define minimum quality and maximum resource budget before inspecting final results.
- Pin dependency versions and record accelerator model, memory, driver/runtime and software stack.
- Establish a well-tuned baseline. Include hyperparameter-search compute in comparisons when ATLAS incurs it.
- Separate training, validation and final test data. Use validation for selection.

## During each run

Record wall time, accelerator model/count, accelerator-hours, peak memory, tokens processed, throughput, precision, optimizer settings, seed, training/validation curves, failures and checkpoint details. Synchronize GPU operations around timing where appropriate. Report unavailable energy/cost metrics as unavailable, not zero.

## Comparing methods

- Keep task, data and quality definition comparable.
- Compare total cost (search plus final run) as well as final-run cost.
- Repeat final candidates across multiple seeds where feasible.
- Report uncertainty and failed/invalid runs.
- Do not treat unlike GPU-hours as hardware-independent units.
- Validation loss is diagnostic, not a universal capability score.
- Do not use the final test set for iterative configuration selection.

## Claim threshold

A compute-saving claim requires matched baselines, a predeclared quality tolerance, consistent accounting of search and training compute, and repeat measurements. One best run is not enough.
