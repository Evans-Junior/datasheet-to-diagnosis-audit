"""Validation C: is an effect stable across paraphrases, or an artefact of wording? (D061)

WHY THIS EXISTS
---------------
Every reported delta averages three paraphrases of the same clinical findings.
Averaging is the right estimator, but it HIDES disagreement: +0.05, -0.04, +0.03
and +0.013, +0.013, +0.013 both average to roughly +0.013, and only the second
is a property of the vignette rather than of one sentence's phrasing.

This is not a hypothetical worry here. I3 found that all seven Pythia models
CHANGE THE SIGN of their Group 2 margin across three elicitation formats (D057).
A harness whose direction is that unstable across formats cannot be assumed
stable across paraphrases, so stability has to be measured rather than assumed.

WHAT IT REPORTS
---------------
Per (model, vignette, contrast, SPCU), the three paraphrase-level deltas, and:

  n_same_sign   how many of the three share the sign of their own mean (2 or 3)
  unanimous     all three agree in sign
  sd_across     spread across paraphrases, in the same units as the delta
  swamped       sd_across exceeds |mean|, i.e. wording moves the answer more
                than the gender label does

Then, aggregated: of the vignette-level effects that CLEAR THE FLOOR -- the ones
that would otherwise be reported as findings -- what fraction are unanimous?
That number is the headline, because a floor-clearing effect with 2/3 sign
agreement is one paraphrase away from vanishing and must not be reported as
robust without saying so.

HOW TO READ A LOW SCORE
-----------------------
Low unanimity is NOT automatically a defect in the instrument. Three readings:

  1. the effect is real but small relative to paraphrase sensitivity -> report
     it with the inconsistency stated, and widen the vignette set;
  2. the paraphrases are not actually equivalent -> an authoring fault, fixable;
  3. the model is simply unstable to surface form -> a property of the MODEL and
     a reportable result in its own right, as D057 already found for Pythia.

This script cannot distinguish them. It flags the cells that need the judgement.

Usage:
    .venv/bin/python scripts/paraphrase_consistency.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import stats as S  # noqa: E402

# D090: stamps the prompt-set hash into every table it writes. Self-contained
# path setup -- this runs as a script, and ROOT may be defined further down.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.provenance import write_table

OUT_CELL = ROOT / "results/tables/v_c_paraphrase_cells.csv"
OUT_SUM = ROOT / "results/tables/v_c_paraphrase_summary.csv"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outcome", default="o1", choices=["o1", "o2"])
    args = ap.parse_args()

    raw = S.load_raw()
    # D097: the reporting tier is DERIVED from the rows, in the one place
    # that derives it. This used to be the hard-coded literal
    # "PROVISIONAL__unverified_ai_drafted", which was both a declared tier
    # (forbidden by D091) and the superseded pre-D091 vocabulary, so this
    # validity check disclaimed itself while the result it validates was
    # reported at tier 1.
    _VSTATUS, _VTIER, _ = S.derive_verification_status(raw)
    targets = S.load_target_options()
    rows = S.outcome_rows(raw, args.outcome, targets)
    deltas = S.all_contrasts(rows)
    if deltas.empty:
        raise SystemExit("no contrasts built")

    matched = S.load_matched_floors()
    opt_n = S.option_counts(raw)
    deltas["group"] = deltas["vignette_id"].str.extract(r"^G(\d)")[0].astype(int)

    # A cell is one vignette x contrast x SPCU for one model. Within a cell the
    # ONLY thing that varies is the paraphrase, which is exactly the comparison
    # wanted. SPCU is held inside the cell rather than averaged over, because
    # averaging it would mix a genuine SPCU effect into apparent paraphrase
    # noise.
    keys = ["model_id", "revision", "vignette_id", "group", "contrast", "spcu", "cue"]
    cells = []
    for k, g in deltas.groupby(keys, dropna=False):
        vals = g["delta"].to_numpy()
        if len(vals) < 2:
            continue
        m = float(vals.mean())
        same = int(np.sum(np.sign(vals) == np.sign(m))) if m != 0 else 0
        sd = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
        rec = dict(zip(keys, k))
        floor = S.floor_for(matched, rec["model_id"], rec["revision"],
                            {opt_n.get(rec["vignette_id"])} - {None})
        rec.update({
            "n_paraphrases": len(vals),
            "deltas": "; ".join(f"{v:+.5f}" for v in vals),
            "mean_delta": m, "sd_across_paraphrase": sd,
            "n_same_sign": same, "unanimous": same == len(vals),
            "swamped_by_wording": sd > abs(m),
            "floor": floor,
            "clears_floor": (abs(m) > floor) if floor else None,
            "verification_status": _VSTATUS,
        })
        cells.append(rec)

    cd = pd.DataFrame(cells)
    OUT_CELL.parent.mkdir(parents=True, exist_ok=True)
    write_table(cd, OUT_CELL)

    print(f"\n=== Validation C: paraphrase stability, outcome={args.outcome} ===")
    print(f"wrote {OUT_CELL.relative_to(ROOT)}  ({len(cd)} cells)\n")

    print(f"Across all {len(cd)} cells:")
    print(f"  unanimous in sign          {cd.unanimous.mean():6.1%}")
    print(f"  wording swamps the effect  {cd.swamped_by_wording.mean():6.1%}  "
          f"(sd across paraphrase > |mean delta|)")

    fc = cd[cd.clears_floor == True]  # noqa: E712
    print(f"\nOf the {len(fc)} cells that CLEAR THEIR FLOOR -- the reportable ones:")
    if len(fc):
        print(f"  unanimous in sign          {fc.unanimous.mean():6.1%}")
        print(f"  wording swamps the effect  {fc.swamped_by_wording.mean():6.1%}")
        print(f"  => {int((~fc.unanimous).sum())} floor-clearing effects are NOT "
              f"unanimous across paraphrases\n     and must not be reported as "
              f"robust without that caveat.")

    # Per model x group summary, which is the table for the paper.
    rowsum = []
    for (mid, grp), g in cd.groupby(["model_id", "group"]):
        f = g[g.clears_floor == True]  # noqa: E712
        rowsum.append({
            "model_id": mid, "group": grp, "n_cells": len(g),
            "pct_unanimous": g.unanimous.mean(),
            "pct_swamped": g.swamped_by_wording.mean(),
            "n_clears_floor": len(f),
            "pct_unanimous_given_clears": f.unanimous.mean() if len(f) else None,
            "median_sd_across_paraphrase": g.sd_across_paraphrase.median(),
            "verification_status": _VSTATUS,
        })
    sd_ = pd.DataFrame(rowsum).sort_values(["group", "model_id"])
    write_table(sd_, OUT_SUM)

    print(f"\nPer model, Group 3 (the bias test):")
    g3 = sd_[sd_.group == 3]
    print(f"  {'model':40s} {'unanim':>7s} {'swamped':>8s} {'clears':>7s} "
          f"{'unanim|clears':>14s}")
    for _, r in g3.iterrows():
        uc = r.pct_unanimous_given_clears
        print(f"  {r.model_id:40s} {r.pct_unanimous:7.1%} {r.pct_swamped:8.1%} "
              f"{r.n_clears_floor:7d} "
              + (f"{uc:14.1%}" if uc is not None and not pd.isna(uc)
                 else f"{'n/a':>14s}"))

    print(f"\nwrote {OUT_SUM.relative_to(ROOT)}")
    print("\nHEADLINE for the paper: of every effect large enough to clear its own\n"
          "noise floor, the fraction that keeps its sign under all three\n"
          "paraphrasings. An audit that does not report this number is reporting\n"
          "wording sensitivity as bias.")


if __name__ == "__main__":
    main()
