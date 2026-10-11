"""Matched-run benchmark analysis for ATLAS experiments."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

from atlas.models import RunResult


@dataclass(frozen=True, slots=True)
class BenchmarkComparison:
    """Aggregate comparison of repeated baseline and candidate runs."""

    baseline_runs: int
    candidate_runs: int
    baseline_mean_quality: float
    candidate_mean_quality: float
    baseline_mean_accelerator_hours: float
    candidate_mean_accelerator_hours: float
    baseline_mean_peak_memory_gb: float
    candidate_mean_peak_memory_gb: float
    baseline_mean_tokens_per_second: float
    candidate_mean_tokens_per_second: float
    compute_reduction_percent: float
    quality_delta: float
    quality_gate_passed: bool


def compare_repeated_runs(
    baseline: list[RunResult],
    candidate: list[RunResult],
    *,
    min_quality: float,
    max_quality_drop: float = 0.01,
) -> BenchmarkComparison:
    """Compare repeated runs without hiding quality regressions.

    Use the same task, data split, evaluation method, and comparable hardware for
    both groups. The function summarizes supplied measurements; it does not
    establish statistical significance or prove causality.
    """
    if len(baseline) < 2 or len(candidate) < 2:
        raise ValueError("At least two runs per group are required for comparison.")
    if not math.isfinite(min_quality) or not 0.0 <= min_quality <= 1.0:
        raise ValueError("min_quality must be finite and between 0 and 1.")
    if not math.isfinite(max_quality_drop) or not 0.0 <= max_quality_drop <= 1.0:
        raise ValueError("max_quality_drop must be finite and between 0 and 1.")

    for group_name, runs in (("baseline", baseline), ("candidate", candidate)):
        for run in runs:
            try:
                run.validate()
            except (AttributeError, ValueError) as exc:
                raise ValueError(f"Invalid {group_name} run: {exc}") from exc

    def mean(runs: list[RunResult], field: str) -> float:
        return statistics.fmean(getattr(run, field) for run in runs)

    baseline_quality = mean(baseline, "quality")
    candidate_quality = mean(candidate, "quality")
    baseline_hours = mean(baseline, "accelerator_hours")
    candidate_hours = mean(candidate, "accelerator_hours")
    quality_delta = candidate_quality - baseline_quality
    compute_reduction = (baseline_hours - candidate_hours) / baseline_hours * 100.0

    return BenchmarkComparison(
        baseline_runs=len(baseline),
        candidate_runs=len(candidate),
        baseline_mean_quality=baseline_quality,
        candidate_mean_quality=candidate_quality,
        baseline_mean_accelerator_hours=baseline_hours,
        candidate_mean_accelerator_hours=candidate_hours,
        baseline_mean_peak_memory_gb=mean(baseline, "peak_memory_gb"),
        candidate_mean_peak_memory_gb=mean(candidate, "peak_memory_gb"),
        baseline_mean_tokens_per_second=mean(baseline, "tokens_per_second"),
        candidate_mean_tokens_per_second=mean(candidate, "tokens_per_second"),
        compute_reduction_percent=compute_reduction,
        quality_delta=quality_delta,
        quality_gate_passed=(
            candidate_quality >= min_quality
            and quality_delta >= -max_quality_drop
        ),
    )
