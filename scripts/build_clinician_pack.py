"""Assemble everything a clinical reviewer needs into one folder.

WHY THIS EXISTS. The review materials were scattered: the form in the repository
root, two briefs in docs/, the compendium in docs/, and the guideline PDFs in
papers/ under filenames like `ciu296.pdf` that say nothing about which vignette
they support. A reviewer asked to check 25 reference answers against 25
guidelines should not have to work out which file is which.

WHAT IT DOES NOT DO. It copies; it never edits. The form is whatever
`scripts/build_review_workbook.py --live-only` last wrote, and the guideline PDFs
are the same bytes as in papers/, so a quote the reviewer checks in the pack is
the quote we read.

Two sources are deliberately EXCLUDED even though they sit in papers/:
NICE NG91 (otitis media, scoped to children) and the UKKA hyperkalaemia
guideline. Both appear in docs/vignette_sources.md only as evidence that they
CANNOT source the row they were once attached to. Shipping them beside the
guidelines of record would re-create exactly the error the clinical review caught
in round 4, where a hyperkalaemia quote was presented as evidence for a
meningitis vignette.

Usage:  .venv/bin/python scripts/build_clinician_pack.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clinician_pack"

FORM = ROOT / "Vignette_Review_Datasheet_to_Diagnosis.xlsx"

DOCS = [
    ("01_START_HERE_what_we_are_asking.md", ROOT / "docs/clinical_review_request.md"),
    ("03_briefing_notes.md",                ROOT / "docs/clinical_review_form.md"),
    ("04_vignettes_compendium.md",          ROOT / "docs/vignettes_compendium.md"),
]

# vignette -> (file in papers/, short condition label)
GUIDELINES: dict[str, tuple[str, str]] = {
    "G1-02":  ("B09879-eng.pdf",                       "malaria"),
    "G1-03":  ("GINA-2026-Strategy-Report-WMS.pdf",    "asthma exacerbation"),
    "G1-04":  ("ciu296.pdf",                           "cellulitis"),
    "G1-05":  ("DC-Guidelines-2024-Pharm2-Update-CHAPTER.pdf", "type 2 diabetes"),
    "G2-01b": ("ACR-SPR_imaging_pregnant_2023_Res31.pdf", "pregnancy test before CT"),
    "G2-02":  ("cuaj-8-245-main.pdf",                  "male LUTS BPH"),
    "G3-01":  ("NICE_ng118.pdf",                       "acute pain, renal colic"),
    "G3-04":  ("attention-deficit-hyperactivity-disorder-diagnosis-and-management-pdf-1837699732933.pdf",
               "ADHD referral"),
    "G3-05":  ("autism-spectrum-disorder-in-adults-diagnosis-and-management-pdf-35109567475909.pdf",
               "autism referral"),
    "G3-07":  ("NICE_ng185.pdf",                       "cardiac rehab referral"),
    "G3-08":  ("NICE_ng226.pdf",                       "joint replacement referral"),
    "G4-01":  ("jama_269_9_034.pdf",                   "ankle sprain"),
    "G4-02":  ("ciu296.pdf",                           "cutaneous abscess"),
    "G4-04":  ("NICE_ng79.pdf",                        "acute sinusitis"),
    "G4-05":  ("NICE_ng141.pdf",                       "cellulitis, floor item"),
    "G4-06":  ("AAO-HNS_Rosenfeld_2014_acute_otitis_externa.pdf", "otitis externa"),
    "G4-07":  ("NICE_ng158.pdf",                       "suspected DVT"),
    "G4-08":  ("RCUK_anaphylaxis_2021.pdf",            "anaphylaxis"),
    "G4-09":  ("NICE_ng232.pdf",                       "minor head injury"),
    "G4-10":  ("NICE_ng153.pdf",                       "impetigo"),
    "G4-11":  ("NICE_ng240.pdf",                       "bacterial meningitis"),
}

# Held at their DOI rather than as a file: we cite them, but the PDF is not
# redistributable from here. Named so the gap is visible, not silently absent.
BY_DOI = {
    "G1-01":  "Community-acquired pneumonia, ATS/IDSA, doi:10.1164/rccm.201908-1581ST",
    "G2-03b": "Cervical screening, USPSTF, doi:10.1001/jama.2018.10897",
    "G3-02":  "Chest pain evaluation, AHA/ACC, doi:10.1161/CIR.0000000000001029",
    "G4-03b": "Group A streptococcal pharyngitis, IDSA, doi:10.1093/cid/cis629",
}


def main() -> int:
    refs = json.loads((ROOT / "docs/references.json").read_text(encoding="utf-8"))
    cited = {v for e in refs["guidelines"] for v in e["vignettes"]}
    covered = set(GUIDELINES) | set(BY_DOI)
    if cited != covered:
        print(f"MISMATCH against references.json:")
        print(f"  cited but not in this pack : {sorted(cited - covered)}")
        print(f"  in this pack but not cited : {sorted(covered - cited)}")
        return 1

    if not FORM.exists():
        return print(f"missing {FORM.name}; run build_review_workbook.py --live-only") or 1

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "guidelines").mkdir(parents=True)

    shutil.copy2(FORM, OUT / "02_REVIEW_FORM.xlsx")
    for name, src in DOCS:
        shutil.copy2(src, OUT / name)

    copied = []
    for vid, (fname, label) in sorted(GUIDELINES.items()):
        src = ROOT / "papers" / fname
        if not src.exists():
            print(f"  MISSING {src}")
            return 1
        dest = OUT / "guidelines" / f"{vid}_{label.replace(' ', '_').replace(',', '')}.pdf"
        shutil.copy2(src, dest)
        copied.append((vid, dest.name))

    cite_of = {}
    for e in refs["guidelines"]:
        for v in e["vignettes"]:
            cite_of[v] = e["cite"]

    lines = [
        "# Clinical review pack",
        "",
        "From datasheet to diagnosis: tracing gender bias through open training-data",
        "pipelines into LLM health advice. Evans Kumi and Aymen Boustani, MSc",
        "Intelligent Systems, McGill.",
        "",
        "Everything needed for the review is in this folder. Read them in order.",
        "",
        "| | File | What it is |",
        "|---|---|---|",
        "| 1 | `01_START_HERE_what_we_are_asking.md` | One page: what we are testing and why a clinician is needed |",
        "| 2 | `02_REVIEW_FORM.xlsx` | **The form.** Open the `Review` sheet and fill columns N to S |",
        "| 3 | `03_briefing_notes.md` | How to read each column, plus Sections 1, 3 and 4 |",
        "| 4 | `04_vignettes_compendium.md` | Background: every vignette and how it was built |",
        "| 5 | `guidelines/` | The guideline PDFs, one per vignette, named by vignette id |",
        "",
        "## Where to spend your time",
        "",
        "The `Review` sheet is the whole task. Column G holds the guideline quote and",
        "column I holds the clinical text exactly as the model receives it. The question",
        "is whether a clinician reading column I could reach the reference answer in",
        "column L **and no other answer**. Column H is our own reading of whether the",
        "guideline stratifies by sex anywhere; please contradict it where you disagree.",
        "",
        "Group 2 rows appear with both sex-parameter arms, because for those three the",
        "correct answer is meant to differ.",
        "",
        "**Please reject rather than repair.** If an item is wrong, mark it and say why.",
        "We would rather rewrite a vignette than carry one that looks right and is not.",
        "",
        "## Guidelines included",
        "",
        f"{len(copied)} of {len(cited)} vignettes have their governing document in",
        "`guidelines/`. Each file is the same PDF we quoted from.",
        "",
        "| Vignette | File | Citation of record |",
        "|---|---|---|",
    ]
    for vid, fname in copied:
        lines.append(f"| {vid} | `{fname}` | {cite_of[vid][:150]} |")
    lines += [
        "",
        "### Held at their DOI instead of as a file",
        "",
        "These three are cited the same way but are not redistributed here; the DOI",
        "resolves to the publisher's copy.",
        "",
    ]
    for vid, what in sorted(BY_DOI.items()):
        lines.append(f"- **{vid}** {what}")
    lines += [
        "",
        "## Two things to know before you start",
        "",
        "**The clinical text was AI-drafted** from guideline passages we located and",
        "quoted ourselves, then author-reviewed. It was not written by a clinician. A",
        "drafted scenario can read fluently, name every finding a rule requires, and",
        "still fail to exclude one alternative. That is the failure we cannot catch",
        "ourselves and the main reason we are asking you.",
        "",
        "**We have already reviewed these rows ourselves** (14 approve, 9 approve with",
        "edit, 2 reject), which is why two vignettes were replaced before you see them.",
        "Our own review cannot validate our own work, so every result we hold currently",
        "reads NOT REPORTABLE. Your sign-off is what changes that, and no result is",
        "reported on a vignette you have not passed. That is enforced in our code.",
        "",
        "Return to: evans.kumi@mail.mcgill.ca",
    ]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    mb = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1048576
    print(f"wrote {OUT.relative_to(ROOT)}/")
    print(f"  {n} files, {mb:.1f} MB")
    print(f"  {len(copied)} guideline PDFs, {len(BY_DOI)} cited by DOI only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
