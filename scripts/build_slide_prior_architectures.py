"""Add a prior-architectures slide immediately before our own design slide.

Five published audit architectures, each drawn in the same visual grammar so the
designs can be compared, each captioned with what this project took from it, then
our own chain with the two pieces none of them had.

Reference numbers match the deck's existing References slide.
Run from the project root.
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
BEFORE = "FOUR GROUPS.  ONE GATE.  TWO FLOORS."   # our own design slide

ACCENT  = RGBColor(0x8D, 0x00, 0x00)
RED     = RGBColor(0xE8, 0x37, 0x2C)
ROSE    = RGBColor(0xC8, 0x62, 0x62)
BODYCOL = RGBColor(0x32, 0x32, 0x32)
MUTED   = RGBColor(0x89, 0x89, 0x89)
BLACK   = RGBColor(0x00, 0x00, 0x00)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
CREAM   = RGBColor(0xF8, 0xEB, 0xEB)
SLATE   = RGBColor(0x3F, 0x4C, 0x5A)
SLATE_L = RGBColor(0xC3, 0xCC, 0xD4)
HAIR    = RGBColor(0xDC, 0xC2, 0xC2)
MM, MB, PB, PP = "Montserrat Medium", "Montserrat Bold", "Poppins Bold", "Poppins"

prs = Presentation(DECK)
dest = None
for i, sl in enumerate(prs.slides):
    for sh in sl.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == BEFORE:
            dest = i
assert dest is not None, "could not find our own design slide"
print("our design slide is at position", dest + 1, "- inserting before it")

layout = next(l for l in prs.slide_layouts if l.name == "Blank")
s = prs.slides.add_slide(layout)
for sh in list(s.shapes):
    sh._element.getparent().remove(sh._element)

def E(v): return Inches(v)

def text(x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spc=None):
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    first = True
    for runs in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if spc is not None: p.space_after = Pt(spc)
        for t, sz, b, col, fnt in runs:
            r = p.add_run(); r.text = t
            r.font.size = Pt(sz); r.font.bold = b; r.font.name = fnt
            r.font.color.rgb = col
    return tb

def box(x, y, w, h, fill, line=None, lw=1.0, rad=0.12, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try: sh.adjustments[0] = rad
        except Exception: pass
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False; sh.text_frame.text = ""
    return sh

def minilabel(x, y, w, t, sz=8.5, col=BODYCOL, bold=False, align=PP_ALIGN.CENTER):
    return text(x, y, w, 0.18, [[(t, sz, bold, col, PP)]], align=align)

def arrow(x, y, w, col=SLATE, h=0.11):
    return box(x, y, w, h, col, shape=MSO_SHAPE.RIGHT_ARROW)

def line(x0, y0, x1, y1, col=HAIR, lw=1.0, dash=False):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x0), E(y0), E(x1), E(y1))
    ln.line.color.rgb = col; ln.line.width = Pt(lw)
    if dash:
        from pptx.oxml.ns import qn
        d = ln.line._get_or_add_ln().makeelement(qn('a:prstDash'), {'val': 'dash'})
        ln.line._get_or_add_ln().append(d)
    return ln

# ------------------------------------------------------------------ header
text(1.20, 0.78, 17.60, 0.34,
     [[("LITERATURE  ·  PRIOR ARCHITECTURES, AND WHAT WE TOOK FROM EACH",
        16, True, ROSE, MM)]])
text(1.20, 1.20, 17.60, 0.82,
     [[("Five audits came before ours", 40, True, BLACK, MB)]])
text(1.20, 2.12, 17.60, 0.50,
     [[("Every choice on the next slide comes from a published audit. Two pieces "
        "were missing from all of them, and those are our contribution.",
        19, False, BODYCOL, MM)]])
line(1.20, 2.88, 18.80, 2.88, ROSE)

# ------------------------------------------------------------------ five cards
CY, CH = 3.08, 4.35
CW, CG = 3.28, 0.30
CX = [1.20 + i * (CW + CG) for i in range(5)]
assert abs(CX[4] + CW - 18.80) < 1e-6, (CX, CX[4] + CW)
PAD = 0.24
IW = CW - 2 * PAD
DY, DH = CY + 0.78, 1.18          # diagram band

def d_chang(x):
    """2x2 of documented bias x clinical relevance."""
    cx, cy, c, g = x + IW / 2 - 0.62, DY + 0.16, 0.56, 0.08
    for r in range(2):
        for col in range(2):
            on = (r, col) in ((0, 0), (1, 1))
            box(cx + col * (c + g), cy + r * (c * 0.62 + g), c, c * 0.62,
                ACCENT if on else CREAM, ROSE, 0.75, rad=0.08)
    minilabel(x + PAD, DY + 0.92, IW, "documented bias  ×  clinical relevance")

def d_zack(x):
    cx = x + PAD
    box(cx, DY + 0.30, 0.78, 0.42, CREAM, ROSE, 0.75, rad=0.10)
    minilabel(cx, DY + 0.38, 0.78, "vignette", 8)
    arrow(cx + 0.84, DY + 0.26, 0.38, ROSE)
    arrow(cx + 0.84, DY + 0.60, 0.38, ROSE)
    for i, lab in enumerate(("woman", "man")):
        box(cx + 1.28, DY + 0.16 + i * 0.44, 0.74, 0.34, WHITE, ROSE, 0.75, rad=0.10)
        minilabel(cx + 1.28, DY + 0.22 + i * 0.44, 0.74, lab, 8)
    text(cx + 2.12, DY + 0.34, 0.50, 0.34,
         [[("≠", 20, True, ACCENT, PB)]], align=PP_ALIGN.CENTER)
    minilabel(x + PAD, DY + 0.92, IW, "swap one word, compare the answer")

def d_equitriage(x):
    base, cx = DY + 0.86, x + PAD + 0.30
    for i, hgt in enumerate((0.62, 0.40, 0.17)):
        box(cx + i * 0.52, base - hgt, 0.34, hgt, ACCENT if i < 2 else SLATE_L,
            None, rad=0.0, shape=MSO_SHAPE.RECTANGLE)
    line(x + PAD, base - 0.30, x + PAD + IW - 0.55, base - 0.30, SLATE, 1.0, dash=True)
    minilabel(x + PAD + IW - 0.62, base - 0.40, 0.60, "5%", 8, SLATE, True)
    line(x + PAD, base, x + PAD + IW, base, HAIR, 1.0)
    minilabel(x + PAD, DY + 0.92, IW, "flip rate against a preregistered threshold")

def d_yoo(x):
    """Horizontal bars: vertical ones put their labels where the caption sits."""
    lx, bx = x + PAD, x + PAD + 1.02
    for i, (w, col, lab) in enumerate(((0.52, ROSE, "sex edit"),
                                       (0.95, SLATE, "inert edit"))):
        y = DY + 0.30 + i * 0.30
        minilabel(lx, y + 0.01, 0.96, lab, 8.5, align=PP_ALIGN.RIGHT)
        box(bx, y, w, 0.19, col, None, rad=0.0, shape=MSO_SHAPE.RECTANGLE)
    line(bx - 0.04, DY + 0.26, bx - 0.04, DY + 0.84, HAIR, 1.0)
    minilabel(x + PAD, DY + 0.92, IW, "the control moves it MORE than the sex edit")

def d_feng(x):
    cx = x + PAD + 0.04
    for i, lab in enumerate(("corpus", "model", "task")):
        box(cx + i * 0.98, DY + 0.30, 0.80, 0.42, CREAM, ROSE, 0.75, rad=0.10)
        minilabel(cx + i * 0.98, DY + 0.38, 0.80, lab, 8)
        if i < 2:
            arrow(cx + 0.82 + i * 0.98, DY + 0.45, 0.14, ROSE, 0.09)
    minilabel(x + PAD, DY + 0.92, IW, "trace a property down the whole pipeline")

CARDS = [
    ("[14]", "CHANG 2025", "PLOS Digital Health", d_chang,
     "A 2×2 of documented bias against clinical relevance, run as paired prompts.",
     "our four groups. The grid IS the group structure."),
    ("[12]", "ZACK 2024", "Lancet Digital Health", d_zack,
     "Counterfactual clinical vignettes on a closed model, one demographic word swapped.",
     "the vignette method, and the reason we needed open models instead."),
    ("[21]", "EQUITRIAGE 2026", "arXiv preprint", d_equitriage,
     "374,275 evaluations, 9,346 gender-swapped pairs. Blinding cut one model 1.34:1 to 0.5%.",
     "the gender-blinded arm (D021), and dropping patient names (D012)."),
    ("[22]", "YOO 2026", "BioNLP, ACL", d_yoo,
     "Inert control edits move clinical LLMs as much as, or more than, demographic edits.",
     "the whole idea of a floor. An effect is judged against noise, never against zero."),
    ("[15]", "FENG 2023", "ACL, best paper", d_feng,
     "Pretraining corpus to model property to downstream unfairness, traced end to end.",
     "the shape of the project: datasheet to diagnosis in one chain."),
]
for x, (num, name, venue, draw, what, took) in zip(CX, CARDS):
    box(x, CY, CW, CH, WHITE, HAIR, 1.25, rad=0.05)
    text(x + PAD, CY + 0.18, IW, 0.26,
         [[(num + "  ", 12, True, ROSE, PB), (name, 12, True, BLACK, PB)]])
    text(x + PAD, CY + 0.46, IW, 0.22, [[(venue, 10, False, MUTED, PP)]])
    draw(x)
    text(x + PAD, DY + 1.22, IW, 0.80, [[(what, 11.5, False, BODYCOL, PP)]])
    line(x + PAD, CY + 3.18, x + CW - PAD, CY + 3.18, HAIR, 1.0)
    text(x + PAD, CY + 3.30, IW, 0.20, [[("WE TOOK", 9.5, True, ACCENT, MM)]])
    text(x + PAD, CY + 3.54, IW, 0.70, [[(took, 11.5, False, ACCENT, PP)]])

# ------------------------------------------------------------------ ours
# The chain is NOT linear and must not be drawn as one. The corpora produce the
# models; the 25 vignettes are a separate instrument built from guidelines. They
# meet once, where every vignette is scored on every model, and only then can the
# gate and the two floors be applied. Drawn as a single row (as it was until
# 2026-11-18) the picture says the models emit the vignettes, and whichever order
# you pick, one node has to be visited twice. Hence the converging Y.
OY, OH = 7.58, 2.80
box(1.20, OY, 17.60, OH, CREAM, ACCENT, 1.75, rad=0.05)
text(1.52, OY + 0.26, 2.60, 0.32, [[("OURS", 17, True, ACCENT, PB)]])
text(1.52, OY + 0.62, 2.60, 0.90,
     [[("the same chain,\nplus two tests\nnobody ran", 11.5, False, BODYCOL, PP)]])

nw, nh = 2.02, 0.72
TOP_Y = OY + 0.30                      # corpora -> models
BOT_Y = OY + 1.16                      # the instrument, built independently
MID_Y = (TOP_Y + BOT_Y) / 2            # where the two meet, and everything after
AX, BX = 4.35, 6.79
JOIN  = BX + nw + 0.19                 # the brace that joins the two inputs
CX2   = [JOIN + 0.40 + i * (nw + 0.42) for i in range(4)]
assert abs((BX + nw) - (AX + 2 * nw + 0.42)) < 1e-9, "bottom node must end with B"
assert CX2[-1] + nw <= 18.80, (CX2, CX2[-1] + nw)

def node(x, y, lab, new=False, w=None):
    w = w or nw
    box(x, y, w, nh, ACCENT if new else WHITE, ACCENT if new else HAIR,
        1.5 if new else 1.0, rad=0.10)
    text(x + 0.06, y, w - 0.12, nh,
         [[(l, 10.5, new, WHITE if new else BODYCOL, PB if new else PP)]
          for l in lab.split("\n")],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spc=0)
    if new:
        text(x, y - 0.24, w, 0.22, [[("NEW", 9, True, ACCENT, MM)]],
             align=PP_ALIGN.CENTER)

# the two inputs
node(AX, TOP_Y, "2 open corpora")
node(BX, TOP_Y, "10 models")
arrow(AX + nw + 0.08, TOP_Y + 0.305, 0.26, SLATE_L)
node(AX, BOT_Y, "25 vignettes\nin 4 groups", w=2 * nw + 0.42)
minilabel(AX, TOP_Y - 0.24, 2 * nw + 0.42, "TRAINED ON OPEN DATA", 9, MUTED, True)

# the brace: both inputs enter the same scoring step, so neither is drawn
# downstream of the other
line(BX + nw, TOP_Y + 0.36, JOIN, TOP_Y + 0.36, ACCENT, 1.5)
line(BX + nw, BOT_Y + 0.36, JOIN, BOT_Y + 0.36, ACCENT, 1.5)
line(JOIN, TOP_Y + 0.36, JOIN, BOT_Y + 0.36, ACCENT, 1.5)
arrow(JOIN + 0.02, MID_Y + 0.305, 0.36, ACCENT)

# everything downstream is applied to the scored rows, in order
node(CX2[0], MID_Y, "17,280\nscored rows")
node(CX2[1], MID_Y, "POSITIVE\nCONTROL", new=True)
node(CX2[2], MID_Y, "TWO FLOORS", new=True)
node(CX2[3], MID_Y, "the finding")
for i in range(3):
    arrow(CX2[i] + nw + 0.08, MID_Y + 0.305, 0.26, ACCENT)

text(4.35, OY + 2.02, 14.39, 0.52,
     [[("The corpora make the models; the 25 vignettes are a separate instrument "
        "built from guidelines, and the two meet only where every vignette is "
        "scored on every model. Neither closest audit has a sex-specific control "
        "group [21, 22], and Yoo's result, that inert edits move a clinical LLM as "
        "much as demographic ones, is what the second of our two floors is built "
        "to test, vignette by vignette.",
        12.5, False, BODYCOL, PP)]])

text(1.20, 10.52, 17.60, 0.42,
     [[("PDFs for [15], [21] and [22] are held in papers/lit/ and quoted from their "
        "own text. [12] and [14] are cited from the verified records in "
        "docs/paper_notes.md. Bracketed numbers match the References slide.",
        11, False, MUTED, PP)]])

lst = prs.slides._sldIdLst
el = list(lst)[-1]
lst.remove(el)
lst.insert(dest, el)
prs.save(OUT)
print("saved", OUT, "slides:", len(Presentation(OUT).slides))
