"""I1: the nuisance floor, measured on the same geometry as the effect it gates.

The floor in `validate_instrument.py` is measured on a content-free frame scored
over ["Code A".."Code D"] and then used to gate binary Yes/No clinical items.
Four mismatches at once (option count, option tokenisation, prompt length, and
max-of-12 against a single targeted delta) inflate it by construction, and the
option-token mismatch makes its magnitude move 2-3x across score keys while the
gate effect is bit-identical across two of them (D051).

This measures the same statistic as the gate -- the sex-parameter flip on the
target option -- on Group 4, which is clinically real, adult, has pregnancy
explicitly excluded, carries no sex-specific content, and is already scored. A
flip there should move nothing, so whatever it moves is instrument noise on the
right geometry.

Stratified by option count so a binary contrast is gated by a binary floor.
See docs/instrument_tuning_log.md entry I1.
"""
from __future__ import annotations

import json
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
N_BOOT = 10_000
SEED = 20260103
RAW_DIRS = {"pmi": "results/raw",
            "mean_logprob": "results/raw__mean_logprob",
            "sum_logprob": "results/raw__sum_logprob"}


def target_deltas(d: pd.DataFrame) -> pd.DataFrame:
    """Signed sex-parameter flip on the target option, per matched item.

    Keys mirror `stats.spcu_positive_control` exactly, so the floor and the
    margin are the same statistic computed on different stimuli.
    """
    d = d[d["option"].astype(str).str.strip()
          == d["target_option"].astype(str).str.strip()].copy()
    keys = ["model_id", "revision", "vignette_id", "paraphrase",
            "gender_identity", "cue"]
    wide = d.pivot_table(index=keys, columns="spcu", values="norm_prob",
                         aggfunc="first").reset_index()
    if not {"female", "male"} <= set(wide.columns):
        raise RuntimeError("need both sex-parameter arms")
    wide["delta"] = wide["female"] - wide["male"]
    return wide


def floor_for(deltas: pd.DataFrame, rng: np.random.Generator) -> dict:
    """Cluster bootstrap over vignettes, matching the gate's aggregation."""
    by_vig = deltas.groupby("vignette_id")["delta"].mean()
    vigs = by_vig.index.to_numpy()
    if len(vigs) == 0:
        return {}
    boot = np.array([np.abs(by_vig.loc[rng.choice(vigs, len(vigs))].mean())
                     for _ in range(N_BOOT)])
    return {
        "n_vignettes": int(len(vigs)),
        "n_items": int(len(deltas)),
        # Direct analogue of the old statistic: worst single vignette.
        "floor_max_abs_vignette": float(np.abs(by_vig).max()),
        "floor_mean_abs_vignette": float(np.abs(by_vig).mean()),
        # The principled threshold: upper tail of the gate statistic's own null
        # distribution, so the floor carries an interval instead of being a max.
        "floor_boot_q95": float(np.quantile(boot, 0.95)),
        "floor_boot_q975": float(np.quantile(boot, 0.975)),
        "per_vignette": "; ".join(f"{v}={m:+.4f}" for v, m in by_vig.items()),
    }


def main() -> None:
    rows = []
    for key, rel in RAW_DIRS.items():
        files = sorted((ROOT / rel).glob("*.parquet"))
        raw = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        if "cue" not in raw.columns:
            raw["cue"] = "cue_absent"
        raw["group"] = raw["group"].astype(str)

        # Option count per vignette: the stratifier. A binary contrast must be
        # gated by a binary floor.
        nopt = (raw.groupby("vignette_id")["option"].nunique().to_dict())

        g4 = raw[raw["group"] == "4"].copy()
        dl = target_deltas(g4)
        dl["n_options"] = dl["vignette_id"].map(nopt)

        for (mid, rev), g in dl.groupby(["model_id", "revision"]):
            for n_opt, gg in g.groupby("n_options"):
                rng = np.random.default_rng(SEED)
                f = floor_for(gg, rng)
                if f:
                    rows.append({"score_key": key, "model_id": mid,
                                 "revision": rev, "n_options": int(n_opt),
                                 **f})
    out = pd.DataFrame(rows).sort_values(
        ["score_key", "n_options", "model_id"]).reset_index(drop=True)
    dest = ROOT / "results/tables/i1_matched_floor.csv"
    write_table(out, dest)
    print(f"wrote {dest}  ({len(out)} rows)")

    # Comparison against the floor actually in force, on the binary stratum
    # that gates Group 2.
    old = {}
    for f in sorted((ROOT / "results/tables").glob(
            "rq0_instrument_validation__*.json")):
        d = json.loads(f.read_text())
        t3 = d["tests"]["T3_nuisance_floor"]["max_abs_delta_norm_prob_by_key"]
        for k, v in t3.items():
            old[(k, d["model"])] = max(float(x) for x in v)

    cmp = out[out["n_options"] == 2].copy()
    cmp["old_floor"] = [old.get((r.score_key, r.model_id), np.nan)
                        for r in cmp.itertuples()]
    cmp["ratio_new_over_old"] = cmp["floor_max_abs_vignette"] / cmp["old_floor"]
    write_table(cmp, ROOT / "results/tables/i1_floor_comparison.csv")

    for key in RAW_DIRS:
        s = cmp[cmp["score_key"] == key]
        if s.empty:
            continue
        print(f"\n=== {key} : binary stratum (gates Group 2) ===")
        print(s[["model_id", "old_floor", "floor_max_abs_vignette",
                 "floor_boot_q95", "ratio_new_over_old"]]
              .to_string(index=False,
                         float_format=lambda x: f"{x:9.4f}"))
        moved = (s["ratio_new_over_old"] - 1).abs() > 0.25
        print(f"  models whose floor moved >25%: {int(moved.sum())}/{len(s)}"
              f"   median ratio {s['ratio_new_over_old'].median():.3f}")


if __name__ == "__main__":
    main()
