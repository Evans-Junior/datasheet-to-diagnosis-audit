"""Redraw the lower band of the 24-arms slide.

Two things were wrong with it:

  1. it showed no output at all, so "17,280 scored option rows" arrived with
     nothing to attach it to. The audience could not see that the model's answer
     is a softmax over that vignette's own option set.
  2. the arithmetic did not multiply out. It read 24 x 25 -> 624 x 10 -> 17,280,
     but 24 x 25 is 600, and 624 x 10 is 6,240. The missing factor is the option
     set, which differs per vignette, and the missing 24 arms belong to G3-02,
     which also varies a clinical cue.

So the band now carries, per group, the shape of the option set and the softmax
we expect from it, and then the arithmetic in the order it actually happens.
Every count is READ from data/vignettes/vignettes.csv and templates.yaml. D109.

Run from the project root.
"""
import sys, collections
import yaml
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
ANCHOR_SHAPE = "m-rowax"          # unique to the arms slide

INK, MUTED = RGBColor(0x1A,0x1A,0x1A), RGBColor(0x70,0x70,0x70)
GREY = RGBColor(0x89,0x89,0x89)
WHITE, CREAM = RGBColor(0xFF,0xFF,0xFF), RGBColor(0xF8,0xEB,0xEB)
ROSE = RGBColor(0xC8,0x62,0x62)
ACCENT = RGBColor(0x8D,0x00,0x00)
RED = RGBColor(0xE8,0x37,0x2C)
RED_TINT = RGBColor(0xFB,0xE2,0xDF)
HAIR = RGBColor(0xDC,0xC2,0xC2)
SLATE = RGBColor(0x3F,0x4C,0x5A)
SLATE_L = RGBColor(0xC3,0xCC,0xD4)
DISPLAY, HEAD, HEADB, BODY = "Rye", "Montserrat Medium", "Montserrat Bold", "Poppins"
BODYB = "Poppins Bold"

# ------------------------------------------------------------------ facts
tpl = yaml.safe_load(open("data/vignettes/templates.yaml"))
trows = tpl["templates"] if isinstance(tpl, dict) and "templates" in tpl else tpl
NOPT = {r["id"]: len(r["answer_options"]) for r in trows}
OPTS = {r["id"]: r["answer_options"] for r in trows}

v = pd.read_csv("data/vignettes/vignettes.csv")
ready = v[v.analysis_ready == True].copy()
ready["nopt"] = ready.vignette_id.map(NOPT)
assert ready.nopt.notna().all()

N_PROMPTS = len(ready)
N_VIG = ready.vignette_id.nunique()
N_ROWS_PER_MODEL = int(ready.nopt.sum())
arms = ready.groupby("vignette_id").size()
BASE_ARMS = int(arms.mode().iloc[0])
EXTRA = arms[arms != BASE_ARMS]
assert len(EXTRA) == 1, EXTRA.to_dict()
EXTRA_ID = EXTRA.index[0]
EXTRA_N = int(EXTRA.iloc[0])

import json, glob
N_MODELS = len(glob.glob("results/tables/rq0_instrument_validation__*.json"))
TOTAL = N_ROWS_PER_MODEL * N_MODELS
assert BASE_ARMS * (N_VIG - 1) + EXTRA_N == N_PROMPTS, "arm arithmetic does not close"
print(f"{N_PROMPTS} prompts over {N_VIG} vignettes ({BASE_ARMS} arms each, "
      f"{EXTRA_N} for {EXTRA_ID})")
print(f"{N_ROWS_PER_MODEL} option rows per model x {N_MODELS} models = {TOTAL}")

G = {}
for g, sub in ready.groupby("group"):
    counts = collections.Counter(NOPT[i] for i in sorted(set(sub.vignette_id)))
    G[int(g)] = dict(vignettes=sub.vignette_id.nunique(),
                     prompts=len(sub),
                     rows=int(sub.nopt.sum()),
                     mix=dict(sorted(counts.items())))
assert sum(d["rows"] for d in G.values()) == N_ROWS_PER_MODEL
for g, d in sorted(G.items()):
    print(f"  group {g}: {d}")

# the modal option count per group, and a representative option set to draw
MODAL = {g: max(d["mix"].items(), key=lambda kv: kv[1])[0] for g, d in G.items()}
EG_SET = {}
for g in G:
    ids = sorted({i for i in set(ready[ready.group == g].vignette_id)
                  if NOPT[i] == MODAL[g]})
    EG_SET[g] = OPTS[ids[0]]

def mixtext(g):
    """'Yes | No on 8, a 4-way on 3' - read from the data, never typed."""
    mix = G[g]["mix"]
    parts = []
    for n, c in sorted(mix.items()):
        parts.append(f"{c} \u00d7 {n} options")
    return "  ·  ".join(parts)

ROWSPEC = {
    1: "four named treatments, one of them the guideline's",
    2: "Yes or No, and the guideline's own answer FLIPS with the sex parameter",
    3: "refer or not, and on one vignette how urgently",
    4: "test or treat, where no disparity is documented anywhere",
}
GCOL = {1: SLATE, 2: ACCENT, 3: SLATE, 4: SLATE}

# ------------------------------------------------------------------ the slide
prs = Presentation(DECK)
hits = [i for i, sl in enumerate(prs.slides)
        if any(sh.name == ANCHOR_SHAPE for sh in sl.shapes)]
assert len(hits) == 1, hits
IDX = hits[0]
s = prs.slides[IDX]
print("arms slide is at position", IDX + 1)

# keep the circled 24, the header and the identity matrix; the note moves up
note = next(sh for sh in s.shapes if sh.name == "m-note")
NOTE_TEXT = note.text_frame.text
KEEP_BELOW = 6.60
dropped = 0
for sh in list(s.shapes):
    if Emu(sh.top).inches >= KEEP_BELOW:
        sh._element.getparent().remove(sh._element)
        dropped += 1
print("shapes dropped from the lower band:", dropped)
assert dropped >= 20, dropped

def E(x): return Inches(x)

def text(x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spc=None,
         name=None):
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    if name: tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    first = True
    for runs in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if spc is not None: p.space_after = Pt(spc)
        for t, sz, bo, col, fnt in runs:
            r = p.add_run(); r.text = t
            r.font.size = Pt(sz); r.font.bold = bo; r.font.name = fnt
            r.font.color.rgb = col
    return tb

def box(x, y, w, h, fill, line=None, lw=1.0, rad=0.08,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=None):
    sh = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if name: sh.name = name
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try: sh.adjustments[0] = rad
        except Exception: pass
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False; sh.text_frame.text = ""
    return sh

def rule(x, y, w, col=HAIR, lw=1.0):
    ln = s.shapes.add_connector(1, E(x), E(y), E(x + w), E(y))
    ln.line.color.rgb = col; ln.line.width = Pt(lw)

L, R = 0.70, 19.30
text(3.75, 6.54, 11.70, 0.30, [[(NOTE_TEXT, 12, False, GREY, BODY)]], name="m-note")
rule(L, 6.88, R - L, ROSE)
text(L, 6.98, R - L, 0.28,
     [[("AND WHAT THE MODEL IS ASKED TO PRODUCE  ·  A SOFTMAX OVER THAT "
        "VIGNETTE'S OWN OPTION SET, WHICH IS WHERE THE LAST FACTOR COMES FROM",
        13, True, ROSE, HEAD)]])

# ---------------------------------------------------- per-group output table
TY, PITCH, RH = 7.34, 0.58, 0.54
# The "WHAT WE EXPECT TO SEE" column was removed on review (D115): it
# predicted the result on a methods slide, and the expectation per group is
# already carried by the group chips on the design slide.
XG, XS, XO, XR = L, 2.14, 3.96, 10.60
WR = 1.20
HDRS = [(XG, 1.36, "GROUP", PP_ALIGN.LEFT),
        (XS, 1.74, "THE OUTPUT", PP_ALIGN.CENTER),
        (XO, 6.30, "WHAT THE SOFTMAX IS OVER", PP_ALIGN.LEFT),
        (XR, WR, "OPTION ROWS", PP_ALIGN.RIGHT)]
for x, w, lab, al in HDRS:
    text(x, TY, w, 0.26, [[(lab, 10.5, True, SLATE, HEAD)]], align=al)
rule(L, TY + 0.30, XR + WR - L, HAIR)

# an illustrative softmax: one option carries the mass, the rest share the
# remainder. The SHAPE is the point, so the heights are drawn, not measured.
SHAPE_H = 0.40
for k, g in enumerate(sorted(G)):
    y = TY + 0.40 + k * PITCH
    d = G[g]
    col = GCOL[g]
    text(XG, y, 1.36, RH,
         [[(f"GROUP {g}", 12.5, True, col, HEADB)],
          [(f"{d['vignettes']} vignettes", 10, False, MUTED, BODY)]],
         anchor=MSO_ANCHOR.MIDDLE, spc=0)

    n = MODAL[g]
    bw, bg = 0.26, 0.10
    tot = n * bw + (n - 1) * bg
    bx = XS + (1.74 - tot) / 2
    heights = {2: [0.86, 0.34], 4: [0.80, 0.30, 0.20, 0.14]}[n]
    for bi in range(n):
        hh = SHAPE_H * heights[bi]
        box(bx, y + 0.06 + (SHAPE_H - hh), bw, hh,
            RED if bi == 0 else SLATE_L, shape=MSO_SHAPE.RECTANGLE)
        bx += bw + bg
    over = ROWSPEC[g]
    text(XO, y, 6.30, RH, [[(over, 12, False, INK, BODY)]],
         anchor=MSO_ANCHOR.MIDDLE)
    text(XR, y, WR, RH,
         [[(f"{d['rows']:,}", 15, True, col, BODYB)],
          [(mixtext(g), 8.5, False, GREY, BODY)]],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spc=0)

TB = TY + 0.40 + 4 * PITCH
rule(L, TB + 0.04, XR + WR - L, HAIR)
text(XO, TB + 0.14, 6.30, 0.28,
     [[("Every arm of every vignette is scored over that vignette's own option set.",
        11, False, GREY, BODY)]])
text(XR, TB + 0.14, WR, 0.30,
     [[(f"{N_ROWS_PER_MODEL:,}", 17, True, ACCENT, BODYB)]],
     align=PP_ALIGN.RIGHT)
print("table bottom:", round(TB + 0.44, 2))
assert TB + 0.44 < 10.60, TB   # the ledger on the right ends lower, by design

# ---------------------------------------------------- the arithmetic, in order
AXx, AW = 13.05, R - 13.05
text(AXx, TY, AW, 0.26,
     [[("AND SO, IN THE ORDER IT HAPPENS", 10.5, True, SLATE, HEAD)]])
rule(AXx, TY + 0.30, AW, HAIR)

def ledger(y, big, lab, note_, big_sz=26):
    text(AXx, y, 2.10, 0.44, [[(big, big_sz, True, ACCENT, HEADB)]],
         anchor=MSO_ANCHOR.MIDDLE)
    text(AXx + 2.20, y, AW - 2.20, 0.44, [[(lab, 12, True, INK, BODYB)]],
         anchor=MSO_ANCHOR.MIDDLE)
    text(AXx, y + 0.42, AW, 0.42, [[(note_, 10, False, MUTED, BODY)]])
    return y + 0.44

ay = TY + 0.40
ledger(ay, f"{N_PROMPTS:,}", "analysis-ready prompts",
       f"{BASE_ARMS} arms on each of {N_VIG} live vignettes, and {EXTRA_N} on "
       f"{EXTRA_ID}, which also varies a clinical cue. That is why it is "
       f"{N_PROMPTS:,} and not {BASE_ARMS * N_VIG}.")
ay += 0.86
rule(AXx, ay, AW, HAIR)
text(AXx, ay + 0.06, AW, 0.26,
     [[("\u00d7   each prompt's own option set", 11.5, True, ROSE, HEADB)]])
ay += 0.36
rule(AXx, ay, AW, HAIR)

ay += 0.08
ledger(ay, f"{N_ROWS_PER_MODEL:,}", "scored option rows, per model",
       "  +  ".join(f"{G[g]['rows']:,}" for g in sorted(G))
       + f"   =   {N_ROWS_PER_MODEL:,}, the four rows on the left.")
ay += 0.72
rule(AXx, ay, AW, HAIR)
text(AXx, ay + 0.06, AW, 0.26,
     [[(f"\u00d7   {N_MODELS} models, 2 open corpora", 11.5, True, ROSE, HEADB)]])
ay += 0.36

box(AXx, ay, AW, 0.62, RED_TINT, RED, 1.75)
text(AXx + 0.18, ay, 2.10, 0.62, [[(f"{TOTAL:,}", 28, True, ACCENT, HEADB)]],
     anchor=MSO_ANCHOR.MIDDLE)
text(AXx + 2.38, ay, AW - 2.56, 0.62,
     [[("scored option rows in all", 12.5, True, INK, BODYB)]],
     anchor=MSO_ANCHOR.MIDDLE)
ay += 0.62
print("ledger bottom:", round(ay, 2))
assert ay < 10.80, ay

prs.save(OUT)
print("saved", OUT, "slides:", len(Presentation(OUT).slides))
