# Paper notes — difficulties, decisions and numbers

Working notes for the write-up. Everything here is either a measured number, a
verified citation, or a problem we actually hit. `docs/decisions.md` holds the
formal decision log (D001–D015); this file is the narrative version, organised by
where it lands in the paper.

Keep appending. A difficulty recorded while it is fresh is worth more than one
reconstructed in the last week.

---

## 1. Contribution claim

**The claim.** Most LLM bias audits can only inspect outputs, because training data
is closed. Fully open families release theirs, so gender skew in the data can be
linked to gender bias in model health advice, and the dataset documentation can be
checked for whether it discloses that risk.

**What makes it defensible rather than incremental:**

- **The data→output link.** The two closest pieces of prior work (see §2) audit
  gender bias in LLM clinical outputs but have no training-data access, so neither
  can attempt RQ1 or RQ4. That link is ours.
- **The invariance rule.** A gender difference counts as bias only where the
  clinically correct answer is identical across patients. Guideline-sourced
  reference answers plus a sex-specific control group make this testable rather
  than asserted.
- **Sex vs gender separated operationally.** We hold Sex Parameter for Clinical Use
  fixed and vary gender identity (D001, D012), which to our knowledge no clinical
  LLM audit has done. A 2025 systematic review found almost no work addressing
  non-binary identities at all.

**Do not overclaim.** RQ4 is association, not causation. The word "transference"
should not appear in a causal sense anywhere.

---

## 2. Related work — verified citations

All DOIs resolved against CrossRef via `scripts/verify_dois.py`; raw output in
`results/tables/doi_verification.json`.

| Role in the paper | Citation |
|---|---|
| Closest prior design — 2×2 of documented bias × clinical relevance, paired prompts. **Our template.** | Chang CT, et al. Evaluating anti-LGBTQIA+ medical bias in large language models. *PLOS Digit Health* 2025;4(9):e0001001. doi:10.1371/journal.pdig.0001001 |
| Precedent for vignette-based gender/race audit in clinical LLMs | Zack T, et al. *Lancet Digit Health* 2024;6(1):e12–e22. doi:10.1016/S2589-7500(23)00225-X |
| Sex/gender bias framing specific to health AI | Cirillo D, et al. *npj Digit Med* 2020;3:81. doi:10.1038/s41746-020-0288-5 |
| Sex vs gender operational standard — **our position rests on this** | McClure RC, et al. Gender harmony. *JAMIA* 2021;29(2):354–363. doi:10.1093/jamia/ocab196 |
| Reporting standard obliging explicit sex/gender treatment | Heidari S, et al. SAGER guidelines. *Res Integr Peer Rev* 2016;1:2. doi:10.1186/s41073-016-0007-6 |
| Why binary-only gender treatment is itself a harm; grounds the non-binary arm | Dev S, et al. EMNLP 2021:1968–1994 |
| Pain-management vignettes; the only part of our set with inherited clinician validation | Logé C, et al. Q-Pain. NeurIPS Datasets & Benchmarks 2021. arXiv:2108.01764; PhysioNet doi:10.13026/2tdv-hj07 |
| Stated reasoning is not faithful to the computation | Turpin M, et al. NeurIPS 2023; Lanham T, et al. 2023 |
| The actual causal method, named as future work | Vig J, et al. NeurIPS 2020 |
| Documentation analysis basis (RQ6) | Gebru T, et al. Datasheets for Datasets |

**Must read before submission.** Two 2025–26 arXiv preprints audit gender bias in
**LLM-based emergency department triage** (one titled EQUITRIAGE; arXiv 2511.17124
and 2605.03998). Directly adjacent to our G3-02 triage vignettes. Neither has
training-data access, so the data link survives — but going in unaware would be bad
and a reviewer who knows them will not be gentle. **Not yet read.**

---

## 3. Methods decisions a reviewer will interrogate

Short form; full reasoning in `decisions.md`.

| # | Decision | Why it will be challenged |
|---|---|---|
| D001, D012 | Hold SPCU fixed, vary gender identity; cross both SPCU values | Without this, any difference is defensible as clinically appropriate. Crossing makes SPCU and gender-identity effects separately estimable. |
| D002 | 2×2 scenario frame, adding a no-bias/irrelevant control cell | Without a noise baseline there is no way to distinguish a gender gap from prompt-sensitivity variance. |
| D003, D011 | Guideline-sourced reference answers, tiered by confidence | Guidelines state management but are **silent** on gender. We read silence as invariance; a reviewer will ask who authorised that reading. |
| D004 | OLMo 2 base **and** instruct | Post-training breaks the clean data→output chain, so RQ4 is anchored on base models only and instruct is a separate labelled comparison. |
| D005 | Rationales are a second outcome, never an explanation | Turpin et al.: a rationale that never mentions gender can still be an answer that moved because of it. |
| D006, D010 | Judge disjoint from the audit set; κ at both quantisations | RQ5 puts a Mistral/Llama model *under* audit; the same model judging would contaminate the comparison. |
| D012 | No patient names | A name carries ethnicity and class signal as well as gender, confounding the manipulation. |
| D014 | PMI as the scoring statistic | Raw log-probability favours short options and high-frequency tokens; the three scores disagree sharply (§5). |
| D015 | float32 scoring | See §4.4. The alternative silently produced a zero gap everywhere. |

---

## 4. Difficulties encountered

The honest research log. Several of these belong in the paper; the numerical ones
belong in a reproducibility or threats-to-validity section.

### 4.1 The proposal's resource assumptions were wrong in three places

- **"OLMo, trained on Dolma" is not true of OLMo 2.** OLMo 2 uses two-stage
  pretraining: stage 1 on `olmo-mix-1124` (~3.9 T tokens, >90% of budget, drawing
  on DCLM, Dolma, Starcoder, Proof Pile II), stage 2 on `dolmino-mix-1124`.
- **The stage-2 mix is not searchable.** infini-gram currently offers 13 indexes,
  including `v4_olmo-mix-1124_llama`, `v4_dolma-v1_7_llama` and
  `v4_piletrain_llama` — but **nothing for `dolmino-mix-1124`**, and nothing for
  any Olmo 3 mix. So RQ4's OLMo arm speaks to stage 1 only. Stated as a limitation,
  with ">90% of the token budget" as the honest quantifier. (D008)
- **OLMoTrace has no public API.** Access is the Ai2 Playground UI; the backend is
  open-sourced (Apache 2.0, `infinigram-api`) but self-hosting needs the full
  index. Phase 4 is therefore manual: a ranked list of the 10–20 most biased
  outputs plus a recording template. (D009)

**Paper-relevant point:** "open training data" is not a binary property. OLMo 2 is
*more* open than Llama and *less* searchable than its own documentation implies.
That nuance is worth a paragraph — it is the kind of gap between stated and
practical openness that the RQ6 documentation analysis exists to surface.

### 4.2 Guideline sourcing was harder than expected

14 of 17 conditions now carry a resolved citation (`docs/vignette_sources.md`).
The three outstanding ones are each outstanding for a *different* structural
reason, which is itself the finding:

- **`G1-02` malaria — living guideline.** WHO malaria guidance sits on MAGICapp,
  is version-dated, and a September 2026 release supersedes 13 August 2025. No
  stable DOI. A DOI circulating from a third-party host was **not** used. Needs a
  version + access-date citation pinned like a model revision, or a reference
  answer can go stale mid-project.
- **`G2-01` pregnancy — wrong level of description.** "Pregnancy-related
  presentation" cannot be assigned a guideline, because the guideline follows from
  the *decision*, not the condition. Blocked until the decision is specified.
- **`G3-03` psychologizing — no guideline exists, structurally.** No guideline says
  "do not attribute this patient's symptoms to anxiety." This is our *most wanted*
  vignette and the least sourceable. Planned fix: reframe so the guideline-mandated
  next step is a specific investigation and score whether it is ordered, making
  psychologizing measurable as failure to order a sourced test.

Also surfaced:

- **Jurisdictional conflict is substantive.** CUA recommends offering PSA screening;
  the Canadian Task Force recommends against and has not revised since 2014. Both
  are current Canadian guidance. This makes PSA screening a **poor Group 2 control**
  — a control needs one correct answer to differ by sex against, not a contested
  one. Same pattern for NICE NG87 vs CADDRA (ADHD), Diabetes Canada vs ADA, CTFPHC
  2013 cervical guidance vs provinces that have moved to HPV-based screening.
- **`G4-03` was swapped.** Laceration repair had no society guideline; replaced with
  group A streptococcal pharyngitis (IDSA, doi:10.1093/cid/cis629), which has an
  unambiguous test-then-treat pathway.
- **Secondary sources are unreliable about their own citations.** Three separate
  cases: two different DOIs circulating for the IDSA SSTI guideline (`ciu296` is the
  full guideline, `ciu444` the executive summary — same trap again for pharyngitis);
  a third-party index mislabelling the 2024 AAO conjunctivitis PPP as
  "Cornea/External Disease PPP"; and **CrossRef itself** misspelling Stiell as
  "Shell" on the 1993 Ottawa Ankle Rules record. Hence `scripts/verify_dois.py`.
  **No citation in this paper came from a search snippet.**

### 4.3 Hardware forced design changes

Apple M4 Pro, 14 cores, 48 GB unified memory, ~270 GB free. **No CUDA**, so: MPS
backend only, no `bitsandbytes` quantisation, no flash-attention.

- Mistral-Small-24B cannot run at bf16 — the official checkpoint is 47.1 GB against
  48 GB of unified memory with a ~36 GB default GPU wired limit. Judge runs at
  8-bit (25.05 GB).
- pythia-12b cannot run in float32 (~48 GB of weights alone) and runs in float16
  with a sensitivity check against pythia-6.9b at both precisions.
- Sequential execution with one resident model is not an optimisation but the
  design: peak RAM is set by the largest single model, not the sum. (D007)
- The checkpoint sweep is one model (pythia-1.4b) at 9 log-spaced steps, with
  download→score→delete. All 143 checkpoints across all sizes would need ~414 GB.

**Useful framing:** the whole study runs on one laptop. That is worth stating — it
makes the audit reproducible by anyone, which matters for an accountability paper.

### 4.4 Two numerical faults that would have produced false findings

Both were caught by **inspecting generated output**, not by reading code. This is
the single most transferable lesson of the project.

**(a) Grammaticality confound (D013).** The first vignette build emitted *"They is
a non-binary person."* Ungrammatical text in the non-binary arm **alone** depresses
that arm's sequence probability for reasons of grammaticality rather than bias —
and it would have done so consistently across every model and every vignette,
producing exactly the clean, replicable "bias against non-binary patients" result
we would have been most tempted to publish. Fixed by carrying verb forms per arm.

**(b) Precision fault (D015).** The first scored output gave **P(Yes) = 0.500 for
every prompt in every arm**. Pythia's logits reach magnitudes around 1080, where
bfloat16's representable spacing exceeds the gap between the " Yes" and " No"
logits — both rounded to the same value, all options tied, and the measured gender
gap was identically zero everywhere.

Casting logits to float32 *after* the forward pass does not help; the precision is
already gone. Two fixes were needed: perform the final projection in float32
(`fp32_head`), and then — after a regression test — move the whole body to float32,
because measured bf16 deviation was **0.242 nats** against a **0.140 nat** gap
between the two leading options, large enough to reverse their ranking. Gender gaps
of interest may be exactly that small.

**Why this matters for the paper.** A uniform zero gap across all models, vignettes
and arms is a *publishable-looking* null result. Had it not been checked, the paper
would have reported no unwarranted gender difference, with a clean methods section
and a numerical artefact as its central finding. Guards now in place: a run aborts
if over half its prompts have tied options, and `scripts/test_scoring.py` asserts
options remain distinguishable.

**Recommend a short methods paragraph on this.** Bias audits report small effects;
if numerical precision can exceed the effect size, precision belongs in the
methods, not in a footnote. We have not seen this discussed in the audit literature.

### 4.5 Clinician access

No clinician attached as of 2026-10-15. Restructured the ask rather than the
science: the reviewer's job is **one global judgement** — do guidelines support
sex-invariance for this condition set — not per-vignette validation (D011). ~45–60
minutes. Materials in `docs/clinical_review_request.md`, `clinical_review_form.md`,
`outreach_email.md`. Five McGill contacts identified.

**Contingency, and why plain deferral is not enough:** excluding unvalidated
vignettes is **not neutral**, because the hardest conditions to source are
disproportionately the ambiguous Group 3 ones — where bias is most expected. So the
primary analysis runs on tiers 1+2 and is repeated on tier 1 alone; if conclusions
hold either way, the missing clinician provably does not change them.

---

## 5. Measured numbers to cite

Environment: Python 3.12.15 (arm64), torch 2.14.1 (MPS), transformers 5.19.0,
mlx 0.32.3. Seed 20261009. `requirements.txt` pins all versions.

**Forward-pass latency** (256-token prompt, bf16, 20 trials,
`results/tables/rq0_bench.json`):

| Model | Params | Weights | Forward pass |
|---|---|---|---|
| pythia-70m | 0.070 B | 0.14 GB | 6.5 ms |
| pythia-160m | 0.162 B | 0.32 GB | 15.5 ms |
| pythia-410m | 0.405 B | 0.81 GB | 39.6 ms |
| pythia-1.4b | 1.415 B | 2.83 GB | 116.7 ms |

Linear at ~83–98 ms per billion parameters; projects to ~250 ms (2.8b), ~600 ms
(6.9b), ~1.05 s (12b). Note these are **bf16** figures; float32 roughly doubles
them (D015). Log-probability scoring is one forward pass per option, so the full
scoring design is well under an hour of compute — **download bandwidth, not
compute, is the binding constraint.**

**Vignette set:** 16 templates → **288 prompts** (3 paraphrases × 2 SPCU × 3 gender
identities = 18 arms each). Per group: 90 / 36 / 108 / 54. `G2-01` blocked.

**Scoring statistics disagree** (pythia-70m, Spearman): `sum_logprob` vs
`mean_logprob` 0.64; `sum_logprob` vs `pmi` **0.15**; `mean_logprob` vs `pmi` 0.19.
Large enough that the choice of statistic could determine the conclusions, so it
was fixed in advance (PMI) and all three are retained for sensitivity reporting.

**Judge sizes:** Mistral-Small-24B at 4-bit 13.26 GB, 8-bit 25.05 GB, bf16 47.1 GB.

---

## 6. Limitations — draft list

1. **Association, not causation** (RQ4). Corpus co-occurrence skew correlating with
   output gaps does not establish that the data caused the gap. The causal method
   (activation patching / causal mediation, Vig et al. 2020) is future work.
2. **Stage-1 coverage only** for the OLMo data link; `dolmino-mix-1124` is not
   indexed (§4.1).
3. **n-gram counts are not semantics.** Pronoun ambiguity, non-binary terms sparse
   in corpora, window choice arbitrary.
4. **Reference-answer quality.** Tier distribution reported by condition; sourced
   from guidelines whose silence on gender we interpret (§4.2, D011).
5. **Sex vs gender.** Guidelines are written around sex; our manipulation is gender
   identity with SPCU held fixed. Vignettes are not patients.
6. **Prompt sensitivity.** Three paraphrases bound it; Group 4 gives the noise
   baseline. Not eliminated.
7. **Numerical precision** can exceed the effect size (§4.4). pythia-12b runs at
   lower precision than the rest.
8. **Legitimate sex differences** exist and Group 2 exists to detect that we have
   not mislabelled one.
9. **Judge reliability** bounded by κ against two human coders, both of whom are
   authors and neither of whom is a clinician.
10. **Single-jurisdiction choices** where guidelines conflict (§4.2).
11. **English only.** Both corpora and vignettes.

---

## 7. Open questions

- Reframe `G3-03` as a sourced-investigation decision, or demote it to a secondary
  coded outcome? (Direct question for the clinical reviewer.)
- Pick an uncontested prostate decision for `G2-02`, or keep PSA screening and make
  the CUA/CTFPHC disagreement a finding in its own right?
- Does post-training amplify or attenuate the gap (OLMo 2 base vs instruct)? This is
  a genuine open result, not a confirmation.
- Do rationales diverge by gender even where the log-probability answer does not?
  That dissociation would be a result worth its own section.

---

## 8. Running list of things to do before submission

- [ ] Read the two ED-triage preprints and position against them (§2)
- [ ] Fill the verbatim guideline quote blocks in `docs/vignette_sources.md`
- [ ] Write clinical findings + reference answers into `data/vignettes/templates.yaml`
- [ ] Pin the WHO malaria guideline version
- [ ] Specify the `G2-01` clinical decision; replace the `G2-02` decision
- [ ] Send the five clinician emails
- [ ] Confirm NICE review dates for CG142 and NG193 at source
- [ ] Sensitivity check: pythia-6.9b at float32 vs float16
- [ ] Confirm McGill's AI-use disclosure wording against `AI_USE.md`
