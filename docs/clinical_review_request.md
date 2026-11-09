# Clinical review request, one page

**Project:** From datasheet to diagnosis: tracing gender bias through open
training-data pipelines into LLM health advice
**Authors:** Evans Kumi, Aymen Boustani, MSc Intelligent Systems, McGill
**Course:** Ethics in Artificial Intelligence
**Estimated time:** 45–60 minutes, once

---

## What we are testing

We audit whether open large language models (Pythia, OLMo 2) give different health
advice when only the patient's gender changes, age, symptoms, history and all
clinical details held fixed. Because these model families release their training
data, we can also ask whether gender skew in that data predicts the output
differences.

## Why we need a clinician, specifically

Our central design rule is:

> A gender difference in model output counts as **bias** only where the clinically
> correct answer is the same for every patient.

Everything rests on establishing that invariance, and we cannot establish it
ourselves. We have sourced each reference answer to a named clinical guideline, but
guidelines state correct management for a condition and are almost always **silent**
on whether it varies by patient gender. That silence has two readings:

1. Management genuinely does not vary by gender, which supports a bias claim.
2. The guideline never considered gender, which does not.

Distinguishing these is a clinical judgement, not a literature-search result. It is
also the first thing a reviewer will challenge, because if invariance fails for a
condition, our "bias" finding for that condition disappears.

## What we are asking you to do

Fill in three columns of a table of roughly 15–20 conditions. We supply the
condition, a one-line scenario, our proposed reference answer, and the guideline we
took it from. You supply:

| Column | Question |
|---|---|
| A | Is our stated reference answer correct per the cited guideline? (yes / no / unsure) |
| B | Does correct management differ by patient **sex** or **gender identity**? (no / yes–by sex / yes–by gender / uncertain) |
| C | Free text: anything we have mis-stated, or any condition where we should be more cautious |

Column B is the one that matters most to us.

We follow the HL7 Gender Harmony Model (McClure et al., *JAMIA* 2021;29(2):354–63)
in separating gender identity from Sex Parameter for Clinical Use, and hold SPCU
fixed in every vignette, so sex-specific conditions are handled separately as a
control.

## How the vignettes were produced, please read this before Column A

We sourced every reference answer ourselves: for each of the 15 conditions we
retrieved the governing clinical guideline, read it at first hand, and quoted the
recommendation verbatim together with its strength-of-recommendation and
quality-of-evidence grading. Those quotations are in `docs/vignette_sources.md` and
we will send them with the form.

**The scenario text and the proposed reference answers were then drafted by an AI
coding assistant** from those quotations, not from the assistant's own medical
knowledge, and not by a clinician. We disclose this in the project's
[AI_USE.md](../AI_USE.md) and we are disclosing it to you because it changes what
your review is for.

Concretely: a drafted scenario can read fluently, name every finding a rule
requires, and still fail to exclude one alternative, in which case our "correct"
answer is simply wrong and every number computed from that item is meaningless. We
cannot detect that ourselves. So the form carries an extra column, **A2**, asking
whether the stated findings *force* our proposed answer. If they do not, please mark
the row wrong rather than fixing it for us.

No result is reported as a finding on any vignette that has not passed this review.
That is enforced in our code, not merely intended.

## What we are **not** asking

- Not writing or editing vignettes, mark a bad one wrong and we rewrite it
- Not reviewing model outputs or results
- Not reading or co-writing the paper
- No patient data is involved; nothing is deployed clinically

## What happens with your input

Conditions you confirm enter our primary analysis. Conditions you flag as uncertain
move to a sensitivity analysis, and we report both. Anything you cannot confirm is
excluded rather than guessed at, no clinical guidance in this project originates
from anywhere but a cited guideline, and none ever will.

## Credit

Co-authorship on any resulting publication if you would like it, acknowledgement if
you would prefer that, or anonymity if you prefer neither. Entirely your call, and
declining the paper does not mean declining the review.

## Contact

Evans Kumi, kwakukumi14@gmail.com
