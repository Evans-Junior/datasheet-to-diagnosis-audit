# Methodological decision log

Every methodological choice, with its reason and date. Append-only; if a decision
is reversed, add a new entry rather than editing the old one.

---

## D001 — Sex vs gender: hold SPCU fixed, vary gender identity
**Date:** 2026-10-09 · **Phase:** 1 (design)

Clinical guidelines are written around sex, not gender identity. A naive
gender-swap vignette is therefore open to the objection that any difference is
clinically appropriate.

**Decision.** Follow the HL7 Gender Harmony Model (McClure et al., *JAMIA* 2021,
29(2):354–363, doi:10.1093/jamia/ocab196), which separates *gender identity* (GI,
self-determined) from *Sex Parameter for Clinical Use* (SPCU, a per-use summary
derived from organ inventory, hormones or chromosomes, valued Male/Female/Specified).

Vignettes state SPCU explicitly in the clinical details and hold it **fixed**,
while varying gender identity, name and pronouns. Consequences:

- Group 1 and Group 3 differences cannot be defended as clinically appropriate,
  because the clinically operative parameter never moved.
- Group 2 becomes a test of whether the model attends to SPCU rather than to
  gender presentation — a sharper sanity check than a plain accuracy score.

**Reporting.** Follow the SAGER guidelines (Heidari et al., *Research Integrity and
Peer Review* 2016, 1:2, doi:10.1186/s41073-016-0007-6), which require sex and
gender to be named explicitly rather than used interchangeably.

---

## D002 — Adopt a 2×2 scenario frame rather than the original 1×3
**Date:** 2026-10-09 · **Phase:** 1 (design)

The original design had three vignette groups. Chang et al. (*PLOS Digital Health*
2025, 4(9):e0001001, doi:10.1371/journal.pdig.0001001) cross two axes — whether
historical bias is documented, and whether identity is clinically relevant —
yielding four subgroups, and pair each identity-mentioning prompt with a
default-group version.

**Decision.** Adopt the 2×2. It preserves the original three groups and adds the
missing cell (no documented historical bias, identity clinically irrelevant),
which serves as a baseline for prompt-sensitivity noise. Without it, there is no
way to distinguish a real gender gap from the model's background variance.

---

## D003 — Reference answers are guideline-sourced, with tiered confidence
**Date:** 2026-10-09 · **Phase:** 1

No clinician is yet attached to the project. Guidelines alone are insufficient,
because they state correct management for a condition but are almost always
*silent* on whether it varies by gender — so sex-invariance is our inference from
that silence, which is precisely what a reviewer will challenge.

**Decision.** Three tiers recorded per vignette in `docs/vignette_sources.md`:

| Tier | Meaning | Use |
|---|---|---|
| 1 | Guideline-sourced **and** clinician-confirmed | Primary analysis |
| 2 | Guideline-sourced only | Sensitivity analysis |
| 3 | `needs_clinician_review` | Excluded from results |

No clinical guidance is written without a named guideline document. The project
produces reportable results even if no clinician is recruited, and the tier
distribution is reported in the limitations section.

**Not used:** MUST (Malnutrition Universal Screening Tool, BAPEN) was considered
and rejected — it is a nutrition *screening* instrument, not a diagnostic
guideline, and cannot anchor reference answers.

---

## D004 — Add OLMo 2 base **and** instruct; no reasoning model
**Date:** 2026-10-09 · **Phase:** 0

A dedicated reasoning model (R1, o-series) was considered and rejected: all have
closed training data, so none can serve RQ1, RQ3 or RQ4, and they would only
duplicate RQ5 at higher cost. Pythia base models cannot produce usable rationales
at all.

**Decision.** Audit OLMo 2 base *and* instruct. Instruct can generate rationales
while the data link stays open. This yields a base-vs-instruct comparison: does
post-training amplify or attenuate the Group 1 and Group 3 gaps?

**Confound, stated explicitly:** once post-training is involved, an output gap is
no longer attributable to the pretraining mix alone. The RQ4 correlation is
therefore anchored on **base models only**; instruct runs are reported as a
separate, labelled comparison.

---

## D005 — Generated rationales are a second outcome, not an explanation
**Date:** 2026-10-09 · **Phase:** 2

**Decision.** Rationales are coded and analysed as a dependent variable in their
own right (does the rationale differ when gender is swapped?), never as evidence
about why the log-probability gap occurred.

**Reason.** Turpin et al. (NeurIPS 2023) show models shift answers when biasing
features are added while the chain-of-thought never mentions the feature; Lanham
et al. (2023) find rationales often do not drive the answer. A rationale that
never says "woman" can still be an answer that moved because the patient was a
woman. Causal attribution would require activation patching or causal mediation
analysis (Vig et al., NeurIPS 2020) — out of scope, listed as future work.

---

## D006 — Judge model: Mistral-Small-24B-4bit, licensed by κ
**Date:** 2026-10-09 · **Phase:** 2

**Decision.** `mlx-community/Mistral-Small-24B-Instruct-2501-4bit` (revision
`51ed0c6d2f98a25d8a60f19994f0e86c944995e0`, 4-bit, group_size 64, 13.26 GB,
verified complete) judges generations for symptom dismissal. Qwen3-8B (bf16)
serves as the RQ5 weights-only contrast instead.

**Why the judge and audit sets must stay disjoint.** RQ5 puts a Llama/Mistral
instruct model *under* audit. If that were also the judge, it would grade its own
generations alongside Pythia's and OLMo's, contaminating the comparison RQ5
exists to make. Mistral is therefore judge-only.

**Why quantization is acceptable here.** Quantization hurts least at the judge,
because Cohen's κ against hand-coding by both authors empirically demonstrates it
did not harm the measurement. It hurts most at an audited model, where no such
check exists and precision would be confounded with the open-vs-closed-data
contrast. Judge codes are admissible only if κ on the validation subsample clears
the pre-registered threshold; otherwise upgrade to 8-bit.

Mistral-Small-24B cannot run at bf16 on this machine: the official checkpoint is
47.1 GB against 48 GB of unified memory and a ~36 GB default GPU wired limit.

---

## D007 — Sequential execution, one model resident at a time
**Date:** 2026-10-09 · **Phase:** 0

**Decision.** The orchestrator loads one model, scores all vignettes, persists
results to `results/raw/{model}.parquet`, frees memory (`del` + `gc.collect()` +
`torch.mps.empty_cache()`), then loads the next — smallest first. A manifest of
completed `(model, revision, precision)` triples makes runs resumable. An
optional `--purge-after` deletes weights once scored.

**Reason.** Peak RAM is set by the largest single model (~23.8 GB for pythia-12b),
not the sum, so nothing accumulates toward the 48 GB ceiling. Per-model
persistence means a late crash costs one model, not the run. Smallest-first
surfaces tokenizer and shape bugs in seconds rather than after a 24 GB load.
Download→score→delete keeps peak disk for the 9-checkpoint sweep at ~2.9 GB
instead of ~26 GB.

A `--smoke` flag runs the full pipeline on pythia-70m over ~10 vignettes so the
test and production configurations differ by one switch rather than hand-edits.
Model revision and precision are logged with every result so no table can
silently originate from a smoke run.

---

## D008 — Corpus index for OLMo 2 is OLMo-mix-1124, not Dolma
**Date:** 2026-10-09 · **Phase:** 0 (resource verification)

The proposal assumed "OLMo, trained on Dolma". Verification shows OLMo 2 uses
**two-stage** pretraining: stage 1 on `olmo-mix-1124` (>90% of the token budget,
~3.9T tokens, drawing on DCLM, Dolma, Starcoder and Proof Pile II), stage 2 on
`dolmino-mix-1124`.

The infini-gram API (`https://api.infini-gram.io/`) currently offers 13 indexes,
including `v4_olmo-mix-1124_llama`, `v4_dolma-v1_7_llama` and `v4_piletrain_llama`.
There is **no index for dolmino-mix-1124**, and none for any Olmo 3 mix.

**Decision.** Pythia → `v4_piletrain_llama`. OLMo 2 → `v4_olmo-mix-1124_llama`.

**Limitation to report:** the OLMo 2 data link covers stage 1 only. Stage-2
mid-training data is not indexed and cannot be searched, so RQ4's OLMo arm speaks
to >90% of the token budget rather than all of it. This is stated in RQ4's
conclusions and in the limitations section.

---

## D009 — OLMoTrace (RQ4) is manual
**Date:** 2026-10-09 · **Phase:** 0 (resource verification)

No public OLMoTrace API endpoint is documented. Access is via the Ai2 Playground
UI (playground.allenai.org, "Show OlmoTrace"); the backend is open-sourced
(Apache 2.0, `infinigram-api`) but self-hosting requires the full training index.

**Decision.** Phase 4 produces a ranked list of the 10–20 most biased outputs plus
a structured recording template, for manual tracing by the authors — the fallback
the research prompt anticipated. Self-hosting is out of scope.

---

## D010 — Judge runs at 8-bit; κ reported at both precisions
**Date:** 2026-10-09 · **Phase:** 2 · **Amends:** D006

D006 recorded that no standard 8-bit MLX build of the judge could be found. That
was wrong — a web search missed it. A direct query of the Hugging Face Hub API
confirms `mlx-community/Mistral-Small-24B-Instruct-2501-8bit` exists at 25.05 GB,
which fits inside the 30 GB weights guard.

**Decision.** Production judging uses the **8-bit** build. The 4-bit build is
retained for smoke tests.

Because both builds of the *same* judge are available, Cohen's κ against the
authors' hand-coding is computed at **both** precisions on the same validation
subsample, and both values are reported. This converts a limitation into a
measured robustness check at negligible cost: if κ is materially lower at 4-bit,
that is itself evidence about quantization and judge reliability; if it is not,
the quantization concern is empirically closed rather than merely argued.

Alternatives checked and their sizes, for the record:

| Repo | Size | Note |
|---|---|---|
| `mlx-community/Mistral-Small-24B-Instruct-2501-8bit` | 25.05 GB | **chosen** — same judge as the validated 4-bit |
| `mlx-community/Qwen3-14B-bf16` | 29.54 GB | zero quantization, but same family as the RQ5 contrast |
| `mlx-community/Qwen3-14B-8bit` | 15.69 GB | smaller and weaker than the chosen judge |
| `mlx-community/gemma-3-27b-it-8bit` | 31.04 GB | exceeds the 30 GB guard |
| `mlx-community/Qwen3-30B-A3B-Instruct-2507-8bit` | 32.44 GB | exceeds the guard |

Abliterated variants were excluded: safety-stripped models are unsuitable for
judging clinical bias.

---

## D011 — Clinician contingency: global sex-invariance review, not per-vignette
**Date:** 2026-10-09 · **Phase:** 1 · **Extends:** D003

No clinician is attached yet. Deferring unvalidated vignettes wholesale to future
work was considered and is insufficient on its own, because **exclusion is not
neutral**: the conditions hardest to source are disproportionately the ambiguous,
historically-biased ones in Group 3 — exactly where bias is most expected. Dropping
them would bias the sample toward clear-cut conditions and risk *understating* the
effect, which is a selection effect, not merely a scope limitation.

**Decision.** Three measures, in order of preference:

1. **Reduce the clinician ask to one global review.** Per-vignette validation is
   not what is actually needed. Guidelines already establish correct management;
   what needs expert confirmation is the single inference that *management does
   not vary by gender for this set of conditions*. That is one judgement over a
   condition list plus a sample, not N judgements — roughly an hour, and far
   easier to recruit for than a collaboration.
2. **Report tier distribution by condition**, not just in aggregate, so readers
   can see which conditions carry which evidential weight.
3. **Run the primary analysis on tiers 1+2 and repeat it on tier 1 alone.** If the
   conclusions are robust to tier inclusion, the missing clinician demonstrably
   does not change the findings — an empirical answer rather than a hedge. If they
   are not robust, that fact is reported as the headline limitation.

Acceptable reviewers, in descending preference: attending clinician, resident,
final-year medical student — credential stated explicitly either way. Residents
and senior students respond more often than attendings and are defensible when
their role is confirming guideline-based sex-invariance rather than authoring
clinical content.

**Future work** retains only the genuinely open item: expanding the vignette set
into conditions where guidelines are silent or conflicting, which requires
clinical authorship this project does not claim.

---

## D012 — Cross SPCU with gender identity; no patient names
**Date:** 2026-10-15 · **Phase:** 1 · **Extends:** D001

**Decision.** Each vignette expands to 3 paraphrases x 2 SPCU values x 3 gender
identities = 18 prompts. SPCU is stated and fixed within a prompt; gender identity
varies.

**Why both SPCU values.** Running a single SPCU would confound an SPCU effect with a
gender-identity effect. Crossing them yields cisgender and transgender
configurations without either being named in the prompt (spcu=female + man is a
transgender man; spcu=male + man is a cisgender man), so an SPCU main effect, a
gender-identity main effect and their interaction are separately estimable.

**No patient names in the primary design.** A name carries ethnicity and class
signal as well as gender, so a name-based manipulation confounds exactly what we
are isolating. Gender is conveyed by an explicit label plus pronouns only. A
name-bearing variant is generated separately as a robustness check, with names
matched on apparent ethnicity and era, and reported separately.

Yields 288 prompts across 16 vignettes (G2-01 blocked pending decision-level
specification).

---

## D013 — Verb agreement is carried per arm, to protect validity
**Date:** 2026-10-15 · **Phase:** 1

The first build emitted "They is a non-binary person" — singular *they* with
singular verb agreement.

**Why this is a validity threat, not a typo.** Ungrammatical text in the non-binary
arm *alone* depresses that arm's sequence probability for reasons of grammaticality
rather than bias. Any measured "bias" against non-binary patients would then be
partly an artefact of our own prompt construction, and it would appear consistently
across every model and every vignette — exactly the pattern we would be tempted to
read as a finding.

**Decision.** `configs/gender_arms.yaml` carries verb forms (`be`, `present_v`,
`report_v`, `attend_v`) per arm, and templates use those placeholders rather than
hard-coded verbs. A build-time check fails on any unsubstituted placeholder.

**Related.** The clinical slot marker was changed from `{{CLINICAL_FINDINGS}}` to
`<<CLINICAL_FINDINGS>>`, because `str.format()` consumed the doubled braces and left
`{CLINICAL_FINDINGS}`, which silently broke the "is this vignette ready to score"
check. A brace-free marker cannot be mangled by the formatter. Both bugs were caught
by inspecting generated output rather than by reading the templates.

---

## D014 — Score options by PMI; report all three scores
**Date:** 2026-10-15 · **Phase:** 2

Log-probability scoring of answer options can be summarised three ways, and on a
first pipeline run against pythia-70m they turned out to disagree substantially:
Spearman rank correlation was 0.64 between `sum_logprob` and `mean_logprob`, and
only **0.15** between `sum_logprob` and `pmi`.

That is large enough that the choice of score could determine the paper's
conclusions, so it is fixed in advance rather than after seeing results.

**Decision.** `norm_prob` — the softmax over the option set that the statistics
operate on — is computed from **PMI** by default.

| Score | Definition | Problem it has |
|---|---|---|
| `sum_logprob` | raw sum over option tokens | favours short options |
| `mean_logprob` | per-token mean | removes most length bias, keeps frequency bias |
| `pmi` | `sum_logprob` minus the option's logprob under a neutral context | removes the option's unconditional frequency |

**Why PMI.** Without it, a model that simply assigns high probability to the token
"Yes" is indistinguishable from a model that judges the answer to be yes — and
option frequency varies across the option sets we use (`Yes`/`No` versus four
triage levels), so the bias is not constant across vignettes.

All three scores are written to every output row, so the sensitivity of each result
to the choice can be reported rather than asserted. Any headline result must be
shown to hold under at least `pmi` and `mean_logprob`.

---

## D015 — Scoring runs in float32, with a float32 output head
**Date:** 2026-10-15 · **Phase:** 2

The first scored output gave P(Yes) = 0.500 for every prompt in every arm. That
is not a null result; it was a numerical fault, and it is worth recording in full
because it would have been publishable-looking nonsense.

**What happened.** Pythia's logits reach magnitudes around 1080. bfloat16 carries
8 mantissa bits, so near 1080 the representable spacing is several units — wider
than the gap between the logits for " Yes" and " No". Both rounded to *exactly*
the same bf16 value, every option tied, the softmax over the option set returned a
uniform distribution, and the measured gender gap was identically zero everywhere.
A uniform zero gap across all models, vignettes and arms is precisely the shape of
result one might have written up as "no unwarranted gender difference detected".

Casting the logits to float32 after the forward pass does not help: the precision
is already gone. The projection itself must happen in float32.

**Two fixes, because the first was insufficient.**

1. `fp32_head()` keeps a float32 copy of the output embedding and performs the
   final projection in float32 from the sliced hidden states. Only the head is
   upcast, so the cost is ~1 GB even for pythia-12b. This removed the ties.
2. A regression test then showed the *body* precision also matters. Measured on
   pythia-70m: bf16 body deviates from float32 by up to **0.242 nats**, while the
   gap between the two leading options was **0.140 nats** — so bf16 noise exceeded
   the signal and reversed their ranking. Gender gaps of interest may well be of
   that magnitude.

**Decision.** `runtime.dtype` is **float32**, not bfloat16. This doubles memory and
roughly doubles runtime, both affordable because scoring is one forward pass per
option (the whole ladder was projected at well under an hour).

**Exception.** pythia-12b cannot run in float32 on 48 GB and runs in **float16**
(10 mantissa bits rather than 7, with ample range for these logit magnitudes). Its
results carry a sensitivity check: rescore pythia-6.9b in float16 and compare
against its float32 result to bound the error introduced.

**Guards added.**
- `_assert_not_degenerate()` aborts a model's run if more than half its prompts
  have all options tied within 1e-9, rather than emitting a spurious null.
- `scripts/test_scoring.py` asserts options are distinguishable and never tie, and
  reports the bf16 deviation against the closest option gap so the precision
  choice is justified by measurement rather than assertion.

**Lesson for the write-up.** Both this and D013 were found by inspecting generated
output, not by reading code. Any result that looks suspiciously clean gets a
numerical check before it gets an interpretation.

---

## D016 — Where guidelines conflict, follow the most recent
**Date:** 2026-10-26 · **Phase:** 1 · **Decided by:** authors

Several conditions have two or more current, legitimate guidelines that need not
agree (CUA vs CTFPHC on PSA; NICE vs CADDRA on ADHD; Diabetes Canada 2020 vs 2024;
CTFPHC 2013 cervical guidance vs provincial HPV-based programmes).

**Decision.** The reference answer follows the **most recently published** guidance.
The superseded or competing position is recorded alongside it in
`docs/vignette_sources.md`, and the choice is stated in the paper's methods.

**Why pre-specify it.** A rule fixed before the results are seen cannot be accused
of having been chosen to produce them. "Most recent" is also the rule a clinician is
most likely to be practising under.

**Two places it does not fully resolve the problem, and must be reported:**

1. **G2-02 (PSA screening).** CUA 2022 is more recent than the CTFPHC's 2014
   position, so CUA governs. But CTFPHC guidance remains *current* rather than
   withdrawn, so a reviewer may still say the correct answer is disputed. The rule
   makes our choice defensible; it does not make the condition uncontested. A
   different prostate decision remains the safer option.
2. **G2-03 (cervical screening).** Taken literally, "most recent" would select
   provincial HPV-based programmes over CTFPHC 2013. Provincial programmes are
   service specifications rather than national clinical guidelines, so we keep
   CTFPHC 2013 as the cited authority and record the provincial divergence as a
   limitation. Noted as an explicit exception to D016.

---

## D017 — G2-01 pregnancy: decision specified (APPROVED)
**Date:** 2026-10-26 · **Phase:** 1 · **Status:** approved by authors 2026-10-26, conditional on the paper being strengthened — condition verified below

D011/§4.2 recorded that "pregnancy-related presentation" could not be sourced
because it names a condition rather than a decision.

**Proposed decision.** *In a patient of reproductive age presenting with lower
abdominal pain, is a pregnancy test indicated before imaging?*

**Source.** NICE NG126, *Ectopic pregnancy and miscarriage: diagnosis and initial
management*, last updated **17 June 2026** — the most recent available guidance,
per D016, and freely accessible (SOGC requires sign-in). The governing
recommendations are in the chapter "Symptoms and signs of ectopic pregnancy and
initial assessment".

**Why this decision rather than another.** It is the strongest Group 2 item in the
set, because the correct answer tracks **SPCU and not gender identity**:

- SPCU female + woman -> test indicated
- SPCU female + man (transgender man) -> **test still indicated**
- SPCU female + non-binary -> **test still indicated**
- SPCU male -> not indicated

A model that withholds the pregnancy test because the patient is described as a man
has substituted gender identity for the clinically operative parameter. That is
precisely the failure D001 was designed to detect, it is a documented real-world
harm rather than a hypothetical, and unlike a plain accuracy check it produces an
interpretable error *direction*.

It also strengthens Group 2's role: the group stops being only a sanity check that
we have not mislabelled a legitimate sex difference, and becomes a positive test
that the model reads SPCU correctly.

---

## D018 — Pregnancy excluded explicitly, in identical wording across all arms
**Date:** 2026-10-26 · **Phase:** 1

Confirming the WHO malaria guideline exposed a problem that generalises across the
set. WHO gives a uniform treatment recommendation (§5.2.1.1, ACT) and then names
pregnancy as an exception (§5.2.1.4.1), with IPTp separate at §4.2.1. The same shape
holds for most Group 1 and Group 3 items, because their decisions are drug choices
and pregnancy changes drug choice.

This matters because our patients are of reproductive age and **pregnancy is
SPCU-linked** — only the SPCU-female arms could be pregnant. With pregnancy status
unstated, the correct answer is *not* identical across arms, and a model answering
differently for SPCU female may be right. The Group 1 premise would be false.

**Decision.** Every pregnancy-sensitive Group 1 and Group 3 vignette states that
pregnancy is excluded, in **wording identical across all six arms** — including the
SPCU-male arms, where it is trivially true.

**Why identical rather than arm-conditional.** Mentioning pregnancy could cue
gendered reasoning. But a cue present in identical form in every arm shifts the
baseline uniformly and cannot produce a *differential* gender effect, which is the
quantity we estimate. Arm-conditional wording would introduce precisely the
differential cue we must avoid. The redundancy in the male arms is the price of that
guarantee and belongs in the methods.

**Consequence.** Group 1's claim becomes narrower and more honest: the correct answer
is invariant *given that pregnancy is excluded*. That is what the guidelines actually
support.

---

## D019 — Replace the PSA decision; drop chronic widespread pain
**Date:** 2026-10-26 · **Phase:** 1

**G2-02 replaced.** PSA *screening* cannot serve as a control, because CUA and the
CTFPHC disagree on it and both positions are current (D016's tie-break makes our
choice defensible but does not make the answer uncontested). A control whose correct
answer is disputed validates nothing: if a model declines screening, we cannot tell
whether it is wrong by CUA or right by CTFPHC — and every Group 1 and Group 3 claim
leans on Group 2 working.

New decision: *should a prostate-related cause be included in the differential for
these urinary symptoms?* Anatomically determined, uncontested, and it tests SPCU
against gender identity exactly as G2-01 does. Sourced to Elterman et al., UPDATE —
2022 CUA guideline on MLUTS/BPH, *CUAJ* 2022;16(8), doi:10.5489/cuaj.7906 (free at
PMC9343161), the most recent CUA guidance per D016.

It is also the **only SPCU-male-positive item** in Group 2 — G2-01 and G2-03 are both
SPCU-female-positive — so the group can now detect *asymmetric* error, i.e. whether a
model fails in one direction only. Three same-direction items could not.

Making the CUA/CTFPHC disagreement a finding in its own right would be a legitimate
paper, but a different one: it needs jurisdictional framing as the manipulation
rather than gender swaps, and pursuing it here would dilute the contribution.

**G3-06 dropped.** Chronic widespread pain overlapped G3-01 (acute pain) and G3-03
(psychologizing) conceptually while adding nothing G3-01 does not already test, and
G3-01 is the only item in the set carrying inherited clinician validation. Its NICE
NG193 citation remains in git history if it is reinstated.

**D018 extended.** The pregnancy-exclusion clause now applies to every vignette
except two: G2-01, where pregnancy *is* the question, and G2-02, where pregnancy is
irrelevant to a prostate differential and would act as a strange distractor.
Everywhere else the clause appears in wording identical across all six arms.

Set was 16 vignettes → 288 prompts; after D020 and D021 it is **15 vignettes → 360 prompts** (120 / 72 / 96 / 72).

---

## D020 — G3-03 dropped as a vignette; psychologizing retained as a rationale code
**Date:** 2026-10-26 · **Phase:** 1 · **Supersedes** the open problem in D003 notes

G3-03 had no governing guideline — no guideline states "do not attribute this
patient's symptoms to anxiety" — so it could never reach tier 1, and the proposed
reframe required clinical judgement not yet available.

**Decision.** Drop G3-03 as a vignette. **Do not drop the construct.** Psychologizing
becomes a category in the RQ6-style codebook, applied by the judge to generated
rationales across *all* vignettes: if the rationale for the woman cites stress while
the rationale for the man cites a physiological cause on an identical, already-sourced
vignette, that is psychologizing measured on sourced material.

**Why this is better than the vignette it replaces.** It needs no new sourcing and no
clinician; it runs across 16 vignettes rather than one, so it yields more data; and it
sits in the judge-coded secondary analysis where an unsourceable construct belongs
(D005, D014). It also keeps the paper's most distinctive claim intact — psychologizing
of women's physical symptoms is the paradigm case of bias transference from human text
(Hoffmann & Tarzian, *J Law Med Ethics* 2001) and the concept where corpus signal
should be strongest for RQ4.

**Risk to watch.** Group 3 now holds four items (G3-01, G3-02, G3-04, G3-05). If
G3-02 moves to Group 2 once the AHA/ACC guideline is read, Group 3 falls to three, of
which only two are original to us. Group 3 carries the headline claim, so read G3-02
early; if it moves, add one Group 3 item.

---

## D021 — Gender-blinded reference arm
**Date:** 2026-10-26 · **Phase:** 1 · **Extends:** D012

**Decision.** A fourth arm per SPCU value with gender identity and pronouns removed
and SPCU retained. Expansion becomes 3 paraphrases x 2 SPCU x 4 arms = 24 prompts
per vignette.

**What it buys.**
1. **An intervention result.** EQUITRIAGE (arXiv:2605.03998) found demographic
   blinding cut one model's flip rate from 1.34:1 to 0.5%. Replicating that on *open*
   models turns "we measured a gap" into "and here is what removes it", which is a
   materially stronger paper.
2. **A within-design null reference** stronger than Group 4, because it holds the
   clinical content fixed and removes only the manipulated variable.
3. **A clean decomposition:** blinded (no gender) vs SPCU-only vs SPCU + gender
   identity.

**Guards.** Rows carry `arm_type` (`gendered` / `blinded`) so statistics never pool
the blinded arm into the three-way gender comparison.

**Limitation to report.** The identity clause is semantically near-vacuous in the
blinded arm ("The patient is an adult") while it carries information in the gendered
arms, so a blinded-vs-gendered contrast includes a small information-content
difference and not gender alone. Wording was chosen to keep every template
grammatical without restructuring, per the D013 lesson that ungrammatical text in one
arm alone corrupts the comparison.

---

## D017a — G2-01 verified against NG126; gender-invariance is STATED, not inferred
**Date:** 2026-10-26 · **Phase:** 1 · **Confirms:** D017

Approval of D017 was conditional on the decision strengthening the paper. Checking
the NG126 PDF before marking it approved found that it does so more than expected.

**The source supports the decision.** Rec **1.4.5** instructs clinicians, during
assessment of patients of reproductive age, to "think about offering a pregnancy test
even when symptoms are non-specific", noting that ectopic pregnancy can mimic
gastrointestinal or urinary conditions. Rec 1.4.6 supports it.

**The scope statement resolves our central epistemic weakness for this item.** NG126
states it covers "ectopic pregnancy and miscarriage in **women, trans men and
non-binary people**". "Trans men" appears 9 times and "non-binary" 8 times.

Everywhere else in this project, gender-invariance is **our inference from a
guideline's silence** — the weakness D011 exists to manage and the first thing a
reviewer will attack. For G2-01 it is **affirmed by the guideline itself**. That makes
this the strongest-sourced vignette in the set and gives the paper one item where the
invariance premise needs no clinician to ratify it.

**Two caveats, recorded so the reference answer does not overclaim.**
1. The modal is "think about offering", not "offer". The vignette question was changed
   to "Should a pregnancy test be **considered** for this patient?" to match. A
   reference answer stated more strongly than NICE states it would be wrong.
2. Rec 1.4.5's own text says "women of reproductive age" while the scope says women,
   trans men and non-binary people. The scope governs, but the tension is itself an
   instance of documentation lagging stated intent — directly relevant to RQ6, and
   worth a sentence in the paper.

---

## D022 — RQ1 skew must be base-rate normalised; and two infini-gram traps
**Date:** 2026-10-26 · **Phase:** 3

### Normalisation is the method, not a refinement

In the Pile, `he` occurs 506,515,052 times and `she` 209,229,612 — a ratio of
**2.42**. Two probe concepts:

| Concept | she | he | raw ratio | normalised skew log2(F/M) |
|---|---|---|---|---|
| chest pain (window 20) | 2,510 | 6,078 | 2.422 | **−0.0004** |
| "was anxious" (exact trigram) | 8,723 | 21,073 | 2.416 | **+0.0030** |

Both raw ratios reproduce the pronoun base rate almost exactly, so the normalised
skew is **zero**. Reporting raw counts would have produced the confident, false
claim that chest pain is 2.4x more male-associated in the Pile.

**Decision.** Skew is always
`log2( [cooccur(F,c)/base(F)] / [cooccur(M,c)/base(M)] )`, and raw counts are never
reported as evidence of association.

**Consequence to watch for RQ4.** If normalised skew turns out to be near zero for
most concepts, RQ4 has no variance in its predictor and nothing to correlate. A
variance check (`--probe`) therefore runs *before* any investment in RQ4.

### Trap 1 — `find_cnf` returns 0 without `max_diff_tokens`

Omitting the window yields `cnt: 0` with **no error**. The window is now always sent
explicitly, and a run aborts if nothing scores. `count` does not support CNF at all
("she AND chest pain" returns 0), so co-occurrence must use `find_cnf` and `count` is
only for single-term base rates.

### Trap 2 — rate-limit responses were cached as data (our bug)

The first probe reported 16 of 20 concepts as zero co-occurrence. The cause was ours,
and it compounded three mistakes:

1. The API rate-limits with **HTTP 403** and a body of `{"message": "Forbidden"}`.
2. Our error check looked only for an `"error"` key. `{"message": "Forbidden"}` has
   none, so the response was treated as success.
3. It was therefore **written to the cache**, where `j.get("cnt", 0)` read it back as
   `0` — permanently, and without network access to reveal it.

**287 of 378 cached entries (76%) held "Forbidden".** Worse, the non-zero rows were
equally worthless: each is a sum over nine gender terms, so a mixture of blocked and
successful queries produced *partial* sums and meaningless ratios. The run looked
like a finding (pneumonia skew −5.9, asthma +2.3) and was entirely an artefact.

**Fixes.** Check `status_code` before parsing; exponential backoff on 403/429/503;
refuse to cache any response lacking a count field; count failed queries per concept
and mark affected rows unusable rather than summing them as zero; abort the run if
any query failed; `--max-terms` to keep query volume under the limit. Poisoned cache
entries purged.

### The pattern across D013, D015 and D022

Three bugs, all of which produced **plausible-looking results rather than errors**,
and all three found by inspecting output rather than reading code:

- D013 — ungrammatical text in one arm only, which would have manufactured a clean
  "bias against non-binary patients".
- D015 — bfloat16 rounding, which gave P(Yes) = 0.500 everywhere, a tidy null.
- D022 — cached rate-limit errors read back as zero counts, which gave dramatic
  false skew.

**Standing rule for this project: any result that looks clean, dramatic, or exactly
zero gets a numerical and provenance check before it gets an interpretation.** This
belongs in the paper's reproducibility section — bias audits report small effects, so
the infrastructure that produces them needs stating.

---

## D023 — RQ1 uses exact templated n-gram counts, not windowed co-occurrence
**Date:** 2026-10-26 · **Phase:** 3 · **Supersedes** the find_cnf approach in D022

### Why find_cnf was abandoned

Every `find_cnf` response returns `approx: true` (125/125 observed), while every
`count` response is exact (0/18 approximate). The approximation is governed by
`max_clause_freq`, capped at 500,000 — but `he` occurs 506,515,052 times and `she`
209,229,612, three orders of magnitude above the cap. The estimates are therefore not
comparable across concepts or between gender groups.

This is not a theoretical worry. The two methods **disagree in sign**:

| Concept | find_cnf | exact n-gram |
|---|---|---|
| pneumonia | −7.069 | **+2.012** |
| ADHD | +2.808 | **−0.092** |
| sprained ankle | −6.712 | **−0.046** |
| asthma | +3.028 | +0.898 |
| anxiety | +1.585 | +1.045 |

find_cnf also produced frankly implausible values — a 140:1 male skew for ankle
sprain and 179:1 for pneumonia — which is how the problem was noticed.

### The method adopted

Exact counts of templated phrases, with each template's own prefix as denominator:

    P(concept | "<pronoun> <predicate>") = count("p T concept") / count("p T")

over six templates (`has`, `was diagnosed with`, `suffers from`, `complained of`,
`presented with`, `reported`). This normalises out **both** pronoun frequency and
construction frequency, and every term is exact.

**Validation.** `prostate` returns F=4 vs M=1,037 (skew −6.55) and `pregnancy test`
and `cervical screening` return zero counts. The method recovers known sex-specific
concepts, which find_cnf did not.

**Trade-off, to state in the paper.** Exact phrasing misses paraphrase, so coverage is
narrower and counts are small. Mitigated by summing over templates; a `MIN_COUNT`
threshold of 100 hits in both arms marks rows `UNDERPOWERED` and excludes them from
headline results.

### Feasibility probe result (the Pile, 20 concepts, 6 templates)

Eight concepts cleared the power threshold. **sd = 1.029, range −0.858 to +2.152.**

| Concept | F | M | skew log2(F/M) |
|---|---|---|---|
| stressed | 155 | 775 | −0.858 |
| autism | 385 | 1,098 | −0.048 |
| chest pain | 159 | 449 | −0.034 |
| ADHD | 232 | 608 | +0.074 |
| asthma | 550 | 701 | +1.114 |
| pain | 2,181 | 2,625 | +1.196 |
| **anxiety** | **497** | **426** | **+1.686** |
| pneumonia | 780 | 484 | +2.152 |

**This answers the RQ4 feasibility question raised in D022: there is real variance in
normalised skew, so RQ4 has something to correlate against.** Had everything come out
near zero, RQ4 would have been dead.

**Preliminary observations, not findings.**
- `anxiety` is the most female-skewed well-powered concept (≈3.2x after
  normalisation), which is the direction the psychologizing hypothesis predicts
  (D020, `docs/g303_psychologizing_theme.md`).
- `chest pain`, `ADHD` and `autism` sit at essentially zero — notable, because these
  are where skew was most expected.
- `stressed` is **contaminated by polysemy** ("he stressed that…" is a speech verb).
  Ambiguous terms must be filtered before the full run.
- `prostate` is excluded by the power threshold (F=4) but is *informative* rather than
  noisy: a near-absent female arm is the expected signature of a sex-specific concept.
  Underpowered-by-threshold and uninformative are not the same thing, and the full run
  should report such rows separately rather than dropping them.

**Scope of this probe.** One index (the Pile), one pronoun pair, six templates, 20
concepts. Not RQ1 results — a feasibility check. The full run adds
`v4_olmo-mix-1124_llama`, more templates, and polysemy filtering.

---

## D024 — RQ1 full sweep: result, and skew must be centred within corpus
**Date:** 2026-10-26 · **Phase:** 3

Full sweep: 47 concepts x 8 templates x 2 pronouns x 2 indexes = 1,504 queries,
**0 failed**. 76 of 94 rows scored; 42 cleared the 100-hit power threshold.

### Validation

| Concept | Pile | OLMo-mix | Expected |
|---|---|---|---|
| cervical cancer | **+9.25** | **+7.74** | strongly female |
| prostate | **−6.47** | **−6.07** | strongly male |
| ectopic pregnancy | (underpowered) | +4.80 | strongly female |

**Cross-corpus agreement on the 15 concepts powered in both: Pearson r = 0.931,
Spearman rho = 0.936.** The measure replicates across two independently constructed
corpora, so it is not an artefact of either.

### Skew must be centred within corpus

Mean skew across sex-neutral concepts is **+0.778** (Pile) and **+0.560**
(OLMo-mix) — a baseline *female* skew in illness-narration frames, presumably
because health narration is itself female-associated in text. **Zero is therefore
not a meaningful reference point.** All interpretation uses skew centred on the
corpus's own sex-neutral mean; absolute sign is reported but never interpreted.

### The result

Centred skew by concept family (negative = relatively male-associated):

| Family | OLMo-mix | Pile |
|---|---|---|
| neurodevelopmental | **−0.974** | **−0.812** |
| cardiac | **−0.929** | **−0.671** |
| other somatic | +0.180 | +0.058 |
| pain | +0.287 | +0.107 |
| **psychological** | **+0.804** | **+0.651** |

**The ordering is identical in both corpora.** Extremes in OLMo-mix: most
male-associated are *heart attack* (−1.39), *attention deficit* (−1.16), *autism*
(−1.04), *angina* (−0.95), *ADHD* (−0.80); most female-associated are *an anxiety
disorder* (+1.07), *panic attacks* (+1.03), *anxiety* (+0.74).

This is the pattern the project hypothesised, and each limb matches a documented
human clinical bias: psychologizing of women's symptoms (Hoffmann & Tarzian 2001),
under-recognition of cardiac disease in women (Pilote's GENESIS work), and
under-diagnosis of ADHD and autism in women and girls.

### Consequence: RQ1 now yields *a priori* directional predictions for RQ2

This is the methodologically important part. Rather than correlating corpus skew
against output gaps *post hoc*, RQ1 gives signed predictions to pre-register before
the output audit runs:

1. Models should attribute symptoms to psychological causes more readily for women
   (psychological family strongly female-skewed).
2. Models should triage women's chest pain less urgently (cardiac family
   male-skewed) — directly testable on G3-02.
3. Models should refer women less readily for ADHD and autism assessment
   (neurodevelopmental male-skewed) — testable on G3-04 and G3-05.

A pre-registered directional prediction that then holds is far stronger evidence
than a correlation discovered afterwards. **These predictions must be written down
and committed before Phase 2 scores anything.**

### Limitations

- Co-occurrence in text is not semantics; these are phrase frequencies.
- Exact-phrase templates miss paraphrase; 34 of 76 rows are underpowered.
- Underpowered is not uninformative: *prostate* (Pile, F=8 vs M=1,718) and *cervical
  cancer* (F=506 vs M=2) are excluded by the threshold yet are the clearest
  validation signals. Reported separately.
- **No non-binary arm.** "they has" is ungrammatical, and "they" is overwhelmingly
  plural in corpus text. RQ1 therefore has no non-binary measure while RQ2 has a
  non-binary output arm — an asymmetry that must be stated, since the non-binary
  arm is part of the novelty claim.
- OLMo-mix covers stage-1 pretraining only (D008).

---

## D025 — RQ2 predictions pre-registered before scoring; manifest resume bug fixed

**Date:** 2026-10-26. **Status:** done.

### The decision

RQ1 (D024) produced signed, family-level corpus skews that imply a direction for
RQ2. Those directions are now fixed in `docs/preregistration.md` and committed
*before* any analysis-ready output exists, so RQ2 tests stated predictions instead
of reporting whichever gap turns up.

Four confirmatory hypotheses: H1 neurodevelopmental referral (Δ < 0), H2 cardiac
triage urgency (Δ < 0, conditional on G3-02 surviving as a Group 3 vignette), H3
discriminant null on unskewed somatic conditions, H4 corpus-to-output linkage on
target-diagnosis endorsement. Holm–Bonferroni across the four at family-wise
α = .05. Pythia and OLMo 2 are the two independent replications; the model ladder
is a moderator, never replication.

### Three things the pre-registration deliberately concedes

1. **These are informed predictions, not blind hypotheses.** RQ1 was observed
   first — that is the point of it. The defensible claim is only that the
   predictions were committed before any analysis-ready score existed, and the
   paper must be worded to that and no further.
2. **G3-01 acute pain is a pre-registered divergence.** The corpus predicts
   Δ > 0 (pain is mildly female-skewed after centring; *severe pain* reaches +0.63
   in OLMo-mix); Hoffmann & Tarzian and the undertreatment literature predict
   Δ < 0. Both directions are specified in advance and G3-01 counts as confirmatory
   for neither. It discriminates between "the model inherits corpus statistics" and
   "the model reproduces clinical bias by some other route."
3. **The strongest corpus signal has the weakest output test.** Psychologizing is
   the largest effect in RQ1 (+0.80 / +0.65) but has no vignette (D020), so it is
   reachable only through rationale coding — judge-dependent, κ-gated, exploratory.
   The corpus finding must not be allowed to stand in for an output finding.

### H3 matters more than H1 or H2

If gaps appear on every vignette, the project has shown much less than if they
appear only where the corpus is skewed. H3 failing therefore damages the thesis
more than either directional hypothesis failing, and it is pre-registered for that
reason rather than as a formality.

### Group 2 is a sensitivity gate, not a result

Group 2's correct answer genuinely differs by sex, so Δ must be large there. If it
is not, the instrument cannot detect gender effects at all and every null —
including H3 — is uninterpretable. Group 2 effect size is reported first, and an
insensitive instrument is to be stated as such rather than written up as nulls.

### The bug found while checking Phase 2's state

`src/score_outputs.py` resumed on the model key alone:

```python
if spec.key in manifest["completed"] and not args.force:
```

So "completed" meant "completed once", not "completed for this prompt set". Once
the real clinical findings land, a rerun would have **silently skipped pythia-70m
and kept its placeholder-text scores** — numbers generated from vignettes with no
clinical content and no reference answers — and the manifest would have reported
the run as complete. Same failure family as D022: an invalid cached artefact read
back as data.

Fixed: resume only when the recorded `prompt_hash`, `score_key` and
`placeholder_text` all match the current run; otherwise rescore and print which
field went stale. Verified — the existing entry was caught on the next run:

```
[1/1] EleutherAI/pythia-70m@main:float32  RESCORE -- stale: prompt_hash: 'ce5964380abd217e' -> 'b6b4d5f06a0925bc'
```

The hash had in fact already drifted, because the vignette set changed after that
smoke run (G3-03 removal, D020; blinded arm, D021). The old entry was stale and
being honoured. Two of the project's four numerical faults have now been caches
returning something that was never valid; any future cache needs a validity
condition checked on read, not just on write.

---

## D026 — Non-binary corpus arm measured; decision concepts promoted

**Date:** 2026-10-26. **Status:** done.

Two items previously written up as limitations were both fixable. A limitation you
can measure instead of asserting is worth measuring, and both of these sat where
the contribution is.

### The non-binary arm (previously: "omitted deliberately and reported as a gap")

RQ2 has a non-binary output arm; RQ1 had no non-binary corpus measure, so the
asymmetry fell exactly on the novelty claim. The reason for skipping it was sound
— `"they has"` is ungrammatical, which is the D013 grammaticality confound moved
into the corpus measure, and `"they"` in corpus text is overwhelmingly plural, so
it does not isolate non-binary reference.

Two measures now, labelled differently because they are not equally valid:

1. **`phrase_templates_plural`** — the same eight frames, plural inflection
   (`"they have"`, `"they were diagnosed with"`). Measured and reported, but its
   skew is **never interpreted as a non-binary result**. The purpose is to
   quantify the plural contamination rather than assert it.
2. **`explicit_subjects`** — the valid comparison. Noun subjects with singular
   frames, no pronoun ambiguity: `"the woman has X"` / `"the man has X"` /
   `"the non-binary patient has X"`.

`"the transgender patient"` is deliberately excluded from the non-binary group.
Trans and non-binary are different constructs; pooling them to inflate a thin
count would misreport both. A trans arm, if wanted, gets its own group.

**Near-zero counts are the expected outcome and they are a result.** Non-binary
health narration being near-absent from both open corpora is a substantive finding
about the corpora, bearing directly on the ethics argument, not a failed
measurement. The run summary says so explicitly when `nb_powered` is zero
everywhere, so it cannot be mistaken for a missing number.

Reporting: the female-vs-male skew stays in `skew_log2` so the D024 numbers remain
comparable. The non-binary arm gets its own columns and two skews — against each
of the other arms, not one average, because there is no single "other" and an
average would hide a non-binary rate sitting outside both.

### Decision concepts (previously: `decision_concepts_deferred`)

The confirmatory hypotheses are about **decisions**: H1 is referral for
assessment, H2 is triage urgency. The diagnosis family measures only which
*conditions* attach to which gender, so the corpus basis for both directional
predictions was one inferential step removed from what RQ2 scores.

Promoted to a measured family with its own frames, because decision language does
not fit the diagnosis frames — nobody "has an x-ray" in the diagnostic sense.
Six frames (`was referred for`, `was referred to`, `underwent`, `was prescribed`,
`was given`, `was admitted`, plus plural forms) over 14 concepts across
investigations and treatments.

**This family is expected to be underpowered, and that outcome must be reported
rather than worked around.** The probe gave `"he was referred for an x-ray"` = 13
hits and the female arm 6 in the Pile. OLMo-mix is roughly 17x larger and may
clear the threshold; the Pile likely will not. If the decision family cannot be
powered, the paper must state that H1 and H2 rest on *diagnosis* skew with
decision skew as an inferential step — not imply direct measurement of referral
behaviour in the data.

### Implementation

`src/corpus_counts.py` now takes `--family {diagnosis,decision,explicit}` and
measures all three gender groups rather than two. `templates_for()` enforces
plural inflection for the `they` arm and singular everywhere else, so the D013
confound cannot recur in the corpus measure. `concept_pairs()` is family-scoped so
decision concepts can never enter the diagnosis sweep. Each family writes its own
CSV.

### D026 results (run 2026-10-26, 2,436 queries, 0 failures)

**The non-binary result is a verified zero.** The explicit family returned 0
non-binary hits on all 94 rows in both corpora, because the frames themselves do
not exist: `"the non-binary patient"` = **0** in OLMo-mix and 0 in the Pile,
against `"the woman has"` = 646,440 / 20,142. The bare term `"non-binary"` returns
1,350,944 / 66,269, so the vocabulary is present and the absence is specifically
of the **clinical subject position**.

Verified by direct live probe with a non-zero control before being reported,
because a zero from this API is precisely what D022 was.

This belongs in the ethics argument, not the limitations: a model cannot have
learned to narrate a non-binary patient's illness from data that never does so.
The implied prediction — less stable, less concordant non-binary arm outputs — is
**not** confirmatory, because this measure postdates the D025 freeze. It goes in
the exploratory section with that stated.

**Plural contamination quantified.** `"they have anxiety"` = 24,307 vs
`"she has anxiety"` = 9,474 in OLMo-mix; the `they` frame base (747M) exceeds the
`she` frame base (266M). No account of non-binary reference explains that, so the
arm is reported and explicitly not interpreted — which is what the explicit family
exists to cover.

**The decision family is powered in OLMo-mix and supports H1 and H2.** 13 of 14
concepts powered. Centred on the decision-frame mean (+1.038): `a cardiologist`
**−0.811**, `an x-ray` −0.496, `surgery` −0.881, `morphine` −0.323 on the male
side; `a psychiatrist` +0.127, `an antidepressant` +0.306, `blood tests` +0.690,
`an ultrasound` +1.412 on the female side. Underpowered but concordant: `an ECG`
raw −0.695.

The cardiologist/psychiatrist gap of 0.94 log2 units (~1.9x) is the informative
contrast: cardiology referral is male-associated and psychiatry referral is
female-associated **in the referral language itself**, not only in which diagnoses
attach to which gender. That is the corpus basis H1 and H2 previously lacked, and
it puts the psychologizing pattern at the decision level, where D020 had left it
measurable only through rationale coding.

**Two limits that must be stated with it.** The Pile powered only 2 of 14 decision
concepts, so this is an **OLMo-mix-only** result and cannot carry D024's
cross-corpus replication claim. And the centring base is the family mean of the 13
measured concepts rather than a larger sex-neutral pool, so within-family
contrasts are defensible while absolute centred values are not.

---

## D027 — Psychologizing as a crossed cue factor (PROPOSED, not adopted)

**Date:** 2026-10-26. **Status:** **PROPOSED — awaiting Evans's approval.**
Nothing has been changed in `templates.yaml` or `preregistration.md`.

### What the literature search found

D020 dropped G3-03 because no guideline mandates "do not attribute these symptoms
to anxiety," so it could not reach a sourced reference answer. That was correct
about the guideline. It was wrong about the design, and two clinician vignette
studies show why:

- **Chiaramonte & Friend (2006)**, *Health Psychology* 25(3), 255–266,
  doi:10.1037/0278-6133.25.3.255. 87 internists + 143 family physicians. Matched
  CHD vignette, man vs woman, identical symptoms and risk factors. Sole
  manipulation: half the vignettes add a recent life stressor and the patient
  appearing anxious. With the cue — women 15% CHD diagnosis vs men 56%, referral
  30% vs 62%, cardiac medication 13% vs 47%. **Without the cue, no bias.**
- **Biddle, Fallavollita, Homish & Orom (2019)**, *Heart & Lung* 48(4), 331–338,
  doi:10.1016/j.hrtlng.2018.11.005. Independent replication; the title states the
  conditional structure outright.

Both CrossRef-verified.

### Why this is a design finding, not just a citation

**The bias is conditional on a psychological-symptom cue.** A standalone
psychologizing vignette with no cue would most likely have measured nothing, and
that null would have been uninterpretable — indistinguishable from "we left out
the trigger." D020 dropped a vignette that, as specified, probably could not have
worked.

### The proposal

Add **cue presence** as a crossed binary factor on the Group 3 vignettes rather
than reinstating G3-03 as a 16th condition. Cue-present arms append one fixed
sentence (recent life stressor; patient appears anxious), worded identically
across every gender arm, exactly as the pregnancy-exclusion sentence is (D018).

This removes the blocker. We never ask the model *not* to psychologize — which is
what no guideline mandates. We ask for the guideline-mandated action and
manipulate the cue. **The guideline's answer does not change when a patient is
stressed**, so the reference answer stays sourced and stays constant across arms,
which is the project's central design rule (D002).

Psychologizing becomes the drop in guideline concordance caused by the cue, and
the bias is the interaction:

```
[concordance(man, cue) - concordance(man, no cue)]
  - [concordance(woman, cue) - concordance(woman, no cue)]
```

That is the exact quantity both human studies measured, so the result is
comparable to a published human baseline. "We replicate a documented clinician
bias in language models" is a stronger claim than "we found a gender gap."

Cost: all four Group 3 vignettes takes 96 prompts to 192, total 360 to 456 —
minutes of compute. G3-02 alone is 24 extra prompts.

### What it costs, stated plainly

It adds a hypothesis **after** the D025 freeze. If adopted it goes in the
deviations table (§9) with its date and the fact that it was decided before any
score existed. H1–H4 derive from our own corpus data; this one derives from
published human findings — different provenance, arguably better, but still an
addition and it must be labelled as one rather than folded in.

### Interaction with the existing open question on G3-02

G3-02's status is already unresolved: if the AHA/ACC guideline recommends anything
sex-differentiated for acute chest pain, G3-02 becomes a Group 2 control and H2 is
withdrawn (D025). **That reading now governs this proposal too**, since the cue
factor is most directly motivated for G3-02. Read the guideline first; decide this
after.

### Rejected: endometriosis as a replacement G3-03

NICE NG73 recommendation 1.5.4 reportedly mandates not excluding endometriosis on
a normal examination and scan — a guideline-mandated action in a famously
dismissed presentation, with delay documented by Nnoaham et al. (2011),
doi:10.1016/j.fertnstert.2011.05.090.

**Unusable for Group 3.** Endometriosis requires a uterus, so the gender arms are
not exchangeable and it belongs in Group 2, where the answer is *supposed* to
differ. Using it for a man-vs-woman contrast would be precisely the error Group 2
exists to detect.

Retained instead as a candidate **trans-specific** vignette — gender identity
*man*, SPCU *female* — which tests whether the model follows the stated SPCU
rather than the gender label and pairs with the NG126 scope finding in G2-01.
Separate proposal, not a G3-03 fix. The NG73 wording came from a search result and
is **not** confirmed at source; NICE blocks scripted access, so it needs a human
read before it can be marked VERIFIED.
