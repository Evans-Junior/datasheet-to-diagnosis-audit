"""Generate docs/vignettes_compendium.md: all live vignettes in one document.

WHY GENERATED AND NOT WRITTEN
-----------------------------
A hand-maintained appendix listing the stimulus set is a derived artefact, and
this project has five logged entries (D086, D087, D090, D092 and this one) about
derived artefacts drifting from their source in silence. The compendium is built
from `data/vignettes/templates.yaml` and the first-hand guideline quotes in
`docs/vignette_sources.md`, so it cannot describe a vignette the instrument is
not actually running.

It also stamps the prompt-set hash, so a reader can tell whether the appendix
and the results tables describe the same study.

Usage:
    .venv/bin/python scripts/build_vignette_compendium.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEMPLATES = ROOT / "data/vignettes/templates.yaml"
SOURCES = ROOT / "docs/vignette_sources.md"
OUT = ROOT / "docs/vignettes_compendium.md"

GROUPS = {
    1: ("Group 1: Sex-neutral conditions",
        "The guideline specifies no sex- or gender-dependent difference. **Carries "
        "H3**: a gap here would be the instrument responding to the descriptor, "
        "not to clinical content."),
    2: ("Group 2: Sex-specific, SPCU-dependent",
        "The correct answer genuinely differs with the Sex Parameter for Clinical "
        "Use. **This is the positive control.** A model that cannot move here "
        "cannot be read anywhere else, because a null and a broken instrument "
        "look identical."),
    3: ("Group 3: Historically biased conditions",
        "Conditions with documented sex or gender disparities in human care. "
        "**Carries H1 and H2.**"),
    4: ("Group 4: Noise baseline",
        "Clinically unambiguous items with no sex- or gender-relevant content. "
        "**Builds the nuisance floor** that every delta is judged against, "
        "stratified by option count."),
}


def source_sections() -> dict[str, str]:
    """Map vignette id -> its first-hand guideline quote block."""
    if not SOURCES.exists():
        return {}
    text = SOURCES.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    # Headings look like "### G4-03b: Acute pharyngitis ...  ✅ COMPLETE".
    # Keyed on the longest id first so "G2-01b" never matches as "G2-01".
    parts = re.split(r"^### ", text, flags=re.M)[1:]
    for part in parts:
        head = part.split("\n", 1)[0]
        m = re.match(r"(G\d-\d+[a-z]?)", head.strip())
        if not m:
            continue
        vid = m.group(1)
        # A retired section must not overwrite the live one for the same id.
        if "RETIRED SECTION" in head and vid in out:
            continue
        out.setdefault(vid, "")
        quotes = re.findall(r"^> ?(.*)$", part, flags=re.M)
        quotes = [q.strip() for q in quotes if q.strip()]
        if quotes:
            out[vid] = "\n".join(f"> {q}" for q in quotes[:6])
    return out


def main() -> int:
    tpls = yaml.safe_load(TEMPLATES.read_text(encoding="utf-8"))
    quotes = source_sections()

    live = [t for t in tpls if not (t.get("blocked_on") or "").strip()]
    out_rows = [t for t in tpls if (t.get("blocked_on") or "").strip()]

    try:
        import pandas as pd
        from src.vignettes import prompt_set_hash
        v = pd.read_csv(ROOT / "data/vignettes/vignettes.csv")
        v = v[v["blocked_on"].fillna("").astype(str).str.strip() == ""]
        v = v[v["analysis_ready"] == True]            # noqa: E712
        phash, nprompts = prompt_set_hash(v), len(v)
    except Exception as exc:                          # noqa: BLE001
        phash, nprompts = f"unavailable ({type(exc).__name__})", "?"

    L: list[str] = []
    L.append("# The stimulus set: every vignette in the study")
    L.append("")
    L.append("**Generated** by `scripts/build_vignette_compendium.py` from "
             "`data/vignettes/templates.yaml` and the first-hand guideline "
             "quotes in `docs/vignette_sources.md`. Do not edit by hand. "
             "edit the template and rebuild, or the next rebuild discards it.")
    L.append("")
    L.append(f"- **Live vignettes:** {len(live)}")
    L.append(f"- **Analysis-ready prompts:** {nprompts}  "
             f"(`prompt_set_hash` = `{phash}`)")
    L.append(f"- **Excluded rows:** {len(out_rows)} "
             f"({', '.join(t['id'] for t in out_rows)})")
    L.append("")
    L.append("## How to read an entry")
    L.append("")
    L.append("Each vignette is a **template**, not a prompt. It expands to **24 "
             "arms**: 2 values of the Sex Parameter for Clinical Use × 4 gender "
             "identities (man, woman, non-binary, blinded) × 3 paraphrases. The "
             "clinical text is byte-identical across every arm of a vignette; "
             "only the patient descriptor changes. `G3-02` expands to 48 because "
             "it carries a crossed psychologizing cue.")
    L.append("")
    L.append("The **reference answer** is the option the quoted guideline forces. "
             "The **target option** is the option whose probability mass is the "
             "second outcome measure (O2), it is not always the correct one, "
             "and for Group 3 it is deliberately the over- or under-treatment "
             "choice.")
    L.append("")
    L.append("**Verification status is per-row and shown on every entry.** "
             "`author_reviewed_against_quoted_guideline` is tier 1: the author "
             "checked the vignette against the guideline sentence quoted for it. "
             "It is not clinician verification (tier 2). See "
             "`docs/preregistration.md` §10.")
    L.append("")

    for g in sorted(GROUPS):
        rows = [t for t in live if t.get("group") == g]
        if not rows:
            continue
        title, blurb = GROUPS[g]
        L.append("---")
        L.append("")
        L.append(f"## {title}")
        L.append("")
        L.append(blurb)
        L.append("")
        L.append(f"**{len(rows)} live item(s):** "
                 f"{', '.join('`' + t['id'] + '`' for t in rows)}")
        L.append("")
        for t in rows:
            vid = t["id"]
            L.append(f"### {vid}: {t.get('condition', '(no condition)')}")
            L.append("")
            opts = [str(o) for o in (t.get("answer_options") or [])]
            by_spcu = t.get("reference_answer_by_spcu") or {}
            ref = (" / ".join(f"**{k}** → {a}" for k, a in by_spcu.items())
                   if by_spcu else f"{t.get('reference_answer')}")
            L.append(f"| | |")
            L.append(f"|---|---|")
            L.append(f"| **Question** | {t.get('question', '')} |")
            L.append(f"| **Options** | {' · '.join(opts)} |")
            L.append(f"| **Reference answer** | {ref} |")
            L.append(f"| **Target option (O2)** | {t.get('target_option', 'n/a')} |")
            L.append(f"| **Decision type** | `{t.get('decision_type', 'n/a')}` |")
            L.append(f"| **Patient age** | {t.get('age', 'n/a')} |")
            L.append(f"| **Verification** | `{t.get('verification', 'n/a')}` |")
            L.append(f"| **Arms** | {48 if t.get('cue_arms') else 24} |")
            L.append("")
            paras = t.get("paraphrases") or []
            if paras:
                L.append("**Clinical text (paraphrase 1 of "
                         f"{len(paras)}, slots unfilled):**")
                L.append("")
                L.append("```text")
                L.append(str(paras[0]).strip())
                L.append("```")
                L.append("")
            q = quotes.get(vid)
            if q:
                L.append("**Governing guideline, quoted at first hand:**")
                L.append("")
                L.append(q)
                L.append("")
            else:
                L.append("**Governing guideline:** see "
                         "`docs/vignette_sources.md`. No quote block parsed "
                         "for this id, which is itself worth checking.")
                L.append("")
            note = (t.get("note") or "").strip()
            if note:
                first = note.split("\n\n")[0].replace("\n", " ").strip()
                L.append(f"**Design note.** {first}")
                L.append("")

    if out_rows:
        L.append("---")
        L.append("")
        L.append("## Excluded rows, and why")
        L.append("")
        L.append("These are kept in the repository rather than deleted, so the "
                 "exclusions are auditable and the review's hit rate is "
                 "measurable. None of them scores anything.")
        L.append("")
        for t in out_rows:
            vid = t["id"]
            kind = ("RETIRED AS SUPERSEDED"
                    if t.get("verification") == "retired_superseded"
                    else "REJECTED ON CLINICAL REVIEW")
            L.append(f"### {vid}: {t.get('condition', '')}  ·  **{kind}**")
            L.append("")
            reason = (t.get("blocked_on") or "").strip()
            for para in reason.split("\n\n"):
                para = " ".join(para.split())
                if para:
                    L.append(para)
                    L.append("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  "
          f"({len(live)} live, {len(out_rows)} excluded, "
          f"{len('\n'.join(L).splitlines())} lines)")
    missing = [t["id"] for t in live if not quotes.get(t["id"])]
    if missing:
        print(f"  NOTE: no guideline quote parsed for: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
