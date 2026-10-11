"""Run one fixed LoRA fine-tuning candidate and append a JSONL measurement record."""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import subprocess
import time
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config-id", required=True)
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--max-steps", required=True, type=int)
    p.add_argument("--learning-rate", required=True, type=float)
    p.add_argument("--lora-rank", required=True, type=int)
    p.add_argument("--records-jsonl", type=Path, default=Path("artifacts/validation/runs.jsonl"))
    p.add_argument("--output-dir", type=Path, default=Path("artifacts/candidate-runs"))
    p.add_argument("--model-id", default="Qwen/Qwen2.5-0.5B")
    p.add_argument("--model-revision", default="main", help="For final study, pin and record an immutable commit.")
    p.add_argument("--dataset-id", default="Salesforce/wikitext")
    p.add_argument("--dataset-config", default="wikitext-2-raw-v1")
    p.add_argument("--dataset-revision", default="main", help="For final study, pin and record an immutable commit.")
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--skip-test", action="store_true", help="Pilot/debugging only.")
    args = p.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU not detected. Use a GPU runtime and record the actual hardware.")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.cuda.reset_peak_memory_stats()
    dataset = load_dataset(args.dataset_id, args.dataset_config, revision=args.dataset_revision)
    for split in ("train", "validation", "test"):
        if split not in dataset or "text" not in dataset[split].column_names:
            raise ValueError(f"Expected train/validation/test splits with a text column; got {list(dataset.keys())}")
        dataset[split] = dataset[split].filter(lambda r: bool(str(r["text"]).strip()))
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, revision=args.model_revision, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    encoded = {}
    for split in ("train", "validation", "test"):
        encoded[split] = dataset[split].map(tokenize, batched=True, remove_columns=dataset[split].column_names)
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(args.model_id, revision=args.model_revision,
        torch_dtype=dtype, low_cpu_mem_usage=True)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(task_type=TaskType.CAUSAL_LM, r=args.lora_rank,
        lora_alpha=2 * args.lora_rank, lora_dropout=0.05, target_modules="all-linear"))
    run_dir = args.output_dir / f"{args.config_id}-seed{args.seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    training_args = TrainingArguments(output_dir=str(run_dir), max_steps=args.max_steps,
        per_device_train_batch_size=1, per_device_eval_batch_size=1, gradient_accumulation_steps=4,
        learning_rate=args.learning_rate, warmup_ratio=0.03, logging_steps=max(1, min(10, args.max_steps)),
        eval_strategy="no", save_strategy="no", gradient_checkpointing=True,
        bf16=torch.cuda.is_bf16_supported(), fp16=not torch.cuda.is_bf16_supported(),
        report_to="none", seed=args.seed, data_seed=args.seed, dataloader_num_workers=0,
        optim="adamw_torch", remove_unused_columns=False)
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    trainer = Trainer(model=model, args=training_args, train_dataset=encoded["train"], data_collator=collator)
    torch.cuda.synchronize()
    start = time.perf_counter()
    trainer.train()
    torch.cuda.synchronize()
    train_seconds = time.perf_counter() - start
    torch.cuda.synchronize()
    start = time.perf_counter()
    val = trainer.evaluate(eval_dataset=encoded["validation"], metric_key_prefix="validation")
    torch.cuda.synchronize()
    val_seconds = time.perf_counter() - start
    test = {}
    test_seconds = 0.0
    if not args.skip_test:
        torch.cuda.synchronize()
        start = time.perf_counter()
        test = trainer.evaluate(eval_dataset=encoded["test"], metric_key_prefix="test")
        torch.cuda.synchronize()
        test_seconds = time.perf_counter() - start
    val_loss = float(val["validation_loss"])
    test_loss = float(test["test_loss"]) if test else None
    if not math.isfinite(val_loss) or val_loss < 0 or (test_loss is not None and not math.isfinite(test_loss)):
        raise ValueError("Non-finite loss encountered; preserve the failure and investigate.")
    gpu_count = torch.cuda.device_count()
    row = {
        "trial_id": f"seed-{args.seed}", "config_id": args.config_id,
        "selection_quality": 1 / (1 + val_loss),
        "test_quality": None if test_loss is None else 1 / (1 + test_loss),
        "accelerator_hours": (train_seconds + val_seconds) * gpu_count / 3600,
        "peak_memory_gb": torch.cuda.max_memory_allocated() / 1024**3,
        "tokens_per_second": 0.0,
        "validation_loss": val_loss, "test_loss": test_loss,
        "test_perplexity": None if test_loss is None else math.exp(min(test_loss, 20)),
        "train_seconds": train_seconds, "validation_eval_seconds": val_seconds,
        "test_eval_seconds_not_charged_to_selection": test_seconds,
        "model_id": args.model_id, "model_revision": args.model_revision,
        "dataset_id": args.dataset_id, "dataset_config": args.dataset_config,
        "dataset_revision": args.dataset_revision, "seed": args.seed,
        "gpu_name": torch.cuda.get_device_name(0), "gpu_count": gpu_count,
        "python_version": platform.python_version(), "torch_version": torch.__version__,
        "code_git_commit": git_commit(),
        "note": "Pilot/test outputs are measurements, not proof of ATLAS benefit. Pin immutable revisions for final study."
    }
    # JSONL records are append-only. Keep raw records and failed-run logs in persistent storage.
    args.records_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.records_jsonl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, allow_nan=False) + "\n")
    (run_dir / "run_manifest.json").write_text(json.dumps(row, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Recorded {args.config_id} seed={args.seed}; validation_loss={val_loss:.5f}; "
          f"accelerator_hours={row['accelerator_hours']:.6f}")
    if args.skip_test:
        print("Pilot mode: held-out test evaluation skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
