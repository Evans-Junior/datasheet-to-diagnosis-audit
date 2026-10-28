"""Pre-build validation of data/vignettes/templates.yaml.

Run after filling in clinical findings, reference answers and answer options, and
BEFORE `src.vignettes --build`. Everything checked here is a fault that is cheap to
fix now and either expensive or impossible to fix after scoring:

  C1 unfilled slots     <<CLINICAL_FINDINGS>> still present, reference_answer null,
                        or answer_options left as option_a..d placeholders.
  C2 option length      Token-length spread within each option set. No score key is
                        length-neutral, so an unmatched set squashes the real effect
                        toward zero and reads as "no bias found" (D035).
  C3 reference validity reference_answer must be one of answer_options, or the
                        scored "correct" option can never be selected.
  C4 pregnancy clause   Templates that append a pregnancy-exclusion sentence must
                        have findings ending in a terminator, or the slot produces a
                        run-on (D018). Flags the guidelines that REQUIRE the clause.
  C5 arm symmetry       Paraphrases of one vignette must share clinical content,
                        age, SPCU and question -- otherwise prompt sensitivity and
                        gender effects are inseparable (D013).
  C6 cue factor         G3-02 only: D027's cue-present/cue-absent arms must differ
                        in the cue sentence and nothing else.

Exit code 1 if any BLOCKER fires. WARN items are judgement calls for the authors.

Usage:
    .venv/bin/python -m scripts.check_templates
    .venv/bin/python -m scripts.check_templates --tokenizer EleutherAI/pythia-410m
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "data/vignettes/templates.yaml"

SLOT = "<<CLINICAL_FINDINGS>>"
PLACEHOLDER_OPTS = {"option_a", "option_b", "option_c", "option_d"}

# Vignettes whose GUIDELINE IS QUOTED as carving out pregnancy, in
# docs/vignette_sources.md. Sourced fact, not inference: WHO malaria names
# artemether-lumefantrine for the first trimester, Diabetes Canada avoids
# incretins/SGLT2i in pregnancy, GINA has a pregnancy section. Whether a given
# vignette should therefore carry the exclusion clause is a CLINICAL judgement and
# stays with the authors (AI_USE.md), so this is a WARN carrying the evidence, not
# a BLOCK asserting the answer.
PREGNANCY_CARVEOUT_DOCUMENTED = {
    "G1-02": "WHO malaria: artemether-lumefantrine specified for the first "
             "trimester; AS+SP and ASPY not recommended in it",
    "G1-03": "GINA 2026: a dedicated pregnancy section; ICS not to be stopped",
    "G1-05": "Diabetes Canada 2024: incretins and SGLT2i avoided or discontinued "
             "in pregnancy or when planning one",
}

# Vignettes where the clause would DESTROY the item, because the decision under
# test is the pregnancy test itself. This one is structural, not clinical.
PREGNANCY_FORBIDDEN = {"G2-01"}

# Max acceptable token spread within an option set (D035).
MAX_TOKEN_SPREAD = 2

blockers: list[str] = []
warnings: list[str] = []


def blocker(vid: str, msg: str) -> None:
    blockers.append(f"  [BLOCK] {vid}: {msg}")


def warn(vid: str, msg: str) -> None:
    warnings.append(f"  [WARN ] {vid}: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default="EleutherAI/pythia-70m")
    ap.add_argument("--strict", action="store_true",
                    help="treat WARN as BLOCK")
    args = ap.parse_args()

    vignettes = yaml.safe_load(TEMPLATES.read_text())
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.tokenizer)

    def ntok(s: str) -> int:
        return len(tok(" " + str(s).strip(), add_special_tokens=False).input_ids)

    filled = 0
    for v in vignettes:
        vid = v["id"]
        paras = v.get("paraphrases") or []
        opts = v.get("answer_options") or []
        ref = v.get("reference_answer")

        # ---- C1 unfilled ------------------------------------------------- #
        slots = sum(SLOT in p for p in paras)
        if slots:
            blocker(vid, f"{slots}/{len(paras)} paraphrases still contain {SLOT}")
        else:
            filled += 1
        if ref in (None, "", "null"):
            blocker(vid, "reference_answer is null")
        if set(map(str, opts)) & PLACEHOLDER_OPTS:
            ph = sorted(set(map(str, opts)) & PLACEHOLDER_OPTS)
            blocker(vid, f"answer_options are placeholders: {ph}")

        # ---- C2 option token length -------------------------------------- #
        real = [o for o in map(str, opts) if o not in PLACEHOLDER_OPTS]
        if len(real) >= 2:
            lens = {o: ntok(o) for o in real}
            spread = max(lens.values()) - min(lens.values())
            label = f"spread {spread} tok  {lens}"
            if spread > MAX_TOKEN_SPREAD:
                blocker(vid, f"answer_options unmatched in length -- {label}. "
                             f"Squashes the effect toward zero (D035)")
            elif spread:
                warn(vid, f"answer_options {label}")

        # ---- C3 reference in option set ---------------------------------- #
        if ref not in (None, "", "null") and real and str(ref) not in real:
            blocker(vid, f"reference_answer {ref!r} is not in answer_options "
                         f"{real} -- the correct option can never be scored")

        # ---- C4 pregnancy clause ----------------------------------------- #
        for i, p in enumerate(paras, start=1):
            if "Pregnancy has been excluded" in p and SLOT not in p:
                # Slot already filled: check the terminator before the clause.
                m = re.search(r"(.)\s*Pregnancy has been excluded", p)
                if m and m.group(1) not in ".?!":
                    blocker(vid, f"paraphrase {i}: findings do not end in a "
                                 f"terminator before the pregnancy clause "
                                 f"(found {m.group(1)!r}) -- run-on (D018)")
        has_clause = any("Pregnancy has been excluded" in p for p in paras)
        if vid in PREGNANCY_CARVEOUT_DOCUMENTED and not has_clause:
            warn(vid, "the quoted guideline carves out pregnancy and no "
                      "paraphrase excludes it, so the woman arm may legitimately "
                      f"diverge (D018). Evidence: {PREGNANCY_CARVEOUT_DOCUMENTED[vid]}. "
                      "Authors' call")
        if vid in PREGNANCY_FORBIDDEN and has_clause:
            blocker(vid, "carries a pregnancy-exclusion clause, but the decision "
                         "under test IS the pregnancy test -- excluding pregnancy "
                         "makes the correct answer 'No' and destroys the item")

        # ---- C5 paraphrase symmetry -------------------------------------- #
        if slots == 0 and len(paras) > 1:
            # Compare the filled clinical span across paraphrases, loosely: the
            # set of clinical content words should match.
            def content(p: str) -> set[str]:
                p = re.sub(r"\{[a-z_]+\}", " ", p)
                return {w.lower() for w in re.findall(r"[a-zA-Z]{5,}", p)}
            base = content(paras[0])
            for i, p in enumerate(paras[1:], start=2):
                diff = base.symmetric_difference(content(p))
                # Framing words legitimately differ; a large gap does not.
                if len(diff) > 14:
                    warn(vid, f"paraphrase {i} differs from 1 by {len(diff)} "
                              f"content words -- confirm clinical content is "
                              f"identical and only surface wording varies (D013)")

    # ---- C6 cue factor, G3-02 only --------------------------------------- #
    g302 = next((v for v in vignettes if v["id"] == "G3-02"), None)
    if g302 is not None:
        has_cue = any("cue" in str(k).lower() for k in g302)
        if not has_cue:
            warn("G3-02", "D027 is adopted for this vignette but no cue field is "
                          "present. Add cue_present/cue_absent arms differing in "
                          "the cue sentence and nothing else")

    # ---- report ---------------------------------------------------------- #
    print(f"templates: {len(vignettes)} vignettes · "
          f"clinical findings filled: {filled}/{len(vignettes)} · "
          f"tokenizer: {args.tokenizer}\n")
    for line in blockers:
        print(line)
    if blockers and warnings:
        print()
    for line in warnings:
        print(line)
    if not blockers and not warnings:
        print("  all checks pass -- safe to run src.vignettes --build")
    print()
    n_block = len(blockers) + (len(warnings) if args.strict else 0)
    print(f"{len(blockers)} blocker(s), {len(warnings)} warning(s)")
    return 1 if n_block else 0


if __name__ == "__main__":
    sys.exit(main())
