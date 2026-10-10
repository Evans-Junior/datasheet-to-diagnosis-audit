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
