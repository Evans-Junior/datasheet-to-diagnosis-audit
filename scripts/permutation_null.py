"""Validation B: permutation nulls for the aggregate statistics (D060).

WHY THIS EXISTS
---------------
Every confirmatory number in this project is currently judged two ways: against
the Group 4 nuisance floor (a MEASUREMENT question -- can the instrument resolve
an effect this size?) and against a cluster bootstrap (a SAMPLING question --
would it reappear with other vignettes?). Both are necessary. Neither is
assumption-free:

  * the floor is measured on PROXY stimuli (Group 4) and then applied to the
    target stimuli (Groups 1 and 3). The matching is argued, not proved.
  * the bootstrap approximates the sampling distribution by resampling; with
    k = 5 vignettes that approximation is crude.

A permutation null needs neither. Under the null that the arm label carries no
information, the label assignment within a matched pair is arbitrary, so the
SIGN of each vignette-level delta is exchangeable. Enumerating all 2^k sign
vectors gives the EXACT null distribution of the test statistic on the actual
target stimuli, with the actual option geometry, and with no proxy and no
resampling approximation.

WHAT IT ADDS OVER `cluster_signflip_p` IN src/stats.py
------------------------------------------------------
That function returns a p-value. This one returns the whole null DISTRIBUTION,
which buys three things a p-value does not:

 1. A `perm_floor`: the 95th percentile of |T| under the null, in the same
    probability units as the Group 4 floor. That is a second, independent
    estimate of "how big can a gap be for no reason", derived from the target
    vignettes themselves rather than from Group 4. Agreement between the two is
    convergent validity for the floor; disagreement is a finding.
 2. An exact p where 2^k is enumerable, so no Monte Carlo error at all.
 3. A permutation test for the RQ3 size trend, which is the result flagged as
    least trustworthy (D045, D052). Permuting the size labels across models
    gives an assumption-free null for Spearman rho, replacing a parametric
    p-value computed on 10 non-independent points.

WHAT IT DOES NOT DO
-------------------
The permutation floor and the Group 4 floor are NOT the same quantity and must
not be swapped for one another:

    Group 4 floor   per-VIGNETTE |delta| on an inert item.  Measurement
                    resolution of a single item.
    perm_floor      spread of the MEAN-over-vignettes statistic under label
                    exchange. Aggregate sampling variability.

The second is the smaller number by construction when k > 1, because averaging
k vignettes shrinks the spread by roughly sqrt(k). So perm_floor < floor is the
EXPECTED result and is not evidence that the Group 4 floor is inflated. What
would be informative is perm_floor > floor, which would mean between-vignette
variability alone can manufacture an effect larger than the per-item resolution
limit -- i.e. that the floor comparison is too lenient at the aggregate level.
That comparison is reported as `ratio_perm_over_floor` and interpreted only in
that direction.

Usage:
    .venv/bin/python scripts/permutation_null.py
    .venv/bin/python scripts/permutation_null.py --n-mc 100000
"""

from __future__ import annotations

import argparse
import itertools
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

OUT_CONTRAST = ROOT / "results/tables/v_b_permutation_contrasts.csv"
OUT_TREND = ROOT / "results/tables/v_b_permutation_size_trend.csv"

# Enumerate exactly below this many clusters; Monte Carlo above it.
EXACT_MAX_K = 20


def signflip_null(d: np.ndarray, n_mc: int, rng: np.random.Generator
                  ) -> tuple[np.ndarray, bool]:
    """Null distribution of mean(d) under sign exchange.

    Exact enumeration of all 2^k sign vectors when k is small, which is the
    usual case here (k = 5 for H1's and H3's Group 3 sets). Returns the null
    sample and whether it is exact.
    """
    k = len(d)
    if k <= EXACT_MAX_K:
        signs = np.array(list(itertools.product([-1, 1], repeat=k)))
        return (signs * d).mean(axis=1), True
    signs = rng.choice([-1.0, 1.0], size=(n_mc, k))
    return (signs * d).mean(axis=1), False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-mc", type=int, default=50_000,
                    help="Monte Carlo draws when exact enumeration is too large")
    ap.add_argument("--outcome", default="o1", choices=["o1", "o2"])
    args = ap.parse_args()
    rng = np.random.default_rng(20261107)

    raw = S.load_raw()
    targets = S.load_target_options()
    rows = S.outcome_rows(raw, args.outcome, targets)
    deltas = S.all_contrasts(rows)
    if deltas.empty:
        raise SystemExit("no contrasts built; nothing to permute")

    matched = S.load_matched_floors()
    opt_n = S.option_counts(raw)

    # Group membership, so a contrast can be restricted to the vignettes a
    # hypothesis is actually stated on rather than pooled across groups with
    # different predictions.
    deltas["group"] = deltas["vignette_id"].str.extract(r"^G(\d)")[0].astype(int)

    out = []
    for (mid, rev, grp, contrast), g in deltas.groupby(
            ["model_id", "revision", "group", "contrast"]):
        # THE UNIT IS THE VIGNETTE. Average paraphrases and SPCU levels within a
        # vignette first; permuting prompt-level rows would treat three
        # paraphrases of one vignette as three independent sign draws and
        # understate the null by sqrt(3). This is D036 applied to permutation.
        per_vig = g.groupby("vignette_id")["delta"].mean()
        d = per_vig.to_numpy()
        k = len(d)
        if k < 2:
            continue

        T = float(d.mean())
        null, exact = signflip_null(d, args.n_mc, rng)

        # Two-sided exact p. The +1 is NOT a continuity fudge: the observed sign
        # vector is itself one of the enumerated permutations, so excluding it
        # would make p=0 attainable, which is never honest. Under exact
        # enumeration the identity permutation is already in `null`, so no
        # correction is applied there.
        if exact:
            p = float((np.abs(null) >= abs(T) - 1e-15).mean())
        else:
            p = float((np.sum(np.abs(null) >= abs(T)) + 1) / (len(null) + 1))

        perm_floor = float(np.quantile(np.abs(null), 0.95))
        floor = S.floor_for(matched, mid, rev,
                            {opt_n[v] for v in per_vig.index if v in opt_n})

        out.append({
            "model_id": mid, "revision": rev, "score_key": S.PRIMARY_SCORE_KEY,
            "outcome": args.outcome, "group": grp, "contrast": contrast,
            "n_vignettes": k, "mean_delta": T,
            "p_permutation": p, "exact": exact,
            "n_null": len(null),
            # Resolution limit of the test: with k clusters no two-sided p below
            # 2/2^k exists, so a p at that value means "as extreme as possible",
            # not "highly significant" (D044).
            "p_resolution_limit": 2.0 / (2 ** k) if exact else 1.0 / len(null),
            "perm_floor_q95": perm_floor,
            "group4_floor": floor,
            "ratio_perm_over_floor": (perm_floor / floor) if floor else None,
            "exceeds_group4_floor": (abs(T) > floor) if floor else None,
            "exceeds_perm_floor": abs(T) > perm_floor,
            "verification_status": "PROVISIONAL__unverified_ai_drafted",
        })

    df = pd.DataFrame(out).sort_values(
        ["group", "contrast", "model_id"]).reset_index(drop=True)
    OUT_CONTRAST.parent.mkdir(parents=True, exist_ok=True)
    write_table(df, OUT_CONTRAST)

    print(f"\n=== Validation B: permutation nulls, outcome={args.outcome}, "
          f"score_key={S.PRIMARY_SCORE_KEY} ===")
    print(f"wrote {OUT_CONTRAST.relative_to(ROOT)}  ({len(df)} rows)\n")

    g3 = df[(df.group == 3) & (df.contrast == "woman_minus_man")]
    if not g3.empty:
        print("Group 3, woman minus man:")
        print(f"  {'model':40s} {'k':>2s} {'mean_d':>9s} {'perm_p':>8s} "
              f"{'perm_q95':>9s} {'G4_floor':>9s} {'ratio':>6s}")
        for _, r in g3.iterrows():
            fl = r.group4_floor
            print(f"  {r.model_id:40s} {r.n_vignettes:2d} {r.mean_delta:+9.5f} "
                  f"{r.p_permutation:8.4f} {r.perm_floor_q95:9.5f} "
                  + (f"{fl:9.5f}" if fl else f"{'n/a':>9s}")
                  + (f" {r.ratio_perm_over_floor:6.2f}" if fl else f" {'n/a':>6s}"))

    both = df[df.group4_floor.notna()]
    if not both.empty:
        n_lenient = int((both.perm_floor_q95 > both.group4_floor).sum())
        print(f"\nConvergent-validity check across {len(both)} model x contrast "
              f"x group cells:")
        print(f"  perm_floor > Group 4 floor in {n_lenient}/{len(both)} cells "
              f"(median ratio {both.ratio_perm_over_floor.median():.3f})")
        if n_lenient == 0:
            print("  => In no cell does between-vignette variability alone exceed the\n"
                  "     per-item resolution limit. The Group 4 floor is the BINDING\n"
                  "     constraint everywhere, which is the conservative direction and\n"
                  "     means no reported effect rests on aggregation.")
        else:
            print("  => WARNING: in these cells the floor comparison is TOO LENIENT at\n"
                  "     the aggregate level. Report the larger of the two thresholds.")

    disagree = df[(df.exceeds_group4_floor.notna())
                  & (df.exceeds_group4_floor != df.exceeds_perm_floor)]
    print(f"\nVerdict disagreements between the two thresholds: {len(disagree)}")
    if not disagree.empty:
        for _, r in disagree.iterrows():
            print(f"  {r.model_id} g{r.group} {r.contrast}: "
                  f"G4={'pass' if r.exceeds_group4_floor else 'fail'} "
                  f"perm={'pass' if r.exceeds_perm_floor else 'fail'}")

    # ---------------------------------------------------------------- #
    # RQ3 size trend, permutation null on the size labels.
    # ---------------------------------------------------------------- #
    print("\n=== RQ3 size trend, permutation null on size labels ===")
    trend_rows = []
    for (grp, contrast), g in df.groupby(["group", "contrast"]):
        g = g[g.group4_floor.notna()].copy()
        # One family only. Pythia and OLMo are separate replications and are
        # never pooled as a single size series (prereg §7).
        g = g[g.model_id.str.startswith("EleutherAI/pythia")]
        if len(g) < 4:
            continue
        g["n_params"] = g.model_id.map(S.n_params)
        g = g[g.n_params.notna()]
        if len(g) < 4:
            continue
        g["rel_gap"] = g.mean_delta.abs() - g.group4_floor

        from scipy import stats as sps
        rho_obs = sps.spearmanr(g.n_params, g.rel_gap).statistic
        sizes = g.n_params.to_numpy()
        vals = g.rel_gap.to_numpy()
        null = np.empty(args.n_mc)
        for i in range(args.n_mc):
            null[i] = sps.spearmanr(rng.permutation(sizes), vals).statistic
        p_perm = float((np.sum(np.abs(null) >= abs(rho_obs)) + 1) / (args.n_mc + 1))
        p_param = sps.spearmanr(g.n_params, g.rel_gap).pvalue

        trend_rows.append({
            "group": grp, "contrast": contrast, "family": "pythia",
            "n_models": len(g), "rho": rho_obs,
            "p_parametric": p_param, "p_permutation": p_perm,
            "n_mc": args.n_mc,
            "verification_status": "PROVISIONAL__unverified_ai_drafted",
        })
        print(f"  g{grp} {contrast:24s} n={len(g)} rho={rho_obs:+.3f} "
              f"p_param={p_param:.4f}  p_perm={p_perm:.4f}")

    if trend_rows:
        td = pd.DataFrame(trend_rows)
        write_table(td, OUT_TREND)
        print(f"\nwrote {OUT_TREND.relative_to(ROOT)}")
        print("\nNOTE: with n=5-7 models the permutation null for Spearman rho is\n"
              "coarse -- rho takes only a few distinct values. A p_permutation that\n"
              "is much larger than p_parametric means the parametric p was relying\n"
              "on an asymptotic approximation that does not hold at this n.")
    else:
        print("  (no size series with >=4 models and a floor; nothing to test)")


if __name__ == "__main__":
    main()
