"""Instrument validation for the Phase 2 scorer (RQ0).

Runs BEFORE any clinical content exists, and answers a question that is logically
prior to every hypothesis: can this measurement apparatus detect an effect that is
really there, and does it report nothing when there is nothing to report?

Four tests. None of them asserts a clinical fact -- the stimuli are deliberately
administrative (letter codes, colours) so that nothing here can be mistaken for,
or leak into, the authored vignettes. Per AI_USE.md clinical content is the
authors' own; this file tests the apparatus, not the medicine.

  T1 determinism      Score the same prompt twice. Delta must be exactly 0.
                      Catches nondeterminism, MPS kernel variance, cache bugs.
  T2 signal recovery  State the answer inside the prompt. The named option must
                      win. An instrument that misses an effect written in the
                      prompt in plain words cannot be trusted to find a subtle
                      one. This is the positive control the design lacked.
  T3 nuisance floor   Matched pairs differing ONLY by the gender token, with no
                      clinical content at all. Gives the magnitude of Delta
                      attributable to the token itself. NOT a null test: a real
                      model does differ here. It is the floor a clinical effect
                      must clear to mean anything.
  T4 score-key choice Options built to differ in token length and corpus
                      frequency. Shows which of sum/mean/pmi survives. Tests the
                      default (pmi) empirically instead of by assertion.

Deliberately imports option_logprob and fp32_head from src.score_outputs rather
than reimplementing them. A validation harness that reimplements the thing it
validates proves only that two of our functions agree.

Usage:
    .venv/bin/python -m scripts.validate_instrument
    .venv/bin/python -m scripts.validate_instrument --model EleutherAI/pythia-160m
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.score_outputs import (NEUTRAL_CONTEXT, PROMPT_FMT, fp32_head,
                               option_logprob, set_seeds)

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "results/tables/rq0_instrument_validation.json"
OUT_CSV = ROOT / "results/tables/rq0_instrument_validation.csv"

# Administrative, not clinical. "Record" framing keeps the stimuli recognisably
# synthetic so they cannot be confused with a vignette.
QUESTION = "Which code should be assigned?"
OPTIONS = ["Code A", "Code B", "Code C", "Code D"]

GENDERS = {"female": "the woman", "male": "the man"}


def score_prompt(model, tok, text: str, question: str, options: list[str],
                 device: str, head, baseline: dict) -> pd.DataFrame:
    """One prompt, every option, all three score keys. Real code path."""
    context = PROMPT_FMT.format(prompt_text=text, question=question)
    neutral = NEUTRAL_CONTEXT.format(question=question)
    rows = []
    for opt in options:
        total, n_tok = option_logprob(model, tok, context, opt, device, head)
        bkey = (question, opt)
        if bkey not in baseline:
            baseline[bkey], _ = option_logprob(model, tok, neutral, opt,
                                               device, head)
        rows.append({"option": opt, "sum_logprob": total,
                     "mean_logprob": total / n_tok if n_tok else float("nan"),
                     "pmi": total - baseline[bkey], "n_option_tokens": n_tok})
    df = pd.DataFrame(rows)
    for key in ("sum_logprob", "mean_logprob", "pmi"):
        v = df[key].to_numpy(dtype=float)
        p = np.exp(v - np.nanmax(v))
        df[f"norm_prob__{key}"] = p / np.nansum(p)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="EleutherAI/pythia-70m")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=20251027)
    args = ap.parse_args()

    set_seeds(args.seed)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=getattr(torch, args.dtype))
    model.to(device).eval()
    head = fp32_head(model)
    baseline: dict = {}
    report: dict = {"model": args.model, "dtype": args.dtype,
                    "device": device, "seed": args.seed,
                    "question": QUESTION, "options": OPTIONS, "tests": {}}
    records = []

    def run(text, tag, **meta):
        df = score_prompt(model, tok, text, QUESTION, OPTIONS, device, head,
                          baseline)
        df["test"] = tag
        for k, v in meta.items():
            df[k] = v
        records.append(df)
        return df

    # ---- T1 determinism -------------------------------------------------- #
    base_text = "Record 4417 is open for review. The patient is the patient."
    a = run(base_text, "T1_determinism", rep=1)
    b = run(base_text, "T1_determinism", rep=2)
    drift = float(np.abs(a["pmi"].to_numpy() - b["pmi"].to_numpy()).max())
    report["tests"]["T1_determinism"] = {
        "max_abs_pmi_drift": drift,
        "pass": bool(drift == 0.0),
        "interpretation": (
            "Identical input scored twice must give bitwise-identical scores. "
            "Any drift means the measured gender gap is confounded with run-to-run "
            "noise and every Delta needs a repeat-measurement error bar."),
    }

    # ---- T2 signal recovery (positive control) --------------------------- #
    t2 = {}
    for target in ("Code A", "Code C"):
        text = (f"Record 4417 is open for review. The applicable rule states "
                f"that {target} is the correct code for this record.")
        df = run(text, "T2_signal_recovery", target=target)
        for key in ("sum_logprob", "mean_logprob", "pmi"):
            col = f"norm_prob__{key}"
            win = df.loc[df[col].idxmax(), "option"]
            t2.setdefault(key, []).append({
                "stated": target, "argmax": win, "recovered": bool(win == target),
                "p_stated": float(df.loc[df["option"] == target, col].iloc[0]),
            })
    report["tests"]["T2_signal_recovery"] = {
        "by_score_key": t2,
        "pass": bool(all(r["recovered"] for r in t2["pmi"])),
        "interpretation": (
            "The prompt names the correct option in plain words. If the scorer "
            "cannot recover that, it cannot recover a subtle clinical effect, and "
            "a null result in Phase 2 would be uninterpretable -- indistinguishable "
            "from a broken instrument. This is the positive control for the "
            "apparatus, distinct from the Group 2 positive control for the models."),
    }

    # ---- T3 nuisance floor ----------------------------------------------- #
    floor = {}
    for i, frame in enumerate((
        "Record 4417 is open for review. The applicant is {g}.",
        "A file was submitted for assessment. {g} attended the appointment.",
        "The reviewer met {g} to complete the form.",
    ), start=1):
        per = {}
        for gid, gtok in GENDERS.items():
            per[gid] = run(frame.format(g=gtok), "T3_nuisance_floor",
                           frame=i, gender_identity=gid)
        for key in ("sum_logprob", "mean_logprob", "pmi"):
            col = f"norm_prob__{key}"
            d = per["female"][col].to_numpy() - per["male"][col].to_numpy()
            floor.setdefault(key, []).append(float(np.abs(d).max()))
    report["tests"]["T3_nuisance_floor"] = {
        "max_abs_delta_norm_prob_by_key": {k: v for k, v in floor.items()},
        "pmi_floor_max": float(max(floor["pmi"])),
        "pmi_floor_mean": float(np.mean(floor["pmi"])),
        "interpretation": (
            "Delta on content-free prompts that differ only by the gender token. "
            "This is NOT a null -- a real model does differ here, and that "
            "difference is the nuisance floor. A Phase 2 effect smaller than this "
            "floor is not evidence of clinical bias; it is the gender token moving "
            "the distribution with no clinical content present. Report the floor "
            "beside every Delta."),
    }

    # ---- T4 score-key robustness ----------------------------------------- #
    # Same meaning, very different token length and surface frequency.
    long_opts = ["Code A", "the code designated as A in the schedule",
                 "Code B", "the code designated as B in the schedule"]
    df4 = score_prompt(model, tok, base_text, QUESTION, long_opts, device, head,
                       baseline)
    df4["test"] = "T4_score_key"
    records.append(df4)
    spread = {}
    for key in ("sum_logprob", "mean_logprob", "pmi"):
        col = f"norm_prob__{key}"
        short = df4[df4["n_option_tokens"] <= 3][col].sum()
        spread[key] = {"p_mass_on_short_options": float(short),
                       "argmax": df4.loc[df4[col].idxmax(), "option"]}
    report["tests"]["T4_score_key"] = {
        "by_score_key": spread,
        "interpretation": (
            "Options matched in meaning but not in length. p_mass_on_short_options "
            "near 1.0 means that score key is reading length, not preference. "
            "sum_logprob is expected to fail hardest; this is the empirical "
            "justification for the pmi default rather than an assertion."),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2))
    pd.concat(records, ignore_index=True).to_csv(OUT_CSV, index=False)

    print(json.dumps({k: {kk: vv for kk, vv in v.items()
                          if kk != "interpretation"}
                      for k, v in report["tests"].items()}, indent=2))
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_CSV}")


if __name__ == "__main__":
    main()
