"""Split the scoring slide in two, and cut the repetition out of the second half.

Before: one slide carried the three ways the harness could manufacture a result
AND the four instrument tests, 40 shapes, read in about four minutes.

After:
  A.  the three guards, with the panels grown into the space the tests vacated
  B.  the four tests, with T2 signal recovery given the whole left half and T1,
      T3 and T4 reduced to one line each. T1 (determinism), T3 (the nuisance
      floor) and T4 (the pmi choice) are already explained on slide A, in the
      PMI panel and the matched-floor panel, so going deeper into them spent
      time on the audience's second hearing of the same three facts.

Every figure on slide B is READ from results/tables/rq0_instrument_validation__*.json
and i4_placebo_regate.csv. D110. Run from the project root.
"""
import sys, json, glob
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK
TITLE_TEXT = "Scoring, and proving the instrument works"

INK, MUTED = RGBColor(0x1A,0x1A,0x1A), RGBColor(0x70,0x70,0x70)
GREY = RGBColor(0x89,0x89,0x89)
WHITE, CREAM = RGBColor(0xFF,0xFF,0xFF), RGBColor(0xF8,0xEB,0xEB)
ROSE = RGBColor(0xC8,0x62,0x62)
ACCENT = RGBColor(0x8D,0x00,0x00)
RED_TINT = RGBColor(0xFB,0xE2,0xDF)
HAIR = RGBColor(0xDC,0xC2,0xC2)
SLATE = RGBColor(0x3F,0x4C,0x5A)
SLATE_T = RGBColor(0xED,0xF1,0xF4)
HEAD, HEADB, BODY = "Montserrat Medium", "Montserrat Bold", "Poppins"
BODYB, MONO = "Poppins Bold", "Courier New"

# ------------------------------------------------------------------ facts
SHORT = {"EleutherAI/pythia-70m": "pythia-70m", "EleutherAI/pythia-160m": "pythia-160m",
         "EleutherAI/pythia-410m": "pythia-410m", "EleutherAI/pythia-1b": "pythia-1b",
         "EleutherAI/pythia-1.4b": "pythia-1.4b", "EleutherAI/pythia-2.8b": "pythia-2.8b",
         "EleutherAI/pythia-6.9b": "pythia-6.9b", "Qwen/Qwen3-8B": "Qwen3-8B",
         "allenai/OLMo-2-1124-7B": "OLMo-2-7B (base)",
         "allenai/OLMo-2-1124-7B-Instruct": "OLMo-2-7B-Instruct"}
rows, t1_drift, t4_sum = [], [], []
QUESTION, OPTIONS = None, None
for f in sorted(glob.glob("results/tables/rq0_instrument_validation__*.json")):
    d = json.load(open(f)); t = d["tests"]
    QUESTION = QUESTION or d["question"]
    OPTIONS = OPTIONS or d["options"]
    pmi = t["T2_signal_recovery"]["by_score_key"]["pmi"]
    rows.append(dict(model=d["model"], passed=bool(t["T2_signal_recovery"]["pass"]),
                     ok=sum(1 for r in pmi if r["recovered"]), n=len(pmi),
                     pmin=min(r["p_stated"] for r in pmi)))
    t1_drift.append(t["T1_determinism"]["max_abs_pmi_drift"])
    t4_sum.append(t["T4_score_key"]["by_score_key"]["sum_logprob"]["p_mass_on_short_options"])
N_MODELS = len(rows)
PASS = [r for r in rows if r["passed"]]
FAIL = sorted([r for r in rows if not r["passed"]], key=lambda r: r["pmin"])
T1_DRIFT, T4_SUM = max(t1_drift), min(t4_sum)
reg = pd.read_csv("results/tables/i4_placebo_regate.csv")
FL_LO, FL_HI = reg.nuisance_floor.min(), reg.nuisance_floor.max()
assert len(FAIL) + len(PASS) == N_MODELS == 10, (len(PASS), len(FAIL))
print(f"T2 {len(PASS)} of {N_MODELS}; fail: {[SHORT[r['model']] for r in FAIL]}")
print(f"T1 max drift {T1_DRIFT}; T4 sum_logprob short-mass min {T4_SUM:.3f}; "
      f"floor {FL_LO:.4f}-{FL_HI:.4f}")

# ------------------------------------------------------------------ slide A
prs = Presentation(DECK)
hits = [i for i, sl in enumerate(prs.slides)
        if any(sh.name == "title" and sh.has_text_frame
               and sh.text_frame.text.strip() == TITLE_TEXT for sh in sl.shapes)]
assert len(hits) == 1, hits
IDX = hits[0]
a = prs.slides[IDX]
print("scoring slide is at position", IDX + 1)

def named(sl, n):
    return next(sh for sh in sl.shapes if sh.name == n)

def retext(sl, name, new, size=None):
    """Replace a single-run paragraph's text, keeping its formatting."""
    p = named(sl, name).text_frame.paragraphs[0]
    p.runs[0].text = new
    for r in p.runs[1:]:
        r.text = ""
    if size is not None:
        p.runs[0].font.size = Pt(size)

# the tests move to slide B
dropped = 0
for sh in list(a.shapes):
    if Emu(sh.top).inches >= 7.20:
        sh._element.getparent().remove(sh._element); dropped += 1
print("shapes moved off slide A:", dropped)
assert dropped == 22, dropped   # TextBox 19 + 4 panels + 16 labels + TextBox 40

retext(a, "title", "Three ways the harness could manufacture a result")
retext(a, "sub", "Each guard below is in the scoring code, not in the write-up. "
                 "The tests that prove the scorer itself works are on the next slide.")

# grow the three panels into the freed space
for n in ("Rounded Rectangle 5", "Rounded Rectangle 11", "Rounded Rectangle 15"):
    named(a, n).height = Inches(5.90)
for n, y, h in (("TextBox 10", 5.85, 2.70), ("TextBox 14", 4.95, 3.80),
                ("TextBox 18", 4.95, 3.80)):
    sh = named(a, n)
    sh.top, sh.height = Inches(y), Inches(h)
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if r.font.size:
                r.font.size = Pt(r.font.size.pt + 4)

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
Atext(1.20, 9.26, 17.60, 0.42,
      [[("All three are decisions about the scorer, taken before any vignette was "
         "run. The next slide is the evidence that the scorer, so built, works.",
         15, True, ACCENT, HEAD)]])

# ------------------------------------------------------------------ slide B
b = prs.slides.add_slide(a.slide_layout)
for sh in list(b.shapes):
    sh._element.getparent().remove(sh._element)
Btext, Bbox, Brule = mk(b)

Btext(1.20, 0.78, 17.60, 0.34,
      [[("OUTPUT AUDIT  ·  STEP 4, AND THE TEST THAT DECIDES WHAT A FLAT RESULT "
         "MEANS", 16, True, ROSE, HEAD)]])
Btext(1.20, 1.20, 17.60, 0.82,
      [[("Four tests, and only one of them changes a reading",
         40, True, RGBColor(0,0,0), HEADB)]])
Btext(1.20, 2.12, 17.60, 0.50,
      [[(f"All four ran on all {N_MODELS} models before a single vignette was scored. "
         "Three confirm the design on the slide before this one. The fourth decides "
         "whether a flat result can be read at all.",
         19, False, RGBColor(0x32,0x32,0x32), HEAD)]])
Brule(1.20, 2.88, 17.60, ROSE)

# --- T2, the whole left half
PX, PY, PW, PH = 1.20, 3.20, 11.30, 6.80
Bbox(PX, PY, PW, PH, CREAM, ACCENT, 1.75)
Bbox(PX + 0.30, PY + 0.26, 0.56, 0.52, ACCENT, rad=0.16)
Btext(PX + 0.30, PY + 0.26, 0.56, 0.52, [[("T2", 17, True, WHITE, HEADB)]],
      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
Btext(PX + 1.02, PY + 0.26, 6.00, 0.52,
      [[("SIGNAL RECOVERY", 20, True, ACCENT, HEADB)]], anchor=MSO_ANCHOR.MIDDLE)
Btext(PX + 0.30, PY + 0.88, 3.40, 0.80,
      [[(f"{len(PASS)} of {N_MODELS}", 46, True, ACCENT, HEADB)]])
Btext(PX + 3.90, PY + 0.96, PW - 4.40, 0.70,
      [[("models can recover an answer their own prompt names in plain words",
         15, True, INK, BODYB)]], anchor=MSO_ANCHOR.MIDDLE)

Btext(PX + 0.30, PY + 1.84, PW - 0.60, 0.80,
      [[("What the test is. A four-option question, nothing clinical, whose own "
         f"prompt states the answer: “{QUESTION}” with options "
         f"{', '.join(OPTIONS)}. The prompt names the right one. The scorer is "
         "asked for it back.", 14, False, MUTED, BODY)]])
Btext(PX + 0.30, PY + 2.72, PW - 0.60, 0.86,
      [[("Why it is the one that matters. A scorer that cannot recover an answer "
         "written into the prompt cannot recover a clinical effect that is not "
         "written anywhere. A flat result from such a model is an unreadable "
         "instrument, and we report it as instrument-limited, never as fairness.",
         14, True, INK, BODY)]])

Btext(PX + 0.30, PY + 3.60, PW - 0.60, 0.28,
      [[("THE FOUR THAT CANNOT, WITH THE PROBABILITY EACH PUT ON THE ANSWER ITS OWN "
         "PROMPT NAMED", 11, True, ROSE, HEAD)]])
CXs = [PX + 0.30, PX + 4.90, PX + 7.10, PX + 9.00]
CWs = [4.40, 2.00, 1.80, 1.70]
for x, w, lab, al in zip(CXs, CWs,
                         ["MODEL", "RECOVERED", "p ON THE ANSWER", "READ AS"],
                         [PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.LEFT]):
    Btext(x, PY + 3.94, w, 0.24, [[(lab, 10, True, SLATE, HEAD)]], align=al)
Brule(PX + 0.30, PY + 4.22, PW - 0.60, HAIR)
ry = PY + 4.30
for r in FAIL:
    Btext(CXs[0], ry, CWs[0], 0.40, [[(SHORT[r["model"]], 14, True, INK, BODYB)]],
          anchor=MSO_ANCHOR.MIDDLE)
    Btext(CXs[1], ry, CWs[1], 0.40,
          [[(f"{r['ok']} of {r['n']}", 14, True, ACCENT, BODYB)]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    Btext(CXs[2], ry, CWs[2], 0.40, [[(f"{r['pmin']:.3f}", 14, True, ACCENT, MONO)]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    Btext(CXs[3], ry, CWs[3], 0.40,
          [[("instrument-limited", 12, False, MUTED, BODY)]], anchor=MSO_ANCHOR.MIDDLE)
    ry += 0.42
assert ry < PY + 6.34, ry
Btext(PX + 0.30, ry + 0.10, PW - 0.60, 0.56,
      [[("It is not a size effect. pythia-70m and pythia-160m both recover the "
         "planted answer, while pythia-1b, 1.4b and 2.8b do not, and one of the "
         "three models that later passes the positive control, OLMo-2-7B base, "
         "is in this table.", 13, False, GREY, BODY)]])
print("T2 panel content bottom:", round(ry + 0.66, 2), "panel bottom", PY + PH)
assert ry + 0.66 < PY + PH - 0.10, (ry, PY + PH)

# --- T1, T3, T4: listed, not explored
QX, QW, CH, CG = 12.90, 6.40, 2.14, 0.19
CARDS = [
    ("T1", "Determinism", f"{N_MODELS} of {N_MODELS}",
     f"The same input scored twice gives bitwise-identical scores. Maximum drift "
     f"{T1_DRIFT:.3f} on every model, so no gap needs a repeat-measurement error "
     f"bar."),
    ("T3", "Nuisance floor", "measured",
     f"Not a pass or a fail. The gap on content-free prompts differing only by the "
     f"gender token IS the floor. Per model and matched on option count, "
     f"{FL_LO:.4f} to {FL_HI:.4f}."),
    ("T4", "Score-key choice", "pmi",
     f"Options matched in meaning but not in length. sum_logprob puts "
     f"{T4_SUM*100:.0f}% of its mass on the shorter option on all {N_MODELS} "
     f"models, which is the empirical reason the primary key is pmi."),
]
for i, (tag, name, verdict, body) in enumerate(CARDS):
    y = PY + i * (CH + CG)
    Bbox(QX, y, QW, CH, SLATE_T, SLATE, 1.0)
    Bbox(QX + 0.26, y + 0.24, 0.50, 0.46, SLATE, rad=0.16)
    Btext(QX + 0.26, y + 0.24, 0.50, 0.46, [[(tag, 15, True, WHITE, HEADB)]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    Btext(QX + 0.90, y + 0.24, 3.10, 0.46, [[(name, 17, True, SLATE, HEADB)]],
          anchor=MSO_ANCHOR.MIDDLE)
    Btext(QX + 4.00, y + 0.24, QW - 4.26, 0.46,
          [[(verdict, 17, True, ACCENT, BODYB)]],
          align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    Btext(QX + 0.26, y + 0.84, QW - 0.52, 1.10, [[(body, 12.5, False, MUTED, BODY)]])
assert PY + 2 * (CH + CG) + CH <= PY + PH + 1e-9

Btext(1.20, 10.18, 17.60, 0.46,
      [[("T1, T3 and T4 confirm choices already made on the slide before this one, "
         "so they are listed and not reopened. T2 is the only one that changes how "
         "a result is read, and four models fail it.", 15, True, ACCENT, HEAD)]])

# ------------------------------------------------------------------ place it
lst = prs.slides._sldIdLst
el = list(lst)[-1]
lst.remove(el)
lst.insert(IDX + 1, el)

prs.save(OUT)
print("saved", OUT, "slides:", len(Presentation(OUT).slides))
