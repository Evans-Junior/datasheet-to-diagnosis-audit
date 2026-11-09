# Instrument tuning log

Companion to `docs/preregistration.md` and `docs/decisions.md`. Every change to
the measuring instrument is recorded here with a pass criterion **written before
the run**, and the outcome recorded afterwards whether it passed or failed.

The paper reports the number of configurations tried, from this file. A disclosed
search over the instrument is defensible; an undisclosed one is not.

## Standing rules

1. **Tuning data.** Only Group 2 (positive control) and Group 4 (noise baseline)
   may be inspected while changing the instrument. These are the instrument
   validation strata and that is their purpose.
2. **Sealed data.** Group 1 and Group 3 carry H1/H2/H3. No instrument change may
   be selected, kept or reverted on the basis of what it does to them.
3. **Criterion before run.** Each entry states its pass criterion before it is
   executed. An entry whose criterion is written afterwards is void.
4. **Failures are recorded.** An intervention that fails stays in this log. The
   count the paper reports includes it.
5. **Classification.** A change is either a **correctness fix** (it repairs a
   demonstrable error in the measurement, justified without reference to any
   outcome) or **tuning** (it is a judgment call among valid options). Only
   tuning consumes the disclosed budget.

### Honest limitation on rule 2

The preregistered Group 3 analysis was executed and inspected **before** this log
was opened, so the sealed-data rule cannot be claimed retrospectively. The
protection actually in force is weaker and is stated as such: every criterion
below is defined on Group 2 and Group 4 quantities only, and makes no reference
to any Group 1 or Group 3 outcome. Group 3 is re-run after the instrument is
fixed, and both the pre-fix and post-fix values are reported side by side. The
reader can therefore see what the instrument change did to the headline numbers
rather than being asked to trust that it was not chosen for its effect on them.

---

## I1, Rebuild the nuisance floor on matched geometry

**Status:** criterion fixed, not yet run. **Classification:** correctness fix.

**The error.** The floor in `scripts/validate_instrument.py:172` is measured on
a content-free bureaucratic frame ("Record 4417 is open for review. The
applicant is the woman.") scored over `["Code A","Code B","Code C","Code D"]`,
and then used to gate binary Yes/No clinical items. The two are mismatched on
four axes simultaneously:

| Axis | Floor as built | Effect it gates |
|---|---|---|
| Option count | 4 arbitrary codes | 2 real words |
| Option tokens | 2 ("Code A") | 1 ("Yes") |
| Prompt | one filler sentence | ~120-word vignette |
| Aggregation | max over 4 options then max over 3 frames (max of 12) | one targeted delta |

A near-uniform softmax over four meaningless codes is the highest-variance place
in the instrument to measure a token perturbation, so the floor is inflated by
construction. The option-token mismatch is why the floor's magnitude changes by
2-3x across score keys while the gate effect is bit-identical across two of them
(D051): part of the floor is a length artifact that cannot occur in the effect.

**Why this is a correctness fix and not tuning.** The four mismatches are
demonstrable from the code and the stimulus files alone. No outcome is consulted
to establish them.

**The replacement.** Measure the floor on Group 4, which already exists and is
already scored, using the *same statistic as the gate*: the SPCU flip on the
target option, within (vignette, paraphrase, gender identity, cue). Group 4 is
clinically real, adult, has pregnancy explicitly excluded and carries no
sex-specific content, so flipping the sex parameter there should move nothing.
Whatever it does move is instrument noise measured on the right geometry.
Stratified by option count: binary Group 4 items (G4-01, G4-03) gate binary
contrasts, the four-option item (G4-02) gates four-option contrasts.

**Pass criterion (fixed before running).** The matched floor differs from the
Code-A floor by more than 25% for a majority of the ten models, on the primary
score key. That would confirm the geometry mismatch is material rather than
cosmetic.

**Declared in advance, and NOT a success criterion.** Which models pass the gate
under the new floor is an outcome to be reported, not a target. I1 is kept or
discarded on the criterion above alone. If the matched floor turns out to be
*higher* and fewer models pass, it is still kept, because it is the correct
measurement.

**Outcome:** **PASS**, decisively. Run 2026-11-03 via `scripts/matched_floor.py`
and `scripts/i1_regate.py`. On the primary score key the matched floor moved by
more than 25% for **10 of 10** models, median ratio **0.118**: the floor in force
was roughly **8.5x too high**. Outputs `results/tables/i1_matched_floor.csv`,
`i1_floor_comparison.csv`, `i1_gate_rerun.csv`.

| Score key | Models moved >25% | Median new/old |
|---|---|---|
| pmi (primary) | 10/10 | 0.118 |
| mean_logprob | 10/10 | 0.317 |
| sum_logprob | 9/10 | 0.157 |

**Reported outcome, which was not the criterion.** The gate goes from **1/10 to
3/10** on the primary key. Both OLMo models now clear their own floor:
OLMo-2-7B base at **2.24x** (margin +0.0175, floor 0.0078) and
OLMo-2-7B-Instruct at **1.88x** (+0.0199, floor 0.0106), with Qwen3-8B at
**3.86x**. All seven Pythia models remain inside their floors with unchanged
sign.

**Disclosure required by rule 5, against our own interest.** On the
`mean_logprob` sensitivity key the matched floor for Qwen3-8B moves the other
way, from 0.0165 to **0.0446**, and Qwen **flips from SENSITIVE to
INSENSITIVE** (0.58x). The matched floor is kept anyway, as pre-declared. The
instrument's verdict on Qwen is therefore score-key dependent, and that is now a
stated limitation rather than a resolved question.

**Second limitation, found during the run.** The binary Group 4 stratum contains
only **two** vignettes (G4-01, G4-03), so the cluster bootstrap over vignettes is
degenerate and `floor_boot_q95` equals the worst-vignette maximum exactly. The
four-option stratum has only **one** (G4-02). The geometry is now right and the
sample size is not. The floor rests on 2 clusters and 24 matched items. Writing
further Group 4 noise vignettes is the cheapest remaining improvement to the
instrument's power and is the recommended next build step.

---

## I2, Score-key sensitivity under the matched floor

**Status:** criterion fixed, not yet run. **Classification:** correctness fix.

**Claim to test.** Once the floor is measured on single-token options, the
`sum_logprob` and `mean_logprob` floors must coincide on the binary strata for
the same reason the effects do (D051): the sum over one token divided by one is
the sum. The apparent three-way score-key sensitivity then collapses to a
genuine two-way contrast, log-probability against PMI.

**Pass criterion (fixed before running).** Maximum absolute difference between
the `sum_logprob` and `mean_logprob` matched floors on the binary stratum is
below 1e-9 for all ten models.

**Outcome:** **PASS**. Maximum absolute difference between the `sum_logprob`
and `mean_logprob` matched floors on the binary stratum is **0.000e+00** across
all ten models, exactly as D051 requires. On the four-option stratum, where
options run to several tokens and the two keys must diverge, the same difference
is **4.893e-02**.

**Consequence.** The instrument has **two** genuine score keys on the gate and
on H1/H2, not three: log-probability and PMI. Length bias cannot affect those
strata by construction, for both the effect and now also the floor. Reporting
"three statistics agree" there would be double counting.

---

## I3, Elicitation for the Pythia family

**Status:** criterion fixed, not yet run. **Classification:** tuning (budget item 1).

**The observation.** Pythia Group 2 target-option probabilities are 0.497 to
0.501 across all seven sizes. That is not a weak signal, it is exactly uniform
over two options: the model is not treating the input as a question. Pythia is a
base LM with no instruction tuning, so zero-shot question-answer format is the
wrong harness for it. This is an elicitation failure, which is a property of the
instrument, not evidence about the model's clinical knowledge.

**Interventions, in fixed order. Stop at the first that passes.**

1. **Contextual calibration** (Zhao et al., *Calibrate Before Use*, ICML 2021).
   Divide out the content-free prompt's per-option probabilities. The existing
   T3 measurement is already reaching for this quantity but applies it as a
   subtracted threshold instead of a per-option correction.
2. **Cloze framing.** "Radiography of the ankle is indicated: yes" in place of
   the question-answer frame.
3. **k-shot prefix** using Group 4 vignettes as exemplars.

**Pass criterion (fixed before running).** At least 2 of the 7 Pythia models
show a Group 2 gate margin exceeding their own matched floor.

**Pre-declared reading of a total failure.** If all three interventions fail,
that is reported as a finding and not buried: open-corpus models at this scale
cannot be audited by probability-based vignette methods. That is a methodological
result about the auditability of the only models that ship the corpora this
project needs, which is the project's own subject matter.

**Criterion ambiguity, resolved before the final models reported.** The
criterion as written did not name a score key, and the two keys can disagree
(see I1's Qwen disclosure). Resolving it by the key already prespecified in
`src/stats.py:61`, `PRIMARY_SCORE_KEY = "pmi"`, fixed long before this log was
opened: **the criterion is judged on pmi**, with `mean_logprob` reported beside
it as the sensitivity key. Recorded here, with the gap acknowledged, because the
ambiguity was noticed after the five small models had reported and before the
two large ones had. The conservative reading is the one adopted.

**I3a outcome: already implemented, discovered during execution.** Contextual
calibration is not a new intervention for this instrument. `score_outputs.py:65`
defines `NEUTRAL_CONTEXT = "Question: {question}\nAnswer:"` and the `pmi` score
key is `logP(option | vignette, question) - logP(option | question alone)`. That
is exactly Zhao et al.'s content-free correction, with a better-specified
content-free input than their "N/A" because it holds the task framing fixed and
removes only the patient. The primary analysis has therefore been calibrated all
along, under a different name, and the Pythia margins of -0.0071 to +0.0025 are
*post*-calibration. Intervention 1 is marked failed without a separate run, and
the reason is structural rather than empirical.

There is also a mathematical reason it could not have rescued the family. Writing
the calibrated binary probability as `p(1-q) / [p(1-q) + (1-p)q]` for raw
probability `p` and content-free probability `q`, its derivative at `p = 0.5` is
`4a/(a+1)^2` with `a = (1-q)/q`, which is maximised at `q = 0.5` and is strictly
below 1 everywhere else. Pythia sits at `p` between 0.497 and 0.501, so
calibration *contracts* differences there rather than expanding them, and it
contracts signal and noise alike. Calibration corrects which option wins. It
does not create sensitivity to clinical content where there is none.

**Outcome:** **FAIL** on the primary key. Run 2026-11-03,
`scripts/i3_elicitation.py` and `scripts/i3_analyse.py`, all seven Pythia
models, 120 tuning prompts per configuration, Group 1 and Group 3 untouched.
Output `results/tables/i3_gate_by_config.csv`.

| Configuration | Pass count on pmi (criterion >=2) | On mean_logprob |
|---|---|---|
| baseline (question-answer) | 0/7 | 0/7 |
| I3b cloze | 1/7 | 1/7 |
| I3c few-shot | 1/7 | 2/7 |

The baseline reproduces the primary analysis exactly (margins -0.0035, -0.0063,
-0.0007, -0.0005, +0.0015, -0.0019, -0.0035), which confirms the variant harness
is faithful and that the differences below come from the prompt format alone.

**Why it fails rather than nearly passes.** No intervention works consistently.
Few-shot turns 6 of 7 margins positive but leaves them tiny and flips
pythia-410m from +0.0015 to -0.0021. Cloze lifts pythia-2.8b to 5.95x its floor
(+0.0214) while pushing pythia-6.9b to -0.0058. Nothing tracks model size:
Spearman of margin against parameter count is +0.429 (p = 0.34) at baseline,
+0.071 (p = 0.88) under cloze and +0.357 (p = 0.43) under few-shot.

**The result that matters more than the pass count.** **All 7 of 7 models change
the SIGN of their Group 2 margin across the three prompt formats.** The measured
direction of a sex-parameter effect in this family is not a property of the
model. It is a property of the prompt format. A single-format audit of these
models would report a direction that a different, equally defensible format
reverses.

**Pre-declared reading, now in force.** Open-corpus models at this scale cannot
be audited by probability-based vignette methods: not because they are too
small to know the clinical content, but because the elicitation harness
determines the answer's sign. This is reported as a finding and not buried. It
bears directly on the project's premise, since these are the only models that
ship the corpora the datasheet-to-diagnosis argument needs.

**Budget.** Tuning item 1 is spent. Two interventions executed (I3b, I3c), one
retired without a run on structural grounds (I3a). All three recorded as failed.


---

## I4, RQ4 corpus-provenance identifiability

**Status:** criterion fixed. **Classification:** correctness fix (diagnostic).

**The observation.** The RQ4 negative control fires: Qwen3-8B, trained on
neither corpus, correlates at rho +0.700 with the Pile and +0.758 with
olmo-mix, while the matched pairings are weak (OLMo base +0.060,
pythia-6.9b -0.117).

**Diagnostic to run.** Whether the two corpora differ enough on the audited
concepts for a provenance claim to be identifiable at all.

**Pass criterion for "RQ4 is identifiable" (fixed before running).** At least 6
concepts on common support with absolute corpus disagreement above 0.5 log2
units.

**Outcome:** **NOT IDENTIFIABLE.** Run 2026-11-03 via
`scripts/i4_identifiability.py`, output
`results/tables/i4_corpus_disagreement.csv`. Criterion required 6 concepts above
0.5 log2; **0** qualify.

| Quantity | Value |
|---|---|
| Concepts audited | 14 |
| On common support (both corpora) | 8 |
| olmo-mix only / Pile only | 5 / 1 |
| Spearman between corpora | **0.976** |
| Pearson | 0.963 |
| Median absolute disagreement | 0.125 log2 |
| Maximum absolute disagreement | 0.377 log2 (pneumonia) |
| Concepts above 0.25 / 0.5 / 1.0 log2 | 1 / 0 / 0 |

**Reading.** The Pile and olmo-mix are both large English web scrapes, and on the
audited concepts their gendered health-term skew is very nearly the same
measurement twice. Two measurements agreeing at rho 0.976 cannot attribute a
model's behaviour to one of them rather than the other, so matched and crossed
pairings are close to the same test and the design has almost no power to
discriminate provenance. Qwen3-8B scoring +0.700 and +0.758 against corpora it
never saw is not an anomaly to be explained away, it is the arithmetic
consequence of that agreement.

**The repair that was tried and abandoned.** Restricting the correlation to
concepts where the corpora disagree was the planned fix. It is not available:
the largest disagreement across all eight common-support concepts is 0.377 log2
and the median is 0.125, so the informative subset has a sample size of about
one. Recorded here as a failed intervention per rule 4.

**What replaces it.** RQ4 is reframed from a provenance estimate to a **measured
non-identifiability result**, reporting rho 0.976 as the coefficient that makes
provenance attribution by n-gram skew correlation impossible between these two
corpora, together with the condition under which it would become possible:
corpora that actually differ (domain-specific against web-scraped), or concepts
selected for maximum corpus disagreement rather than for clinical interest. Note
that selecting concepts that way trades clinical relevance for identifiability,
which is a design tension to state rather than hide.

**A second defect this exposed.** Only 8 of 14 concepts have skew in both
corpora, so the matched and crossed pairings were partly computed over
non-overlapping concept sets. The `common` support variant already in
`rq4_linkage.csv` is therefore the only comparable one, and the `all_powered`
variant should not be read as a like-for-like contrast.


---

## I5, Circularity introduced by I1 (found during execution, not planned)

**Status:** run 2026-11-03. **Classification:** correctness fix, arising from I1.

Not a planned entry. Found while checking why H3's new equivalence margin came
out as the binary floor (0.0131) rather than the four-option floor (0.0117):
H3's preregistered vignette set includes G4-01, G4-02 and G4-03, so after I1 the
margin is derived from three of the eight vignettes being tested.

**No pass criterion was fixed in advance**, because the problem was not
anticipated. Recorded as a diagnostic rather than a tested intervention, and the
preregistered H3 was not redefined. Three variants published instead; see D056.

**Outcome.** H3 is supported on all three. The clean variant, Group 1 only
against the matched floor, gives delta +0.000199 with CI [-0.003402, +0.003612]
inside a margin of 0.0117. The circularity is real and does not change the
verdict.

**Consequence for rule 1.** The standing rule permits tuning on Group 2 and
Group 4. Group 4 is also H3 test material, so that permission leaks into a
preregistered hypothesis. The rule is amended going forward: **Group 4 may be
used to build the instrument, and any H3 result that depends on a Group 4
derived quantity must be reported alongside its Group 1 only counterpart.**

---

# Validation round 1, 2026-11-07

A different kind of entry from I1–I5. Those changed the instrument. These add
**independent thresholds and disclosures** without altering any measured effect,
so none of them can move a result in a preferred direction. The reason they are
in this log rather than only in `decisions.md` is that the criterion-before-run
discipline is what makes them worth anything, and one of them produced a
prediction failure that belongs on the record.

Prompted by a direct question about whether the floor alone is trustworthy. It
is not, and the measurements below say so.

## I6, Permutation nulls on the real data

**Status:** run 2026-11-07. **Classification:** added threshold, no effect changed.
**Decision:** D060. **Script:** `scripts/permutation_null.py`.

**Criterion fixed before the run, written into the module docstring:**

> "perm_floor < floor is the EXPECTED result and is not evidence that the
> Group 4 floor is inflated… What would be informative is perm_floor > floor,
> which would mean between-vignette variability alone can manufacture an effect
> larger than the per-item resolution limit."

The reasoning was that averaging k vignettes shrinks the null spread by roughly
√k, so the aggregate threshold ought to sit below the per-item one. A null
result here would have meant the Group 4 floor was already the binding
constraint and the permutation test was redundant confirmation.

**Outcome: the prediction failed.** perm_floor exceeds the Group 4 floor in
**147 of 240 cells (61%)**, median ratio **1.413**, and all **93** verdict
disagreements run the same way: Group 4 says pass, permutation says fail. The
threshold I expected to be redundant is the binding one in the majority of cells.

**Consequence.** Where the two disagree the larger threshold governs. No effect
is reported as exceeding noise on the Group 4 floor alone. This is a tightening
of the project's own criteria after seeing the data, which is only acceptable
because it runs *against* interest, it can remove findings and cannot create
any.

**Second outcome, not anticipated.** Group 3 has four vignettes, so the smallest
attainable two-sided permutation p is 2/2⁴ = 0.125. **No Group 3 result can
reach α = 0.05 at the current vignette count**, whatever the models do. Observed
p ranges 0.125 to 1.000 across ten models. Reaching 0.05 needs k ≥ 6. This is
now a quantified requirement for a preregistration amendment rather than a
general wish for more data.

## I7, Paraphrase sign stability

**Status:** run 2026-11-07. **Classification:** added disclosure.
**Decision:** D061. **Script:** `scripts/paraphrase_consistency.py`.

**Criterion fixed before the run.** Report, for every cell clearing its own
floor, whether all three paraphrases share the sign of their mean. **No pass
threshold was set, deliberately**, the number is a disclosure requirement, not
a gate, and setting a threshold after seeing it would be the exact failure this
log exists to prevent.

**Outcome.** 61.1% of all 1,920 cells are unanimous in sign; **41.2% have
wording moving the answer more than the gender label does**. Among the 1,260
floor-clearing cells, 75.8% are unanimous, leaving **305 reportable effects that
are not**.

**The uncomfortable part.** On Group 3, OLMo-2-7B base is worst on every measure:
28.3% unanimous overall, 70% swamped by wording, and only **47.1%** of its
floor-clearing effects unanimous. It is one of the three models that passes the
§6 gate and an open-data model the argument depends on. Per-item Group 3 effects
on that model are not stable enough to quote individually.

## I8, Placebo attribute perturbation

**Status:** built 2026-11-07, **scoring pending**. **Classification:** added
threshold. **Decision:** D062.

**Criterion fixed before any scoring.** A gender effect must exceed **both** the
Group 4 floor and the placebo floor. An effect clearing the first but not the
second is recorded as surface-token sensitivity carried by the gender word, not
as a gender effect. Fixed now, before the 216 prompts are scored, so the rule
cannot be chosen to suit the answer.

**Rule 2 compliance.** The placebo runs on the gender-blinded arm of Groups 1, 3
and the original Group 4, which includes sealed hypothesis material. It is
admissible under the I5 amendment because it adds no tunable parameter: it emits
one threshold, and the direction of its effect on conclusions (it can only
remove findings) is fixed in advance by the criterion above.

**Nothing to report yet.** Outcome to be appended after scoring. If the placebo
floor comes out *above* the gender effects on Group 3, that is a finding against
the project and will be recorded as one.

## I9, Guideline contamination audit

**Status:** run 2026-11-07. **Classification:** added disclosure.
**Decision:** D063. **Script:** `scripts/contamination_audit.py`.

**Criterion fixed before the run.** Long spans (≥ 10 tokens) and short spans
(4–7 tokens) read differently; a negative control span, clinical in register but
from no guideline we use, must return non-zero or the probe has no power and the
nulls mean nothing. That power condition was stated first and is the reason the
result is interpretable.

**Outcome.** The negative control returns 1 / 3 / 3 hits across the Pile,
olmo-mix and DCLM, so the probe has power. Long-span contamination in 3 of 24
cells, including **G4-03, one of the two vignettes the binary floor is built
from**. Disclosed; mitigating that G4-03 gave the *larger* floor value, so
memorisation is not making the gate more lenient.

**The finding that changes an interpretation.** For G3-02, which carries H2,
**both spans are zero in all three corpora**. The chest-pain triage decision H2
tests is absent from every training corpus in these terms. A null on H2 is a
**data-absence** result, not a fairness result. That is a reinterpretation of an
existing number rather than a new measurement, and it is the single most useful
thing this round produced.
