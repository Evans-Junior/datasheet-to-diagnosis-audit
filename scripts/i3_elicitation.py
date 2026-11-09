"""I3: elicitation variants for the Pythia family.

Pythia Group 2 target probabilities are 0.497-0.501 across all seven sizes:
exactly uniform over two options, i.e. the model is not treating the input as a
question. Pythia is a base LM with no instruction tuning, so the zero-shot
question-answer frame in `score_outputs.PROMPT_FMT` is the wrong harness.

Runs only the tuning strata (Group 2 and the binary Group 4 items), so Group 1
and Group 3 are untouched. See docs/instrument_tuning_log.md entry I3.

I3a (contextual calibration) is NOT run here: `score_outputs` already subtracts
a content-free baseline, logP(option | question, no patient), to form the `pmi`
score key. That is Zhao et al.'s correction with a better-specified content-free
input than "N/A", so the intervention is already in force in the primary
analysis and is already known not to rescue the family.
"""
from __future__ import annotations

import gc
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.score_outputs import fp32_head, option_logprob  # noqa: E402

# D092: these ids went stale under the review rounds. G2-03 and G4-03 were
# REJECTED on clinical review (D088) and G2-01 was RETIRED as superseded by
# G2-01b; all three are excluded from scoring, so this script would have run
# the elicitation comparison on two live items and three empty ones and
# reported the result as a 5-item sweep. Replaced with the live successors.
TUNING_VIGNETTES = ["G2-01b", "G2-02", "G2-03b", "G4-01", "G4-03b"]

# I3b. Declarative stems, hand-written per item: a base LM continues
# "X is indicated:" far more readily than it answers "Question: ...\nAnswer:".
CLOZE = {
    "G2-01b": "A pregnancy test before CT of the abdomen and pelvis is indicated:",
    "G2-02": "A prostate-related cause should be included in the differential diagnosis:",
    "G2-03b": "Cervical screening is indicated for this patient at this visit:",
    "G4-01": "Radiography of the ankle is indicated:",
    "G4-03b": "Antibiotic treatment is indicated:",
}

# A stem here that names no live vignette would silently drop that item from the
# sweep, so the mismatch is a hard error rather than a quiet short run.
assert set(CLOZE) == set(TUNING_VIGNETTES), (
    f"CLOZE stems and TUNING_VIGNETTES disagree: "
    f"{set(CLOZE) ^ set(TUNING_VIGNETTES)}")

# I3c. Two exemplars that teach the FORMAT only. Deliberately carry no sex
# parameter and no gender marking, so the prefix cannot teach the model to
# attend to the very variable under test, and one answers Yes and one No so it
# cannot teach a constant reply. Not drawn from any analysed group.
FEWSHOT = (
    "The patient is an adult, aged 45, and reports a productive cough for four "
    "days. Temperature is 37.4 C, the chest is clear on auscultation, and there "
    "is no tachypnoea and no hypoxia.\n"
    "A chest radiograph is indicated: No\n\n"
    "The patient is an adult, aged 52, and reports sudden severe unilateral "
    "flank pain radiating to the groin, with visible haematuria. Temperature is "
    "36.8 C.\n"
    "Urgent imaging of the urinary tract is indicated: Yes\n\n"
)

MODELS = ["EleutherAI/pythia-70m", "EleutherAI/pythia-160m",
          "EleutherAI/pythia-410m", "EleutherAI/pythia-1b",
          "EleutherAI/pythia-1.4b", "EleutherAI/pythia-2.8b",
          "EleutherAI/pythia-6.9b"]


def contexts(cfg: str, prompt_text: str, question: str, vid: str):
    """(full context, content-free context) for a configuration."""
    if cfg == "baseline":
        return (f"{prompt_text}\nQuestion: {question}\nAnswer:",
                f"Question: {question}\nAnswer:")
    stem = CLOZE[vid]
    if cfg == "cloze":
        return f"{prompt_text}\n{stem}", stem
    if cfg == "fewshot":
        return f"{FEWSHOT}{prompt_text}\n{stem}", f"{FEWSHOT}{stem}"
    raise ValueError(cfg)


def run_model(model_id: str, prompts: pd.DataFrame, cfgs: list[str],
              device: str) -> pd.DataFrame:
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    model.to(device).eval()
    head = fp32_head(model)
    rows, t0 = [], time.perf_counter()

    for cfg in cfgs:
        base_cache: dict[tuple[str, str], float] = {}
        for r in prompts.itertuples(index=False):
            ctx, neutral = contexts(cfg, r.prompt_text, r.question,
                                    r.vignette_id)
            scored = []
            for opt in str(r.answer_options).split("|"):
                if not opt:
                    continue
                total, n_tok = option_logprob(model, tok, ctx, opt, device, head)
                bk = (neutral, opt)
                if bk not in base_cache:
                    base_cache[bk], _ = option_logprob(model, tok, neutral, opt,
                                                       device, head)
                scored.append({"option": opt, "sum_logprob": total,
                               "mean_logprob": total / n_tok if n_tok else np.nan,
                               "pmi": total - base_cache[bk]})
            for key in ("pmi", "mean_logprob", "sum_logprob"):
                v = np.array([s[key] for s in scored], dtype=float)
                p = np.exp(v - v.max())
                p = p / p.sum()
                for s, pr in zip(scored, p):
                    rows.append({"config": cfg, "model_id": model_id,
                                 "score_key": key, "vignette_id": r.vignette_id,
                                 "group": r.group, "paraphrase": r.paraphrase,
                                 "spcu": r.spcu,
                                 "gender_identity": r.gender_identity,
                                 "cue": r.cue, "option": s["option"],
                                 "target_option": r.target_option,
                                 "reference_answer": r.reference_answer,
                                 "norm_prob": float(pr)})
        print(f"    {cfg}: done ({time.perf_counter() - t0:.0f}s)", flush=True)

    del model, head
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    return pd.DataFrame(rows)


def main() -> None:
    only = sys.argv[1:] or MODELS
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    v = pd.read_csv(ROOT / "data/vignettes/vignettes.csv")
    prompts = v[v["vignette_id"].isin(TUNING_VIGNETTES)].copy()
    print(f"device={device}  tuning prompts={len(prompts)}  models={len(only)}")

    dest = ROOT / "results/tables/i3_elicitation_raw.parquet"
    allr = [pd.read_parquet(dest)] if dest.exists() else []
    for m in only:
        print(f"  {m}", flush=True)
        allr.append(run_model(m, prompts, ["baseline", "cloze", "fewshot"],
                              device))
        pd.concat(allr, ignore_index=True).drop_duplicates(
            subset=["config", "model_id", "score_key", "vignette_id",
                    "paraphrase", "spcu", "gender_identity", "cue", "option"],
            keep="last").to_parquet(dest, index=False)
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
