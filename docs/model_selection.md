# Model and corpus selection, methodology

**Status:** methodology section, written 2026-11-07. Records the reasoning and the
measurements behind the choice of model families. Companion to **D068** (why no
medical model), **D065** (DCLM's corpus is nested in OLMo's), **D069** (the
corpus-independence criterion) and **D070** (DCLM model arms not added).

This section answers a question a reviewer will ask early: *why these models?*
The short answer is not "because their data is open". Openness is the entry
requirement, not the selection criterion. The selection criterion is that the
corpora must be **independent measurements of each other**, and that turned out to
be something this project could *test* rather than assert.

---

## 1. What the research question forces on the design

The RQ1 → RQ4 chain is: measure gender skew in a training corpus; measure
gender-conditioned behaviour in models trained on that corpus; then ask whether
the first explains the second.

The third step is the binding constraint. To ask whether a corpus property
explains a model property, the corpus has to be **counted**, not merely
described. A dataset card saying "web text, filtered for quality" supports no
such inference. What is needed is the ability to ask *how many times does this
exact phrase occur* and get an exact answer, over trillions of tokens.

That is a far stronger requirement than "open weights", and stronger than "open
data" as the phrase is usually used.

---

## 2. Five criteria, in the order they bind

| | Criterion | Why the design needs it | What it rules out |
|---|---|---|---|
| **C1** | Pretraining corpus publicly released **and** indexed for exact n-gram counting | RQ1 and RQ4 are impossible otherwise | Every closed model; every "open-weights, undisclosed-data" model; **every medical LLM** (D068) |
| **C2** | Corpora **mutually non-nested**: verified, not assumed | Two nested corpora give one measurement reported twice, inflating apparent agreement | DCLM as a third corpus arm (D065) |
| **C3** | At least one family with a parameter ladder trained on **fixed data in fixed order** | RQ3's size trend is otherwise confounded by data differences between sizes | Almost every family except Pythia |
| **C4** | Base **and** instruction-tuned checkpoints within one family | Separates pretraining-corpus effects from alignment effects | Families releasing only one or the other |
| **C5** | One closed-data model as contrast | External validity: shows whether the open models behave atypically | n/a |

C1 is a gate. C2 is the criterion this project contributes a test for. C3 and C4
are satisfied by exactly one family each. C5 is a single deliberate exception to
C1, included *because* it fails C1.

---

## 3. C1 eliminates almost everything, and all of medicine

Recorded in full in **D068**. The summary finding, which is a result rather than
an apology:

> There is currently no medical LLM with a fully open, exact-n-gram-queryable
> pretraining corpus at a size runnable on 48 GB. The models a clinician would
> actually be offered are precisely the ones whose data cannot be audited.

This is why the audit runs on general-purpose models. It is not a convenience
sample.

---

## 4. C2, the criterion that is usually asserted and never tested

### 4.1 The idea

Multi-corpus audits normally justify corpus independence by provenance: different
organisations, different release dates, different documentation. That is an
argument about paperwork, not about text.

But the n-gram instrument built for RQ1 can test it directly. If two corpora are
genuinely different samples of written English, their per-concept gender skew
should **correlate but diverge**: the same broad social patterns, different
sampling noise, different editorial mix. If one corpus is largely contained in
the other, skew should be **near-identical**, because it is the same text.

So: run the identical sweep on both corpora and compare the per-concept
`skew_log2` values. No new instrument is needed.

### 4.2 The measurement

141 concepts swept; correlations computed on concepts powered in both corpora.

| Pair | n | Spearman ρ | max \|Δskew\| | median \|Δskew\| | Reading |
|---|---|---|---|---|---|
| **olmo-mix-1124 vs DCLM-baseline** | 27 | **+0.9994** | **0.039** | **0.003** | **One corpus measured twice** |
| Pile vs olmo-mix-1124 | 15 | +0.9357 | 0.782 | 0.176 | Two corpora |
| Pile vs DCLM-baseline | 15 | +0.9357 | 0.790 | 0.187 | Two corpora |

**The discriminant is sharp, not marginal.** The median per-concept disagreement
differs by a factor of about 59 between the nested pair and the independent pairs.
This is not a judgement call about provenance; it is a measurement with a
two-order-of-magnitude gap, and the two independent pairs agree with each other to
four decimal places on ρ, which is what one expects if the Pile is being compared
against essentially the same corpus twice.

### 4.3 Confirmed structurally, two independent ways

The measurement said "same corpus"; the documentation says why.

1. **The dataset card.** `allenai/olmo-mix-1124` lists **DCLM-baseline at 3.70T
   tokens of a 3.90T total**, roughly 95%,  "with no additional filtering."
2. **Direct counts.** The phrase `"she has"` returns **94,109,792** occurrences in
   olmo-mix-1124 against **93,884,699** in DCLM-baseline, a ratio of **1.0024**.

Checking the dataset card first would have made the sweep unnecessary. That is
recorded as an error in reasoning in **D065**, not as a discovery.

### 4.4 Why this is worth stating as a methodological point

"Trained on open data" is routinely treated as if it implied *independently*
open data. It does not. Two of the three largest open pretraining corpora are not
independent samples of text, and this is discoverable either from a dataset card
or from fifteen minutes of n-gram counting, but only if someone looks.

For this project it means **corpus-level attribution in this model family is
impossible in principle, not merely underpowered.** That is a stronger and more
useful limitation than the one it replaced (D054's "two corpora agree at
ρ = 0.976"), because it is structural and verifiable rather than statistical.

---

## 5. Why Pythia and OLMo-2 are the two families that survive

They are not the two open families that happened to be available. They are the
minimal set satisfying C1 **and** C2 simultaneously, and they differ on every axis
that could plausibly matter.

| Axis | Pythia / the Pile | OLMo-2 / olmo-mix-1124 |
|---|---|---|
| Corpus vintage | 2020 | 2024 |
| Corpus scale | ~300B tokens | ~3.9T tokens (≈13×) |
| Construction philosophy | 22 **named, curated** sources assembled deliberately | Model-filtered Common Crawl (DCLM-baseline) plus curated additions |
| Deduplication | Released both as-is and deduplicated | Filtered upstream |
| Parameter ladder on fixed data | **Yes, 70m to 12b, same data, same order** (C3) | No |
| Base + instruct | n/a | **Yes** (C4) |
| Exact n-gram queryable | Yes | Yes |

### 5.1 And they disagree exactly where the experiment needs them to

Corpus independence is only useful if the corpora actually disagree about
something the study measures. They do, and the largest disagreement is the
best-placed one possible:

| Concept | Pile | olmo-mix | DCLM |
|---|---|---|---|
| **attention deficit** | **+0.186** | **−0.597** | **−0.605** |
| pneumonia | +1.328 | +0.950 | +0.951 |
| ADHD | −0.020 | −0.240 | −0.240 |
| autism | −0.269 | −0.475 | −0.477 |

`attention deficit` **flips sign** between the Pile and the olmo/DCLM pair:
female-skewed in the Pile, male-skewed in olmo-mix. That concept underlies
**G3-04, which carries H1**. It is the single largest and most consequential
cross-corpus disagreement in the whole sweep, and **only the Pile/OLMo pair
exposes it**, olmo and DCLM differ by 0.008 on the same concept.

Note also the shape of the table: on every row, olmo and DCLM agree to three
decimal places while the Pile stands apart. The nesting is visible by eye.

### 5.2 The consequence for the model set

Because the Pile is now the **only non-nested corpus in the design**, every Pythia
checkpoint carries unique information and none is redundant. That is the
independent reason all seven sizes were kept rather than trimmed to five (D065),
a decision originally taken for RQ3's size ladder, and now over-determined.

---

## 6. What the 5% that differs actually buys, a null result

olmo-mix-1124 minus DCLM-baseline is roughly pes2o, arXiv and other curated
additions: disproportionately academic and biomedical. That invites an obvious
question, does adding curated biomedical text change the gender skew a health
audit would see?

Measured on the same sweep:

| Quantity | Median | Max |
|---|---|---|
| Co-occurrence **count** ratio, olmo ÷ DCLM | **1.0071** | 1.137 (community-acquired pneumonia) |
| **Skew** disagreement \|Δskew_log2\| | **0.0028** | 0.0391 |

**So: adding curated academic biomedical text at this proportion raises biomedical
volume slightly and moves measured gender skew essentially not at all.** Stated as
a null, because that is what it is. The largest volume effect lands where expected,
the most academic phrasing, "community-acquired pneumonia", at 1.14×, but it
does not propagate into skew.

This is recorded here because an earlier draft of the reasoning claimed the
biomedical remainder diverged substantially and offered it as a reason to retain
DCLM as a model arm. On measurement it does not, and that reason is withdrawn
(see D070).

---

## 7. Qwen3-8B, the one deliberate C1 failure

Included under C5 as a closed-data contrast. It is **not a corpus arm**. No RQ4
statement about Qwen is possible by construction, and that impossibility is the
point: it demonstrates on a model in the same table what the audit cannot do when
the corpus is undisclosed, which is the situation for every deployed clinical
assistant.

---

## 8. The resulting set

| Family | Models | Corpus | Criteria served |
|---|---|---|---|
| Pythia | 7 (70m → 12b) | the Pile | C1, C2, **C3** |
| OLMo-2 | 2 (7B base, 7B Instruct) | olmo-mix-1124 | C1, C2, **C4** |
| Qwen3 | 1 (8B) | undisclosed | **C5** |

Ten models, two independent corpora, one closed contrast. DCLM-7B base and
Instruct were considered and **not added**: see D070 and §6.

---

## 9. Literature this section rests on

| Work | Cited for |
|---|---|
| Biderman et al. 2023, *Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling*, ICML 2023 (PMLR 202:2397–2430), [arXiv:2304.01373](https://arxiv.org/abs/2304.01373) | C3. The only family trained at 8 sizes on identical data in identical order, released in both Pile and deduplicated-Pile variants, explicitly built so that scaling and training dynamics can be studied rather than guessed |
| Gao et al. 2020, *The Pile: An 800GB Dataset of Diverse Text for Language Modeling*, [arXiv:2101.00027](https://arxiv.org/abs/2101.00027) | Corpus 1 provenance: 22 named, individually documented sources, which is what makes its divergence from web-filtered corpora interpretable rather than mysterious |
| OLMo 2 team, *2 OLMo 2 Furious*, [arXiv:2501.00656](https://arxiv.org/abs/2501.00656) | Corpus 2 and the base/instruct pair (C4) |
| Li et al. 2024, *DataComp-LM: In Search of the Next Generation of Training Sets for Language Models*, NeurIPS 2024, [arXiv:2406.11794](https://arxiv.org/abs/2406.11794) | DCLM-baseline's construction by model-based filtering of Common Crawl, the provenance that explains why it dominates olmo-mix by token count |
| Soldaini et al. 2024, *Dolma: an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research*, ACL 2024, [arXiv:2402.00159](https://arxiv.org/abs/2402.00159) | AI2's corpus-documentation lineage, the predecessor to olmo-mix; ~200 TB of raw text curated to 11 TB, released ODC-BY |
| Biderman et al. 2022, *Datasheet for the Pile*, [arXiv:2201.07311](https://arxiv.org/abs/2201.07311) | **Directly relevant to this project's title.** The Pile is one of very few pretraining corpora with a published datasheet in Gebru et al.'s sense, which is part of why corpus 1 can be reasoned about at all. Its existence for the Pile and absence for most corpora is itself the "datasheet" half of *datasheet to diagnosis* |
| Liu et al. 2024, *Infini-gram: Scaling Unbounded n-gram Language Models to a Trillion Tokens*, COLM 2024, [arXiv:2401.17377](https://arxiv.org/abs/2401.17377) | **The instrument C1 depends on.** Exact-substring counting at corpus scale, with an index of ~7 bytes per token; without it C1 is unsatisfiable by any model |
| Elazar et al. 2024, *What's In My Big Data?*, ICLR 2024 spotlight, [arXiv:2310.20707](https://arxiv.org/abs/2310.20707) | The premise, and the precedent for corpus-level auditing: "we have a limited understanding of the content of these corpora". Also the methodological sibling, count-and-search over 35 TB on one node |
| Feng et al. 2023, *From Pretraining Data to Language Models to Downstream Tasks: Tracking the Trails of Political Biases Leading to Unfair NLP Models*, ACL 2023 **best paper**, [arXiv:2305.08283](https://arxiv.org/abs/2305.08283) | **The closest methodological relative.** Runs the corpus-property → model-property → downstream-unfairness chain for political bias; this project runs it for gender in clinical advice. Their finding that unfairness can arise from "non-toxic and non-malicious data" is the premise for auditing skew rather than toxicity |
| Dodge et al. 2021, *Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus*, EMNLP 2021, [arXiv:2104.08758](https://arxiv.org/abs/2104.08758) | Documentation debt: what filtering decisions remove, and who they remove |
| Gebru et al. 2021, *Datasheets for Datasets*, CACM 64(12) | The "datasheet" in this project's title, and the normative standard the corpora are held to |
| Bender et al. 2021, *On the Dangers of Stochastic Parrots*, FAccT 2021 | Scale versus curation; why corpus size does not imply representativeness |

### What is genuinely new here relative to that literature

Elazar et al. and the corpus-documentation line ask *what is in a corpus*. Feng et
al. ask *whether a corpus property propagates into model behaviour and downstream
harm*. Neither asks **whether two corpora presented as separate are separate**, and
neither offers a test for it.

The contribution in this section is small but, as far as the searches found,
unclaimed: **the same n-gram instrument used to measure corpus skew can be used to
falsify corpus independence**, and when applied to the three largest open
pretraining corpora it shows that two of them are the same corpus. Any multi-corpus
audit should run this check before treating its corpora as replicates.
