"""Split the worked example in two: the input, then the probabilities.

One slide carried the full prompt, the eight arm headers, a 3 x 8 matrix of
probabilities and a four-sentence reading note: 78 shapes, and the audience was
asked to read a clinical vignette and a matrix of 24 numbers at the same time.

  A.  the input       the prompt itself, the named guideline both answers come
                      from, what changes between arms, and what to watch for
  B.  the output      the matrix, moved up into the room the prompt vacated

The matrix shapes are MOVED, not retyped: their XML elements are deep-copied into
the new slide and shifted up, so the numbers cannot drift from the ones that were
verified. D111. Run from the project root.
"""
import sys, copy, json
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
TITLE_TEXT = "What the models actually did"
VIG = "G2-02"
SPLIT_AT, SHIFT = 4.80, 1.05      # inches

INK, MUTED = RGBColor(0x1A,0x1A,0x1A), RGBColor(0x70,0x70,0x70)
GREY = RGBColor(0x89,0x89,0x89)
WHITE, CREAM = RGBColor(0xFF,0xFF,0xFF), RGBColor(0xF8,0xEB,0xEB)
ROSE = RGBColor(0xC8,0x62,0x62)
ACCENT = RGBColor(0x8D,0x00,0x00)
HAIR = RGBColor(0xDC,0xC2,0xC2)
SLATE = RGBColor(0x3F,0x4C,0x5A)
SLATE_T = RGBColor(0xED,0xF1,0xF4)
HEAD, HEADB, BODY, BODYB = "Montserrat Medium", "Montserrat Bold", "Poppins", "Poppins Bold"

# ------------------------------------------------------------------ facts
gl = json.load(open("docs/references.json"))["guidelines"]
ent = [g for g in gl if VIG in g["vignettes"]]
assert len(ent) == 1, ent
CITE, DOI, STATUS = ent[0]["cite"], ent[0]["doi"], ent[0]["status"]
assert STATUS == "verified", STATUS
print("source for", VIG, "->", CITE)

prs = Presentation(DECK)
hits = [i for i, sl in enumerate(prs.slides)
        if any(sh.name == "title" and sh.has_text_frame
               and sh.text_frame.text.strip() == TITLE_TEXT for sh in sl.shapes)]
assert len(hits) == 1, hits
IDX = hits[0]
a = prs.slides[IDX]
print("worked example is at position", IDX + 1)

def named(sl, n):
    return next(sh for sh in sl.shapes if sh.name == n)

def retext(sl, name, new):
    p = named(sl, name).text_frame.paragraphs[0]
    p.runs[0].text = new
    for r in p.runs[1:]:
        r.text = ""

# ------------------------------------------------------------------ slide B
b = prs.slides.add_slide(a.slide_layout)
for sh in list(b.shapes):
    sh._element.getparent().remove(sh._element)

moving = [sh for sh in a.shapes if Emu(sh.top).inches >= SPLIT_AT]
assert len(moving) >= 60, len(moving)
sid = 200
for sh in moving:
    el = copy.deepcopy(sh._element)
    for node in el.iter():
        assert node.get(qn('r:embed')) is None, "a moved shape carries an image"
    cnv = el.find('.//' + qn('p:cNvPr'))
    cnv.set('id', str(sid)); sid += 1
    b.shapes._spTree.insert_element_before(el, 'p:extLst')
    sh._element.getparent().remove(sh._element)
print("shapes moved to the new slide:", len(moving))

for sh in b.shapes:
    sh.top = Emu(sh.top) - Inches(SHIFT)
tops = [Emu(sh.top).inches for sh in b.shapes]
bots = [Emu(sh.top).inches + Emu(sh.height).inches for sh in b.shapes]
print("moved block now spans %.2f to %.2f" % (min(tops), max(bots)))
assert min(tops) > 3.10, min(tops)
assert max(bots) < 11.05, max(bots)

def mk(target):
    def text(x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spc=None):
        tb = target.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
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

    def box(x, y, w, h, fill, line=None, lw=1.0, rad=0.05,
            shape=MSO_SHAPE.ROUNDED_RECTANGLE):
        sh = target.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
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
        ln = target.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
        ln.line.color.rgb = col; ln.line.width = Pt(lw)
    return text, box, rule

Atext, Abox, Arule = mk(a)
Btext, Bbox, Brule = mk(b)

Btext(1.20, 0.78, 17.60, 0.34,
      [[("WORKED EXAMPLE  ·  THE OUTPUT, ONE VIGNETTE, EIGHT ARMS, THREE MODELS",
         16, True, ROSE, HEAD)]])
Btext(1.20, 1.20, 17.60, 0.82,
      [[("What the models actually did", 40, True, RGBColor(0,0,0), HEADB)]])
Btext(1.20, 2.12, 17.60, 0.50,
      [[("The same prompt as the slide before, with only the bracketed label and the "
         "sex parameter changed. Everything below is the probability the model put "
         "on “Yes”.", 19, False, RGBColor(0x32,0x32,0x32), HEAD)]])
Brule(1.20, 2.88, 17.60, ROSE)

# ------------------------------------------------------------------ slide A
retext(a, "kicker", "WORKED EXAMPLE  ·  THE INPUT, AND WHY THIS VIGNETTE IS THE CONTROL")
retext(a, "title", "One vignette, and the two things that move in it")
retext(a, "sub", "Positive control G2-02. Everything below is byte-identical "
                 "across all 24 arms except the two fields marked in red.")

# the prompt box grows into the room the matrix left
named(a, "Rounded Rectangle 5").height = Inches(1.86)
tb6 = named(a, "TextBox 6")
tb6.top, tb6.height = Inches(3.34), Inches(1.40)
for p in tb6.text_frame.paragraphs:
    for r in p.runs:
        if r.font.size:
            r.font.size = Pt(17)

# run 0 reads "Sex for clinical use: female.   The patient is ": the first half
# varies between arms and the second does not, so it is split before colouring.
# Otherwise the subtitle promises two red fields and the slide shows three.
from pptx.text.text import _Run
p0 = tb6.text_frame.paragraphs[0]
r0 = p0.runs[0]
HEAD_TXT = "Sex for clinical use: female."
assert r0.text.startswith(HEAD_TXT), r0.text
tail = r0.text[len(HEAD_TXT):]
el = copy.deepcopy(r0._r)
r0._r.addnext(el)
rest = _Run(el, p0)
r0.text = HEAD_TXT
rest.text = tail
rest.font.bold = False
rest.font.color.rgb = INK

VARY = 0
for p in tb6.text_frame.paragraphs:
    for r in p.runs:
        if r.text.strip() == HEAD_TXT or r.text.strip().startswith("[a woman"):
            r.font.color.rgb = ACCENT
            VARY += 1
assert VARY == 2, VARY

PANELS = [
    ("THE SOURCE OF BOTH ANSWERS",
     [("The correct answer is not ours to choose. It is read off a named guideline, "
       "and on this vignette that guideline gives two different answers depending "
       "on the sex parameter, which is exactly what makes it a control.", False),
      (CITE, True),
      (f"doi:{DOI}  ·  read at first hand", False)]),
    ("WHAT CHANGES BETWEEN ARMS",
     [("Sex for clinical use. A clinical field. The guideline's own answer depends "
       "on it, so the model is REQUIRED to move with it.", True),
      ("The bracketed identity label, with its pronouns. A social field. No "
       "guideline anywhere makes the answer depend on it, so the model must NOT "
       "move with it.", True),
      ("Nothing else. Same age, same findings, same residual volume, same question, "
       "same two options.", False)]),
]
PY_, PH_ = 5.36, 2.92
PW_, PG_ = 8.64, 0.32
for i, (head, lines) in enumerate(PANELS):
    x = 1.20 + i * (PW_ + PG_)
    Abox(x, PY_, PW_, PH_, CREAM, ROSE, 1.25)
    Atext(x + 0.30, PY_ + 0.28, PW_ - 0.60, 0.30,
          [[(head, 11.5, True, ROSE, HEAD)]])
    Atext(x + 0.30, PY_ + 0.72, PW_ - 0.60, PH_ - 1.00,
          [[(t, 14, bo, INK if bo else MUTED, BODY)] for t, bo in lines], spc=11)
assert abs((1.20 + (PW_ + PG_) + PW_) - 18.80) < 1e-9, PW_

Atext(1.20, 8.52, 17.60, 0.42,
      [[("The prompt never contains the words “transgender” or "
         "“cisgender”. Crossing a clinical field with a social label is "
         "what produces the six configurations, and it is the whole design.",
         13, False, GREY, BODY)]])

# ------------------------------------------------------------------ place it
lst = prs.slides._sldIdLst
el = list(lst)[-1]
lst.remove(el)
lst.insert(IDX + 1, el)

prs.save(OUT)
print("saved", OUT, "slides:", len(Presentation(OUT).slides))
