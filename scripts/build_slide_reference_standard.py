"""Rebuild the reference-standard slide as TWO slides, behind the grouping slide.

  A.  the sources       circled total, the 25 guideline documents by issuing body,
                        and how a named document becomes a scored reference answer
  B.  the silence scale the D029 grade: what the question is, what each level means,
                        how strong a warrant each gives, and the distribution

Until 2026-11-18 both lived on one slide, which left the document list at 11.5pt
and the scale table squeezed under it. The split is D107.

Counts are READ from docs/references.json and data/vignettes/sex_stratification_D029.csv.
Run from the project root.
"""
import copy, json, sys, csv, collections
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
SRC_IDX, DEST_IDX = 10, 6          # the existing guidelines slide -> position 7 and 8

INK, MUTED = RGBColor(0x1A,0x1A,0x1A), RGBColor(0x70,0x70,0x70)
GREY = RGBColor(0x89,0x89,0x89)
WHITE, CREAM = RGBColor(0xFF,0xFF,0xFF), RGBColor(0xF8,0xEB,0xEB)
ROSE = RGBColor(0xC8,0x62,0x62)            # the deck's existing accent for kickers
ACCENT = RGBColor(0x8D,0x00,0x00)
HAIR = RGBColor(0xDC,0xC2,0xC2)
SLATE = RGBColor(0x3F,0x4C,0x5A)
RAMP = [RGBColor(0x8E,0x2F,0x2F), RGBColor(0xB3,0x4A,0x4A),
        RGBColor(0xD9,0x8C,0x8C), RGBColor(0xF0,0xCF,0xCF)]
RAMP_TXT = [WHITE, WHITE, INK, INK]
DISPLAY, HEAD, HEADB, BODY = "Rye", "Montserrat Medium", "Montserrat Bold", "Poppins"
BODYB = "Poppins Bold"

# ------------------------------------------------------------------ facts
gl = json.load(open("docs/references.json"))["guidelines"]
N_DOCS = len(gl)
N_VIG = sum(len(v["vignettes"]) for v in gl)

strat = list(csv.DictReader(open("data/vignettes/sex_stratification_D029.csv")))
lvl = collections.Counter()
basis = {}
for r in strat:
    g = int(r["d029"].split("/")[-1])      # "0/1" is counted once, at 1
    lvl[g] += 1
    basis[r["id"]] = r["basis"]
N_SPLIT = sum(1 for r in strat if "/" in r["d029"])
assert sum(lvl.values()) == len(strat) == 25, (lvl, len(strat))
# one worked example per level, chosen by id so the pick is stable, text read from file
EG = {0: "G3-04", 1: "G3-02", 2: "G1-02", 3: "G4-04"}
assert set(EG.values()) <= set(basis), EG
print("docs", N_DOCS, "vignettes", N_VIG, "levels", dict(sorted(lvl.items())), "split", N_SPLIT)

prs = Presentation(DECK)
src, dst = prs.slides[5], prs.slides[SRC_IDX]

# ------------------------------------------------------------------ harvest
def txt(name):
    for sh in dst.shapes:
        if sh.name == name:
            return sh.text_frame.text
    raise KeyError(name)

KICKER, TITLE = txt("TextBox 3"), txt("TextBox 4")
SUB = txt("TextBox 5").split("\n")[0].strip()   # 2nd sentence is now the D029 block
D029_LABEL = txt("TextBox 35")
BLOCKS = []                                   # (header, items)
pend = {}
for sh in dst.shapes:
    if not (sh.has_text_frame and sh.name.startswith("TextBox")):
        continue
    n = int(sh.name.split()[1])
    if not 8 <= n <= 33:
        continue
    if n % 2 == 0:
        pend[n] = sh.text_frame.text
    else:
        BLOCKS.append((pend.pop(n - 1), sh.text_frame.text.split("\n")))
assert not pend and len(BLOCKS) == 13, (pend, len(BLOCKS))
assert sum(len(i) for _, i in BLOCKS) == N_DOCS
ISSUERS = len(BLOCKS)
print("issuer blocks", ISSUERS, "documents listed", sum(len(i) for _, i in BLOCKS))

# ------------------------------------------------------------------ slide B exists
b = prs.slides.add_slide(dst.slide_layout)
for sh in list(b.shapes):
    sh._element.getparent().remove(sh._element)
for sh in list(dst.shapes):
    sh._element.getparent().remove(sh._element)

# ------------------------------------------------------------------ helpers
def E(v): return Inches(v)

def mk(target):
    def text(x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spc=None):
        tb = target.shapes.add_textbox(E(x), E(y), E(w), E(h))
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

    def box(x, y, w, h, fill, line=None, lw=1.0, rad=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
        sh = target.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
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
        ln = target.shapes.add_connector(1, E(x), E(y), E(x + w), E(y))
        ln.line.color.rgb = col; ln.line.width = Pt(lw)
    return text, box, rule

Atext, Abox, Arule = mk(dst)
Btext, Bbox, Brule = mk(b)

def header(text, kicker, title, sub, title_sz=40, x=1.20, w=17.60):
    text(x, 0.78, w, 0.34, [[(kicker, 16, True, ROSE, HEAD)]])
    text(x, 1.20, w, 0.82, [[(title, title_sz, True, RGBColor(0,0,0), HEADB)]])
    text(x, 2.12, w, 0.50, [[(sub, 19, False, RGBColor(0x32,0x32,0x32), HEAD)]])

# =================================================================== SLIDE A
# the hand-drawn circle, copied off the grouping slide so the two totals rhyme
ff = src.shapes[0]
el = copy.deepcopy(ff._element)
EMBED = qn('r:embed')
# the circle is an SVG fill, so the relationship sits on asvg:svgBlip, not on
# a:blip. Remap every r:embed found by iterating, never by reading the blip.
remapped = 0
for node in el.iter():
    rid_old = node.get(EMBED)
    if rid_old:
        node.set(EMBED, dst.part.relate_to(src.part.related_part(rid_old), RT.IMAGE))
        remapped += 1
assert remapped, "no image relationship found on the circle"
print("circle image rels remapped:", remapped)
cnv = el.find('.//' + qn('p:cNvPr'))
cnv.set('id', '900'); cnv.set('name', 'Freeform circle')
dst.shapes._spTree.insert_element_before(el, 'p:extLst')

Atext(0.22, 0.45, 2.47, 1.89, [[(str(N_DOCS), 117.75, None, RGBColor(0,0,0), DISPLAY)]])
Atext(2.42, 1.44, 1.60, 0.66,
      [[("guideline", 15, True, RGBColor(0,0,0), HEAD)],
       [("documents", 15, True, RGBColor(0,0,0), HEAD)]], spc=0)

Atext(4.20, 0.50, 15.10, 0.34, [[(KICKER + "  ·  THE SOURCES", 16, True, ROSE, HEAD)]])
Atext(4.20, 0.94, 15.10, 0.80, [[(TITLE, 34, True, RGBColor(0,0,0), HEADB)]])
Atext(4.20, 1.86, 15.10, 0.60, [[(SUB, 16, False, RGBColor(0x32,0x32,0x32), HEAD)]])

Arule(1.20, 2.56, 17.60)
Atext(1.20, 2.72, 17.60, 0.32,
      [[(f"{N_VIG} VIGNETTES  ·  {N_DOCS} GUIDELINE DOCUMENTS  ·  {ISSUERS} "
         "ISSUING BODIES  ·  ONE NAMED DOCUMENT FOR EVERY VIGNETTE, ALL QUOTED AT "
         "FIRST HAND", 13, True, ROSE, HEAD)]])

# --- the document list, repacked across four columns by height, not by the
# column it happened to sit in on the old single slide
CX = [1.20, 5.73, 10.26, 14.79]
LIST_TOP, CW_ = 3.30, 4.03
HEAD_H, PITCH, BLOCK_GAP = 0.34, 0.30, 0.22
cy = [LIST_TOP] * 4
for hdr, items in sorted(BLOCKS, key=lambda b_: (-len(b_[1]), b_[0])):
    col = min(range(4), key=lambda c: cy[c])
    y = cy[col]
    Atext(CX[col], y, CW_, 0.30, [[(hdr, 14.5, True, INK, HEADB)]])
    Atext(CX[col], y + HEAD_H, CW_, PITCH * len(items),
          [[(it, 13, False, MUTED, BODY)] for it in items], spc=3)
    cy[col] = y + HEAD_H + PITCH * len(items) + BLOCK_GAP
print("column bottoms:", [round(v, 2) for v in cy])
assert max(cy) < 8.00, cy

# --- how a named document becomes a scored reference answer
SY = 8.16
Arule(1.20, SY, 17.60)
Atext(1.20, SY + 0.16, 17.60, 0.30,
      [[("AND HOW A NAMED DOCUMENT BECOMES A SCORED REFERENCE ANSWER, FOR EVERY "
         "ONE OF THE 25", 13, True, ROSE, HEAD)]])
STEPS = [
    ("THE DOCUMENT", "NICE NG79, acute sinusitis", "read at first hand, not from a review"),
    ("THE PASSAGE", "“do not offer an antibiotic”", "quoted verbatim, with its clause number"),
    ("THE REFERENCE ANSWER", "No", "the same answer for every patient"),
    ("THE SCORED OPTION", "Yes  |  No", "the model's probability on each"),
]
nw_, ng_ = 4.00, 0.53
for i, (lab, big, note) in enumerate(STEPS):
    x = 1.20 + i * (nw_ + ng_)
    Abox(x, SY + 0.60, nw_, 1.42, CREAM if i < 3 else WHITE, ROSE, 1.25)
    Atext(x + 0.22, SY + 0.76, nw_ - 0.44, 0.24, [[(lab, 10.5, True, ROSE, HEAD)]])
    Atext(x + 0.22, SY + 1.04, nw_ - 0.44, 0.40, [[(big, 15, True, INK, BODYB)]])
    Atext(x + 0.22, SY + 1.52, nw_ - 0.44, 0.42, [[(note, 11.5, False, GREY, BODY)]])
    if i < 3:
        Abox(x + nw_ + 0.13, SY + 1.25, ng_ - 0.26, 0.12, ROSE,
             shape=MSO_SHAPE.RIGHT_ARROW)
assert 1.20 + 3 * (nw_ + ng_) + nw_ <= 18.80

Atext(1.20, SY + 2.18, 17.60, 0.40,
      [[("A gender difference counts as bias only where the named document gives the "
         "same correct answer for every patient. Where the document's own answer "
         "changes with the sex parameter, the vignette is a positive control instead.",
         11.5, False, GREY, BODY)]])

# =================================================================== SLIDE B
Btext(1.20, 0.78, 17.60, 0.34,
      [[(KICKER + "  ·  GRADING WHAT THE DOCUMENT DOES NOT SAY", 16, True, ROSE, HEAD)]])
Btext(1.20, 1.20, 17.60, 0.82,
      [[("Silence about sex is graded, not assumed", 40, True, RGBColor(0,0,0), HEADB)]])
Btext(1.20, 2.12, 17.60, 0.50,
      [[("A guideline that says nothing about sex may have ruled it out, or may never "
         "have been asked. Those are different warrants, so every document carries a "
         "grade for which one it is.", 19, False, RGBColor(0x32,0x32,0x32), HEAD)]])
Brule(1.20, 2.88, 17.60, ROSE)

# --- left: what the question is
LX, LW = 1.20, 5.30
Bbox(LX, 3.22, LW, 3.86, CREAM, ROSE, 1.25)
Btext(LX + 0.30, 3.46, LW - 0.60, 0.30,
      [[("THE QUESTION WE PUT TO EVERY DOCUMENT", 11.5, True, ROSE, HEAD)]])
Btext(LX + 0.30, 3.84, LW - 0.60, 0.90,
      [[("Does this guideline stratify by sex ANYWHERE in it?", 21, True, INK, BODYB)]])
Btext(LX + 0.30, 4.86, LW - 0.60, 1.96,
      [[("Not whether it stratifies in the recommendation we test. Anywhere at all, "
         "cover to cover.", 13.5, True, INK, BODY)],
       [("A document that does stratify by sex somewhere has shown it will when it "
         "judges sex relevant, so its silence on our recommendation is a choice, and "
         "an informative one. A document that never mentions sex may simply never "
         "have been asked.", 13.5, False, MUTED, BODY)]], spc=10)

# --- distribution of the 25, one bar per level: a single stacked bar made the
# 1-of-25 segment 0.21in wide, too narrow for its own label
DY_ = 7.40
Btext(LX, DY_, LW, 0.28,
      [[(f"HOW THE {N_VIG} FALL", 11.5, True, ROSE, HEAD)]])
BLX, BLW = LX + 1.10, 3.40
scale = BLW / max(lvl.values())
for i_ in range(4):
    y = DY_ + 0.40 + i_ * 0.44
    Btext(LX, y, 1.00, 0.34, [[(f"level {i_}", 12, True, MUTED, HEAD)]],
          anchor=MSO_ANCHOR.MIDDLE)
    w = lvl[i_] * scale
    Bbox(BLX, y + 0.05, w, 0.24, RAMP[i_], shape=MSO_SHAPE.RECTANGLE)
    Btext(BLX + w + 0.12, y, 0.70, 0.34, [[(str(lvl[i_]), 13, True, INK, BODYB)]],
          anchor=MSO_ANCHOR.MIDDLE)
BB = DY_ + 0.40 + 4 * 0.44
Btext(LX, BB + 0.12, LW, 0.80,
      [[(f"{lvl[2] + lvl[3]} of the {N_VIG} rest on an omission rather than on a "
         f"stated claim, which is why the grade is reported beside every result "
         f"and not folded into it. Graded by both authors against the full text "
         f"and logged as D029; column H of the clinician workbook carries the "
         f"grade and its evidence on every row.", 11.5, False, GREY, BODY)]])
print("left column bottom:", round(BB + 0.92, 2))
assert BB + 0.92 < 10.60, BB

# --- right: the scale
TX, TY = 7.00, 3.22
Btext(TX, TY, 11.80, 0.30, [[(D029_LABEL, 12.5, True, ROSE, HEAD)]])
ROWS = [
    ("0", "names the disparity",
     "The guideline names the disparity in the very outcome we measure, and tells "
     "clinicians to counteract it",
     "Strongest.  Not silence at all"),
    ("1", "invariance stated",
     "Invariance is stated outright, for example “do not exclude … because "
     "of age, sex or gender”",
     "Strong.  An explicit claim"),
    ("2", "stratifies elsewhere",
     "The document does stratify by sex elsewhere, where it judged sex relevant, "
     "but not here",
     "Moderate.  An informative omission"),
    ("3", "never mentions sex",
     "Sex is never mentioned anywhere in the document",
     "Weakest.  The question may never have been asked"),
]
WIDTHS = [2.60, 4.20, 3.30, 1.70]
assert abs(sum(WIDTHS) - 11.80) < 1e-9, sum(WIDTHS)
HEADER_H, ROW_H = 0.44, 0.88
gt = b.shapes.add_table(len(ROWS) + 1, 4, E(TX), E(TY + 0.38),
                        E(sum(WIDTHS)), E(HEADER_H + ROW_H * len(ROWS)))
gt.name = "d029_table"
tbl = gt.table
tbl.first_row = False; tbl.horz_banding = False
tbl._tbl.find(qn('a:tblPr')).set('firstRow', '0')
for el2 in tbl._tbl.find(qn('a:tblPr')).findall(qn('a:tableStyleId')):
    tbl._tbl.find(qn('a:tblPr')).remove(el2)
for i, w in enumerate(WIDTHS):
    tbl.columns[i].width = E(w)
tbl.rows[0].height = E(HEADER_H)
for i in range(1, len(ROWS) + 1):
    tbl.rows[i].height = E(ROW_H)

def cell(r, c, paras, fill, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT):
    cl = tbl.cell(r, c)
    cl.fill.solid(); cl.fill.fore_color.rgb = fill
    cl.margin_left = cl.margin_right = Inches(0.16)
    cl.margin_top = cl.margin_bottom = Inches(0.06)
    cl.vertical_anchor = anchor
    tf = cl.text_frame; tf.word_wrap = True
    first = True
    for runs in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        for t, sz, bo, col, fnt in runs:
            rn = p.add_run(); rn.text = t
            rn.font.size = Pt(sz); rn.font.bold = bo; rn.font.name = fnt
            rn.font.color.rgb = col

for c, head in enumerate(["LEVEL", "WHAT IT MEANS",
                          "STRENGTH OF THE WARRANT", "IN OUR SET"]):
    cell(0, c, [[(head, 12, True, ROSE, HEAD)]], WHITE)
for i, (num, name, meaning, strength) in enumerate(ROWS, start=1):
    bg = CREAM if i % 2 else WHITE
    cell(i, 0, [[(num + "   ", 24, True, RAMP_TXT[i - 1], DISPLAY),
                 (name, 13.5, True, RAMP_TXT[i - 1], HEADB)]], RAMP[i - 1])
    cell(i, 1, [[(meaning, 13.5, False, INK, BODY)]], bg)
    cell(i, 2, [[(strength, 13.5, True, RGBColor(0x8E,0x2F,0x2F), BODY)]], bg)
    cell(i, 3, [[(f"{lvl[i-1]} of {N_VIG}", 14, True, INK, HEADB)]], bg,
         align=PP_ALIGN.CENTER)
TBL_BOTTOM = TY + 0.38 + HEADER_H + ROW_H * len(ROWS)

# --- one real example per level, quoted from the grading sheet
EY = TBL_BOTTOM + 0.30
Btext(TX, EY, 11.80, 0.30,
      [[("ONE DOCUMENT FROM OUR SET AT EACH LEVEL, IN THE WORDS OF THE GRADE ITSELF",
         12, True, ROSE, HEAD)]])
ey = EY + 0.38
for i in range(4):
    Bbox(TX, ey, 0.46, 0.44, RAMP[i], rad=0.18)
    Btext(TX, ey, 0.46, 0.44, [[(str(i), 15, True, RAMP_TXT[i], BODYB)]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    Btext(TX + 0.62, ey, 1.30, 0.44, [[(EG[i], 13, True, INK, BODYB)]],
          anchor=MSO_ANCHOR.MIDDLE)
    Btext(TX + 1.92, ey, 9.88, 0.44, [[(basis[EG[i]], 13, False, MUTED, BODY)]],
          anchor=MSO_ANCHOR.MIDDLE)
    ey += 0.48
print("example strip bottom:", round(ey, 2))
assert ey < 10.34, ey

Btext(TX, ey + 0.08, 11.80, 0.40,
      [[(f"{N_SPLIT} of the {N_VIG} sit between 0 and 1: the guideline names an access "
         "disparity and also sets a single threshold that applies to everyone. They "
         "are counted once, at 1.", 11.5, False, GREY, BODY)]])

# ------------------------------------------------------------------ move both
lst = prs.slides._sldIdLst
items = list(lst)
a_el, b_el = items[SRC_IDX], items[-1]
assert a_el is not b_el
lst.remove(a_el); lst.remove(b_el)
lst.insert(DEST_IDX, a_el)
lst.insert(DEST_IDX + 1, b_el)

prs.save(OUT)
chk = Presentation(OUT)
print("saved", OUT, "slides:", len(chk.slides))
