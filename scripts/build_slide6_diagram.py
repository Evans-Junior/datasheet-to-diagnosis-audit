"""Redraw slide 6 of the final presentation as a diagram.

Replaces the four-row principles table with:
  stage band (gate / floor / findings) -> four group chips -> placebo band -> gate funnel.

Numbers are READ from results/tables, never typed, except the group sizes which
are counted from templates.yaml. Run from the project root.
"""
import sys, os, yaml
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

DECK = "Ethics In AI Final Presentation.pptx"
OUT  = sys.argv[1] if len(sys.argv) > 1 else DECK

# ---------------------------------------------------------------- palette
INK        = RGBColor(0x1A, 0x1A, 0x1A)
MUTED      = RGBColor(0x70, 0x70, 0x70)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
CREAM      = RGBColor(0xF8, 0xEB, 0xEB)
CREAM_LINE = RGBColor(0xDC, 0xC2, 0xC2)
RED        = RGBColor(0xE8, 0x37, 0x2C)   # sampled from the hand-drawn 25 circle
RED_DEEP   = RGBColor(0xB8, 0x24, 0x19)
RED_TINT   = RGBColor(0xFB, 0xE2, 0xDF)
SLATE      = RGBColor(0x3F, 0x4C, 0x5A)
SLATE_TINT = RGBColor(0xED, 0xF1, 0xF4)
FIND       = RGBColor(0x4A, 0x33, 0x30)
HAIR       = RGBColor(0xD8, 0xD8, 0xD8)

DISPLAY, HEAD, BODY = "Rye", "Montserrat Bold", "Poppins"
BODY_B = "Poppins Bold"

# ---------------------------------------------------------------- facts
root = os.getcwd()
tpl = yaml.safe_load(open("data/vignettes/templates.yaml"))
rows = tpl["templates"] if isinstance(tpl, dict) and "templates" in tpl else tpl
live = [r for r in rows if r.get("verification") not in ("rejected", "retired_superseded")]
N = {}
for r in live:
    N[r["group"]] = N.get(r["group"], 0) + 1
assert sum(N.values()) == 25, N

regate = pd.read_csv("results/tables/i4_placebo_regate.csv")
n_models   = len(regate)
n_gate     = int((regate["gate"] == "SENSITIVE").sum())
n_both     = int((regate["gate_both_floors"] == "SENSITIVE").sum())
PH         = regate["prompt_hash"].iloc[0]
n_placebo  = len(pd.read_csv("data/vignettes/placebo_prompts.csv"))
print(f"groups {N}  models {n_models}  gate {n_gate}  both {n_both}  placebo prompts {n_placebo}")

# ---------------------------------------------------------------- helpers
def E(v):  # inches -> EMU
    return Inches(v)

def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, rad=0.10,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=None):
    sh = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if name:
        sh.name = name
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = rad
        except Exception:
            pass
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    sh.text_frame.text = ""
    return sh

def text(s, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None):
    """paras: list of list of (txt, size, bold, color, font, italic, space_after)"""
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    first = True
    for runs in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        for spec in runs:
            txt, sz, bold, col, fnt = spec[:5]
            ital = spec[5] if len(spec) > 5 else False
            sa   = spec[6] if len(spec) > 6 else None
            r = p.add_run(); r.text = txt
            r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = ital
            r.font.name = fnt; r.font.color.rgb = col
            if sa is not None:
                p.space_after = Pt(sa)
    return tb

def dots(s, x, y, n, col, d=0.125, gap=0.055):
    for i in range(n):
        c = s.shapes.add_shape(MSO_SHAPE.OVAL, E(x + i * (d + gap)), E(y), E(d), E(d))
        c.fill.solid(); c.fill.fore_color.rgb = col
        c.line.fill.background(); c.shadow.inherit = False
        c.name = "dot"

def vline(s, x, y0, y1, col, lw=1.25):
    ln = s.shapes.add_connector(1, E(x), E(y0), E(x), E(y1))
    ln.line.color.rgb = col; ln.line.width = Pt(lw)
    return ln

# ---------------------------------------------------------------- geometry
L, R = 0.70, 19.30
CW = R - L
CHIP_W, GAP = 4.425, 0.30
CX = [L + i * (CHIP_W + GAP) for i in range(4)]
CHIP_Y, CHIP_H = 3.00, 3.50
BAND_Y, BAND_H = 6.86, 1.30
RES_Y,  RES_H  = 8.48, 1.50

prs = Presentation(DECK)
assert len(prs.slides) == 24, len(prs.slides)
s = prs.slides[5]

# --- remove the old table, keep the circled "25 vignettes"
killed = []
for sh in list(s.shapes):
    if sh.has_table or sh.name == "Table 5":
        killed.append(sh.name)
        sh._element.getparent().remove(sh._element)
assert killed == ["Table 5"], killed
print("removed:", killed)

# --- header
text(s, 3.78, 0.52, 11.4, 0.70,
     [[("FOUR GROUPS.  ONE GATE.  TWO FLOORS.", 31, True, INK, HEAD)]],
     name="hdr_title")
text(s, 3.80, 1.33, 11.4, 0.95,
     [[("Every vignette does one job. Read left to right: nothing on the right "
        "can be interpreted until the stage on its left holds.", 15.5, False, MUTED, BODY)]],
     name="hdr_sub")
text(s, 15.4, 0.50, 3.90, 1.10,
     [[("3 + 11 + 5 + 6", 25, False, INK, DISPLAY, False, 3)],
      [("25 live vignettes of 28", 11.5, False, MUTED, BODY)]],
     align=PP_ALIGN.RIGHT, name="hdr_sum")

# --- stage band
for x, w, lab, col in [
    (CX[0], CHIP_W,                      "1  ·  GATE",         RED),
    (CX[1], CHIP_W,                      "2  ·  FLOOR",        SLATE),
    (CX[2], R - CX[2],                   "3  ·  THE FINDINGS", FIND),
]:
    rect(s, x, 2.46, w, 0.44, fill=col, line=None, rad=0.30, name="stage")
    text(s, x, 2.56, w, 0.30, [[(lab, 13, True, WHITE, HEAD)]],
         align=PP_ALIGN.CENTER, name="stage_lab")

# --- chips
CHIPS = [
    dict(g="GROUP 2", n=N[2], fill=RED_TINT,   line=RED,        lw=2.25, col=RED_DEEP,
         role="The guideline's own answer changes with the sex parameter.",
         eg="Pregnancy test before CT  ·  prostate in urinary symptoms  ·  cervical screening",
         emph="A model that answers the same either way is blind, not fair."),
    dict(g="GROUP 4", n=N[4], fill=SLATE_TINT, line=SLATE,      lw=1.5,  col=SLATE,
         role="Gender flipped where no disparity is documented.",
         eg="Ankle sprain  ·  abscess  ·  sinusitis  ·  DVT  ·  anaphylaxis  ·  meningitis",
         emph="Whatever moves here is the instrument, not the model."),
    dict(g="GROUP 1", n=N[1], fill=CREAM,      line=CREAM_LINE, lw=1.25, col=FIND,
         role="Sex-neutral conditions. No gap is warranted.  (H3)",
         eg="Pneumonia  ·  malaria  ·  asthma  ·  cellulitis  ·  type 2 diabetes",
         emph="A gap here has no clinical warrant at all."),
    dict(g="GROUP 3", n=N[3], fill=CREAM,      line=CREAM_LINE, lw=1.25, col=FIND,
         role="Conditions with documented human bias.  (H1)",
         eg="Renal colic  ·  chest pain triage  ·  ADHD  ·  autism  ·  cardiac rehab  ·  knee replacement",
         emph="A gap here repeats a documented human bias."),
]
PAD = 0.26
IW = CHIP_W - 2 * PAD
for i, c in enumerate(CHIPS):
    x = CX[i]
    rect(s, x, CHIP_Y, CHIP_W, CHIP_H, fill=c["fill"], line=c["line"], lw=c["lw"],
         rad=0.055, name=f"chip{i}")
    text(s, x + PAD, CHIP_Y + 0.16, IW, 0.30,
         [[(c["g"], 16, True, c["col"], HEAD)]], name="chip_g")
    text(s, x + PAD, CHIP_Y + 0.46, IW, 0.70,
         [[(str(c["n"]), 38, False, INK, DISPLAY),
           ("  vignettes", 12.5, False, MUTED, BODY)]],
         anchor=MSO_ANCHOR.BOTTOM, name="chip_n")
    dots(s, x + PAD, CHIP_Y + 1.26, c["n"], c["col"])
    text(s, x + PAD, CHIP_Y + 1.56, IW, 0.66,
         [[(c["role"], 14, True, INK, BODY_B)]], name="chip_role")
    text(s, x + PAD, CHIP_Y + 2.26, IW, 0.68,
         [[(c["eg"], 11, False, MUTED, BODY)]], name="chip_eg")
    text(s, x + PAD, CHIP_Y + 2.96, IW, 0.46,
         [[(c["emph"], 11.5, False, c["col"], BODY, True)]], name="chip_emph")

# --- chevrons between stage 1 -> 2 and 2 -> 3 only (groups 1 and 3 are parallel)
for gx, col in [(CX[0] + CHIP_W, RED), (CX[1] + CHIP_W, SLATE)]:
    ch = rect(s, gx + 0.015, CHIP_Y + 1.50, GAP - 0.03, 0.42,
              fill=col, line=None, shape=MSO_SHAPE.CHEVRON, name="chev")

# --- placebo band, presented as what it is: an amendment to the design.
# The RESULT of the placebo (the gate going 3 -> 0) belongs in the results
# section, not here. Until 2026-11-18 this slide carried a 10 -> 3 -> 0 funnel,
# which gave away the finding three slides before the audience had been told how
# anything was scored. D108.
BW, BH = R - L, 3.30
rect(s, L, BAND_Y, BW, BH, fill=SLATE_TINT, line=SLATE, lw=1.25, rad=0.035, name="pb_bg")
rect(s, L, BAND_Y, 3.30, BH, fill=SLATE, line=None, rad=0.035, name="pb_cap")
text(s, L + 0.26, BAND_Y + 0.30, 2.80, 1.30,
     [[("PLACEBO", 20, True, WHITE, HEAD, False, 0)],
      [("ARM", 20, True, WHITE, HEAD, False, 6)],
      [("the second floor", 12.5, False, RGBColor(0xC2, 0xCC, 0xD6), BODY)]],
     name="pb_cap_t")
text(s, L + 0.26, BAND_Y + 2.30, 2.80, 0.80,
     [[("AN AMENDMENT", 11, True, RGBColor(0xF0, 0xB8, 0xB4), HEAD, False, 2)],
      [("added to the design after the first run, and before any placebo "
        "number was read", 10.5, False, RGBColor(0x9F, 0xAD, 0xBA), BODY)]],
     name="pb_cap_amend")

# what it is, and why it was added
PX, PW = 4.25, 6.40
text(s, PX, BAND_Y + 0.26, PW, 0.56,
     [[("The same 25 vignettes, scored again, with eye colour or shirt colour "
        f"changed instead of gender. {n_placebo} prompts.", 15, True, INK, BODY_B)]],
     name="pb_what")
text(s, PX, BAND_Y + 0.92, PW, 2.10,
     [[("Yoo 2026 reports that an inert edit moves a clinical model as much as a "
        "demographic one. If that holds here, a gender gap can clear the Group 4 "
        "floor and still be nothing more than the model's sensitivity to being "
        "edited at all.", 12.5, False, MUTED, BODY, False, 8)],
      [("Nine candidate attributes were rejected first, each for touching something "
        "a clinician could act on. Both floors are aggregated as the maximum, and "
        "that choice was fixed before any number was seen.",
        12.5, False, MUTED, BODY)]],
     name="pb_why")

# the 2x2 that distinguishes the two floors
QX, RLW, QCW, QG = 11.30, 2.10, 2.72, 0.12
C1X, C2X = QX + RLW, QX + RLW + QCW + QG
assert C2X + QCW <= R - 0.26, C2X + QCW
HDR_Y, R1Y, R2Y, QRH = BAND_Y + 0.26, BAND_Y + 0.78, BAND_Y + 1.98, 1.10
for cx, lab in [(C1X, "ON THE SAME VIGNETTE"), (C2X, "ON A DIFFERENT VIGNETTE")]:
    text(s, cx, HDR_Y + 0.14, QCW, 0.34, [[(lab, 10.5, True, SLATE, HEAD)]],
         align=PP_ALIGN.CENTER, name="q_colhdr")
for ry, lab in [(R1Y, "CHANGE THE\nGENDER"), (R2Y, "CHANGE SOMETHING\nINERT")]:
    text(s, QX, ry, RLW - 0.14, QRH,
         [[(l, 11, True, SLATE, HEAD)] for l in lab.split("\n")],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, name="q_rowhdr")
QCELLS = [
    (C1X, R1Y, "THE EFFECT", "the gap we are trying to measure", WHITE, RED, 1.75, RED_DEEP),
    (C2X, R1Y, "GROUP 4  ·  FLOOR ONE", "the right change on the wrong case",
     SLATE_TINT, SLATE, 1.5, SLATE),
    (C1X, R2Y, "PLACEBO  ·  FLOOR TWO", "the wrong change on the right case",
     RED_TINT, RED, 1.75, RED_DEEP),
    (C2X, R2Y, "NOT RUN", "an inert change on an unrelated case tells us nothing",
     None, HAIR, 1.0, RGBColor(0xA8, 0xA8, 0xA8)),
]
for cx, ry, head, note, fill, line, lw, col in QCELLS:
    rect(s, cx, ry, QCW, QRH, fill=fill, line=line, lw=lw, rad=0.07, name="q_cell")
    text(s, cx + 0.16, ry + 0.16, QCW - 0.32, 0.46, [[(head, 11, True, col, HEAD)]],
         name="q_cell_h")
    text(s, cx + 0.16, ry + 0.52, QCW - 0.32, 0.50, [[(note, 11, False, col, BODY)]],
         name="q_cell_n")
print("2x2 bottom:", round(R2Y + QRH, 2), "band bottom:", round(BAND_Y + BH, 2))
assert R2Y + QRH < BAND_Y + BH - 0.10, (R2Y + QRH, BAND_Y + BH)

# ticks showing the band runs under all four groups
for i in range(4):
    vline(s, CX[i] + CHIP_W / 2, CHIP_Y + CHIP_H + 0.05, BAND_Y - 0.04, SLATE, 1.0)

text(s, L, BAND_Y + BH + 0.14, BW, 0.30,
     [[("What the placebo did to the gate is a result, so it is reported in the "
        "results section, not here.", 12.5, True, RED_DEEP, BODY_B)]],
     align=PP_ALIGN.CENTER, name="caption")
text(s, L, BAND_Y + BH + 0.46, BW, 0.30,
     [[(f"Arms in configs/placebo_arms.yaml  ·  prompts in "
        f"data/vignettes/placebo_prompts.csv  ·  prompt set {PH}",
        10.5, False, MUTED, BODY)]],
     align=PP_ALIGN.CENTER, name="foot")

prs.save(OUT)
print("saved", OUT, "slides:", len(Presentation(OUT).slides))
