"""Rerun the RQ2/RQ3 statistics under a non-primary score key (D042).

pythia-1.4b fails T2 signal recovery under `pmi`, the preregistered primary key,
while passing under `mean_logprob` and `sum_logprob`. Any 1.4b null under pmi is
therefore instrument-limited, and the claim needs a second key to be readable.

No model is re-run. `src/score_outputs.py` writes every score key onto every
option row and uses `score_key` only to choose which column `norm_prob` softmaxes,
so an alternative key is a re-softmax of data already on disk. The softmax is over
the option set within one prompt, which is exactly what score_outputs does.

    .venv/bin/python -m scripts.sensitivity_score_key --key mean_logprob

Writes results/raw__<key>/ and results/tables__<key>/ so the primary tables are
never overwritten by a sensitivity analysis.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results/raw"


def resoftmax(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Replace norm_prob with the softmax of `key` within each prompt."""
    d = df.copy()
    d["score_key"] = key

    # Keyed on the model-scoped prompt, not prompt_id alone. One file holds one
    # run so they coincide here, but the bare key is the same mistake that made
    # outcome_rows() flag four models as duplicates of each other.
    gkeys = [c for c in ("model_id", "revision", "prompt_id") if c in d.columns]
    d["norm_prob"] = d.groupby(gkeys, sort=False)[key].transform(
        lambda v: np.exp(v - v.max()) / np.exp(v - v.max()).sum())
    out = d
    # The softmax must be a distribution over each prompt's own option set, or
    # the outcome is not a probability and every Delta is meaningless.
    sums = out.groupby(gkeys)["norm_prob"].sum()
    bad = sums[(sums - 1.0).abs() > 1e-9]
    if len(bad):
        raise RuntimeError(f"{len(bad)} prompts do not sum to 1 after resoftmax")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--key", default="mean_logprob",
                    choices=["mean_logprob", "sum_logprob", "pmi"])
    args = ap.parse_args()

    files = sorted(RAW.glob("*.parquet"))
    if not files:
        raise SystemExit(f"no scored results in {RAW}")

    out_raw = ROOT / f"results/raw__{args.key}"
    out_tab = ROOT / f"results/tables__{args.key}"
    if out_raw.exists():
        shutil.rmtree(out_raw)
    out_raw.mkdir(parents=True)
    out_tab.mkdir(parents=True, exist_ok=True)

    for f in files:
        df = pd.read_parquet(f)
        if args.key not in df.columns:
            raise SystemExit(f"{f.name} has no column {args.key!r}")
        resoftmax(df, args.key).to_parquet(out_raw / f.name, index=False)
    print(f"rewrote {len(files)} run(s) under score_key={args.key} -> "
          f"{out_raw.relative_to(ROOT)}")

    # The floor files live in the primary tables dir and are keyed on the pmi
    # floor. Copy them across so the equivalence margin and the T2 flag are the
    # same measured quantities, not silently recomputed ones.
    for f in (ROOT / "results/tables").glob("rq0_instrument_validation__*"):
        shutil.copy2(f, out_tab / f.name)

    from src import stats
    # stats.main() parses sys.argv itself, so this script's own flags have to be
    # cleared or argparse rejects them there.
    sys.argv = [sys.argv[0]]
    stats.RAW, stats.TABLES = out_raw, out_tab
    stats.PRIMARY_SCORE_KEY = args.key
    print(f"\n=== statistics under score_key={args.key} "
          f"(SENSITIVITY, not the preregistered primary) ===")
    stats.main()


if __name__ == "__main__":
    main()
