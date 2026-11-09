# Instrument validation (RQ0)

**Run:** 2026-10-27 · `scripts/validate_instrument.py` · Apple M4 Pro, MPS,
float32, seed 20251027 · results in `results/tables/rq0_instrument_validation.json`
and `.csv`.

## Why this exists

Every hypothesis in `preregistration.md` is a claim about a difference between two
measured numbers. None of it means anything until the apparatus producing those
numbers is shown to detect an effect that is really present and to stay quiet when
one is not. That check is logically prior to the hypotheses, and it does not need
clinical content, so it could be run while the vignettes were still unwritten.

The stimuli are deliberately **administrative, not clinical**: record numbers and
letter codes. Nothing here asserts a clinical fact, so nothing here crosses the
line `AI_USE.md` draws around clinical content, and nothing can leak into the
authored vignettes by accident.

The harness imports `option_logprob` and `fp32_head` from `src/score_outputs.py`
rather than reimplementing them. A validation that reimplements what it validates
shows only that two of our own functions agree.

## T1, Determinism ✅ PASS

Same prompt scored twice. **Maximum absolute PMI drift: exactly 0.0**, on all three
models.

This matters more than it looks. MPS kernels are not guaranteed bitwise
reproducible, and had drift been non-zero, every Δ in Phase 2 would have needed a
repeat-measurement error bar to separate a gender effect from run-to-run noise.
It is zero, so a single pass per prompt is sufficient and Δ carries no measurement
variance. One fewer thing to defend.

## T2, Signal recovery (positive control for the apparatus) ✅ PASS

The prompt states the answer in plain words ("the applicable rule states that Code
A is the correct code"). The named option must win.

| Score key | Stated Code A | Stated Code C |
|---|---|---|
| `sum_logprob` | ✅ p = 0.953 | ✅ p = 0.947 |
| `mean_logprob` | ✅ p = 0.731 | ✅ p = 0.731 |
| `pmi` | ✅ p = 0.782 | ✅ p = 0.972 |

Recovered on every score key, both targets, all three models. **This is the control
the design was missing.** Without it, a null in Phase 2 is uninterpretable, a
model with no gender gap and a broken scorer produce the same table. Note it is a
distinct control from Group 2: Group 2 tests whether the *models* respond to gender
when gender is clinically relevant; T2 tests whether the *instrument* can see
anything at all.

## T3, Nuisance floor (the important one)

Matched prompt pairs differing **only** by the gender token, in content-free
administrative text. Max |Δ norm_prob| across three frames, `pmi`:

| Model | Floor (max) | Floor (mean) |
|---|---|---|
| pythia-70m | 0.0207 | 0.0126 |
| pythia-160m | **0.0626** | 0.0261 |
| pythia-410m | 0.0309 | 0.0244 |

**This is not a null test and must never be reported as one.** A real model does
differ between "the woman" and "the man" with no clinical content present. That
difference is the floor a clinical effect has to clear before it means anything.

**Two consequences, and the second is a design change.**

1. **Every Δ in Phase 2 must be reported against this floor.** A Δ of 0.02 on a
   clinical vignette is not evidence of clinical bias at 70m; it is what the gender
   token does on its own.
2. **RQ3 is confounded unless each model is normalised by its own floor.** The floor
   is not constant across the ladder, it triples from 70m to 160m and is
   **non-monotonic** (160m above 410m). So "the gap grows with model size", the
   natural RQ3 finding, can be produced entirely by the floor growing. RQ3 must
   compare *floor-relative* gaps, and the floor must be measured per model and per
   checkpoint. This was not in the pre-registration and is recorded as a deviation.

## T4, Score-key robustness: no key is length-neutral

Options matched in meaning, deliberately unmatched in length ("Code A" vs "the code
designated as A in the schedule"). Share of probability mass landing on the short
options, 0.5 would be length-neutral:

| Model | `sum_logprob` | `mean_logprob` | `pmi` |
|---|---|---|---|
| pythia-70m | 1.0000 | 0.165 | 0.545 |
| pythia-160m | 1.0000 | 0.402 | **0.037** |
| pythia-410m | 1.0000 | 0.756 | 0.306 |

`sum_logprob` is catastrophic and consistently so, it puts **essentially all** mass
on the short option, every model, every time. That confirms the docstring's claim
empirically rather than by assertion. But the headline is worse than expected:
**`mean_logprob` and `pmi` are both unstable across models, in opposite
directions**, and `pmi` at 160m is the single worst reading in the table (0.037,
it over-corrects almost completely toward the long options).

So the `pmi` default cannot be defended as "length-neutral". It is defensible only
as "least bad on average", which is a weaker claim than the code comment implies.

**What this does and does not threaten.** It does **not** create spurious gender
effects: length bias is identical across the gender arms of a matched pair, so it
cancels in Δ. What it destroys is **sensitivity**. If length bias pushes the softmax
to p ≈ 0.9999 on one option, both arms sit at 0.9999 and the gender effect is
squashed to nothing, a floor effect that would read as "no bias found".

**Therefore: answer options must be matched in token length within each option
set.** This is a hard constraint on the authored vignettes, not a preference, and
it is cheap to satisfy at writing time and impossible to repair afterwards.

## Verdict

The apparatus is sound: deterministic, and able to recover an effect that is
present. Two things came out of it that the design did not have:

- a **per-model nuisance floor** every Δ must be reported against, and
- a **length-matching constraint** on answer options, with the reason stated in
  terms of power rather than bias.

Neither was in the pre-registration. Both are logged as deviations in
`preregistration.md` §9 and as **D035**.

## Reproduce

```bash
.venv/bin/python -m scripts.validate_instrument                              # 70m
.venv/bin/python -m scripts.validate_instrument --model EleutherAI/pythia-160m
.venv/bin/python -m scripts.validate_instrument --model EleutherAI/pythia-410m
```

Runs in well under a minute per model. **Re-run the floor for every model and
checkpoint in the final ladder** before interpreting any Δ.
