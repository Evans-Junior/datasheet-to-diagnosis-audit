"""Build the manual vignette-review workbook: every vignette beside its source quote.

One row per vignette. The clinical text as the model actually receives it, the
verbatim guideline quote recorded in docs/vignette_sources.md, and the approval
columns the reviewer fills in. Written for author review under D064, and
reusable unchanged for clinician review once REB approval is in place.

Usage:
    .venv/bin/python scripts/build_review_workbook.py
    .venv/bin/python scripts/build_review_workbook.py --only G2-03b,G4-03b \
        --out Vignette_Review_New_Rows.xlsx

--only builds a focused sheet holding just the named vignettes. It exists
because a row added AFTER a review round needs reviewing on its own, and
re-opening a 28-row workbook to find three rows invites approving the other
25 again by scrolling past them. The sheet is otherwise identical, so a
focused approval and a full-sheet approval mean the same thing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.vignettes import load, expand  # noqa: E402

SOURCES = ROOT / "docs/vignette_sources.md"
OUT = ROOT / "Vignette_Review_Datasheet_to_Diagnosis.xlsx"

HDR = PatternFill("solid", fgColor="0F3A44")
SRC = PatternFill("solid", fgColor="E8F2F1")      # source quote column
ASK = PatternFill("solid", fgColor="FDF2D9")      # columns the reviewer fills
WARN = PatternFill("solid", fgColor="FBE4E0")     # not quoted at source
THIN = Side(style="thin", color="B8C4C4")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def parse_sources() -> dict[str, dict]:
    """Pull the per-vignette source block out of docs/vignette_sources.md.

    Keyed on the vignette id in the `### G2-01 — ...` headings. Returns the
    status marker, the citation line, and every blockquote in the section
    concatenated -- the blockquotes ARE the verbatim guideline text, which is
    the whole point of the column they land in.
    """
    text = SOURCES.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    # Split on level-3 headings that start with a vignette id.
    # The id pattern must allow a LETTER SUFFIX. Replacement vignettes created
    # on clinical review are named G2-01b, G2-03b, G4-03b -- the convention
    # deliberately keeps the lineage visible instead of renumbering. With the
    # old `G\d-\d\d` pattern a "### G2-01b" heading matched as "G2-01" and its
    # evidence was silently filed under the row it replaced, which is the worst
    # possible failure for a row created BECAUSE the original was rejected.
    parts = re.split(r"\n### (G\d-\d\d[a-z]?)([^\n]*)\n", text)
    for i in range(1, len(parts) - 1, 3):
        vid, heading, body = parts[i], parts[i + 1], parts[i + 2]
        # Quotes and their labels are collected AS PAIRS, each quote taking the
        # nearest bold run that precedes it. They used to be gathered into two
        # independent lists and zipped by index, which silently drifted: every
        # bold phrase in the surrounding prose that was not a quote label shifted
        # the whole mapping. That is how G4-01's foot rule came to be labelled
        # "[Reference answer]" and G4-11's ceftriaxone quote came to be labelled
        # with a sentence about target_option. The clinical reviewer caught all
        # four. Pairing at parse time makes the drift impossible rather than
        # unlikely.
        quotes, labels = [], []
        for block in re.finditer(r"((?:^> .*\n?)+)", body, re.M):
            q = " ".join(l.lstrip("> ").rstrip()
                         for l in block.group(1).splitlines())
            q = re.sub(r"\s+", " ", q).strip()
            if not q:
                continue
            bolds = re.findall(r"\*\*([^*\n]{2,140}?):?\*\*", body[:block.start()])
            labels.append(bolds[-1].strip() if bolds else f"Quote {len(quotes) + 1}")
            quotes.append(q)
        # The citation used to be "the first prose line after the heading", which
        # broke as soon as a section opened by explaining what the OLD source was.
        # G4-02's round-4 section begins "G4-02 was acute conjunctivitis, sourced
        # to the AAO Conjunctivitis Preferred Practice Pattern", so the workbook
        # cited the retired guideline for a cutaneous abscess. Prefer the
        # paragraph that declares the new source; fall back to a paragraph that
        # looks like a citation; only then to the old line rule.
        def _clean(t: str) -> str:
            return re.sub(r"\s+", " ", re.sub(r"[*`]", "", t)).strip()

        paras = [_clean(x) for x in re.split(r"\n\s*\n", body)]
        CITEY = re.compile(r"doi:|DOI\s|https?://|\bNG\d+|\bCG\d+|\bet al\b"
                           r"|\b(?:19|20)\d\d\b", re.I)
        cite = ""
        for para in paras:
            if re.match(r"(?i)new source", para):
                cite = para[:400]
                break
        if not cite:
            for para in paras:
                if not para or para.startswith((">", "|", "#")):
                    continue
                if CITEY.search(para):
                    cite = para[:400]
                    break
        if not cite:
            for line in body.splitlines():
                t = line.strip()
                if t and not t.startswith((">", "**", "#", "-", "|", "1.", "2.")):
                    cite = t
                    break
        # Status marker only, not the whole title: the title is already in the
        # `condition` column and repeating it crowds out the marker.
        mk = re.search(r"([\u2705\u26a0\u274c].*)$", heading)
        status = mk.group(1).strip() if mk else ""

        # A heading carrying the retirement marker (U+2298) is HISTORY, not
        # evidence: the row it documents was re-sourced or replaced by a later
        # round. Skip it outright instead of merging it. Merging would let a
        # superseded section contribute both its stale marker -- status_line is
        # first-wins, so the oldest section would keep deciding the colour of
        # the row -- and its now-irrelevant quotes, which is how the retired
        # NG91 block would have gone on "supporting" a vignette NG91 cannot
        # source. The quotes stay in the .md for provenance; they stop counting.
        if "\u2298" in heading:
            continue

        # MERGE, never overwrite. docs/vignette_sources.md legitimately carries
        # more than one section per id -- G2-01 has the NG126 sourcing block at
        # one place and a separate "RESOLVED (D017)" discussion further down.
        # Keying by id and assigning would let the later, quote-free section
        # erase the verbatim NG126 quotes, which is exactly what it did: the
        # best-sourced vignette in the set rendered as NOT QUOTED AT SOURCE.
        prev = out.get(vid)
        if prev:
            prev["quotes"] += quotes
            prev["labels"] += labels
            prev["citation"] = prev["citation"] or cite
            # Keep whichever status marker exists; a section without quotes has
            # no authority to downgrade one that has them.
            if status and not prev["status_line"]:
                prev["status_line"] = status
            prev["quoted_at_source"] = bool(prev["quotes"])
        else:
            out[vid] = {
                "status_line": status,
                "citation": cite,
                "quotes": quotes,
                "labels": labels,
                "quoted_at_source": bool(quotes),
            }
    return out


def main() -> None:
    templates, arms = load()
    src = parse_sources()

    argv = sys.argv[1:]
    only: list[str] = []
    out = OUT
    if "--only" in argv:
        only = [s.strip() for s in argv[argv.index("--only") + 1].split(",")
                if s.strip()]
        known = {t["id"] for t in templates}
        missing = [v for v in only if v not in known]
        if missing:
            # Fail rather than silently build a short sheet. A typo'd id in a
            # focused review would produce a workbook that LOOKS complete and
            # quietly omits the row the reviewer was asked to look at.
            sys.exit(f"--only: no such vignette: {', '.join(missing)}")
        templates = [t for t in templates if t["id"] in only]
    if "--out" in argv:
        out = ROOT / argv[argv.index("--out") + 1]
    elif only:
        out = ROOT / "Vignette_Review_New_Rows_Datasheet_to_Diagnosis.xlsx"

    # Render each vignette the way the model receives it. The BLINDED arm with
    # SPCU female is used for display: the reviewer is checking clinical
    # content, not the gender manipulation, and a gendered arm would invite
    # review of the wrong thing.
    gid = next(g for g in arms["gender_identities"] if g["key"] == "blinded")
    rendered: dict[str, str] = {}
    for tpl in templates:
        # GROUP 2 SHOWS BOTH SPCU ARMS. Everywhere else one arm is right: the
        # reviewer is checking clinical content, and a gendered arm would invite
        # review of the wrong thing. Group 2 is the exception, because the whole
        # point of a Group 2 item is that the correct answer DIFFERS by the sex
        # parameter -- so a reviewer shown only the female arm cannot check the
        # male one. That is not hypothetical: the G2-03 reject was written by
        # reasoning about an SPCU-male variant this sheet never displayed, where
        # "the last cervical screening test was six years ago" describes a history
        # the patient cannot have. Showing both arms is what makes that checkable.
        spcus = ["female", "male"] if tpl["group"] == 2 else ["female"]
        by_spcu = tpl.get("reference_answer_by_spcu") or {}
        chunks = []
        for sp in spcus:
            rows = [r for r in expand(tpl, arms)
                    if r["gender_identity"] == "blinded" and r["spcu"] == sp
                    and r["paraphrase"] == 1]
            if not rows:
                continue
            if len(spcus) > 1:
                ans = by_spcu.get(sp, tpl.get("reference_answer") or "?")
                chunks.append(f"=== SPCU {sp.upper()}  (reference answer: "
                              f"{ans}) ===\n{rows[0]['prompt_text']}")
            else:
                chunks.append(rows[0]["prompt_text"])
        if chunks:
            rendered[tpl["id"]] = "\n\n".join(chunks)

    wb = Workbook()

    # ------------------------------------------------------------------ #
    ws = wb.active
    ws.title = "Start here"
    ws.column_dimensions["A"].width = 112
    lines = [
        ("Vignette review — From datasheet to diagnosis", 16, True),
        ("", 11, False),
        ("WHAT THIS IS", 12, True),
        ("Every vignette in the study, with the verbatim guideline text it was built "
         "from in the column beside it. Your job is to decide, for each row, whether "
         "the reference answer is the answer the quoted guideline actually gives.", 11, False),
        ("", 11, False),
        ("THE ONE QUESTION THAT MATTERS", 12, True),
        ("Column H holds the clinical text. Column G holds the guideline quote. Read G, "
         "then read H, and ask: could a clinician reading H reach the reference answer "
         "in column K and no other answer? If a second answer is defensible, the item "
         "will produce noise that cannot be attributed to gender.", 11, False),
        ("", 11, False),
        ("PLEASE REJECT RATHER THAN REPAIR", 12, True),
        ("If an item is wrong, mark it Reject and say why in column R. Do not rewrite "
         "the clinical text in place. A rewritten item has no record of what changed, "
         "and the before/after comparison this project depends on needs that record.", 11, False),
        ("", 11, False),
        ("READ THIS BEFORE YOU START — the sourcing caveat", 12, True),
        ("Rows shaded PINK in column F are NOT YET QUOTED AT SOURCE. For those, the "
         "guideline named is a candidate identified from a literature search, and the "
         "wording in column G is either absent or taken from a secondary summary — "
         "nobody has opened the primary document. Weight your confidence accordingly, "
         "and treat 'the quote supports this answer' as unanswerable for those rows.", 11, False),
        ("", 11, False),
        ("WHAT YOUR APPROVAL DOES AND DOES NOT DO", 12, True),
        ("Author review moves an item from 'unverified_ai_drafted' to "
         "'author_reviewed_against_quoted_guideline'. It does NOT make any number "
         "reportable: only a clinician can do that, and that step waits on REB "
         "approval from McGill (D064). Every table and figure will still carry a "
         "PROVISIONAL stamp after you finish, and the stamp will say which of the two "
         "provisional states it came from.", 11, False),
        ("", 11, False),
        ("COLUMNS YOU FILL IN", 12, True),
        ("  M   Is the reference answer correct per the quoted guideline?", 11, False),
        ("  N   Do the findings FORCE that answer, with every competing reason negated?", 11, False),
        ("  O   Does the quote in column G actually support the answer? (n/a if not sourced)", 11, False),
        ("  P   Is the text free of gendered words and anatomy outside the SPCU line?", 11, False),
        ("  Q   APPROVE / APPROVE WITH EDIT / REJECT", 11, False),
        ("  R   Your comment, and for a reject, what is wrong", 11, False),
    ]
    if only:
        lines[1:1] = [
            ("", 11, False),
            (f"FOCUSED SHEET \u2014 {len(only)} row(s): {', '.join(only)}", 12, True),
            ("These rows were added or rewritten after the last review round, so "
             "they have not been reviewed yet. Every other row in the study is "
             "unchanged and is not reproduced here. Approving these does not "
             "re-approve anything else.", 11, False),
        ]
    for i, (t, sz, bold) in enumerate(lines, start=1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(size=sz, bold=bold,
                      color="0F3A44" if bold and sz >= 12 else "000000")
        c.alignment = Alignment(wrap_text=True, vertical="top")

    # ------------------------------------------------------------------ #
    rv = wb.create_sheet("Review")
    cols = [
        ("A", "id", 9), ("B", "group", 7), ("C", "condition", 30),
        ("D", "tier", 6), ("E", "verification", 20),
        ("F", "source status", 20), ("G", "VERBATIM GUIDELINE QUOTE", 62),
        ("H", "clinical text as the model sees it", 72),
        ("I", "question", 34), ("J", "answer options", 26),
        ("K", "reference answer", 18), ("L", "target option", 14),
        ("M", "answer correct?", 15), ("N", "findings force it?", 16),
        ("O", "quote supports it?", 16), ("P", "no gendered words?", 16),
        ("Q", "APPROVE?", 20), ("R", "your comment", 46),
    ]
    for letter, name, width in cols:
        rv.column_dimensions[letter].width = width
        c = rv.cell(row=1, column=rv[letter + "1"].column, value=name)
        c.fill = HDR
        c.font = Font(bold=True, color="FFFFFF", size=10)
        c.alignment = Alignment(wrap_text=True, vertical="center")
    rv.row_dimensions[1].height = 34

    order = sorted(templates, key=lambda t: (t["group"], t["id"]))
    r = 2
    n_unsourced = 0
    for tpl in order:
        vid = tpl["id"]
        s = src.get(vid, {})
        quotes = s.get("quotes") or []
        labels = s.get("labels") or []
        # A row whose status marker is the cross (U+274C) is NOT sourced, even
        # though quotes were found for it. docs/vignette_sources.md legitimately
        # quotes a guideline verbatim in order to DISQUALIFY it -- G4-11 quotes
        # NG91's "children and young people" scope to prove NG91 cannot source an
        # adult vignette. Counting those quotes as support turned the one open row
        # green in column F, which is the single most misleading thing this
        # workbook could do. The marker in the heading governs, not quote presence.
        disqualified = "\u274c" in (s.get("status_line") or "")
        if quotes and not disqualified:
            parts = []
            for i, q in enumerate(quotes[:4]):
                lab = labels[i] if i < len(labels) else f"Quote {i+1}"
                parts.append(f"[{lab}]  {q}")
            quote_text = "\n\n".join(parts)
            status = s.get("status_line") or "QUOTED (no marker)"
        elif disqualified:
            # Sourcing was attempted and FAILED. Show the disqualifying evidence,
            # because a reviewer needs to see why the candidate was rejected.
            parts = []
            for i, q in enumerate(quotes[:4]):
                lab = labels[i] if i < len(labels) else f"Quote {i+1}"
                parts.append(f"[{lab}]  {q}")
            quote_text = ("[CANDIDATE GUIDELINE DISQUALIFIED -- NOT SOURCED]  The "
                          "quotes below are the evidence that the named guideline "
                          "does NOT cover this vignette. They are not support for "
                          "the reference answer. See docs/vignette_sources.md, "
                          "\"Sourcing round 2\", and D071 for the options to close "
                          "this row.\n\n" + "\n\n".join(parts))
            status = s.get("status_line") or "NOT SOURCED"
            n_unsourced += 1
        else:
            quote_text = ("[NOT YET QUOTED AT SOURCE]  The guideline named for this "
                          "item is a candidate from a literature search. The primary "
                          "document has not been opened. See the template note in "
                          "data/vignettes/templates.yaml and docs/vignette_sources.md.")
            status = "NOT QUOTED AT SOURCE"
            n_unsourced += 1

        # A REJECTED row must say so in the status column. Its sourcing section
        # can legitimately still read "COMPLETE" -- G2-03's USPSTF citation is
        # sound and carried over to G2-03b, because the defect was in the
        # vignette text, not the citation. But a reviewer scanning column F
        # would see a green tick on a row that has been thrown out, which is the
        # same class of error as the disqualified-quote bug above. The verdict
        # on the row overrides the verdict on its sourcing.
        if tpl.get("verification") == "rejected":
            blocked_why = (tpl.get("blocked_on") or "").strip().replace("\n", " ")
            status = (f"\u274c REJECTED AND EXCLUDED \u2014 not scored. "
                      f"Sourcing status was: {status or 'n/a'}")
            quote_text = (f"[ROW REJECTED ON CLINICAL REVIEW \u2014 EXCLUDED FROM "
                          f"THE RUN]  {blocked_why[:600]}\n\n{quote_text}")

        by = tpl.get("reference_answer_by_spcu")
        ref = ("  |  ".join(f"SPCU {k}: {v}" for k, v in by.items()) if by
               else str(tpl.get("reference_answer")))

        vals = [vid, tpl["group"], tpl["condition"], tpl.get("tier"),
                tpl.get("verification", "unverified"), status, quote_text,
                rendered.get(vid, "(not rendered: clinical slot still empty)"),
                tpl.get("question"),
                " | ".join(tpl.get("answer_options") or []),
                ref, tpl.get("target_option"), "", "", "", "", "", ""]
        for j, v in enumerate(vals, start=1):
            c = rv.cell(row=r, column=j, value=v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BOX
            if j == 7:
                c.fill = SRC
            elif j == 6 and (not quotes or disqualified):
                c.fill = WARN
            elif j >= 13:
                c.fill = ASK
        rv.row_dimensions[r].height = 150
        r += 1

    last = r - 1
    yn = DataValidation(type="list", formula1='"Yes,No,Unsure,n/a"', allow_blank=True)
    ap = DataValidation(type="list",
                        formula1='"APPROVE,APPROVE WITH EDIT,REJECT,not reviewed yet"',
                        allow_blank=True)
    rv.add_data_validation(yn)
    rv.add_data_validation(ap)
    for col in ("M", "N", "O", "P"):
        yn.add(f"{col}2:{col}{last}")
    ap.add(f"Q2:Q{last}")

    rv.freeze_panes = "C2"
    rv.auto_filter.ref = f"A1:R{last}"

    # ------------------------------------------------------------------ #
    gl = wb.create_sheet("Full sources")
    gl.column_dimensions["A"].width = 10
    gl.column_dimensions["B"].width = 34
    gl.column_dimensions["C"].width = 118
    for j, name in enumerate(["id", "citation", "every quote recorded for this item"],
                             start=1):
        c = gl.cell(row=1, column=j, value=name)
        c.fill = HDR
        c.font = Font(bold=True, color="FFFFFF", size=10)
    rr = 2
    for tpl in order:
        s = src.get(tpl["id"], {})
        body = "\n\n".join(s.get("quotes") or []) or "(none recorded)"
        for j, v in enumerate([tpl["id"], s.get("citation", ""), body], start=1):
            c = gl.cell(row=rr, column=j, value=v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BOX
        gl.row_dimensions[rr].height = 160
        rr += 1
    gl.freeze_panes = "A2"

    wb.save(out)
    print(f"wrote {out.name}")
    print(f"  vignettes        : {len(order)}")
    print(f"  quoted at source : {len(order) - n_unsourced}")
    print(f"  NOT yet quoted   : {n_unsourced}  (shaded pink in column F)")
    print(f"  sheets           : Start here | Review | Full sources")
    print(f"  dropdowns on     : M, N, O, P (Yes/No/Unsure/n-a) and Q (approve)")


if __name__ == "__main__":
    main()
