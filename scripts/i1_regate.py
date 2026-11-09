"""I1/I2: re-run the Group 2 gate against the matched-geometry floor.

Reuses `stats.spcu_positive_control` unchanged so the margin is the same
statistic as before; only the floor it is compared against changes.
See docs/instrument_tuning_log.md entries I1 and I2.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import src.stats as S  # noqa: E402

# D090: stamps the prompt-set hash into every table it writes. Self-contained
# path setup -- this runs as a script, and ROOT may be defined further down.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.provenance import write_table

RAW_DIRS = {"pmi": "results/raw",
            "mean_logprob": "results/raw__mean_logprob",
            "sum_logprob": "results/raw__sum_logprob"}
FLOOR_STAT = "floor_max_abs_vignette"

mf = pd.read_csv(ROOT / "results/tables/i1_matched_floor.csv")

# ---- I2: do the two log-probability floors coincide on single-token options? #
b = mf[mf["n_options"] == 2].pivot_table(
    index="model_id", columns="score_key", values=FLOOR_STAT)
gap = float((b["sum_logprob"] - b["mean_logprob"]).abs().max())
print(f"I2  max |sum_logprob floor - mean_logprob floor| on binary stratum "
      f"= {gap:.3e}   criterion <1e-9 -> {'PASS' if gap < 1e-9 else 'FAIL'}")
b4 = mf[mf["n_options"] == 4].pivot_table(
    index="model_id", columns="score_key", values=FLOOR_STAT)
print(f"    same on the 4-option stratum (multi-token options, where the two "
      f"keys must differ) = "
      f"{float((b4['sum_logprob'] - b4['mean_logprob']).abs().max()):.3e}")

# ---- I1: the gate, old floor against matched floor ------------------------- #
rows = []
for key, rel in RAW_DIRS.items():
    S.PRIMARY_SCORE_KEY = key
    S.RAW = ROOT / rel
    raw = S.load_raw()
    old_floors = S.load_floors()
    new = {r.model_id: getattr(r, FLOOR_STAT)
           for r in mf[(mf["score_key"] == key)
                       & (mf["n_options"] == 2)].itertuples()}
    gate = S.spcu_positive_control(raw, old_floors)
    for r in gate.itertuples(index=False):
        nf = new.get(r.model_id, np.nan)
        rows.append({
            "score_key": key, "model_id": r.model_id,
            "mean_margin": r.mean_margin,
            "old_floor": r.nuisance_floor, "old_gate": r.gate,
            "matched_floor": nf,
            "times_matched_floor": r.mean_margin / nf if nf else np.nan,
            "new_gate": ("SENSITIVE" if r.mean_margin > nf else "INSENSITIVE"),
        })

out = pd.DataFrame(rows)
write_table(out, ROOT / "results/tables/i1_gate_rerun.csv")
print(f"\nwrote {ROOT / 'results/tables/i1_gate_rerun.csv'}")
for key in RAW_DIRS:
    s = out[out["score_key"] == key]
    print(f"\n=== {key} ===")
    print(s[["model_id", "mean_margin", "old_floor", "old_gate",
             "matched_floor", "times_matched_floor", "new_gate"]]
          .to_string(index=False, float_format=lambda x: f"{x:9.4f}"))
    print(f"  pass count: old {(s['old_gate']=='SENSITIVE').sum()}/10  ->  "
          f"matched {(s['new_gate']=='SENSITIVE').sum()}/10")
