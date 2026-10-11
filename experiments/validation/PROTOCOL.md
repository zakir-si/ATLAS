# ATLAS validation protocol

## Research question
On a fixed pool of completed fine-tuning candidates, does ATLAS's quality-per-accelerator-hour selection rule choose a candidate with lower selected-run accelerator-hours than prespecified simple policies while meeting a validation-quality floor and retaining acceptable held-out test quality?

## Hypothesis
The primary hypothesis is conditional and narrow: under the preregistered quality floor and per-candidate budget, the ATLAS selector may reduce selected-run accelerator-hours relative to best-validation-quality selection without test-quality degradation beyond a preregistered margin. The null or an inconclusive result is acceptable.

## Design
- One seed block is one trial; every trial must include the exact same candidate grid.
- Candidate selection may use validation quality and resource measurements only.
- Test quality is held out until all candidate runs are completed and the policy/thresholds are frozen.
- Keep hardware, model revision, dataset revision, preprocessing, max sequence length, and evaluation sample counts fixed within a study.
- Save failed runs, OOMs, retries, and exclusions with reasons.
- Use at least five seed blocks for a preliminary study; consider ten or more and a power analysis for stronger claims.

## Candidate grid
See README. Treat it as a pipeline smoke-test grid; do not call it an optimized or exhaustive search.

## Metrics
- Validation loss and transformed selection quality: q = 1 / (1 + validation_loss).
- Held-out test loss, perplexity and transformed test quality: 1 / (1 + test_loss).
- Candidate accelerator-hours: (training wall time + validation evaluation wall time) × number of GPUs / 3600.
- Peak allocated GPU memory and estimated tokens/second are secondary metrics; disclose the tokens/second approximation.
- Test-evaluation time is reported separately and not used in selection.

## Policies
1. ATLAS's actual `select_best_run` implementation.
2. Best validation quality among eligible candidates.
3. Fastest eligible candidate.
4. Seeded random eligible candidate.

Eligibility is determined using the preregistered validation-quality floor and max candidate accelerator-hours. No eligible candidate is a failed policy outcome, not permission to change the floor after seeing results.

## Uncertainty and reporting
Compare policies within each seed block. Report per-trial paired differences, mean/median/SD, and a bootstrap 95% interval over independent seed blocks. With few seeds, intervals can be unstable and do not replace a power analysis. Report all outcomes, including negative/null results.

## Critical limitation
Every policy selects from the same already-measured candidate pool. This experiment compares the resource use of the selected candidate, not the total cost to discover it. A total-search-cost claim requires a separate sequential/budget-matched study that charges all exploration, failed runs, validation, and selection overhead.
