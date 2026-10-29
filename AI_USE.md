# Declaration of AI Assistance

**Project:** From datasheet to diagnosis: tracing gender bias through open training-data pipelines into LLM health advice
**Course:** Ethics in Artificial Intelligence (McGill University)
**Authors:** Evans Kumi, Aymen Boustani
**Last updated:** 2026-10-28

## Summary

An AI coding assistant (Claude Code, Anthropic) was used during the implementation
and analysis phases of this project, and — as of 2026-10-28 — in drafting the
clinical text of the vignette instrument. This document records what it was used
for and what it was not, so that readers, markers, and reviewers can judge the work
on an accurate account of how it was produced.

**Change of scope, 2026-10-28.** An earlier version of this declaration stated that
all clinical content was the authors' own and was "not filled in by a model". That
is no longer true, and the declaration has been revised rather than the practice
concealed. The assistant now drafts the vignette clinical findings, answer option
sets, and candidate reference answers. §"Clinical content" below states exactly
what that means, and §"Verification gate" states what must happen before any of it
can support a reported result. The authors' reason was time; the honest handling of
that is disclosure plus a hard verification gate, not a quiet redefinition of
"authored".

## What AI assistance was used for

- **Code implementation.** Writing and debugging the Python modules under `src/`
  (corpus queries, vignette generation, log-probability scoring, statistical models,
  plotting), plus configuration and packaging.
- **Engineering scaffolding.** Repository structure, caching and reproducibility
  infrastructure, environment setup, and resource verification (checking that model
  revisions, corpus indexes, and APIs referenced in the design are current).
- **Literature search support.** Locating candidate references and retrieving
  bibliographic details. Every citation retained in the final work was checked by the
  authors against the primary source.
- **Drafting and editing support.** Restructuring and copy-editing prose drafted by
  the authors, and summarising prior work for the authors to verify.
- **Methodological critique.** Several design faults were identified by the
  assistant and adopted on the authors' judgement — among them that the inference
  unit was the vignette rather than the prompt pair (D036), that the instrument
  needed a positive control and a nuisance floor (D035), and that answer options
  must be token-length matched. Each is recorded in `docs/decisions.md` with its
  reasoning, so a reader can audit the argument rather than take the conclusion on
  trust.
- **Clinical content drafting.** See below.

## Clinical content — what the assistant drafted, and from what

For each of the 15 vignettes the assistant wrote:

- the **clinical findings** sentence shared by all arms of that vignette,
- the **answer option set**, and
- a **candidate reference answer**.

These were derived from guideline passages that the **authors had already located,
retrieved and quoted verbatim at first hand** in `docs/vignette_sources.md`,
together with each passage's own strength-of-recommendation and
quality-of-evidence grading. The drafting task was, in each case, to express
criteria already quoted in that file — for example, to write findings that
explicitly satisfy or negate each limb of a decision rule the guideline states.

**What this is not.** No clinical fact in the instrument originates from the
assistant's own knowledge. Where a draft went beyond what the quoted passage
supports, that is an error to be caught at the verification gate below, not a
feature of the method. The assistant was not used as a source of clinical
authority, and the project does not treat it as one.

**The known risk, stated plainly.** A language model drafting the stimulus
materials for an audit of language models is a validity threat and is reported as
one. Two distinct concerns:

1. **Subtle clinical error.** A findings sentence can look complete and still fail
   to negate one limb of a rule, which would make the item's reference answer
   wrong. This is what the verification gate exists to catch.
2. **Stimulus–instrument affinity.** Text written by one language model may be
   unrepresentative of clinical prose in ways that interact with how other language
   models score it. This cannot be fully removed. It is mitigated by holding the
   clinical text identical across all arms of a vignette — the measured quantity is
   a *difference* between arms of the same text, so any affinity effect is common to
   both sides of every contrast and cancels in Δ. It is not mitigated for
   between-vignette comparisons, and the limitations section says so.

## Verification gate

The following is binding and is enforced in code, not left to intention:

- Every vignette's clinical findings, option set and reference answer begin at
  **tier 3 (unverified)** in `docs/vignette_sources.md`.
- A vignette is promoted only when a **qualified clinician** has confirmed that the
  findings force the stated reference answer and no other, against the quoted
  guideline passage. The reviewer is given the guideline quote, the draft, and an
  explicit instruction that the draft is AI-generated and should be rejected rather
  than corrected if it is wrong.
- `scripts/check_templates.py` blocks the build while any required field is
  unfilled, and records verification status per vignette.
- **No result computed on an unverified vignette may be reported as a finding.**
  Where unverified items are scored during development, their numbers are labelled
  as such and carry no inferential weight.

## What the authors remain responsible for

- **Research design.** The research questions, the four-group vignette taxonomy, and
  the decision rule that a gender difference only counts as bias where the clinically
  correct answer is invariant.
- **Guideline sourcing.** Identifying, retrieving and quoting the governing
  recommendation for every vignette, including its grading, at first hand from the
  primary document. All 15 blocks in `docs/vignette_sources.md` were sourced this
  way before any clinical text was drafted.
- **Clinical adjudication.** Accepting, amending or rejecting each drafted vignette,
  and securing clinician review.
- **Qualitative coding.** The RQ6 codebook and its application, including all
  double-coding and reliability statistics.
- **Interpretation.** All claims, causal language, limitations, and conclusions.

## Verification commitments

- No citation appears in this work unless an author has confirmed it against the
  primary source. AI-suggested references that could not be verified were discarded.
- No dataset statistic or empirical result in this work was produced by a language
  model acting as a source of fact. All reported numbers come from the code in
  `src/`, which is in the repository and reproducible.
- Methodological decisions, including those prompted by a suggestion from the
  assistant, are recorded with their rationale in `docs/decisions.md` and were adopted
  only on the authors' judgement.

## Note on the object of study

This project audits language models, and a language model was used to build part of
the instrument. These are separate models — the assistant is not among the systems
under audit (Pythia, OLMo 2, and the weights-only contrast model) — and it played no
part in **generating, scoring, or coding the data analysed**: it produced no model
output that enters the results, computed no score, and assigned no qualitative code.
Its role in the instrument itself is declared above and carried into the limitations
section rather than left for a reader to infer.

## Policy

This declaration is intended to satisfy McGill's requirements on the disclosure of
generative AI use in coursework and the disclosure expectations of ACM FAccT and
AAAI/ACM AIES. Where those requirements and this declaration diverge, the
requirements govern and this file is to be corrected.
