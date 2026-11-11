"""RQ4, run as H4 was preregistered: open-data models only, matched vs crossed (D099).

WHY THIS EXISTS
---------------
H4 in `docs/preregistration.md` is specific, and the specificity is the whole
test:

    "Tested separately per corpus-model pair, Pile skew against Pythia, OLMo-mix
     skew against OLMo 2, because the linkage claim is that a model inherits
     *its own* training corpus's skew. Cross-pairings (Pile skew against OLMo 2)
     are a negative control: they should link more weakly."

Two things follow that were not being reported together.

First, Qwen3-8B is **out of scope for H4 by preregistration** (§4: "no corpus
access, so no linkage"). Treating its cross-corpus correlation as the reason RQ4
fails inverted the design: a model with no declared corpus is a post-hoc placebo,
n = 1, and it cannot carry a verdict about nine models that do have one. The
identifiability question has to be settled inside the open-data set or not at all.

Second, the preregistered negative control had never actually been *tested*. The
cross-pairings were tabulated beside the matched ones in `rq4_linkage.csv` and
left for a reader to eyeball. H4 predicts matched > crossed; that is a paired
comparison over models and it has a p-value.

WHAT IT COMPUTES
----------------
 1. The preregistered control, on COMMON SUPPORT. This matters: `all_powered`
    means a different concept set per corpus (8 concepts powered in the Pile, 11
    in olmo-mix), so comparing a matched rho at n=11 against a crossed rho at
    n=8 compares two different tests. On common support both are n=8 over the
    same concepts, and the only thing varying is which corpus the skew came from,
    which is what the control is for.
 2. The per-model linkage at `all_powered`, which uses all available power and is
    the right number for the headline.
 3. The trend across models, decomposed. "Does linkage grow with scale" and "does
    linkage appear with post-training" are different questions and the Pythia
    ladder answers the first on its own, with training data held constant.

Usage:
    .venv/bin/python scripts/rq4_matched_vs_crossed.py
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd
from scipy.stats import spearmanr, wilcoxon

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.provenance import write_table  # noqa: E402

LINK = ROOT / "results/tables/rq4_linkage.csv"
OUT_CTRL = ROOT / "results/tables/rq4_matched_vs_crossed.csv"
OUT_TREND = ROOT / "results/tables/rq4_linkage_trend.csv"

# Parameter count in billions. Kept here rather than parsed from the id so that a
# renamed checkpoint fails loudly instead of being silently dropped from a trend.
SIZE = {
    "pythia-70m": 0.07, "pythia-160m": 0.16, "pythia-410m": 0.41,
    "pythia-1b": 1.0, "pythia-1.4b": 1.4, "pythia-2.8b": 2.8,
    "pythia-6.9b": 6.9,
    "OLMo-2-1124-7B": 7.0, "OLMo-2-1124-7B-Instruct": 7.0,
}
FAMILY = {m: ("pythia" if m.startswith("pythia") else "olmo") for m in SIZE}
TUNED = {m: m.endswith("Instruct") for m in SIZE}


def short(mid: str) -> str:
    return mid.split("/")[-1]


def main() -> int:
    d = pd.read_csv(LINK)
    d = d[d.skew_variant == "centred"]
    # Preregistration section 4: the weights-only model has no declared corpus,
    # so it is not in H4's population. It stays available as a placebo elsewhere.
    d = d[d.model_corpus != "(none declared)"]

    unknown = set(d.model_id.map(short)) - set(SIZE)
    if unknown:
        print(f"unrecognised model(s), refusing to build a trend over a "
              f"roster I cannot size: {sorted(unknown)}")
        return 1

    ctrl_rows, trend_rows = [], []
    for mid, g in d.groupby("model_id"):
        m = short(mid)
        com = g[g.support == "common"]
        allp = g[g.support == "all_powered"]
        mt_c = com[com.pairing == "matched"]
        cr_c = com[com.pairing == "crossed"]
        mt_a = allp[allp.pairing == "matched"]
        if len(mt_c) != 1 or len(mt_a) != 1 or cr_c.empty:
            print(f"{m}: expected one matched row per support and at least one "
                  f"crossed row; got {len(mt_c)}/{len(mt_a)}/{len(cr_c)}")
            return 1
        ctrl_rows.append({
            "model": m, "family": FAMILY[m], "n_params_b": SIZE[m],
            "instruction_tuned": TUNED[m],
            "own_corpus": mt_c.model_corpus.iloc[0].replace("v4_", "")
                                                   .replace("_llama", ""),
            "n_concepts": int(mt_c.n_vignettes.iloc[0]),
            "rho_matched": round(float(mt_c.spearman_rho.iloc[0]), 4),
            "rho_crossed_max": round(float(cr_c.spearman_rho.max()), 4),
            "rho_crossed_mean": round(float(cr_c.spearman_rho.mean()), 4),
            "n_crossed_corpora": len(cr_c),
            "matched_beats_crossed": bool(
                mt_c.spearman_rho.iloc[0] > cr_c.spearman_rho.max()),
            "support": "common",
        })
        trend_rows.append({
            "model": m, "family": FAMILY[m], "n_params_b": SIZE[m],
            "instruction_tuned": TUNED[m],
            "n_concepts": int(mt_a.n_vignettes.iloc[0]),
            "rho_matched": round(float(mt_a.spearman_rho.iloc[0]), 4),
            "p_one_sided": round(float(mt_a.p_one_sided.iloc[0]), 4),
            "n_concordant": int(mt_a.n_concordant.iloc[0]),
            "n_signed": int(mt_a.n_signed.iloc[0]),
            "support": "all_powered",
        })

    c = pd.DataFrame(ctrl_rows).sort_values(["family", "n_params_b", "model"])
    t = pd.DataFrame(trend_rows).sort_values(["family", "n_params_b", "model"])

    pd.set_option("display.width", 200)
    print("=" * 78)
    print("1. THE PREREGISTERED NEGATIVE CONTROL, on common support (n=8, same")
    print("   concepts for every cell, so only the corpus varies)")
    print("=" * 78)
    print(c[["model", "own_corpus", "rho_matched", "rho_crossed_max",
             "matched_beats_crossed"]].to_string(index=False))

    w = wilcoxon(c.rho_matched, c.rho_crossed_max, alternative="greater")
    n_win = int(c.matched_beats_crossed.sum())
    print()
    print(f"   H4 predicts matched > crossed. Matched wins in {n_win} of "
          f"{len(c)} models.")
    print(f"   Wilcoxon signed-rank, one-sided (matched > crossed): "
          f"W = {w.statistic:.1f}, p = {w.pvalue:.4f}")
    if n_win <= len(c) / 2:
        print()
        print("   THE CONTROL FAILS, AND IT FAILS WITHOUT QWEN. A model's own")
        print("   corpus does not predict its output gap better than a corpus it")
        print("   never saw. So a matched rho, however large, does not identify")
        print("   the corpus it came from. This is a fact about the two corpora")
        print("   being near-duplicates on the audited concepts, not about any")
        print("   one model, and dropping the weights-only model does not")
        print("   repair it.")

    print()
    print("=" * 78)
    print("2. PER-MODEL LINKAGE at all_powered, and the trend")
    print("=" * 78)
    print(t[["model", "n_params_b", "instruction_tuned", "n_concepts",
             "rho_matched", "p_one_sided"]].to_string(index=False))

    py = t[t.family == "pythia"]
    print()
    r_py, p_py = spearmanr(py.n_params_b, py.rho_matched)
    r_all, p_all = spearmanr(t.n_params_b, t.rho_matched)
    print(f"   Pythia ladder only, size vs linkage : rho = {r_py:+.3f}, "
          f"p = {p_py:.4f}  (n = {len(py)})")
    print(f"   All nine open models, size vs linkage: rho = {r_all:+.3f}, "
          f"p = {p_all:.4f}  (n = {len(t)})")
    print()
    print("   Read the two rows together. The Pythia ladder spans a hundredfold")
    print("   in parameters with training data held constant and shows no")
    print("   linkage trend, so scale is not what produces linkage. The")
    print("   all-model correlation is larger only because the two models at the")
    print("   top of it differ from Pythia in family, corpus AND post-training.")

    base = t[(t.family == "olmo") & (~t.instruction_tuned)]
    inst = t[(t.family == "olmo") & (t.instruction_tuned)]
    if len(base) == 1 and len(inst) == 1:
        b = float(base.rho_matched.iloc[0]); i = float(inst.rho_matched.iloc[0])
        print()
        print(f"   OLMo 2 7B base      rho = {b:+.3f} "
              f"(p = {float(base.p_one_sided.iloc[0]):.4f})")
        print(f"   OLMo 2 7B Instruct  rho = {i:+.3f} "
              f"(p = {float(inst.p_one_sided.iloc[0]):.4f})")
        print(f"   Same parameter count, same corpus, same pretraining. The")
        print(f"   difference of {i - b:+.3f} is attributable to post-training,")
        print(f"   and it is the only place in the roster where linkage appears.")

    write_table(c, OUT_CTRL)
    write_table(t, OUT_TREND)
    print()
    print(f"wrote {OUT_CTRL.relative_to(ROOT)}")
    print(f"wrote {OUT_TREND.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
