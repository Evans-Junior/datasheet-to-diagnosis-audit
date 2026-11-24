"""Render the paper's corpora scatter (Figure A1) at a size a projector can show.

The paper draws this figure 2.86in wide, which is 0.42 of the text width in a
two-column layout. Dropping that file onto a 13.3in slide is the mistake D125
warned about: the type is set for print and a room cannot read it.

So the figure is REDRAWN rather than rescaled. It is the same function, from
scripts/build_paper_figures.py, reading the same table, so the slide and the
appendix cannot disagree about a number. What changes is the physical size and
therefore the type size relative to the plot, plus the resolution, because a
220 dpi file blown up to 6in on a slide is 100 dpi on the wall.

Writes results/figures/slides/fig_corpora_slide.png.

Usage:
    .venv/bin/python scripts/build_slide_corpora_figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib                      # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt        # noqa: E402

OUT = ROOT / "results/figures/slides/fig_corpora_slide.png"
SCALE = 2.15        # 2.86in in print becomes 6.15in on the slide
DPI = 200           # 1230 px across, so about 200 dpi at the size it is shown


def main() -> int:
    import os
    os.chdir(ROOT)                     # the figure functions read relative paths
    import build_paper_figures as B

    fig, _, info = B.fig_corpora()
    w, h = fig.get_size_inches()
    fig.set_size_inches(w * SCALE, h * SCALE)

    # Scaling the canvas does not scale the type, so every text object is
    # scaled by hand. Without this the labels stay at 7.2pt on a 6in figure,
    # which is the same unreadable result as using the print file.
    for ax in fig.axes:
        for t in ([ax.title, ax.xaxis.label, ax.yaxis.label]
                  + ax.get_xticklabels() + ax.get_yticklabels()
                  + list(ax.texts)):
            t.set_fontsize(t.get_fontsize() * SCALE * 0.78)
        for c in ax.collections:                     # the scatter dots
            c.set_sizes([s * SCALE * 1.6 for s in c.get_sizes()])
        for ln in ax.lines:                          # the 45-degree guide
            ln.set_linewidth(ln.get_linewidth() * SCALE * 0.8)
        # The label offsets are in POINTS, set for 7.2pt type. Scaling the
        # type without scaling them pushes every label into its own dot, which
        # is how the first render came out. Annotations carry theirs in xyann.
        import matplotlib.text as mtext
        for ann in ax.texts:
            ann.set_color("#1A1A1A")
            if isinstance(ann, mtext.Annotation) and ann.anncoords == "offset points":
                dx, dy = ann.xyann
                ann.xyann = (dx * SCALE * 0.9, dy * SCALE * 0.9)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    px = int(OUT.stat().st_size / 1024)
    print(f"wrote {OUT.relative_to(ROOT)}  ({px} KB, {info})")
    print(f"  drawn at {w * SCALE:.2f} x {h * SCALE:.2f} in, {DPI} dpi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
