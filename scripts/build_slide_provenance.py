"""Add a method-provenance slide directly after our own design slide.

Row per design element: what it does here, who built it first, what we changed.
Borrowed rows and our own two additions are separated by fill and by a rule, so
the boundary between inherited and new method is visible rather than asserted.
Reference numbers match the deck's References slide.
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
AFTER = "FOUR GROUPS.  ONE GATE.  TWO FLOORS."

ACCENT=RGBColor(0x8D,0x00,0x00); RED=RGBColor(0xE8,0x37,0x2C)
ROSE=RGBColor(0xC8,0x62,0x62); BODYCOL=RGBColor(0x32,0x32,0x32)
MUTED=RGBColor(0x89,0x89,0x89); BLACK=RGBColor(0,0,0); WHITE=RGBColor(0xFF,0xFF,0xFF)
CREAM=RGBColor(0xF8,0xEB,0xEB); REDT=RGBColor(0xFB,0xE2,0xDF)
SLATE=RGBColor(0x3F,0x4C,0x5A); SLATE_L=RGBColor(0xC3,0xCC,0xD4)
HAIR=RGBColor(0xDC,0xC2,0xC2)
MM,MB,PB,PP="Montserrat Medium","Montserrat Bold","Poppins Bold","Poppins"

prs = Presentation(DECK)
dest = None
for i, sl in enumerate(prs.slides):
    for sh in sl.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == AFTER:
            dest = i + 1
assert dest, "design slide not found"
print("inserting at position", dest + 1)

s = prs.slides.add_slide(next(l for l in prs.slide_layouts if l.name == "Blank"))
for sh in list(s.shapes):
    sh._element.getparent().remove(sh._element)

def E(v): return Inches(v)
def text(x,y,w,h,paras,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,spc=None):
    tb=s.shapes.add_textbox(E(x),E(y),E(w),E(h)); tf=tb.text_frame; tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    tf.vertical_anchor=anchor; first=True
    for runs in paras:
        p=tf.paragraphs[0] if first else tf.add_paragraph(); first=False
        p.alignment=align
        if spc is not None: p.space_after=Pt(spc)
        for t,sz,b,col,fnt in runs:
            r=p.add_run(); r.text=t; r.font.size=Pt(sz); r.font.bold=b
            r.font.name=fnt; r.font.color.rgb=col
    return tb
def box(x,y,w,h,fill,line=None,lw=1.0,rad=0.09,shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh=s.shapes.add_shape(shape,E(x),E(y),E(w),E(h))
    if shape==MSO_SHAPE.ROUNDED_RECTANGLE:
        try: sh.adjustments[0]=rad
        except Exception: pass
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb=fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb=line; sh.line.width=Pt(lw)
    sh.shadow.inherit=False; sh.text_frame.text=""
    return sh
def rule(x,y,w,col=HAIR,lw=1.0):
    ln=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,E(x),E(y),E(x+w),E(y))
    ln.line.color.rgb=col; ln.line.width=Pt(lw)

# ---------------------------------------------------------------- header
text(1.20,0.78,17.60,0.34,[[("METHOD PROVENANCE  ·  WHICH PIECE CAME FROM WHERE",16,True,ROSE,MM)]])
text(1.20,1.20,17.60,0.82,[[("Five of seven pieces are inherited",40,True,BLACK,MB)]])
text(1.20,2.12,17.60,0.50,
     [[("Each row names the published design it came from. The last two rows are "
        "ours, and they are the two the prior audits did not have.",19,False,BODYCOL,MM)]])
rule(1.20,2.86,17.60,ROSE)

# ---------------------------------------------------------------- chain
NODES=[("2 open corpora",0),("10 models",0),("25 vignettes\nin 4 groups",0),
       ("POSITIVE\nCONTROL",1),("TWO FLOORS",1),("the finding",0)]
nx,nw,ng=1.20,2.52,0.46
for i,(lab,new) in enumerate(NODES):
    x=nx+i*(nw+ng)
    box(x,3.06,nw,0.80,ACCENT if new else WHITE,ACCENT if new else HAIR,1.5 if new else 1.0)
    text(x+0.06,3.06,nw-0.12,0.80,
         [[(l,11,new,WHITE if new else BODYCOL,PB if new else PP)] for l in lab.split("\n")],
         align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE,spc=0)
    if i<len(NODES)-1:
        box(x+nw+0.09,3.40,ng-0.18,0.12,ACCENT if i in (2,3) else SLATE_L,shape=MSO_SHAPE.RIGHT_ARROW)
assert nx+5*(nw+ng)+nw <= 18.80

# ---------------------------------------------------------------- table
ROWS=[
 ("Four vignette groups","A 2×2 of documented bias against clinical relevance, which is what "
  "sorts 25 vignettes into groups of 3, 11, 5 and 6.","[14] Chang 2025",
  "Added a guideline-quoted reference answer to every cell.",0),
 ("Matched counterfactual pairs","Byte-identical clinical text; only the identity label and pronouns move, "
  "so any difference is unwarranted by construction.","[12] Zack 2024",
  "Ran it on open-data models, so the corpus can be queried.",0),
 ("Gender-blinded reference arm","A fourth arm with identity withheld, never pooled with the gendered "
  "arms, giving a within-design null.","[21] EQUITRIAGE 2026",
  "Also dropped patient names, which their ablation justified.",0),
 ("Judging against a floor","An effect counts only above measured noise, never against zero.",
  "[22] Yoo 2026","Made the floor per model AND matched on option count.",0),
 ("Corpus to model to task","Tracing one property down the whole pipeline rather than testing the "
  "model alone.","[15] Feng 2023","Applied it to a clinical reference standard.",0),
 ("Positive control gate","Group 2, where the guideline's answer genuinely changes with the sex "
  "parameter. A model that cannot move here cannot be read anywhere.","OURS",
  "Neither closest audit has a sex-specific control group.",1),
 ("Placebo floor","An inert edit to the SAME vignette. Group 4 is the right change on the wrong "
  "case; this is the wrong change on the right case.","OURS",
  "Yoo used paraphrases; a one-span attribute swap is tighter.",1),
]
TX,TY=1.20,4.26
W=[3.30,6.60,2.70,5.00]
assert abs(sum(W)-17.60)<1e-9, sum(W)
HH,RH=0.44,0.80
gt=s.shapes.add_table(len(ROWS)+1,4,E(TX),E(TY),E(sum(W)),E(HH+RH*len(ROWS)))
tbl=gt.table; tbl.first_row=False; tbl.horz_banding=False
tp=tbl._tbl.find(qn('a:tblPr')); tp.set('firstRow','0')
for el in tp.findall(qn('a:tableStyleId')): tp.remove(el)
for i,w in enumerate(W): tbl.columns[i].width=E(w)
tbl.rows[0].height=E(HH)
for i in range(1,len(ROWS)+1): tbl.rows[i].height=E(RH)

def cell(r,c,paras,fill,align=PP_ALIGN.LEFT):
    cl=tbl.cell(r,c); cl.fill.solid(); cl.fill.fore_color.rgb=fill
    cl.margin_left=cl.margin_right=Inches(0.15)
    cl.margin_top=cl.margin_bottom=Inches(0.06)
    cl.vertical_anchor=MSO_ANCHOR.MIDDLE
    tf=cl.text_frame; tf.word_wrap=True; first=True
    for runs in paras:
        p=tf.paragraphs[0] if first else tf.add_paragraph(); first=False
        p.alignment=align
        for t,sz,b,col,fnt in runs:
            rn=p.add_run(); rn.text=t; rn.font.size=Pt(sz); rn.font.bold=b
            rn.font.name=fnt; rn.font.color.rgb=col

for c,h in enumerate(["DESIGN ELEMENT","WHAT IT DOES IN OUR INSTRUMENT",
                      "FIRST BUILT BY","WHAT WE CHANGED"]):
    cell(0,c,[[(h,11.5,True,ROSE,MM)]],WHITE)
for i,(el,does,src,chg,ours) in enumerate(ROWS,start=1):
    bg = REDT if ours else (CREAM if i%2 else WHITE)
    cell(i,0,[[(el,13,True,ACCENT if ours else BLACK,PB)]],bg)
    cell(i,1,[[(does,11.5,False,BODYCOL,PP)]],bg)
    cell(i,2,[[(src,12,True,ACCENT if ours else SLATE,PB)]],bg)
    cell(i,3,[[(chg,11.5,False,ACCENT if ours else MUTED,PP)]],bg)

# the boundary between inherited method and our own
# A floating label here overlapped the row above it and ran past the table
# edge. The rule, the red fill and the OURS column already mark the boundary
# three times over, so the rule carries it alone.
rule(TX,TY+HH+RH*5,sum(W),ACCENT,2.5)

bottom=TY+HH+RH*len(ROWS)
text(1.20,bottom+0.16,17.60,0.40,
     [[("Bracketed numbers match the References slide. The two rows below the line "
        "are what the five prior audits did not have, and they are also the two that "
        "decide whether anything else on the next slides can be read.",
        12,False,MUTED,PP)]])
assert bottom+0.60 < 11.0, bottom

lst=prs.slides._sldIdLst; el=list(lst)[-1]; lst.remove(el); lst.insert(dest,el)
prs.save(OUT); print("saved", OUT, "slides:", len(Presentation(OUT).slides))
