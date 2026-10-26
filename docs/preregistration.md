# Pre-registration: directional predictions for RQ2, derived from RQ1

**Frozen:** 2026-10-26. **Parent commit:** `de031e1` (RQ1 full sweep).
**Authors:** Evans Kumi, Aymen Boustani.

This document exists so that the RQ2 output audit is a *test* of stated
predictions rather than a search for whichever gender gap happens to appear. It is
append-only: once committed, hypotheses are never edited or removed. Changes of
plan go in §9 as dated deviations, with reasons.

---

## 1. What is observed, and what is not

Honesty about this is the whole point of the document, so it comes first.

**Already observed (and used to derive the predictions below):**
- The complete RQ1 corpus sweep — 1,504 infini-gram queries over the Pile and
  OLMo-mix-1124, 42 powered concept-corpus rows. `results/tables/rq1_corpus_skew.csv`,
  recorded as D024.

**Not observed by either author:**
- Any score from any audited model on any analysis-ready vignette. No vignette is
  analysis-ready yet: all 360 prompts still carry the `<<CLINICAL_FINDINGS>>`
  placeholder and `reference_answer: null`, and `src/score_outputs.py` refuses to
  run on them without `--allow-unready`.

**Declared prior run, which carries no information about any hypothesis below:**
`results/raw/EleutherAI_pythia-70m__main__float32.parquet` is a pipeline smoke test
on pythia-70m over placeholder vignette text, tagged `placeholder_text=True`. The
text scored contains no clinical findings and the vignettes it scores have no
reference answers, so no concordance outcome can be computed from it. It exists to
prove the scoring code runs and is not degenerate. It is excluded from every result
table by its tag.

**Therefore the claim this document supports is narrow and should be stated that
way in the paper:** the predictions were fixed in a public commit before any
analysis-ready output was generated. They were *derived from* observed corpus data,
so they are informed predictions, not blind hypotheses. That is the strong form
available here, and the paper must not overclaim beyond it.

---

## 2. The derivation

RQ1 measures, for each health concept, `log2(rate_female / rate_male)` where rate
is `P(concept | "<pronoun> <predicate>")` summed over eight illness-narration
templates. Positive = relatively female-associated.

Illness narration carries a baseline female skew (sex-neutral mean **+0.778** in
the Pile, **+0.560** in OLMo-mix), so zero is not a reference point and every value
below is centred on its own corpus's sex-neutral mean (D024).

| Concept family | OLMo-mix | Pile | Vignettes |
|---|---|---|---|
| neurodevelopmental | **−0.974** | **−0.812** | G3-04, G3-05 |
| cardiac | **−0.929** | **−0.671** | G3-02 |
| other somatic | +0.180 | +0.058 | G1-*, G4-* |
| pain | +0.287 | +0.107 | G3-01 |
| **psychological** | **+0.804** | **+0.651** | rationale codes only |

Ordering is identical in both corpora; across the 15 concepts powered in both,
Pearson r = 0.931, Spearman ρ = 0.936.

**The mechanism assumed throughout:** a model trained on text where a diagnosis
co-occurs preferentially with one gender will endorse that diagnosis more readily
for patients marked as that gender, even where the clinical findings are identical
and the guideline is sex-invariant.

---

## 3. Outcome measures

Two distinct outcomes, which must not be conflated.

**O1 — guideline concordance (the ethics-relevant outcome).**
`norm_prob` of the guideline-concordant option, from `score_key=pmi`
(D014, D015). This is what a patient experiences as better or worse care. Defined
only for vignettes with a sourced reference answer.

**O2 — target-diagnosis endorsement (the mechanism-relevant outcome).**
`norm_prob` of the option naming the vignette's target diagnosis, whether or not it
is the concordant answer. This is the outcome the corpus mechanism speaks to
directly, and it is defined even where concordance is contested.

**The contrast.** For matched prompt pairs — identical template, paraphrase, SPCU
value and clinical text, differing only in gender-identity arm:

> Δ = outcome(woman arm) − outcome(man arm)

Δ is also computed for the non-binary arm against each of the other two, and every
gendered arm is compared against the **blinded** arm (D021), which is never pooled
with them.

---

## 4. Confirmatory hypotheses

Four. Each states a direction, the vignettes it is tested on, and what result
falsifies it. Nothing else in this project is confirmatory.

### H1 — Neurodevelopmental referral (strongest prediction)
Corpus: neurodevelopmental is the most male-skewed family in both corpora
(−0.97 / −0.81), with *attention deficit* (−1.16) and *autism* (−1.04) at the
extreme in OLMo-mix.

**Prediction: Δ < 0 on O1 for G3-04 and G3-05** — models endorse referral for
specialist ADHD and autism assessment less readily for the woman arm than the man
arm, given identical findings.

**Falsified by:** Δ ≥ 0, or a null, in either vignette in either model family.

### H2 — Cardiac triage urgency
Corpus: cardiac is the second most male-skewed family (−0.93 / −0.67); *heart
attack* is the single most male-associated sex-neutral concept measured (−1.39).

**Prediction: Δ < 0 on O1 for G3-02** — the woman arm receives less probability
mass on the more urgent triage option.

**Falsified by:** Δ ≥ 0, or a null.

**Conditional.** G3-02's status is unresolved: the AHA/ACC chest pain guideline
discusses sex differences, and if it recommends anything sex-differentiated for
this scenario then G3-02 is a Group 2 control, not a bias test, and H2 is withdrawn
rather than tested. That reading is pending (`docs/source_links.md`). **If H2 is
withdrawn, it is withdrawn in §9 with the guideline text quoted — not quietly
dropped, and not retained as a weaker claim.**

### H3 — Discriminant null on unskewed conditions
Corpus: "other somatic" is essentially unskewed once centred (+0.18 / +0.06).

**Prediction: Δ ≈ 0 on O1 for G1-01…G1-05 and G4-01…G4-03**, with the 95% interval
on the family-level estimate containing zero.

**Falsified by:** a systematic non-zero Δ across this family.

H3 is what makes the project an argument about *mechanism* rather than a claim that
models are biased everywhere. A paper that finds gaps on every vignette has shown
much less than one that finds them exactly where the corpus is skewed. **H3 failing
is more damaging to the thesis than H1 or H2 failing**, because it would mean the
gaps are not corpus-traceable.

### H4 — Linkage (RQ4)
**Prediction: across all tested vignettes, sign(Δ on O2) = sign(centred corpus skew
of that vignette's target concept), and the two correlate positively** (Spearman
ρ > 0, one-sided).

Stated on O2 rather than O1 deliberately: concordance flips sign with how the
question is posed, endorsement does not. Tested separately per corpus-model pair
— Pile skew against Pythia, OLMo-mix skew against OLMo 2 — because the linkage
claim is that a model inherits *its own* training corpus's skew. Cross-pairings
(Pile skew against OLMo 2) are a negative control: they should link more weakly.

---

## 5. Pre-registered divergence: acute pain (G3-01)

This one is worth isolating, because the corpus and the clinical literature predict
**opposite** directions.

- Hoffmann & Tarzian (2001) and the undertreatment literature predict women receive
  *less* analgesia — Δ < 0.
- RQ1 predicts the reverse: pain is mildly *female*-skewed after centring (+0.29 /
  +0.11), and *severe pain* reaches +0.63 in OLMo-mix. On the §2 mechanism that
  gives Δ > 0.

So G3-01 discriminates between two accounts of where model bias comes from:
corpus co-occurrence statistics, or reproduction of documented clinical bias
through some other route. **We commit now to reporting whichever direction appears,
and to not reinterpreting the mechanism after the fact.** Because the two
predictions conflict, G3-01 is not counted as confirmatory for either; it is a
pre-registered discriminating test with both outcomes specified in advance.

This is also the cleanest place to be honest in the write-up: our mechanism is one
hypothesis among several, and we have one case where it contradicts the field's
expectation.

---

## 6. Controls, and the instrument-sensitivity gate

**Positive control — Group 2 (G2-01, G2-02, G2-03).** Here the correct answer
*does* differ by sex, so Δ must be large and in the clinically correct direction.

**This is a gate, not a result.** If Group 2 shows no gender effect, the instrument
cannot detect gender effects at all, and every null elsewhere — H3 included — is
uninterpretable. We commit to reporting the Group 2 effect size first, and to
stating plainly that the audit is insensitive if it is small, rather than
presenting nulls as findings.

**Negative control — Group 4 (G4-*).** No documented bias and identity is
clinically irrelevant: Δ ≈ 0 expected. Group 4 also carries H3.

**Blinded-arm reference (D021).** Distance from the blinded arm measures how much
*any* gender marking perturbs the answer, separating "the model treats women
differently from men" from "the model treats gender-marked patients differently
from unmarked ones."

**SPCU control (D001, D012).** Gender identity is the manipulated factor; SPCU is
held fixed within each contrast and crossed across them. If an effect tracks SPCU
rather than gender identity, it is a sex-parameter effect, not a gender-identity
effect, and must be reported as such.

---

## 7. Analysis plan

**Unit.** The matched prompt pair (§3). Pairs are complete by construction: every
clinical text appears in every arm.

**Estimate.** Mixed-effects model on the paired differences, random intercepts for
vignette and for paraphrase, fitted per model. Reported with 95% intervals.

**Test.** Wilcoxon signed-rank on paired differences within each hypothesis family,
one-sided where §4 states a direction, as the distribution-free primary test.

**Multiple comparisons.** Holm–Bonferroni across H1–H4 at family-wise α = .05.
Within-family vignette-level tests are descriptive and labelled as such.

**Models are not replicates.** The eight-model Pythia ladder is one family at
eight sizes. Scores are never pooled across sizes as independent observations;
size is a moderator (RQ3). Pythia and OLMo 2 are the two independent replications,
and a prediction counts as supported only if it holds in both.

**Checkpoints.** The pythia-1.4b checkpoint sweep tests whether a gap emerges
during training (RQ3). Direction is not pre-registered — RQ1 says nothing about
training dynamics — so this is exploratory.

**Exclusions, fixed now.**
- Prompts failing `_assert_not_degenerate()` (options tied within 1e-9).
- Any run tagged `placeholder_text=True`.
- Vignettes without a sourced reference answer are excluded from O1 and may still
  enter O2 (D003); which vignettes these are will be recorded at freeze time of the
  vignette set, not chosen after seeing scores.
- pythia-12b runs float16, not float32 (48 GB limit). Its results are reported with
  a precision-sensitivity check and are not used to decide any hypothesis on their
  own, given D015.

---

## 8. Exploratory — explicitly not confirmatory

Labelled so they cannot later be presented as predictions.

- **Psychologizing (the strongest corpus signal, +0.80 / +0.65).** There is no
  psychologizing vignette: G3-03 was dropped because no guideline says "do not
  attribute these symptoms to anxiety" (D020). The construct survives only as a
  **rationale code** applied to generated explanations (D005), which needs the
  judge, Cohen's κ ≥ 0.70 against hand-coding, and the codebook. We expect
  psychologizing codes to fall more often on the woman arm, but this is a coding
  outcome on a secondary method, not a scored hypothesis. **The corpus result here
  is strong and the output test is weak — the paper must say so rather than letting
  the corpus finding stand in for an output finding.**
- Non-binary arm effects. RQ1 has **no** non-binary measure ("they has" is
  ungrammatical, and "they" is overwhelmingly plural), so no corpus-derived
  direction exists. Any output difference is reported descriptively. This asymmetry
  must be stated wherever the non-binary arm is claimed as novelty.
- OLMo 2 base vs instruct: whether instruction tuning widens or narrows gaps.
- Qwen3-8B as the weights-only contrast (RQ5) — no corpus access, so no linkage.
- Interactions between SPCU and gender identity.

---

## 9. Deviations

Append-only. Every entry: date, what changed, why, and whether it was decided
before or after seeing RQ2 scores.

| Date | Change | Reason | Before/after seeing scores |
|---|---|---|---|
| — | none yet | — | — |
