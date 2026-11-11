"""RQ6 reliability: Cohen's kappa and raw agreement per dimension (D098).

Reads `docs/rq6_coding_sheet.csv` and writes the two tables the codebook's
section 7 promises:

  results/tables/rq6_codes.csv        one row per document x dimension, with both
                                      coders' codes, the agreed code and the
                                      evidence each coder cited
  results/tables/rq6_reliability.csv  per dimension: kappa, raw agreement, n
                                      disagreements, and the threshold verdict

WHAT IT REFUSES TO DO
---------------------
It will not compute a reliability statistic from a partially coded sheet, and it
will not substitute the AI draft for a missing coder. Both refusals are the
point. `docs/codebook.md` section 6 defines kappa over two independent human
passes on the pre-adjudication codes; anything else is a different statistic
wearing that name.

NO verification_status OR prompt_hash COLUMN, DELIBERATELY
----------------------------------------------------------
Every table built from model scores carries both (D043, D090, D091). These two
carry neither, and the omission is a claim rather than an oversight: RQ6 codes
documents, not vignettes, so no prompt set and no clinical verification tier
bears on them. Stamping a vignette tier here would imply the codes inherit a
gate they are not subject to. RQ6's own quality gate is the kappa threshold in
this file, and `results/tables/rq6_search_counts.csv` already follows the same
convention.

TWO THINGS ABOUT KAPPA ON TEN DOCUMENTS, BOTH REPORTED RATHER THAN HIDDEN
-------------------------------------------------------------------------
 1. Where both coders use a single value throughout a dimension -- expected on
    D4 and D5, where nearly every document is 0 -- expected agreement is 1, so
    kappa is 0/0 and UNDEFINED. That is not a failure to agree; it is perfect
    agreement on a constant, which kappa cannot express. Such a dimension is
    reported as `kappa = undefined (no variance)` with its raw agreement, and it
    must not be read as a low score or silently dropped.
 2. With ten documents and marginals skewed toward 0, one disagreement moves
    kappa a long way. The codebook says to treat the threshold as a screen and
    report raw agreement beside it, which is why both are columns here.

Usage:
    .venv/bin/python scripts/rq6_reliability.py
    .venv/bin/python scripts/rq6_reliability.py --vs-draft   # secondary diagnostic
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHEET = ROOT / "docs/rq6_coding_sheet.csv"
OUT_CODES = ROOT / "results/tables/rq6_codes.csv"
OUT_REL = ROOT / "results/tables/rq6_reliability.csv"
THRESHOLD = 0.70
ORDINAL = {"D1", "D2", "D3", "D4", "D5", "D6"}


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    """Cohen's kappa, or None where expected agreement is 1 (no variance)."""
    n = len(a)
    if n == 0:
        return None
    cats = sorted(set(a) | set(b))
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    if abs(1.0 - pe) < 1e-12:
        return None
    return (po - pe) / (1.0 - pe)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vs-draft", action="store_true",
                    help="also report each human coder against the AI draft, as "
                         "a diagnostic about machine coding. Never a substitute "
                         "for the second human pass.")
    args = ap.parse_args()

    if not SHEET.exists():
        print(f"missing {SHEET}")
        return 1
    # keep_default_na=False: "n/a"/"NA"/"None" are pandas NA sentinels by
    # default, so without this a deliberate code round-trips to a blank
    # cell and the completeness gate below misreads it as uncoded.
    d = pd.read_csv(SHEET, dtype=str, keep_default_na=False).fillna("")

    for col in ("evans_code", "aymen_code"):
        if col not in d.columns:
            print(f"GATE FAILED: no column '{col}' in the coding sheet.")
            return 1

    n_e = int((d.evans_code.str.strip() != "").sum())
    n_a = int((d.aymen_code.str.strip() != "").sum())
    print(f"coding sheet: {len(d)} cells "
          f"({len(d.document.unique())} documents x "
          f"{len(d.dimension.unique())} dimensions)")
    print(f"  evans_code filled : {n_e}/{len(d)}")
    print(f"  aymen_code filled : {n_a}/{len(d)}")
    if "ai_draft_code" in d.columns:
        n_ai = int((d.ai_draft_code.str.strip() != "").sum())
        print(f"  ai_draft_code     : {n_ai}/{len(d)}  (a proposal, not a coder)")

    if n_e < len(d) or n_a < len(d):
        print()
        print("GATE FAILED. Reliability needs two complete independent human "
              "passes, and this sheet does not have them yet.")
        print()
        print("Refusing to compute kappa on a partial sheet, because a kappa "
              "over the subset that happens to be coded is not the kappa the "
              "codebook defines, and nothing downstream would be able to tell "
              "the difference.")
        print("Refusing to substitute ai_draft_code for a missing coder, "
              "because then the statistic measures agreement with a machine "
              "while being reported as inter-rater reliability.")
        print()
        print("To proceed, per docs/codebook.md section 6:")
        print("  1. Calibrate on document 2 (02_pile_datasheet). Settle the "
              "four calls listed at the top of docs/rq6_dossier.md, fill the "
              "ANCHOR lines in the codebook with the passages you agree on, "
              "and record any rule you had to add. Calibration is not counted "
              "toward reliability.")
        print("  2. Code all ten documents independently, with no discussion. "
              "Every code above 0 carries a verbatim quotation and a locator.")
        print("  3. Re-run this script.")
        return 1

    rows, rel = [], []
    for dim, g in d.groupby("dimension"):
        e = list(g.evans_code.str.strip())
        a = list(g.aymen_code.str.strip())
        k = cohen_kappa(e, a)
        agree = sum(1 for x, y in zip(e, a) if x == y)
        raw = agree / len(g)
        if k is None:
            verdict = "undefined (no variance)"
        elif k >= THRESHOLD:
            verdict = "PASS"
        else:
            verdict = "BELOW THRESHOLD: report as unreliable, or revise the "\
                      "definition and recode ALL documents from scratch"
        rel.append({
            "dimension": dim,
            "n_documents": len(g),
            "kappa": "" if k is None else round(k, 4),
            "kappa_defined": k is not None,
            "raw_agreement": round(raw, 4),
            "n_disagreements": len(g) - agree,
            "scale": "ordinal 0-3" if dim in ORDINAL else "nominal qualifier",
            "threshold": THRESHOLD,
            "verdict": verdict,
        })

    for _, r in d.iterrows():
        rows.append({
            "document": r.document, "dimension": r.dimension,
            "evans_code": r.evans_code.strip(),
            "aymen_code": r.aymen_code.strip(),
            "agreed_code": r.get("agreed_code", "").strip(),
            "pre_adjudication_agree": r.evans_code.strip() == r.aymen_code.strip(),
            "evans_passage_ids": r.get("evans_passage_ids", ""),
            "aymen_passage_ids": r.get("aymen_passage_ids", ""),
            "evans_quote": r.get("evans_quote", ""),
            "aymen_quote": r.get("aymen_quote", ""),
            "ai_draft_code": r.get("ai_draft_code", ""),
            "search_steps_done": r.get(
                "search_steps_done_1_read_2_terms_3_structural", ""),
        })

    OUT_CODES.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_CODES, index=False, quoting=csv.QUOTE_MINIMAL)
    pd.DataFrame(rel).to_csv(OUT_REL, index=False, quoting=csv.QUOTE_MINIMAL)

    print()
    print(pd.DataFrame(rel)[["dimension", "kappa", "raw_agreement",
                             "n_disagreements", "verdict"]].to_string(index=False))
    print()
    nd = [r for r in rel if not r["kappa_defined"]]
    if nd:
        print(f"{len(nd)} dimension(s) have no variance, so kappa is undefined "
              f"there: {', '.join(r['dimension'] for r in nd)}. Report the raw "
              f"agreement and say why kappa is absent. Do not read an undefined "
              f"kappa as a low one.")
    low = [r for r in rel if r["kappa_defined"] and r["kappa"] < THRESHOLD]
    if low:
        print(f"{len(low)} dimension(s) below {THRESHOLD}: "
              f"{', '.join(r['dimension'] for r in low)}. Codebook section 6.4: "
              f"either exclude from conclusions or revise and recode every "
              f"document, never patch only the rows that disagreed.")

    if args.vs_draft and "ai_draft_code" in d.columns:
        print()
        print("Secondary diagnostic, the AI draft against each human coder. "
              "This is a result about machine coding and carries no weight in "
              "the reliability claim.")
        ai = list(d.ai_draft_code.str.strip())
        for who, col in (("evans", d.evans_code), ("aymen", d.aymen_code)):
            h = list(col.str.strip())
            k = cohen_kappa(h, ai)
            agree = sum(1 for x, y in zip(h, ai) if x == y) / len(d)
            print(f"  draft vs {who:6s} raw agreement {agree:6.1%}  "
                  f"kappa {'undefined' if k is None else f'{k:+.3f}'}")

    print()
    print(f"wrote {OUT_CODES.relative_to(ROOT)}")
    print(f"wrote {OUT_REL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
