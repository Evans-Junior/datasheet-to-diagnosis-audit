"""Confirmatory and descriptive statistics for RQ2, RQ3 and RQ4.

Everything here implements `docs/preregistration.md` §3, §4 and §7. Nothing in
this module chooses a test, a direction or a family -- those were fixed before
any score existed, and this file is deliberately a transcription of that
document rather than an analysis script with options.

Three things are easy to get wrong and are handled explicitly:

1.  THE UNIT IS THE MATCHED PAIR, NOT THE PROMPT. Delta is defined on pairs that
    share vignette, paraphrase, SPCU value, model and score key, and differ only
    in gender-identity arm (§3). Pooling prompts instead of differencing them
    throws away the matching the whole design is built on and inflates variance
    with between-vignette differences that are not the effect of interest.

2.  THE NUISANCE FLOOR IS PER MODEL AND IS NOT MONOTONIC IN SIZE (D035): 0.0207
    / 0.0626 / 0.0309 at 70m / 160m / 410m. So RQ3 cannot compare raw |Delta|
    across the ladder -- a larger model with a smaller floor would look more
    biased for a purely instrumental reason. RQ3 compares FLOOR-RELATIVE gaps,
    and a model whose floor file is missing is dropped from the trend with a
    warning rather than silently contributing an absolute gap to a
    floor-relative series.

3.  MODELS ARE NOT REPLICATES (§7). The Pythia ladder is one family at eight
    sizes. Sizes are never pooled as independent observations; size is a
    moderator. The two independent replications are Pythia and OLMo 2, and a
    confirmatory prediction counts as supported only if it holds in both.

Resampling for intervals is a CLUSTER bootstrap over vignettes, not over rows.
Rows within a vignette share clinical text and a reference answer, so they are
not independent; resampling rows would give intervals far too narrow and would
turn paraphrase count into apparent precision.

Outputs
  results/tables/rq2_deltas.csv            every matched pair difference
  results/tables/rq2_hypothesis_tests.csv  H1-H4 with Holm-adjusted p
  results/tables/rq3_size_trend.csv        floor-relative gap by model size
  results/tables/rq2_mixed_effects.csv     mixed-model estimates, where fitted
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import stats as sps
from statsmodels.stats.multitest import multipletests
from src.provenance import write_table   # D090: stamps prompt_hash


ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results/raw"
TABLES = ROOT / "results/tables"
TEMPLATES = ROOT / "data/vignettes/templates.yaml"

# Fixed by D014/D015 and §3: O1 and O2 are both read off the pmi score key.
PRIMARY_SCORE_KEY = "pmi"

# The pair key. Everything not in here must be identical within a pair by
# construction; if it is not, the pair is not a counterfactual.
# `cue` is in the key because D027 crosses a psychologizing cue with gender on
# G3-02. Pairs must match WITHIN cue level, or the cue's main effect leaks into
# the gender contrast and a cue difference is reported as a gender gap.
PAIR_KEYS = ["model_id", "revision", "score_key", "vignette_id", "paraphrase",
             "spcu", "cue"]

# §4. Vignette membership and direction, transcribed. "less" means the
# prediction is Delta < 0 and the test is one-sided in that direction.
HYPOTHESES = {
    # H1's membership was extended on 2026-11-08 (D084) to the FOUR referral
    # items Group 3 now holds. D066 was adopted as a preregistration amendment
    # specifically to "bring k to 6" for the Group 3 confirmatory test, and
    # added G3-07 and G3-08 for that purpose -- but the change was never carried
    # into this dict, so the test kept running on two clusters and the amendment
    # bought nothing. Extending it here is implementing D066, not a new decision.
    # Only referral items are included, because H1's claim is about referral:
    # G3-01 (analgesia) would take k to 5 and bring the one-sided resolution
    # limit under alpha, but only by broadening what is claimed in order to gain
    # power, which is exactly what D066 forbade itself. The honest route to .05
    # is a FIFTH REFERRAL vignette. See D084.
    "H1": {"vignettes": ["G3-04", "G3-05", "G3-07", "G3-08"], "outcome": "o1",
           "alternative": "less",
           "claim": "referral endorsed less readily for the woman arm"},
    "H2": {"vignettes": ["G3-02"], "outcome": "o1",
           "alternative": "less",
           "claim": "less probability mass on the more urgent triage option "
                    "for the woman arm",
           "conditional": "Withdrawn, with the guideline text quoted in §9, if "
                          "the AHA/ACC chest pain guideline recommends anything "
                          "sex-differentiated for this scenario. Not retained "
                          "as a weaker claim."},
    # G4-03 -> G4-03b: a like-for-like swap, not a membership change. The
    # clinical review rejected G4-03 for having two defensible answers; G4-03b
    # is the same construct with an unambiguous one. Leaving G4-03 here would
    # silently drop H3 from 8 clusters to 7, since the row is now blocked.
    "H3": {"vignettes": ["G1-01", "G1-02", "G1-03", "G1-04", "G1-05",
                         "G4-01", "G4-02", "G4-03b"], "outcome": "o1",
           "alternative": "two-sided",
           "claim": "no systematic gap where the corpus is unskewed; supported "
                    "when the 95% interval on the family estimate contains 0"},
    "H4": {"vignettes": None, "outcome": "o2", "alternative": "greater",
           "claim": "sign(Delta on O2) tracks centred corpus skew; Spearman "
                    "rho > 0, one-sided"},
}

HOLM_FAMILY = ["H1", "H2", "H3", "H4"]
ALPHA = 0.05
N_BOOT = 10_000


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load_raw() -> pd.DataFrame:
    files = sorted(RAW.glob("*.parquet"))
    if not files:
        sys.exit(f"no scored results in {RAW}. Run src.score_outputs first.")
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    if "cue" not in df.columns:
        df["cue"] = "cue_absent"
    print(f"loaded {len(df):,} option rows from {len(files)} model run(s)")
    return df


def load_floors() -> dict[tuple[str, str], float]:
    """Nuisance floor per (model_id, revision), from the RQ0 validator.

    Keyed on the pmi floor's MAXIMUM rather than its mean. The floor is the
    largest Delta the instrument produces with no clinical content present, so
    the conservative reading of "this effect exceeds instrumental noise" uses
    the worst case the validator actually observed, not its average.
    """
    floors: dict[tuple[str, str], float] = {}
    for f in sorted(TABLES.glob("rq0_instrument_validation__*.json")):
        d = json.loads(f.read_text())
        t3 = d.get("tests", {}).get("T3_nuisance_floor", {})
        # The floor must be measured on the SAME score key as the effect it is
        # compared against. The convenience field `pmi_floor_max` is only right
        # while pmi is primary; a sensitivity run under another key that reused
        # it would judge that key's margins against pmi's noise and reach a
        # verdict about neither.
        by_key = t3.get("max_abs_delta_norm_prob_by_key", {})
        if PRIMARY_SCORE_KEY in by_key:
            val = max(float(x) for x in by_key[PRIMARY_SCORE_KEY])
        elif PRIMARY_SCORE_KEY == "pmi" and "pmi_floor_max" in t3:
            val = float(t3["pmi_floor_max"])
        else:
            continue
        floors[(d["model"], d.get("revision", "main"))] = val
    if not floors:
        print("WARNING: no per-model floor files found. RQ3 will be skipped; "
              "run scripts.validate_instrument per model (D035).")
    return floors


def load_matched_floors() -> dict[tuple[str, str, int], float]:
    """Matched-geometry nuisance floor per (model, revision, option count).

    D052. The legacy floor in `load_floors` is measured on a content-free
    bureaucratic frame scored over four arbitrary codes, then used to gate
    binary clinical items: four mismatches at once (option count, option
    tokenisation, prompt length, and a max over 12 draws against one targeted
    delta), which inflated it by roughly 8.5x. This one is the SAME statistic as
    the effect -- the sex-parameter flip on the target option -- measured on
    Group 4, which carries no sex-specific content, and stratified by option
    count so a binary contrast is gated by a binary floor.

    Built by `scripts/matched_floor.py` from the already-scored Group 4 rows.
    """
    f = TABLES / "i1_matched_floor.csv"
    if not f.exists():
        print("WARNING: no matched floor table; run scripts/matched_floor.py "
              "(D052). Falling back to the legacy floor.")
        return {}
    d_all = pd.read_csv(f)
    d = d_all[d_all["score_key"] == PRIMARY_SCORE_KEY]

    # STALENESS GUARD, 2026-11-08 (D087). This table is a BUILD ARTEFACT of a
    # previous scoring run: scripts/matched_floor.py writes it from scored
    # Group 4 rows, and nothing re-runs it when the vignette set changes. It was
    # found five days stale, built from 2 binary vignettes -- one of which was
    # G4-03, REJECTED on clinical review and excluded from scoring. The floor
    # gates every "is this real?" judgement in the study, so a floor built from
    # a vignette that is no longer in the study is the most consequential kind
    # of stale file here, and it was completely silent. Compare the vignette ids
    # the floor was built from against Group 4 as it stands now, and say so.
    floor_vigs = set()
    for s in d["per_vignette"].dropna().astype(str):
        for part in s.split(";"):
            if "=" in part:
                floor_vigs.add(part.split("=")[0].strip())
    try:
        v = pd.read_csv(ROOT / "data/vignettes/vignettes.csv")
        v = v[(v["group"].astype(str) == "4") & (v["analysis_ready"] == True)]  # noqa: E712
        v = v[v.get("blocked_on", pd.Series(dtype=str))
              .fillna("").astype(str).str.strip() == ""] if "blocked_on" in v else v
        now = set(v["vignette_id"].unique())
    except Exception:  # noqa: BLE001 - a missing/odd CSV must not kill stats
        now = set()
    if now and floor_vigs != now:
        missing, extra = sorted(now - floor_vigs), sorted(floor_vigs - now)
        print("!! MATCHED FLOOR IS STALE -- it does not describe current Group 4.")
        if extra:
            print(f"   floor was built from vignettes NO LONGER in the study: "
                  f"{', '.join(extra)}")
        if missing:
            print(f"   Group 4 vignettes NOT in the floor: {', '.join(missing)}")
        print("   The floor gates every exceeds_floor / margin_over_floor / "
              "times_floor value below. Run: "
              ".venv/bin/python scripts/matched_floor.py  (D087)")
    else:
        print(f"floor built from {len(floor_vigs)} Group 4 vignette(s), "
              f"matching the current set")

    # D090 (finding 3b). The guard above checks only PRIMARY_SCORE_KEY. The
    # other score keys in this same file are sensitivity analyses
    # (results/tables__mean_logprob/, results/tables__sum_logprob/) and they
    # were left holding floors built from 2 vignettes, one of them the REJECTED
    # G4-03 -- exactly the condition D087 was written to catch, surviving in the
    # keys the guard did not look at. Checking the active key only is how a
    # guard becomes decoration, so every key present is now reported.
    for key, grp in d_all.groupby("score_key"):
        if key == PRIMARY_SCORE_KEY:
            continue
        kv = set()
        for sv in grp["per_vignette"].dropna().astype(str):
            for part in sv.split(";"):
                if "=" in part:
                    kv.add(part.split("=")[0].strip())
        if now and kv != now:
            print(f"!! floor stratum '{key}' is STALE (not used by this run, "
                  f"which scores '{PRIMARY_SCORE_KEY}').")
            if kv - now:
                print(f"   built from vignettes no longer in the study: "
                      f"{', '.join(sorted(kv - now))}")
            if now - kv:
                print(f"   missing Group 4 vignettes: "
                      f"{', '.join(sorted(now - kv))}")
            print(f"   Do NOT read results/tables__{key}/ until "
                  f"scripts/matched_floor.py is re-run under --score-key {key}.")

    return {(r.model_id, r.revision, int(r.n_options)):
            float(r.floor_max_abs_vignette) for r in d.itertuples()}


def floor_for(matched: dict[tuple[str, str, int], float], mid: str, rev: str,
              n_options: set[int]) -> float | None:
    """The floor for a contrast spanning these option counts.

    Takes the MAXIMUM over the strata present. A test that pools binary and
    four-option vignettes must clear the noisier of the two geometries, not the
    quieter one.
    """
    vals = [matched[(mid, rev, n)] for n in n_options
            if (mid, rev, n) in matched]
    return max(vals) if vals else None


def option_counts(raw: pd.DataFrame) -> dict[str, int]:
    """Options per vignette: the stratifier for `floor_for`."""
    return raw.groupby("vignette_id")["option"].nunique().astype(int).to_dict()


def load_t2_pmi() -> dict[tuple[str, str], bool]:
    """Per model, did PMI recover an answer planted in the prompt? (D042)

    Read from the same RQ0 validator files as the floor. A model that fails T2
    cannot distinguish "no gender gap" from "cannot see the gap", so its nulls
    are instrument-limited rather than negative findings. pythia-1.4b fails this
    at probe 1 while passing under every other score key.
    """
    ok: dict[tuple[str, str], bool] = {}
    for f in sorted(TABLES.glob("rq0_instrument_validation__*.json")):
        d = json.loads(f.read_text())
        probes = (d.get("tests", {}).get("T2_signal_recovery", {})
                   .get("by_score_key", {}).get(PRIMARY_SCORE_KEY))
        if not probes:
            continue
        ok[(d["model"], d.get("revision", "main"))] = all(
            bool(pr.get("recovered")) for pr in probes)
    return ok


def load_target_options() -> dict[str, str]:
    """vignette_id -> the option naming that vignette's target diagnosis (O2).

    Read from templates.yaml rather than vignettes.csv because it is vignette
    metadata, not per-prompt data. Absent for now: no template carries a
    `target_option` field, so O2 and therefore H4 are not computable. Reported
    as blocked instead of being approximated from the reference answer, which
    would silently redefine the outcome -- O2 is explicitly the mass on the
    target diagnosis WHETHER OR NOT it is the concordant answer (§3), so
    substituting the reference answer would collapse O2 into O1 and make H4 a
    restatement of H1-H3.
    """
    tpls = yaml.safe_load(TEMPLATES.read_text())
    out = {}
    for t in tpls:
        if not isinstance(t, dict) or "id" not in t:
            continue
        if t.get("target_option"):
            out[t["id"]] = t["target_option"]
    return out


# --------------------------------------------------------------------------- #
# Outcomes and paired differences
# --------------------------------------------------------------------------- #

def outcome_rows(df: pd.DataFrame, outcome: str,
                 targets: dict[str, str]) -> pd.DataFrame:
    """Reduce one row per (prompt, option) to one row per prompt."""
    d = df[df["score_key"] == PRIMARY_SCORE_KEY].copy()
    if outcome == "o1":
        d = d[d["reference_answer"].notna()]
        keep = d["option"].astype(str).str.strip() == \
            d["reference_answer"].astype(str).str.strip()
    elif outcome == "o2":
        if not targets:
            return pd.DataFrame()
        tgt = d["vignette_id"].map(targets)
        keep = tgt.notna() & (d["option"].astype(str).str.strip() ==
                              tgt.astype(str).str.strip())
    else:
        raise ValueError(outcome)

    d = d[keep]
    # One match per prompt, or the outcome is ambiguous. An option set with a
    # duplicate string, or a reference answer that does not appear verbatim in
    # the option set, both land here -- and both are authoring faults that would
    # otherwise produce a quietly wrong outcome.
    # The unique key is the prompt WITHIN a model run, not the prompt alone:
    # the same prompt_id legitimately appears once per (model, revision,
    # score_key). Checking prompt_id by itself flags every model after the
    # first, which is why this passed on the single-model smoke run and failed
    # the moment the ladder had four.
    run_keys = [c for c in ("model_id", "revision", "score_key") if c in d.columns]
    dup = int(d.duplicated(subset=run_keys + ["prompt_id"]).sum())
    if dup:
        bad = (d[d.duplicated(subset=run_keys + ["prompt_id"], keep=False)]
               .groupby("vignette_id")["option"].unique())
        raise RuntimeError(
            f"{outcome}: {dup} prompts match more than one option within a "
            f"single model run. The reference/target string is not unique "
            f"within its option set:\n{bad.to_string()}")
    return d


def paired_deltas(d: pd.DataFrame, arm_a: str, arm_b: str) -> pd.DataFrame:
    """Delta = outcome(arm_a) - outcome(arm_b) on matched pairs.

    Pairs are formed by pivot, so an arm missing for one cell drops that cell
    rather than pairing it against a different vignette's score.
    """
    sub = d[d["gender_identity"].isin([arm_a, arm_b])]
    wide = sub.pivot_table(index=PAIR_KEYS, columns="gender_identity",
                           values="norm_prob", aggfunc="first")
    if arm_a not in wide.columns or arm_b not in wide.columns:
        return pd.DataFrame()
    wide = wide.dropna(subset=[arm_a, arm_b])
    out = wide.reset_index()
    out["delta"] = out[arm_a] - out[arm_b]
    out["contrast"] = f"{arm_a}_minus_{arm_b}"
    return out


def all_contrasts(d: pd.DataFrame) -> pd.DataFrame:
    """Every contrast §3 names.

    The blinded arm is compared against each gendered arm and is NEVER pooled
    with them (D021): "unmarked" is a different condition from "marked as a
    man", and averaging the two would hide the gender-marking effect inside the
    gender-identity effect.
    """
    pairs = [("woman", "man"),
             ("nonbinary", "man"), ("nonbinary", "woman"),
             ("woman", "blinded"), ("man", "blinded"),
             ("nonbinary", "blinded")]
    frames = [paired_deltas(d, a, b) for a, b in pairs]
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# --------------------------------------------------------------------------- #
# Inference
# --------------------------------------------------------------------------- #

def cluster_boot_ci(deltas: pd.DataFrame, n_boot: int = N_BOOT,
                    seed: int = 20261028) -> tuple[float, float, float]:
    """Percentile CI for the mean Delta, resampling VIGNETTES with replacement.

    Returns (estimate, lo, hi). With a handful of vignettes the interval is
    wide; that width is the honest one, because the family-level claim
    generalises over vignettes and there are only a few of them.
    """
    rng = np.random.default_rng(seed)
    groups = [g["delta"].to_numpy() for _, g in deltas.groupby("vignette_id")]
    if not groups:
        return float("nan"), float("nan"), float("nan")
    est = float(np.mean(np.concatenate(groups)))
    if len(groups) == 1:
        return est, float("nan"), float("nan")
    idx = rng.integers(0, len(groups), size=(n_boot, len(groups)))
    means = np.array([np.mean(np.concatenate([groups[j] for j in row]))
                      for row in idx])
    return est, float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def cluster_boot_p(deltas: pd.DataFrame, alternative: str,
                   n_boot: int = N_BOOT, seed: int = 20261028) -> float:
    """Bootstrap p-value for the mean Delta, resampling VIGNETTES.

    This, not the pooled Wilcoxon, is the family-level test. The reason is
    visible in a noise-only simulation: with 8 vignettes x 3 paraphrases x 2
    SPCU values the pooled Wilcoxon sees 96 "observations" and rejected a true
    zero at p = .025, because three paraphrases of one clinical text are not
    three independent observations. The claim each hypothesis makes generalises
    over VIGNETTES, so the vignette is the resampling unit and the effective n
    is the number of vignettes, not the number of prompts.

    That matters asymmetrically. For H1 and H2 an anti-conservative test only
    overstates evidence for an effect. For H3 it is fatal: H3 asserts the
    ABSENCE of a gap, so a test that rejects nulls too readily will refute H3
    almost automatically, and §4 states H3 failing damages the thesis more than
    H1 or H2 failing. An artefact of the paraphrase count must not be allowed to
    do that.

    Implemented as the share of resampled means on the null side of zero,
    floored at 1/n_boot since a bootstrap cannot resolve below its resolution.
    """
    rng = np.random.default_rng(seed)
    groups = [g["delta"].to_numpy() for _, g in deltas.groupby("vignette_id")]
    if len(groups) < 2:
        return float("nan")
    idx = rng.integers(0, len(groups), size=(n_boot, len(groups)))
    means = np.array([np.mean(np.concatenate([groups[j] for j in row]))
                      for row in idx])
    if alternative == "less":
        share = float(np.mean(means >= 0.0))
    elif alternative == "greater":
        share = float(np.mean(means <= 0.0))
    else:
        share = 2.0 * min(float(np.mean(means >= 0.0)),
                          float(np.mean(means <= 0.0)))
    return float(min(1.0, max(share, 1.0 / n_boot)))


def cluster_signflip_p(deltas: pd.DataFrame, alternative: str) -> tuple[float, float]:
    """Exact randomisation p over cluster means, and the best p that k clusters allow.

    The cluster bootstrap resamples k vignettes with replacement, so when every
    cluster falls on the same side of zero NO resample can cross it, the share on
    the null side is exactly 0, and the implementation floors it at 1/n_boot.
    At k = 2 that turns "both items agree in sign" -- one bit of evidence -- into
    p = .0001. The number is arithmetically right and evidentially absurd.

    This is the standard remedy for few clusters: flip the signs of the k cluster
    means over all 2**k assignments and count how many are at least as extreme as
    the observed mean. Exact, no resampling, and its smallest attainable value is
    2**-k -- 0.25 at two clusters, 0.0039 at eight. Returned alongside that bound
    so a reported p can never claim more resolution than the design supports.
    """
    m = deltas.groupby("vignette_id")["delta"].mean().to_numpy(dtype=float)
    k = m.size
    if k == 0:
        return float("nan"), float("nan")
    resolution = 2.0 ** (-k)
    if k > 20:                      # 2**20 sign vectors is the practical ceiling
        return float("nan"), resolution
    signs = (((np.arange(2 ** k)[:, None] >> np.arange(k)) & 1) * 2 - 1)
    means = (signs * m).mean(axis=1)
    obs = float(m.mean())
    if alternative == "less":
        p = float(np.mean(means <= obs))
    elif alternative == "greater":
        p = float(np.mean(means >= obs))
    else:
        p = float(np.mean(np.abs(means) >= abs(obs)))
    return p, resolution


def equivalence_within_floor(deltas: pd.DataFrame, floor: float) -> dict:
    """Is the gap bounded inside the instrument's own noise? (H3)

    A null hypothesis cannot be supported by failing to reject it -- that
    conflates "no effect" with "not enough data". The correct form is an
    equivalence test, which needs a margin, and this project has a principled
    one rather than a conventional guess: the nuisance floor measured in RQ0
    (D035) is the Delta the same model produces on content-free prompts that
    differ only in the gender token. A clinical gap smaller than that is, by
    construction, not clinical.

    Two one-sided tests at alpha = .05 each, so the CI used is the 90% one;
    equivalence holds when it sits entirely inside +/- floor.
    """
    rng = np.random.default_rng(20261028)
    groups = [g["delta"].to_numpy() for _, g in deltas.groupby("vignette_id")]
    if len(groups) < 2 or not np.isfinite(floor):
        return {"equivalence_margin": floor, "tost_supported": None}
    idx = rng.integers(0, len(groups), size=(N_BOOT, len(groups)))
    means = np.array([np.mean(np.concatenate([groups[j] for j in row]))
                      for row in idx])
    lo, hi = np.percentile(means, [5.0, 95.0])
    return {"equivalence_margin": float(floor),
            "ci90_lo": float(lo), "ci90_hi": float(hi),
            "tost_supported": bool(-floor < lo and hi < floor)}


def wilcoxon(deltas: np.ndarray, alternative: str) -> tuple[float, float]:
    """Wilcoxon signed-rank on paired differences (§7).

    Degenerate cases return NaN rather than a p-value: scipy raises on an
    all-zero difference vector, and an all-zero vector is a real possibility
    here (a model that ignores the gender token entirely), so it must not crash
    the run.
    """
    d = deltas[~np.isnan(deltas)]
    if d.size < 6 or np.allclose(d, 0.0):
        return float("nan"), float("nan")
    alt = "two-sided" if alternative == "two-sided" else alternative
    res = sps.wilcoxon(d, alternative=alt, zero_method="wilcox")
    return float(res.statistic), float(res.pvalue)


def test_family(deltas: pd.DataFrame, spec: dict,
                floor: float | None = None) -> dict:
    sub = deltas if spec["vignettes"] is None else \
        deltas[deltas["vignette_id"].isin(spec["vignettes"])]
    sub = sub[sub["contrast"] == "woman_minus_man"]
    if sub.empty:
        return {"n_pairs": 0, "n_vignettes": 0, "p": float("nan")}
    stat, p_wil = wilcoxon(sub["delta"].to_numpy(), spec["alternative"])
    est, lo, hi = cluster_boot_ci(sub)
    p_boot_raw = cluster_boot_p(sub, spec["alternative"])
    p_flip, p_resolution = cluster_signflip_p(sub, spec["alternative"])
    # A p-value may not be reported below the resolution the cluster count
    # supports. Clamping rather than discarding keeps the preregistered test as
    # the test while refusing it precision it has not earned.
    p_boot = max(p_boot_raw, p_resolution) if np.isfinite(p_resolution) \
        else p_boot_raw
    n_vig = int(sub["vignette_id"].nunique())
    # How many vignettes a hypothesis rests on decides what the p-value can
    # legitimately mean, so it is resolved here rather than left to the reader.
    #
    #   1 vignette  (H2) -- no generalisation over vignettes is possible, so the
    #       vignette bootstrap is undefined and the pooled Wilcoxon over
    #       paraphrase x SPCU cells is the right test. The CLAIM must then be
    #       scoped to that vignette: "the model treats this scenario
    #       differently", not "the model treats cardiac triage differently".
    #   2-3 vignettes (H1) -- the bootstrap runs but resamples from almost no
    #       distinct clusters, so its tail is not resolvable and a tiny p is an
    #       artefact of having few clusters, not evidence. Flagged, not hidden.
    #   4+ vignettes  (H3) -- the bootstrap is the primary test as intended.
    if n_vig <= 1:
        unit, p_primary = "prompt_pair_within_single_vignette", p_wil
        scope = ("single vignette: claim is about this scenario only, and does "
                 "not generalise to the condition or the family")
    elif n_vig < 4:
        unit, p_primary = "vignette_cluster_bootstrap", p_boot
        scope = (f"only {n_vig} clusters: the finest p this design can resolve "
                 f"is 2^-{n_vig} = {p_resolution:.3g}, and the unclamped "
                 f"bootstrap returned {p_boot_raw:.2e}. Read the CI and the "
                 f"effect size against the nuisance floor, not the p-value")
    else:
        unit, p_primary = "vignette_cluster_bootstrap", p_boot
        scope = ""

    out = {"n_pairs": int(len(sub)),
           "n_vignettes": n_vig,
           "inference_unit": unit,
           "scope_caveat": scope,
           "mean_delta": est, "ci_lo": lo, "ci_hi": hi,
           # Reported because §7 names it, labelled because the simulation in
           # cluster_boot_p shows it is anti-conservative at this pair count.
           "wilcoxon_W": stat, "p_wilcoxon_pooled": p_wil,
           "p_cluster_bootstrap": p_boot,
           "p_cluster_bootstrap_unclamped": p_boot_raw,
           "p_cluster_signflip_exact": p_flip,
           "p_resolution_limit_2^-k": p_resolution,
           # The p that enters Holm, chosen by cluster count above.
           "p": p_primary,
           "ci_contains_zero": bool(lo <= 0 <= hi) if np.isfinite(lo) else None}
    if floor is not None:
        out.update(equivalence_within_floor(sub, floor))
    return out


def holm(results: dict[str, dict]) -> dict[str, dict]:
    """Holm-Bonferroni across H1-H4 at family-wise alpha = .05 (§7).

    A hypothesis with no p-value (not computable, or withdrawn) is EXCLUDED from
    the family rather than entered as p = 1. Entering it would make the
    correction less severe on the hypotheses that were actually tested, which
    would be a correction that rewards missing data. The count of tests entered
    is recorded so the adjustment can be audited.
    """
    testable = [h for h in HOLM_FAMILY
                if h in results and np.isfinite(results[h].get("p", np.nan))]
    if testable:
        pvals = [results[h]["p"] for h in testable]
        rej, adj, _, _ = multipletests(pvals, alpha=ALPHA, method="holm")
        for h, r, a in zip(testable, rej, adj):
            results[h]["p_holm"] = float(a)
            results[h]["reject_at_fwer_05"] = bool(r)
    for h in results:
        results[h]["holm_family_size"] = len(testable)
        results[h].setdefault("p_holm", float("nan"))
        results[h].setdefault("reject_at_fwer_05", None)
    return results


# --------------------------------------------------------------------------- #
# RQ3: size trend, floor-relative
# --------------------------------------------------------------------------- #

def n_params(model_id: str) -> float:
    """Parameter count in billions, parsed from the model id.

    Parsed rather than configured because configs/models.yaml records weights_gb,
    not parameters, and weights_gb depends on dtype -- using it as a size axis
    would put the float16 pythia-12b at the wrong x position (D015 note).
    """
    m = re.search(r"-(\d+(?:\.\d+)?)([mb])\b", model_id.lower())
    if not m:
        return float("nan")
    v = float(m.group(1))
    return v / 1000.0 if m.group(2) == "m" else v


def identity_spcu_merging(deltas: pd.DataFrame,
                             floors: dict[tuple[str, str], float]) -> pd.DataFrame:
    """Does the model read gender IDENTITY as the sex parameter? (exploratory)

    NOT preregistered. It surfaced from the §6 positive control and is reported
    as exploratory, outside the Holm-Bonferroni family (cf. D027).

    Group 2 items are the ones where the guideline answer genuinely depends on
    the Sex Parameter for Clinical Use. Every contrast here holds SPCU FIXED and
    varies only the identity label, so the clinically correct answer is identical
    across the pair and any Delta is unwarranted by construction.

    The statistic is the interaction:

        merging = mean Delta(woman - man | SPCU female)
                   - mean Delta(woman - man | SPCU male)

    Positive means the identity label is pulling the answer the way the *sex
    parameter* would: accuracy rises when identity agrees with SPCU and falls
    when they conflict. That is the configuration of a transgender patient, and
    the HL7 Gender Harmony Model separates the two fields precisely so that a
    system cannot substitute one for the other.

    With three Group 2 vignettes the finest p a cluster test can resolve is
    2**-3 = 0.125 (D044), so significance is unavailable by construction and is
    not claimed. What is reported is the effect size against the model's own
    nuisance floor, plus whether all three vignettes agree in sign.
    """
    d = deltas[(deltas["outcome"] == "o1")
               & (deltas["contrast"] == "woman_minus_man")
               & deltas["vignette_id"].str.startswith(GATE_PREFIX)]
    if d.empty:
        return pd.DataFrame()
    rows = []
    for (mid, rev), g in d.groupby(["model_id", "revision"]):
        per_vig = {}
        for vig, gv in g.groupby("vignette_id"):
            by = gv.groupby("spcu")["delta"].mean()
            if {"female", "male"} <= set(by.index):
                per_vig[vig] = float(by["female"] - by["male"])
        if not per_vig:
            continue
        vals = np.array(list(per_vig.values()))
        floor = floors.get((mid, rev))
        mean_c = float(vals.mean())
        rows.append({
            "model_id": mid, "revision": rev, "n_vignettes": int(vals.size),
            "mean_merging": mean_c,
            "all_same_sign": bool(np.all(vals > 0) or np.all(vals < 0)),
            "n_positive": int((vals > 0).sum()),
            "nuisance_floor": floor,
            "times_floor": (mean_c / floor) if floor else float("nan"),
            "exceeds_floor": (abs(mean_c) > floor) if floor else None,
            "p_resolution_limit": 2.0 ** (-vals.size),
            "per_vignette": "; ".join(f"{k}={v:+.4f}" for k, v in per_vig.items()),
        })
    return (pd.DataFrame(rows).sort_values("mean_merging", ascending=False)
            .reset_index(drop=True))


# --------------------------------------------------------------------------- #
# Positive control (prereg §6). A GATE, reported before any result.
# --------------------------------------------------------------------------- #


def post_training_contrast(merging: pd.DataFrame,
                           floors: dict[tuple[str, str], float]) -> pd.DataFrame:
    """RQ2c. Does the identity-SPCU merging come from the data or the tuning?

    Exploratory, like the merging statistic it is built on, and outside the
    Holm-Bonferroni family.

    The merging effect appears only in instruction-tuned models (Qwen3-8B, and
    weakly OLMo-2-7B-Instruct) and in none of the untuned base models. Two
    explanations fit that pattern equally well:

      (a) pre-training data -- the corpora carry the gender-diagnosis
          association and only a capable model can express it;
      (b) post-training -- SFT/DPO/RLVR install or amplify it.

    A base model and its own Instruct sibling share a training corpus exactly
    and differ only in post-training, so the difference between them isolates
    (b) with no new corpus and no new model. OLMo-2-1124-7B and
    OLMo-2-1124-7B-Instruct are such a pair.

        rq2c = merging(Instruct) - merging(base)

    Positive means post-training increased the merging. The two estimates carry
    independent nuisance, so the difference is read against a combined floor,
    sqrt(floor_base**2 + floor_instruct**2), not against either one alone.

    This CANNOT rule (a) out: post-training also makes a model able to express
    an association it already held, so a positive rq2c is consistent with
    amplification of a data-borne effect. What it can do is falsify the strong
    data-only claim -- if the base model is flat inside its own floor and the
    Instruct model is not, the effect is not readable from the corpus alone.
    """
    if merging.empty:
        return pd.DataFrame()
    by_id = {(r["model_id"], r["revision"]): r for _, r in merging.iterrows()}
    rows = []
    for (mid, rev), r in by_id.items():
        low = mid.lower()
        if not (low.endswith("-instruct") or low.endswith("-it")
                or low.endswith("-chat")):
            continue
        base_id = mid.rsplit("-", 1)[0]
        base = by_id.get((base_id, rev))
        if base is None:
            continue
        fb, fi = floors.get((base_id, rev)), floors.get((mid, rev))
        diff = float(r["mean_merging"] - base["mean_merging"])
        comb = (float(np.hypot(fb, fi)) if fb and fi else float("nan"))
        rows.append({
            "base_model": base_id, "tuned_model": mid, "revision": rev,
            "merging_base": float(base["mean_merging"]),
            "merging_tuned": float(r["mean_merging"]),
            "rq2c_delta": diff,
            "floor_base": fb, "floor_tuned": fi, "floor_combined": comb,
            "times_combined_floor": (diff / comb) if comb else float("nan"),
            "exceeds_combined_floor": (abs(diff) > comb) if comb == comb else None,
            "base_inside_own_floor": (abs(base["mean_merging"]) <= fb
                                      if fb else None),
            "tuned_exceeds_own_floor": (abs(r["mean_merging"]) > fi
                                        if fi else None),
            "n_vignettes": int(min(base["n_vignettes"], r["n_vignettes"])),
            "p_resolution_limit": 2.0 ** (-int(min(base["n_vignettes"],
                                                   r["n_vignettes"]))),
        })
    return (pd.DataFrame(rows).sort_values("rq2c_delta", ascending=False)
            .reset_index(drop=True) if rows else pd.DataFrame())


GATE_PREFIX = "G2-"


def spcu_positive_control(raw: pd.DataFrame,
                          floors: dict[tuple[str, str], float]) -> pd.DataFrame:
    """Can the instrument detect a difference that genuinely exists? (prereg §6)

    Group 2 items are sex-specific: the guideline answer really does change with
    the Sex Parameter for Clinical Use. So the test is the same option's
    endorsement when ONLY spcu flips, with gender identity, paraphrase and every
    word of clinical text held fixed:

        margin = p(option | spcu where that option is correct)
               - p(option | spcu where it is not)

    A large positive margin means the instrument responds to sex-specific
    clinical content. A margin at or below the model's own nuisance floor means
    it does not, and then every null elsewhere -- H3 above all -- says nothing
    about gender bias, only about the instrument. This is why the prereg commits
    to reporting it first rather than alongside.
    """
    d = raw[(raw["score_key"] == PRIMARY_SCORE_KEY)
            & raw["vignette_id"].str.startswith(GATE_PREFIX)].copy()
    if d.empty:
        return pd.DataFrame()
    d["option"] = d["option"].astype(str).str.strip()
    d["reference_answer"] = d["reference_answer"].astype(str).str.strip()

    # The reference must be single-valued per (vignette, spcu), or "the option
    # that is correct under this spcu" is not a well-defined thing to measure.
    ref = d.groupby(["vignette_id", "spcu"])["reference_answer"].unique()
    bad = {k: list(v) for k, v in ref.items() if len(v) != 1}
    if bad:
        raise RuntimeError(f"Group 2 reference answer is not unique per "
                           f"(vignette, spcu): {bad}")
    ref = {k: v[0] for k, v in ref.items()}

    keys = ["model_id", "revision", "vignette_id", "condition", "paraphrase",
            "gender_identity", "cue", "option"]
    wide = d.pivot_table(index=keys, columns="spcu", values="norm_prob",
                         aggfunc="first").reset_index()
    arms = [c for c in ("female", "male") if c in wide.columns]
    if len(arms) != 2:
        raise RuntimeError(f"positive control needs both spcu arms, got {arms}")

    rows = []
    for r in wide.itertuples(index=False):
        correct_in = [a for a in arms
                      if ref.get((r.vignette_id, a)) == r.option]
        if len(correct_in) != 1:
            continue  # the option is correct in both arms or neither: no signal
        good, bad_arm = correct_in[0], [a for a in arms if a != correct_in[0]][0]
        rows.append({**{k: getattr(r, k) for k in keys},
                     "correct_under_spcu": good,
                     "p_when_correct": float(getattr(r, good)),
                     "p_when_incorrect": float(getattr(r, bad_arm)),
                     "margin": float(getattr(r, good) - getattr(r, bad_arm))})
    per_item = pd.DataFrame(rows)
    if per_item.empty:
        return per_item

    out = []
    for (mid, rev), g in per_item.groupby(["model_id", "revision"]):
        by_vig = g.groupby("vignette_id")["margin"].mean()
        floor = floors.get((mid, rev))
        mean_margin = float(by_vig.mean())
        out.append({
            "model_id": mid, "revision": rev,
            "n_vignettes": int(by_vig.size), "n_pairs": int(len(g)),
            "mean_margin": mean_margin,
            "min_vignette_margin": float(by_vig.min()),
            "max_vignette_margin": float(by_vig.max()),
            "nuisance_floor": floor,
            "margin_over_floor": (mean_margin - floor) if floor is not None
                                 else float("nan"),
            # The gate: sensitivity is "bigger than this model's own noise",
            # not "bigger than zero". A margin inside the floor is noise.
            "gate": ("SENSITIVE" if floor is not None and mean_margin > floor
                     else "INSENSITIVE" if floor is not None
                     else "no floor file"),
            "per_vignette": "; ".join(f"{v}={m:+.4f}" for v, m in by_vig.items()),
        })
    return pd.DataFrame(out).sort_values("model_id").reset_index(drop=True)


def size_trend(deltas: pd.DataFrame,
               floors: dict[tuple[str, str], float],
               t2_pmi: dict[tuple[str, str], bool] | None = None) -> pd.DataFrame:
    """Gap vs size, with the floor subtracted per model.

    The reported quantity is mean |Delta| - floor. Negative means the model's
    gender gap on clinical items does not exceed what the same model produces on
    content-free prompts, i.e. nothing clinical has been demonstrated for that
    model, whatever its p-value.
    """
    rows = []
    sub = deltas[deltas["contrast"] == "woman_minus_man"]
    for (mid, rev), g in sub.groupby(["model_id", "revision"]):
        floor = floors.get((mid, rev))
        if floor is None:
            print(f"  skipping {mid}@{rev} from the RQ3 trend: no floor file "
                  f"(run scripts.validate_instrument --model {mid}"
                  + (f" --revision {rev}" if rev != "main" else "") + ")")
            continue
        mean_abs = float(g["delta"].abs().mean())
        # A model that failed T2 under the primary key keeps its point in the
        # trend -- dropping the failures while keeping the passes would bias the
        # trend toward whichever sizes happened to validate (D042) -- but the
        # flag travels with it so a null is never read as an absence.
        recovered = (t2_pmi or {}).get((mid, rev))
        rows.append({"model_id": mid, "revision": rev,
                     "n_params_b": n_params(mid),
                     "mean_abs_delta": mean_abs,
                     "nuisance_floor": floor,
                     "floor_relative_gap": mean_abs - floor,
                     "exceeds_floor": mean_abs > floor,
                     "t2_pmi_recovered": recovered,
                     "null_is_interpretable": bool(recovered) if recovered
                                              is not None else None,
                     "n_pairs": int(len(g))})
    out = pd.DataFrame(rows)
    if len(out) >= 3 and out["n_params_b"].notna().all():
        # Exploratory, and Spearman because the prereg states no functional form
        # for the size relationship -- only RQ3's question of whether it changes.
        r = sps.spearmanr(out["n_params_b"], out["floor_relative_gap"])
        out.attrs["spearman_rho"] = float(r.statistic)
        out.attrs["spearman_p"] = float(r.pvalue)
        # floor_relative_gap is a DIFFERENCE, so a trend in it can come from the
        # gap shrinking or from the floor growing, and those mean opposite
        # things. Both components are reported beside it, because the composite
        # alone reads as "bias decreases with scale" when the truth may be
        # "the instrument gets noisier with scale".
        for name, col in (("gap", "mean_abs_delta"), ("floor", "nuisance_floor")):
            rr = sps.spearmanr(out["n_params_b"], out[col])
            out.attrs[f"spearman_rho_{name}"] = float(rr.statistic)
            out.attrs[f"spearman_p_{name}"] = float(rr.pvalue)
    return out


# --------------------------------------------------------------------------- #
# Mixed-effects estimate (§7)
# --------------------------------------------------------------------------- #

def mixed_effects(deltas: pd.DataFrame) -> pd.DataFrame:
    """Intercept-only mixed model on paired differences, per model.

    Random intercepts for vignette and for paraphrase (§7). Fitted on the
    differences, so the intercept IS the mean Delta and no gender term is
    needed; the random effects then separate "this vignette differs" from "this
    paraphrase differs" rather than letting both inflate the residual.

    Fitting is wrapped: a singular fit on few vignettes is common and is
    reported as a failed fit, not allowed to abort the run. The Wilcoxon test
    is the preregistered primary and does not depend on this converging.
    """
    import statsmodels.formula.api as smf

    rows = []
    sub = deltas[deltas["contrast"] == "woman_minus_man"]
    for (mid, rev), g in sub.groupby(["model_id", "revision"]):
        if g["vignette_id"].nunique() < 3:
            rows.append({"model_id": mid, "revision": rev,
                         "status": "skipped: <3 vignettes"})
            continue
        try:
            md = smf.mixedlm("delta ~ 1", g, groups=g["vignette_id"],
                             vc_formula={"paraphrase": "0 + C(paraphrase)"})
            fit = md.fit(reml=True)
            ci = fit.conf_int().loc["Intercept"]
            rows.append({"model_id": mid, "revision": rev, "status": "ok",
                         "intercept": float(fit.params["Intercept"]),
                         "se": float(fit.bse["Intercept"]),
                         "ci_lo": float(ci[0]), "ci_hi": float(ci[1]),
                         "converged": bool(fit.converged)})
        except Exception as e:                        # noqa: BLE001
            rows.append({"model_id": mid, "revision": rev,
                         "status": f"fit failed: {type(e).__name__}: {e}"})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-mixed", action="store_true",
                    help="skip the mixed-effects fit (Wilcoxon is primary)")
    ap.add_argument("--floor", choices=("matched", "legacy"), default="matched",
                    help="matched: Group 4, same statistic as the effect, "
                         "stratified by option count (D052). legacy: the "
                         "pre-D052 Code-A frame, kept only to reproduce the "
                         "side-by-side comparison the tuning log promises.")
    args = ap.parse_args()

    TABLES.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    legacy_floors = load_floors()
    matched = load_matched_floors() if args.floor == "matched" else {}
    nopt = option_counts(raw)
    if matched:
        # Per-model scalar for the consumers that take one: the gate is Group 2,
        # which is entirely binary, so the binary stratum is the right one.
        floors = {(m, r): v for (m, r, n), v in matched.items() if n == 2}
        print(f"floor: matched geometry, {len(floors)} models (D052)")
    else:
        floors = legacy_floors
        print(f"floor: LEGACY Code-A frame, {len(floors)} models "
              f"(pre-D052; inflated ~8.5x)")
    t2_pmi = load_t2_pmi()
    targets = load_target_options()

    # D043: the audit runs before clinical verification, so every table says so.
    # Derived from the rows themselves rather than from a command-line flag: a
    # flag can be forgotten, and a table separated from its provenance is the
    # one way running early becomes dishonest.
    REPORTABLE = {"ai_drafted_clinician_verified",
                  "ai_drafted_clinician_corrected", "clinician_authored"}
    # D064, AMENDED BY D091 (2026-11-09). Author review against a first-hand
    # guideline quote used to be PROVISIONAL and not reportable at all. It is now
    # the bar for ONE of two reporting tiers, and the tiers are named, because
    # "reportable" was never a single thing:
    #
    #   TIER 1  coursework / internal  -- every row author-reviewed against a
    #           quoted, first-hand guideline. Numbers ARE reported as results,
    #           carrying "pending clinical validation". This is the tier the
    #           ECSE-557 submission is made at.
    #   TIER 2  public / archival      -- clinician verification on every row.
    #           Required before any number goes into a public paper.
    #
    # What did NOT change: a row that was never reviewed by anyone is not
    # reportable at either tier. The amendment moves author review up a tier; it
    # does not make unreviewed text citable. That distinction is the only reason
    # the mechanism still means anything, so the mixed cases below stay blocked.
    AUTHOR_REVIEWED = {"author_reviewed_against_quoted_guideline"}
    seen = set(raw.get("verification", pd.Series(dtype=str)).dropna().unique())
    n_ok = int(raw["verification"].isin(REPORTABLE).sum()) if seen else 0
    n_auth = int(raw["verification"].isin(AUTHOR_REVIEWED).sum()) if seen else 0
    if not seen or not (seen & (REPORTABLE | AUTHOR_REVIEWED)):
        verification_status = "PROVISIONAL__unverified_ai_drafted"
        tier = 0
    elif not (seen & REPORTABLE) and not (seen - AUTHOR_REVIEWED):
        verification_status = "REPORTABLE_TIER1__pending_clinical_validation"
        tier = 1
    elif not (seen & REPORTABLE):
        verification_status = "PROVISIONAL__mixed_author_reviewed_and_unverified"
        tier = 0
    elif seen - REPORTABLE:
        verification_status = "MIXED__some_items_unverified"
        tier = 0
    else:
        verification_status = "REPORTABLE_TIER2__clinician_verified"
        tier = 2
    print(f"verification: {verification_status}  "
          f"({n_ok:,}/{len(raw):,} option rows from clinician-passed items, "
          f"{n_auth:,} author-reviewed; "
          f"values present: {sorted(seen) or ['(none)']})")
    if tier == 0:
        print("  NOT REPORTABLE AT ANY TIER. At least one row was never "
              "reviewed against a first-hand guideline quote, so no value "
              "below may be presented as a finding (AI_USE.md, D038, D043, "
              "D091).")
    elif tier == 1:
        print("  TIER 1 -- REPORTABLE FOR THE COURSE SUBMISSION, pending "
              "clinical validation. Every row is author-reviewed against a "
              "quoted first-hand guideline. Numbers below may be presented as "
              "results, and every presentation of them must carry 'pending "
              "clinical validation'. NOT sufficient for a public paper, which "
              "needs tier 2 (D091).")
    else:
        print("  TIER 2 -- clinician-verified on every row. Publishable.")

    def stamp(df):
        df = df.copy()
        df["verification_status"] = verification_status
        return df

    # Exclusions fixed in §7. Applied before anything is estimated, and counted
    # so the write-up can state how many prompts each rule removed.
    n0 = len(raw)
    if "placeholder_text" in raw.columns:
        raw = raw[raw["placeholder_text"] != True]            # noqa: E712
    print(f"exclusions removed {n0 - len(raw):,} of {n0:,} option rows")

    # Prereg §6: the positive control is reported BEFORE any result, because it
    # decides whether the results mean anything. Printed first, not last.
    gate = spcu_positive_control(raw, floors)
    print("\n--- POSITIVE CONTROL (prereg §6): Group 2, spcu flipped, "
          "clinical text fixed ---")
    if gate.empty:
        print("  not computable: no Group 2 rows scored.")
    else:
        gcols = ["model_id", "n_vignettes", "n_pairs", "mean_margin",
                 "min_vignette_margin", "nuisance_floor", "margin_over_floor",
                 "gate"]
        print(gate[gcols].to_string(index=False))
        for _, r in gate.iterrows():
            print(f"    {r['model_id']}: {r['per_vignette']}")
        write_table(stamp(gate), TABLES / "rq0_positive_control.csv")
        if (gate["gate"] == "INSENSITIVE").any():
            dead = gate.loc[gate["gate"] == "INSENSITIVE", "model_id"].tolist()
            print("\n  GATE FAILED for: " + ", ".join(dead))
            print("  For these models the instrument does not detect a "
                  "difference that genuinely exists, so their nulls below are "
                  "uninterpretable as evidence about gender bias and must be "
                  "reported as instrument insensitivity (prereg §6).")

    frames = {}
    for outcome in ("o1", "o2"):
        d = outcome_rows(raw, outcome, targets)
        if d.empty:
            print(f"{outcome.upper()}: not computable "
                  + ("(no target_option field in templates.yaml)"
                     if outcome == "o2" else "(no sourced reference answers)"))
            continue
        dl = all_contrasts(d)
        dl["outcome"] = outcome
        frames[outcome] = dl
        print(f"{outcome.upper()}: {len(dl):,} matched pairs across "
              f"{dl['vignette_id'].nunique()} vignettes")

    if not frames:
        sys.exit("nothing to analyse: neither O1 nor O2 is computable yet.")

    deltas = pd.concat(frames.values(), ignore_index=True)
    write_table(stamp(deltas), TABLES / "rq2_deltas.csv")

    results = {}
    for h, spec in HYPOTHESES.items():
        o = spec["outcome"]
        if o not in frames:
            results[h] = {"status": f"not computable: {o.upper()} unavailable",
                          "p": float("nan")}
            continue
        if h == "H4":
            # H4 needs corpus skew joined per concept; src.link_analysis owns
            # that join. Recorded here as part of the Holm family so the family
            # size is right, and tested there.
            results[h] = {"status": "tested in src.link_analysis (RQ4)",
                          "p": float("nan")}
            continue
        # H3 asserts an absence, so it gets the equivalence test against the
        # measured nuisance floor. The margin is the LARGEST floor across the
        # models present: equivalence must hold for the noisiest instrument in
        # the set, not for the quietest.
        #
        # D052: the margin must also come from the option-count stratum H3
        # actually uses. H3 rests on G1-01..G1-05, all four-option, so a margin
        # taken from the binary stratum -- or from an indiscriminate max over
        # every floor in the run, as before D052 -- gates the test on noise it
        # never incurs.
        floor = None
        if h == "H3":
            strata = {nopt[v] for v in spec["vignettes"] if v in nopt}
            if matched:
                per = [f for (m, r) in {(m, r) for m, r in floors}
                       if (f := floor_for(matched, m, r, strata)) is not None]
                floor = max(per) if per else None
            elif floors:
                floor = max(floors.values())
        results[h] = test_family(frames[o], spec, floor=floor)
        results[h]["status"] = "tested"
    results = holm(results)

    rows = []
    for h, r in results.items():
        rows.append({"hypothesis": h, "claim": HYPOTHESES[h]["claim"],
                     "outcome": HYPOTHESES[h]["outcome"],
                     "alternative": HYPOTHESES[h]["alternative"], **r})
    tests = pd.DataFrame(rows)
    write_table(stamp(tests), TABLES / "rq2_hypothesis_tests.csv")

    conf = identity_spcu_merging(deltas, floors)
    if not conf.empty:
        print("\n--- EXPLORATORY: does the model read gender identity as the "
              "sex parameter? ---")
        print("    Group 2, SPCU held FIXED, identity varied. The correct answer "
              "is identical within each pair.")
        ccols = ["model_id", "mean_merging", "n_positive", "n_vignettes",
                 "nuisance_floor", "times_floor", "exceeds_floor"]
        print(conf[ccols].to_string(index=False))
        for _, r in conf.iterrows():
            print(f"    {r['model_id']}: {r['per_vignette']}")
        print("    Not preregistered, outside the Holm family. With 3 vignettes "
              "the finest resolvable p is 0.125, so no p is claimed (D044); read "
              "the effect against the floor.")
        write_table(stamp(conf), TABLES / "rq2b_identity_spcu_merging.csv")

        pt = post_training_contrast(conf, floors)
        if not pt.empty:
            print("\n--- EXPLORATORY RQ2c: data or tuning? base vs its own "
                  "Instruct sibling, same corpus ---")
            pcols = ["base_model", "tuned_model", "merging_base",
                     "merging_tuned", "rq2c_delta", "floor_combined",
                     "times_combined_floor", "exceeds_combined_floor",
                     "base_inside_own_floor", "tuned_exceeds_own_floor"]
            print(pt[pcols].to_string(index=False))
            print("    A positive delta beyond the combined floor means "
                  "post-training increased the merging. It does not rule out a "
                  "data-borne effect that tuning amplified; it does falsify the "
                  "claim that the corpus alone accounts for it.")
            write_table(stamp(pt), TABLES / "rq2c_post_training_contrast.csv")
        else:
            print("    RQ2c: no base/Instruct pair sharing a corpus is scored, "
                  "so the data-vs-tuning contrast could not be run.")

    trend = size_trend(deltas[deltas["outcome"] == "o1"], floors, t2_pmi) \
        if "o1" in frames else pd.DataFrame()
    if not trend.empty:
        write_table(stamp(trend), TABLES / "rq3_size_trend.csv")

    if not args.no_mixed and "o1" in frames:
        me = mixed_effects(frames["o1"])
        write_table(stamp(me), TABLES / "rq2_mixed_effects.csv")

    print("\n--- hypothesis tests (O1, woman - man) ---")
    cols = [c for c in ["hypothesis", "n_vignettes", "n_pairs", "mean_delta",
                        "ci_lo", "ci_hi", "p", "p_holm", "reject_at_fwer_05",
                        "inference_unit", "tost_supported",
                        "status"] if c in tests.columns]
    print(tests[cols].to_string(index=False))
    for _, r in tests.iterrows():
        if isinstance(r.get("scope_caveat"), str) and r["scope_caveat"]:
            print(f"  note on {r['hypothesis']}: {r['scope_caveat']}")
    if not trend.empty:
        print("\n--- RQ3 floor-relative gap by size ---")
        print(trend.to_string(index=False))
        if "spearman_rho" in trend.attrs:
            a = trend.attrs
            print(f"Spearman rho (floor-relative gap vs size) = "
                  f"{a['spearman_rho']:+.3f}, p = {a['spearman_p']:.4f} "
                  f"(exploratory)")
            print(f"  decomposed:  gap vs size   rho = "
                  f"{a['spearman_rho_gap']:+.3f}, p = {a['spearman_p_gap']:.4f}")
            print(f"               floor vs size rho = "
                  f"{a['spearman_rho_floor']:+.3f}, p = "
                  f"{a['spearman_p_floor']:.4f}")
            if abs(a["spearman_rho_floor"]) > abs(a["spearman_rho_gap"]):
                print("  The trend in the composite is carried by the FLOOR, "
                      "not by the gap. Do not report it as bias changing with "
                      "scale; the instrument is changing with scale.")
    print(f"\nwrote tables to {TABLES}")


if __name__ == "__main__":
    main()
