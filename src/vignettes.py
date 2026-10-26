"""Build counterfactual vignette variants from templates (Phase 1).

Expansion per vignette:
    3 paraphrases x 2 SPCU values x 4 arms = 24 prompts
    (arms: man, woman, non-binary, and a gender-blinded reference -- D021)

SPCU is stated and held fixed within a prompt; gender identity varies (D001).
Both SPCU values are generated so an SPCU effect cannot be mistaken for a
gender-identity effect (D012).

The clinical slot {{CLINICAL_FINDINGS}} and `reference_answer` are left for the
authors to fill from the guideline named in each template's `guideline_ref`
(D003). This module never writes clinical content; it refuses to mark a vignette
analysis-ready while either is missing.

Usage:
    .venv/bin/python -m src.vignettes --build
    .venv/bin/python -m src.vignettes --build --include-unready
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "data/vignettes/templates.yaml"
ARMS = ROOT / "configs/gender_arms.yaml"
OUT = ROOT / "data/vignettes/vignettes.csv"

CLINICAL_SLOT = "<<CLINICAL_FINDINGS>>"

FIELDS = [
    "prompt_id", "vignette_id", "group", "condition", "guideline_ref",
    "paraphrase", "spcu", "gender_identity", "arm_type", "age",
    "prompt_text", "question", "answer_options",
    "reference_answer", "tier", "analysis_ready", "blocked_on",
]


def load() -> tuple[list[dict], dict]:
    templates = yaml.safe_load(TEMPLATES.read_text())
    meta = next((t for t in templates if isinstance(t, dict) and "meta" in t), None)
    if meta is not None:
        templates = [t for t in templates if t is not meta]
    arms = yaml.safe_load(ARMS.read_text())
    return templates, arms


def expand(tpl: dict, arms: dict) -> list[dict]:
    rows = []
    paraphrases = tpl.get("paraphrases") or []
    if not paraphrases:
        return rows

    for p_i, text in enumerate(paraphrases, start=1):
        for spcu in arms["spcu_values"]:
            for gid in arms["gender_identities"]:
                body = text.format(
                    label=gid["label"],
                    subject=gid["subject"],
                    object=gid["object"],
                    possessive=gid["possessive"],
                    spcu_statement=spcu["statement"],
                    age=tpl["age"],
                    be=gid["be"],
                    present_v=gid["present_v"],
                    report_v=gid["report_v"],
                    attend_v=gid["attend_v"],
                )
                # Sentence-initial pronoun capitalisation, done after
                # substitution so templates stay readable.
                body = _fix_caps(body)

                # The slot is still present => clinical findings not yet written.
                clinical_filled = CLINICAL_SLOT not in body
                has_answer = tpl.get("reference_answer") is not None
                ready = clinical_filled and has_answer

                rows.append({
                    "prompt_id": f"{tpl['id']}_p{p_i}_{spcu['key']}_{gid['key']}",
                    "vignette_id": tpl["id"],
                    "group": tpl["group"],
                    "condition": tpl["condition"],
                    "guideline_ref": tpl.get("guideline_ref"),
                    "paraphrase": p_i,
                    "spcu": spcu["key"],
                    "gender_identity": gid["key"],
                    "arm_type": "blinded" if gid["key"] == "blinded" else "gendered",
                    "age": tpl["age"],
                    "prompt_text": body,
                    "question": tpl.get("question"),
                    "answer_options": "|".join(tpl.get("answer_options") or []),
                    "reference_answer": tpl.get("reference_answer"),
                    "tier": tpl.get("tier"),
                    "analysis_ready": ready,
                    "blocked_on": (tpl.get("blocked_on") or "").strip(),
                })
    return rows


def _fix_caps(s: str) -> str:
    out, cap = [], True
    for ch in s:
        out.append(ch.upper() if cap and ch.isalpha() else ch)
        if ch in ".!?":
            cap = True
        elif not ch.isspace():
            cap = False
    return "".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--include-unready", action="store_true",
                    help="write rows that are not analysis-ready (default: write "
                         "all rows but flag them)")
    args = ap.parse_args()
    if not args.build:
        ap.print_help()
        return

    templates, arms = load()
    rows: list[dict] = []
    skipped: list[str] = []
    for tpl in templates:
        got = expand(tpl, arms)
        if not got:
            skipped.append(f"{tpl['id']} ({(tpl.get('blocked_on') or 'no paraphrases').split(chr(10))[0][:60]})")
        rows.extend(got)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    ready = sum(1 for r in rows if r["analysis_ready"])
    n_vig = len({r["vignette_id"] for r in rows})
    per_group: dict[int, int] = {}
    for r in rows:
        per_group[r["group"]] = per_group.get(r["group"], 0) + 1

    print(f"templates expanded : {n_vig}")
    print(f"prompts generated  : {len(rows)}")
    print(f"  per group        : {dict(sorted(per_group.items()))}")
    print(f"  arms per vignette: {len(rows) // n_vig if n_vig else 0}")
    print(f"analysis-ready     : {ready}/{len(rows)}")
    if skipped:
        print("\nskipped (blocked):")
        for s in skipped:
            print(f"  - {s}")
    if ready < len(rows):
        print(f"\nNOT READY TO SCORE. {len(rows) - ready} prompts still need a "
              f"clinical findings slot filled and/or a sourced reference answer.\n"
              f"See docs/vignette_sources.md — fill the verbatim guideline quote "
              f"first, then the reference answer.")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
