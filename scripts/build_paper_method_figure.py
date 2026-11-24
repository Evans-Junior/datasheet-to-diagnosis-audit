"""Draw the three-audit method diagram as a print figure.

The project already had this diagram, but only as a 16:9 presentation slide
(paper_overleaf/figures/fig_pipeline.png): white text on a dark red field, at
1920x1080. That cannot go into a two-column paper, and it still carried two
things the study did not do (expert interviews, a Dolma-era corpus label).

This redraws it at the width it is printed at, in the paper's own palette, with
the content the paper actually reports. The teaching assistant's note was that
this diagram, more than any paragraph, is what made the project legible to a
reader coming to it cold, so it belongs in the paper and near the front of it.

EVERY FIGURE IS DRAWN AT THE WIDTH IT IS PRINTED AT (D120). \textwidth is 6.8in
on this geometry and this is a figure*, so SLOT is 6.8.

    .venv/bin/python scripts/build_paper_method_figure.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = ["paper_overleaf/figures/fig_method.pdf",
       "paper_overleaf_v2/figures/fig_method.pdf",
       "results/figures/paper/fig_method.png"]

DARKRED, ROSE, REDT = "#8B0000", "#F8EBEB", "#FBE2DF"
EDGE, INK, MUTED = "#D9BFBF", "#1A1A1A", "#4A4A4A"

plt.rcParams.update({
    "font.family": "serif", "text.color": INK,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})

SLOT = 6.8
FIG_H = 3.42

# ---------------------------------------------------------------- content
# (column header, research questions, [(title, detail), ...])
COLS = [
    ("OUTPUT AUDIT", "RQ2, RQ3, RQ5", [
        ("25 clinical vignettes",
         "four groups; the correct answer\nquoted from a named guideline"),
        ("624 prompts",
         "sex parameter held fixed,\nidentity label varied"),
        ("10 models scored",
         "17,280 answer options, against two\nfloors and a positive control"),
    ]),
    ("DATA AUDIT", "RQ1", [
        ("Two open corpora",
         "the Pile (Pythia) and\nOLMo-mix (OLMo 2)"),
        ("Exact-phrase counts",
         "infini-gram, over matched\nillness-narration templates"),
        ("Skew per clinical concept",
         "log₂(female rate / male rate),\ncompared concept to concept"),
    ]),
    ("DOCUMENTATION AUDIT", "RQ6", [
        ("10 dataset cards and reports",
         "for the corpora and the models\nthat were actually queried"),
        ("A 30-term search",
         "sex, gender and health terms,\nper document"),
        ("What each one discloses",
         "whether gender was measured, and\nwhether health use was declared"),
    ]),
]

SYNTH = ("Does the chain hold together?",
         "Does a model's gap follow the skew in its own corpus rather than another's (RQ4),\n"
         "and did the documentation of that corpus disclose the risk to anyone deploying it?")

# ---------------------------------------------------------------- layout
fig = plt.figure(figsize=(SLOT, FIG_H))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

CW, GAP = 0.313, 0.0305
LEFTS = [0.0, CW + GAP, 2 * (CW + GAP)]
ROW_TOP, BH, VGAP = 0.875, 0.166, 0.062
TOPS = [ROW_TOP - i * (BH + VGAP) for i in range(3)]

def box(x, y, w, h, fc, ec, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y - h), w, h,
                 boxstyle="round,pad=0,rounding_size=0.012",
                 linewidth=lw, facecolor=fc, edgecolor=ec, mutation_aspect=SLOT / FIG_H))

def arrow(x, y0, y1):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>",
                 mutation_scale=7, linewidth=0.8, color=MUTED, shrinkA=0, shrinkB=0))

for li, (head, rqs, steps) in zip(LEFTS, COLS):
    cx = li + CW / 2
    ax.text(cx, 0.972, head, ha="center", va="center",
            fontsize=8.2, weight="bold", color=DARKRED)
    ax.text(cx, 0.925, rqs, ha="center", va="center", fontsize=7.0,
            style="italic", color=MUTED)
    for ri, (title, detail) in enumerate(steps):
        top = TOPS[ri]
        box(li, top, CW, BH, ROSE, EDGE)
        ax.text(cx, top - 0.044, title, ha="center", va="center",
                fontsize=7.8, weight="bold")
        ax.text(cx, top - 0.111, detail, ha="center", va="center",
                fontsize=7.0, color=MUTED, linespacing=1.38)
        if ri < 2:
            arrow(cx, top - BH, TOPS[ri + 1] + 0.004)
    arrow(cx, TOPS[2] - BH, 0.206)

# ---------------------------------------------------------------- synthesis
box(0.0, 0.200, 1.0, 0.190, REDT, DARKRED, lw=1.0)
ax.text(0.5, 0.157, SYNTH[0], ha="center", va="center",
        fontsize=8.0, weight="bold", color=DARKRED)
ax.text(0.5, 0.072, SYNTH[1], ha="center", va="center",
        fontsize=7.2, color=INK, linespacing=1.45)

for path in OUT:
    import os
    if not os.path.isdir(os.path.dirname(path)):
        continue
    fig.savefig(path, dpi=300 if path.endswith(".png") else None,
                bbox_inches=None, pad_inches=0)
    print("wrote", path)
