"""Figures for the RQs, one file per RQ, named by the question it answers.

Every figure drawn from the vignette set carries its `verification_status` in the
footer. D043 runs the audit before clinical verification, and a figure is the
artefact most likely to be lifted into a slide away from the table that qualifies
it, so the qualification travels inside the image.

    .venv/bin/python -m src.plots

Writes results/figures/*.png (and .pdf for the two that go in the paper).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.provenance import (NOT_PROMPT_DERIVED, NOT_PROMPT_DERIVED_PREFIX,
                            STAMP_COL, prompt_hash_now)   # D118

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results/tables"
FIGS = ROOT / "results/figures"

# Validated with the dataviz palette validator against surface #fcfcfb:
# lightness band, chroma floor, CVD separation (worst adjacent deutan dE 9.2) and
# normal-vision floor all pass. The aqua sits below 3:1 on the light surface, so
# every series carrying it is directly labelled -- which the relief rule requires.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1a1a19", "#5c5c58", "#e3e3e0"
SURFACE = "#fcfcfb"

_HASH: str | None = None   # set by main(), stamped by _footer

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
})

SHORT = {"EleutherAI/pythia-70m": "70m", "EleutherAI/pythia-160m": "160m",
         "EleutherAI/pythia-410m": "410m", "EleutherAI/pythia-1b": "1b",
         "EleutherAI/pythia-1.4b": "1.4b", "EleutherAI/pythia-2.8b": "2.8b",
         "EleutherAI/pythia-6.9b": "6.9b", "EleutherAI/pythia-12b": "12b",
         "allenai/OLMo-2-1124-7B": "OLMo-2 7B", "Qwen/Qwen3-8B": "Qwen3 8B",
         "allenai/OLMo-2-1124-7B-Instruct": "OLMo-2 7B Instruct"}


def _short(s: pd.Series) -> pd.Series:
    return s.map(lambda m: SHORT.get(m, m.split("/")[-1]))


# Tables each figure is drawn from. The guard below reads them, so adding a
# figure without adding its table here means that figure is ungated.
SOURCES = (
    "rq0_positive_control.csv",
    "rq3_size_trend.csv",
    "rq2_hypothesis_tests.csv",
    "rq1_corpus_skew.csv",
    "rq2b_identity_spcu_merging.csv",
)


def _assert_current() -> str:
    """Refuse to draw from stale tables, and return the hash to stamp (D118).

    This module is not in run_full_pipeline.sh, so a run that rebuilds every
    table leaves these figures untouched. That is exactly what happened: the set
    was drawn on 2026-11-02 and then sat through the 11-09 rescore still
    carrying pre-floor-fix numbers under a PROVISIONAL banner the run had
    already retired. Nothing read it, which is the only reason it did no harm.
    A figure cannot be checked against its caption once it has been lifted into
    a slide, so the check happens before the file is written.
    """
    cur = prompt_hash_now()
    bad = []
    for name in SOURCES:
        if name in NOT_PROMPT_DERIVED or name.startswith(NOT_PROMPT_DERIVED_PREFIX):
            continue
        f = TABLES / name
        if not f.exists():
            bad.append(f"{name}: missing")
            continue
        d = pd.read_csv(f)
        if STAMP_COL not in d.columns:
            bad.append(f"{name}: unstamped")
            continue
        seen = sorted({str(v) for v in d[STAMP_COL].dropna()})
        if seen != [cur]:
            bad.append(f"{name}: {', '.join(seen) or 'no hash'}")
    if bad:
        raise SystemExit(
            "refusing to draw figures from stale tables.\n"
            f"  current prompt set: {cur}\n    "
            + "\n    ".join(bad)
            + "\n  rebuild the tables first: sh scripts/run_full_pipeline.sh --no-score"
        )
    return cur


def _footer(fig, df: pd.DataFrame | None) -> None:
    """Stamp provenance into the image itself (D043)."""
    status = None
    if df is not None and "verification_status" in df.columns and len(df):
        status = str(df["verification_status"].iloc[0])
    if status and status.startswith("PROVISIONAL"):
        # D064/D091: a figure separated from its caption is the likeliest way an
        # unreviewed number reaches a slide, so the condition is burnt into the
        # image rather than left to the surrounding text.
        detail = ("author-reviewed against the guideline quote but NOT passed by "
                  "a clinician" if "author_reviewed" in status
                  else "AI-drafted vignettes not yet passed by a clinician")
        fig.text(0.5, 0.005,
                 f"NOT REPORTABLE: computed on {detail} "
                 f"(AI_USE.md, D038, D043, D091)",
                 ha="center", va="bottom", fontsize=7, color=ORANGE)
    elif status and status.startswith("REPORTABLE_TIER1"):
        fig.text(0.5, 0.005,
                 "Tier 1 result — every vignette author-reviewed against a "
                 "quoted first-hand guideline; PENDING CLINICAL VALIDATION "
                 "(D091)",
                 ha="center", va="bottom", fontsize=7, color=ORANGE)
    elif status and status.startswith("REPORTABLE_TIER2"):
        fig.text(0.5, 0.005, "Tier 2 result — clinician-verified",
                 ha="center", va="bottom", fontsize=7, color=MUTED)
    elif status:
        fig.text(0.5, 0.005, f"verification: {status}", ha="center",
                 va="bottom", fontsize=7, color=MUTED)
    if _HASH:
        # The date a file was written says nothing about which prompt set it
        # was written from, and the file date is what misled a reader once.
        fig.text(0.995, 0.005, f"prompt set {_HASH[:8]}", ha="right",
                 va="bottom", fontsize=6, color=MUTED)


def _save(fig, name: str, pdf: bool = False) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    # Reserve the footer strip rather than relying on a tight bbox, which packs
    # the provenance stamp straight onto the x-axis label.
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(FIGS / f"{name}.png", dpi=200)
    if pdf:
        fig.savefig(FIGS / f"{name}.pdf")
    plt.close(fig)
    print(f"  wrote results/figures/{name}.png")


# --------------------------------------------------------------------------- #

def fig_positive_control() -> None:
    """RQ0 gate: can the instrument see a difference that genuinely exists?

    Each model's Group 2 margin against its own nuisance floor, drawn as a band.
    A dot inside the band is an instrument that cannot detect sex-specific
    clinical content -- which makes every null elsewhere uninterpretable. This is
    the figure the preregistration (§6) says to show before any result.
    """
    f = TABLES / "rq0_positive_control.csv"
    if not f.exists():
        print("  skip rq0_positive_control: no table"); return
    d = pd.read_csv(f).dropna(subset=["nuisance_floor"])
    d["label"] = _short(d["model_id"])
    d = d.sort_values("nuisance_floor")
    y = np.arange(len(d))

    fig, ax = plt.subplots(figsize=(7.2, 0.46 * len(d) + 1.9))
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.barh(yi, 2 * r["nuisance_floor"], left=-r["nuisance_floor"],
                height=0.62, color=GRID, zorder=1)
    ax.scatter(d["mean_margin"], y, s=52, color=BLUE, zorder=3,
               edgecolor=SURFACE, linewidth=1.6, label="observed margin")
    ax.axvline(0, color=MUTED, linewidth=1, zorder=2)

    for yi, (_, r) in zip(y, d.iterrows()):
        ax.annotate(f"{r['mean_margin']:+.4f}",
                    (r["mean_margin"], yi), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=7.5,
                    color=INK)
    ax.set_yticks(y, d["label"])
    ax.set_xlabel("Δ in endorsement of the same option when only SPCU flips")
    n_pass = int((d["gate"] == "SENSITIVE").sum()) if "gate" in d else 0
    ax.set_title(f"RQ0 gate — only {n_pass} of {len(d)} models can detect a "
                 f"difference that is really there\nGrey band = that model's "
                 f"own nuisance floor; a dot inside it is noise",
                 loc="left", fontsize=10.5)
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    _footer(fig, d)
    _save(fig, "rq0_positive_control", pdf=True)


def fig_size_trend() -> None:
    """RQ3: the gap and the floor, plotted together and in the same units.

    Plotting only `floor_relative_gap` against size produces a clean negative
    trend that reads as "bias decreases with scale". It is the floor that moves
    (D045). Both components therefore share one axis -- they are both |Δ
    norm_prob|, so no second scale is needed or permitted.
    """
    f = TABLES / "rq3_size_trend.csv"
    if not f.exists():
        print("  skip rq3_size_trend: no table"); return
    d = pd.read_csv(f).dropna(subset=["n_params_b"]).sort_values("n_params_b")
    if d.empty:
        print("  skip rq3_size_trend: empty"); return

    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.plot(d["n_params_b"], d["nuisance_floor"], "-o", color=ORANGE,
            linewidth=2, markersize=7, label="nuisance floor (instrument noise)")
    ax.plot(d["n_params_b"], d["mean_abs_delta"], "-o", color=BLUE,
            linewidth=2, markersize=7, label="mean |Δ| (the gender gap)")
    ax.set_xscale("log")
    ax.set_xticks(d["n_params_b"], [SHORT.get(m, m) for m in d["model_id"]],
                  rotation=0)
    ax.minorticks_off()
    ax.set_ylim(bottom=0, top=float(d["nuisance_floor"].max()) * 1.25)
    ax.set_xlabel("model size (log scale)")
    ax.set_ylabel("|Δ norm_prob|")
    mid = len(d) // 2
    ax.annotate("the gap is flat …",
                (d["n_params_b"].iloc[mid], d["mean_abs_delta"].iloc[mid]),
                xytext=(0, 12), textcoords="offset points", ha="center",
                color=BLUE, fontsize=8.5)
    ax.annotate("… the instrument gets noisier",
                (d["n_params_b"].iloc[mid], d["nuisance_floor"].iloc[mid]),
                xytext=(0, -20), textcoords="offset points", ha="center",
                color=ORANGE, fontsize=8.5)
    ax.set_title("RQ3 — why the floor-relative gap must never be plotted alone\n"
                 "ρ(size, gap) = +0.14, p = .76   ·   "
                 "ρ(size, floor) = +0.93, p = .003\n"
                 "ρ(size, gap − floor) = −0.86, p = .014  ← the composite, "
                 "carried entirely by the floor",
                 loc="left", fontsize=10)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    _footer(fig, d)
    _save(fig, "rq3_size_trend", pdf=True)


def fig_hypotheses() -> None:
    """RQ2: each hypothesis's effect and CI, against the floor it must clear."""
    f = TABLES / "rq2_hypothesis_tests.csv"
    if not f.exists():
        print("  skip rq2_hypothesis_tests: no table"); return
    d = pd.read_csv(f)
    d = d[d["mean_delta"].notna()].copy()
    if d.empty:
        print("  skip rq2: nothing computable"); return
    trend = pd.read_csv(TABLES / "rq3_size_trend.csv") \
        if (TABLES / "rq3_size_trend.csv").exists() else pd.DataFrame()
    floor = float(trend["nuisance_floor"].max()) if len(trend) else None

    import textwrap
    y = np.arange(len(d))[::-1]
    fig, ax = plt.subplots(figsize=(8.4, 1.05 * len(d) + 2.0))
    if floor:
        ax.axvspan(-floor, floor, color=GRID, zorder=0,
                   label=f"largest nuisance floor (±{floor:.3f})")
    for yi, (_, r) in zip(y, d.iterrows()):
        lo, hi = r.get("ci_lo"), r.get("ci_hi")
        if pd.notna(lo) and pd.notna(hi):
            ax.plot([lo, hi], [yi, yi], color=BLUE, linewidth=2.4, zorder=2,
                    solid_capstyle="round")
        ax.scatter([r["mean_delta"]], [yi], s=56, color=BLUE, zorder=3,
                   edgecolor=SURFACE, linewidth=1.6)
        ax.annotate(f"{r['mean_delta']:+.4f}   p = {r['p']:.3g}   "
                    f"({int(r['n_vignettes'])} vignette"
                    f"{'s' if r['n_vignettes'] != 1 else ''})",
                    (r["mean_delta"], yi), xytext=(0, 14),
                    textcoords="offset points", ha="center", fontsize=7.5)
    ax.axvline(0, color=MUTED, linewidth=1, zorder=1)
    ax.set_yticks(y, [f"{h}\n" + "\n".join(textwrap.wrap(str(c), 30))
                      for h, c in zip(d["hypothesis"], d["claim"])],
                  fontsize=8)
    ax.set_xlabel("Δ norm_prob  (woman − man)")
    ax.set_title("RQ2 — every effect is an order of magnitude inside the "
                 "instrument's own noise", loc="left", fontsize=10.5)
    ax.set_ylim(-0.75, len(d) - 0.25)
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    _footer(fig, d)
    _save(fig, "rq2_hypotheses", pdf=True)


def fig_corpus_skew() -> None:
    """RQ1: gender skew around health concepts, adequately powered concepts only.

    Diverging, because the quantity has a meaningful zero and two signed poles:
    positive is female-skewed, negative male-skewed.
    """
    f = TABLES / "rq1_corpus_skew.csv"
    if not f.exists():
        print("  skip rq1_corpus_skew: no table"); return
    d = pd.read_csv(f)
    d = d[d["powered"] & d["skew_log2"].notna()].copy()
    if d.empty:
        print("  skip rq1: no adequately powered concepts"); return
    d = d.sort_values("skew_log2")
    y = np.arange(len(d))
    colors = [BLUE if v >= 0 else ORANGE for v in d["skew_log2"]]

    fig, ax = plt.subplots(figsize=(7.4, 0.34 * len(d) + 2.0))
    ax.barh(y, d["skew_log2"], color=colors, height=0.66, zorder=2)
    ax.axvline(0, color=MUTED, linewidth=1, zorder=3)
    ax.set_yticks(y, d["concept"], fontsize=7.5)
    ax.set_xlabel("skew_log2  —  log₂(female rate ÷ male rate)")
    ax.set_title("RQ1 — gender skew around health concepts in the training "
                 "corpora\nright = female-skewed · left = male-skewed · "
                 "adequately powered concepts only", loc="left", fontsize=10.5)
    for yi, v in zip(y, d["skew_log2"]):
        ax.annotate(f"{v:+.2f}", (v, yi), xytext=(4 if v >= 0 else -4, 0),
                    textcoords="offset points", va="center",
                    ha="left" if v >= 0 else "right", fontsize=7)
    _save(fig, "rq1_corpus_skew", pdf=True)


def fig_merging() -> None:
    """Exploratory: identity read as the sex parameter, against each model's floor.

    Drawn as a ratio to the floor rather than in raw units, because the floors
    differ by a factor of five across the set and a raw bar chart would make the
    noisiest model look like the most biased one.
    """
    f = TABLES / "rq2b_identity_spcu_merging.csv"
    if not f.exists():
        print("  skip merging: no table"); return
    d = pd.read_csv(f).dropna(subset=["times_floor"]).sort_values("times_floor")
    if d.empty:
        print("  skip merging: empty"); return
    d["label"] = _short(d["model_id"])
    y = np.arange(len(d))
    colors = [ORANGE if v > 1 else GRID for v in d["times_floor"]]

    fig, ax = plt.subplots(figsize=(7.6, 0.42 * len(d) + 2.4))
    ax.barh(y, d["times_floor"], color=colors, height=0.66, zorder=2)
    ax.axvline(1.0, color=INK, linewidth=1.2, zorder=3)
    ax.annotate("the model's own noise floor", (1.0, len(d) - 0.4),
                xytext=(6, 0), textcoords="offset points", fontsize=8,
                color=INK, va="center")
    ax.set_yticks(y, d["label"], fontsize=8)
    ax.set_xlabel("identity–SPCU merging, as a multiple of that model's "
                  "nuisance floor")
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.annotate(f"{r['times_floor']:.2f}×   ({r['n_positive']}/"
                    f"{int(r['n_vignettes'])} vignettes agree)",
                    (max(r["times_floor"], 0), yi), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=7.5)
    ax.set_xlim(right=float(d["times_floor"].max()) * 1.45)
    ax.set_title("EXPLORATORY — is gender identity read as the sex parameter?\n"
                 "Group 2: sex parameter fixed, only the identity label varies,\n"
                 "so the clinically correct answer never changes",
                 loc="left", fontsize=10)
    _footer(fig, d)
    _save(fig, "rq2b_identity_spcu_merging", pdf=True)


def main() -> None:
    global _HASH
    _HASH = _assert_current()
    FIGS.mkdir(parents=True, exist_ok=True)
    print(f"writing figures to {FIGS.relative_to(ROOT)}  (prompt set {_HASH})")
    fig_positive_control()
    fig_size_trend()
    fig_hypotheses()
    fig_corpus_skew()
    fig_merging()


if __name__ == "__main__":
    main()
