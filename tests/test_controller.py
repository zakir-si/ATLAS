import pytest

from atlas.controller import select_best_run
from atlas.models import RunResult


def run(name: str, quality: float, hours: float) -> RunResult:
    return RunResult(name, quality, hours, 8.0, 100.0)


def test_selects_best_eligible_run() -> None:
    results = [run("baseline", 0.90, 10.0), run("efficient", 0.88, 6.0),
               run("too-low-quality", 0.70, 1.0)]
    selected = select_best_run(results, min_quality=0.85, max_accelerator_hours=8.0)
    assert selected.run.name == "efficient"
    assert selected.eligible_run_count == 1
    assert selected.considered_run_count == 3
    assert selected.quality_margin == pytest.approx(0.03)


def test_quality_threshold_is_not_relaxed() -> None:
    with pytest.raises(RuntimeError, match="No measured run"):
        select_best_run([run("bad", 0.79, 1.0)], min_quality=0.80, max_accelerator_hours=5.0)


def test_compute_budget_is_enforced() -> None:
    with pytest.raises(RuntimeError, match="compute budget"):
        select_best_run([run("slow", 0.99, 6.0)], min_quality=0.90, max_accelerator_hours=5.0)


def test_empty_results_rejected() -> None:
    with pytest.raises(ValueError, match="At least one"):
        select_best_run([], min_quality=0.8, max_accelerator_hours=1)


@pytest.mark.parametrize("quality", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_quality_is_not_selected(quality: float) -> None:
    selected = select_best_run([run("invalid", quality, 1.0), run("valid", 0.8, 2.0)],
                               min_quality=0.7, max_accelerator_hours=3.0)
    assert selected.run.name == "valid"


def test_invalid_measurement_is_not_selected() -> None:
    selected = select_best_run([run("invalid", 0.9, -1.0), run("valid", 0.85, 2.0)],
                               min_quality=0.8, max_accelerator_hours=3.0)
    assert selected.run.name == "valid"
