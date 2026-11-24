"""Cascade two stale claims through the final deck.

  A. citations   15 of 25 -> 25 of 25   (references.json is now fully verified)
  B. the gate    3 of 10  -> 0 of 10    (an effect must now clear the placebo floor too)

Counts are READ from results/tables and docs/references.json, never typed.
Run from the project root.
"""
import json, sys, copy
import pandas as pd
from pptx import Presentation
from pptx.util import Pt

DECK = "Ethics In AI Final Presentation.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else DECK

# ---- facts
reg = pd.read_csv("results/tables/i4_placebo_regate.csv")
N_MODELS = len(reg)
N_GATE = int((reg["gate"] == "SENSITIVE").sum())
N_BOTH = int((reg["gate_both_floors"] == "SENSITIVE").sum())
pt = pd.read_csv("results/tables/rq2c_post_training_contrast.csv").iloc[0]
PT_RATIO = pt.merging_tuned / pt.merging_base
PT_TIMES = pt.times_combined_floor
gl = json.load(open("docs/references.json"))["guidelines"]
N_CITE = sum(1 for v in gl if v["status"] == "verified")
N_VIG = sum(len(v["vignettes"]) for v in gl)
assert N_CITE == N_VIG == 25, (N_CITE, N_VIG)
print(f"models {N_MODELS}  gate {N_GATE} -> both {N_BOTH}  citations {N_CITE}/{N_VIG}")

prs = Presentation(DECK)

def shape(idx, name):
    for sh in prs.slides[idx].shapes:
        if sh.name == name:
            return sh
    raise KeyError(f"slide {idx+1}: no shape {name!r}")

def set_run(idx, name, old, new, run=0, para=0):
    """Replace one run's text, keeping its formatting."""
    r = shape(idx, name).text_frame.paragraphs[para].runs[run]
    assert r.text == old, f"slide {idx+1} {name}: expected\n  {old!r}\ngot\n  {r.text!r}"
    r.text = new
    print(f"  slide {idx+1} {name}: rewritten")

def append_run(idx, name, text, bold=True, para=0):   # kept, currently unused
    p = shape(idx, name).text_frame.paragraphs[para]
    src = p.runs[-1]
    r = p.add_run(); r.text = text
    r.font.size = src.font.size; r.font.name = src.font.name
    r.font.bold = bold
    if src.font.color and src.font.color.type is not None:
        try:
            r.font.color.rgb = src.font.color.rgb
        except Exception:
            pass
    print(f"  slide {idx+1} {name}: appended")

def text_sub(name, old, new):
    """Replace a substring in a named textbox, wherever that slide ended up.

    Unlike set_run/cell_sub this does not take a slide index. The two steps that
    run before this one insert slides, so every index in this file is already an
    offset of an offset; a claim that appears once in the deck is safer found by
    its shape name and its own words.
    """
    hits = []
    for i, sl in enumerate(prs.slides, 1):
        for sh in sl.shapes:
            if sh.name != name or not sh.has_text_frame:
                continue
            for para in sh.text_frame.paragraphs:
                for r in para.runs:
                    if old in r.text:
                        r.text = r.text.replace(old, new); hits.append(i)
    assert len(hits) == 1, f"{name}: {len(hits)} hits for {old!r}"
    print(f"  slide {hits[0]} {name}: rewritten")


def cell_sub(idx, old, new):
    """Replace a substring inside a table cell, across whichever run holds it."""
    hits = 0
    for sh in prs.slides[idx].shapes:
        if not sh.has_table:
            continue
        for row in sh.table.rows:
            for c in row.cells:
                for p in c.text_frame.paragraphs:
                    for r in p.runs:
                        if old in r.text:
                            r.text = r.text.replace(old, new); hits += 1
    assert hits == 1, f"slide {idx+1}: {hits} hits for {old!r}"
    print(f"  slide {idx+1} table: rewritten")

print("\n-- A. citations")
set_run(15, "TextBox 5",
        "Tier 1 result, pending clinical validation. 15 of 25 vignette-guideline "
        "pairs carry a first-hand citation of record.",
        f"Tier 1 result, pending clinical validation. All {N_CITE} of {N_VIG} "
        "vignette-guideline pairs carry a first-hand citation of record.")
set_run(22, "TextBox 9",
        "15 of 25 vignette-guideline pairs carry a first-hand citation of record, "
        "3 are identified but unread and 7 pending. No clinician has signed off a "
        "vignette yet.",
        f"All {N_CITE} of {N_VIG} vignette-guideline pairs now carry a first-hand "
        "citation of record. No clinician has signed off a vignette yet, so every "
        "result stands at Tier 1.")

print("\n-- B. the gate")
cell_sub(15,
         "up to 21.5× the model's own noise floor.",
         f"up to 21.5× the model's own noise floor. None of the {N_GATE} "
         "clears the placebo floor as well.")
cell_sub(15,
         "shows the second-largest merging effect, 19.7× its floor.",
         "shows the second-largest merging effect, 19.7× its gender floor, "
         "though not its placebo floor.")
set_run(20, "TextBox 8",
        "Among the 3 that pass, the identity label is read as the clinical sex "
        "parameter, up to 21.5 times the model's own floor. Instruction tuning on "
        "the same corpus multiplied it 11-fold.",
        f"Among the {N_GATE} that pass, identity is read as the clinical sex "
        "parameter, up to 21.5\u00d7 their own floor. Instruction tuning on the same "
        f"corpus more than tripled it, a rise of {PT_TIMES:.0f} combined floors. "
        "None clears the placebo floor.")
# The worked example (slide 15) deliberately says NOTHING about the placebo. It
# sits before the results section, and the placebo result is introduced there.
# This line used to be appended here and gave the finding away early. D108.
set_run(22, "TextBox 33", "Placebo-floor gating", "After the placebo floor")
set_run(22, "TextBox 34",
        "Placebo prompts are scored for all 10 models but no analysis reads them "
        "yet, so no effect has been tested against the second floor the "
        "preregistration committed to.",
        f"Now run. Clearing an inert edit to the same vignette as well as the Group 4 "
        f"floor takes the gate from {N_GATE} of {N_MODELS} to {N_BOTH} of {N_MODELS}. "
        "A true null, or too few arms to resolve one?")

print("\n-- C. the post-training ratio")
# times_combined_floor is the RISE in units of the combined floor, not the factor
# by which tuning multiplied the effect. Two slides read it as the factor and so
# claimed an 11-fold increase where the effect in fact more than tripled: 0.061
# to 0.214 is 3.5x, and it is the 0.153 RISE that is 11 combined floors. The
# paper always said this correctly, which is how the mismatch surfaced.
text_sub("TextBox 22",
         "multiplied the effect 11-fold,",
         f"more than tripled the effect,")
prs.save(OUT)
print("\nsaved", OUT)
