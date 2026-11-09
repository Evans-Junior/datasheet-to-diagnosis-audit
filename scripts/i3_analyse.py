"""I3: gate margin and matched floor per elicitation configuration.

Same statistic as the primary gate (sex-parameter flip on the option that is
correct under one arm and not the other, Group 2) and the same matched floor as
I1 (sex-parameter flip on the target option, binary Group 4), recomputed inside
each configuration so margin and floor always come from the same harness.

Pass criterion fixed in docs/instrument_tuning_log.md before running:
at least 2 of 7 Pythia models with a Group 2 margin exceeding their own
matched floor.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# D090: stamps the prompt-set hash into every table it writes. Self-contained
# path setup -- this runs as a script, and ROOT may be defined further down.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.provenance import write_table

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["config", "model_id", "score_key"]


def gate_margin(d: pd.DataFrame) -> pd.Series:
    """Group 2: p(correct option | its spcu) - p(same option | other spcu)."""
    g2 = d[d["vignette_id"].str.startswith("G2")].copy()
    g2["option"] = g2["option"].str.strip()
    g2["reference_answer"] = g2["reference_answer"].astype(str).str.strip()
    ref = (g2.groupby(["vignette_id", "spcu"])["reference_answer"]
             .agg(lambda s: s.unique()[0]).to_dict())
    idx = KEYS + ["vignette_id", "paraphrase", "gender_identity", "cue",
                  "option"]
    w = g2.pivot_table(index=idx, columns="spcu", values="norm_prob",
                       aggfunc="first").reset_index()
    rows = []
    for r in w.itertuples(index=False):
        good = [a for a in ("female", "male")
                if ref.get((r.vignette_id, a)) == r.option]
        if len(good) != 1:
            continue
        bad = "male" if good[0] == "female" else "female"
        rows.append({**{k: getattr(r, k) for k in KEYS},
                     "vignette_id": r.vignette_id,
                     "margin": getattr(r, good[0]) - getattr(r, bad)})
    per = pd.DataFrame(rows)
    return (per.groupby(KEYS + ["vignette_id"])["margin"].mean()
               .groupby(KEYS).mean())


def matched_floor(d: pd.DataFrame) -> pd.Series:
    """Binary Group 4: |sex-parameter flip on the target option|, worst item."""
    g4 = d[d["vignette_id"].str.startswith("G4")].copy()
    g4 = g4[g4["option"].str.strip() == g4["target_option"].str.strip()]
    idx = KEYS + ["vignette_id", "paraphrase", "gender_identity", "cue"]
    w = g4.pivot_table(index=idx, columns="spcu", values="norm_prob",
                       aggfunc="first").reset_index()
    w["delta"] = w["female"] - w["male"]
    return (w.groupby(KEYS + ["vignette_id"])["delta"].mean().abs()
             .groupby(KEYS).max())


def main() -> None:
    d = pd.read_parquet(ROOT / "results/tables/i3_elicitation_raw.parquet")
    out = pd.concat([gate_margin(d).rename("margin"),
                     matched_floor(d).rename("matched_floor")], axis=1)
    out["times_floor"] = out["margin"] / out["matched_floor"]
    out["gate"] = np.where(out["margin"] > out["matched_floor"],
                           "SENSITIVE", "INSENSITIVE")
    out = out.reset_index()
    write_table(out, ROOT / "results/tables/i3_gate_by_config.csv")

    order = ["baseline", "cloze", "fewshot"]
    for key in ("pmi", "mean_logprob"):
        print(f"\n================ score key: {key} ================")
        s = out[out["score_key"] == key]
        piv = s.pivot_table(index="model_id", columns="config",
                            values=["margin", "times_floor"])
        for stat in ("margin", "times_floor"):
            print(f"\n--- {stat} ---")
            print(piv[stat][[c for c in order if c in piv[stat].columns]]
                  .to_string(float_format=lambda x: f"{x:9.4f}"))
        print("\n--- pass count (margin > own matched floor) ---")
        for c in order:
            ss = s[s["config"] == c]
            if ss.empty:
                continue
            n = int((ss["gate"] == "SENSITIVE").sum())
            print(f"  {c:9s}  {n}/{len(ss)}"
                  f"   criterion >=2 -> {'PASS' if n >= 2 else 'FAIL'}")


if __name__ == "__main__":
    main()
