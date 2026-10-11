import pytest

from atlas.benchmark import compare_repeated_runs
from atlas.models import RunResult


def runs(name: str, quality: float, hours: float) -> list[RunResult]:
    return [
        RunResult(f"{name}-1", quality, hours, 8.0, 100.0),
        RunResult(f"{name}-2", quality, hours, 8.5, 110.0),
    ]


def test_reports_compute_reduction_when_quality_gate_passes() -> None:
    result = compare_repeated_runs(
        runs("baseline", 0.90, 10.0),
        runs("candidate", 0.895, 7.0),
        min_quality=0.88,
        max_quality_drop=0.01,
    )

    assert result.compute_reduction_percent == pytest.approx(30.0)
    assert result.quality_delta == pytest.approx(-0.005)
    assert result.quality_gate_passed is True
    assert result.baseline_runs == 2
    assert result.candidate_runs == 2


def test_quality_gate_fails_when_candidate_quality_is_too_low() -> None:
    result = compare_repeated_runs(
        runs("baseline", 0.92, 10.0),
        runs("candidate", 0.85, 5.0),
        min_quality=0.88,
        max_quality_drop=0.01,
    )

    assert result.compute_reduction_percent == pytest.approx(50.0)
    assert result.quality_gate_passed is False


def test_requires_repeated_runs() -> None:
    with pytest.raises(ValueError, match="At least two runs per group"):
        compare_repeated_runs(
            [RunResult("baseline", 0.9, 10.0, 8.0, 100.0)],
            runs("candidate", 0.9, 5.0),
            min_quality=0.8,
        )


@pytest.mark.parametrize("min_quality", [-0.1, 1.1, float("nan")])
def test_rejects_invalid_quality_threshold(min_quality: float) -> None:
    with pytest.raises(ValueError, match="min_quality"):
        compare_repeated_runs(
            runs("baseline", 0.9, 10.0),
            runs("candidate", 0.9, 5.0),
            min_quality=min_quality,
        )


def test_rejects_invalid_measurements() -> None:
    invalid = [
        RunResult("bad", 0.9, -1.0, 8.0, 100.0),
        RunResult("good", 0.9, 5.0, 8.0, 100.0),
    ]
    with pytest.raises(ValueError, match="Invalid baseline run"):
        compare_repeated_runs(
            invalid,
            runs("candidate", 0.9, 5.0),
            min_quality=0.8,
        )
