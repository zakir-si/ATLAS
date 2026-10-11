import json
import subprocess
import sys
from pathlib import Path


def test_analysis_rejects_empty_input(tmp_path: Path) -> None:
    data = tmp_path / "runs.jsonl"
    data.write_text("", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "experiments/validation/analyze_selection.py",
         "--input", str(data), "--output-dir", str(tmp_path / "out"),
         "--min-quality", "0.1", "--max-hours", "1"],
        capture_output=True, text=True,
    )
    assert proc.returncode != 0
    assert "No run records found" in proc.stderr


def test_analysis_runs_on_synthetic_records(tmp_path: Path) -> None:
    data = tmp_path / "runs.jsonl"
    rows = []
    for seed in (41, 42, 43):
        for config, q, hours in (("cheap", .2, .1), ("mid", .3, .2), ("long", .4, .4)):
            rows.append({"trial_id": f"seed-{seed}", "config_id": config,
                "selection_quality": q, "test_quality": q - .01,
                "accelerator_hours": hours, "peak_memory_gb": 2.0,
                "tokens_per_second": 10.0, "gpu_name": "synthetic",
                "gpu_count": 1, "model_id": "synthetic-model", "model_revision": "rev",
                "dataset_id": "synthetic-data", "dataset_revision": "rev"})
    data.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "experiments/validation/analyze_selection.py",
         "--input", str(data), "--output-dir", str(tmp_path / "out"),
         "--min-quality", "0.1", "--max-hours", "0.3", "--bootstrap-samples", "100"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "out" / "analysis_summary.json").exists()
    summary = json.loads((tmp_path / "out" / "analysis_summary.json").read_text())
    assert summary["test_quality_used_for_selection"] is False
