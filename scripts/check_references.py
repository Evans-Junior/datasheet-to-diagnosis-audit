"""Stop a deck shipping a reference list that does not match the study (D101).

WHY THIS EXISTS. Slides grow citations by hand, and a hand-maintained reference
list drifts in both directions: a vignette gets added and never acquires a
citation, or a citation outlives the vignette it supported. Neither is visible
on the slide, and a reference list that is quietly incomplete is worse than one
that is visibly incomplete, because it reads as a complete one.

So `docs/references.json` is the single source the decks render from, and this
gate checks it against the live vignette set and against the project record:

  1. every analysis-ready vignette appears in exactly one guideline entry;
  2. no guideline entry names a vignette that is no longer live;
  3. every entry carries a status, and the status vocabulary is closed;
  4. nothing is silently 'verified' without a source_of_record (literature) or
     a DOI/identifier (guidelines).

It does NOT require every vignette to be formally cited. Ten of them are quoted
at first hand in the compendium without a written citation, and that is a real
state of the project; the gate's job is to make sure the decks say so rather
than to pretend otherwise. What it refuses is SILENCE: a vignette that appears
in neither the verified nor the pending list.

Exit codes: 0 consistent, 1 drifted.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "docs/references.json"
VIGNETTES = ROOT / "data/vignettes/vignettes.csv"
STATUSES = {"verified", "identifier_only", "pending"}


def main() -> int:
    refs = json.loads(REFS.read_text(encoding="utf-8"))
    lit, gls = refs["literature"], refs["guidelines"]

    v = pd.read_csv(VIGNETTES)
    live = set(v[v["analysis_ready"] == True]["vignette_id"].unique())  # noqa: E712

    cited: Counter[str] = Counter()
    for g in gls:
        for vid in g["vignettes"]:
            cited[vid] += 1

    problems: list[str] = []

    missing = sorted(live - set(cited))
    if missing:
        problems.append(f"{len(missing)} live vignette(s) in NO reference entry, "
                        f"so the decks would cite nothing for them: {missing}")

    stale = sorted(set(cited) - live)
    if stale:
        problems.append(f"{len(stale)} reference entr(ies) name a vignette that "
                        f"is not live: {stale}")

    dupes = sorted(k for k, n in cited.items() if n > 1)
    if dupes:
        problems.append(f"vignette(s) in more than one guideline entry, so a "
                        f"slide would print two citations for one item: {dupes}")

    for g in gls:
        if g.get("status") not in STATUSES:
            problems.append(f"guideline entry {g['vignettes']} has status "
                            f"{g.get('status')!r}; allowed: {sorted(STATUSES)}")
        if g.get("status") == "verified" and not (g.get("doi") or "NICE" in g["cite"]
                                                  or "GINA" in g["cite"]
                                                  or "arXiv" in g["cite"]
                                                  or "USPSTF" in g["cite"]):
            problems.append(f"guideline entry {g['vignettes']} claims 'verified' "
                            f"with no DOI and no named guideline identifier")
    for e in lit:
        if e.get("status") == "verified" and not e.get("source_of_record"):
            problems.append(f"literature entry {e['id']} claims 'verified' with "
                            f"no source_of_record")

    by_status = Counter(g["status"] for g in gls)
    print(f"references: {len(lit)} literature, {len(gls)} guideline entries "
          f"covering {len(cited)} vignette(s)")
    print(f"  live vignettes            : {len(live)}")
    for s in ("verified", "identifier_only", "pending"):
        n_v = sum(len(g["vignettes"]) for g in gls if g["status"] == s)
        print(f"  {s:17s} : {by_status.get(s, 0):2d} entr(ies), "
              f"{n_v:2d} vignette(s)")

    if problems:
        print()
        print("REFERENCE GATE FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1

    n_formal = sum(len(g["vignettes"]) for g in gls if g["status"] == "verified")
    print(f"  consistent. {n_formal} of {len(live)} live vignettes carry a "
          f"formal citation of record; the rest are quoted at first hand in "
          f"docs/vignettes_compendium.md and are rendered as pending, not "
          f"omitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
