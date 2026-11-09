"""I5: H3's equivalence margin is circular under the matched floor.

D052 moved the nuisance floor onto Group 4. H3's preregistered vignette set is
["G1-01".."G1-05", "G4-01", "G4-02", "G4-03"], so three of its eight vignettes
are now the same data the margin is derived from, and the test is partly
compared against itself. The legacy floor did not have this problem because it
was measured on separate synthetic frames, so the defect is one D052 introduced.

Group 4's documented purpose (data/vignettes/templates.yaml) is to "establish
the model's background variance so a Group 1/3 gap can be distinguished from
prompt-sensitivity noise (D002)". That is the floor's job. Carrying the same
items into H3 as test material was double duty from the start.

Reports three variants side by side. The preregistered definition is NOT
replaced: redefining a preregistered hypothesis after seeing its result is the
thing the preregistration exists to prevent.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import src.stats as S  # noqa: E402

deltas = pd.read_csv(ROOT / "results/tables/rq2_deltas.csv")
d = deltas[deltas["outcome"] == "o1"]
matched = S.load_matched_floors()
legacy = S.load_floors()
raw = pd.read_parquet(next((ROOT / "results/raw").glob("*.parquet")))
nopt = S.option_counts(pd.concat(
    [pd.read_parquet(f) for f in (ROOT / "results/raw").glob("*.parquet")],
    ignore_index=True))

PRE = ["G1-01", "G1-02", "G1-03", "G1-04", "G1-05", "G4-01", "G4-02", "G4-03"]
G1 = PRE[:5]


def margin(vigs, src):
    strata = {nopt[v] for v in vigs if v in nopt}
    if src == "legacy":
        return max(legacy.values())
    per = [S.floor_for(matched, m, r, strata)
           for (m, r, n) in {(m, r, n) for (m, r, n) in matched}]
    return max(f for f in per if f is not None)


def run(label, vigs, src, circular):
    sub = d[d["vignette_id"].isin(vigs)]
    spec = {"vignettes": vigs, "outcome": "o1", "alternative": "two-sided"}
    f = margin(vigs, src)
    r = S.test_family(sub, spec, floor=f)
    print(f"{label:46s} n_vig={r['n_vignettes']:>2}  "
          f"delta={r['mean_delta']:+.6f}  "
          f"CI[{r['ci_lo']:+.6f},{r['ci_hi']:+.6f}]  "
          f"margin={f:.4f} ({f/abs(r['mean_delta']):.1f}x)  "
          f"TOST={str(r['tost_supported']):5s}  "
          f"{'CIRCULAR' if circular else 'clean'}")


print("H3: 'no systematic gap where the corpus is unskewed'\n")
run("preregistered (G1+G4), matched floor", PRE, "matched", True)
run("preregistered (G1+G4), legacy floor", PRE, "legacy", False)
run("Group 1 only (G1-01..05), matched floor", G1, "matched", False)
print("\nThe third row is the non-circular test of the same claim on the "
      "matched floor.\nThe second is non-circular but uses the inflated "
      "wrong-geometry floor D052 corrects.")
