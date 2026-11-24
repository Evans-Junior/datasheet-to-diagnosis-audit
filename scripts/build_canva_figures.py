"""Render the audit's charts as standalone images for Canva, in deck colours.

Two so far: the RQ3 size trend, and the RQ1 corpus skew.

WHY THIS EXISTS SEPARATELY FROM build_paper_figures.py. That script draws
fig_size at the width it is PRINTED at in the two-column paper: 3.74 inches,
serif, 7pt tick labels. Dropped on a slide and scaled up, that figure carries
paper typography onto a projector. This one draws the same two panels at slide
scale in the deck's own palette, so it sits beside the other slides rather than
beside the other figures.

The two-panel shape is kept on purpose and is not a style choice (D114). Pythia
is the only CONTROLLED size series: one corpus, one recipe, seven sizes. Across
all ten models size is confounded with family AND corpus, since the three
largest come from two other families. One chart holding both claims is the chart
that drew three separate reviewer complaints. So the controlled series is panel
A and the confounded points are panel B, and the confound is shown rather than
averaged away.

COLOURS. From deck_src/part1.js, with one documented substitution. The deck's
TEAL (#2E8C9A) fails the dataviz chroma floor at 0.088, which is the formal name
for "reads as grey": a near-grey stops doing identity work, and the floor here is
a series and not a background. #1189A8 is the same hue with enough chroma to
carry it. Checked, not eyeballed:

  light on white   #C2503F, #1189A8   band PASS, chroma PASS, CVD dE 16.3
                                      (protan), normal dE 25.4, contrast PASS
  dark on #0F3A44  #D2695A, #1189A8   band PASS, chroma PASS, CVD dE 11.5
                                      (protan), normal dE 24.5, contrast PASS

Every value is READ from results/tables and the table is refused if it was built
from a different prompt set than the one on disk now.

    .venv/bin/python scripts/build_canva_size_figure.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from build_paper_figures import (SHORT, TICK_B, OTHERS, PILE, OLMO,
                                 _check)                      # noqa: E402

OUT = ROOT / "results/figures/canva"

# The deck's body font, which lives inside PowerPoint rather than in the system
# font list. Without this the figure renders in DejaVu and stops matching the
# slides, which is the one thing it exists to do.
DFONTS = Path("/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts")
FAMILY = "DejaVu Sans"
for stem in ("Calibri.ttf", "Calibrib.ttf"):
    if (DFONTS / stem).exists():
        font_manager.fontManager.addfont(str(DFONTS / stem))
        FAMILY = "Calibri"

# ------------------------------------------------------------- deck palette --
INK, MUT, TINT = "#0F3A44", "#5A7883", "#EEF4F4"

THEMES = {
    "light": dict(bg="#FFFFFF", gap="#C2503F", floor="#1189A8",
                  ink=INK, mut=MUT, grid="#DCE7E9", link="#C9D6D9"),
    "dark":  dict(bg=INK, gap="#D2695A", floor="#1189A8",
                  ink="#FFFFFF", mut="#A8C0C7", grid="#24525C", link="#2E5B65"),
}

W, H, DPI = 12.0, 5.4, 200          # 2400 x 1080 px, drops onto any 16:9 slide
SKEW_W, SKEW_H = 12.0, 6.4          # taller: fourteen rows need the height


def draw(t: dict):
    d = __import__("pandas").read_csv(ROOT / "results/tables/rq3_size_trend.csv")
    st = json.load(open(ROOT / "results/tables/rq3_size_trend_stats.json"))
    PH = _check(d, 10)

    py = d[d.family == "pythia"].sort_values("n_params_b")
    assert len(py) == 7, len(py)
    others = d.set_index("model_id").loc[OTHERS]

    # The controlled claim is the within-family one. The all-ten rho is
    # confounded and must not be the number printed on a size-trend chart.
    pf = st["by_family"]["pythia"]
    r_gap, p_gap = pf["spearman_rho_raw_gap"], pf["spearman_p_raw_gap"]
    r_flr, p_flr = pf["spearman_rho_floor"], pf["spearman_p_floor"]

    plt.rcParams.update({
        "font.family": FAMILY, "font.size": 14,
        "axes.edgecolor": t["grid"], "axes.linewidth": 0.9,
        "xtick.color": t["mut"], "ytick.color": t["mut"],
        "text.color": t["ink"], "axes.labelcolor": t["ink"],
        "figure.facecolor": t["bg"], "savefig.facecolor": t["bg"],
        "axes.facecolor": t["bg"],
    })

    fig, (a, b) = plt.subplots(
        1, 2, figsize=(W, H), sharey=True,
        gridspec_kw=dict(width_ratios=[2.05, 1.30], wspace=0.06))

    # ---- panel A: size varied, everything else held -----------------------
    a.plot(py.n_params_b, py.mean_abs_delta, "-o", color=t["gap"],
           lw=2.8, ms=10, zorder=3, clip_on=False)
    a.plot(py.n_params_b, py.nuisance_floor, "--o", color=t["floor"],
           lw=2.8, ms=10, zorder=3, clip_on=False)
    a.set_xscale("log")
    a.set_xticks(py.n_params_b)
    a.set_xticklabels([SHORT[m] for m in py.model_id], fontsize=12.5)
    a.minorticks_off()
    # 1B and 1.4B are adjacent on a log axis and collide, so the tighter of the
    # two drops a whole line rather than being removed.
    for lab, m in zip(a.get_xticklabels(), py.model_id):
        if SHORT[m] == "1.4B":
            lab.set_y(lab.get_position()[1] - 0.075)
    a.set_xlabel("Pythia: one corpus, one recipe, seven sizes",
                 fontsize=13, labelpad=16, color=t["mut"])
    a.set_ylabel("Mean gender gap  |Δ|", fontsize=14)
    a.set_title("size varied, everything else held", loc="left",
                fontsize=15, color=t["ink"], pad=10, fontweight="bold")
    a.text(0.035, 0.95,
           f"gap vs size    ρ = {r_gap:+.2f},  p = {p_gap:.3f}\n"
           f"floor vs size  ρ = {r_flr:+.2f},  p = {p_flr:.2f}",
           transform=a.transAxes, va="top", ha="left", fontsize=12.5,
           color=t["mut"], linespacing=1.6)

    # Selective direct labels: the two ends of each line, which is what the
    # claim is about. A number on all fourteen points would be noise.
    #
    # The gap label always sits above its point and the floor label always
    # below, the same convention panel B uses. At 70M the two series are
    # 0.0058 and 0.0058, so a shared offset puts one label exactly on top of
    # the other and the render shows one number where there are two.
    for col, vals, dy in ((t["gap"], py.mean_abs_delta, 14),
                          (t["floor"], py.nuisance_floor, -26)):
        for x, y in ((py.n_params_b.iloc[0], vals.iloc[0]),
                     (py.n_params_b.iloc[-1], vals.iloc[-1])):
            a.annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                       xytext=(0, dy), ha="center", fontsize=12, color=col,
                       fontweight="bold")

    # ---- panel B: one model each, size confounded with family -------------
    xs = range(len(OTHERS))
    for x, (mid, row) in zip(xs, others.iterrows()):
        b.plot([x, x], [row.nuisance_floor, row.mean_abs_delta],
               color=t["link"], lw=2.0, zorder=1)
        b.plot(x, row.nuisance_floor, "o", color=t["floor"], ms=11, zorder=3)
        b.plot(x, row.mean_abs_delta, "o", color=t["gap"], ms=11, zorder=3)
        b.annotate(f"{row.mean_abs_delta:.3f}", (x, row.mean_abs_delta),
                   textcoords="offset points", xytext=(0, 13), ha="center",
                   fontsize=12, color=t["gap"], fontweight="bold")
        b.annotate(f"{row.nuisance_floor:.3f}", (x, row.nuisance_floor),
                   textcoords="offset points", xytext=(0, -24), ha="center",
                   fontsize=12, color=t["floor"], fontweight="bold")
    b.set_xticks(list(xs))
    b.set_xticklabels([TICK_B[m] for m in OTHERS], fontsize=12.5)
    b.set_xlim(-0.65, len(OTHERS) - 0.35)
    b.set_xlabel("one model each, three different corpora",
                 fontsize=13, labelpad=16, color=t["mut"])
    b.set_title("size confounded with family", loc="left",
                fontsize=15, color=t["ink"], pad=10, fontweight="bold")

    for ax in (a, b):
        ax.tick_params(labelsize=12.5)
        ax.yaxis.grid(True, color=t["grid"], lw=1.0)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    b.spines["left"].set_visible(False)
    b.tick_params(axis="y", length=0)
    a.set_ylim(0, max(d.mean_abs_delta.max(), d.nuisance_floor.max()) * 1.26)

    fig.legend(handles=[
        Line2D([], [], color=t["gap"], marker="o", lw=2.8, ms=10,
               label="mean gender gap  |Δ|"),
        Line2D([], [], color=t["floor"], marker="o", lw=2.8, ms=10, ls="--",
               label="that model's own noise floor")],
        loc="lower center", ncol=2, frameon=False, fontsize=13.5,
        labelcolor=t["ink"], bbox_to_anchor=(0.5, 0.005))
    fig.subplots_adjust(left=0.085, right=0.995, top=0.90, bottom=0.30)
    return fig, PH


def draw_skew(t: dict):
    """The corpus skew chart: which illnesses the training text genders.

    WHICH CONCEPTS APPEAR IS EDITORIAL and stays here in writing, exactly as it
    does in build_paper_figures.fig_skew: the condition each vignette turns on,
    one per group, plus strep throat because G4-03 measures the presenting
    complaint and the diagnosis separately. The table also holds drug names,
    synonyms and the psych probes, which belong to other charts. What is NOT
    editorial is every number, and the assert makes a concept that stops being
    measurable fail the run instead of quietly vanishing from the picture.

    THE PILE POINT IS DRAWN ONLY WHERE THE PILE IS POWERED. Where it is not, the
    row keeps its olmo-mix point and the legend says how many Pile points there
    are, rather than drawing an unmeasured point as though it were a zero.
    """
    import pandas as pd
    d = pd.read_csv(ROOT / "results/tables/rq1_corpus_skew.csv")
    d = d[d["index"].isin([PILE, OLMO])]
    wide = d.pivot_table(index="concept", columns="index",
                         values=["skew_log2", "powered"], aggfunc="first")
    sk, pw = wide["skew_log2"], wide["powered"]

    CONCEPTS = ["pneumonia", "malaria", "asthma", "cellulitis",
                "type 2 diabetes", "prostate", "cervical cancer", "pain",
                "chest pain", "ADHD", "autism", "conjunctivitis",
                "sore throat", "strep throat"]
    missing = [c for c in CONCEPTS if c not in sk.index]
    assert not missing, missing
    sk, pw = sk.loc[CONCEPTS], pw.loc[CONCEPTS]
    unpowered = [c for c in CONCEPTS if not bool(pw.loc[c, OLMO])]
    assert not unpowered, unpowered
    # The two calibration points, asserted because the whole chart is only
    # readable if these two come out the way anatomy says they must.
    assert abs(sk.loc["cervical cancer", OLMO] - 7.74) < 0.01
    assert abs(sk.loc["prostate", OLMO] + 6.07) < 0.01

    order = sk[OLMO].sort_values(ascending=False).index     # stated rule
    n_pile = int(pw.loc[order, PILE].fillna(False).astype(bool).sum())

    plt.rcParams.update({
        "font.family": FAMILY, "font.size": 14,
        "axes.edgecolor": t["grid"], "axes.linewidth": 0.9,
        "xtick.color": t["mut"], "ytick.color": t["mut"],
        "text.color": t["ink"], "axes.labelcolor": t["ink"],
        "figure.facecolor": t["bg"], "savefig.facecolor": t["bg"],
        "axes.facecolor": t["bg"],
    })
    fig, ax = plt.subplots(figsize=(SKEW_W, SKEW_H))
    y = list(range(len(order)))[::-1]
    for yi, c in zip(y, order):
        v = sk.loc[c, OLMO]
        has = bool(pw.loc[c, PILE]) and pd.notna(sk.loc[c, PILE])
        if has:
            ax.plot([sk.loc[c, PILE], v], [yi, yi], color=t["link"], lw=2.2,
                    zorder=1)
            ax.plot(sk.loc[c, PILE], yi, "o", color=t["floor"], ms=11, zorder=3)
        ax.plot(v, yi, "s", color=t["gap"], ms=10, zorder=3)
        # Hang the label off whichever of the two points is further out, not
        # off the olmo-mix one. On strep throat and pneumonia the Pile sits
        # outside olmo-mix, so a fixed offset printed the number on top of the
        # blue dot. Only the render shows this.
        outer = v
        if has:
            p = sk.loc[c, PILE]
            outer = max(v, p) if v >= 0 else min(v, p)
        ax.annotate(f"{v:+.2f}", (outer, yi), textcoords="offset points",
                    xytext=(16 if v >= 0 else -16, 0),
                    ha="left" if v >= 0 else "right", va="center",
                    fontsize=12, fontweight="bold", color=t["gap"])

    ax.axvline(0, color=t["mut"], lw=1.2, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(list(order), fontsize=13)
    ax.set_ylim(-0.9, len(order) - 0.2)
    ax.set_xlim(-8.6, 10.2)
    ax.set_xlabel("Gender skew,  log\u2082(female rate / male rate)",
                  fontsize=13, labelpad=10, color=t["mut"])
    # The sign is the thing most easily misread, so it is written on the chart
    # rather than left to the axis label.
    # Anchored to where zero actually falls, so the two captions sit either
    # side of the line they describe rather than either side of the midpoint.
    lo, hi = ax.get_xlim()
    zero = (0 - lo) / (hi - lo)
    ax.annotate("more often written about women  \u2192", xy=(zero + 0.012, 1.012),
                xycoords="axes fraction", ha="left", va="bottom",
                fontsize=12.5, color=t["gap"], fontweight="bold")
    ax.annotate("\u2190  more often written about men", xy=(zero - 0.012, 1.012),
                xycoords="axes fraction", ha="right", va="bottom",
                fontsize=12.5, color=t["floor"], fontweight="bold")
    ax.legend(handles=[
        Line2D([], [], ls="", marker="s", ms=10, color=t["gap"],
               label=f"olmo-mix, OLMo 2's corpus ({len(order)} concepts)"),
        Line2D([], [], ls="", marker="o", ms=11, color=t["floor"],
               label=f"the Pile, Pythia's corpus ({n_pile} powered)")],
        loc="lower right", frameon=False, fontsize=12.5,
        labelcolor=t["ink"], handletextpad=0.6, borderpad=0.6, labelspacing=0.6)
    ax.xaxis.grid(True, color=t["grid"], lw=1.0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=13)
    ax.tick_params(axis="x", labelsize=12)
    fig.subplots_adjust(left=0.155, right=0.985, top=0.935, bottom=0.095)
    return fig, None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name, t in THEMES.items():
        fig, PH = draw(t)
        p = OUT / f"size_trend_{name}.png"
        fig.savefig(p, dpi=DPI)
        made.append(p)
        if name == "light":
            # Same drawing with no background, for a Canva slide that is not
            # white. The ink text still needs a pale surface under it.
            q = OUT / "size_trend_light_transparent.png"
            fig.savefig(q, dpi=DPI, transparent=True)
            made.append(q)
        plt.close(fig)

    for name, t in THEMES.items():
        fig, _ = draw_skew(t)
        p = OUT / f"corpus_skew_{name}.png"
        fig.savefig(p, dpi=DPI)
        made.append(p)
        if name == "light":
            q = OUT / "corpus_skew_light_transparent.png"
            fig.savefig(q, dpi=DPI, transparent=True)
            made.append(q)
        plt.close(fig)

    for p in made:
        print(f"  -> {p.relative_to(ROOT)}")
    print(f"prompt set {PH}, {DPI} dpi; size trend "
          f"{int(W * DPI)} x {int(H * DPI)} px, corpus skew "
          f"{int(SKEW_W * DPI)} x {int(SKEW_H * DPI)} px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
