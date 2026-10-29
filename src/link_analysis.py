"""RQ4 / H4 — does corpus skew predict the direction and size of output gaps?

This is the module the whole thesis turns on. RQ2 and RQ3 can only show that
models differ by gender; RQ1 can only show that corpora are skewed. H4 is the
claim that joins them, and it is the reason the project uses Pythia and OLMo 2
rather than whatever model is most capable.

The prediction, from `docs/preregistration.md` §4:

    sign(Delta on O2) = sign(centred corpus skew of that vignette's target
    concept), and the two correlate positively (Spearman rho > 0, one-sided).

Four things here are decisions, not mechanics, and each is defended in place:

1.  O2, NOT O1. Concordance flips sign with how a question is posed -- for
    G4-01 and G4-03 the guideline-correct answer is "No", so a model that
    endorses the target action MORE scores LOWER on O1. Endorsement does not
    flip. Running H4 on O1 would scramble the sign on exactly those items.

2.  MATCHED PAIRS ONLY, AND MATCHED CORPUS. The claim is that a model inherits
    ITS OWN training corpus's skew, so Pile skew is tested against Pythia and
    OLMo-mix skew against OLMo 2. The cross-pairings are run too, as a negative
    control: if Pile skew predicts OLMo 2's gaps just as well, the mechanism is
    not inheritance but something both corpora share, and H4's interpretation
    collapses even if its correlation holds.

3.  UNDERPOWERED CONCEPTS ARE DROPPED, NOT DOWNWEIGHTED. RQ1 flags concepts
    whose smaller arm has under 100 occurrences. At counts of 4 against 10 the
    skew estimate is noise with a sign, and a Spearman correlation cannot tell
    noise from signal -- it only sees the ranking. Including them would let
    sampling error generate or destroy the linkage result.

4.  SKEW IS CENTRED BEFORE USE. Health text is globally female-skewed in both
    corpora, so raw per-concept skew carries a constant offset that is a
    property of the whole corpus, not of the concept. H4 is a claim about
    RELATIVE skew between concepts, so the offset is removed per
    (corpus, method) family before any test. Reported both ways, because the
    centring constant is itself a finding about the corpora.

Outputs
  results/tables/rq4_linkage.csv          one row per (model, corpus) pairing
  results/tables/rq4_concept_level.csv    the per-vignette join, for the figure
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import stats as sps

from src.stats import (PRIMARY_SCORE_KEY, all_contrasts, load_raw,
                       outcome_rows, load_target_options)

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results/tables"
TERMS = ROOT / "configs/terms.yaml"

# skew_log2 = log2(rate_female / rate_male), so POSITIVE means female-skewed.
# Delta = outcome(woman) - outcome(man). H4 therefore predicts a POSITIVE
# correlation, and the sign convention must not be flipped anywhere below.
SKEW_COL = "skew_log2"

# RQ1's own power flag: the smaller arm needs >= 100 occurrences.
POWER_COL = "powered"


# --------------------------------------------------------------------------- #

def load_skew() -> pd.DataFrame:
    """Per-concept corpus skew, from the RQ1 tables.

    The diagnosis family is used for the primary join because its concepts are
    the vignette conditions themselves. The decision family is loaded too and
    reported separately: it is closer to what RQ2 actually scores (decisions,
    not diagnoses), which is why D026 added it, but it has far fewer concepts.
    """
    frames = []
    for name in ("rq1_corpus_skew.csv", "rq1_corpus_skew_decision.csv",
                 "rq1_corpus_skew_explicit.csv"):
        f = TABLES / name
        if f.exists():
            d = pd.read_csv(f)
            d["source_table"] = name
            frames.append(d)
    if not frames:
        sys.exit(f"no RQ1 skew tables in {TABLES}. Run src.corpus_counts first.")
    return pd.concat(frames, ignore_index=True)


def primary_concepts() -> dict[str, list[str]]:
    """vignette_id -> its health concepts, in the order terms.yaml lists them.

    Order matters: the first entry is the vignette's condition as a bare term
    ("pneumonia", "ADHD"), and the later ones are elaborations or treatments.
    The primary concept is the FIRST one that RQ1 found adequately powered, so
    the choice is made by data availability rather than by picking whichever
    concept gives the nicer correlation.
    """
    terms = yaml.safe_load(TERMS.read_text())
    return {k: list(v) for k, v in terms["health_concepts"].items()}


def centre(d: pd.DataFrame) -> pd.DataFrame:
    """Subtract the mean skew within each (corpus index, method) family."""
    d = d.copy()
    d["skew_centred"] = d.groupby(["index", "method"])[SKEW_COL].transform(
        lambda s: s - s.mean())
    return d


def pick_primary(skew: pd.DataFrame, concepts: dict[str, list[str]]) -> pd.DataFrame:
    """One skew value per (corpus, vignette): the first powered concept."""
    rows = []
    for (idx, method), g in skew.groupby(["index", "method"]):
        by_concept = {str(r.concept): r for r in g.itertuples(index=False)}
        for vid, clist in concepts.items():
            chosen = None
            for c in clist:
                r = by_concept.get(c)
                if r is not None and bool(getattr(r, POWER_COL)):
                    chosen = r
                    break
            if chosen is None:
                # Recorded rather than dropped silently: which vignettes have no
                # usable corpus measurement is a result about the corpora, and it
                # decides how many points H4 is actually tested on.
                rows.append({"index": idx, "method": method, "vignette_id": vid,
                             "concept": None, "skew_log2": np.nan,
                             "skew_centred": np.nan, "powered": False,
                             "reason": "no powered concept for this vignette"})
                continue
            rows.append({"index": idx, "method": method, "vignette_id": vid,
                         "concept": str(chosen.concept),
                         "skew_log2": float(getattr(chosen, SKEW_COL)),
                         "skew_centred": float(chosen.skew_centred),
                         "powered": True, "reason": ""})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #

def o2_by_vignette(raw: pd.DataFrame) -> pd.DataFrame:
    """Mean Delta on O2 per (model, vignette), woman - man.

    Averaged over paraphrase, SPCU and cue within a vignette, because H4 is a
    per-concept claim and the concept is a property of the vignette. The spread
    across those cells is kept as sd so the figure can show it.
    """
    targets = load_target_options()
    d = outcome_rows(raw, "o2", targets)
    if d.empty:
        sys.exit("O2 is not computable: no target_option in templates.yaml "
                 "(see docs/decisions.md D037).")
    dl = all_contrasts(d)
    dl = dl[dl["contrast"] == "woman_minus_man"]
    out = (dl.groupby(["model_id", "revision", "vignette_id"])["delta"]
             .agg(["mean", "std", "count"]).reset_index()
             .rename(columns={"mean": "delta_o2", "std": "delta_sd",
                              "count": "n_pairs"}))
    # corpus_index is a property of the model, not of the pair, so it is not a
    # pair key and the pivot in all_contrasts() drops it. Reattached here from
    # the raw rows: without it there is no way to tell a matched pairing from a
    # crossed one, and the matched/crossed contrast is the whole inheritance
    # claim. Asserted one-to-one, because a model mapped to two corpus indexes
    # would silently duplicate every vignette row.
    cmap = (raw[["model_id", "revision", "corpus_index"]]
            .drop_duplicates().reset_index(drop=True))
    dup = cmap.duplicated(subset=["model_id", "revision"]).sum()
    if dup:
        raise RuntimeError(f"{dup} model(s) carry more than one corpus_index; "
                           f"cannot assign matched/crossed pairing")
    out = out.merge(cmap, on=["model_id", "revision"], how="left")
    # A model with no declared corpus (the --smoke config, and the RQ5 contrast
    # model, which has none by design) must not vanish: pandas drops null
    # groups by default, which would silently empty the whole analysis. Marked
    # explicitly so its pairing reads "unknown" rather than being absent.
    out["corpus_index"] = out["corpus_index"].fillna("(none declared)")
    return out


def spearman_one_sided(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
    """Spearman rho with a one-sided p for rho > 0.

    scipy's one-sided alternatives exist, but the degenerate cases must be
    handled here: fewer than 4 points, or no variance in either variable, give
    no testable correlation and must return NaN rather than a p-value that
    looks like evidence.
    """
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if x.size < 4 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan"), float("nan"), int(x.size)
    r = sps.spearmanr(x, y, alternative="greater")
    return float(r.statistic), float(r.pvalue), int(x.size)


def sign_concordance(x: np.ndarray, y: np.ndarray) -> dict:
    """How often sign(Delta) matches sign(skew), with an exact binomial test.

    The correlation and the sign test answer different questions, and H4 states
    both. A correlation can be driven by a couple of extreme concepts while most
    signs disagree; matching signs can hold while magnitudes are unrelated.
    Zeros are excluded rather than counted as agreement.
    """
    m = np.isfinite(x) & np.isfinite(y) & (x != 0) & (y != 0)
    x, y = x[m], y[m]
    if x.size == 0:
        return {"n_signed": 0, "n_concordant": 0, "prop_concordant": float("nan"),
                "p_binom_one_sided": float("nan")}
    agree = int(np.sum(np.sign(x) == np.sign(y)))
    p = float(sps.binomtest(agree, x.size, 0.5, alternative="greater").pvalue)
    return {"n_signed": int(x.size), "n_concordant": agree,
            "prop_concordant": agree / x.size, "p_binom_one_sided": p}


# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", default="exact_phrase:diagnosis",
                    help="RQ1 method family for the primary join")
    args = ap.parse_args()

    TABLES.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    if "corpus_index" not in raw.columns:
        sys.exit("scored results carry no corpus_index; rerun src.score_outputs")

    skew = centre(load_skew())
    prim = pick_primary(skew, primary_concepts())
    prim = prim[prim["method"] == args.method]
    if prim.empty:
        sys.exit(f"no RQ1 rows for method {args.method!r}. "
                 f"Available: {sorted(skew['method'].unique())}")

    o2 = o2_by_vignette(raw)
    indexes = sorted(prim["index"].unique())

    # COMMON SUPPORT. A concept can be adequately powered in one corpus and not
    # the other, so the Pile join and the OLMo-mix join cover different vignette
    # sets. Comparing matched against crossed rho across different sets is not a
    # negative control -- the two numbers would differ because the items differ,
    # not because inheritance does or does not hold. The matched/crossed
    # contrast is therefore computed on the INTERSECTION, and the per-corpus
    # numbers on all available vignettes are reported beside it. Both are kept:
    # restricting costs power, so the wider join is the better estimate of each
    # correlation and the narrower one is the only valid comparison between them.
    powered = prim[prim["powered"]]
    per_corpus = {i: set(powered[powered["index"] == i]["vignette_id"])
                  for i in indexes}
    common = set.intersection(*per_corpus.values()) if per_corpus else set()
    print(f"powered vignettes per corpus: "
          f"{ {i: len(v) for i, v in per_corpus.items()} }; "
          f"common support: {len(common)}")
    if len(common) < 4:
        print("  WARNING: common support is below 4 vignettes, so the "
              "matched-vs-crossed comparison is not interpretable. Report the "
              "per-corpus correlations and say the control could not be run.")

    joined, rows = [], []
    for (mid, rev, own_idx), g in o2.groupby(["model_id", "revision",
                                              "corpus_index"]):
        for idx in indexes:
            s = prim[prim["index"] == idx][["vignette_id", "concept",
                                            "skew_log2", "skew_centred"]]
            j = g.merge(s, on="vignette_id", how="inner")
            j["skew_index"] = idx
            # "matched" = the model's own training corpus. The whole inheritance
            # claim lives in the contrast between matched and crossed.
            j["pairing"] = ("unknown" if own_idx == "(none declared)"
                            else "matched" if idx == own_idx else "crossed")
            joined.append(j)

            for support, jj in (("all_powered", j),
                                ("common", j[j["vignette_id"].isin(common)])):
                for label, col in (("centred", "skew_centred"),
                                   ("raw", "skew_log2")):
                    rho, p, n = spearman_one_sided(jj[col].to_numpy(),
                                                   jj["delta_o2"].to_numpy())
                    sc = sign_concordance(jj[col].to_numpy(),
                                          jj["delta_o2"].to_numpy())
                    rows.append({"model_id": mid, "revision": rev,
                                 "model_corpus": own_idx, "skew_index": idx,
                                 "pairing": (j["pairing"].iloc[0]
                                             if len(j) else ""),
                                 "support": support, "skew_variant": label,
                                 "n_vignettes": n, "spearman_rho": rho,
                                 "p_one_sided": p, **sc})

    link = pd.DataFrame(rows)
    if link.empty:
        sys.exit("no (model x corpus) cells to test. Either no models are "
                 "scored or no vignette has a powered concept.")
    cj = pd.concat(joined, ignore_index=True) if joined else pd.DataFrame()
    link.to_csv(TABLES / "rq4_linkage.csv", index=False)
    cj.to_csv(TABLES / "rq4_concept_level.csv", index=False)

    n_unpowered = int((~prim["powered"]).sum())
    print(f"\nskew method: {args.method}")
    print(f"vignettes with no adequately powered concept: {n_unpowered} "
          f"of {len(prim)} (corpus x vignette cells)")
    print("\n--- RQ4 linkage (O2, woman - man) ---")
    cols = ["model_id", "pairing", "skew_index", "support", "skew_variant",
            "n_vignettes", "spearman_rho", "p_one_sided", "n_concordant",
            "n_signed", "p_binom_one_sided"]
    print(link[cols].to_string(index=False))
    print("\nH4 is supported only where the MATCHED pairing shows rho > 0 and "
          "the crossed pairing is weaker ON THE COMMON SUPPORT rows. A matched "
          "result alone does not establish inheritance, and a matched-crossed "
          "difference computed across different vignette sets establishes "
          "nothing at all.")
    print(f"\nwrote {TABLES/'rq4_linkage.csv'}")
    print(f"wrote {TABLES/'rq4_concept_level.csv'}")


if __name__ == "__main__":
    main()
