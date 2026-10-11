# ATLAS

**Adaptive Training and Learning Acceleration System** — a research-first toolkit for quality-constrained, compute-aware model fine-tuning.

> Status: early-stage scaffold. No compute savings or model-quality improvements are claimed until reproducible, matched benchmarks demonstrate them.

## Included
- Python selection core with strict measurement validation.
- Repeated-run benchmark comparison with an explicit quality gate.
- FastAPI backend and local browser interface.
- CLI for selecting from JSON run measurements.
- Google Colab LoRA fine-tuning template with resource manifest.
- Unit/API tests, GitHub Actions CI, Docker and documentation.

## Quick start

Python 3.11 is recommended.

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src
uvicorn atlas.api:app --app-dir src --reload
~~~

Open http://127.0.0.1:8000/ for the UI and http://127.0.0.1:8000/docs for API docs.

## Benchmark comparisons

Use `atlas.benchmark.compare_repeated_runs` to summarize repeated baseline and candidate measurements. It reports average quality, accelerator-hours, peak memory, throughput, compute reduction and whether a predeclared quality gate passed. It requires at least two runs in each group. This is an analysis helper, not an optimization algorithm; it does not establish statistical significance or prove causality. See [the experiment protocol](docs/EXPERIMENT_PROTOCOL.md).

## Research integrity

Predeclare the quality metric, threshold and compute budget. Keep train/validation/test splits separate. Compare against a strong baseline with the same task and evaluation protocol. Record hardware, duration, tokens, memory, versions, seed and code revision. Include hyperparameter-search compute. Repeat final experiments where feasible and report uncertainty and negative results.

The current selector only chooses among supplied measurements; it does not train models or reduce compute by itself. Example numbers are synthetic, not benchmark results.

## API
- GET /health/live — process liveness.
- GET /health/ready — readiness.
- POST /api/v1/select — select a qualifying measured run.
- GET /docs — generated OpenAPI docs.

The API has no authentication and is for local development only. Do not expose it to an untrusted network.

## Colab

Open notebooks/atlas_baseline.ipynb in Google Colab. Configure a permitted model and dataset you are licensed to use. The notebook records time, peak CUDA memory and validation loss. Validation loss is not a universal capability score; use a task-specific held-out evaluator before making quality claims.

## Enterprise boundary

This is a development foundation, not a certified enterprise product. It currently has no authentication, multi-tenancy, persistent database, job queue or model registry. Enterprise deployment requires threat modeling, access controls, durable storage, observability, independent security review and operational validation.

See docs/ARCHITECTURE.md, docs/EXPERIMENT_PROTOCOL.md, docs/SECURITY.md and docs/ROADMAP.md.
