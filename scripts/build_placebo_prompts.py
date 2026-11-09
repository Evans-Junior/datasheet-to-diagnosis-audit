"""Validation A: build the placebo-perturbation prompt set (D062).

Emits a SEPARATE prompt file in the same schema as data/vignettes/vignettes.csv,
so the main 576-prompt audit set is left untouched and the two can never be
pooled by accident. Score it with:

    .venv/bin/python -m src.score_outputs --prompts data/vignettes/placebo_prompts.csv

The placebo delta is taken BETWEEN TWO LEVELS OF ONE ATTRIBUTE, holding vignette,
paraphrase, SPCU and arm fixed. Everything else about the prompt is byte
identical, exactly as in the gender counterfactual -- the only difference is
which inert word is swapped.

See configs/placebo_arms.yaml for the admissibility conditions each attribute
has to meet and the nine attributes rejected for failing them.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.vignettes import FIELDS, CLINICAL_SLOT, _fix_caps, load  # noqa: E402

CFG = ROOT / "configs/placebo_arms.yaml"
OUT = ROOT / "data/vignettes/placebo_prompts.csv"


def main() -> None:
    templates, arms = load()
    cfg = yaml.safe_load(CFG.read_text())
    scope = cfg["scope"]
    attrs = cfg["placebo_attributes"]

    gid = next(g for g in arms["gender_identities"] if g["key"] == scope["arm"])
    spcus = [s for s in arms["spcu_values"] if s["key"] in scope["spcu"]]
    exclude = set(scope.get("vignettes_exclude") or [])

    rows = []
    blocked_skipped = []
    for tpl in templates:
        if tpl["group"] not in scope["groups"] or tpl["id"] in exclude:
            continue
        # A REJECTED vignette must not appear in the placebo set. Selection
        # here is by group plus an explicit exclude list, so a row the clinical
        # review threw out stayed in: G4-03 was rejected under D082 and excluded
        # from scoring, and still contributed 18 placebo prompts. These measure
        # surface-form sensitivity on "the same vignettes whose gender effects
        # are being reported" -- the claim this file's own banner makes -- so
        # including a vignette that is NOT being reported falsifies that claim.
        # (The nuisance floor is a separate statistic, built from scored Group 4
        # rows by scripts/matched_floor.py; see D087.) 2026-11-08, D086.
        if (tpl.get("blocked_on") or "").strip():
            blocked_skipped.append(tpl["id"])
            continue
        for p_i, para in enumerate(tpl.get("paraphrases") or [], start=1):
            for spcu in spcus:
                base = para.format(
                    label=gid["label"], subject=gid["subject"],
                    object=gid["object"], possessive=gid["possessive"],
                    reflexive=gid.get("reflexive", gid["object"]),
                    spcu_statement=spcu["statement"], age=tpl["age"],
                    be=gid["be"], present_v=gid["present_v"],
                    report_v=gid["report_v"], attend_v=gid["attend_v"],
                )
                base = _fix_caps(base)
                if CLINICAL_SLOT in base:
                    continue      # clinical findings not yet written
                ref = (tpl.get("reference_answer_by_spcu") or {}).get(spcu["key"]) \
                    if tpl.get("reference_answer_by_spcu") else tpl.get("reference_answer")
                if ref is None:
                    continue

                for attr in attrs:
                    for lvl in attr["levels"]:
                        # Appended at the end, the same position the D027 cue
                        # uses, so the placebo and the cue are mechanically
                        # identical interventions and differ only in content.
                        text = base.rstrip() + " " + lvl["sentence"]
                        rows.append({
                            "prompt_id": (f"{tpl['id']}_p{p_i}_{spcu['key']}_"
                                          f"{scope['arm']}_{attr['key']}_{lvl['key']}"),
                            "vignette_id": tpl["id"], "group": tpl["group"],
                            "condition": tpl["condition"],
                            "guideline_ref": tpl.get("guideline_ref"),
                            "paraphrase": p_i, "spcu": spcu["key"],
                            "gender_identity": scope["arm"],
                            # arm_type marks these so no statistics module can
                            # ever pool them with the gendered arms.
                            "arm_type": f"placebo:{attr['key']}:{lvl['key']}",
                            "cue": "cue_absent", "age": tpl["age"],
                            "prompt_text": text, "question": tpl.get("question"),
                            "answer_options": "|".join(tpl.get("answer_options") or []),
                            "reference_answer": ref,
                            "target_option": tpl.get("target_option"),
                            "tier": tpl.get("tier"),
                            "verification": tpl.get("verification", "unverified"),
                            "analysis_ready": True, "blocked_on": "",
                        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    vigs = sorted({r["vignette_id"] for r in rows})
    print(f"placebo prompts written : {len(rows)}  -> {OUT.relative_to(ROOT)}")
    print(f"vignettes               : {len(vigs)}  {', '.join(vigs)}")
    if blocked_skipped:
        print(f"REJECTED, kept out of the placebo set : "
              f"{', '.join(sorted(blocked_skipped))}  (D086)")
    print(f"attributes              : {len(attrs)} x 2 levels")
    print(f"arm / spcu              : {scope['arm']} / {','.join(scope['spcu'])}")
    per_attr = len(rows) // (len(attrs) * 2)
    print(f"matched placebo pairs   : {per_attr * len(attrs)} "
          f"({per_attr} per attribute)")
    print("\nEach pair differs by exactly one inert word. Any movement is\n"
          "surface-form sensitivity, measured on the same vignettes whose\n"
          "gender effects are being reported.")


if __name__ == "__main__":
    main()
