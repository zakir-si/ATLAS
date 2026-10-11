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

The `atlas.benchmark.compare_repeated_runs` function summarizes repeated baseline and candidate measurements. It reports mean quality, accelerator-hours, peak memory, throughput, compute reduction and a predeclared quality gate. It requires at least two runs per group. It does **not** calculate confidence intervals, establish statistical significance, or prove that the candidate method caused the difference.

Example use:

```python
from atlas.benchmark import compare_repeated_runs
from atlas.models import RunResult

baseline = [
    RunResult("base-seed-1", 0.90, 10.0, 8.0, 100.0),
    RunResult("base-seed-2", 0.91, 10.5, 8.2, 98.0),
]
candidate = [
    RunResult("candidate-seed-1", 0.90, 7.0, 7.0, 125.0),
    RunResult("candidate-seed-2", 0.89, 7.2, 7.1, 121.0),
]

report = compare_repeated_runs(
    baseline,
    candidate,
    min_quality=0.88,
    max_quality_drop=0.02,
)
print(report)
```

The values above are illustrative only, not actual benchmark results. Run on a consistent task, data split and comparable hardware before interpreting the output.

## Claim threshold

A compute-saving claim requires matched baselines, a predeclared quality tolerance, consistent accounting of search and training compute, and repeat measurements. One best run is not enough.
