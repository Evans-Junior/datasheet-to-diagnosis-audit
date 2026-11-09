"""I4: is the RQ4 corpus-provenance claim identifiable at all?

The RQ4 negative control fires: Qwen3-8B, trained on neither corpus, correlates
at rho +0.700 with the Pile and +0.758 with olmo-mix, while matched pairings are
weak. Before trying to repair the estimator, test whether the two corpora differ
enough on the audited concepts for provenance to be recoverable even in
principle.

Pass criterion for "RQ4 is identifiable", fixed before running (tuning log I4):
at least 6 concepts on common support with |corpus disagreement| > 0.5 log2.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
THRESHOLD, MIN_CONCEPTS = 0.5, 6

d = pd.read_csv(ROOT / "results/tables/rq4_concept_level.csv")
s = d.groupby(["concept", "skew_index"])["skew_log2"].mean().unstack()
s.columns = [c.replace("v4_", "").replace("_llama", "") for c in s.columns]
a, b = s.columns[0], s.columns[1]

s["disagreement"] = s[a] - s[b]
s["common_support"] = s[[a, b]].notna().all(axis=1)
s = s.reindex(s["disagreement"].abs().sort_values(ascending=False,
                                                 na_position="last").index)
s.to_csv(ROOT / "results/tables/i4_corpus_disagreement.csv")

common = s[s["common_support"]]
n_big = int((common["disagreement"].abs() > THRESHOLD).sum())
rho = common[a].corr(common[b], method="spearman")

print(s.round(3).to_string())
print(f"\nconcepts audited:            {len(s)}")
print(f"on common support:           {len(common)}")
print(f"olmo-mix only:               {int(s[a].notna().sum() - len(common))}")
print(f"pile only:                   {int(s[b].notna().sum() - len(common))}")
print(f"\nSpearman between corpora (common support): {rho:.3f}")
print(f"Pearson:                                   "
      f"{common[a].corr(common[b]):.3f}")
print(f"median |disagreement|:                     "
      f"{common['disagreement'].abs().median():.3f} log2")
print(f"max |disagreement|:                        "
      f"{common['disagreement'].abs().max():.3f} log2")
for t in (0.25, 0.5, 1.0):
    print(f"  concepts with |disagreement| > {t}: "
          f"{int((common['disagreement'].abs() > t).sum())}")
print(f"\ncriterion: >={MIN_CONCEPTS} concepts above {THRESHOLD} log2 "
      f"-> got {n_big} -> "
      f"{'IDENTIFIABLE' if n_big >= MIN_CONCEPTS else 'NOT IDENTIFIABLE'}")
