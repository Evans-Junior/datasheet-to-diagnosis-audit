"""Build the RQ6 coding worksheet: candidate passages, and a blank code sheet.

Codebook §5 says the unit of CODING is the document and the unit of EVIDENCE is
the passage. This script produces one file for each, so the coders spend their
time judging passages rather than hunting for them in 64-page PDFs.

What it does NOT do is assign a code. It cannot: every dimension in the codebook
turns on a judgement the extraction has no access to -- whether a sentence makes
a claim about THIS corpus or about corpora in general (D1 1-vs-2), whether a
number comes with a method (D1 2-vs-3), whether two topics are genuinely related
or merely adjacent (D4). The terms are mechanical; the codes are not.

The candidate tagging is deliberately OVER-INCLUSIVE. A passage tagged for a
dimension is one the coder must look at, not one that scores above 0 on it. The
cost of a false candidate is thirty seconds of reading; the cost of a missed one
is an absence claim that is simply wrong, which is the failure mode codebook §1
is written against.

Outputs
  docs/rq6_passages.csv      candidate evidence, with the dimensions it may bear on
  docs/rq6_coding_sheet.csv  document x dimension, blank, one column per coder
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/raw/rq6"
PASSAGES = ROOT / "docs/rq6_passages.csv"
SHEET = ROOT / "docs/rq6_coding_sheet.csv"

DIMENSIONS = [
    ("D1", "gender composition of the corpus", "0-3"),
    ("D2", "gender-related downstream risk", "0-3"),
    ("D3", "health or medical content acknowledgement", "0-3"),
    ("D4", "health x demographic intersection", "0-3"),
    ("D5", "gender identity beyond the binary", "0-3"),
    ("D6", "stated scope of appropriate use", "0-3"),
    ("D7", "measurement / assertion / reported", "M|A|R"),
    ("D8", "traceability", "T|P|N"),
]

DEM = r"\b(gender\w*|sex|sexes|female\w*|male\w*|wom[ae]n|m[ae]n\b|demographic\w*)"
NB = r"(non-?binary|transgender|\btrans\b|gender identit\w*)"
HEALTH = r"\b(medical\w*|clinical\w*|health\w*|patient\w*|diagnos\w*|biomedical|PubMed)"
COMPOSITION = r"(distribut\w*|proportion\w*|percent\w*|\d+\s?%|skew\w*|imbalanc\w*|" \
              r"represent\w*|compos\w*|frequenc\w*|co-?occurr\w*|over-?represent\w*)"
RISK = r"(harm\w*|risk\w*|bias\w*|stereotyp\w*|unfair\w*|fairness|disparit\w*)"
SCOPE = r"(out of scope|not intended|should not be used|not be used|" \
        r"research purposes|research only|as-?is|no warrant\w*|" \
        r"recommend that users|intended use|limitations)"

# Architectural "bias" is not social bias. Without this, the OLMo 2 report looks
# like it discusses bias five times when every instance is a transformer bias
# term -- which would turn a real absence into a false presence.
ARCH_BIAS = re.compile(r"bias(es)?\s+term|no\s+bias(es)?\b|without\s+a\s+bias|"
                       r"exclude\s+all\s+bias|Biases\s+None", re.I)


def candidates(s: str) -> list[str]:
    tags = []
    has_dem, has_health = re.search(DEM, s, re.I), re.search(HEALTH, s, re.I)
    social_risk = re.search(RISK, s, re.I) and not ARCH_BIAS.search(s)
    if has_dem and re.search(COMPOSITION, s, re.I):
        tags.append("D1")
    if has_dem and social_risk:
        tags.append("D2")
    if has_health:
        tags.append("D3")
    if has_dem and has_health:
        tags.append("D4")
    if re.search(NB, s, re.I):
        tags.append("D5")
    if re.search(SCOPE, s, re.I):
        tags.append("D6")
    return tags


def is_junk(s: str) -> bool:
    """Drop reference entries and extracted table dumps.

    Both are long strings of comma- or number-separated fragments that match
    terms without being prose. Kept conservative: a dropped passage is invisible
    to the coder, so the test is narrow and anything borderline survives.
    """
    if len(s) < 60 or len(s) > 900:
        return True
    if re.search(r"arXiv:\d{4}\.\d{4,5}|et al\., 20\d\d\.|preprint", s):
        return True
    digits = sum(c.isdigit() for c in s)
    return digits / max(len(s), 1) > 0.18 or s.count(",") > 14


def main() -> None:
    docs = sorted(f for f in SRC.glob("*.md"))
    if not docs:
        raise SystemExit(f"no documents in {SRC}. Run scripts/rq6_fetch.py first.")

    rows, counts = [], {}
    for f in docs:
        text = re.sub(r"\s+", " ", f.read_text(encoding="utf-8"))
        retrieved = ""
        m = re.search(r"# retrieved: (\d{4}-\d{2}-\d{2})", text)
        if m:
            retrieved = m.group(1)
        n = 0
        for s in re.split(r"(?<=[.!?]) +", text):
            s = s.strip()
            if is_junk(s):
                continue
            tags = candidates(s)
            if not tags:
                continue
            n += 1
            rows.append({
                "passage_id": f"{f.stem.split('_')[0]}-{n:03d}",
                "document": f.stem, "retrieved": retrieved,
                "candidate_dimensions": " ".join(tags),
                "quote": s,
                "locator_authors_fill": "",
            })
        counts[f.stem] = n

    with PASSAGES.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    sheet = []
    for f in docs:
        for dim, label, scale in DIMENSIONS:
            sheet.append({
                "document": f.stem, "dimension": dim, "what_it_asks": label,
                "scale": scale,
                "evans_code": "", "evans_passage_ids": "", "evans_quote": "",
                "aymen_code": "", "aymen_passage_ids": "", "aymen_quote": "",
                "agreed_code": "", "adjudication_rule_added": "",
                "search_steps_done_1_read_2_terms_3_structural": "",
            })
    with SHEET.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sheet[0]))
        w.writeheader()
        w.writerows(sheet)

    print(f"candidate passages per document:")
    for k, v in counts.items():
        print(f"  {v:>4d}  {k}")
    print(f"\n{len(rows)} passages -> {PASSAGES}")
    print(f"{len(sheet)} rows ({len(docs)} docs x {len(DIMENSIONS)} dims) -> {SHEET}")


if __name__ == "__main__":
    main()
