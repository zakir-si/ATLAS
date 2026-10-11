# ATLAS Research Validation Kit

This is a reproducible experiment scaffold for testing the current ATLAS measured-run selector against simple selection baselines. It is **not evidence of improved performance** until real runs complete.

## Scope and honest claim

ATLAS currently selects among runs that have already been measured. This study evaluates the quality/resource trade-off of selecting a candidate from a fixed measured pool. It does **not** show lower total hyperparameter-search cost, because the entire candidate pool has already incurred its compute cost.

## Environment

Use Python 3.11 and a fresh branch. On Colab, select a T4 GPU (or record the actual assigned GPU).

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev,training]'
python -m pip check
python -m compileall -q experiments/validation
pytest -q experiments/validation/tests
```

Save the environment and outputs to persistent storage (e.g. Google Drive):

```bash
mkdir -p artifacts/validation
python --version > artifacts/validation/python-version.txt
python -m pip freeze > artifacts/validation/requirements-lock.txt
```

Never commit access tokens. Keep pilot and final data files separate.

## Candidate grid

| Config ID | LoRA rank | Learning rate | Training steps |
|---|---:|---:|---:|
| steps50-r4-lr1e4 | 4 | 0.0001 | 50 |
| steps100-r8-lr2e4 | 8 | 0.0002 | 100 |
| steps150-r8-lr2e4 | 8 | 0.0002 | 150 |

This small grid validates the pipeline, not the universal quality of these hyperparameters. It is not enough to establish generality.

## Pilot (debugging only)

```bash
PILOT_RUNS_FILE=artifacts/validation/pilot_runs.jsonl bash experiments/validation/run_pilot.sh
```

Pilot runs skip test evaluation. Use them to catch bugs, estimate runtime, and set a defensible quality floor/budget. Do not use pilot metrics as confirmatory evidence.

## Preregister

Copy `PRE-REGISTRATION-TEMPLATE.md` to `PRE-REGISTRATION.md`. Complete it and commit it before the final batch. Freeze code commit, package versions, model/data revisions, candidate grid, seeds, quality floor, resource budget, policy list, analysis, and decision rule.

The starter uses Qwen/Qwen2.5-0.5B and Salesforce/wikitext as a low-cost pipeline-validation task. Pin immutable model and dataset revisions for the actual study, verify dataset licensing/terms, and preserve resolved revisions/fingerprints. The code's default model revision is not a substitute for recording a resolved immutable revision.

## Confirmatory batch

```bash
RUNS_FILE=artifacts/validation/final_runs.jsonl bash experiments/validation/run_confirmatory.sh
```

The script uses seeds 41–45 and all three candidates per seed. Do not inspect final test results or change thresholds/policies before every declared run finishes. If you change the method after looking at test results, label those results exploratory and use a fresh batch for confirmation.

## Analyze

Use the quality floor and accelerator-hour budget written in the preregistration—not values selected after seeing test results.

```bash
python experiments/validation/analyze_selection.py \
  --input artifacts/validation/final_runs.jsonl \
  --output-dir artifacts/validation/analysis \
  --min-quality 0.15 \
  --max-hours 0.25 \
  --bootstrap-samples 10000 \
  --seed 20261011
```

The example threshold/budget above are placeholders. Replace them with preregistered values. If any trial has no eligible candidate, record that failure; do not relax the threshold post hoc.

## Evidence to publish

Archive raw JSONL records, failed-run/OOM log, protocol, exact code commit, package lock, hardware/runtime information, analysis JSON/CSV, and a short report including negative or inconclusive results. The bootstrap interval is descriptive with only five seed blocks; five is not a guarantee of adequate statistical power. Replicate on another task/model before making broader claims.

## What a result can support

A supportive result would require a predeclared selected-run compute advantage over a baseline and held-out test quality within a predeclared non-inferiority margin, with uncertainty reported. The selector operates on already measured runs, so never call selected-run hours "total search savings." Total-search savings require a separate budget-matched online experiment that counts every candidate, failed run, validation pass, and overhead.
