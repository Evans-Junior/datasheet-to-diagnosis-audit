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
# D092: moved from G2-01, now retired as superseded. The carve-out belongs
# to whichever row is live, or the clause gets injected into the one item
# whose decision IS the pregnancy test.
PREGNANCY_FORBIDDEN = {"G2-01b"}

# Max acceptable token spread within an option set (D035).
MAX_TOKEN_SPREAD = 2

# Read from the arms config rather than hardcoded, so adding an SPCU value
# cannot silently leave a group-2 vignette with an unscorable arm.
def _spcu_keys() -> set[str]:
    import yaml as _y
    arms = _y.safe_load((ROOT / "configs/gender_arms.yaml").read_text())
    return {a["key"] for a in arms["spcu_values"]}


SPCU_KEYS = _spcu_keys()

# Provenance and review state, per AI_USE.md. Origin and verification are kept in
# one controlled vocabulary so that "a clinician approved it" can never be
# recorded in a way that also erases "an assistant drafted it" -- those are
# different facts and a reader is owed both. Only REPORTABLE values may support a
# reported result.
VERIFICATION_VALUES = {
    "unverified_ai_drafted",
    # AUTHOR review, which is NOT clinician review and is NOT reportable.
    # src/stats.py has recognised this value since D040 -- it maps to
    # PROVISIONAL__author_reviewed_not_clinician_validated -- but this
    # vocabulary was never updated, so the two modules disagreed: stats.py
    # accepted the label while this checker called every row carrying it a
    # blocker. Admitting it here closes that split. It stays out of REPORTABLE,
    # which is the whole point: an author checking a vignette against the
    # guideline they themselves quoted is a real step and still not a clinician.
    "author_reviewed_against_quoted_guideline",
    "ai_drafted_clinician_verified",
    "ai_drafted_clinician_corrected",
    "clinician_authored",
    "rejected",
    # D092: withdrawn for a DESIGN reason, not a clinical one. G2-01 passed
    # author review and was retired because G2-01b tests the same construct
    # from a better source; calling that "rejected" would misreport the review's
    # hit rate, which is evidence we rely on elsewhere (prereg S10).
    "retired_superseded",
}
REPORTABLE = {"ai_drafted_clinician_verified",
              "ai_drafted_clinician_corrected",
              "clinician_authored"}

blockers: list[str] = []
warnings: list[str] = []


def blocker(vid: str, msg: str) -> None:
    blockers.append(f"  [BLOCK] {vid}: {msg}")


def warn(vid: str, msg: str) -> None:
    warnings.append(f"  [WARN ] {vid}: {msg}")


# Sections of configs/models.yaml whose models SCORE answer options. Only these
# tokenizers can gate option length. `judge` is excluded on purpose: the judge
# never scores an option set (D006 keeps it disjoint), so its tokenization is
# irrelevant to D035 -- and including it raised a false blocker on G1-02, whose
# options are within the limit on every tokenizer that actually scores. `smoke`
# is excluded because it only re-lists an audited model.
SCORING_SECTIONS = ("audit", "contrast")


def _tokenizer_ids_from_models_yaml() -> list:
    """Every SCORING model id in configs/models.yaml, so a new model cannot
    enter the study with its tokenizer unchecked (D090)."""
    import yaml as _y
    cfg = _y.safe_load((ROOT / "configs/models.yaml").read_text())
    ids: list = []

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("id"), str) and "/" in node["id"]:
                ids.append(node["id"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    present = [k for k in SCORING_SECTIONS if k in cfg]
    missing = [k for k in SCORING_SECTIONS if k not in cfg]
    if missing:
        # Fail loudly rather than quietly checking fewer tokenizers than the
        # study scores with -- that is exactly how G4-10 slipped through.
        print(f"!! configs/models.yaml has no {', '.join(missing)} section(s); "
              f"option-length checking may be incomplete")
    for k in present:
        walk(cfg[k])
    # Preserve order, drop duplicates. Smallest first keeps the common case fast.
    return list(dict.fromkeys(ids))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default=None,
                    help="force a single tokenizer. Default: EVERY distinct "
                         "tokenizer in configs/models.yaml (D090)")
    ap.add_argument("--strict", action="store_true",
                    help="treat WARN as BLOCK")
    args = ap.parse_args()

    vignettes = yaml.safe_load(TEMPLATES.read_text())
    from transformers import AutoTokenizer

    # D090: the option-length limit MUST be checked against every tokenizer that
    # scores, not one representative. G4-10's option set was spread 2 tok under
    # pythia (a warning) and spread 4 tok under Qwen3 and OLMo-2 (a blocker),
    # because "corticosteroid" costs 3 pythia tokens and 6 on both 8B
    # tokenizers. Checking pythia only meant the limit was never enforced
    # against the three models whose nuisance floor that item sets -- and it
    # sets H3's equivalence margin. One tokenizer cannot stand in for another.
    tok_ids = ([args.tokenizer] if args.tokenizer
               else _tokenizer_ids_from_models_yaml())
    tokenizers, seen = {}, set()
    for tid in tok_ids:
        try:
            t = AutoTokenizer.from_pretrained(tid)
        except Exception as exc:                      # not cached / offline
            print(f"  (tokenizer unavailable, skipped: {tid} -- "
                  f"{type(exc).__name__})")
            continue
        # Dedupe by behaviour, not by name: the whole Pythia ladder shares one
        # tokenizer, so loading seven of them would say nothing new.
        sig = tuple(len(t(" " + w, add_special_tokens=False).input_ids)
                    for w in ("corticosteroid", "flucloxacillin", "Topical",
                              "immunocompetent", "lymphadenopathy"))
        sig = (t.vocab_size, sig)
        if sig in seen:
            continue
        seen.add(sig)
        tokenizers[tid] = t
    if not tokenizers:
        print("!! no tokenizer could be loaded -- option-length check SKIPPED")

    def ntok_all(s: str) -> dict:
        """Token length of one option under every distinct tokenizer."""
        txt = " " + str(s).strip()
        return {tid: len(t(txt, add_special_tokens=False).input_ids)
                for tid, t in tokenizers.items()}

    def ntok(s: str) -> int:
        """Worst-case (largest) length, kept for callers wanting one number."""
        per = ntok_all(s)
        return max(per.values()) if per else 0

    filled = 0
    for v in vignettes:
        vid = v["id"]
        paras = v.get("paraphrases") or []
        opts = v.get("answer_options") or []
        ref = v.get("reference_answer")
        # Group 2's correct answer tracks the SEX PARAMETER FOR CLINICAL USE,
        # not gender identity, so one scalar cannot express it: a pregnancy test
        # is indicated for SPCU female and not for SPCU male, and that
        # difference is the control, not a bias. Such a vignette carries
        # reference_answer_by_spcu instead, and both are checked.
        by_spcu = v.get("reference_answer_by_spcu")

        # ---- C1 unfilled ------------------------------------------------- #
        slots = sum(SLOT in p for p in paras)
        if slots:
            blocker(vid, f"{slots}/{len(paras)} paraphrases still contain {SLOT}")
        else:
            filled += 1
        if ref in (None, "", "null") and not by_spcu:
            blocker(vid, "reference_answer is null and no "
                         "reference_answer_by_spcu is given")
        if by_spcu:
            missing = SPCU_KEYS - set(by_spcu)
            if missing:
                blocker(vid, f"reference_answer_by_spcu is missing SPCU "
                             f"value(s) {sorted(missing)}: every arm must have "
                             f"a scorable answer")
            if ref not in (None, "", "null"):
                blocker(vid, "both reference_answer and "
                             "reference_answer_by_spcu are set -- ambiguous")
            if v.get("group") != 2:
                warn(vid, f"reference_answer_by_spcu on a group-{v.get('group')} "
                          f"vignette. Outside group 2 an SPCU-dependent answer "
                          f"means the item is not a bias test")
            if len(set(by_spcu.values())) == 1:
                warn(vid, "reference_answer_by_spcu gives the same answer for "
                          "every SPCU value, so it need not be SPCU-keyed")
        if set(map(str, opts)) & PLACEHOLDER_OPTS:
            ph = sorted(set(map(str, opts)) & PLACEHOLDER_OPTS)
            blocker(vid, f"answer_options are placeholders: {ph}")

        # ---- C2 option token length -------------------------------------- #
        real = [o for o in map(str, opts) if o not in PLACEHOLDER_OPTS]
        if len(real) >= 2 and tokenizers:
            # Per-tokenizer spread. The verdict is the WORST tokenizer, because
            # the item is scored under all of them (D090).
            per_tok = {}
            for tid in tokenizers:
                lens_t = {o: ntok_all(o)[tid] for o in real}
                per_tok[tid] = (max(lens_t.values()) - min(lens_t.values()),
                                lens_t)
            worst_tid = max(per_tok, key=lambda k: per_tok[k][0])
            spread, lens = per_tok[worst_tid]
            agree = len({v[0] for v in per_tok.values()}) == 1
            where = ("" if agree or len(per_tok) == 1
                     else f"  worst of {len(per_tok)} tokenizers: "
                          f"{worst_tid.split('/')[-1]}"
                          f" (others: "
                          f"{', '.join(f'{k.split(chr(47))[-1]}={v[0]}' for k, v in per_tok.items() if k != worst_tid)})")
            label = f"spread {spread} tok  {lens}{where}"
            if spread > MAX_TOKEN_SPREAD:
                blocker(vid, f"answer_options unmatched in length -- {label}. "
                             f"Squashes the effect toward zero (D035)")
            elif spread:
                warn(vid, f"answer_options {label}")

        # ---- C3 reference in option set ---------------------------------- #
        for who, cand in ([("reference_answer", ref)] if ref not in (None, "", "null")
                          else []) + [(f"reference_answer_by_spcu[{k}]", a)
                                      for k, a in (by_spcu or {}).items()]:
            if real and str(cand) not in real:
                blocker(vid, f"{who} {cand!r} is not in answer_options "
                             f"{real} -- the correct option can never be scored")

        # ---- C3b target_option (O2) --------------------------------------- #
        # O2 is the mass on the TARGET DIAGNOSIS option, which may differ from
        # the concordant answer -- G4-01 and G4-03 are exactly the cases where
        # the guideline says "no" and the target action is still "Yes". Without
        # this pointer RQ4 has no data path at all (D037).
        # ---- C3c verification vocabulary ---------------------------------- #
        ver = v.get("verification")
        if ver not in VERIFICATION_VALUES:
            blocker(vid, f"verification {ver!r} is not one of "
                         f"{sorted(VERIFICATION_VALUES)} (see AI_USE.md)")

        tgt = v.get("target_option")
        if tgt in (None, "", "null"):
            blocker(vid, "target_option is unset -- O2 and therefore H4/RQ4 "
                         "cannot be computed for this vignette (D037)")
        elif real and str(tgt) not in real:
            blocker(vid, f"target_option {tgt!r} is not in answer_options {real}")

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
          f"tokenizers checked: "
          f"{', '.join(t.split('/')[-1] for t in tokenizers) or 'NONE'}\n")
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

    # TEMPLATES-vs-CSV DRIFT. Everything downstream reads
    # data/vignettes/vignettes.csv, including the staleness stamp in
    # scripts/results_summary.py, which hashes THAT FILE. So editing
    # templates.yaml without running `src.vignettes --build` leaves every
    # staleness check passing while the study definition has already moved --
    # the exact failure the stamp exists to catch, invisible to the stamp.
    # Found 2026-11-08 when the G4-03b contradiction fix (D085) sat in
    # templates.yaml and in the review workbook, which reads templates directly,
    # while the scored prompts still carried the contradictory text and the
    # summary reported itself current. Printed every run, like the clinician
    # gate, and for the same reason: the moment everything looks clean is when
    # this is easiest to miss.
    csv_path = ROOT / "data/vignettes/vignettes.csv"
    if not csv_path.exists():
        print("PROMPT CSV MISSING -- run: .venv/bin/python -m src.vignettes --build")
    else:
        import csv as _csv
        # D090: compare EVERY field the hash covers, not prompt_text alone.
        # G4-10's answer_options were rewritten with its prompt_text untouched;
        # a prompt_text-only comparison called the stale CSV current, which is
        # the same defect the gate exists to catch.
        sys.path.insert(0, str(ROOT))
        from src.vignettes import (load as _load, expand as _expand,
                                   HASHED_FIELDS as _HF)

        # D092: blocked_on and analysis_ready are not hashed (they change which
        # prompts EXIST, not what any one prompt says) but a change to either
        # still makes the CSV stale. Retiring G2-01 edited only blocked_on, and
        # a signature over _HF alone called the stale CSV current.
        _DRIFT = tuple(_HF) + ("blocked_on", "analysis_ready")

        def _sig(row: dict) -> tuple:
            return tuple(str(row.get(f, "")).strip() for f in _DRIFT)

        with csv_path.open(encoding="utf-8") as fh:
            on_disk = {(r["vignette_id"], r["prompt_id"]): _sig(r)
                       for r in _csv.DictReader(fh)}
        # Expand from templates.yaml the same way src.vignettes does, so the
        # comparison is against what a rebuild WOULD write, not a proxy for it.
        _tpls, _arms = _load()
        from_templates = {(r["vignette_id"], r["prompt_id"]): _sig(r)
                          for tpl in _tpls for r in _expand(tpl, _arms)}
        changed = sorted({vid for k, txt in from_templates.items()
                          if (vid := k[0]) and on_disk.get(k) != txt})
        gone = sorted({k[0] for k in on_disk if k not in from_templates})
        added = sorted({k[0] for k in from_templates if k not in on_disk})
        drift = sorted(set(changed) | set(gone) | set(added))
        if drift:
            print(f"\n!! PROMPT CSV IS BEHIND templates.yaml for "
                  f"{len(drift)} vignette(s): {', '.join(drift)}")
            print("   Nothing downstream can see your edit, and the staleness "
                  "stamp hashes the CSV, so it will report the old prompts as "
                  "CURRENT. Run: .venv/bin/python -m src.vignettes --build")
            print(f"   (fields compared: {', '.join(_DRIFT)})")
            n_block += 1
        else:
            print("prompt CSV matches templates.yaml "
                  f"({len(from_templates)} prompts)")

    # The clinician gate, printed every run. "0 blockers" means the instrument
    # BUILDS; it does not mean anything built from it may be reported. Keeping
    # the two counts side by side is the whole point -- a clean validator run is
    # exactly the moment someone is most likely to forget the difference.
    vers = [v.get("verification") for v in vignettes]
    ok = sum(1 for x in vers if x in REPORTABLE)
    rej = sum(1 for x in vers if x == "rejected")
    ret = sum(1 for x in vers if x == "retired_superseded")
    print(f"clinician-verified: {ok}/{len(vers) - rej - ret} live rows reportable"
          + (f", {rej} rejected" if rej else "")
          + (f", {ret} retired as superseded" if ret else ""))
    # D092: a retired row is excluded from scoring exactly like a rejected one,
    # so it must come out of the denominator too. Leaving it in made the live
    # set look as though it still held an unreviewed vignette, which would drop
    # the whole run from tier 1 to tier 0 (D091) on a bookkeeping error.
    live = len(vers) - rej - ret
    if ok < live:
        # Split the non-reportable remainder. Calling an author-reviewed row
        # "AI-drafted and UNVERIFIED" understates the work done on it and makes
        # the one line a reader actually scans less accurate -- while lumping it
        # in with reportable rows would overstate it. Both counts, every run.
        auth = sum(1 for x in vers
                   if x == "author_reviewed_against_quoted_guideline")
        unver = live - ok - auth
        if auth:
            print(f"  {auth} vignette(s) are AUTHOR-REVIEWED against the quoted "
                  f"guideline. That is a real check and it is NOT clinician "
                  f"verification: still not reportable (AI_USE.md, D038).")
        if unver:
            print(f"  {unver} vignette(s) are AI-drafted and UNVERIFIED. They "
                  f"build and score, but no number computed from them may be "
                  f"reported as a finding (AI_USE.md, D038).")
    return 1 if n_block else 0


if __name__ == "__main__":
    sys.exit(main())
