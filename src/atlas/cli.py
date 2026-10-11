"""Command-line interface for selecting from measured run records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from atlas.controller import select_best_run
from atlas.models import RunResult


def main() -> None:
    parser = argparse.ArgumentParser(prog="atlas", description="ATLAS local training utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)
    select_parser = subparsers.add_parser("select", help="select from JSON run measurements")
    select_parser.add_argument("input", type=Path, help="JSON file containing an array of run objects")
    select_parser.add_argument("--min-quality", type=float, required=True)
    select_parser.add_argument("--max-accelerator-hours", type=float, required=True)
    args = parser.parse_args()

    if args.command == "select":
        try:
            payload = json.loads(args.input.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ValueError("Input JSON must be an array of run objects.")
            runs = [RunResult(**item) for item in payload]
            selected = select_best_run(
                runs,
                min_quality=args.min_quality,
                max_accelerator_hours=args.max_accelerator_hours,
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError, RuntimeError) as exc:
            print(f"atlas: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps({
            "selected": {
                "name": selected.run.name,
                "quality": selected.run.quality,
                "accelerator_hours": selected.run.accelerator_hours,
            },
            "quality_margin": selected.quality_margin,
            "quality_per_accelerator_hour": selected.quality_per_accelerator_hour,
            "eligible_run_count": selected.eligible_run_count,
            "considered_run_count": selected.considered_run_count,
        }, indent=2))


if __name__ == "__main__":
    main()
