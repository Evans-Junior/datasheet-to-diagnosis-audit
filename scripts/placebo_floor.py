"""D062: the placebo floor -- the right stimulus with the wrong manipulation.

    Group 4 floor   right manipulation, wrong stimulus  (flip sex, other vignette)
    placebo floor   right stimulus, wrong manipulation  (same vignette, inert swap)

An effect that clears the Group 4 floor but not the placebo floor is surface-token
sensitivity that happens to be carried by the gender word, not a gender effect.
Only a perturbation on the SAME vignette separates those, so an effect must clear
BOTH floors.

The statistic is identical to `scripts/matched_floor.py`: the signed shift of
probability mass on the target option, averaged within a vignette, then taken at
its worst vignette, stratified by option count. The ONLY difference is what is
flipped -- an inert attribute instead of the sex parameter -- which is the whole
point. Reusing the aggregation is what makes the two numbers comparable.

AGGREGATION IS MAX, and that was decided before the numbers were seen rather than
after (author decision, 2026-11-17). Max is the project's convention everywhere
else a floor is taken: `matched_floor.floor_max_abs_vignette` is the worst single
vignette, and the gate compares against it. Mean would have produced a friendlier
verdict here, which is precisely why switching to it after seeing max would be the
post-hoc choice the decision log exists to prevent. The mean is written to the
table beside the max so the sensitivity is visible rather than argued about.

HEADLINE USES TWO ATTRIBUTES, NOT THREE. D062 adopted eye colour, shirt colour and
appointment slot, and flagged the third as the weakest: "booked for the morning"
implies a non-urgent pathway, which can interact with the acute presentations in
G3-01 and G3-02, so it is not clinically inert in the way the rule requires. The
headline floor is therefore the max over the two patient-descriptive attributes,
and appointment slot is reported separately because its DISAGREEMENT with the
other two is itself the finding.

Writes:
  results/tables/i4_placebo_floor.csv      per model, attribute, option count
  results/tables/i4_placebo_regate.csv     the Group 2 gate against both floors
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.provenance import write_table          # noqa: E402
from src.vignettes import prompt_set_hash       # noqa: E402

RAW = ROOT / "results/raw_placebo"
PROMPTS = ROOT / "data/vignettes/placebo_prompts.csv"
N_BOOT = 10_000
SEED = 20260103

# D062's admissibility rule, condition 1: clinically inert. Appointment slot is
# admitted to the set but held out of the headline; see the module docstring.
PATIENT_DESCRIPTIVE = ("eye_colour", "shirt_colour")


def load() -> pd.DataFrame:
    files = sorted(RAW.glob("*.parquet"))
    if not files:
        sys.exit(f"no scored placebo runs in {RAW}")
    raw = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    # arm_type lives in the prompt table, not the scored rows, so the attribute
    # and level are joined back rather than parsed out of prompt_id. Parsing the
    # id would break silently the first time an attribute name contains the
    # separator, and "appointment_slot" already contains one.
    arms = pd.read_csv(PROMPTS)[["prompt_id", "arm_type"]]
    raw = raw.merge(arms, on="prompt_id", how="left", validate="many_to_one")
    if raw["arm_type"].isna().any():
        sys.exit("some scored placebo rows have no arm_type; prompt set changed?")

    parts = raw["arm_type"].str.split(":", expand=True)
    if parts.shape[1] != 3 or not (parts[0] == "placebo").all():
        sys.exit("arm_type is not placebo:<attribute>:<level> on every row")
    raw["attribute"], raw["level"] = parts[1], parts[2]
    return raw


def deltas_for(d: pd.DataFrame) -> pd.DataFrame:
    """Signed shift on the target option between the two levels of one attribute.

    Mirrors matched_floor.target_deltas. The gender arm is 'blinded' on every
    placebo row by construction, so no gender term is present at all and whatever
    moves is pure surface-form sensitivity.
    """
    d = d[d["option"].astype(str).str.strip()
          == d["target_option"].astype(str).str.strip()].copy()
    keys = ["model_id", "revision", "vignette_id", "group", "paraphrase",
            "attribute"]
    wide = d.pivot_table(index=keys, columns="level", values="norm_prob",
                         aggfunc="first").reset_index()
    out = []
    for attr, g in wide.groupby("attribute"):
        levels = [c for c in g.columns
                  if c not in keys and g[c].notna().any()]
        if len(levels) != 2:
            sys.exit(f"{attr}: expected 2 levels, found {levels}")
        a, b = sorted(levels)
        gg = g[keys].copy()
        gg["delta"] = g[a].to_numpy() - g[b].to_numpy()
        gg["contrast"] = f"{a} - {b}"
        out.append(gg)
    return pd.concat(out, ignore_index=True)


def floor_for(d: pd.DataFrame, rng: np.random.Generator) -> dict:
    by_vig = d.groupby("vignette_id")["delta"].mean()
    vigs = by_vig.index.to_numpy()
    if len(vigs) == 0:
        return {}
    boot = np.array([np.abs(by_vig.loc[rng.choice(vigs, len(vigs))].mean())
                     for _ in range(N_BOOT)])
    return {
        "n_vignettes": int(len(vigs)),
        "n_items": int(len(d)),
        "floor_max_abs_vignette": float(np.abs(by_vig).max()),
        "floor_mean_abs_vignette": float(np.abs(by_vig).mean()),
        "floor_boot_q95": float(np.quantile(boot, 0.95)),
        "worst_vignette": str(np.abs(by_vig).idxmax()),
        "per_vignette": "; ".join(f"{v}={m:+.4f}" for v, m in by_vig.items()),
    }


def main() -> int:
    raw = load()
    want = prompt_set_hash(pd.read_csv(PROMPTS))
    stamped = set(raw["prompt_hash"].dropna().unique())
    if stamped != {want}:
        sys.exit(f"placebo rows stamped {stamped}, current set is {want}. "
                 f"Rescore before analysing.")

    nopt = raw.groupby("vignette_id")["option"].nunique().to_dict()
    dl = deltas_for(raw)
    dl["n_options"] = dl["vignette_id"].map(nopt)

    rows = []
    for (mid, rev, attr, grp, n_opt), g in dl.groupby(
            ["model_id", "revision", "attribute", "group", "n_options"]):
        rng = np.random.default_rng(SEED)
        f = floor_for(g, rng)
        if f:
            rows.append({"model_id": mid, "revision": rev, "attribute": attr,
                         "group": int(grp), "n_options": int(n_opt),
                         "in_headline": attr in PATIENT_DESCRIPTIVE,
                         "contrast": g["contrast"].iloc[0], **f})
    out = pd.DataFrame(rows).sort_values(
        ["group", "n_options", "model_id", "attribute"]).reset_index(drop=True)
    write_table(out, ROOT / "results/tables/i4_placebo_floor.csv")
    print(f"wrote results/tables/i4_placebo_floor.csv  ({len(out)} rows)")

    # ---- re-gate Group 2 against BOTH floors -------------------------------
    pc = pd.read_csv(ROOT / "results/tables/rq0_positive_control.csv")

    # THE FLOOR THAT GATES GROUP 2 IS MEASURED ON GROUP 2. The placebo exists to
    # supply the RIGHT stimulus with the wrong manipulation; taking the worst
    # binary vignette anywhere in the set would put a Group 3 or Group 4 stimulus
    # back under a Group 2 margin, which is the wrong-stimulus problem the Group 4
    # floor already has and the placebo was built to remove. The first version of
    # this script did exactly that and reported the gate falling to 0 of 10; the
    # difference is entirely stimulus mismatch, not evidence.
    g2 = out[(out["group"] == 2) & (out["n_options"] == 2)]
    if g2.empty:
        sys.exit("no Group 2 placebo rows; the placebo set must cover Group 2 "
                 "or it cannot gate the positive control")
    head = (g2[g2["in_headline"]]
            .groupby("model_id")["floor_max_abs_vignette"].max())
    head_mean = (g2[g2["in_headline"]]
                 .groupby("model_id")["floor_max_abs_vignette"].mean())
    allthree = g2.groupby("model_id")["floor_max_abs_vignette"].max()
    anybinary = (out[out["n_options"] == 2]
                 .groupby("model_id")["floor_max_abs_vignette"].max())

    pc = pc.copy()
    pc["placebo_floor_max"] = pc["model_id"].map(head)
    pc["placebo_floor_mean_of_attrs"] = pc["model_id"].map(head_mean)
    pc["placebo_floor_all3"] = pc["model_id"].map(allthree)
    pc["placebo_floor_any_binary_vignette"] = pc["model_id"].map(anybinary)
    pc["binding_floor"] = pc[["nuisance_floor", "placebo_floor_max"]].max(axis=1)
    pc["margin_over_both"] = pc["mean_margin"].abs() - pc["binding_floor"]
    pc["gate_both_floors"] = np.where(pc["margin_over_both"] > 0,
                                      "SENSITIVE", "INSENSITIVE")
    write_table(pc, ROOT / "results/tables/i4_placebo_regate.csv")
    print(f"wrote results/tables/i4_placebo_regate.csv")

    print("\n=== Group 2 gate, gender floor alone vs both floors ===")
    show = pc[["model_id", "mean_margin", "nuisance_floor", "placebo_floor_max",
               "binding_floor", "gate", "gate_both_floors"]]
    print(show.to_string(index=False, float_format=lambda x: f"{x:9.4f}"))
    was = int((pc["gate"] == "SENSITIVE").sum())
    now = int((pc["gate_both_floors"] == "SENSITIVE").sum())
    print(f"\n  gate: {was} of {len(pc)}  ->  {now} of {len(pc)} once the "
          f"placebo floor also has to be cleared")
    survivors = pc.loc[pc["gate_both_floors"] == "SENSITIVE", "model_id"].tolist()
    print(f"  survives both: {', '.join(survivors) or 'none'}")

    # ---- the comparison the placebo was built for: ONE stimulus, both ----
    # manipulations. The model-level gate above compares a MEAN margin against a
    # MAX floor, which is the project's existing convention but is asymmetric and
    # does most of the work in a borderline case. Per vignette there is no such
    # asymmetry: the same vignette's sex-parameter flip and its worst inert-
    # attribute swap, side by side.
    import re as _re

    def _per(s):
        return {k: float(v) for k, v in
                _re.findall(r"(G\d-\d\d\w*)=([+-][\d.]+)", str(s))}

    head_rows = out[(out["group"] == 2) & (out["in_headline"])]
    # A per-vignette ratio is only interpretable for a model that detects the sex
    # parameter AT ALL. A model that fails the positive control has gender deltas
    # that are instrument noise, so its ratio is noise over noise and sits near 1
    # by construction -- four Pythia models "clear" one vignette each at 1.0x to
    # 2.9x on exactly that basis. Carrying the flag on every row stops the column
    # being read as seven models partially passing.
    passes = dict(zip(pc["model_id"], pc["gate"] == "SENSITIVE"))
    pv = []
    for mid, g in pc.groupby("model_id"):
        gender = _per(g["per_vignette"].iloc[0])
        worst: dict[str, float] = {}
        for r in head_rows[head_rows["model_id"] == mid].itertuples():
            for v, x in _per(r.per_vignette).items():
                worst[v] = max(worst.get(v, 0.0), abs(x))
        for v, gval in sorted(gender.items()):
            pl = worst.get(v, float("nan"))
            pv.append({"model_id": mid, "vignette_id": v,
                       "gender_margin_abs": abs(gval),
                       "placebo_worst_abs": pl,
                       "ratio_gender_over_placebo": abs(gval) / pl if pl else float("nan"),
                       "clears_own_placebo": bool(abs(gval) > pl),
                       "model_detects_sex_parameter": bool(passes.get(mid, False)),
                       "interpretable": bool(passes.get(mid, False))})
    pv = pd.DataFrame(pv)
    write_table(pv, ROOT / "results/tables/i4_placebo_per_vignette.csv")
    print("wrote results/tables/i4_placebo_per_vignette.csv")

    print("\n=== same stimulus, both manipulations (Group 2) ===")
    print("  Only models that pass the gender gate are interpretable here; a model")
    print("  that fails it has noise in both terms and a ratio near 1 means nothing.")
    for interp in (True, False):
        sel = pv[pv["interpretable"] == interp]
        if sel.empty:
            continue
        print(f"\n  {'INTERPRETABLE' if interp else 'NOT INTERPRETABLE (fails the gender gate)'}")
        for mid, g in sel.groupby("model_id"):
            n = int(g["clears_own_placebo"].sum())
            best = g.loc[g["ratio_gender_over_placebo"].idxmax()]
            print(f"    {mid:<32} clears {n}/{len(g)}  "
                  f"best {best.vignette_id} at {best.ratio_gender_over_placebo:.1f}x")

    print("\n=== sensitivity: what the aggregation choice does ===")
    for label, col in (("max over the 2 descriptive attrs (REPORTED)", "placebo_floor_max"),
                       ("mean over the 2 descriptive attrs", "placebo_floor_mean_of_attrs"),
                       ("max over all 3, incl. appointment slot", "placebo_floor_all3"),
                       ("worst binary vignette ANYWHERE (wrong stimulus)",
                        "placebo_floor_any_binary_vignette")):
        n = int((pc["mean_margin"].abs()
                 - pc[["nuisance_floor", col]].max(axis=1) > 0).sum())
        print(f"  {label:<44} gate {n} of {len(pc)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
