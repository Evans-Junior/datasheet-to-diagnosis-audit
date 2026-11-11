"""Fail a deck that renders a JavaScript non-value onto a slide (D100).

WHY THIS EXISTS. `figures.js` throws when a TABLE is missing or stale, which is
the loud failure. The quiet one is reading a FIELD that the accessor does not
expose: JavaScript yields `undefined`, the template literal interpolates it, and
the slide ships a sentence like "undefined of 10 models". Three of these reached
a rendered deck while every other check passed, because none of them was built
to look at the words.

Two of the three were worse than cosmetic. `${GR.before}` printed "undefined of
10" where the floor-geometry fix changed a gate verdict, and a filter on a field
that did not exist printed "0 of 10 models have an interpretable null" when the
true count is 6. A wrong number reads as a finding.

The word "null" is deliberately NOT a trigger: it is ordinary statistical
English in this deck ("not a null result", "the Pythia nulls").

Usage:  python deck_src/qa_tokens.py <deck.pptx> [...]
"""

from __future__ import annotations

import re
import sys
import zipfile

# Tokens that no slide should ever contain. Each is a JavaScript value that
# only appears by accident.
BAD = ("undefined", "NaN", "[object Object]", "Infinity", "${")


def check(path: str) -> int:
    z = zipfile.ZipFile(path)
    names = sorted(n for n in z.namelist()
                   if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    hits = []
    for n in names:
        text = " ".join(re.findall(r"<a:t>(.*?)</a:t>",
                                   z.read(n).decode("utf-8")))
        for tok in BAD:
            start = 0
            while (i := text.find(tok, start)) != -1:
                hits.append((n, tok, text[max(0, i - 70):i + 70]))
                start = i + len(tok)
    # Speaker notes too: a note read aloud is as public as a slide.
    for n in sorted(x for x in z.namelist()
                    if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", x)):
        text = " ".join(re.findall(r"<a:t>(.*?)</a:t>", z.read(n).decode("utf-8")))
        for tok in BAD:
            if tok in text:
                i = text.find(tok)
                hits.append((n, tok, text[max(0, i - 70):i + 70]))

    print(f"{path}: {len(names)} slides scanned")
    if not hits:
        print("  clean: no undefined, NaN, [object Object], Infinity or "
              "unexpanded ${...}")
        return 0
    for n, tok, ctx in hits:
        print(f"  !! {n}  [{tok}]  ...{ctx}...")
    print()
    print(f"{len(hits)} occurrence(s). Each one is an accessor field that does "
          f"not exist. Find the field on the figures.js object before fixing "
          f"the slide, because the number it should have printed is probably "
          f"not the one now showing.")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(max(check(p) for p in sys.argv[1:]))
