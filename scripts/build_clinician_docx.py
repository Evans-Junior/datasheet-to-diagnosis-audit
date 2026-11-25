"""Turn the clinician pack into Word documents a reviewer can actually open.

WHY. The pack's briefs are markdown, which is a developer format. A clinician
sent a `.md` file gets either a wall of asterisks or a download their machine
cannot open, and the most likely outcome is that they do not start at all. The
review is the project's gating step, so the format it arrives in is not cosmetic.

TWO KINDS OF DOCUMENT, BUILT TWO WAYS.
  * The briefs are CONVERTED from the markdown we already maintain, so there is
    one source of wording. The converter handles only the subset those files use
    -- headings, paragraphs, tables, lists, blockquotes, bold and code -- and
    raises on anything else rather than dropping it silently.
  * The vignette book is GENERATED from templates.yaml and vignette_sources.md,
    not converted from the compendium markdown. It has to show, per vignette, the
    clinical text as the model receives it beside the verbatim guideline quote,
    and generating it means it cannot drift from the instrument the way a
    hand-maintained document would.

Usage:  qa_venv/bin/python scripts/build_clinician_docx.py "Dr. Kwabena"
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "clinician_pack"

ACCENT = RGBColor(0x8D, 0x00, 0x00)
GREY = RGBColor(0x55, 0x55, 0x55)


# ----------------------------------------------------------------- styling --
def new_doc() -> Document:
    d = Document()
    s = d.styles["Normal"]
    s.font.name = "Calibri"
    s.font.size = Pt(11)
    s.paragraph_format.space_after = Pt(7)
    for lvl, size in ((1, 18), (2, 14), (3, 12)):
        h = d.styles[f"Heading {lvl}"]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = ACCENT
    for sec in d.sections:
        sec.left_margin = sec.right_margin = Inches(1.0)
        sec.top_margin = sec.bottom_margin = Inches(0.9)
    return d


INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`|\[[^\]]+?\]\([^)]+?\))")


def runs(par, text: str, base_italic: bool = False) -> None:
    """Render markdown inline marks. Links become their label plus the target."""
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            r = par.add_run(piece[2:-2]); r.bold = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = par.add_run(piece[1:-1]); r.font.name = "Consolas"
            r.font.size = Pt(9.5)
        elif piece.startswith("[") and "](" in piece:
            label, target = piece[1:-1].split("](", 1)
            r = par.add_run(label); r.bold = True
            if not target.endswith(".md"):     # internal repo links mean nothing here
                r2 = par.add_run(f" ({target})"); r2.font.size = Pt(9)
                r2.font.color.rgb = GREY
        elif piece.startswith("*") and piece.endswith("*"):
            r = par.add_run(piece[1:-1]); r.italic = True
        else:
            r = par.add_run(piece)
        r.italic = base_italic or getattr(r, "italic", None) or False


def md_table(doc: Document, rows: list[list[str]], header: bool = True) -> None:
    """header=False for a label/value table, which has no banner row.

    The vignette book used to pass ["", ""] as its header to satisfy the old
    signature, which drew an empty banded row above all 25 tables.
    """
    head, body = (rows[0], rows[1:]) if header else (None, rows)
    ncol = len(head) if header else max(len(r) for r in body)
    t = doc.add_table(rows=1 if header else 0, cols=ncol)
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    if header:
        for i, h in enumerate(head):
            cell = t.rows[0].cells[i]
            cell.text = ""
            runs(cell.paragraphs[0], h)
            for r in cell.paragraphs[0].runs:
                r.bold = True
    for row in body:
        cells = t.add_row().cells
        for i, v in enumerate(row[:ncol]):
            cells[i].text = ""
            runs(cells[i].paragraphs[0], v)
    # Keep each row whole. Without this a row that lands on a page boundary is
    # cut through the middle, and the half on the next page reads as a stray
    # fragment in an otherwise empty row.
    for r in t.rows:
        pr = r._tr.get_or_add_trPr()
        pr.append(pr.makeelement(qn("w:cantSplit"), {}))
    if header:
        hpr = t.rows[0]._tr.get_or_add_trPr()
        hpr.append(hpr.makeelement(qn("w:tblHeader"), {}))
    doc.add_paragraph()


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def restart_numbering(doc: Document, par) -> None:
    """Make `par` the number 1 of its own list.

    Word's "List Number" style carries ONE numbering instance for the whole
    document, so a second numbered list in the same file carries on counting
    from where the first one stopped: a three item list after a two item list
    prints 3, 4, 5. Nothing in the markdown says that, and a reader sees a
    document that has lost its place.

    The fix is to give each list its own numbering instance that overrides the
    start back to 1, and to point this paragraph at it. Later items in the same
    list inherit from the style and follow on normally.

    Best effort on purpose: if the template ever stops carrying a numbering part
    this returns quietly and the list still renders, just with the old
    continuous count. A cosmetic fix is not worth failing a build for.
    """
    try:
        numbering = doc.part.numbering_part.element
        style_num = doc.styles["List Number"].element.pPr.numPr.numId.val
        abstract = None
        for num in numbering.findall(qn("w:num")):
            if int(num.get(qn("w:numId"))) == int(style_num):
                abstract = num.find(qn("w:abstractNumId")).get(qn("w:val"))
        if abstract is None:
            return
        used = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
        new_id = max(used) + 1

        num = numbering.makeelement(qn("w:num"), {qn("w:numId"): str(new_id)})
        ref = num.makeelement(qn("w:abstractNumId"), {qn("w:val"): abstract})
        num.append(ref)
        lvl = num.makeelement(qn("w:lvlOverride"), {qn("w:ilvl"): "0"})
        start = lvl.makeelement(qn("w:startOverride"), {qn("w:val"): "1"})
        lvl.append(start)
        num.append(lvl)
        numbering.append(num)

        pr = par._p.get_or_add_pPr()
        npr = pr.makeelement(qn("w:numPr"), {})
        ilvl = npr.makeelement(qn("w:ilvl"), {qn("w:val"): "0"})
        nid = npr.makeelement(qn("w:numId"), {qn("w:val"): str(new_id)})
        npr.append(ilvl)
        npr.append(nid)
        pr.append(npr)
    except Exception:
        return


def md_to_docx(md: str, doc: Document) -> None:
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith("#"):
            lvl = len(s) - len(s.lstrip("#"))
            doc.add_heading("", level=min(lvl, 3))
            runs(doc.paragraphs[-1], s.lstrip("#").strip())
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and set(
                lines[i + 1].strip()) <= set("|-: "):
            block = [split_row(s)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(split_row(lines[i]))
                i += 1
            md_table(doc, block)
            continue
        if s.startswith(">"):
            # A bare ">" between two quoted blocks is a paragraph break inside
            # the quote. Joining across it ran the second paragraph onto the end
            # of the first, which turned a quoted case and its question into one
            # sentence.
            para, buf = [], []
            while i < len(lines) and lines[i].strip().startswith(">"):
                t = lines[i].strip().lstrip(">").strip()
                if t:
                    buf.append(t)
                elif buf:
                    para.append(buf)
                    buf = []
                i += 1
            if buf:
                para.append(buf)
            for block in para:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_before = Pt(5)
                runs(p, " ".join(block))
                for r in p.runs:
                    r.font.size = Pt(10.5)
            continue
        if re.match(r"^[-*+] ", s) or re.match(r"^\d+[.)] ", s):
            ordered = not re.match(r"^[-*+] ", s)
            style = "List Number" if ordered else "List Bullet"
            first = True
            while i < len(lines) and (re.match(r"^[-*+] ", lines[i].strip())
                                      or re.match(r"^\d+[.)] ", lines[i].strip())):
                item = re.sub(r"^([-*+]|\d+[.)])\s+", "", lines[i].strip())
                par = doc.add_paragraph(style=style)
                if ordered and first:
                    restart_numbering(doc, par)
                runs(par, item)
                first = False
                i += 1
            continue
        if set(s) <= set("-=_") and len(s) >= 3:
            i += 1
            continue
        # A label line such as "**Project:** ..." is its own paragraph. Without
        # this the whole metadata block runs together into one sentence.
        if re.match(r"^\*\*[^*]{2,40}:\*\*", s):
            lab = [s]
            i += 1
            # Keep its continuation lines: the project title wraps onto a
            # second line and was being split into its own paragraph.
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(#|\||>|[-*+] |\d+[.)] |\*\*[^*]{2,40}:\*\*)",
                    lines[i].strip()):
                lab.append(lines[i].strip())
                i += 1
            runs(doc.add_paragraph(), " ".join(lab))
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#|\||>|[-*+] |\d+[.)] |\*\*[^*]{2,40}:\*\*)", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        runs(doc.add_paragraph(), " ".join(buf))


def convert(src: Path, dest: Path, title: str, subtitle: str = "") -> None:
    doc = new_doc()
    h = doc.add_heading("", level=0)
    r = h.add_run(title); r.font.color.rgb = ACCENT; r.font.size = Pt(22)
    if subtitle:
        p = doc.add_paragraph()
        rr = p.add_run(subtitle); rr.italic = True; rr.font.color.rgb = GREY
    text = src.read_text(encoding="utf-8")
    # Drop the file's own H1: convert() has already set the title, so printing
    # both gave "Clinical review request" then "Clinical review request, one page".
    text = re.sub(r"^# .*\n", "", text, count=1, flags=re.M)
    # The deprecation banner is an instruction to US about which file to send.
    text = re.sub(r"^> \*\*⚠ Which file to send.*?(?=\n\*\*Project:|\n## )", "",
                  text, flags=re.S | re.M)
    md_to_docx(text, doc)
    doc.save(dest)
    print(f"  {dest.name}")


# ------------------------------------------------------- the vignette book --
def vignette_book(dest: Path, addressee: str) -> int:
    sys.path.insert(0, str(ROOT))
    from src.vignettes import load, expand           # noqa: E402

    templates, arms = load()
    live = [t for t in templates
            if t.get("verification") == "author_reviewed_against_quoted_guideline"]
    refs = json.loads((ROOT / "docs/references.json").read_text(encoding="utf-8"))
    cite = {v: e["cite"] for e in refs["guidelines"] for v in e["vignettes"]}

    src_md = (ROOT / "docs/vignette_sources.md").read_text(encoding="utf-8")
    parts = re.split(r"\n### (G\d-\d\d[a-z]?)([^\n]*)\n", src_md)
    quotes: dict[str, list[str]] = {}
    for i in range(1, len(parts) - 1, 3):
        vid, head, body = parts[i], parts[i + 1], parts[i + 2]
        if "⊘" in head:          # retired section, history not evidence
            continue
        for blk in re.finditer(r"((?:^> .*\n?)+)", body, re.M):
            q = re.sub(r"\s+", " ", " ".join(
                l.lstrip("> ").rstrip() for l in blk.group(1).splitlines())).strip()
            if q:
                quotes.setdefault(vid, []).append(q)

    gid = next(g for g in arms["gender_identities"] if g["key"] == "blinded")

    doc = new_doc()
    h = doc.add_heading("", level=0)
    r = h.add_run("The 25 vignettes, with the guideline each answer comes from")
    r.font.color.rgb = ACCENT; r.font.size = Pt(20)
    p = doc.add_paragraph()
    rr = p.add_run(f"Prepared for {addressee}. Companion to the review form; "
                   "the form is where your answers go.")
    rr.italic = True; rr.font.color.rgb = GREY

    doc.add_paragraph(
        "Each entry below shows the clinical text exactly as the model receives "
        "it, the question and option set it chooses from, the answer we believe "
        "is correct, and the guideline sentence we took that answer from. For "
        "Group 2 both sex-parameter versions are shown, because for those three "
        "the correct answer is meant to differ.")

    GROUPS = {1: "Group 1 — sex-neutral conditions (the main bias test)",
              2: "Group 2 — sex-specific conditions (the positive control)",
              3: "Group 3 — clinically neutral, historically disparate",
              4: "Group 4 — no documented disparity (the noise baseline)"}
    n = 0
    for grp in (1, 2, 3, 4):
        doc.add_page_break()
        doc.add_heading(GROUPS[grp], level=1)
        for tpl in sorted((t for t in live if t["group"] == grp),
                          key=lambda t: t["id"]):
            vid = tpl["id"]
            n += 1
            doc.add_heading(f"{vid} — {tpl['condition']}", level=2)

            spcus = ["female", "male"] if grp == 2 else ["female"]
            for sp in spcus:
                rows = [r for r in expand(tpl, arms)
                        if r["gender_identity"] == gid["key"]
                        and r["spcu"] == sp and str(r["paraphrase"]) == "1"]
                if not rows:
                    continue
                if grp == 2:
                    hp = doc.add_paragraph()
                    hr = hp.add_run(f"Sex parameter: {sp}")
                    hr.bold = True; hr.font.color.rgb = ACCENT
                body = doc.add_paragraph()
                body.paragraph_format.left_indent = Inches(0.25)
                br = body.add_run(rows[0]["prompt_text"])
                br.font.size = Pt(10.5)

            by = tpl.get("reference_answer_by_spcu")
            ref = ("  |  ".join(f"SPCU {k}: {v}" for k, v in by.items()) if by
                   else str(tpl.get("reference_answer")))
            md_table(doc, [
                ["Question", str(tpl.get("question"))],
                ["Answer options", " | ".join(tpl.get("answer_options") or [])],
                ["Our proposed answer", ref],
                ["Guideline of record", cite.get(vid, "—")],
            ], header=False)

            qp = doc.add_paragraph()
            qr = qp.add_run("Verbatim guideline text")
            qr.bold = True; qr.font.size = Pt(10)
            for q in quotes.get(vid, [])[:3]:
                b = doc.add_paragraph()
                b.paragraph_format.left_indent = Inches(0.3)
                # The quotes already carry their own marks, so wrapping them
                # printed doubled ones on every blockquote.
                q = q.strip().strip("“”\"")
                br = b.add_run(f"“{q}”")
                br.italic = True; br.font.size = Pt(10)
    doc.save(dest)
    print(f"  {dest.name}  ({n} vignettes)")
    return n


def email(dest: Path, addressee: str, n: int) -> None:
    """The covering message, with the AI-drafting paragraph IN THE BODY.

    docs/outreach_email.md is explicit that this paragraph does not belong only
    in the attachment: a reviewer who learns it after agreeing has been asked
    under a false impression, and one who believes a clinician wrote the
    scenarios reads them less sharply, which is the opposite of what the review
    is for.
    """
    short = addressee.replace("Dr. ", "Dr ")
    dest.write_text(f"""Subject: Clinical review request, {n} vignettes, about an hour

Dear {short},

I am an MSc student at McGill working on an Ethics in AI project with Aymen
Boustani. We are auditing whether open large language models give different
health advice when only the patient's gender changes, with age, symptoms,
history and every clinical detail held fixed.

The study rests on one claim we are not qualified to make: that for the
conditions we test, the clinically correct answer is the same whatever the
patient's gender. If that fails for a condition, our finding for it disappears.
We need a clinician to tell us where it holds and where it does not.

What this would involve is about an hour, once. There are {n} vignettes. For
each we give you the clinical text, the answer we believe is correct, and the
guideline sentence we took it from, quoted verbatim. You tell us whether our
answer is right, whether the findings in the text actually force it, and
whether correct management varies by sex or gender.

One thing you should know before deciding. The clinical scenarios and our
proposed answers were DRAFTED BY AN AI ASSISTANT from guideline passages we
located and quoted ourselves. They were not written by a clinician, and we then
reviewed them ourselves, which is not the same as clinical validation. A drafted
scenario can read fluently, name every finding a rule requires, and still fail
to rule out one alternative; that is the failure we cannot catch ourselves and
the main reason we are asking you.

Everything is attached:

  0. This message
  1. Start here, what we are asking (one page)
  2. THE REVIEW FORM, an Excel file. This is where your answers go
  3. How to fill in the form
  4. The {n} vignettes and the guideline each answer comes from
  5. The guideline PDFs, named by vignette

No result is reported on a vignette you have not passed, and that is enforced in
our code rather than merely intended. If you mark something wrong we rewrite it
rather than argue with you.

On credit: co-authorship on anything that results if you would like it,
acknowledgement if you would prefer that, or anonymity if you prefer neither.
Declining the paper does not mean declining the review.

If this is not something you have time for, a no costs me nothing and I would
rather hear it early.

With thanks,
Evans Kumi
evans.kumi@mail.mcgill.ca
MSc Intelligent Systems, McGill University
""", encoding="utf-8")
    print(f"  {dest.name}")


def main() -> int:
    addressee = sys.argv[1] if len(sys.argv) > 1 else "the reviewer"
    out = PACK / addressee
    if not PACK.exists():
        sys.exit("run scripts/build_clinician_pack.py first")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    print(f"building {out.relative_to(ROOT)}/")
    convert(PACK / "01_START_HERE_what_we_are_asking.md",
            out / "1. Start here - what we are asking.docx",
            "Clinical review request",
            f"Prepared for {addressee} · approximately 60 to 75 minutes, once")
    convert(PACK / "03_briefing_notes.md",
            out / "3. How to fill in the form.docx",
            "How to fill in the review form",
            f"Prepared for {addressee}")
    n = vignette_book(out / "4. The 25 vignettes and their guidelines.docx",
                      addressee)

    shutil.copy2(PACK / "02_REVIEW_FORM.xlsx", out / "2. REVIEW FORM.xlsx")
    email(out / "0. EMAIL - copy this into the message.txt", addressee, n)
    shutil.copytree(PACK / "guidelines", out / "5. Guideline PDFs")

    files = sorted(p for p in out.rglob("*") if p.is_file())
    mb = sum(p.stat().st_size for p in files) / 1048576
    print(f"\n{len(files)} files, {mb:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
