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

Two distinct outcomes, which must not be mixed up.

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
| 2026-10-27 | **Every reported Δ must be accompanied by that model's nuisance floor**, measured on content-free prompts differing only by the gender token | Instrument validation (D035) measured the floor at max \|Δ norm_prob\| = 0.0207 / 0.0626 / 0.0309 for pythia-70m / 160m / 410m. A Δ below the floor is the gender token moving the distribution with no clinical content present, not clinical bias | **Before.** No clinical content exists yet; all 360 prompts are still placeholders |
| 2026-10-27 | **RQ3 compares floor-relative gaps, not raw gaps**, with the floor measured per model and per checkpoint | The floor is not constant across the ladder and is **non-monotonic** (160m > 410m). "The gap grows with model size" can therefore be produced entirely by the floor growing. Raw cross-model Δ comparison is confounded (D035) | **Before** |
| 2026-10-27 | **Answer options must be token-length matched within each option set** | No score key is length-neutral: `sum_logprob` puts ~100% of mass on the shortest option at every size, and `pmi`/`mean_logprob` are unstable across models in opposite directions. Length bias cancels in a matched gender pair, so this threatens **sensitivity, not validity** — an unmatched set squashes the real effect toward zero and reads as "no bias found" (D035) | **Before** |
| 2026-10-27 | **D027 adopted** — psychologizing added as a crossed cue factor, **scoped to G3-02 only**; estimand is the cue × gender interaction | §4.3.2 of the chest-pain guideline (COR 2a, B-R) gates CBT referral behind recurrent presentations and a negative ischaemia workup, so it is the only item where a guideline licenses the test. **Exploratory, not confirmatory**: it postdates this document's freeze and does not join H1–H4 or the Holm–Bonferroni family | **Before** |
| 2026-10-28 | **Family-level p comes from a cluster bootstrap over vignettes (10,000 resamples), not the pooled Wilcoxon** named in §7. The pooled Wilcoxon is still reported, labelled anti-conservative | §7's unit reads as one observation per prompt pair, but each vignette contributes 6 pairs of the *same* clinical text, so pooling treats paraphrase count as sample size. A noise-only simulation (true effect zero) rejected at p = .025 through the pooled test; the clustered test gave p = .40–.70 across five seeds (D036) | **Before.** No analysis-ready score exists; all 15 vignettes still hold `<<CLINICAL_FINDINGS>>` |
| 2026-10-28 | **H3 additionally requires an equivalence test**: the 90% interval on the family mean Δ must lie within ± the largest per-model nuisance floor | A null cannot be supported by failing to reject it. The equivalence margin is not a convention but the measured floor from D035 — a gap smaller than what the model produces on content-free prompts is not clinical by construction. Without this, H3 is unfalsifiable in one direction and auto-refuted in the other (D036) | **Before** |
| 2026-10-28 | **Inference unit varies with cluster count, and H2's claim is narrowed accordingly.** H2 rests on one vignette, so it is tested on prompt pairs within G3-02 and its claim is scoped to that scenario, not to cardiac triage generally. H1's 2-cluster bootstrap p is reported with its tail flagged unresolvable | A single-vignette hypothesis cannot generalise over vignettes, and no test choice repairs that. Stating the scope is the only honest option; the alternative was to let a family-level p imply a generality the design does not support (D036) | **Before** |
| 2026-10-28 | **H4 is recorded as blocked, not withdrawn**, pending a `target_option` field per vignette | O2 is the mass on the target diagnosis *whether or not* it is concordant (§3); no template carries that pointer and `src/vignettes.py` does not propagate one. Approximating it from the reference answer would collapse O2 into O1 and make H4 a restatement of H1–H3, guaranteeing the linkage result by construction (D037) | **Before** |
| 2026-10-28 | **Vignette clinical text, option sets and candidate reference answers are AI-drafted** from guideline passages the authors quoted at first hand, behind a clinician verification gate; no result is reportable on an unverified item | Time constraint, disclosed rather than concealed: `AI_USE.md` was rewritten to state it before the drafting happened. The threat is mitigated for every Δ by holding the clinical text identical across arms, so stylistic affinity cancels within each contrast; it is **not** mitigated for between-vignette or concept-level comparisons, which is stated in the limitations (D038) | **Before** |
| 2026-10-28 | **G3-01's question narrowed** from "Would you offer analgesia, and at what strength?" to "Should analgesia be offered?" | The stem asked two things against a binary option set, so a model answering the dose half would have been scored as non-concordant on the offer half. Direction and vignette membership unchanged (D038) | **Before** |
| 2026-10-28 | **Group 2 reference answers are keyed by sex parameter** (`reference_answer_by_spcu`), not by a single value | A pregnancy test is indicated for SPCU female and not SPCU male. That difference is the Group 2 control working as designed, and a scalar reference answer could not express it — it would have scored one SPCU arm of every Group 2 item as wrong by construction (D038) | **Before** |
| 2026-10-28 | **G3-02 gains the two D027 cue arms** (`cue_absent`, `cue_present`), crossed with gender; `cue` joins the matched-pair key | Already adopted as exploratory on 2026-10-27; this records the implementation and the wording. Pairs are matched *within* cue level, so the cue cannot leak into the gender contrast. Still exploratory and still outside the Holm–Bonferroni family | **Before** |
| 2026-10-29 | **The §6 positive control is computed and reported first**, as `rq0_positive_control.csv`, and a model failing it has its nulls labelled instrument-insensitive | §6 committed to this gate in prose but `src/stats.py` never implemented it: all six contrasts held SPCU fixed inside the pair, so the SPCU contrast the gate needs appeared in no table. All seven Pythia sizes fail it — mean O1 on Group 2 is 0.497–0.501 against two options, i.e. chance | **After.** Scores existed for the Pythia ladder. The gate's *definition* is unchanged from §6; only its implementation is new |
| 2026-10-29 | **The audit runs on unverified AI-drafted vignettes**, with every table stamped `verification_status` | Time constraint. D038's gate forbids *reporting* an unverified item, not computing it; running early proves the pipeline on real text and makes the clinician's corrections measurable as a before/after effect size (D043) | **After** |
| 2026-10-29 | **`pmi` stays the primary score key, but pythia-1.4b's nulls under it are labelled instrument-limited** and the `mean_logprob` sensitivity becomes required | pythia-1.4b fails T2 signal recovery under `pmi`, reading a planted answer as the least likely of four; p(stated) under `pmi` falls monotonically with size, 0.782 → 0.281. Switching the primary key after seeing this would be choosing the key by its results (D042) | **After** |
| 2026-10-29 | **Cluster-bootstrap p is clamped at `2^-k` for k clusters**; exact sign-flip p reported beside it | With k = 2 and both clusters negative, no resample can cross zero, so the implementation floored the share at `1/n_boot` and H1 reported p = .0001, Holm p = .0003, **reject = True** — on an effect 10–50× smaller than the nuisance floor. Clamped it is p = 0.25 and does not reject. The change removes a false positive (D044) | **After** |
| 2026-10-29 | **RQ3's scaling ρ is reported only with its gap and floor components** | ρ(size, floor-relative gap) = −0.857, p = .014, which reads as "bias decreases with scale". Decomposed: ρ(size, gap) = +0.143, p = .76; ρ(size, floor) = +0.929, p = .003. The trend is entirely the instrument's noise growing with scale (D045) | **After** |
| 2026-10-29 | **Identity–SPCU merging added as an exploratory analysis**, outside the Holm family and with no p claimed | Found by implementing the §6 control, not by testing H1–H4. Group 2 holds SPCU fixed and varies identity, so the correct answer is constant within a pair; Qwen3-8B shows a +0.216 interaction, 7.65× its floor, 6/6 arms in the same direction. Promoting a control's by-product to a confirmatory hypothesis is the move preregistration prevents (D046) | **After** |
| 2026-10-29 | **The nuisance floor is read from the score key in use**, not from `pmi_floor_max` unconditionally | The `mean_logprob` sensitivity re-analysis was comparing that key's margins against PMI's floor and reversing the gate verdict for Qwen3-8B. The validator had always written per-key floors; the reader was wrong. With matched floors the verdict is robust across keys | **After** |
| 2026-10-29 | **RQ3's scaling claim is the within-family (Pythia-only) row**; the all-model ρ is reported as a between-family contrast, not a scaling result | ρ(size, gap) is +0.143 (p = .76) across the Pythia ladder and +0.705 (p = .023) across all ten models, because the second varies family, corpus and instruction tuning alongside size. Only the first holds training data constant (D045) | **After** |

**Note on all twenty.** Twelve are marked **Before**: each of those was decided
while the only scored artefact in the repository was the pythia-70m placeholder-text
smoke run, whose numbers carry no information about any hypothesis (D025). The
vignette set reached 0 blockers and built 384 analysis-ready prompts on 2026-10-28,
and no model had been run against it. Of those twelve, three change how H1–H3 are
**tested** and none changes a predicted direction or a vignette's family membership;
one records a blocked outcome measure rather than dropping the hypothesis it carries.

**The eight marked After** were all decided on 2026-10-29, after the ten-model run
existed, and they are declared as such rather than folded into the method. None of
them changes a hypothesis, a predicted direction, the primary score key, or a
vignette's family membership. Six are instrument- or reporting-level fixes to faults
the run exposed, and every one of them makes a result *weaker*: the §6 gate now
disqualifies nine models' nulls, the `2^-k` clamp removes H1's false positive, the
RQ3 decomposition removes a significant scaling trend, and the per-key floor
lookup removes a verdict flip. The two that add analyses — the identity–SPCU
merging and the provisional run itself — are labelled exploratory and provisional
respectively, outside the Holm–Bonferroni family and outside the reportable set
until clinician review returns (D043, D046).

**What is still true of the pre-registration proper.** H1–H4, their predicted
directions, the primary score key, the inference unit, the four vignette groups and
the equivalence margin's definition are all as filed on 2026-10-26, before any
model was scored. Every pre-registered hypothesis was tested as filed, and every one
of them failed to reject.

---

## 10. Amendment 1 — two reporting tiers (2026-11-09, D091)

**Decided after seeing scores.** Stated plainly because that is the fact that
matters when reading it.

### What this document said before

§9's 2026-10-28 entry committed to: *"no result is reportable on an unverified
item"*, and D038/D043/D064 implemented it as a single gate — clinician
verification or nothing. Under that rule every number in this study was
`PROVISIONAL` and the course submission could present none of them as results.

### What it says now

Reporting has **two tiers**, and "reportable" names which one.

| Tier | Bar | What may be said | Venue |
|---|---|---|---|
| **0** | a row never reviewed by anyone | nothing; not citable | — |
| **1** | **every** row author-reviewed against a **quoted, first-hand** guideline passage | numbers presented as results, each carrying **"pending clinical validation"** | coursework, internal, teaching |
| **2** | clinician verification on every row | numbers presented without that qualifier | public paper, archival release |

The ECSE-557 submission is made at **tier 1**. The public paper will not be
submitted below **tier 2**.

### Why the change

Three reasons, in order of weight.

1. **The original rule conflated two different claims.** "This number is a
   property of these models under this instrument" and "this number is clinically
   meaningful" have different evidentiary bars, and only the second needs a
   clinician. A measurement result — that 7 of 10 models fail the positive
   control, that an exact sign-flip test on k = 4 clusters cannot resolve below
   p = 0.0625 — is about the apparatus, and clinician review cannot make it more
   or less true.
2. **Author review turned out to be a real check, with evidence.** It was
   adopted as a stopgap and has since **rejected two vignettes outright**
   (G2-03, G4-03), corrected a third that had reproduced the rejected row's
   defect (G4-03b, D088), and caught three guideline-citation errors that no
   validator detected (D040, D085, D088). A step with that hit rate is not
   usefully grouped with "unverified".
3. **The gate was producing the wrong incentive.** A single all-or-nothing
   threshold that could not be met before the deadline meant the honest label
   and the useless label were the same label, which is how a provenance system
   stops being read.

### What did NOT change, and this is the part that keeps it honest

- **Tier 0 is unchanged.** A vignette never reviewed against a first-hand quote
  is not reportable at any tier. The amendment promotes author review by one
  tier; it does not make unreviewed text citable. `src/stats.py` still blocks
  the mixed cases.
- **Nothing is relabelled retroactively.** Tier is derived from the rows
  themselves at analysis time, not set by a flag, so a table cannot be promoted
  by anyone's intention.
- **Every tier-1 presentation carries the condition.** Enforced in three places
  rather than left to the author: `scripts/results_summary.py` prints it,
  `src/plots.py` burns it into every figure, and `deck_src/figures.js` puts it
  on every results slide of the deck.
- **The clinical review still happens, and its result is reported either way.**
  It is scheduled post-submission. If it changes a number, the changed number is
  what goes in the paper, and the before/after is reported as a measurable
  effect of verification — which was D043's original argument for running early.

### What would make this amendment look like motivated reasoning

Stated in advance so it can be checked: if clinical review later **overturns a
direction or a gate verdict**, then tier 1 was too weak a bar for the claims made
at it, and this amendment was wrong. The test is pre-committed and the answer is
not yet known. What would *not* vindicate it is review merely adjusting
magnitudes, since tier 1's claims are directional and floor-relative.
