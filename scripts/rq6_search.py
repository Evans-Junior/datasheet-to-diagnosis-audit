"""RQ6 step 2: term hit counts across the retrieved documentation.

Mechanises the search protocol in `docs/codebook.md` §4, which exists so that a
level-0 code means "absent after this specific search" rather than "I did not
find it". Doing it by hand across eight documents invites exactly the error the
protocol is written to prevent: a missed section, an unsearched synonym, and a
published absence claim that is simply false.

Zero counts are results, not missing data, and are written out as zeros.

Usage
    # one plain-text or markdown file per document, named by its inventory id
    .venv/bin/python scripts/rq6_search.py data/raw/rq6/
    -> results/tables/rq6_search_counts.csv

Each input file must carry its retrieval date on the first line as
`# retrieved: YYYY-MM-DD`, because dataset and model cards are edited without
version notice (the same failure mode D033 recorded for clinical PDFs). The
script refuses a file without one rather than recording an undated reading.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results/tables/rq6_search_counts.csv"

# Exactly the list in docs/codebook.md §4, in the same order. Kept here as the
# single source of truth for the counts; if it changes, the codebook changes
# with it and every document is recounted.
TERMS = [
    "gender", "sex", "woman", "women", "man", "men", "male", "female",
    "non-binary", "nonbinary", "transgender", "trans ", "identity",
    "demographic", "representation", "underrepresent", "skew", "imbalance",
    "bias", "stereotype", "fairness", "harm", "medical", "clinical", "health",
    "patient", "diagnosis", "pubmed", "disparity", "equity",
]

# Matching is per-term, and the two failure modes pull in opposite directions.
#
# Too loose: "sex" matches "unisex" and "sexagenarian"; "man"/"men" match "many",
# "management", "permanent", "implementation". A document would then score a hit
# on the dimensions that matter most without containing the word at all.
#
# Too strict: both-boundary matching missed "biases" in "may contain biases
# relating to gender" -- a level-1 D1 disclosure scored as absent. That is the
# dangerous direction, because RQ6's headline finding is an ABSENCE and this
# error manufactures one.
#
# So: STRICT terms take both boundaries plus an optional plural; STEM terms take
# a left boundary and any suffix ("bias" -> biases/biased, "health" ->
# healthcare/healthy, "diagnos" -> diagnosis/diagnoses/diagnostic). Anything not
# listed is matched as a plain substring.
STRICT = {"sex", "man", "men", "male", "female", "woman", "women"}
STEM = {"bias", "skew", "harm", "patient", "stereotype", "disparity",
        "identity", "demographic", "representation", "underrepresent",
        "imbalance", "equity", "fairness", "health", "medical", "clinical",
        "diagnosis", "gender", "transgender", "non-binary", "nonbinary"}

# Terms whose listed spelling is not the stem to match on.
STEM_OVERRIDE = {"diagnosis": "diagnos", "representation": "represent",
                 "identity": "identit", "disparity": "disparit",
                 "equity": "equit"}

DATE_RE = re.compile(r"^#\s*retrieved:\s*(\d{4}-\d{2}-\d{2})\s*$", re.I)


def pattern(term: str) -> str:
    if term in STRICT:
        return rf"\b{re.escape(term)}s?\b"
    if term in STEM:
        return rf"\b{re.escape(STEM_OVERRIDE.get(term, term))}\w*"
    return re.escape(term)


def count(text: str, term: str) -> int:
    return len(re.findall(pattern(term), text, flags=re.I))


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    files = sorted(f for f in src.rglob("*")
                   if f.suffix.lower() in {".txt", ".md"} and f.is_file())
    if not files:
        sys.exit(f"no .txt or .md files under {src}. Retrieve the documents "
                 f"listed in docs/codebook.md §2 first.")

    rows, undated = [], []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        first = text.split("\n", 1)[0]
        m = DATE_RE.match(first.strip())
        if not m:
            undated.append(f.name)
            continue
        for t in TERMS:
            rows.append({"document": f.stem, "retrieved": m.group(1),
                         "term": t, "hits": count(text, t),
                         "chars": len(text)})

    if undated:
        sys.exit("refusing to count undated documents -- add "
                 "'# retrieved: YYYY-MM-DD' as the first line of:\n  "
                 + "\n  ".join(undated))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["document", "retrieved", "term",
                                           "hits", "chars"])
        w.writeheader()
        w.writerows(rows)

    docs = sorted({r["document"] for r in rows})
    print(f"counted {len(TERMS)} terms across {len(docs)} document(s)\n")
    width = max(len(d) for d in docs)
    key = ["gender", "female", "non-binary", "medical", "health", "pubmed"]
    print("  " + " ".join(f"{k:>11s}" for k in ["document".ljust(width)] + key))
    for d in docs:
        hits = {r["term"]: r["hits"] for r in rows if r["document"] == d}
        print("  " + f"{d:<{width}}" + " "
              + " ".join(f"{hits.get(k, 0):>11d}" for k in key))
    zero = [d for d in docs
            if all(r["hits"] == 0 for r in rows
                   if r["document"] == d and r["term"] in
                   {"gender", "female", "male", "woman", "women"})]
    if zero:
        print(f"\nno gender term at all in: {', '.join(zero)} "
              f"-- D1 level 0, and §4 steps 1 and 3 still required")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
