"""Copy four slides out of the seven-minute stepped deck into the reviewed pitch.

The pitch cannot be given without these four beats, and they already exist,
drawn the way we want them:

  s05  Hold the biology fixed. Vary only the identity.
  s06  From one matrix to the scored corpus
  s07  Four groups, so the instrument can be caught lying
  s08  Three ways this harness could lie to us

THESE ARE THE SLIDES THEMSELVES, NOT A REDRAW. The two decks are built from the
same kit: same 13.33 x 7.5 canvas, same "Datasheet to Diagnosis" theme, same
five layouts. So every shape, colour, word, placeholder and speaker note is
carried straight over and nothing has to be adjusted to make it look right.

The script still checks all three of those things rather than assuming them, and
if a future target differs it says so and stops instead of producing a slide
that is subtly wrong. The four slides carry no pictures, charts, connectors or
groups and no relationship references at all, which is what makes the copy
clean in the first place.

Each slide is inserted immediately before the slide it sets up, and is added to
the same PowerPoint section as its neighbour so the section panel stays right.
Run from the project root.
"""
import copy
import sys

from pptx import Presentation

SRC = "Datasheet_to_Diagnosis_7min_Stepped.pptx"
DECK = sys.argv[1] if len(sys.argv) > 1 else "Datasheet_to_Diagnosis_5min_Pitch_ Reviewed.pptx"
OUT = sys.argv[2] if len(sys.argv) > 2 else DECK

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
P14 = "{http://schemas.microsoft.com/office/powerpoint/2010/main}"

def text_of(sl):
    return "\n".join(sh.text_frame.text for sh in sl.shapes if sh.has_text_frame)

def first_line(sl):
    return next((sh.text_frame.text.strip().split("\n")[0] for sh in sl.shapes
                 if sh.has_text_frame and sh.text_frame.text.strip()), "")

def starts(t):
    return lambda sl: first_line(sl).startswith(t)

# source slide, and the slide in the pitch it goes in front of. The order here
# is the order they are built; placement is worked out separately.
WANTED = [
    (5, "matrix",  starts("Every commitment decided something in the build")),
    (6, "scale",   starts("Every commitment decided something in the build")),
    (7, "groups",  starts("Before trusting any null")),
    (8, "defence", starts("Before trusting any null")),
]
# within one insertion point, the order the four appear
SEQUENCE = {"matrix": ["matrix", "scale"], "groups": ["groups", "defence"]}

def copy_notes(s_sl, d_sl):
    """Carry the speaker notes over as the shapes they are.

    This kit writes a bare notes master with no placeholders in it, so a notes
    slide created from that master has nowhere to put text and python-pptx
    hands back None for its text frame. The source notes slide holds no
    relationship references of its own, only the two (notes master, slide) that
    are rewired on creation, so its whole shape tree can simply be moved across.
    """
    if not s_sl.has_notes_slide:
        return ""
    s_notes, d_notes = s_sl.notes_slide, d_sl.notes_slide
    tree = d_notes.shapes._spTree
    for sh in list(d_notes.shapes):
        sh._element.getparent().remove(sh._element)
    for child in s_notes.shapes._spTree:
        if child.tag in (f"{P}nvGrpSpPr", f"{P}grpSpPr"):
            continue
        tree.append(copy.deepcopy(child))
    return s_notes.notes_text_frame.text


# --------------------------------------------------------------- compatibility
src = Presentation(SRC)
prs = Presentation(DECK)

def theme_of(p):
    part = p.slide_masters[0].part.part_related_by(
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme")
    return part.blob.decode()

import re
def fonts(p):
    x = theme_of(p)
    return (re.search(r'<a:majorFont><a:latin typeface="([^"]*)"', x).group(1),
            re.search(r'<a:minorFont><a:latin typeface="([^"]*)"', x).group(1))

assert (src.slide_width, src.slide_height) == (prs.slide_width, prs.slide_height), (
    f"different canvas: source {src.slide_width}x{src.slide_height}, "
    f"target {prs.slide_width}x{prs.slide_height}. These slides are absolutely "
    "positioned, so they would land in a corner. Scale them or pick another deck.")
assert fonts(src) == fonts(prs), (
    f"different theme fonts: source {fonts(src)}, target {fonts(prs)}. Most runs "
    "in these slides name no font and would change face on arrival.")
SRC_LAYOUTS = {l.name for l in src.slide_layouts}
DST_LAYOUTS = {l.name: l for l in prs.slide_layouts}
missing = SRC_LAYOUTS - set(DST_LAYOUTS)
assert not missing, (f"the target has no layout named {sorted(missing)}, so the "
                     "placeholders on these slides would inherit nothing.")
print(f"source {SRC}")
print(f"target {DECK}")
print(f"canvas {prs.slide_width/914400:.2f} x {prs.slide_height/914400:.2f} in, "
      f"theme fonts {fonts(prs)}, layouts match")

GUARD = "cell00"                             # unique to the matrix slide
already = [i for i, sl in enumerate(prs.slides, 1)
           if any(sh.name == GUARD for sh in sl.shapes)]
assert not already, (f"these slides are already in the deck, at {already}. "
                     "Delete them in PowerPoint before running this again.")

# every anchor is resolved against the deck as it stands, before anything moves
anchors = {}
for n, key, pred in WANTED:
    hits = [i for i, sl in enumerate(prs.slides) if pred(sl)]
    assert hits, f"{key}: found no slide to sit in front of"
    anchors[key] = hits[0]                   # the FIRST of a click-build run
print("insert before:", {k: f"{v + 1} ({first_line(prs.slides[v])[:40]})"
                         for k, v in sorted(anchors.items())})

# --------------------------------------------------------------------- the copy
copied = {}
for n, key, _ in WANTED:
    s_sl = src.slides[n - 1]
    layout = DST_LAYOUTS[s_sl.slide_layout.name]

    d_sl = prs.slides.add_slide(layout)
    for sh in list(d_sl.shapes):             # drop the placeholders it seeds
        sh._element.getparent().remove(sh._element)

    tree = d_sl.shapes._spTree
    kept = 0
    for child in s_sl.shapes._spTree:
        if child.tag in (f"{P}nvGrpSpPr", f"{P}grpSpPr"):
            continue                         # the destination has its own
        tree.append(copy.deepcopy(child))
        kept += 1

    notes = copy_notes(s_sl, d_sl)

    copied[key] = d_sl
    print(f"  s{n:02d}  {first_line(s_sl)[:48]:50s} {kept} shapes on {layout.name}, "
          f"{len(notes.split())} words of notes")

# ---------------------------------------------------------------- the placement
# The new slides were appended to the end. Lift them out and drop each group in
# from the bottom up, so the anchors resolved above keep their index.
lst = prs.slides._sldIdLst
els = {key: e for key, e in zip(copied, list(lst)[-len(copied):])}
for e in els.values():
    lst.remove(e)
for key in sorted(SEQUENCE, key=lambda k: anchors[k], reverse=True):
    for offset, member in enumerate(SEQUENCE[key]):
        lst.insert(anchors[key] + offset, els[member])

# ----------------------------------------------------------------- the sections
# A slide that is in no section lands in a stray "Default" one in the section
# panel. Each new slide joins the section its neighbour is already in.
secs = prs.part._element.find(f".//{P14}sectionLst")
if secs is None:
    print("no sections in this deck, nothing to register")
else:
    owner = {}
    for sec in secs.findall(f"{P14}section"):
        for sid in sec.find(f"{P14}sldIdLst").findall(f"{P14}sldId"):
            owner[sid.get("id")] = sec
    order = [e.get("id") for e in lst]
    for key, sl in copied.items():
        sid = str(els[key].get("id"))
        i = order.index(sid)
        # the first slide below it that already belongs somewhere
        sec = next((owner[order[j]] for j in range(i + 1, len(order))
                    if order[j] in owner), None)
        if sec is None:
            continue
        slst = sec.find(f"{P14}sldIdLst")
        ref = next(e for e in slst.findall(f"{P14}sldId")
                   if e.get("id") == order[next(j for j in range(i + 1, len(order))
                                                if order[j] in owner)])
        new = slst.makeelement(f"{P14}sldId", {"id": sid})
        slst.insert(list(slst).index(ref), new)
        owner[sid] = sec
        print(f"  {first_line(sl)[:44]:46s} joins section "
              f"{sec.get('name')!r}")

prs.save(OUT)

out = Presentation(OUT)
print(f"\nsaved {OUT}  {len(out.slides)} slides")
for i, sl in enumerate(out.slides, 1):
    new = "   <= copied in" if any(
        sh.name in ("cell00", "ch-0-n", "g1-bg", "d1-fx") for sh in sl.shapes) else ""
    print(f"  {i:2d}  {first_line(sl)[:62]}{new}")
