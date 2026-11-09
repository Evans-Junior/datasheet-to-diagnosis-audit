"""Model-by-model bias summary: one row per model, for the results section.

Reads the per-RQ tables that src/stats.py writes and collapses them into the
single table a reader actually wants -- "which models showed a gender effect,
how big, and is it bigger than this instrument's own noise" -- plus a markdown
rendering for the paper and the deck.

It refuses to drop the provenance. Every row carries the verification_status it
inherited, and if any input row is PROVISIONAL the output is stamped
NOT REPORTABLE, because a summary table is exactly where a provisional number
would quietly become a finding.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.provenance import write_table   # D090

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
OUT_CSV = T / "summary_model_bias.csv"
OUT_MD = ROOT / "docs" / "results_model_bias.md"


def _read(name: str) -> pd.DataFrame | None:
    p = T / f"{name}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    return df if len(df) else None


def current_prompt_hash() -> tuple[str, int]:
    """The hash of the prompt set as it stands NOW, for staleness detection."""
    v = pd.read_csv(ROOT / "data/vignettes/vignettes.csv")
    if "blocked_on" in v.columns:
        v = v[v["blocked_on"].fillna("").astype(str).str.strip() == ""]
    v = v[v["analysis_ready"] == True]  # noqa: E712
    # D090: must be the SAME definition src.score_outputs stamps into the
    # manifest, so it is imported, never re-implemented here.
    sys.path.insert(0, str(ROOT))
    from src.vignettes import prompt_set_hash
    return prompt_set_hash(v), len(v)


def scored_prompt_hashes() -> set[str]:
    m = ROOT / "results" / "raw" / "manifest.json"
    if not m.exists():
        return set()
    d = json.loads(m.read_text())
    return {r.get("prompt_hash") for r in d.get("runs", []) if r.get("prompt_hash")}


def short(model_id: str) -> str:
    return str(model_id).split("/")[-1]


def build() -> tuple[pd.DataFrame, list[str]]:
    notes: list[str] = []
    gate = _read("rq0_positive_control")
    trend = _read("rq3_size_trend")
    deltas = _read("rq2_deltas")
    if gate is None and trend is None:
        print("No scored tables found. Run src.score_outputs then src.stats first.")
        raise SystemExit(1)

    base = trend if trend is not None else gate
    rows = []
    for _, r in base.iterrows():
        mid = r["model_id"]
        row: dict[str, object] = {
            "model": short(mid),
            "model_id": mid,
            "params_b": r.get("n_params_b"),
        }
        if trend is not None:
            tr = trend[trend["model_id"] == mid]
            if len(tr):
                tr = tr.iloc[0]
                row["mean_abs_delta"] = tr.get("mean_abs_delta")
                row["nuisance_floor"] = tr.get("nuisance_floor")
                row["floor_relative_gap"] = tr.get("floor_relative_gap")
                row["exceeds_floor"] = tr.get("exceeds_floor")
                row["null_is_interpretable"] = tr.get("null_is_interpretable")
        if gate is not None:
            g = gate[gate["model_id"] == mid]
            if len(g):
                g = g.iloc[0]
                row["gate"] = g.get("gate")
                row["gate_margin"] = g.get("mean_margin")
                row["gate_margin_over_floor"] = g.get("margin_over_floor")
        if deltas is not None:
            d = deltas[deltas["model_id"] == mid]
            if len(d) and "delta" in d.columns:
                row["n_pairs"] = len(d)
                row["mean_delta_signed"] = d["delta"].mean()
                # direction only means anything if the gate opened
                row["direction"] = (
                    "woman arm lower" if d["delta"].mean() < 0 else "woman arm higher"
                )
        vs = [c for c in ("verification_status",) if c in base.columns]
        row["verification_status"] = r.get(vs[0]) if vs else "unknown"
        rows.append(row)

    df = pd.DataFrame(rows)

    # ---- provenance gates --------------------------------------------------
    statuses = set(df["verification_status"].astype(str))
    if any(not st.startswith("REPORTABLE") for st in statuses):
        notes.append(
            "NOT REPORTABLE AT ANY TIER. At least one input row was never "
            f"reviewed against a first-hand guideline quote (statuses seen: "
            f"{sorted(statuses)}). Under D038/D043/D091 no number in this "
            "table may be cited as a finding."
        )
    elif any(st.startswith("REPORTABLE_TIER1") for st in statuses):
        # D091: tier 1 is reportable, and saying so without the condition
        # attached is exactly the overclaim the tiers exist to prevent.
        notes.append(
            "REPORTABLE — TIER 1, PENDING CLINICAL VALIDATION. Every vignette "
            "is author-reviewed against a quoted first-hand guideline, which is "
            "the bar fixed for the course submission (D091). These numbers may "
            "be presented as results provided 'pending clinical validation' "
            "travels with them. A public paper requires tier 2: clinician "
            "verification on every row. Clinical review is scheduled and will "
            "be reported whether or not it changes these values."
        )
    elif any(st.startswith("REPORTABLE_TIER2") for st in statuses):
        notes.append("REPORTABLE — TIER 2, clinician-verified on every row.")
    cur_hash, n_cur = current_prompt_hash()
    scored = scored_prompt_hashes()
    if scored and cur_hash not in scored:
        notes.append(
            f"STALE. These numbers were scored from a different prompt set. "
            f"Current prompt set: {n_cur} prompts, hash {cur_hash}. Hashes in "
            f"the scoring manifest: {sorted(scored)}. Rerun src.score_outputs "
            "before reading anything below as a property of the current "
            "instrument."
        )
    if not df.get("gate", pd.Series(dtype=object)).astype(str).eq("SENSITIVE").any():
        notes.append(
            "NO MODEL PASSED THE GATE in this run. The positive control is the "
            "precondition for interpreting any Group 1/3/4 number: a model that "
            "cannot show a sex-parameter effect where the guideline says one "
            "exists cannot be used to argue that an absence of gender effect is "
            "an absence of bias. Treat every delta below as uninterpretable."
        )
    return df, notes


def to_markdown(df: pd.DataFrame, notes: list[str]) -> str:
    cur_hash, n_cur = current_prompt_hash()
    out = ["# Model-by-model bias summary", ""]
    out.append("Generated by `scripts/results_summary.py`. Do not hand-edit.")
    out.append("")
    for n in notes:
        out.append(f"> **{n}**")
        out.append("")
    cols = [c for c in ("model", "params_b", "gate", "gate_margin",
                        "mean_abs_delta", "nuisance_floor", "exceeds_floor",
                        "direction", "n_pairs", "verification_status")
            if c in df.columns]
    hdr = {"model": "Model", "params_b": "Params (B)", "gate": "Gate",
           "gate_margin": "Gate margin", "mean_abs_delta": "Mean |Δ|",
           "nuisance_floor": "Noise floor", "exceeds_floor": "Above floor?",
           "direction": "Direction", "n_pairs": "Pairs",
           "verification_status": "Provenance"}
    out.append("| " + " | ".join(hdr[c] for c in cols) + " |")
    out.append("|" + "|".join("---" for _ in cols) + "|")
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, float):
                cells.append(f"{v:+.4f}" if c in ("gate_margin",
                                                  "mean_delta_signed") else f"{v:.4f}")
            else:
                cells.append("" if pd.isna(v) else str(v))
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    out.append(f"Current prompt set: **{n_cur} prompts**, hash `{cur_hash}`.")
    return "\n".join(out) + "\n"


def main() -> None:
    df, notes = build()
    write_table(df, OUT_CSV)        # D090: stamps prompt_hash
    OUT_MD.write_text(to_markdown(df, notes), encoding="utf-8")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}  ({len(df)} models)")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    for n in notes:
        print(f"  !! {n}")
    if notes:
        sys.exit(0)


if __name__ == "__main__":
    main()
