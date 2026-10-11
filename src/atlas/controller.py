"""Quality-constrained selection logic; this module does not train models."""

from __future__ import annotations

import math
from collections.abc import Sequence

from atlas.models import RunResult, Selection


def select_best_run(
    results: Sequence[RunResult],
    min_quality: float,
    max_accelerator_hours: float,
) -> Selection:
    """Select the highest quality-per-accelerator-hour eligible run.

    Measurements must validate, quality must meet min_quality, and
    accelerator-hours must not exceed the budget. If none qualifies, raise
    RuntimeError rather than silently lowering the target.
    """
    if not results:
        raise ValueError("At least one result is required.")
    if not math.isfinite(min_quality) or not 0.0 <= min_quality <= 1.0:
        raise ValueError("min_quality must be finite and between 0 and 1.")
    if not math.isfinite(max_accelerator_hours) or max_accelerator_hours <= 0:
        raise ValueError("max_accelerator_hours must be finite and positive.")

    valid: list[RunResult] = []
    invalid_count = 0
    for result in results:
        try:
            result.validate()
        except (AttributeError, ValueError):
            invalid_count += 1
            continue
        valid.append(result)

    eligible = [
        result for result in valid
        if result.quality >= min_quality
        and result.accelerator_hours <= max_accelerator_hours
    ]
    if not eligible:
        detail = f" No valid candidates were supplied ({invalid_count} invalid)." if invalid_count else ""
        raise RuntimeError(
            "No measured run meets both the quality threshold and compute budget." + detail
        )

    best = max(
        eligible,
        key=lambda run: (
            run.quality / run.accelerator_hours,
            run.quality,
            -run.accelerator_hours,
        ),
    )
    return Selection(
        run=best,
        quality_margin=best.quality - min_quality,
        quality_per_accelerator_hour=best.quality / best.accelerator_hours,
        eligible_run_count=len(eligible),
        considered_run_count=len(results),
    )
