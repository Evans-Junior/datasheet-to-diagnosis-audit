"""Generate the paper/deck figures that had no generator.

Until 2026-11-19 paper_overleaf/figures/fig_*.pdf were hand-exported: nothing
in the repo produced them, nothing checked them against results/tables, and
nothing would have noticed if the tables moved underneath them. src/plots.py
writes a DIFFERENT set (results/figures/rq*.png|pdf), last run 11-02 and now
badly stale, which no artefact reads.

All five paper figures are built here. fig_size was rebuilt on 11-19 (D114);
the other four were verified correct against the tables the same day but still
had no generator, so they could drift exactly as fig_size had. D121.

fig_size was the one a reviewer found three faults in:

  1. the legend keys COLOUR only (red = gap, grey = floor), but the chart also
     uses marker SHAPE to separate families, and nothing explains the shape;
  2. Qwen3's noise floor (0.0177) lands beside the "OLMo 2 7B" text label and
     just above OLMo base's gap (0.0173), so it reads as OLMo's;
  3. OLMo's own floors (0.0097, 0.0099) sit on the Pythia dashed line, so they
     read as Pythia points.

The cause is one chart doing two jobs. Pythia is the only CONTROLLED size
series (one corpus, one recipe, 7 sizes); across all ten models size is
confounded with family and corpus, which the stats file says in as many words.
So the figure is now two panels, and the confound is shown instead of hidden.

Every value is READ from results/tables and asserted against it.

EVERY FIGURE IS DRAWN AT THE WIDTH IT IS PRINTED AT. The paper is two-column
letter at margin=0.85in, so \\textwidth is 6.8in and a figure* spans it. A
figure drawn wider than its slot has its text downscaled by LaTeX, which is how
a 7.4in figure in a 0.48\\linewidth slot ended up rendering 9pt text at 4pt.
SLOT below records each figure's slot in inches; change the .tex and change it
here (D120).

    .venv/bin/python scripts/build_paper_figures.py
"""
import json, sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.stats import spearmanr

from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.provenance import prompt_hash_now   # D121: refuse a stale table set

OUT_PDF = "paper_overleaf/figures"
OUT_PNG = "results/figures/paper"

# Validated with the dataviz skill's checker against a light surface:
# lightness band PASS, chroma floor PASS, CVD separation dE 21.3 (deutan),
# normal-vision dE 27.2, contrast PASS. The previous grey floor failed the
# chroma floor outright, which is the formal name for the reviewer's complaint:
# a near-grey stops doing identity work, and the floor here IS a series.
GAP   = "#AD2E24"
FLOOR = "#2A6FB0"
INK, MUTED, GRID = "#1A1A1A", "#5A5A5A", "#DDDAD6"

plt.rcParams.update({
    "font.family": "serif", "font.size": 11,
    "axes.edgecolor": "#B9B4AE", "axes.linewidth": 0.7,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.labelcolor": INK,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})

SHORT = {"EleutherAI/pythia-70m": "70M", "EleutherAI/pythia-160m": "160M",
         "EleutherAI/pythia-410m": "410M", "EleutherAI/pythia-1b": "1B",
         "EleutherAI/pythia-1.4b": "1.4B", "EleutherAI/pythia-2.8b": "2.8B",
         "EleutherAI/pythia-6.9b": "6.9B",
         "allenai/OLMo-2-1124-7B": "OLMo 2\n7B",
         "allenai/OLMo-2-1124-7B-Instruct": "OLMo 2\n7B Inst",
         "Qwen/Qwen3-8B": "Qwen3\n8B"}
OTHERS = ["allenai/OLMo-2-1124-7B", "allenai/OLMo-2-1124-7B-Instruct",
          "Qwen/Qwen3-8B"]
TICK_B = {"allenai/OLMo-2-1124-7B": "OLMo\n7B",
          "allenai/OLMo-2-1124-7B-Instruct": "OLMo\n7B-I",
          "Qwen/Qwen3-8B": "Qwen3\n8B"}

# Single-line model names. SHORT above wraps for the size chart's x axis, which
# is the only place two lines fit.
ROW = {"EleutherAI/pythia-70m": "Pythia 70M",
       "EleutherAI/pythia-160m": "Pythia 160M",
       "EleutherAI/pythia-410m": "Pythia 410M",
       "EleutherAI/pythia-1b": "Pythia 1B",
       "EleutherAI/pythia-1.4b": "Pythia 1.4B",
       "EleutherAI/pythia-2.8b": "Pythia 2.8B",
       "EleutherAI/pythia-6.9b": "Pythia 6.9B",
       "allenai/OLMo-2-1124-7B": "OLMo 2 7B",
       "allenai/OLMo-2-1124-7B-Instruct": "OLMo 2 7B Inst",
       "Qwen/Qwen3-8B": "Qwen3 8B"}
ROSTER = list(ROW)                      # 7 Pythia ascending, OLMo, OLMo-I, Qwen

# \textwidth = 8.5in - 2*0.85in. A figure* spans it; \linewidth inside one of
# its subfigures is that times the subfigure fraction.
TEXTWIDTH = 6.8
SLOT = {"fig_gate":    0.47 * TEXTWIDTH,
        "fig_merging": 0.47 * TEXTWIDTH,
        "fig_skew":    0.70 * TEXTWIDTH,
        "fig_size":    0.55 * TEXTWIDTH,
        "fig_corpora": 0.42 * TEXTWIDTH}

# A dot or bar inside the floor is not a result. The band is a region, not a
# series, so it takes a tint of FLOOR rather than a fourth hue.
BAND = "#D6E4F2"
NULL = "#9A938C"        # a model whose effect does not clear its own floor


def _dead(ax, keep=("left", "bottom")):
    for sp in ("top", "right", "left", "bottom"):
        if sp not in keep:
            ax.spines[sp].set_visible(False)


def _hgrid(ax):
    ax.xaxis.grid(True, color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def _check(df, n):
    assert len(df) == n, (len(df), n)
    assert df.prompt_hash.nunique() == 1, df.prompt_hash.unique()
    got = str(df.prompt_hash.iloc[0])
    cur = prompt_hash_now()
    assert got == cur, (
        f"table is stale: built from prompt set {got}, current is {cur}. "
        "Rebuild first: sh scripts/run_full_pipeline.sh --no-score")
    return got


# --------------------------------------------------------------------------- #
# The positive control. Each model's gender margin against its own floor.

def fig_gate():
    d = pd.read_csv("results/tables/rq0_positive_control.csv").set_index("model_id")
    PH = _check(d, 10)
    d = d.loc[ROSTER]
    passes = d.gate == "SENSITIVE"
    assert passes.sum() == 3, passes.sum()

    fig, ax = plt.subplots(figsize=(SLOT["fig_gate"], 2.30))
    y = range(len(d))[::-1]                       # first model at the top
    for yi, (mid, r) in zip(y, d.iterrows()):
        ax.barh(yi, 2 * r.nuisance_floor, left=-r.nuisance_floor, height=0.62,
                color=BAND, zorder=1)
    ok = [(yi, r) for yi, (_, r) in zip(y, d.iterrows()) if r.gate == "SENSITIVE"]
    no = [(yi, r) for yi, (_, r) in zip(y, d.iterrows()) if r.gate != "SENSITIVE"]
    ax.scatter([r.mean_margin for _, r in no], [yi for yi, _ in no],
               s=26, color=NULL, zorder=3)
    ax.scatter([r.mean_margin for _, r in ok], [yi for yi, _ in ok],
               s=34, color=GAP, zorder=4)
    for yi, r in ok:                              # only the three that matter
        ax.annotate(f"+{r.mean_margin:.3f}", (r.mean_margin, yi),
                    textcoords="offset points", xytext=(7, -2.5),
                    fontsize=8, color=GAP)

    ax.axvline(0, color="#8C8680", lw=0.8, zorder=2)
    ax.set_yticks(list(y))
    ax.set_yticklabels([ROW[m] for m in d.index], fontsize=8.2)
    ax.tick_params(axis="x", labelsize=8.2)
    ax.set_ylim(-0.7, len(d) - 0.3)
    # An axis label wider than the axes clips at both ends, and at these
    # widths that is easy to do. Keep it short; the caption carries the rest.
    ax.set_xlabel("Change when the sex parameter flips",
                  fontsize=8.2, labelpad=4)
    pad = 0.055 * (d.mean_margin.max() - min(0, d.mean_margin.min()))
    ax.set_xlim(min(-d.nuisance_floor.max(), d.mean_margin.min()) - pad,
                d.mean_margin.max() + pad * 7.5)
    ax.legend(handles=[
        Line2D([], [], ls="", marker="o", ms=5.4, color=GAP,
               label=f"clears its floor ({int(passes.sum())})"),
        Line2D([], [], ls="", marker="o", ms=5.0, color=NULL,
               label=f"inside it ({int((~passes).sum())})")],
        loc="upper right", frameon=False, fontsize=7.0,
        handletextpad=0.4, borderpad=0.15, labelspacing=0.28)
    _dead(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    _hgrid(ax)
    fig.subplots_adjust(left=0.315, right=0.985, top=0.99, bottom=0.185)
    return fig, PH, dict(passes=int(passes.sum()))


# --------------------------------------------------------------------------- #
# Identity read as the sex parameter, in multiples of each model's own floor.

def fig_merging():
    d = pd.read_csv("results/tables/rq2b_identity_spcu_merging.csv")
    PH = _check(d, 10)
    d = d.sort_values("times_floor", ascending=False).reset_index(drop=True)
    clears = d.exceeds_floor.astype(str) == "True"
    assert clears.sum() == 3, clears.sum()

    fig, ax = plt.subplots(figsize=(SLOT["fig_merging"], 2.30))
    y = list(range(len(d)))[::-1]
    ax.barh(y, d.times_floor, height=0.66, zorder=2,
            color=[GAP if c else BAND for c in clears])
    for yi, (_, r) in zip(y, d.iterrows()):
        hit = str(r.exceeds_floor) == "True"
        ax.annotate(f"{r.times_floor:.1f}\u00d7",
                    (r.times_floor if hit else 1.0, yi),
                    textcoords="offset points", xytext=(6, -2.6),
                    fontsize=8, color=GAP if hit else NULL)

    ax.axvline(1, color=INK, lw=1.0, zorder=3)
    ax.annotate("its own floor (1\u00d7)", (1, len(d) - 0.35),
                textcoords="offset points", xytext=(4, 0),
                fontsize=7.6, color=MUTED, va="center")
    ax.set_yticks(y)
    ax.set_yticklabels([ROW[m] for m in d.model_id], fontsize=8.2)
    ax.tick_params(axis="x", labelsize=8.2)
    ax.set_xlim(min(0, d.times_floor.min()) - 0.9, d.times_floor.max() * 1.30)
    ax.set_ylim(-0.7, len(d) + 0.1)
    ax.set_xlabel("Identity effect, in multiples of the floor",
                  fontsize=8.2, labelpad=4)
    _dead(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    _hgrid(ax)
    fig.subplots_adjust(left=0.315, right=0.985, top=0.95, bottom=0.185)
    return fig, PH, dict(clears=int(clears.sum()))


# --------------------------------------------------------------------------- #
# Corpus skew per concept, both corpora. Not prompt-derived, so no hash.

PILE, OLMO = "v4_piletrain_llama", "v4_olmo-mix-1124_llama"


def fig_skew():
    d = pd.read_csv("results/tables/rq1_corpus_skew.csv")
    d = d[d["index"].isin([PILE, OLMO])]
    wide = d.pivot_table(index="concept", columns="index",
                         values=["skew_log2", "powered"], aggfunc="first")
    sk, pw = wide["skew_log2"], wide["powered"]

    # WHICH concepts appear is editorial and stays here in writing: the
    # condition each clinical vignette turns on, one per vignette group, plus
    # strep throat because G4-03 measures the presenting complaint and the
    # diagnosis separately and both are powered. The table also holds drug
    # names, synonyms and the psych:* probes, which belong to other figures.
    # What is NOT editorial is every number below, and the assert makes a
    # concept that stops being measurable fail the build instead of vanishing.
    CONCEPTS = ["pneumonia", "malaria", "asthma", "cellulitis",
                "type 2 diabetes", "prostate", "cervical cancer", "pain",
                "chest pain", "ADHD", "autism", "conjunctivitis",
                "sore throat", "strep throat"]
    missing = [c for c in CONCEPTS if c not in sk.index]
    assert not missing, missing
    sk, pw = sk.loc[CONCEPTS], pw.loc[CONCEPTS]
    unpowered = [c for c in CONCEPTS if not bool(pw.loc[c, OLMO])]
    assert not unpowered, unpowered

    # The Pile point is drawn only where the Pile itself is powered. Where it
    # is not, the concept keeps its OLMo point and the caption says so, rather
    # than being dropped or drawn as if it had been measured.
    order = sk[OLMO].sort_values(ascending=False).index      # stated rule
    n_pile = int(pw.loc[order, PILE].fillna(False).astype(bool).sum())
    assert len(order) == 14, len(order)
    assert abs(sk.loc["cervical cancer", OLMO] - 7.74) < 0.01
    assert abs(sk.loc["prostate", OLMO] + 6.07) < 0.01

    fig, ax = plt.subplots(figsize=(SLOT["fig_skew"], 2.85))
    y = list(range(len(order)))[::-1]
    for yi, c in zip(y, order):
        has = bool(pw.loc[c, PILE]) and pd.notna(sk.loc[c, PILE])
        if has:
            ax.plot([sk.loc[c, PILE], sk.loc[c, OLMO]], [yi, yi],
                    color="#C9C3BD", lw=1.0, zorder=1)
            ax.plot(sk.loc[c, PILE], yi, "o", color=FLOOR, ms=5.6, zorder=3)
        ax.plot(sk.loc[c, OLMO], yi, "s", color=GAP, ms=5.2, zorder=3)

    ax.axvline(0, color="#8C8680", lw=0.8, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(list(order), fontsize=8.6)
    ax.tick_params(axis="x", labelsize=8.6)
    ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlabel(r"Gender skew, $\log_2$(female rate / male rate)",
                  fontsize=8.6, labelpad=4)
    ax.legend(handles=[
        Line2D([], [], ls="", marker="o", ms=5.6, color=FLOOR,
               label=f"the Pile ({n_pile})"),
        Line2D([], [], ls="", marker="s", ms=5.2, color=GAP,
               label=f"OLMo-mix ({len(order)})")],
        loc="lower right", frameon=False, fontsize=8.2,
        handletextpad=0.5, borderpad=0.3, labelspacing=0.4)
    _dead(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    _hgrid(ax)
    fig.subplots_adjust(left=0.255, right=0.99, top=0.99, bottom=0.145)
    return fig, None, dict(concepts=len(order), pile=n_pile)


# --------------------------------------------------------------------------- #
# Do the two corpora disagree enough to attribute a gap to one of them?

def fig_corpora():
    d = pd.read_csv("results/tables/i4_corpus_disagreement.csv")
    c = d[d.common_support.astype(str) == "True"].copy()
    assert len(c) == 8, len(c)
    rho, p = spearmanr(c["piletrain"], c["olmo-mix-1124"])
    assert abs(rho - 0.976) < 0.001, rho

    fig, ax = plt.subplots(figsize=(SLOT["fig_corpora"], 2.52))
    lo = min(c["piletrain"].min(), c["olmo-mix-1124"].min()) - 0.28
    hi = max(c["piletrain"].max(), c["olmo-mix-1124"].max()) + 0.46
    ax.plot([lo, hi], [lo, hi], ls="--", lw=1.0, color="#B4ADA6", zorder=1)
    ax.scatter(c["piletrain"], c["olmo-mix-1124"], s=30, color=GAP, zorder=3)

    # Hand-placed because eight labels in 2.5 inches cannot be auto-placed:
    # each offset is chosen so the text clears its own dot and its neighbours.
    OFF = {"pneumonia": (-6, 7, "right"), "pain": (7, -3, "left"),
           "malaria": (7, -3, "left"), "chest pain": (-7, -3, "right"),
           "ADHD": (7, -3, "left"), "autism": (7, -3, "left")}
    LEAD = {"asthma": (22, -20, "left"),
            "type 2 diabetes": (-50, 21, "left")}
    for _, r in c.iterrows():
        xy = (r["piletrain"], r["olmo-mix-1124"])
        if r.concept in LEAD:
            dx, dy, ha = LEAD[r.concept]
            ax.annotate(r.concept, xy, textcoords="offset points",
                        xytext=(dx, dy), fontsize=7.2, color=INK,
                        ha=ha, va="center",
                        arrowprops=dict(arrowstyle="-", color="#B4ADA6",
                                        lw=0.7, shrinkA=0, shrinkB=3,
                                        connectionstyle="arc3,rad=0.22"))
        else:
            dx, dy, ha = OFF[r.concept]
            ax.annotate(r.concept, xy, textcoords="offset points",
                        xytext=(dx, dy), fontsize=7.2, color=INK, ha=ha)

    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.text(0.035, 0.965, f"Spearman $\\rho$ = {rho:.3f}\n{len(c)} concepts",
            transform=ax.transAxes, va="top", ha="left",
            fontsize=7.8, color=MUTED, linespacing=1.45)
    ax.set_xlabel("Skew in the Pile", fontsize=8.4, labelpad=3)
    ax.set_ylabel("Skew in OLMo-mix", fontsize=8.4, labelpad=3)
    ax.tick_params(labelsize=7.6)
    _dead(ax)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.195, right=0.985, top=0.985, bottom=0.165)
    return fig, None, dict(concepts=len(c), rho=round(float(rho), 4))



def fig_size_trend():
    d = pd.read_csv("results/tables/rq3_size_trend.csv")
    st = json.load(open("results/tables/rq3_size_trend_stats.json"))
    assert len(d) == 10, len(d)
    assert d.prompt_hash.nunique() == 1
    PH = d.prompt_hash.iloc[0]

    py = d[d.family == "pythia"].sort_values("n_params_b")
    assert len(py) == 7, len(py)
    others = d.set_index("model_id").loc[OTHERS]

    # the controlled claim is the within-family one; the all-ten figure is
    # confounded and must not be the number on a size-trend chart
    pf = st["by_family"]["pythia"]
    r_gap, p_gap = pf["spearman_rho_raw_gap"], pf["spearman_p_raw_gap"]
    r_flr, p_flr = pf["spearman_rho_floor"], pf["spearman_p_floor"]

    fig, (a, b) = plt.subplots(
        1, 2, figsize=(SLOT["fig_size"], 2.42), sharey=True,
        gridspec_kw=dict(width_ratios=[2.05, 1.38], wspace=0.07))

    # ---- panel A: the controlled series
    a.plot(py.n_params_b, py.mean_abs_delta, "-o", color=GAP, lw=2.0, ms=6,
           zorder=3, clip_on=False)
    a.plot(py.n_params_b, py.nuisance_floor, "--o", color=FLOOR, lw=2.0, ms=6,
           zorder=3, clip_on=False)
    a.set_xscale("log")
    a.set_xticks(py.n_params_b)
    a.set_xticklabels([SHORT[m] for m in py.model_id], fontsize=7.4)
    a.minorticks_off()
    # 1B and 1.4B are adjacent on a log axis and their labels collide, so the
    # tighter of the two drops to a second row rather than being removed. The
    # drop has to clear a whole line: at the first offset tried the two labels
    # still touched, which the validators cannot see and only a render shows.
    for lab, m in zip(a.get_xticklabels(), py.model_id):
        if SHORT[m] == "1.4B":
            lab.set_y(lab.get_position()[1] - 0.088)
    a.set_xlabel("Pythia: one corpus, one recipe", fontsize=7.8, labelpad=11)
    a.set_ylabel(r"Mean gender gap  $|\Delta|$", fontsize=8.0)
    a.set_title("size varied, all else held", loc="left",
                fontsize=8.2, color=INK, pad=4)
    a.text(0.035, 0.955,
           f"gap vs size   $\\rho$ = {r_gap:+.2f}, p = {p_gap:.3f}\n"
           f"floor vs size  $\\rho$ = {r_flr:+.2f}, p = {p_flr:.2f}",
           transform=a.transAxes, va="top", ha="left", fontsize=7.0,
           color=MUTED, linespacing=1.5)

    # ---- panel B: three single points, each from a different family
    xs = range(len(OTHERS))
    for x, (mid, row) in zip(xs, others.iterrows()):
        b.plot([x, x], [row.nuisance_floor, row.mean_abs_delta],
               color="#C9C3BD", lw=1.4, zorder=1)
        b.plot(x, row.nuisance_floor, "o", color=FLOOR, ms=7, zorder=3)
        b.plot(x, row.mean_abs_delta, "o", color=GAP, ms=7, zorder=3)
        b.annotate(f"{row.mean_abs_delta:.3f}", (x, row.mean_abs_delta),
                   textcoords="offset points", xytext=(0, 7), ha="center",
                   fontsize=7.0, color=GAP)
        b.annotate(f"{row.nuisance_floor:.3f}", (x, row.nuisance_floor),
                   textcoords="offset points", xytext=(0, -14), ha="center",
                   fontsize=7.0, color=FLOOR)
    b.set_xticks(list(xs))
    b.set_xticklabels([TICK_B[m] for m in OTHERS], fontsize=7.0)
    b.set_xlim(-0.6, len(OTHERS) - 0.4)
    b.set_xlabel("one model each", fontsize=7.8)
    b.set_title("size confounded", loc="left",
                fontsize=8.2, color=INK, pad=4)

    for ax in (a, b):
        ax.tick_params(labelsize=7.4)
        ax.yaxis.grid(True, color=GRID, lw=0.7)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    b.spines["left"].set_visible(False)
    b.tick_params(axis="y", length=0)
    a.set_ylim(0, max(d.mean_abs_delta.max(), d.nuisance_floor.max()) * 1.22)

    fig.legend(handles=[
        Line2D([], [], color=GAP, marker="o", lw=2.0, ms=6,
               label=r"mean gender gap $|\Delta|$"),
        Line2D([], [], color=FLOOR, marker="o", lw=2.0, ms=6, ls="--",
               label="that model's own noise floor")],
        loc="lower center", ncol=2, frameon=False, fontsize=7.4,
        bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(left=0.105, right=0.995, top=0.875, bottom=0.335)
    return fig, PH, dict(py=len(py), others=len(others))


# fig_size and fig_corpora are embedded in the deck as PNG by
# scripts/update_slide_figures.py; the rest are paper-only.
BUILD = [("fig_gate", fig_gate, False),
         ("fig_merging", fig_merging, False),
         ("fig_skew", fig_skew, False),
         ("fig_size", fig_size_trend, True),
         ("fig_corpora", fig_corpora, True)]


def main():
    import os
    os.makedirs(OUT_PNG, exist_ok=True)
    for name, fn, png in BUILD:
        fig, PH, info = fn()
        w, _ = fig.get_size_inches()
        assert abs(w - SLOT[name]) < 0.01, (name, w, SLOT[name])
        fig.savefig(f"{OUT_PDF}/{name}.pdf")
        if png:
            fig.savefig(f"{OUT_PNG}/{name}.png", dpi=220)
        plt.close(fig)
        bits = ", ".join(f"{k} {v}" for k, v in info.items())
        print(f"{name}: {bits}" + (f", prompt set {PH}" if PH else ""))
        print(f"  -> {OUT_PDF}/{name}.pdf"
              + (f"  +  {OUT_PNG}/{name}.png" if png else ""))


if __name__ == "__main__":
    sys.exit(main())
