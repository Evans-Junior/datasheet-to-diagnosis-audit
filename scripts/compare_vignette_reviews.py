"""Put the two reviewers' vignette workbooks side by side and sort out what is settled.

Two people reviewed the same 25 vignettes in their own copy of the workbook
built by scripts/build_review_workbook.py. Comparing them by eye means opening
two files and scrolling in step, which is how a disagreement gets missed. This
reads both and writes one workbook that answers the two questions worth asking:
which vignettes both of us cleared, and which ones still need a decision.

IT DECIDES NOTHING. Every judgment in the output is one of the two reviewers'
own cells, copied. The adjudication columns are left empty on purpose: the
point of two coders is that the resolution is theirs, and a script that filled
it in would be inventing agreement that nobody reached.

WHAT COUNTS AS NEEDING ATTENTION. Four things, in the order they are worth
your time:

  1. opposed verdicts, where one of us would keep a vignette and the other
     would throw it away
  2. one of us said APPROVE and the other APPROVE WITH EDIT, so the edit is
     either owed or unnecessary and somebody has to say which
  3. a verdict missing from one side, including a vignette only one of us was
     ever sent
  4. the same verdict reached from different item answers, which is the quiet
     one: two people can both write APPROVE while disagreeing about whether
     the quoted guideline supports the answer at all

Usage:
    .venv/bin/python scripts/compare_vignette_reviews.py
    .venv/bin/python scripts/compare_vignette_reviews.py --aymen other.xlsx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent

# The returned copies. --evans/--aymen override, because the next round will
# arrive under some other name and renaming a teammate's file loses the trail.
EVANS = ROOT / "Vignette_Review_Datasheet_to_Diagnosis_reviewed_evans.xlsx"
AYMEN = ROOT / "vignettes_aymen.xlsx"
# Rows added after the first round went out, reviewed on their own sheet.
EVANS_EXTRA = [ROOT / "Vignette_Review_New_Rows_reviewed_evans.xlsx"]
AYMEN_EXTRA: list[Path] = []
OUT = ROOT / "Vignette_Review_Comparison.xlsx"

# Styling follows build_review_workbook.py so the two feel like one artefact.
HDR = PatternFill("solid", fgColor="0F3A44")
OK = PatternFill("solid", fgColor="E3F2EE")       # settled
EDIT = PatternFill("solid", fgColor="FDF2D9")     # settled, edit owed
BAD = PatternFill("solid", fgColor="FBE4E0")      # opposed, or missing
ASKF = PatternFill("solid", fgColor="FFF8E6")     # for the two of you to fill
THIN = Side(style="thin", color="B8C4C4")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

ITEMS = [("answer correct?", "answer"),
         ("findings force it?", "findings"),
         ("quote supports it?", "quote"),
         ("no gendered words?", "wording")]
VERDICTS = ["APPROVE", "APPROVE WITH EDIT", "REJECT"]


def norm(v) -> str:
    """A cell as a comparable string. Blank, None and whitespace are all ''."""
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("", "none", "nan") else s


def read(path: Path) -> dict[str, dict]:
    """One reviewer's filled workbook, keyed by vignette id.

    Reads the header row by NAME rather than by position. Evans' copy carries
    two extra columns he added while reviewing, so a positional read silently
    pairs his 'suggested fix' with Aymen's nothing.
    """
    if not path.exists():
        raise SystemExit(f"compare_vignette_reviews: no such file: {path}")
    wb = load_workbook(path, data_only=True)
    if "Review" not in wb.sheetnames:
        raise SystemExit(f"{path.name}: no 'Review' sheet (has {wb.sheetnames})")
    ws = wb["Review"]
    hdr = {norm(ws.cell(1, c).value): c for c in range(1, ws.max_column + 1)}
    if "id" not in hdr or "APPROVE?" not in hdr:
        raise SystemExit(f"{path.name}: not a review sheet (no id/APPROVE? column)")

    def cell(r, name):
        return norm(ws.cell(r, hdr[name]).value) if name in hdr else ""

    out: dict[str, dict] = {}
    for r in range(2, ws.max_row + 1):
        vid = cell(r, "id")
        if not vid:
            continue
        out[vid] = {
            "condition": cell(r, "condition"),
            "group": cell(r, "group"),
            "verdict": cell(r, "APPROVE?"),
            "comment": cell(r, "your comment"),
            "fix": cell(r, " suggested fix") or cell(r, "suggested fix"),
            "support": cell(r, "sentence in column G that supports the answer"),
            # The evidence columns. Unused by the comparison, read here so that
            # anything building a follow-up round (build_resolution_round.py)
            # can show a vignette without reopening the review workbook.
            "quote": cell(r, "VERBATIM GUIDELINE QUOTE"),
            "clinical": cell(r, "clinical text as the model sees it"),
            "question": cell(r, "question"),
            "options": cell(r, "answer options"),
            "reference": cell(r, "reference answer"),
            "target": cell(r, "target option"),
            "source_status": cell(r, "source status"),
            **{key: cell(r, col) for col, key in ITEMS},
        }
    return out


def load_side(main: Path, extra: list[Path]) -> dict[str, dict]:
    """One reviewer's main sheet plus any focused sheets, merged on id."""
    rows = read(main)
    for p in extra:
        if not p.exists():
            print(f"  note: {p.name} not found, skipping")
            continue
        for vid, row in read(p).items():
            if vid in rows:
                print(f"  note: {vid} is in both {main.name} and {p.name}; "
                      "keeping the focused sheet's answer")
            rows[vid] = row
    return rows


def classify(e: dict | None, a: dict | None) -> tuple[str, str]:
    """(status, why). Status drives the sheet a row lands on and its colour."""
    ev = e["verdict"] if e else ""
    av = a["verdict"] if a else ""

    def answers(row):
        """The item answers one side gave, as a readable line."""
        got = [f"{name} {row[name]}" for _, name in ITEMS if row[name]]
        return ", ".join(got) if got else "no item answers either"

    def gaps():
        """Where the two sides answered the same item differently."""
        return [name for _, name in ITEMS if e[name] != a[name]]

    if e is None or a is None:
        who, other = ("Aymen", e) if a is None else ("Evans", a)
        return ("NOT REVIEWED BY BOTH",
                f"{who} has no row for this vignette. "
                f"The other side: {other['verdict'] or 'no verdict'}")
    if not ev or not av:
        # A blank verdict is not a blank review. Whatever item answers that
        # side did give are the substance of their opinion, and on G2-02 one
        # of them is a No, which is the opposite of the missing APPROVE.
        who, row = ("Aymen", a) if not av else ("Evans", e)
        return ("NOT REVIEWED BY BOTH",
                f"{who} left the verdict blank. {who}'s item answers: "
                f"{answers(row)}")

    differ = gaps()
    also = (" Items also differ: "
            + ", ".join(f"{d} (Evans {e[d] or 'blank'} / Aymen {a[d] or 'blank'})"
                        for d in differ)) if differ else ""

    if ev != av:
        if "REJECT" in (ev, av):
            return "OPPOSED", f"Evans says {ev}, Aymen says {av}.{also}"
        return "EDIT DISPUTED", f"Evans says {ev}, Aymen says {av}.{also}"
    if differ:
        detail = ", ".join(f"{d} (Evans {e[d] or 'blank'} / Aymen {a[d] or 'blank'})"
                           for d in differ)
        return "AGREED, ITEMS DIFFER", f"both say {ev}, but: {detail}"
    if ev == "APPROVE":
        return "AGREED, CLEARED", "both approve, every check matches"
    if ev == "REJECT":
        return "AGREED, REJECTED", "both reject"
    return "AGREED, EDIT OWED", "both approve with edit, so the edit is still owed"


# Most urgent first. The sheet is read top down and so is this.
ORDER = ["OPPOSED", "NOT REVIEWED BY BOTH", "EDIT DISPUTED", "AGREED, ITEMS DIFFER",
         "AGREED, REJECTED", "AGREED, EDIT OWED", "AGREED, CLEARED"]
SETTLED = {"AGREED, CLEARED", "AGREED, EDIT OWED", "AGREED, REJECTED"}
FILLS = {"OPPOSED": BAD, "NOT REVIEWED BY BOTH": BAD, "EDIT DISPUTED": EDIT,
         "AGREED, ITEMS DIFFER": EDIT, "AGREED, REJECTED": OK,
         "AGREED, EDIT OWED": EDIT, "AGREED, CLEARED": OK}


def kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Cohen's kappa on the three-level verdict, over rows both of you filled.

    Reported because raw agreement flatters a sheet where almost everything is
    APPROVE: two people who approve everything agree 100% of the time and have
    told you nothing. Returns None when there is nothing to measure.
    """
    if not pairs:
        return None
    n = len(pairs)
    po = sum(1 for x, y in pairs if x == y) / n
    labels = set(x for x, _ in pairs) | set(y for _, y in pairs)
    pe = sum((sum(1 for x, _ in pairs if x == L) / n) *
             (sum(1 for _, y in pairs if y == L) / n) for L in labels)
    return None if pe >= 1 else (po - pe) / (1 - pe)


def head(ws, names, widths):
    for i, (name, w) in enumerate(zip(names, widths), start=1):
        c = ws.cell(1, i, name)
        c.fill, c.font = HDR, Font(bold=True, color="FFFFFF", size=10)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BOX
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"


def put(ws, r, values, fill=None, wrap_from=None):
    for i, v in enumerate(values, start=1):
        c = ws.cell(r, i, v)
        c.border = BOX
        c.alignment = Alignment(vertical="top",
                                wrap_text=wrap_from is not None and i >= wrap_from)
        if fill is not None:
            c.fill = fill


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evans", type=Path, default=EVANS)
    ap.add_argument("--aymen", type=Path, default=AYMEN)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    print(f"Evans : {args.evans.name}")
    E = load_side(args.evans, EVANS_EXTRA)
    print(f"Aymen : {args.aymen.name}")
    A = load_side(args.aymen, AYMEN_EXTRA)

    ids = sorted(set(E) | set(A))
    rows = []
    for vid in ids:
        e, a = E.get(vid), A.get(vid)
        status, why = classify(e, a)
        rows.append({"id": vid, "e": e, "a": a, "status": status, "why": why,
                     "condition": (e or a).get("condition", "")})
    rows.sort(key=lambda d: (ORDER.index(d["status"]), d["id"]))

    wb = Workbook()

    # ---------------------------------------------------------- 1. summary
    ws = wb.active
    ws.title = "Summary"
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 8
    ws.column_dimensions["C"].width = 74
    r = 1
    ws.cell(r, 1, "Where the two reviews stand").font = Font(bold=True, size=14,
                                                             color="0F3A44")
    r += 2
    both = [d for d in rows if d["e"] and d["a"] and d["e"]["verdict"]
            and d["a"]["verdict"]]
    agreed = [d for d in both if d["e"]["verdict"] == d["a"]["verdict"]]
    k = kappa([(d["e"]["verdict"], d["a"]["verdict"]) for d in both])
    for label, val, note in [
        ("Vignettes in either review", len(rows), "the union of both workbooks"),
        ("Reviewed by both, verdict given", len(both),
         "the only rows on which agreement can be measured"),
        ("Same verdict from both", len(agreed),
         f"{(100 * len(agreed) / len(both)):.0f}% raw agreement" if both else ""),
        ("Cohen's kappa on the verdict", round(k, 3) if k is not None else "n/a",
         "chance-corrected; raw agreement flatters a sheet that is mostly APPROVE"),
    ]:
        ws.cell(r, 1, label).font = Font(bold=True, size=10)
        ws.cell(r, 2, val)
        ws.cell(r, 3, note).font = Font(size=9, color="5A7883")
        r += 1
    r += 1
    ws.cell(r, 1, "By status").font = Font(bold=True, size=11, color="0F3A44")
    r += 1
    MEANING = {
        "OPPOSED": "one of you would keep it, the other would throw it away. Settle first.",
        "NOT REVIEWED BY BOTH": "no second opinion exists yet. Not a disagreement, a gap.",
        "EDIT DISPUTED": "one says approve, the other approve with edit. Decide if the edit is owed.",
        "AGREED, ITEMS DIFFER": "same verdict, different reasons. Check you approved the same thing.",
        "AGREED, REJECTED": "both reject. Out, unless it is replaced.",
        "AGREED, EDIT OWED": "both approve with edit. Nothing to settle, but the edit is still owed.",
        "AGREED, CLEARED": "both approve and every check matches. Done.",
    }
    for st in ORDER:
        n = sum(1 for d in rows if d["status"] == st)
        if not n:
            continue
        c = ws.cell(r, 1, st)
        c.font = Font(bold=True, size=10)
        c.fill = FILLS[st]
        ws.cell(r, 2, n)
        ws.cell(r, 3, MEANING[st]).font = Font(size=9, color="5A7883")
        ws.cell(r, 3).alignment = Alignment(wrap_text=True, vertical="center")
        r += 1
    r += 1
    for line in [
        "This file is generated by scripts/compare_vignette_reviews.py. Do not edit it by hand:",
        "rerun the script when either review changes. Fill the adjudication columns on",
        "'Needs attention' together, then record what you decided in docs/decisions.md.",
        "Nothing here was decided by the script. Every judgment is one of your own cells.",
    ]:
        ws.cell(r, 1, line).font = Font(size=9, color="5A7883")
        r += 1

    # ------------------------------------------------- 2. needs attention
    ws = wb.create_sheet("Needs attention")
    cols = ["id", "condition", "status", "what differs", "Evans verdict",
            "Aymen verdict", "Evans: answer/findings/quote/wording",
            "Aymen: answer/findings/quote/wording",
            "Evans comment", "Evans suggested fix",
            "Aymen comment", "AGREED VERDICT (fill in)", "how you settled it (fill in)"]
    head(ws, cols, [9, 26, 21, 40, 17, 17, 15, 15, 46, 40, 46, 20, 40])
    dv = DataValidation(type="list", formula1='"' + ",".join(VERDICTS) + '"',
                        allow_blank=True)
    ws.add_data_validation(dv)
    r = 2
    for d in rows:
        if d["status"] in SETTLED:
            continue
        e, a = d["e"] or {}, d["a"] or {}
        # The four checks as one short string, in the header's order, so the
        # row can be read without opening the 'Every item' sheet.
        strip = lambda row: " / ".join((row.get(n) or "-") for _, n in ITEMS)
        put(ws, r, [d["id"], d["condition"], d["status"], d["why"],
                    e.get("verdict", "") or "(blank)",
                    a.get("verdict", "") or "(blank)",
                    strip(e) if e else "(no row)", strip(a) if a else "(no row)",
                    e.get("comment", ""), e.get("fix", ""), a.get("comment", ""),
                    None, None], fill=FILLS[d["status"]], wrap_from=2)
        for col in (12, 13):
            ws.cell(r, col).fill = ASKF
        dv.add(ws.cell(r, 12))
        ws.row_dimensions[r].height = 58
        r += 1
    if r == 2:
        ws.cell(2, 1, "Nothing outstanding: every vignette has the same verdict "
                      "from both of you.")

    # --------------------------------------------------------- 3. cleared
    ws = wb.create_sheet("Cleared by both")
    head(ws, ["id", "condition", "verdict", "note", "Evans comment", "Aymen comment"],
         [9, 30, 20, 40, 52, 52])
    r = 2
    for d in rows:
        if d["status"] not in SETTLED:
            continue
        e, a = d["e"], d["a"]
        put(ws, r, [d["id"], d["condition"], e["verdict"], d["why"],
                    e.get("comment", ""), a.get("comment", "")],
            fill=FILLS[d["status"]], wrap_from=2)
        ws.row_dimensions[r].height = 42
        r += 1

    # ------------------------------------------------------- 4. all items
    ws = wb.create_sheet("Every item")
    cols = ["id", "condition", "status"]
    for _, name in ITEMS:
        cols += [f"E: {name}", f"A: {name}"]
    cols += ["E: verdict", "A: verdict"]
    head(ws, cols, [9, 28, 21] + [11] * (2 * len(ITEMS)) + [18, 18])
    r = 2
    for d in rows:
        e, a = d["e"] or {}, d["a"] or {}
        vals = [d["id"], d["condition"], d["status"]]
        for _, name in ITEMS:
            vals += [e.get(name, ""), a.get(name, "")]
        vals += [e.get("verdict", ""), a.get("verdict", "")]
        put(ws, r, vals, fill=FILLS[d["status"]], wrap_from=2)
        # Mark only the cells that actually differ, so the eye goes to them.
        for i, (_, name) in enumerate(ITEMS):
            if e.get(name, "") != a.get(name, ""):
                for col in (4 + 2 * i, 5 + 2 * i):
                    ws.cell(r, col).fill = BAD
                    ws.cell(r, col).font = Font(bold=True)
        r += 1

    wb.save(args.out)

    print(f"\nwrote {args.out.name}")
    print(f"  {len(rows)} vignettes, {len(both)} with a verdict from both")
    if both:
        print(f"  same verdict on {len(agreed)} of {len(both)} "
              f"({100 * len(agreed) / len(both):.0f}%), "
              f"kappa {('%.3f' % k) if k is not None else 'n/a'}")
    print()
    for st in ORDER:
        got = [d for d in rows if d["status"] == st]
        if got:
            print(f"  {st:<24} {len(got):>2}   {', '.join(d['id'] for d in got)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
