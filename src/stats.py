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
    "H1": {"vignettes": ["G3-04", "G3-05"], "outcome": "o1",
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
    "H3": {"vignettes": ["G1-01", "G1-02", "G1-03", "G1-04", "G1-05",
                         "G4-01", "G4-02", "G4-03"], "outcome": "o1",
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
        if "pmi_floor_max" not in t3:
            continue
        floors[(d["model"], d.get("revision", "main"))] = float(t3["pmi_floor_max"])
    if not floors:
        print("WARNING: no per-model floor files found. RQ3 will be skipped; "
              "run scripts.validate_instrument per model (D035).")
    return floors


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
    dup = d["prompt_id"].duplicated().sum()
    if dup:
        raise RuntimeError(
            f"{outcome}: {dup} prompts match more than one option. The "
            f"reference/target string is not unique within its option set.")
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
    p_boot = cluster_boot_p(sub, spec["alternative"])
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
        scope = (f"only {n_vig} clusters: the bootstrap tail is not resolvable, "
                 f"treat a small p as directional evidence and read the CI, not "
                 f"the p-value")
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


def size_trend(deltas: pd.DataFrame,
               floors: dict[tuple[str, str], float]) -> pd.DataFrame:
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
        rows.append({"model_id": mid, "revision": rev,
                     "n_params_b": n_params(mid),
                     "mean_abs_delta": mean_abs,
                     "nuisance_floor": floor,
                     "floor_relative_gap": mean_abs - floor,
                     "exceeds_floor": mean_abs > floor,
                     "n_pairs": int(len(g))})
    out = pd.DataFrame(rows)
    if len(out) >= 3 and out["n_params_b"].notna().all():
        # Exploratory, and Spearman because the prereg states no functional form
        # for the size relationship -- only RQ3's question of whether it changes.
        r = sps.spearmanr(out["n_params_b"], out["floor_relative_gap"])
        out.attrs["spearman_rho"] = float(r.statistic)
        out.attrs["spearman_p"] = float(r.pvalue)
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
    args = ap.parse_args()

    TABLES.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    floors = load_floors()
    targets = load_target_options()

    # Exclusions fixed in §7. Applied before anything is estimated, and counted
    # so the write-up can state how many prompts each rule removed.
    n0 = len(raw)
    if "placeholder_text" in raw.columns:
        raw = raw[raw["placeholder_text"] != True]            # noqa: E712
    print(f"exclusions removed {n0 - len(raw):,} of {n0:,} option rows")

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
    deltas.to_csv(TABLES / "rq2_deltas.csv", index=False)

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
        floor = max(floors.values()) if (h == "H3" and floors) else None
        results[h] = test_family(frames[o], spec, floor=floor)
        results[h]["status"] = "tested"
    results = holm(results)

    rows = []
    for h, r in results.items():
        rows.append({"hypothesis": h, "claim": HYPOTHESES[h]["claim"],
                     "outcome": HYPOTHESES[h]["outcome"],
                     "alternative": HYPOTHESES[h]["alternative"], **r})
    tests = pd.DataFrame(rows)
    tests.to_csv(TABLES / "rq2_hypothesis_tests.csv", index=False)

    trend = size_trend(deltas[deltas["outcome"] == "o1"], floors) \
        if "o1" in frames else pd.DataFrame()
    if not trend.empty:
        trend.to_csv(TABLES / "rq3_size_trend.csv", index=False)

    if not args.no_mixed and "o1" in frames:
        me = mixed_effects(frames["o1"])
        me.to_csv(TABLES / "rq2_mixed_effects.csv", index=False)

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
            print(f"Spearman rho = {trend.attrs['spearman_rho']:.3f}, "
                  f"p = {trend.attrs['spearman_p']:.4f} (exploratory)")
    print(f"\nwrote tables to {TABLES}")


if __name__ == "__main__":
    main()
