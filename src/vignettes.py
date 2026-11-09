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
    "paraphrase", "spcu", "gender_identity", "arm_type", "cue", "age",
    "prompt_text", "question", "answer_options",
    "reference_answer", "target_option", "tier", "verification",
    "analysis_ready", "blocked_on",
]

# Vignettes with no cue factor run a single arm with no appended sentence, so
# the column exists for every row and D027's crossing is visible in the data
# rather than implied by which file a row came from.
NO_CUE = {"cue_absent": ""}


# ---------------------------------------------------------------------------
# D090: THE prompt-set hash. One definition, imported by src.score_outputs and
# scripts.results_summary, because two copies of a hash are two hashes.
#
# It used to hash prompt_text alone. That made the entire staleness mechanism
# blind to the answer options: rewriting G4-10's option set for token-length
# matching changed what every model scores on that item and left the hash
# IDENTICAL, so results_summary would have reported tables built from the old
# options as "matches a scored run". Everything that decides which string is
# scored, or which string counts as correct, belongs in the hash.
HASHED_FIELDS = ("prompt_text", "question", "answer_options",
                 "reference_answer", "target_option")


def prompt_set_hash(df) -> str:
    """sha256 over every field that changes what is scored (D090)."""
    import hashlib
    import pandas as pd
    missing = [c for c in HASHED_FIELDS if c not in df.columns]
    if missing:
        raise KeyError(
            f"prompt_set_hash: prompt frame is missing {missing}. The hash must "
            f"cover every scored field; silently hashing fewer is the D090 bug.")
    joined = df[list(HASHED_FIELDS)].astype(str).agg("\x1f".join, axis=1)
    return hashlib.sha256(
        pd.util.hash_pandas_object(joined, index=False).values.tobytes()
    ).hexdigest()[:16]


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

    # D027, scoped to G3-02 only: a crossed psychologizing cue. The arms differ
    # in ONE appended sentence and nothing else, so the estimand is the cue x
    # gender interaction rather than a main effect of either.
    cue_arms = tpl.get("cue_arms") or NO_CUE

    for p_i, text in enumerate(paraphrases, start=1):
        for spcu in arms["spcu_values"]:
            for gid in arms["gender_identities"]:
              for cue_key, cue_text in cue_arms.items():
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

                  if cue_text:
                      body = body.rstrip() + " " + cue_text

                  # Group 2's answer tracks the SPCU, not the gender label, so
                  # it is resolved per arm. Everywhere else one scalar serves
                  # all six arms -- which is what makes those items bias tests.
                  by_spcu = tpl.get("reference_answer_by_spcu")
                  ref = (by_spcu or {}).get(spcu["key"]) if by_spcu \
                      else tpl.get("reference_answer")

                  # The slot is still present => clinical findings not yet written.
                  clinical_filled = CLINICAL_SLOT not in body
                  # blocked_on now GATES readiness. It used to be recorded and
                  # ignored, so a row the clinical reviewer had rejected still
                  # came out analysis_ready=True and would have been scored. A
                  # reject that does not stop the row from being scored is
                  # decoration. 2026-11-08, D082.
                  blocked = bool((tpl.get("blocked_on") or "").strip())
                  ready = clinical_filled and ref is not None and not blocked

                  rows.append({
                      "prompt_id": (f"{tpl['id']}_p{p_i}_{spcu['key']}_{gid['key']}"
                                    + (f"_{cue_key}" if len(cue_arms) > 1 else "")),
                      "vignette_id": tpl["id"],
                      "group": tpl["group"],
                      "condition": tpl["condition"],
                      "guideline_ref": tpl.get("guideline_ref"),
                      "paraphrase": p_i,
                      "spcu": spcu["key"],
                      "gender_identity": gid["key"],
                      "arm_type": "blinded" if gid["key"] == "blinded" else "gendered",
                      "cue": cue_key,
                      "age": tpl["age"],
                      "prompt_text": body,
                      "question": tpl.get("question"),
                      "answer_options": "|".join(tpl.get("answer_options") or []),
                      "reference_answer": ref,
                      "target_option": tpl.get("target_option"),
                      "verification": tpl.get("verification", "unverified"),
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
