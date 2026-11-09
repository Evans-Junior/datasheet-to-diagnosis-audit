# Project documentation: what has been done, what it found, what is left

**From datasheet to diagnosis: tracing gender bias through open training-data
pipelines into LLM health advice.**
Evans Kumi, Aymen Boustani. Written 2026-10-26, at commit `7789641`.

This is the orientation document. It explains the argument, every component built
so far, every result measured, every decision that now constrains the design, and
what remains. `docs/decisions.md` is the authoritative log; this document is the
readable path through it.

---

# 1. The argument, in one page

Most LLM bias audits can only look at outputs, because training data is closed.
Two model families release theirs: **Pythia** (trained on the Pile) and **OLMo 2**
(trained on OLMo-mix-1124). That makes a chain of inference available that other
audits cannot attempt:

> gender skew **in the training data** → gender bias **in model health advice** →
> whether the **datasheet disclosed** that risk

**The design rule everything hangs on.** A gender difference in output is only
bias if the clinically correct answer is the *same* for every patient. Otherwise
you are penalising a model for being right. So every vignette carries a
guideline-sourced reference answer, and vignettes sit on two axes (D002):

|  | Answer should be identical | Answer should differ |
|---|---|---|
| **No documented human bias** | **Group 4**: noise baseline (ankle sprain, conjunctivitis, strep throat) | n/a |
| **Documented human bias** | **Group 3**: the direct bias test (pain, chest pain, ADHD, autism) | **Group 2**: positive control (pregnancy test, prostate, cervical screening) |
| **Routine, sex-neutral** | **Group 1**: main bias test (pneumonia, malaria, asthma, cellulitis, diabetes) | n/a |

Group 2 is the control that makes the whole thing honest: there the answer
*should* differ by sex, so if the audit finds no difference in Group 2, the audit
cannot detect differences at all and every null elsewhere is meaningless.

**What is varied.** Gender identity (man / woman / non-binary / blinded) is
manipulated. **Sex Parameter for Clinical Use (SPCU)**: the HL7 Gender Harmony
Model's term for the sex value a clinician actually needs, is stated explicitly
and held fixed (D001). This is what lets us say "the clinical facts were
identical and only the gender wording changed."

**The six research questions.**

| RQ | Question | Status |
|---|---|---|
| RQ1 | How skewed is gender representation around health concepts in the Pile and OLMo-mix? | **Done** (§5) |
| RQ2 | Do Pythia and OLMo give clinically unwarranted gender differences? | Blocked on vignette content |
| RQ3 | Does the gap change with model size and across training checkpoints? | Code ready, blocked with RQ2 |
| RQ4 | Does data skew predict the size and direction of output gaps? | Feasible, needs RQ2 |
| RQ5 | How does a weights-only model (Qwen3-8B) compare? | Code ready |
| RQ6 | Do the datasheets disclose gender composition and downstream health risk? | Not started |

---

# 2. Where the project stands

| Phase | What it is | Status |
|---|---|---|
| 0 | Environment, repo, resource verification | **Done** |
| 1 | Vignette engine (360 prompts generated) | **Engine done; clinical content missing** |
| 2 | Output scoring (log-probability) | **Code done and tested; cannot run** |
| 3 | Corpus counts (RQ1) | **Done, result in §5** |
| 4 | Linking data skew to output gaps (RQ4) | Not written, needs Phase 2 output |
| 5 | Statistics and figures | Not written |
| 6 | Datasheet audit (RQ6) | Not started |

**The single blocker.** All 360 prompts still contain the literal placeholder
`<<CLINICAL_FINDINGS>>` and `reference_answer: null`. Nothing downstream can run
on real data until the clinical text and reference answers are written. The
scoring code *refuses* to run on them without `--allow-unready`, and tags any
such output `placeholder_text=True` so it can never leak into a result table.

That is deliberate. The alternative, inventing plausible-sounding clinical
findings, would make every number in the paper unsourced.

---

# 3. The design in detail

## 3.1 How a prompt is built

**360 prompts = 15 vignettes × 3 paraphrases × 2 SPCU values × 4 gender arms.**

- **15 vignettes**: 5 in Group 1, 3 in Group 2, 4 in Group 3, 3 in Group 4.
- **3 paraphrases** each, to bound prompt sensitivity. Prompt wording moves LLM
  answers; three phrasings let us report how much.
- **2 SPCU values** (female / male), stated as an explicit sentence
  (`"Sex for clinical use: female."`), crossed with gender identity (D012). This
  is what separates a *sex-parameter* effect from a *gender-identity* effect.
- **4 arms**: `man`, `woman`, `nonbinary`, and `blinded` (D021). The blinded arm
  says "an adult" / "the patient" and carries no gender marking at all. It is the
  reference for how much *any* gender marking moves the answer, and it is never
  pooled with the gendered arms.

Composition as generated: 270 gendered prompts, 90 blinded.

## 3.2 Two things in the design that exist because of near-misses

**Verb agreement per arm (D013).** The first build emitted *"They is a non-binary
person."* Ungrammatical text in the **non-binary arm alone** lowers that arm's
sequence probability for grammatical reasons, not bias reasons, consistently,
across every model and every vignette. It would have manufactured a clean,
publishable, completely false "bias against non-binary patients." Each arm now
carries its own verb forms (`be`, `present_v`, `report_v`, `attend_v`).

**No patient names.** Using names to signal gender would introduce an ethnicity
confound, since names carry both. `name_variant.enabled: false`.

## 3.3 How answers are measured

**Log-probability scoring**, not free generation. For each answer option, one
forward pass computes the model's log-probability of that option's tokens given
the prompt; options are then compared.

Why: it works on **base** models (which cannot follow instructions), it is
**deterministic** (no sampling noise), and it is cheap, one forward pass per
option. The whole scoring design is under an hour of compute.

The score used is **PMI** (pointwise mutual information), not raw
log-probability (D014): raw probability favours options that are simply common
English. `norm_prob` is the softmax over options of their PMI.

**Rationales are a second outcome, not an explanation (D005).** Short generated
justifications are coded for themes, including psychologizing,  by an LLM judge
validated against hand-coding at **Cohen's κ ≥ 0.70**. A model's stated reason is
not evidence of its actual computation, and the paper must not treat it as such.

## 3.4 Models

| Role | Model | Why |
|---|---|---|
| Audit ladder | Pythia 70m → 12b (8 sizes) | Open training data (the Pile); size is the RQ3 axis |
| Checkpoints | pythia-1.4b at 9 log-spaced steps | When during training does a gap appear |
| Audit | OLMo 2 7B base **and** instruct | Second open corpus; base vs instruct = post-training effect |
| Contrast (RQ5) | Qwen3-8B | Strong model, no data access, the comparison most audits are stuck with |
| Judge | Mistral-Small-24B-Instruct, 8-bit MLX | Codes rationales; disjoint from the audited set (D006) |

Hardware: Apple M4 Pro, 48 GB unified memory, **no CUDA**. Execution is strictly
sequential with one model resident at a time (D007), so peak memory is set by the
largest single model rather than their sum. The checkpoint sweep downloads, scores
and deletes each checkpoint: 2.9 GB peak instead of 414 GB.

---

# 4. What has been built

## 4.1 Code

| File | Lines | What it does |
|---|---|---|
| `src/vignettes.py` | 168 | Expands 15 templates × 3 paraphrases × 2 SPCU × 4 arms into 360 prompts; marks each `analysis_ready` or records what it is `blocked_on` |
| `src/score_outputs.py` | 400 | Log-probability scoring, sequential execution, resumable manifest, degeneracy guard |
| `src/corpus_counts.py` | 503 | infini-gram querying, caching, three measurement families, skew computation |
| `scripts/bench_forward.py` | 110 | Measures forward-pass latency for scheduling |
| `scripts/test_scoring.py` | 94 | Regression test guarding the precision fix (D015) |
| `scripts/verify_dois.py` | 92 | Resolves every DOI against CrossRef |

## 4.2 Configuration

- `configs/models.yaml`, the model ladder, dtypes, seed `20261009`, judge spec
  and κ validation plan.
- `configs/gender_arms.yaml`, the four arms with their pronouns **and verb
  forms**, and the two SPCU statements.
- `configs/terms.yaml`, the corpus term lists, the three template families, and
  a `polysemy_excluded` block documenting every term removed and why.
- `data/vignettes/templates.yaml`, the 15 vignettes. **This is the file awaiting
  clinical content.**

## 4.3 Documentation

| File | What it is for |
|---|---|
| `docs/decisions.md` | 26 numbered entries, append-only. Every methodological choice with its reason. The defence document in review. |
| `docs/preregistration.md` | The four confirmatory hypotheses, frozen before any scoring |
| `docs/paper_notes.md` | Narrative for the write-up: contribution claim, related work, difficulties, limitations |
| `docs/vignette_sources.md` | Guideline citation and confidence tier per vignette; the verbatim quote blocks |
| `docs/source_links.md` | A checked link per condition plus what to look for in it |
| `docs/clinical_review_*` | The one-page ask and the reviewer form |
| `docs/outreach_email.md` | Clinician outreach drafts |
| `docs/g303_psychologizing_theme.md` | The psychologizing construct and its literature |
| `AI_USE.md` | The project's disclosure of tool use |

## 4.4 How to run it

```bash
# Smoke-test the pipeline (needs --allow-unready until vignettes are filled)
.venv/bin/python -m src.score_outputs --smoke --allow-unready

# Regression test for the precision fix
.venv/bin/python scripts/test_scoring.py

# Rebuild the prompt set after editing templates.yaml
.venv/bin/python -m src.vignettes --build

# Corpus counts (cached; re-running costs nothing)
.venv/bin/python -m src.corpus_counts --run --family diagnosis
.venv/bin/python -m src.corpus_counts --run --family decision
.venv/bin/python -m src.corpus_counts --run --family explicit
```

---

# 5. Results

## 5.1 RQ1: gender skew in the training corpora, the headline finding

**The measure.** For each health concept, using eight illness-narration frames
("{pron} has", "{pron} was diagnosed with", "{pron} complained of", …):

```
rate(group)  = count("<subject> <frame> <concept>") / count("<subject> <frame>")
skew_log2    = log2( rate(female) / rate(male) )
```

Dividing by the frame's own count is what makes this work. **Raw co-occurrence
counts are worthless here**: "he was anxious" appears 21,073 times against "she
was anxious" 8,723, a ratio of 2.42, and the base rate of "he" versus "she" is
2.421. The entire apparent difference is the pronoun base rate. Normalised skew:
**+0.003**. This is D022, and it is the single most important methodological point
in RQ1.

**The sweep.** 47 concepts × 8 frames × 2 pronouns × 2 corpora =
**1,504 queries, 0 failures**. 76 of 94 rows scored; **42 cleared the power
threshold** (≥100 hits in both arms).

### Validation, does the measure detect what it must?

| Concept | Pile | OLMo-mix | Should be |
|---|---|---|---|
| cervical cancer | **+9.25** | **+7.74** | strongly female |
| prostate | **−6.47** | **−6.07** | strongly male |
| ectopic pregnancy | underpowered | **+4.80** | strongly female |

Sex-specific conditions land where biology puts them, at very large magnitudes.
**Across the 15 concepts powered in both corpora: Pearson r = 0.931,
Spearman ρ = 0.936.** The pattern replicates across two independently constructed
corpora, so it is not an artefact of either one.

### The correction that changes interpretation

Mean skew across **sex-neutral** concepts is **+0.778** (Pile) and **+0.560**
(OLMo-mix), a baseline *female* skew in illness narration, presumably because
narrating illness is itself female-associated in text.

**So zero is not a reference point.** Reading raw signs would have you conclude
that almost every condition is female-skewed. Everything below is centred on each
corpus's own sex-neutral mean.

### The result

Centred skew by concept family. Negative = relatively male-associated.

| Family | OLMo-mix | Pile | Vignettes |
|---|---|---|---|
| neurodevelopmental | **−0.974** | **−0.812** | G3-04, G3-05 |
| cardiac | **−0.929** | **−0.671** | G3-02 |
| other somatic | +0.180 | +0.058 | G1-\*, G4-\* |
| pain | +0.287 | +0.107 | G3-01 |
| **psychological** | **+0.804** | **+0.651** | (no vignette, D020) |

**The ordering is identical in both corpora.** Extremes in OLMo-mix:

| Most male-associated | | Most female-associated | |
|---|---|---|---|
| heart attack | −1.391 | an anxiety disorder | +1.072 |
| attention deficit | −1.157 | panic attacks | +1.032 |
| autism | −1.036 | anxiety | +0.739 |
| angina | −0.946 | a panic attack | +0.646 |
| ADHD | −0.800 | sore throat | +0.620 |

### Why this matters

Each limb matches a **separately documented human clinical bias**:

- **Psychologizing** of women's symptoms, Hoffmann & Tarzian (2001).
- **Cardiac under-recognition** in women, including Dr Louise Pilote's GENESIS
  work at McGill, which is one reason she is on the outreach list.
- **ADHD and autism under-diagnosis** in women and girls, a well-established
  literature.

The corpora reproduce, in text frequency, the shape of biases documented in
clinical practice. That is the finding that makes the data→output chain worth
tracing.

### Limits on this result

- **Co-occurrence is not semantics.** These are phrase frequencies, nothing more.
- **34 of 76 rows are underpowered.** But underpowered is not uninformative:
  *prostate* (Pile: F=8, M=1,718) and *cervical cancer* (F=506, M=2) fail the
  threshold and are the clearest validation signals in the whole sweep. Reported
  separately rather than discarded.
- **Exact phrases miss paraphrase.** The frames are a sample of how illness is
  narrated, not a census.
- **OLMo-mix is stage-1 only.** Stage 2 (`dolmino-mix-1124`) is not indexed by
  infini-gram (D008), so the OLMo link covers pretraining, not the full pipeline.

## 5.2 The pre-registration (D025)

RQ1 produced *signed* skews, which means it produces **directional predictions**
for RQ2 rather than a correlation to be computed afterwards. Those are frozen in
`docs/preregistration.md`:

| | Prediction | Tested on | Corpus basis |
|---|---|---|---|
| **H1** | Δ < 0, less referral for women | G3-04, G3-05 | neurodev −0.97 / −0.81 |
| **H2** | Δ < 0, less urgent triage for women | G3-02 | cardiac −0.93 / −0.67 |
| **H3** | Δ ≈ 0, **no** gap where corpus is unskewed | G1-\*, G4-\* | somatic +0.18 / +0.06 |
| **H4** | sign(Δ) = sign(skew) across concepts | all | n/a |

where Δ = outcome(woman arm) − outcome(man arm) on matched prompt pairs.
Holm–Bonferroni across the four at family-wise α = .05.

**Three things to understand about this document, because they are what a reviewer
will probe:**

**(a) The claim is narrower than "pre-registered".** RQ1 was observed first, that
is the whole point of it. So these are *informed predictions committed before any
analysis-ready score existed*, not blind hypotheses. §1 of the pre-registration
concedes this explicitly and declares the one prior scoring run (the pythia-70m
placeholder smoke test). Stating the limit ourselves costs nothing; being caught
not stating it costs the result.

**(b) H3 is the important one.** If gaps appear on *every* vignette, we have shown
much less than if they appear *only* where the corpus is skewed, the second is a
mechanism claim, the first is just a sentiment. **H3 failing damages the thesis
more than H1 or H2 failing.**

**(c) G3-01 acute pain is a pre-registered divergence.** Our corpus mechanism and
the clinical literature predict **opposite** directions:

- Hoffmann & Tarzian: women receive *less* analgesia → Δ < 0.
- RQ1: pain is mildly *female*-skewed after centring (+0.29 / +0.11; *severe pain*
  reaches +0.63 in OLMo-mix) → Δ > 0.

Both are specified in advance, G3-01 counts as confirmatory for neither, and
whichever way it falls gets reported. A case where our own mechanism makes the
counter-intuitive prediction is worth more to the paper's credibility than a
uniformly supportive result.

## 5.3 Measured performance (Phase 0)

Forward-pass latency, 256-token prompt, bf16 on MPS, 20 trials:

| Model | Params | Weights | Forward pass |
|---|---|---|---|
| pythia-70m | 0.070 B | 0.14 GB | 6.5 ms |
| pythia-160m | 0.162 B | 0.32 GB | 15.5 ms |
| pythia-410m | 0.405 B | 0.81 GB | 39.6 ms |
| pythia-1.4b | 1.415 B | 2.83 GB | 116.7 ms |

Linear at ~83–98 ms per billion parameters, projecting to ~250 ms (2.8b),
~600 ms (6.9b), ~1.05 s (12b). **Download bandwidth, not compute, is the binding
constraint.**

## 5.4 Three proposal assumptions that verification overturned

Worth knowing, because the proposal text still contains them:

1. OLMo 2 is **not** "trained on Dolma". It is two-stage: `olmo-mix-1124` then
   `dolmino-mix-1124`.
2. `dolmino-mix-1124` is **not indexed** by infini-gram, so the data link covers
   stage 1 only.
3. **OLMoTrace has no public API.** Phase 4's document-level tracing is manual
   through the Ai2 Playground (D009), which caps how many examples it can cover.

---

# 6. The four faults that would have produced false findings

These are in the paper's difficulties section because they are the most useful
thing the project has to say about doing this kind of audit. Each one produced
output that looked fine.

## 6.1 bfloat16 silently destroyed every result (D015)

**Symptom:** scoring returned **P(Yes) = 0.500 for every prompt in every arm.** A
perfect, clean null result.

**Cause:** Pythia's output logits reach magnitudes around **1080**. At that
magnitude bfloat16's representable spacing is *wider than the gap between the
" Yes" and " No" logits*, so both rounded to the same number. The model was
computing a difference; the number format was erasing it.

**Fix, in two parts.** First, compute the final projection in float32
(`fp32_head()`). Then the regression test showed that bf16 noise in the model
*body* (0.242 nats) also exceeds the closest option gap (0.140 nats) and can
reverse the ranking, so the whole forward pass moved to float32.

**Why it matters beyond this project:** had this shipped, we would have published
"no gender bias detected," which is a *reassuring* false conclusion. It is guarded
by `scripts/test_scoring.py` and by `_assert_not_degenerate()`, which aborts if
more than half of prompts have all options tied within 1e-9.

## 6.2 Cached rate-limit errors read back as data (D022)

**Symptom:** plausible-looking corpus counts, many of them zero.

**Cause:** infini-gram rate-limits with **HTTP 403** and body
`{"message": "Forbidden"}`. That body has no `"error"` key, so the client treated
it as a successful response, **and cached it.** On every subsequent read it came
back as `cnt = 0`, permanently.

**Scale: 287 of 378 cached entries (76%) were poisoned.** The non-zero rows were
equally worthless, because each was a sum over nine gender terms mixing blocked
and successful queries.

**Fix:** check HTTP status *before* parsing; back off on 403/429/503; **refuse to
cache any response lacking a count field**; count failures per concept; abort the
whole run if any query failed.

## 6.3 `find_cnf` was unusable, and wrong in sign (D023)

The original plan used infini-gram's windowed co-occurrence endpoint. All 125
responses came back `approx=True` (versus 0 of 18 for exact `count`), with clause
frequencies three orders of magnitude above the `max_clause_freq` cap, "he" alone
has 506M occurrences against a 500k cap.

It **disagreed with exact counts in sign**: pneumonia −7.069 vs +2.012,
ADHD +2.808 vs −0.092. Replaced entirely by exact templated n-grams.

## 6.4 Manifest resume kept invalid scores (D025)

**Found 2026-10-26 while checking what state Phase 2 was in.** The resume check
was:

```python
if spec.key in manifest["completed"] and not args.force:
```

So "completed" meant "completed **once**", not "completed for this prompt set".
Once the real clinical findings land, a rerun would have **silently skipped
pythia-70m and kept its placeholder-text scores**, numbers computed from
vignettes with no clinical content and no reference answers, while reporting the
run as complete.

The stale entry was *already* being honoured: the prompt set had changed twice
since that run (G3-03 removed, D020; blinded arm added, D021).

**Fix:** resume only when `prompt_hash`, `score_key` and `placeholder_text` all
match the current run; otherwise rescore and print which field went stale.
Verified on the next run:

```
[1/1] EleutherAI/pythia-70m@main:float32  RESCORE -- stale: prompt_hash: 'ce5964380abd217e' -> 'b6b4d5f06a0925bc'
```

## The pattern across all four

**Two of the four were caches returning something that was never valid.** The
lesson generalises: a cache needs a validity condition checked on **read**, not
only on write. The other two were a number format and an API estimate, in both
cases the code ran without error and produced output in the right shape.

**None of these announced itself.** Every one produced numbers that could have
gone into a paper. That is the argument for the regression test, the degeneracy
guard, the failure counting and the readiness refusal, all of which exist because
one of these got through first.

---

# 7. The decisions that constrain the design

26 entries in `docs/decisions.md`. Grouped by what they govern.

**The sex/gender position**
- **D001** SPCU held fixed, gender identity varied, the core manipulation.
- **D012** SPCU crossed with gender identity; no patient names (ethnicity confound).
- **D011** Sex-invariance judged once, globally, by the reviewer, not per vignette.
- **D018** Pregnancy excluded in identical wording across arms, so it cannot be a
  hidden cue.

**The vignette set**
- **D002** The 2×2 frame (bias documented × answer should differ).
- **D003** Tiered reference answers; nothing invented to fill a row.
- **D016** Where guidelines conflict, the most recent one governs.
- **D017 / D017a** G2-01's pregnancy-test decision, approved and verified against
  NICE NG126, which turned out to state trans-inclusive scope outright.
- **D019** PSA decision replaced; G3-06 chronic pain dropped.
- **D020** G3-03 psychologizing dropped as a vignette (no guideline says "do not
  attribute this to anxiety"), retained as a rationale code.
- **D021** The gender-blinded reference arm.

**Measurement**
- **D013** Verb agreement per arm, the grammaticality confound.
- **D014** PMI scoring, not raw log-probability.
- **D015** float32 throughout.
- **D022** Base-rate normalisation is mandatory; two infini-gram traps.
- **D023** Exact templated n-grams, not windowed co-occurrence.
- **D024** The full sweep result; skew must be centred within corpus.
- **D026** Non-binary arm measured; decision concepts promoted (see §8).

**Execution and infrastructure**
- **D004** OLMo 2 base + instruct; no reasoning model in the audit set.
- **D005** Rationales are a second outcome, not an explanation.
- **D006** Judge disjoint from the audited models.
- **D007** Strictly sequential execution with explicit memory release.
- **D008** OLMo-mix-1124, not Dolma; stage 1 only.
- **D009** OLMoTrace is manual.
- **D010** Judge at 8-bit; κ reported at both precisions.
- **D025** Pre-registration; manifest staleness fix.

---

# 8. Two measurement gaps closed (D026)

Both of these were previously written up as *limitations*. On inspection both were
fixable, and a limitation you can measure instead of asserting is worth measuring.

## 8.1 The non-binary arm was never measured

**The gap.** RQ2 has a non-binary output arm; RQ1 had **no** non-binary corpus
measure at all. Since the non-binary arm is part of the project's novelty claim,
that asymmetry sat exactly where the contribution is.

**Why it was skipped.** `"they has"` is ungrammatical, so the non-binary arm
cannot use the same eight frames, the same confound as D013, but in the corpus
measure instead of the prompts. And `"they"` in corpus text is overwhelmingly
**plural**, so counting it does not isolate non-binary reference.

**What was built instead, two measures, honestly labelled:**

1. **`phrase_templates_plural`**: the same eight frames, plural inflection
   (`"they have"`, `"they were diagnosed with"`). This *is* measured now, and its
   skew is reported but **never interpreted as a non-binary result**, because the
   plural contamination is real. The point of measuring it is to quantify the
   contamination rather than assert it.
2. **`explicit_subjects`**: the actually valid comparison. Noun subjects, singular
   frames, no pronoun ambiguity whatsoever: `"the woman has X"` vs `"the man has
   X"` vs `"the non-binary patient has X"`.

Note on term choice: `"the transgender patient"` is deliberately **excluded**.
Trans and non-binary are different constructs, and pooling them to inflate a thin
count would misreport both. If the trans arm is wanted, it gets its own group.

**The expected outcome is near-zero counts, and that is a result.** Non-binary
health narration being near-absent from both open corpora is a substantive
finding about the corpora, and one that bears directly on the ethics argument,
not a failed measurement. The code says so explicitly when it happens.

## 8.2 The corpus measured diagnoses; the hypotheses are about decisions

**The gap.** H1 is about **referral for assessment**; H2 is about **triage
urgency**. The diagnosis family measures only which *conditions* attach to which
gender. So the corpus basis for the two directional hypotheses was one inferential
step removed from what RQ2 actually scores.

**Why it was deferred.** Decision language does not fit the diagnosis frames,
nobody "has an x-ray" in the diagnostic sense, so it needs its own templates.

**What was built:** a `decision` family with six frames
(`"{pron} was referred for"`, `"{pron} was referred to"`, `"{pron} underwent"`,
`"{pron} was prescribed"`, `"{pron} was given"`, `"{pron} was admitted"`, plus
plural forms) over 14 decision concepts spanning investigations (x-ray, CT,
ultrasound, blood tests, ECG, specialist, psychiatrist, cardiologist) and
treatments (antibiotics, painkillers, morphine, antidepressant, physiotherapy,
surgery).

**Expect this one to be underpowered.** The probe gave
`"he was referred for an x-ray"` = 13 hits and the female arm 6, in the Pile.
These phrases are far rarer than diagnosis phrases. OLMo-mix is roughly 17× larger
and may clear the threshold; the Pile probably will not. That is worth knowing
either way, if the decision family cannot be powered, the paper must say H1 and
H2 rest on *diagnosis* skew with decision skew as an inferential step, rather than
implying direct measurement.

## 8.3 How the sweeps are now organised

`src/corpus_counts.py` gained a `--family` switch and measures all three gender
groups rather than two:

| Family | Frames | Concepts | Purpose |
|---|---|---|---|
| `diagnosis` | 8 illness-narration | 47 health + psychologizing | The §5.1 headline result |
| `decision` | 6 referral/treatment | 14 decision | Direct corpus basis for H1, H2 |
| `explicit` | 8, noun subjects | 47 health + psychologizing | The valid non-binary comparison |

Each family writes its own CSV, so families can never overwrite one another. The
female-vs-male skew stays in `skew_log2` for comparability with the published
§5.1 numbers; the non-binary arm adds separate columns
(`cooccur_nonbinary`, `rate_nonbinary`, `skew_nb_vs_female`, `skew_nb_vs_male`,
`nb_powered`) and is **never folded into** that number. Two skews are reported
rather than one average, because there is no single "other" to compare against and
averaging would hide a non-binary rate that sits outside both.

## 8.4 Results of the three sweeps

Run 2026-10-26. **2,436 further queries, 0 failures.**

### The non-binary finding: zero, and verified as a real zero

The explicit noun-subject family returned **0 non-binary hits across all 94
concept-corpus rows in both corpora**, and the reason is upstream of the
concepts. The *frames themselves* never occur:

| Probe | OLMo-mix | Pile |
|---|---|---|
| `the non-binary patient` | **0** | **0** |
| `the nonbinary patient` | 1 | 0 |
| `the non-binary patient has` | **0** | **0** |
| `the transgender patient has` | 53 | 2 |
| `the woman has` | 646,440 | 20,142 |
| `the man has` | 1,139,475 | 37,323 |
| `the female patient has` | 679 | 33 |
| `non-binary` (bare term) | **1,350,944** | **66,269** |

The last row is what makes this a finding rather than a vocabulary gap. Non-binary
people are **not absent from these corpora**: the term appears over 1.35 million
times in OLMo-mix. They are absent from the **clinical subject position**. In two
corpora totalling trillions of tokens, the phrase "the non-binary patient" occurs
zero times, against 646,440 occurrences of "the woman has".

**This zero was verified by direct probe before being reported.** A zero from this
API is exactly what D022 was: a rate-limit error cached as data. The probe above
was run against the live endpoint with a bare-term control that returns large
non-zero counts, so the pipeline was working when it returned the zeros.

For the write-up, this belongs in the ethics argument, not the limitations. A model
cannot have learned how to narrate a non-binary patient's illness from training
data that never does so. The downstream prediction, that non-binary arm outputs
will be less stable and less guideline-concordant than either gendered arm, now
has a stated basis, though it is **not** pre-registered as confirmatory, because
the measure arrived after D025 was frozen.

### The plural contamination, now quantified rather than asserted

The `they` arm in the diagnosis family is powered (40 of 94 rows, 298,440 hits),
and it is just as plural-dominated as predicted:

| | OLMo-mix | Pile |
|---|---|---|
| `they have anxiety` | 24,307 | 317 |
| `she has anxiety` | 9,474 | 202 |
| frame base, `they` arm | 747,228,476 | 28,109,594 |
| frame base, `she` arm | 266,261,215 | 16,790,889 |

The `they` frames are **more** frequent than the `she` frames, which no account of
non-binary reference can explain. So the arm is measured, reported, and explicitly
not interpreted as a non-binary result, which is the whole reason for building the
explicit family alongside it.

### The decision family: powered in OLMo-mix, and it supports H1 and H2

13 of 14 concepts powered in OLMo-mix. Centred on the decision-frame mean
(+1.038), negative = relatively male-associated:

| Concept | Centred | Concept | Centred |
|---|---|---|---|
| surgery | **−0.881** | a psychiatrist | +0.127 |
| **a cardiologist** | **−0.811** | a CT scan | +0.163 |
| an x-ray | −0.496 | **an antidepressant** | **+0.306** |
| morphine | −0.323 | a specialist | +0.353 |
| painkillers | −0.279 | blood tests | +0.690 |
| physiotherapy | −0.148 | an ultrasound | +1.412 |
| antibiotics | −0.115 | | |

Underpowered but same direction: `an ECG` raw −0.695 (F=48, M=199).

**The informative contrast is cardiologist vs psychiatrist**: −0.811 against
+0.127, a gap of 0.94 log2 units, roughly **1.9×**. Referral to cardiology is
male-associated; referral to psychiatry and prescription of antidepressants are
female-associated, *in the referral language itself*, not merely in which
diagnoses attach to which gender.

This is the corpus basis H1 and H2 were missing. It is also the psychologizing
pattern appearing at the decision level, which matters because psychologizing has
no vignette (D020) and was otherwise only measurable through rationale coding.

**Two constraints on how far this can be pushed:**

1. **No cross-corpus replication.** The Pile powered only 2 of 14 decision
   concepts (`surgery` −0.540, `antibiotics` +0.540 centred). The decision family
   is effectively an **OLMo-mix-only** result, so it cannot carry the r = 0.931
   replication claim that §5.1 can. The paper must report it as single-corpus.
2. **The centring base is weaker here.** §5.1 centres on sex-neutral concepts
   within a large pool; this centres on the family mean of 13 concepts that are
   themselves the measured set. Directional contrasts *within* the family (the
   cardiologist/psychiatrist gap) are the defensible reading; absolute centred
   values are not.

### Summary of all three sweeps

| Family | Queries | Powered (F/M) | NB powered | Usable? |
|---|---|---|---|---|
| `diagnosis` | 1,504 | 42 / 94 | 40 (plural-contaminated) | **Yes**: the headline result, replicated across corpora |
| `decision` | ~560 | 15 / 28 | 8 | **Yes, OLMo-mix only**: direct basis for H1, H2 |
| `explicit` | ~1,880 | 2 / 94 | **0** | As a *presence* measure, yes, the zero is the finding. As a skew comparison, no: too sparse. |


---

# 9. What is left, and who owns it

## 9.1 Yours, the critical path

Everything downstream is blocked on the first two.

| # | Task | Why it blocks |
|---|---|---|
| 1 | **Write clinical findings + reference answers** into `data/vignettes/templates.yaml`, then `--build` | All 360 prompts are placeholders. Phase 2 cannot run. |
| 2 | **Quote the governing recommendation verbatim** into the 14 remaining blocks in `docs/vignette_sources.md` | G2-01 is done as the worked example. Without these, reference answers are unsourced. |
| 3 | **Read G3-02's AHA/ACC sex-differences section early** | If it recommends anything sex-differentiated, G3-02 becomes a Group 2 control, H2 is withdrawn, and Group 3 drops to three items. This changes the design, so do it before writing content. |
| 4 | Send the five clinician outreach emails | The sex-invariance review (D011) is the one judgement we cannot make ourselves |
| 5 | Decide G2-02's final prostate decision | CUA and the Canadian Task Force disagree; a control needs one correct answer |
| 6 | Pin the WHO malaria guideline version | Living guideline, no stable DOI |
| 7 | Confirm NICE review dates for CG142 and NG193 at source | NICE's own pages disagree |
| 8 | Read both ED-triage preprints in full | Decide whether to adopt a pre-registered flip-rate metric |
| 9 | Confirm McGill's AI-use disclosure wording against `AI_USE.md` | Graded submission |

## 9.2 Still to build

| Component | Depends on |
|---|---|
| `src/stats.py`, the §7 analysis plan from the pre-registration | Phase 2 output |
| `src/link_analysis.py`, RQ4 linkage | Phase 2 output + §5.1 (done) |
| `src/plots.py`, figures per RQ | stats |
| `docs/codebook.md`, RQ6 datasheet audit codebook | nothing; can start now |
| Judge validation harness, κ against two hand-coders | rationale generation |
| pythia-6.9b float32 vs float16 sensitivity check | nothing; can run now |

## 9.3 Open questions with no answer yet

- Does post-training amplify or attenuate the gap? (OLMo 2 base vs instruct.) A
  genuine open result, not a confirmation.
- Do rationales diverge by gender even where the log-probability answer does not?
  That dissociation would deserve its own section.
- Keep PSA screening and make the CUA/CTFPHC disagreement a finding in its own
  right, or pick an uncontested prostate decision?

---

# 10. How to read a result from this pipeline without fooling yourself

The five checks, in order. Each exists because something went wrong.

1. **Is it tagged `placeholder_text=True`?** Then it is not a result. The vignettes
   had no clinical content.
2. **Did any query fail?** `corpus_counts` aborts the run if so, because a partial
   sum over gender terms makes the ratio meaningless (D022).
3. **Is it powered?** `powered=False` means under 100 hits in an arm. Report it
   separately, do not discard it, the two clearest validation signals in RQ1 are
   both underpowered.
4. **Is it centred?** Raw corpus skew is contaminated by a baseline female skew of
   +0.56 to +0.78 in illness narration. An uncentred sign is not interpretable
   (D024).
5. **Did Group 2 move?** If the positive control shows no gender effect, the
   instrument is insensitive and **no null anywhere else means anything**,
   including H3, which means the mechanism claim cannot be made in either
   direction. This is reported first, before any other result.

And one standing rule for the write-up: **where a corpus finding is strong but the
corresponding output test is weak, say so.** Psychologizing is the clearest case,
the largest effect in RQ1 (+0.80 / +0.65), but it has no vignette, so it is
reachable only through judge-dependent rationale coding. The corpus finding must
not be allowed to stand in for an output finding.
