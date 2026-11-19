"""Measure forward-pass latency per model size on this machine.

RQ2/RQ3's primary method is log-probability scoring of answer options, which is
one forward pass per scored item. This script measures that pass directly so the
project schedule rests on measured numbers rather than estimates.

Usage:
    .venv/bin/python scripts/bench_forward.py
    .venv/bin/python scripts/bench_forward.py --models EleutherAI/pythia-70m
"""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Sizes small enough to download quickly; larger members of the ladder are
# projected from these measurements (see results/tables/rq0_bench.json).
DEFAULT_MODELS = [
    "EleutherAI/pythia-70m",
    "EleutherAI/pythia-160m",
    "EleutherAI/pythia-410m",
    "EleutherAI/pythia-1.4b",
]

PROMPT_TOKENS = 256  # representative vignette + question length
N_WARMUP = 3
N_TRIALS = 20


def bench(model_id: str, device: str) -> dict:
    tok = AutoTokenizer.from_pretrained(model_id)
    t0 = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.bfloat16)
    model.to(device).eval()
    load_s = time.perf_counter() - t0

    n_params = sum(p.numel() for p in model.parameters())
    ids = torch.randint(0, tok.vocab_size, (1, PROMPT_TOKENS), device=device)

    with torch.no_grad():
        for _ in range(N_WARMUP):
            model(ids)
        if device == "cuda":
            torch.cuda.synchronize()
        elif device == "mps":
            torch.mps.synchronize()

        t0 = time.perf_counter()
        for _ in range(N_TRIALS):
            model(ids)
        if device == "cuda":
            torch.cuda.synchronize()
        elif device == "mps":
            torch.mps.synchronize()
        elapsed = time.perf_counter() - t0

    per_pass_ms = (elapsed / N_TRIALS) * 1000

    del model
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    elif device == "mps":
        torch.mps.empty_cache()

    return {
        "model": model_id,
        "params_b": round(n_params / 1e9, 4),
        "weights_gb_bf16": round(n_params * 2 / 1e9, 2),
        "load_s": round(load_s, 1),
        "forward_ms": round(per_pass_ms, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    ap.add_argument("--out", default="results/tables/rq0_bench.json")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device={device}  torch={torch.__version__}  "
          f"prompt_tokens={PROMPT_TOKENS}  trials={N_TRIALS}\n")

    rows = []
    for mid in args.models:
        try:
            row = bench(mid, device)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"{mid:30s} FAILED: {type(exc).__name__}: {exc}")
            continue
        rows.append(row)
        print(f"{row['model']:30s} {row['params_b']:>7.3f}B  "
              f"{row['weights_gb_bf16']:>6.2f}GB  "
              f"load {row['load_s']:>5.1f}s  "
              f"forward {row['forward_ms']:>7.1f}ms")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"device": device, "torch": torch.__version__,
         "prompt_tokens": PROMPT_TOKENS, "trials": N_TRIALS, "rows": rows},
        indent=2,
    ))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
