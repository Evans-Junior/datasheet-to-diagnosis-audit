# Declaration of AI Assistance

**Project:** From datasheet to diagnosis: tracing gender bias through open training-data pipelines into LLM health advice
**Course:** Ethics in Artificial Intelligence (McGill University)
**Authors:** Evans Kumi, Aymen Boustani
**Last updated:** 2026-10-09

## Summary

An AI coding assistant (Claude Code, Anthropic) was used during the implementation
and analysis phases of this project. This document records what it was used for and
what it was not, so that readers, markers, and reviewers can judge the work on an
accurate account of how it was produced.

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

## What the authors are responsible for

The following are the authors' own work and were not delegated:

- **Research design.** The research questions, the three-group vignette taxonomy
  (sex-neutral / sex-specific / clinically neutral but historically biased), and the
  decision rule that a gender difference only counts as bias where the clinically
  correct answer is invariant.
- **Clinical content.** All reference answers and their guideline sourcing. Any
  vignette whose correct answer could not be sourced to a named clinical guideline is
  flagged `needs_clinician_review` in `docs/vignette_sources.md` rather than filled in
  by a model.
- **Qualitative coding.** The RQ6 codebook and its application, including all
  double-coding and reliability statistics.
- **Interpretation.** All claims, causal language, limitations, and conclusions.

## Verification commitments

- No citation appears in this work unless an author has confirmed it against the
  primary source. AI-suggested references that could not be verified were discarded.
- No clinical guidance, dataset statistic, or empirical result in this work was
  produced by a language model acting as a source of fact. All reported numbers come
  from the code in `src/`, which is in the repository and reproducible.
- Methodological decisions, including those prompted by a suggestion from the
  assistant, are recorded with their rationale in `docs/decisions.md` and were adopted
  only on the authors' judgement.

## Note on the object of study

This project audits language models. The use of a language model as a development tool
is separate from the models under audit (Pythia, OLMo, and the weights-only contrast
model) and played no part in generating, scoring, or coding the data analysed. The
assistant was not used to produce model outputs, reference answers, or qualitative
codes that enter the results.

## Policy

This declaration is intended to satisfy McGill's requirements on the disclosure of
generative AI use in coursework and the disclosure expectations of ACM FAccT and
AAAI/ACM AIES.