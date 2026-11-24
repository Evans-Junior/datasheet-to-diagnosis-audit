"""Add a results slide showing what the placebo floor did to the gate.

Inserted directly after 'What the three audits measured'. Every figure is READ
from results/tables/i4_placebo_regate.csv and i4_placebo_per_vignette.csv.
Run from the project root.
"""
import sys
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
AFTER_TITLE = "What the three audits measured"

# deck typography, read off the existing results slides
ACCENT  = RGBColor(0x8D, 0x00, 0x00)
ROSE    = RGBColor(0xC8, 0x62, 0x62)
BODYCOL = RGBColor(0x32, 0x32, 0x32)
BLACK   = RGBColor(0x00, 0x00, 0x00)
CREAM   = RGBColor(0xF8, 0xEB, 0xEB)
SLATE   = RGBColor(0x3F, 0x4C, 0x5A)
SLATE_L = RGBColor(0xA9, 0xB4, 0xBF)
MM, MB, PB = "Montserrat Medium", "Montserrat Bold", "Poppins Bold"

# ------------------------------------------------------------------ facts
reg = pd.read_csv("results/tables/i4_placebo_regate.csv")
pv  = pd.read_csv("results/tables/i4_placebo_per_vignette.csv")
N_MODELS = len(reg)
N_GATE   = int((reg.gate == "SENSITIVE").sum())
N_BOTH   = int((reg.gate_both_floors == "SENSITIVE").sum())
sens = reg[reg.gate == "SENSITIVE"].set_index("model_id")

SHORT = {"Qwen/Qwen3-8B": "Qwen3-8B",
         "allenai/OLMo-2-1124-7B-Instruct": "OLMo-2-7B-Instruct",
         "allenai/OLMo-2-1124-7B": "OLMo-2-7B (base)"}
ORDER = ["Qwen/Qwen3-8B", "allenai/OLMo-2-1124-7B-Instruct", "allenai/OLMo-2-1124-7B"]
assert set(ORDER) == set(sens.index), sens.index.tolist()

VIG = {"G2-01b": "pregnancy test before CT",
       "G2-02": "prostate in urinary symptoms",
       "G2-03b": "cervical screening"}

det = pv[pv.model_detects_sex_parameter == True]
n_pairs = len(det)
n_clear = int(det.clears_own_placebo.sum())

# the two headline anecdotes, read not typed
inst = "allenai/OLMo-2-1124-7B-Instruct"
worst = det[(det.model_id == inst) & (det.vignette_id == "G2-02")].iloc[0]
best  = det[(det.model_id == inst) & (det.vignette_id == "G2-03b")].iloc[0]
print(f"gate {N_GATE}->{N_BOTH}; pairs {n_clear}/{n_pairs}; "
      f"prostate placebo {worst.placebo_worst_abs} vs gender {worst.gender_margin_abs}; "
      f"cervical ratio {best.ratio_gender_over_placebo:.2f}")

prs = Presentation(DECK)
titles = []
for i, s in enumerate(prs.slides):
    for sh in s.shapes:
        if sh.name == "title" and sh.has_text_frame:
            titles.append((i, sh.text_frame.text.strip()))
src_i = [i for i, t in titles if t == AFTER_TITLE]
assert len(src_i) == 1, titles
DEST = src_i[0] + 1
print("inserting at position", DEST + 1)

layout = next(l for l in prs.slide_layouts if l.name == "Blank")
s = prs.slides.add_slide(layout)
for sh in list(s.shapes):
    sh._element.getparent().remove(sh._element)

def E(v): return Inches(v)

def text(x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None, spc=None):
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
        for t, sz, b, col, fnt in runs:
            r = p.add_run(); r.text = t
            r.font.size = Pt(sz); r.font.bold = b; r.font.name = fnt
            r.font.color.rgb = col
    return tb

# ------------------------------------------------------------------ header
text(1.20, 0.78, 17.60, 0.34,
     [[("RESULTS  ·  THE SECOND FLOOR", 16, True, ROSE, MM)]], name="kicker")
text(1.20, 1.20, 17.60, 0.82,
     [[("What the placebo did to the result", 40, True, BLACK, MB)]], name="title")
text(1.20, 2.12, 17.60, 0.50,
     [[("Group 4 asks whether a gap beats noise from a different vignette. The placebo "
        "asks whether it beats an inert edit to the same one. An effect has to clear both.",
        19, False, BODYCOL, MM)]], name="sub")
ln = s.shapes.add_connector(1, E(1.20), E(2.88), E(18.80), E(2.88))
ln.line.color.rgb = ROSE; ln.line.width = Pt(1.0)

# ------------------------------------------------------------------ three stats
STATS = [
    (f"{N_GATE} → {N_BOTH}", "of 10 models survive both floors",
     f"All {N_GATE} models that read the sex parameter clear their own Group 4 gender "
     f"floor. None clears its own placebo floor, so no effect is yet separable from "
     f"the instrument."),
    (f"{worst.placebo_worst_abs:.3f}", "moved by eye colour alone",
     f"On the prostate vignette an inert edit moves OLMo-2-7B-Instruct by "
     f"{worst.placebo_worst_abs:.3f}. The sex parameter moves it "
     f"{worst.gender_margin_abs:.3f}, nearly three times less."),
    # NOT a survivor. Nothing survives the gate. This is the single strongest
    # case, measured per vignette, and the preregistered aggregation throws it
    # away. Labelling it "survives" read as a contradiction of the 3 -> 0 above.
    (f"{best.ratio_gender_over_placebo:.1f}×", "the best case, discarded by design",
     f"On cervical screening the same model moves {best.gender_margin_abs:.3f} for the "
     f"sex parameter against that vignette's own placebo of {best.placebo_worst_abs:.4f}. "
     f"The gate weighs a model against the WORST placebo anywhere in its set, so this "
     f"case is discarded by design, not by result."),
]
for i, (big, lab, body) in enumerate(STATS):
    x = 1.20 + i * 6.035
    text(x, 3.18, 5.53, 0.95, [[(big, 62, True, ACCENT, MB)]])
    text(x, 4.18, 5.53, 0.40, [[(lab, 19, True, BLACK, PB)]])
    text(x, 4.64, 5.53, 1.40, [[(body, 15, False, BODYCOL, MM)]])

# ------------------------------------------------------------------ panels
PY_, PH_ = 6.30, 4.18
for x, w, head in [(1.20, 10.55, "EVERY MODEL THAT CLEARED THE GENDER FLOOR FAILS THE PLACEBO FLOOR"),
                   (12.25, 6.55, f"PER VIGNETTE, FOR THE {N_GATE} THAT READ THE SEX PARAMETER")]:
    p = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, E(x), E(PY_), E(w), E(PH_))
    p.adjustments[0] = 0.045
    p.fill.solid(); p.fill.fore_color.rgb = CREAM
    p.line.color.rgb = ROSE; p.line.width = Pt(1.0)
    p.shadow.inherit = False; p.text_frame.text = ""
    text(x + 0.30, PY_ + 0.28, w - 0.60, 0.30, [[(head, 13.5, True, ROSE, MM)]])

# --- how to read the chart. The Group 2 series is the EFFECT; without it the
# two floors have nothing to be compared against and the panel says nothing.
text(1.50, 6.92, 9.95, 0.34,
     [[("The dark red bar on top of each model is the effect: how far its answer "
        "moves on Group 2, the only vignettes where the guideline's own answer "
        "depends on the sex parameter. The two slate bars below it are the noise "
        "the effect has to beat. It beats one of them.", 11.5, True, BODYCOL, MM)]])

# --- chart
cd = CategoryChartData()
cd.categories = [SHORT[m] for m in reversed(ORDER)]
# pptx draws the FIRST series lowest in each cluster, so the effect is added
# last and sits on top of the two floors it has to clear.
cd.add_series("placebo floor",
              tuple(float(sens.loc[m, "placebo_floor_max"]) for m in reversed(ORDER)))
cd.add_series("Group 4 gender floor",
              tuple(float(sens.loc[m, "nuisance_floor"]) for m in reversed(ORDER)))
cd.add_series("gender margin (Group 2)",
              tuple(float(sens.loc[m, "mean_margin"]) for m in reversed(ORDER)))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED,
                        E(1.50), E(7.34), E(9.95), E(2.91), cd)
ch = gf.chart
ch.has_title = False
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(11); ch.legend.font.name = "+mn-lt"; ch.legend.font.color.rgb = BODYCOL
plot = ch.plots[0]
plot.gap_width = 60
plot.overlap = -10
plot.has_data_labels = True
dl = plot.data_labels
dl.number_format = "0.000"; dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size = Pt(10); dl.font.bold = True; dl.font.name = "+mn-lt"
dl.font.color.rgb = BODYCOL
for ser, col in zip(plot.series, (SLATE, SLATE_L, ACCENT)):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = col
    ser.format.line.fill.background()
va, ca = ch.value_axis, ch.category_axis
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = RGBColor(0xE4, 0xD6, 0xD6)
va.major_gridlines.format.line.width = Pt(0.75)
va.minimum_scale = 0
va.maximum_scale = 0.15
va.tick_labels.number_format = "0.00"; va.tick_labels.number_format_is_linked = False
for ax in (va, ca):
    ax.tick_labels.font.size = Pt(11)
    ax.tick_labels.font.name = "+mn-lt"
    ax.tick_labels.font.color.rgb = BODYCOL
    ax.format.line.color.rgb = RGBColor(0xD8, 0xC8, 0xC8)
ca.has_major_gridlines = False

# --- per-vignette matrix: 3 vignettes down, the 3 models across
MUTED_G = RGBColor(0x8C, 0x8C, 0x8C)
rx = 12.55
text(rx, 6.94, 5.95, 0.46,
     [[("Each cell is the gender gap on that vignette as a multiple of that vignette's "
        "own placebo movement. Above 1.00\u00d7 the gap clears.",
        11, False, RGBColor(0x89,0x89,0x89), MM)]])
COLX = [rx + 2.40, rx + 3.60, rx + 4.80]
SHORTC = {"Qwen/Qwen3-8B": "Qwen3-8B",
          "allenai/OLMo-2-1124-7B-Instruct": "OLMo-Inst",
          "allenai/OLMo-2-1124-7B": "OLMo base"}
hy = 7.56
for cx, m in zip(COLX, ORDER):
    text(cx, hy, 1.15, 0.26, [[(SHORTC[m], 11, True, BLACK, PB)]], align=PP_ALIGN.RIGHT)
hl = s.shapes.add_connector(1, E(rx), E(hy + 0.30), E(rx + 5.95), E(hy + 0.30))
hl.line.color.rgb = RGBColor(0xDC, 0xC2, 0xC2); hl.line.width = Pt(0.75)
ry = hy + 0.44
for vid in ("G2-01b", "G2-02", "G2-03b"):
    text(rx, ry, 2.30, 0.30, [[(VIG[vid], 11.5, False, BODYCOL, MM)]],
         anchor=MSO_ANCHOR.MIDDLE)
    for cx, m in zip(COLX, ORDER):
        r = det[(det.model_id == m) & (det.vignette_id == vid)].iloc[0]
        ok = bool(r.clears_own_placebo)
        text(cx, ry, 1.15, 0.30,
             [[(f"{r.ratio_gender_over_placebo:,.2f}\u00d7", 13 if ok else 12,
                True, ACCENT if ok else MUTED_G, PB)]],
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    ry += 0.50
text(rx, ry + 0.12, 5.95, 0.62,
     [[(f"{n_clear} of {n_pairs} pairs clear, shown in red. These cells are the "
        "sensitivity check, not the result: they show what the preregistered gate "
        "costs, which is the honest way round.",
        11, False, RGBColor(0x89,0x89,0x89), MM)]])
print("right panel bottom:", round(ry + 0.74, 2), "panel ends", PY_ + PH_)
assert ry + 0.74 < PY_ + PH_ - 0.05, (ry, PY_ + PH_)

text(1.20, 10.56, 17.60, 0.46,
     [[(f"Nothing survives the preregistered gate, and the {best.ratio_gender_over_placebo:.1f}× "
        "cell is not an exception to it: the gate weighs each model against the worst "
        "placebo anywhere in its set. The maximum was fixed as the aggregation before "
        f"any placebo number was seen. Under the mean it would read 1 of {N_MODELS}, "
        "which is why the choice had to be made first.", 15, True, ACCENT, MM)]])

# ------------------------------------------------------------------ move into place
lst = prs.slides._sldIdLst
el = list(lst)[-1]
lst.remove(el)
lst.insert(DEST, el)

prs.save(OUT)
print("saved", OUT, "slides:", len(Presentation(OUT).slides))
