"""Build the second-round workbook: the vignettes the two reviewers did not agree on.

The first round produced two independent reviews and
scripts/compare_vignette_reviews.py sorted out where they stand. This takes
what is unsettled and turns it back into something one person can fill in, so
the pair can converge on a vignette set both of them have signed off.

It is written to be SENT. Everything a reader needs to re-judge a vignette is
on the row: the clinical text as the model receives it, the question, the
options, the reference answer, the verbatim guideline quote, and the other
reviewer's reasoning in their own words. Nobody should have to open the first
workbook again to answer this one.

THE SHEETS, IN THE ORDER THEY MATTER:

  1. You objected, I accepted   the rows Aymen rejected or flagged and Evans
                                kept. Evans' reasons are given; Aymen says
                                whether he now agrees.
  2. I rejected, you accepted   the mirror image. Evans' reasons for throwing
                                the row out; Aymen says whether he agrees.
  3. New rows                   the replacements written after round one went
                                out. Aymen has never seen these, so they get
                                the full review columns, not an agree box.
  4. Also open                  everything else still unsettled: one blank
                                verdict, the approve-versus-approve-with-edit
                                disputes, and the rows where both verdicts
                                match but the item answers do not. Lower
                                priority, and the sheet says so.

IT ANSWERS NOTHING. Every cell holding a judgment is one of the two reviewers'
own, copied. The response columns are empty with a dropdown. A script that
filled them would be inventing the agreement the round exists to reach.

Usage:
    .venv/bin/python scripts/build_resolution_round.py
    .venv/bin/python scripts/build_resolution_round.py --aymen other.xlsx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from compare_vignette_reviews import (  # noqa: E402
    AYMEN, EVANS, EVANS_EXTRA, ITEMS, VERDICTS, classify, load_side)

OUT = ROOT / "Vignette_Review_Round2_for_Aymen.xlsx"
PROMPTS = ROOT / "data/vignettes/vignettes.csv"


def analysis_set() -> tuple[set[str], dict[str, str]]:
    """The vignettes actually in the study, and the fallback clinical text.

    THIS IS NOT COSMETIC. Three of the rows the two reviews disagree about are
    already out of the analysis set: G2-01, G2-03 and G4-03 were replaced by
    the `b` rows after round one went out, and `analysis_ready` in the built
    prompt set is the authority on that, not either workbook. Asking a
    reviewer to re-argue a vignette that no longer exists wastes the one
    favour you are asking of them, so every row carries its status and the
    superseded ones say what replaced them.

    The second return value is the prompt text, taken from the BLINDED arm so
    the sheet shows the stem without a gendered label attached. The new-rows
    workbook left that column empty for G2-01b and G2-03b, and the clinical
    text is the one thing a reviewer cannot judge the row without.
    """
    import csv
    live: set[str] = set()
    text: dict[str, str] = {}
    with io_open(PROMPTS) as fh:
        for row in csv.DictReader(fh):
            vid = (row.get("vignette_id") or "").strip()
            if not vid:
                continue
            if str(row.get("analysis_ready", "")).strip().lower() == "true":
                live.add(vid)
            if vid not in text and (row.get("gender_identity") or "") == "blinded":
                text[vid] = (row.get("prompt_text") or "").strip()
    if not live:
        raise SystemExit(f"build_resolution_round: no analysis_ready rows in {PROMPTS}")
    return live, text


def io_open(path: Path):
    return open(path, newline="", encoding="utf-8")


def status_of(vid: str, live: set[str]) -> str:
    """'live' or a sentence naming the row that replaced this one."""
    if vid in live:
        return "LIVE, in the analysis set"
    rep = vid + "b"
    if rep in live:
        return f"SUPERSEDED by {rep}, no longer in the analysis set"
    return "NOT in the analysis set"

HDR = PatternFill("solid", fgColor="0F3A44")
SUB = PatternFill("solid", fgColor="1C5C68")
MINE = PatternFill("solid", fgColor="EAF3FA")     # Evans' side, not to change
YOURS = PatternFill("solid", fgColor="F2EFF8")    # Aymen's own round-one cells
EVID = PatternFill("solid", fgColor="E8F2F1")     # the vignette itself
ASKF = PatternFill("solid", fgColor="FFF3D6")     # for Aymen to fill
THIN = Side(style="thin", color="B8C4C4")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

AGREE = ["I AGREE with Evans", "I STILL DISAGREE", "UNSURE, let us talk"]


def band(ws, row, col_from, col_to, text, fill):
    """A labelled stripe across a group of columns, so the sheet reads in blocks."""
    ws.merge_cells(start_row=row, start_column=col_from,
                   end_row=row, end_column=col_to)
    c = ws.cell(row, col_from, text)
    c.fill = fill
    c.font = Font(bold=True, color="FFFFFF", size=9)
    c.alignment = Alignment(horizontal="center", vertical="center")


def header(ws, cols, widths, bands):
    for i, (name, w) in enumerate(zip(cols, widths), start=1):
        c = ws.cell(2, i, name)
        c.fill, c.font = HDR, Font(bold=True, color="FFFFFF", size=10)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BOX
        ws.column_dimensions[get_column_letter(i)].width = w
    for a, b, text, fill in bands:
        band(ws, 1, a, b, text, fill)
    ws.row_dimensions[1].height = 18
    ws.row_dimensions[2].height = 42
    ws.freeze_panes = "C3"


def write(ws, r, values, fills):
    """One row. `fills` is a list of (first_col, last_col, fill)."""
    for i, v in enumerate(values, start=1):
        c = ws.cell(r, i, v)
        c.border = BOX
        c.alignment = Alignment(vertical="top", wrap_text=i > 2)
    for a, b, f in fills:
        for i in range(a, b + 1):
            ws.cell(r, i).fill = f
    ws.row_dimensions[r].height = 110


def intro(wb, counts, evans_name, aymen_name, live, settled, superseded):
    ws = wb.create_sheet("Start here", 0)
    ws.column_dimensions["A"].width = 112
    lines = [
        ("Round two: the vignettes we did not agree on", 15, True, "0F3A44"),
        ("", 10, False, None),
        (f"We reviewed the same vignettes separately. {settled} of them have the same "
         "verdict from both of us and", 10, False, "1A1A1A"),
        ("are settled. This workbook holds the rest. Everything you need to judge a row "
         "is on the row itself,", 10, False, "1A1A1A"),
        ("so you should not need the first workbook open beside this one.",
         10, False, "1A1A1A"),
        ("", 10, False, None),
        (f"Check the STATUS column first. {len(live)} vignettes are in the analysis set. "
         f"{len(superseded)} rows we disagreed", 10, True, "8B4513"),
        (f"about ({', '.join(superseded)}) are already out, replaced by the b rows on "
         "sheet 3, so a verdict on", 10, True, "8B4513"),
        ("them changes nothing in the study. They are here because you should see why "
         "they were replaced,", 10, True, "8B4513"),
        ("not because the study is waiting on them.", 10, True, "8B4513"),
        ("", 10, False, None),
        ("What to do, sheet by sheet", 12, True, "0F3A44"),
        (f"1. You objected, I accepted ({counts[0]} rows). You rejected these, or "
         "flagged a problem with them,", 10, False, "1A1A1A"),
        ("   and I kept them. My reasons are on the row. Say in the gold column "
         "whether you now agree.", 10, False, "1A1A1A"),
        (f"2. I rejected, you accepted ({counts[1]} rows). The mirror image: I would "
         "throw these out and you", 10, False, "1A1A1A"),
        ("   would keep them. My reasons are on the row. Same question in the gold "
         "column.", 10, False, "1A1A1A"),
        (f"3. New rows ({counts[2]} rows). These are replacements I wrote AFTER the "
         "first round went out, so you", 10, False, "1A1A1A"),
        ("   have never seen them. They get the full review, the same four checks and "
         "a verdict, not an", 10, False, "1A1A1A"),
        ("   agree box. My own review of each is shown for reference, after you have "
         "formed your own.", 10, False, "1A1A1A"),
        (f"4. Also open ({counts[3]} rows). Lower priority. One row where your verdict "
         "cell is empty, the rows", 10, False, "1A1A1A"),
        ("   where one of us said APPROVE and the other APPROVE WITH EDIT, and the rows "
         "where we agreed on", 10, False, "1A1A1A"),
        ("   the verdict but answered the four checks differently. Worth a pass if you "
         "have time.", 10, False, "1A1A1A"),
        ("", 10, False, None),
        ("Two things worth saying plainly", 12, True, "0F3A44"),
        ("Our agreement in round one was 65% raw, Cohen's kappa 0.264. That is poor, "
         "and it is the number", 10, False, "1A1A1A"),
        ("we would have to report. Converging here is what fixes it, so disagreeing "
         "with me on this sheet is", 10, False, "1A1A1A"),
        ("more useful than going along with me.", 10, False, "1A1A1A"),
        ("Only the gold columns are for you. Blue is mine and lavender is your own "
         "round-one answer, both", 10, False, "1A1A1A"),
        ("shown so you can see what each of us actually said. Green is the vignette "
         "itself.", 10, False, "1A1A1A"),
        ("", 10, False, None),
        (f"Built by scripts/build_resolution_round.py from {evans_name} and "
         f"{aymen_name}.", 9, False, "5A7883"),
        ("Rerun it rather than editing this file by hand.", 9, False, "5A7883"),
    ]
    for i, (text, size, bold, colour) in enumerate(lines, start=1):
        c = ws.cell(i, 1, text)
        c.font = Font(size=size, bold=bold, color=colour or "1A1A1A")
    return ws


# The evidence block, identical on every sheet.
EV_COLS = ["clinical text as the model sees it", "question", "answer options",
           "reference answer", "VERBATIM GUIDELINE QUOTE"]
EV_W = [44, 30, 34, 20, 48]


def evidence(row):
    return [row.get("clinical", ""), row.get("question", ""), row.get("options", ""),
            row.get("reference", ""), row.get("quote", "")]


def items_of(row):
    return [row.get(name, "") or "-" for _, name in ITEMS]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evans", type=Path, default=EVANS)
    ap.add_argument("--aymen", type=Path, default=AYMEN)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    E = load_side(args.evans, EVANS_EXTRA)
    A = load_side(args.aymen, [])
    live, prompt_text = analysis_set()
    # Fill any clinical-text gap from the built prompt set. The workbook is the
    # record of the review; the prompt set is the record of what the model was
    # actually shown, so it wins when the two disagree about emptiness.
    for vid, row in E.items():
        if not row.get("clinical") and prompt_text.get(vid):
            row["clinical"] = prompt_text[vid] + "\n\n[text taken from the built prompt set, blinded arm]"

    # ---- sort the unsettled rows into the four sheets
    s1, s2, s3, s4 = [], [], [], []
    for vid in sorted(set(E) | set(A)):
        e, a = E.get(vid), A.get(vid)
        status, why = classify(e, a)
        if status.startswith("AGREED") and "ITEMS DIFFER" not in status:
            continue
        ev = (e or {}).get("verdict", "")
        av = (a or {}).get("verdict", "")
        if a is None:
            s3.append((vid, e, a, why))                     # Aymen never saw it
        elif av == "REJECT" and ev != "REJECT":
            s1.append((vid, e, a, why))
        elif not av and (a or {}).get("answer", "") == "No" and ev != "REJECT":
            s1.append((vid, e, a, why))                     # objected without a verdict
        elif ev == "REJECT" and av != "REJECT":
            s2.append((vid, e, a, why))
        else:
            s4.append((vid, e, a, why))

    for bucket in (s1, s2, s4):
        bucket.sort(key=lambda row: (row[0] not in live, row[0]))

    wb = Workbook()
    wb.remove(wb.active)
    dv_agree = DataValidation(type="list",
                              formula1='"' + ",".join(AGREE) + '"', allow_blank=True)
    dv_yn = DataValidation(type="list", formula1='"Yes,No,Unsure,n-a"',
                           allow_blank=True)
    dv_verdict = DataValidation(type="list", formula1='"' + ",".join(VERDICTS) + '"',
                               allow_blank=True)

    # ------------------------------------------- sheets 1 and 2, same shape
    for title, rows, mine_label, ask in [
        ("1. You objected, I accepted", s1,
         "MY VERDICT AND WHY I KEPT IT",
         "DO YOU NOW AGREE WITH ME?"),
        ("2. I rejected, you accepted", s2,
         "MY VERDICT AND WHY I REJECTED IT",
         "DO YOU NOW AGREE WITH ME?"),
    ]:
        ws = wb.create_sheet(title)
        cols = (["id", "condition", "status", "your round-one verdict",
                 "your round-one checks (answer / findings / quote / wording)",
                 "your round-one comment", "my verdict", "my reason",
                 "my suggested fix"] + EV_COLS
                + ["YOUR ANSWER (dropdown)", "why, if you still disagree"])
        widths = [9, 24, 34, 18, 26, 40, 18, 52, 44] + EV_W + [22, 44]
        n = len(cols)
        header(ws, cols, widths, [
            (4, 6, "YOUR ROUND ONE", SUB), (7, 9, mine_label, HDR),
            (10, 14, "THE VIGNETTE", SUB), (n - 1, n, ask, PatternFill(
                "solid", fgColor="B7791F"))])
        ws.add_data_validation(dv_agree)
        r = 3
        for vid, e, a, why in rows:
            e, a = e or {}, a or {}
            write(ws, r, [vid, e.get("condition", "") or a.get("condition", ""),
                          status_of(vid, live),
                          a.get("verdict", "") or "(no verdict given)",
                          " / ".join(items_of(a)), a.get("comment", ""),
                          e.get("verdict", ""), e.get("comment", ""),
                          e.get("fix", "")] + evidence(e or a) + [None, None],
                  [(4, 6, YOURS), (7, 9, MINE), (10, 14, EVID), (n - 1, n, ASKF)])
            dv_agree.add(ws.cell(r, n - 1))
            r += 1
        if r == 3:
            ws.cell(3, 1, "Nothing in this category.")

    # ------------------------------------------------------- sheet 3, new rows
    ws = wb.create_sheet("3. New rows")
    cols = (["id", "condition"] + EV_COLS
            + ["YOUR: answer correct?", "YOUR: findings force it?",
               "YOUR: quote supports it?", "YOUR: no gendered words?",
               "YOUR VERDICT", "YOUR comment",
               "why this row exists / my review", "my verdict"])
    widths = [9, 26] + EV_W + [14, 14, 14, 14, 20, 44, 52, 18]
    n = len(cols)
    header(ws, cols, widths, [
        (3, 7, "THE VIGNETTE", SUB),
        (8, 13, "YOUR REVIEW, PLEASE FILL IN", PatternFill("solid", fgColor="B7791F")),
        (14, 15, "MINE, FOR REFERENCE AFTER YOU HAVE FORMED YOURS", HDR)])
    for dv in (dv_yn, dv_verdict):
        ws.add_data_validation(dv)
    r = 3
    for vid, e, a, why in s3:
        e = e or {}
        write(ws, r, [vid, e.get("condition", "")] + evidence(e)
              + [None, None, None, None, None, None,
                 e.get("comment", ""), e.get("verdict", "")],
              [(3, 7, EVID), (8, 13, ASKF), (14, 15, MINE)])
        for col in range(8, 12):
            dv_yn.add(ws.cell(r, col))
        dv_verdict.add(ws.cell(r, 12))
        r += 1
    if r == 3:
        ws.cell(3, 1, "No new rows outstanding.")

    # ------------------------------------------------------ sheet 4, the rest
    ws = wb.create_sheet("4. Also open")
    cols = ["id", "condition", "status", "what is unsettled", "your verdict",
            "my verdict", "your checks", "my checks", "your comment", "my reason",
            "my suggested fix", "YOUR ANSWER (dropdown)", "note"]
    widths = [9, 24, 34, 46, 18, 18, 24, 24, 38, 46, 40, 22, 36]
    n = len(cols)
    header(ws, cols, widths, [
        (5, 11, "ROUND ONE, BOTH OF US", SUB),
        (n - 1, n, "YOUR ANSWER", PatternFill("solid", fgColor="B7791F"))])
    ws.add_data_validation(dv_agree)
    r = 3
    for vid, e, a, why in s4:
        e, a = e or {}, a or {}
        write(ws, r, [vid, e.get("condition", "") or a.get("condition", ""),
                      status_of(vid, live), why,
                      a.get("verdict", "") or "(blank)", e.get("verdict", ""),
                      " / ".join(items_of(a)), " / ".join(items_of(e)),
                      a.get("comment", ""), e.get("comment", ""), e.get("fix", ""),
                      None, None],
              [(5, 11, YOURS), (n - 1, n, ASKF)])
        dv_agree.add(ws.cell(r, n - 1))
        r += 1
    if r == 3:
        ws.cell(3, 1, "Nothing else outstanding.")

    settled = sum(1 for vid in set(E) | set(A)
                  if classify(E.get(vid), A.get(vid))[0] in
                  ("AGREED, CLEARED", "AGREED, EDIT OWED", "AGREED, REJECTED"))
    superseded = sorted(v for v, *_ in s1 + s2 + s4 if v not in live)
    intro(wb, [len(s1), len(s2), len(s3), len(s4)],
          args.evans.name, args.aymen.name, live, settled, superseded)
    wb.save(args.out)

    print(f"wrote {args.out.name}")
    for title, rows in [("1. You objected, I accepted", s1),
                        ("2. I rejected, you accepted", s2),
                        ("3. New rows", s3),
                        ("4. Also open", s4)]:
        print(f"  {title:<30} {len(rows):>2}   "
              f"{', '.join(v for v, *_ in rows) or '(none)'}")
    print(f"\n  {settled} vignettes are already agreed and are not in this file.")
    print(f"  {len(live)} vignettes are in the analysis set; "
          f"superseded and shown for the record only: {', '.join(superseded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
