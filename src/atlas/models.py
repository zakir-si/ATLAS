"""Validated data models shared by the selector and API."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunResult:
    """Measurements from one completed training/evaluation run.

    quality is a task-specific score normalized to [0, 1].
    accelerator_hours is total accelerator-hours, not wall-clock hours.
    """

    name: str
    quality: float
    accelerator_hours: float
    peak_memory_gb: float
    tokens_per_second: float

    def validate(self) -> None:
        """Raise ValueError for invalid measurements."""
        if not self.name.strip():
            raise ValueError("Run name must not be empty.")
        values = {
            "quality": self.quality,
            "accelerator_hours": self.accelerator_hours,
            "peak_memory_gb": self.peak_memory_gb,
            "tokens_per_second": self.tokens_per_second,
        }
        for field, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{field} must be finite.")
        if not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between 0 and 1.")
        if self.accelerator_hours <= 0.0:
            raise ValueError("accelerator_hours must be greater than zero.")
        if self.peak_memory_gb < 0.0:
            raise ValueError("peak_memory_gb must be non-negative.")
        if self.tokens_per_second < 0.0:
            raise ValueError("tokens_per_second must be non-negative.")


@dataclass(frozen=True, slots=True)
class Selection:
    """Selected eligible run and derived metrics."""

    run: RunResult
    quality_margin: float
    quality_per_accelerator_hour: float
    eligible_run_count: int
    considered_run_count: int
