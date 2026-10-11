# Architecture

## Current scope

ATLAS v0.1 has four responsibilities: training execution (currently an explicit notebook), measurement, quality-constrained selection, and presentation through CLI/API/UI. The current API receives already measured results. It does not launch jobs, download datasets or upload artifacts.

## Data flow

training run -> measurement manifest -> validation -> eligible candidates -> selection -> report

Future manifests should include code commit, model revision, dataset revision/fingerprint, configuration, seed, hardware, precision, token count, elapsed time, accelerator count, peak memory and evaluator/version.

## Selection objective

The current selector maximizes quality divided by accelerator-hours, subject to a quality floor and resource budget. This is a baseline, not a universally optimal objective. It can favor a run barely above the quality floor; future work should compare Pareto-frontier selection, monetary cost, uncertainty-aware estimates and multi-objective optimization.

## Planned boundaries

- Training adapters for Transformers/TRL and later distributed engines.
- Profiling for hardware discovery, timing, memory and cost.
- Evaluation adapters isolated from training data.
- Versioned manifests and artifact storage.
- Controller for budgets and search algorithms.

Avoid microservices until deployment needs justify them. Shared deployments need authentication, authorization, queueing, durable storage, tenant isolation, audit events and observability.
