#!/usr/bin/env bash
set -euo pipefail
OUT="${RUNS_FILE:-artifacts/validation/final_runs.jsonl}"
mkdir -p "$(dirname "$OUT")"
for seed in 41 42 43 44 45; do
  python experiments/validation/train_candidate.py --config-id steps50-r4-lr1e4 --seed "$seed" --max-steps 50 --learning-rate 0.0001 --lora-rank 4 --records-jsonl "$OUT"
  python experiments/validation/train_candidate.py --config-id steps100-r8-lr2e4 --seed "$seed" --max-steps 100 --learning-rate 0.0002 --lora-rank 8 --records-jsonl "$OUT"
  python experiments/validation/train_candidate.py --config-id steps150-r8-lr2e4 --seed "$seed" --max-steps 150 --learning-rate 0.0002 --lora-rank 8 --records-jsonl "$OUT"
done
printf 'Completed the declared candidate grid. Preserve logs and do not change the preregistered analysis post hoc.\n'
