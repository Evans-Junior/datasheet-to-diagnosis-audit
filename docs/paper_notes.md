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

### 2.1 The two closest papers — ED triage gender audits

Both verified on arXiv. **Abstracts read; full texts not yet read.**

**Guerra-Adames A, Avalos-Fernandez M, Dorémus O, Celi LA, Gil-Jardiné C, Lagarde E.
Auditing Sex/Gender Disparities in Emergency Triage with LLM-based Paired
Comparisons.** arXiv:2511.17124 (21 Nov 2025; v2 6 Aug 2026), cs.CY.
https://arxiv.org/abs/2511.17124
Trains a model to imitate *observed* triage decisions, then tests pairs of real
records differing only in sex. 140,000+ admissions at Bordeaux University Hospital
plus MIMIC-IV. Identical presentations slightly more likely to receive a
lower-severity score when female: 1.1% (France), 2.2% (MIMIC-IV). The gap appeared
mainly where tabular *and* textual sex markers combined, and **disappeared when the
model was retrained on sex-neutralised inputs**. Framed as documentation-level and
hypothesis-generating, explicitly not evidence of bedside clinician behaviour.

**Young RJ, Matthews AM. EQUITRIAGE: A Fairness Audit of Gender Bias in LLM-Based
Emergency Department Triage.** arXiv:2605.03998 (5 May 2026), cs.CL/cs.CY.
https://arxiv.org/abs/2605.03998
Five LLMs (Gemini-3-Flash, Nemotron-3-Super, DeepSeek-V3.1, Mistral-Small-3.2,
GPT-4.1-Nano); 374,275 evaluations over 18,714 MIMIC-IV-ED vignettes; four prompting
strategies; 9,346 gender-swapped counterfactual pairs. All five exceeded a
pre-registered 5% flip-rate threshold (9.9%–43.8%). DeepSeek undertriaged women
2.15:1, Gemini 1.34:1. Demographic blinding cut Gemini to 0.5%. Chain-of-thought
**reduced** accuracy for all five. A two-model ablation found the same directional
pattern arises from different sources: in Gemini from the combined name-and-gender
swap, in DeepSeek from the gender token alone.

#### What this means for our positioning

**EQUITRIAGE overlaps G3-02 directly and at far greater scale.** Demote cardiac
triage from a headline vignette to one condition among seventeen; do not compete on
their ground with 288 prompts against their 374,000.

**What survives — and it is the whole project.** Neither has training-data access:
EQUITRIAGE audits five closed models, Guerra-Adames trains on hospital records. So
RQ1, RQ3 and RQ4 are impossible for both. Our contribution is not "LLMs show gender
bias in triage" — that is now established by others — it is **where the bias comes
from**. Lead with the data link, not the output gap.

**Three findings that help us:**
- EQUITRIAGE's ablation (Gemini: name+gender combined; DeepSeek: gender token alone)
  is independent empirical support for **D012**, dropping names from the primary
  design. Cite it rather than arguing the point from first principles.
- Their result that chain-of-thought reduced accuracy strengthens **D005**.
- Guerra-Adames's effect vanishing under sex-neutralised retraining is suggestive of
  a data→output pathway — adjacent to RQ4 but without corpus access. Good to
  position against.

**Two differentiators to state explicitly:** both appear to treat gender as binary,
so our non-binary arm is novel ground; and neither has a sex-specific control group,
so neither can show its models correctly differentiate where they should.

**Cautions.** EQUITRIAGE is a two-author preprint, not peer-reviewed, with some
strikingly large numbers — read critically, and do not let a 43.8% flip rate anchor
expectations for a real effect size. Separately, both use **MIMIC-IV-ED** as a
vignette source; that is a real alternative to authoring our own, but it needs
PhysioNet credentialing and would cost us the guideline-anchored invariance rule
that makes our design defensible. Recommend staying with authored vignettes.

**Metric worth borrowing:** their pre-registered **flip rate** against a stated
threshold is a cleaner headline statistic than a raw probability gap, and
pre-registering ours would strengthen the paper.

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

### 4.1a One guideline states gender-invariance outright — NICE NG126

Worth its own paragraph in the paper. Across the whole set, our invariance premise
rests on **interpreting guideline silence** about gender (§4.2, D011). NG126 is the
exception: its scope says it covers "ectopic pregnancy and miscarriage in **women,
trans men and non-binary people**", and it uses "trans men" 9 times and "non-binary"
8 times throughout.

So for G2-01 the claim "correct management does not vary by gender identity" is
**stated by the guideline**, not inferred by us. That single item needs no clinician
to ratify its premise, and it demonstrates that guidelines *can* be explicit about
this — which sharpens the RQ6 argument considerably: when other guidelines are silent,
that silence is a documentation choice, not an inevitability.

**Also a small RQ6 finding in itself:** NG126's recommendation 1.4.5 says "women of
reproductive age" while its scope says women, trans men and non-binary people. The
scope governs, but the recommendation text lags the stated intent — documentation
inconsistency inside a single document, which is exactly the phenomenon RQ6 codes for.

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

**(b0) Cached rate-limit errors read back as zero counts (D022).** The first RQ1
probe reported 16 of 20 concepts as having zero gender co-occurrence, and gave
dramatic skew for the rest (pneumonia −5.9, asthma +2.3). All of it was an artefact:
infini-gram rate-limits with HTTP 403 and a body of `{"message": "Forbidden"}`, which
carries no `"error"` key, so our client treated it as success and **cached it** — after
which it read back as `cnt = 0` forever. 287 of 378 cached entries (76%) held
"Forbidden", and the non-zero rows were sums over nine gender terms mixing blocked and
successful queries, so those ratios were meaningless too.

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

**The common pattern — worth a paragraph of its own.** Three bugs (D013, D015, D022),
all of which produced *plausible-looking results rather than errors*, and all three
caught by inspecting output rather than reading code. One manufactured a clean effect,
one manufactured a clean null, one manufactured dramatic false skew. The project's
standing rule is now: any result that looks clean, dramatic, or exactly zero gets a
numerical and provenance check before it gets an interpretation.

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

## 4a. RQ1 headline result (D024)

Full sweep: 1,504 queries, 0 failures, 42 powered rows across two corpora.

**Validation.** cervical cancer +9.25 (Pile) / +7.74 (OLMo-mix); prostate -6.47 /
-6.07. **Cross-corpus agreement r = 0.931, rho = 0.936** on 15 shared concepts.

**Centre before interpreting.** Mean sex-neutral skew is +0.778 (Pile) / +0.560
(OLMo-mix) -- a baseline female skew in illness-narration frames. Zero is not a
reference point.

**Centred skew by family, identical ordering in both corpora:**

| Family | OLMo-mix | Pile |
|---|---|---|
| neurodevelopmental | -0.974 | -0.812 |
| cardiac | -0.929 | -0.671 |
| other somatic | +0.180 | +0.058 |
| pain | +0.287 | +0.107 |
| psychological | +0.804 | +0.651 |

Each limb matches a documented human bias: psychologizing of women (Hoffmann &
Tarzian), cardiac under-recognition in women (Pilote), ADHD/autism under-diagnosis
in women and girls.

**The strategic consequence.** RQ1 now generates signed, *a priori* predictions for
RQ2 -- psychologize women more, triage women's chest pain lower, refer women less
for ADHD/autism. Pre-registering these before Phase 2 runs converts a post-hoc
correlation into a confirmed prediction, which is a far stronger claim. **Write them
down before scoring anything.**

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

- [x] Identify and assess the two ED-triage preprints (§2.1) — abstracts read
- [ ] Read both ED-triage preprints in **full**; decide whether to adopt a
      pre-registered flip-rate metric (§2.1)
- [ ] Fill the verbatim guideline quote blocks in `docs/vignette_sources.md`
- [ ] Write clinical findings + reference answers into `data/vignettes/templates.yaml`
- [ ] Pin the WHO malaria guideline version
- [ ] Specify the `G2-01` clinical decision; replace the `G2-02` decision
- [ ] Send the five clinician emails
- [ ] Confirm NICE review dates for CG142 and NG193 at source
- [ ] Sensitivity check: pythia-6.9b at float32 vs float16
- [ ] Confirm McGill's AI-use disclosure wording against `AI_USE.md`

---

## 4b. Pre-registration (D025)

RQ2's hypotheses were fixed in `docs/preregistration.md` and committed before any
analysis-ready score existed. For the write-up, three framing points matter more
than the hypothesis list itself.

**Word the claim precisely.** RQ1 was observed before the predictions were written
— deliberately, since the predictions are derived from it. The claim is "committed
before any analysis-ready output was generated," not "pre-registered blind." A
reviewer who spots the difference and finds us overclaiming will discount the whole
result; one who sees us state it ourselves will not. §1 of the pre-registration
makes the concession explicitly, including declaring the pythia-70m placeholder
smoke run.

**The discriminant null is the interesting hypothesis.** H3 predicts *no* gap on
the unskewed somatic conditions (G1-*, G4-*). An audit finding gaps everywhere
shows much less than one finding them exactly where the corpus is skewed — the
latter is a mechanism claim, the former just a sentiment. So H3 failing hurts the
thesis more than H1 or H2 failing, and the paper should say that before showing
results, not after.

**G3-01 is the one place our mechanism contradicts the field.** The corpus predicts
models give women *more* analgesia (pain is mildly female-skewed after centring;
*severe pain* +0.63 in OLMo-mix); Hoffmann & Tarzian predict less. Both directions
are pre-specified, G3-01 counts as confirmatory for neither, and whichever way it
falls gets reported. Volunteering a case where our own mechanism makes the
counter-intuitive prediction is worth more to the paper's credibility than a
uniformly supportive result would be.

**The gate to report first.** Group 2's answers genuinely differ by sex, so Δ must
be large there. If it is not, the instrument is insensitive and every null is
uninterpretable — H3 included, which means the mechanism claim cannot be made
either way. Group 2 effect size therefore goes in the results before anything else.

**Asymmetry to state, not bury.** RQ1 has no non-binary measure while RQ2 has a
non-binary arm. The non-binary arm is part of the novelty claim, so the paper has
to say the linkage analysis cannot cover it.

---

## 4c. Non-binary patients are absent from the clinical subject position (D026)

This is the finding to lead the ethics section with, because it is a single clean
number rather than an inference.

`"the non-binary patient"` occurs **zero times** in the Pile and zero times in
OLMo-mix-1124. `"the non-binary patient has"` likewise zero. Against that:
`"the woman has"` 646,440 occurrences in OLMo-mix, `"the man has"` 1,139,475.

The move that makes this a result rather than a vocabulary gap is the control:
the bare term `"non-binary"` returns **1,350,944** occurrences in OLMo-mix and
66,269 in the Pile. Non-binary people are in these corpora. They are not in them
*as patients*.

**Why this is stronger than a representation-count argument.** The usual framing
is that a group is underrepresented and therefore served worse. Here the relevant
distribution is not thin, it is empty, and empty in a specific grammatical
position that the audit then probes directly. The model is asked to reason about a
non-binary patient; the training data contains no instance of that construction.
Whatever the model does in that arm, it is not drawing on narration of non-binary
illness, because none exists in its data.

**Use it carefully in two respects.** It postdates the D025 freeze, so the
downstream prediction (less stable, less concordant non-binary outputs) is
exploratory, not confirmatory — say so. And the measure is phrase presence, so the
claim is about this construction, not about all possible ways a non-binary patient
might be described; `"the transgender patient has"` returns 53 and 2, which is
near-absence of a different construct rather than the same one.

## 4d. Referral language carries the gender skew too (D026)

The confirmatory hypotheses are about decisions — H1 referral, H2 triage — but
until now the corpus measured only which *diagnoses* attach to which gender,
leaving a gap between the predictor and what RQ2 scores. Measuring referral and
treatment frames directly closes it:

**Cardiology referral is male-associated (−0.811 centred); psychiatry referral
(+0.127) and antidepressant prescription (+0.306) are female-associated.** The
cardiologist/psychiatrist gap is 0.94 log2 units, roughly 1.9x.

So the psychologizing pattern is present in *decision* language, not only in
diagnosis attachment. That matters because G3-03 was dropped (D020) and
psychologizing was otherwise reachable only through judge-coded rationales — the
weakest instrument in the project. It now has corpus evidence at the level the
hypotheses operate on.

Report it as **single-corpus**: the Pile powered only 2 of 14 decision concepts,
so this cannot claim the r = 0.931 cross-corpus replication that the diagnosis
family can. And prefer within-family contrasts over absolute centred values, since
the centring base here is the 13 measured concepts rather than a broad sex-neutral
pool.

## §4e — The guidelines are more inclusive than the data (D034)

The sharpest version of the datasheet-to-diagnosis argument came out of sourcing,
not modelling, and it is one sentence long: **the clinical guidance is more
inclusive than the training data can support.**

Two of the governing guidelines state the gender-identity/anatomy decoupling
themselves, rather than leaving us to impose it. CUA MLUTS/BPH: *"We acknowledge
that not all patients identify as male. These guidelines should also be applicable
to non-binary people, transwomen, and any patients who may have anatomical features
of a cis-male genitourinary tract, such as a prostate."* NICE NG126's scope covers
trans men and non-binary people. In both, the operative criterion is anatomy — the
HL7 **SPCU** — and identity is explicitly *not* determinative.

Against that, the RQ1 corpus result: `"the non-binary patient"` occurs **zero
times** in both the Pile and olmo-mix-1124, in a frame where `"the woman has"`
occurs 646,440 and 20,142 times respectively. Non-binary people are *present* in
the corpora — 1,350,944 and 66,269 bare occurrences of "non-binary" — but absent
from the **clinical subject position**.

So a model trained on these corpora cannot have learned what these guidelines
require, because the data contains no instance of the sentence in which the
requirement would appear. This is not a performance claim and must not be written
as one; it is a claim about what the training distribution makes learnable. It is
also the cleanest available answer to "why audit the data rather than just the
outputs" — an output-only audit would record a failure here, and could not say that
the failure was structurally guaranteed.

**Framing discipline.** Report this as *absence of the clinical subject position*,
not as "the models are transphobic" or as a measured disparity. The non-binary arm
is thin and exploratory (post-dates the D025 freeze); report direction and absence,
never significance. The zero itself was verified by a live probe with a non-zero
control before being reported, because an unverified zero from this API is exactly
what D022 was.

---

## §5 — RQ6 search results: what the documentation does and does not say

Ten documents retrieved 2026-10-28 (`scripts/rq6_fetch.py`, identity-checked),
term counts in `results/tables/rq6_search_counts.csv`. **These are §4 step-2
counts and verbatim passages, not codes.** Coding is the authors' own work and has
not been done; nothing below assigns a D1–D8 level.

### The headline is not "they never mention gender". It is narrower and stronger.

**The Pile measures gender bias, per component, and says so.** §6.4.1 of Gao et
al.:

> "We computed gender associations by computing co-occurrences for binary
> pronouns. For each word, we computed the difference in the rate it co-occurs
> with 'he' and 'she' and weighed it by the square root of its frequency. We
> report the top 15 most biased adjectives or adverbs … for each"

with a stated purpose:

> "Our goal is to provide users of this dataset with preliminary guidance on how
> the different components are biased so that they can make decisions on which
> components to train on."

Figure 13 gives average sentiment by gender **across all components**, and the
component list includes PubMed Central and PubMed Abstracts. So the biomedical
components *were* examined for gender. Their conclusion:

> "Generally, we find no significant sentiment bias towards men or women. This, of
> course, does not mean that the dataset is free of gender bias (as our
> co-occurrence tests show)."

That last sentence is an honest caveat and should be quoted as one. The Pile
authors did not overclaim.

### The gap is three specific things, not an absence of effort

1. **They measured adjectives and sentiment; we measure clinical concepts.** Their
   unit is "which adjectives co-occur with he/she". Ours is "which *diagnoses and
   decisions* co-occur with he/she", which is where the skew we find lives:
   *heart attack* at −1.39, *attention deficit* at −1.16, *autism* at −1.04. A
   sentiment-neutral component can be concept-skewed, and Figure 13 would not
   show it.
2. **Their gender measurement is binary by construction** — "co-occurrences for
   **binary pronouns**", their words. `non-binary` and `transgender` return **0
   hits in both Pile documents**. So the only gender analysis in the entire
   documentation corpus could not have detected the thing D026/D034 identifies:
   `"the non-binary patient"` at zero occurrences, against clinical guidelines
   (CUA MLUTS/BPH, NICE NG126) that explicitly require that population to be
   covered.
3. **Medical use is an intended application, stated twice.** Gao et al.: *"We
   included PMC in the hopes that it will benefit potential downstream
   applications to the medical domain."* The datasheet: *"The PubMed Abstracts
   dataset gives researchers, especially in the medical field, a strong basis for
   building models…"* So this is not a general-purpose corpus being used off-label
   for health. Health was a design goal.

### The two topics never meet

Across all 10 documents, a sentence-level search for any demographic term
co-occurring with any health term returns **three hits, and all three are
artefacts**: two are table/figure label runs in the Pile paper's appendix (the
component list adjacent to Table 10's gender adjectives), and the third is the
*Datasheets for Datasets* question template itself in the Pile datasheet, which
lists "health data" among sensitive categories.

The datasheet's **answer** to that question is worth quoting in full, because it is
the closest any document comes to the intersection:

> "Does the dataset contain data that might be considered sensitive in any way
> (e.g., data that reveals racial or ethnic origins, sexual orientations,
> religious beliefs, political opinions or union memberships, or locations;
> financial or health data; biometric or genetic data …)?
> **The Pile: We do not know the extent to which this is the case, although we
> expect that it does.**"

### The OLMo 2 side is the stark one

| Document | `gender` | `sex` | `female` | `demographic` | `bias` | `health` |
|---|---|---|---|---|---|---|
| Pile paper | 7 | 1 | 3 | 4 | 24 | 9 |
| Pile datasheet | 16 | 1 | 0 | 0 | 5 | 9 |
| Pythia paper | 32 | 0 | 0 | 0 | 60 | 0 |
| Pythia model card | 1 | 0 | 0 | 0 | 3 | 0 |
| Dolma paper | 1 | 0 | 0 | 3 | 13 | 0 |
| **olmo-mix-1124 dataset card** | **0** | 0 | 0 | 0 | **0** | 0 |
| **OLMo 2 report** | **0** | 0 | 0 | 0 | 4 | 3 |
| **OLMo 2 model card** | **0** | 0 | 0 | 0 | 2 | 0 |
| Qwen3 report | 0 | 0 | 0 | 0 | 1 | 0 |
| Qwen3 model card | 0 | 0 | 0 | 0 | 0 | 0 |

The corpus this project queries for OLMo 2 — `olmo-mix-1124` — has a dataset card
containing **zero** occurrences of every gender term, every demographic term, and
the word "bias". The Dolma paper, which documents the corpus family, mentions
`gender` **once** in 64 pages while discussing `harm` twelve times.

### Two cautions before any of this is written up

**The Qwen3 comparison does not say what it looks like it says.** Qwen3's zeros sit
beside an undisclosed training corpus, so there is nothing for its documentation to
characterise. The contrast that matters is Pile-vs-OLMo — two projects that both
released their data, one of which documented gender composition and one of which
did not. That shows the disclosure is a *choice*, not a property of being open.

**Counts are not codes, and a zero is not yet a finding.** Codebook §4 requires a
full read and a structural check before any level-0 code; only step 2 is done. In
particular the OLMo 2 report has 4 `bias` and 3 `health` hits that have not been
read in context, and the Pythia paper's 32 `gender` and 60 `bias` hits are
substantial and unexamined — Pythia is a model suite whose stated purpose is bias
research, so those hits may be about *studying* bias rather than about the corpus's
composition. That distinction is exactly what D7 (measurement vs assertion) exists
to record, and it cannot be settled from a hit count.


---

## §5b — Two things the full read changed, one of them about the project's novelty

### The OLMo 2 absence is cleaner than the counts suggested

Read in context, the OLMo 2 report's hits evaporate:

- All **five** `bias` hits are architectural. *"No biases: we exclude all bias
  terms from our architecture"*; *"RMSNorm … without a bias term"*; a table row
  reading `Biases None None None`; and one reference title (*"…a simple way to
  debias automatic evaluators"*).
- All **three** `health` hits are infrastructure. *"embedding norms settle in a
  healthy region"*, *"GPU health checks"*, *"automatic health checks"*.

So a 58-page report on a fully open model family contains **no discussion of
social bias at all**, and no medical content discussion. The model card carries one
generic sentence — *"Such content may also be produced unintentionally, especially
in cases involving bias, so we recommend that users consider the risks"* — with
gender unspecified. Had the hit counts gone into the write-up unread, the paper
would have claimed this report discusses health and bias. It discusses neither.

### The Pythia paper already did a causal version of H4, and this must be cited

This is the find that matters most, and it is a threat to the novelty claim if
discovered by a reviewer rather than by us. Pythia's §"Mitigating Gender Bias"
reports a **counterfactual retraining intervention**:

> "we analyze whether deliberately modifying the frequency of gendered terms in
> the pretraining data of a language model can have an impact on its downstream
> behavior and biases"

> "we … counterfactually retrain models such that the last 7% and 21% of model
> training has a majority of pronouns modified such that their grammatical gender
> is feminine rather than masculine"

> "To test the effects of corpus statistics on the biases learned by language
> models, we repeat segments of pretraining on specific models, with altered
> corpus statistics."

Measured on WinoBias and CrowS-Pairs, with a clear effect across scale. So the
claim "corpus gender statistics affect downstream gender bias" is **already
established for Pythia specifically, causally, by intervention** — a stronger
design than H4's observational correlation.

**What this does and does not cost us.** H4 cannot be presented as establishing
that link for the first time; written that way, the paper would be visibly unaware
of the suite's own flagship result. Rewritten, three things remain genuinely new:

1. **Domain and outcome.** They measured occupation–pronoun stereotyping
   (WinoBias) and stereotype preference (CrowS-Pairs). We measure
   **guideline-concordance of clinical decisions**, where there is an externally
   defined correct answer and a patient-facing consequence. "Does it associate
   nurses with women" and "does it withhold an ADHD referral from a woman given
   identical findings" are different claims about different harms.
2. **Concept-level rather than pronoun-level corpus measurement.** Their
   intervention manipulated *pronoun grammatical gender* wholesale. RQ1 measures
   the gender skew of **specific clinical concepts** — heart attack −1.39,
   attention deficit −1.16 — which is what lets RQ4 ask whether the gap appears
   *where the skew is*, rather than whether gender signal matters in general.
   H3's discriminant null is only meaningful at concept level.
3. **The documentation arm.** RQ6 has no counterpart in their work.

**And it hands us an opportunity we should state even if we do not take it.**
Pythia exists to support exactly this: 154 checkpoints and a public retraining
codebase. The strongest possible version of this project would intervene on the
*clinical concept* frequencies and retrain, converting RQ4 from correlation to
causation using the mechanism its own authors built. That is out of scope for a
course project on a 48 GB laptop, and saying so explicitly — naming the design we
would run with more compute — is better than leaving a reviewer to propose it.

**Positioning, in one sentence.** The Pile authors measured gender bias in their
corpus but not in clinical concepts; the Pythia authors showed corpus gender
statistics causally affect stereotype benchmarks but not clinical advice; and
neither connected either finding to the health applications the Pile was
explicitly assembled to support. That is the gap, and it is narrower and more
defensible than "nobody has looked at this".
