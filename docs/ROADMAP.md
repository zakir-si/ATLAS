# Roadmap and release gates

## v0.1 — Research scaffold
- [x] Strict measurement model and quality-constrained selector
- [x] Local API, browser demo, CLI, tests and CI definition
- [x] Colab LoRA fine-tuning template
- [ ] Execute CI and repair issues from actual results
- [ ] Run a baseline and archive real measurements

## v0.2 — Reproducible experiment runner
- Immutable run manifest and schema versioning
- Training adapter interface and resumable checkpoints
- Hardware discovery and robust timing/memory instrumentation
- Evaluation adapter and baseline/candidate comparison
- Explicit accounting for hyperparameter-search compute

## v0.3 — Adaptive search
- Compare random search and successive halving
- Schedule experiments within a hard budget
- Add safeguards for misleading early learning curves
- Run ablations to isolate each strategy's contribution

## v0.4 — External alpha
- Versioned CLI/SDK and installation matrix
- Durable local artifact store and exportable reports
- Regression benchmarks and compatibility tests
- External feedback and reproducibility audit

## Enterprise candidate
- Authentication, authorization, audit logs and tenant isolation
- Queue/worker architecture, cancellation, retries and recovery
- Durable database/object storage, retention and backup/restore
- Metrics, structured logs, tracing, alerts and runbooks
- SBOM, dependency/secret scanning, build provenance and security review
- Support matrix, SLOs, incident response and release policy

No release may claim a percentage of compute savings without reproducible, matched benchmark evidence. Enterprise readiness is deployment-specific.
