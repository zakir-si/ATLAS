#!/usr/bin/env bash
set -euo pipefail
OUT="${PILOT_RUNS_FILE:-artifacts/validation/pilot_runs.jsonl}"
mkdir -p "$(dirname "$OUT")"
for seed in 11 12 13; do
  python experiments/validation/train_candidate.py --config-id steps50-r4-lr1e4 --seed "$seed" --max-steps 50 --learning-rate 0.0001 --lora-rank 4 --skip-test --records-jsonl "$OUT"
  python experiments/validation/train_candidate.py --config-id steps100-r8-lr2e4 --seed "$seed" --max-steps 100 --learning-rate 0.0002 --lora-rank 8 --skip-test --records-jsonl "$OUT"
  python experiments/validation/train_candidate.py --config-id steps150-r8-lr2e4 --seed "$seed" --max-steps 150 --learning-rate 0.0002 --lora-rank 8 --skip-test --records-jsonl "$OUT"
done
