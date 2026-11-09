"""Geometry and overflow QA without a renderer.

Substitute for the visual pass when LibreOffice and Poppler are unavailable.
Checks: shapes inside the slide with a margin, text that cannot fit its box at
the stated font size, and overlapping text frames.
"""
import math, sys
from pptx import Presentation
from pptx.util import Emu

EMU = 914400.0
P = Presentation(sys.argv[1])
W = P.slide_width / EMU
H = P.slide_height / EMU
MARGIN = 0.45          # allow slightly under 0.5 for footers
print(f"canvas {W:.2f} x {H:.2f} in,  {len(P.slides.__iter__.__self__._sldIdLst)} slides\n")

def runs_text(tf):
    return "\n".join(p.text for p in tf.paragraphs)

def max_font(tf, default=14.0):
    szs = [r.font.size.pt for p in tf.paragraphs for r in p.runs
           if r.font.size is not None]
    return max(szs) if szs else default

oob, over, ovl = [], [], []
for i, sl in enumerate(P.slides, start=1):
    frames = []
    for sh in sl.shapes:
        if sh.left is None or sh.top is None or sh.width is None or sh.height is None:
            continue
        x, y = sh.left / EMU, sh.top / EMU
        w, h = sh.width / EMU, sh.height / EMU
        nm = sh.name or sh.shape_type
        # out of bounds
        if x < MARGIN - 0.001 or y < MARGIN - 0.001 or x + w > W - MARGIN + 0.001 or y + h > H - MARGIN + 0.001:
            # footers and slide numbers sit low by design
            if not (y > 6.8 and h < 0.45):
                oob.append((i, nm, round(x,2), round(y,2), round(w,2), round(h,2)))
        if not sh.has_text_frame:
            continue
        txt = runs_text(sh.text_frame).strip()
        if not txt:
            continue
        fs = max_font(sh.text_frame)
        # crude fit model: avg glyph advance ~0.50 em, line height ~1.26 em
        cpl = max(1.0, (w * 72.0) / (0.50 * fs))
        lines = 0
        for seg in txt.split("\n"):
            lines += max(1, math.ceil(len(seg) / cpl))
        need = lines * 1.26 * fs / 72.0
        if need > h * 1.12:
            over.append((i, nm, round(fs,1), len(txt), lines, round(need,2), round(h,2)))
        frames.append((nm, x, y, w, h, txt[:28]))
    # overlapping text frames
    for a in range(len(frames)):
        for b in range(a + 1, len(frames)):
            n1,x1,y1,w1,h1,t1 = frames[a]; n2,x2,y2,w2,h2,t2 = frames[b]
            ox = min(x1+w1, x2+w2) - max(x1, x2)
            oy = min(y1+h1, y2+h2) - max(y1, y2)
            if ox > 0.12 and oy > 0.12:
                area = ox * oy
                if area > 0.30:
                    ovl.append((i, n1, n2, round(area,2), t1, t2))

def show(title, rows, hdr):
    print(f"=== {title}: {len(rows)} ===")
    if rows:
        print("  " + hdr)
        for r in rows[:40]:
            print("  " + "  ".join(str(v) for v in r))
    print()

show("OUT OF BOUNDS", oob, "slide name x y w h")
show("LIKELY TEXT OVERFLOW", over, "slide name fontpt chars lines need_in have_in")
show("OVERLAPPING TEXT FRAMES", ovl, "slide a b area t_a t_b")
