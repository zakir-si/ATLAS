"""Analyze a fixed candidate pool using ATLAS's actual selection function.

This reports selected-run resource use, not end-to-end search savings.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from atlas.controller import select_best_run
from atlas.models import RunResult


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        required = {"trial_id", "config_id", "selection_quality", "test_quality",
                    "accelerator_hours", "peak_memory_gb", "tokens_per_second"}
        missing = required - row.keys()
        if missing:
            raise ValueError(f"Line {number} missing fields: {sorted(missing)}")
        for key in ("selection_quality", "test_quality", "accelerator_hours",
                    "peak_memory_gb", "tokens_per_second"):
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"Line {number}: {key} must be a finite number")
        if not 0 <= row["selection_quality"] <= 1 or not 0 <= row["test_quality"] <= 1:
            raise ValueError(f"Line {number}: quality values must be in [0, 1]")
        if row["accelerator_hours"] <= 0:
            raise ValueError(f"Line {number}: accelerator_hours must be positive")
        rows.append(row)
    if not rows:
        raise ValueError("No run records found")
    return rows


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    pos = (len(values) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] if lo == hi else values[lo] * (hi - pos) + values[hi] * (pos - lo)


def bootstrap_ci(values: list[float], n: int, seed: int) -> list[float | None]:
    if len(values) < 2:
        return [None, None]
    rng = random.Random(seed)
    means = [statistics.fmean(rng.choice(values) for _ in values) for _ in range(n)]
    return [percentile(means, .025), percentile(means, .975)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--min-quality", required=True, type=float)
    parser.add_argument("--max-hours", required=True, type=float)
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261011)
    args = parser.parse_args()
    if not 0 <= args.min_quality <= 1 or args.max_hours <= 0 or args.bootstrap_samples < 100:
        parser.error("invalid threshold/budget or too few bootstrap samples")
    rows = read_jsonl(args.input)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row["trial_id"])].append(row)
    if len(groups) < 2:
        raise ValueError("Need at least two trial blocks; >=5 is recommended for a preliminary study")
    expected = None
    for trial, group in groups.items():
        ids = [str(r["config_id"]) for r in group]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate candidate in trial {trial}")
        configs = set(ids)
        if expected is None:
            expected = configs
        elif configs != expected:
            raise ValueError(f"Candidate grid mismatch in trial {trial}")
    # Avoid pooling unlike experiments.
    for field in ("gpu_name", "gpu_count", "model_id", "model_revision", "dataset_id", "dataset_revision"):
        values = {str(r[field]) for r in rows if r.get(field) not in (None, "")}
        if len(values) > 1:
            raise ValueError(f"Mixed {field} values; analyze separate studies")

    rng = random.Random(args.seed)
    selected: list[dict[str, Any]] = []
    for trial, group in sorted(groups.items()):
        eligible = [r for r in group if r["selection_quality"] >= args.min_quality
                    and r["accelerator_hours"] <= args.max_hours]
        if not eligible:
            raise ValueError(f"No eligible candidate in trial {trial}; do not change threshold post hoc")
        results = [RunResult(name=str(r["config_id"]), quality=float(r["selection_quality"]),
                    accelerator_hours=float(r["accelerator_hours"]),
                    peak_memory_gb=float(r["peak_memory_gb"]),
                    tokens_per_second=float(r["tokens_per_second"])) for r in group]
        atlas_selection = select_best_run(results, min_quality=args.min_quality,
                                          max_accelerator_hours=args.max_hours)
        by_id = {str(r["config_id"]): r for r in group}
        picks = {
            "ATLAS_quality_per_hour": by_id[atlas_selection.run.name],
            "best_validation_quality": max(eligible, key=lambda r: (r["selection_quality"], -r["accelerator_hours"])),
            "fastest_eligible": min(eligible, key=lambda r: (r["accelerator_hours"], -r["selection_quality"])),
            "random_eligible": rng.choice(eligible),
        }
        for policy, row in picks.items():
            selected.append({"trial_id": trial, "policy": policy, "selected_config_id": row["config_id"],
                "validation_quality": row["selection_quality"], "heldout_test_quality": row["test_quality"],
                "selected_run_accelerator_hours": row["accelerator_hours"],
                "peak_memory_gb": row["peak_memory_gb"], "test_loss": row.get("test_loss"),
                "test_perplexity": row.get("test_perplexity")})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "selected_runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(selected[0]))
        writer.writeheader()
        writer.writerows(selected)
    summaries = {}
    policies = sorted({r["policy"] for r in selected})
    for policy in policies:
        subset = [r for r in selected if r["policy"] == policy]
        hours = [float(r["selected_run_accelerator_hours"]) for r in subset]
        quality = [float(r["heldout_test_quality"]) for r in subset]
        summaries[policy] = {
            "n_trials": len(subset), "mean_selected_run_accelerator_hours": statistics.fmean(hours),
            "mean_heldout_test_quality": statistics.fmean(quality),
            "hours_bootstrap_95_ci_mean": bootstrap_ci(hours, args.bootstrap_samples, args.seed),
            "test_quality_bootstrap_95_ci_mean": bootstrap_ci(quality, args.bootstrap_samples, args.seed + 1),
        }
    summary = {
        "analysis_version": 1, "n_independent_trials": len(groups), "n_candidate_rows": len(rows),
        "min_quality": args.min_quality, "max_hours": args.max_hours,
        "bootstrap_samples": args.bootstrap_samples, "bootstrap_seed": args.seed,
        "test_quality_used_for_selection": False,
        "search_cost_included": False,
        "warning": "All policies select from already-measured candidates. These are selected-run hours, not total search savings.",
        "policy_results": summaries,
    }
    (args.output_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
