<!-- Slide number: 1 -->
From Datasheet to Diagnosis
Tracing gender bias through open training-data pipelines into LLM health advice
Evans Kumi  and  Aymen Boustani
McGill University  ·  MSc Intelligent Systems  ·  ECSE-557 Ethics in Artificial Intelligence
Living document  ·  last updated 4 November 2026

### Notes:
This deck is the running record of the project. It is updated whenever something critical changes, and every slide carries the date of the run it reports. All model-side numbers remain provisional until a clinician passes the vignettes.

<!-- Slide number: 2 -->
The project in one slide
Most audits can prove a model is biased. None can say where the bias came from, because the training data is closed.
1
The opening
2
The instrument
3
The result
4
The contribution
Pythia and OLMo 2 publish their full training corpora, queryable by exact n-gram. For these models the data and the behaviour can be put side by side.
15 guideline-sourced clinical vignettes expanded to 384 prompts, a measured noise floor per model, and a pre-registered analysis plan frozen before scoring.
The chain can be completed, but not yet closed. Three of ten models can do the clinical task. Corpus provenance turns out not to be identifiable between these two corpora.
A working instrument, a pre-registered null, and a measured account of exactly where the datasheet to diagnosis chain breaks.
THE ONE-SENTENCE VERSION
The clinical guidance is more inclusive than the training data can support. Two of our source guidelines explicitly require care for non-binary and trans patients, and the phrase "the non-binary patient" occurs zero times in either corpus.
2

### Notes:
Lead with the closed-data problem, then the opening that makes this project possible, then be honest that the chain is not yet closed. The one-sentence version at the bottom is the line to repeat if you only get one sentence.

<!-- Slide number: 3 -->
What this deck covers
The problem and objective
Related work
1
2
Why output-only audits stop at the model boundary, and the six research questions.
What the literature established, and the four places it directly changed our design.
Methodology
Results and analysis
3
4
The vignette groups, the prompt grid, the invariance rule, scoring, statistics and the gate.
The gate, the hypotheses, the exploratory finding, scale, linkage, representation and documentation.
Instrument fix round 1
Limitations and conclusions
5
6
A measurement error found on 3 November, the four results it moved, and how tuning stayed disclosed.
What is still broken, what would change our mind, and what remains to be done.
3

### Notes:
Six sections. Sections 1 to 3 are stable. Sections 4 and 5 change as runs complete, and section 6 is the part to revisit before every supervisor meeting.

<!-- Slide number: 4 -->
1.  The problem, and the objective
Why an audit that can only see outputs cannot support an intervention
4

<!-- Slide number: 5 -->
Existing audits stop at the model boundary
Gender bias in clinical LLM output is a settled empirical question. Zack et al. [24] showed GPT-4 reproduces racial and gender patterns in clinical vignettes. Chang et al. [3] found anti-LGBTQIA+ bias across four models. Two 2026 emergency-triage audits [9, 23] replicate it at scale.
THE USUAL SITUATION
Training data
Model
Biased advice
Conclusion available:  "the model is biased."  Supports no intervention, because the cause is unreachable.
closed
Audits can measure here
OUR STARTING POINT
Training data
Model
Advice
Question available:  does the skew in the data predict the gap in the advice?
published, queryable
Measurable end to end
A third leg makes it an ethics claim rather than a measurement: we also read the datasheets, to ask whether the documentation disclosed the risk the data and the models demonstrate. That is what makes the title literal.
5

### Notes:
The top row is every audit in the literature. The bottom row is what open corpora make possible. The distinction to stress is that we are not claiming a better bias measurement, we are claiming a reachable cause.

<!-- Slide number: 6 -->
Objective and the six research questions
OBJECTIVE
To test whether the chain from a published datasheet to a specific piece of clinical advice can be completed at all, and to report on where it breaks.
The contribution is not another demonstration that models show gender bias, which is established. It is a working instrument, a pre-registered null, and a measured account of the break points.

|  | Research question | Status |
| --- | --- | --- |
| RQ1 | Is there a measurable gender skew in how illnesses are described in the open corpora? | Final |
| RQ2 | Do models give different clinical advice when only the patient's gender changes? | Provisional |
| RQ3 | Does that difference grow with model size? | Provisional |
| RQ4 | Does a model's output gap follow the skew in its own training corpus? | Not identifiable |
| RQ5 | Are non-binary patients represented at all in the corpora? | Final |
| RQ6 | Do the published datasheets disclose gender composition and connect it to health use? | Final |

RQ4 changed status on 3 November. It is now reported as a measured non-identifiability result rather than a provenance estimate.
6

### Notes:
Three of six research questions are final. RQ2 and RQ3 stay provisional until a clinician passes the vignettes. RQ4's status change is the most significant revision since the interim report, and slide 24 explains it.

<!-- Slide number: 7 -->
2.  Related work, and how it changed the design
Four bodies of work, and the specific design decision each one forced
7

<!-- Slide number: 8 -->
Gender bias in clinical language model outputs
Cirillo et al. 2020  [4]
WHAT THIS ESTABLISHED
Sets out why sex and gender bias in health AI differs from other domains: clinical correctness sometimes genuinely depends on sex, so an audit that cannot separate a legitimate clinical difference from an illegitimate one is useless.
That clinical LLM gender bias exists is not in question. Our contribution cannot be another demonstration of it.
Zack et al. 2024  [24]
Cirillo's observation drove our central design rule: a gender difference counts as bias only where the clinically correct answer is the same for every patient. That rule is what Group 2 of our vignette set exists to enforce.
GPT-4 reproduces racial and gender patterns in clinical vignettes. Established that the effect is real in a frontier model, and set the vignette-based method we build on.
Chang et al. 2025  [3]
Anti-LGBTQIA+ medical bias across four large language models. Extends the question past the gender binary, which most audits do not do.
THE GAP WE TARGET
Every model these studies audit was trained on data the public cannot inspect, so the question stops at the model boundary. None can say where the bias originates.
Loge et al. 2021  [14]
Q-Pain measures social bias in pain management through question answering. A direct precedent for scoring fixed answer options rather than free text.
8

### Notes:
Four papers, one conclusion: the phenomenon is established, so a project that only re-demonstrates it adds nothing. Cirillo is the one that shaped our method rather than our motivation.

<!-- Slide number: 9 -->
What the 2026 triage audits changed for us
Two 2026 emergency-triage audits [9, 23] cover gender bias in triage at far greater scale than we could. Our cardiac vignette is demoted from a headline result to one condition among fifteen. Three things survive, and two of our existing choices gain support.
1
Neither has corpus access
2
Both treat gender as binary
3
Neither has a sex-specific control
So neither can ask where the bias originates. This is the whole space our project occupies.
So neither speaks to non-binary patients. Our third gender arm is carried throughout, not added as an extra.
So neither can show its models correctly differentiate where they should. Our Group 2 does exactly this, and it is why we can tell a null from a blind instrument.
Their findings also support two choices we had already made
SUPPORTS EXCLUDING PATIENT NAMES
SUPPORTS SCORING OPTIONS, NOT FREE TEXT
In one model the effect arose from the gender token alone. A name carries ethnicity and class signal alongside gender, so a name-based manipulation would confound the variable we are isolating. Our prompts use an explicit label and pronouns only.
Chain-of-thought prompting reduced accuracy in all five models they tested, which matches Turpin et al. [21] on unfaithful explanations. We score probability on fixed options instead, which buys determinism.
9

### Notes:
This slide is the honest response to a reviewer asking whether recent work scooped us. It did on the cardiac condition, and we say so. What survives is the corpus access, the non-binary arm and the positive control, and their results independently back two of our method choices.

<!-- Slide number: 10 -->
Sex and gender as an operational standard
We do not invent a definition. Borrowing an existing clinical standard is what lets us separate a legitimate clinical difference from an illegitimate one in code rather than in prose.
HL7 GENDER HARMONY MODEL  [15]
NON-BINARY REPRESENTATION  [5]
Separates gender identity from the Sex Parameter for Clinical Use, which is the single value a clinical system should consult when a decision depends on physiology.
Dev et al. show the harms of gender exclusivity in language technologies. Their work is why the non-binary arm is primary throughout rather than an afterthought.
One mechanical consequence. Verb forms are carried per arm, so singular they takes plural agreement. If the non-binary arm alone contained ungrammatical text, its sequence probability would fall because it reads as bad English, not because of bias. That would have manufactured a finding.
Gender identity
Sex parameter
varies in our prompts
held fixed in our prompts
WHY THIS MATTERS FOR THE RESULT
Crossing the two gives transgender configurations without naming them. Two sex-parameter values times three gender identities yields six combinations. Sex parameter female with identity man is a transgender man. Sex parameter male with identity woman is a transgender woman. The model is never told the patient is transgender: the configuration simply exists in the prompt grid. This is what produced our main exploratory finding, and the standard is the only reason it was available to find.
10

### Notes:
The Gender Harmony Model is doing real work here, not decorating the method. Without separating identity from the sex parameter there is no way to hold the clinically relevant fact fixed while the label moves, and the transgender configurations would not exist in the data at all.

<!-- Slide number: 11 -->
The corpora, the tooling, and what the models were built for
The Pile  [7]  and its datasheet  [1]
WHAT EACH FAMILY WAS ACTUALLY BUILT FOR
The most thoroughly documented large corpus in public. Trained Pythia.
Neither open-data family was built to answer clinical questions. This is a confound, and we state it rather than treat the models as interchangeable.
Dolma  [20]  and OLMo 2  [18]
Pythia  [2]
A scientific instrument for studying training dynamics. Eight sizes trained on identical data in identical order, 154 checkpoints each, and no attempt at competitive benchmark performance. It was built to be studied, not to be used.
Documents the corpus family behind OLMo 2, our second open-data model.
Datasheets for Datasets  [8]
Supplies the structure for our documentation analysis. Our codebook asks of each document whether it discloses gender composition and connects it to downstream health use.
OLMo 2  [18]
Built to be a genuinely open and capable model, with the full data, code and recipe released. Closer to a usable system, and it shows in the results: both OLMo models now pass our gate and no Pythia model does.
Infini-gram  [13]
Exact n-gram counts over both corpora through an API. This is the tool that makes corpus measurement possible at all.
A limit we hit. Infini-gram has no prebuilt index for the newer open corpora, so switching to a more capable open model would break the corpus linkage entirely.
Qwen3-8B [19] is included as a closed-data capability reference, not as an audit target.
11

### Notes:
The purpose question matters because a marker will ask why the open models perform so badly. The answer is that Pythia was never built to answer questions, and that is a property of the model set we inherited, not a flaw in the instrument.

<!-- Slide number: 12 -->
How the literature became design decisions
Each row is a specific mechanism in the repository, traceable to the work that forced it.

| From the literature | What we built because of it |
| --- | --- |
| Clinical correctness sometimes depends on sex [4] | Every vignette carries a reference answer quoted from a named guideline, with that guideline's own strength-of-recommendation grading |
| Gender identity is not a clinical sex parameter [15] | The Gender Harmony distinction is built into the prompt grid: the sex parameter is held fixed while identity varies |
| Non-binary erasure in language technology [5] | A third gender arm throughout, with per-arm verb agreement, and a corpus measure that reports absence as a result |
| The gender token alone can drive the effect [9, 23] | Patient names excluded entirely, so ethnicity and class signal cannot confound the gender manipulation |
| Chain-of-thought explanations are unfaithful [21] | Deterministic log-probability scoring of fixed options, never free-text generation |
| Documentation structure for datasets [8] | A written codebook, coded independently by both authors, with inter-coder agreement reported whatever it is |
| Corpus-level bias amplification [25] | Corpus skew measured as a base-rate-normalised log ratio and centred, so a raw frequency difference is not read as skew |

12

### Notes:
This is the slide that answers whether the literature review is decorative. Every row names a mechanism a reader can find in the repository.

<!-- Slide number: 13 -->
3.  Methodology
The instrument, the prompt grid, the invariance rule, scoring, statistics and the gate
13

<!-- Slide number: 14 -->
What is being designed is an instrument, not a model
The deliverable is an audit instrument with four parts, in one reproducible repository.
1
2
3
4
A clinical stimulus set
A scoring pipeline
A corpus measurement tool
A pre-registered analysis plan
15 vignette templates expanded to 384 prompts. Each carries a correct answer quoted from a named guideline and a confidence tier.
Deterministic log-probability scoring of fixed options, with a four-test validation suite and a measured noise floor per model.
Exact templated n-gram counts over the Pile and the OLMo mix, base-rate normalised and centred.
Four directional hypotheses, a positive and a negative control, and a multiple-comparison correction, frozen before any model was scored.
WHO IT IS FOR, AND WHAT THEY MUST NOT GET

| Stakeholder | What they get | What they must not get |
| --- | --- | --- |
| Dataset publishers | A measurable disclosure gap in their own documentation | A claim that releasing data was a mistake |
| Model releasers | An instrument that tells a model with no gender gap apart from an instrument too insensitive to find one | A benchmark score to optimise against |
| Regulators and funders | Evidence that open training data is necessary but not yet sufficient for accountability | A ranked list of biased models |
| Clinicians | A reviewable statement of what each guideline requires, in a form they can correct | Any suggestion that the vignettes are patients |

14

### Notes:
The right-hand column is the ethics of the design. It says what the instrument refuses to be used for, and those refusals are enforced in code, not just stated.

<!-- Slide number: 15 -->
Four vignette groups, each with a job in the design
5
3
4
3
vignettes
vignettes
vignettes
vignettes
Group 1
Group 2
Group 3
Group 4
Sex-neutral conditions, unskewed in the corpus
Sex-specific conditions: pregnancy test, prostate, cervical screening
Historically biased conditions: ADHD, autism, cardiac, pain
No documented bias, gender clinically irrelevant
Discriminant null. Carries H3
Positive control. A null here invalidates the run
Where an effect is predicted. Carries H1 and H2
Noise baseline, and since 3 November the source of the floor
WHY GROUP 2 IS THE MOST IMPORTANT GROUP
Group 2 is where the guideline answer genuinely does depend on the sex parameter. A model that understands the clinical task must show a difference there. A model that does not cannot be used to argue that an absence of gender difference anywhere else is an absence of bias. This single group is what separates a real null from a blind instrument, and it is reported before every other result.
15

### Notes:
Groups 1 and 4 both predict no effect but for different reasons: Group 1 is a clinical claim, Group 4 is an instrument baseline. Keeping them separate is what lets us measure the noise floor without contaminating the hypothesis test. That distinction became important on 3 November.

<!-- Slide number: 16 -->
How 15 templates become 384 prompts
Every slot in a template is identity. The clinical text is identical across every arm of a vignette, so only the identity marking changes.
15
3
2
4
360
x
x
x
templates
paraphrases
sex parameter
values
arms: woman, man,
non-binary, blinded
prompts
plus 24 for G3-02, which carries a second crossed condition: a psychologizing cue, present and absent.  Total 384.
WHY THREE PARAPHRASES
WHY NO PATIENT NAMES
THE BLINDED ARM
The same clinical facts written three ways, with the identity slots in different positions. Without this, a result might be an artefact of one sentence shape: if the gender word always sits in the same place, we are measuring that position as much as the word.
A name carries ethnicity and class signal alongside gender, so a name-based manipulation would confound the thing being isolated. Gender is conveyed only by an explicit label and pronouns.
A fourth arm with identity removed but the sex parameter kept. It is a reference point, not a fourth gender, and every row carries a flag so the statistics cannot pool it into the three-way comparison. The identity clause is nearly empty of meaning there, so pooling it would quietly contaminate the contrast.
16

### Notes:
The arithmetic is 15 times 3 times 2 times 4 equals 360, plus 24 for the one vignette that carries a crossed cue, giving 384. Every prompt has a matched partner identical in template, paraphrase, sex parameter and clinical text, differing only in identity marking. Those matched pairs are the unit the whole analysis is built on.

<!-- Slide number: 17 -->
Crossing the sex parameter with identity
Two sex-parameter values times three gender identities gives six configurations. The model is never told a patient is transgender. The configuration simply exists in the prompt grid.
Identity:  woman
Identity:  man
Identity:  non-binary
Sex parameter:
female
cisgender woman
transgender man
non-binary,
female parameter
Sex parameter:
male
transgender woman
cisgender man
non-binary,
male parameter
The two highlighted cells are where identity and the sex parameter disagree, which is the situation of a transgender patient. A trans man receives less probability on an indicated pregnancy test. A trans woman receives more probability on a cervical screening not indicated for her. This is the configuration our main exploratory finding sits in.
17

### Notes:
This is the single most important methodology slide. Walk the grid slowly. The point to land is that the transgender configurations are produced by the design rather than written into any prompt, so the model cannot be responding to the word transgender.

<!-- Slide number: 18 -->
The invariance rule, and how we grade it
A gender difference counts as bias only where the correct answer is the same for every patient. Guidelines state management but are usually silent on gender, and reading silence as invariance is a judgement. So we grade it per item rather than assume it.
The guideline names the disparity we predict, in our own outcome variable. NICE NG87 [16] does this for ADHD referral.
4
Strongest
1 item
The guideline states invariance within its scope. NICE NG126 [17] does this for the pregnancy item and explicitly covers trans men and non-binary people.
3
Strong
several
The guideline stratifies by sex elsewhere in the same document but not for our condition. The authors demonstrably had sex in mind and chose not to stratify, which makes the silence a considered omission.
2
Moderate
several
Silence alone, in a document that never stratifies by sex anywhere. These are labelled as such and are the ones to challenge first.
1
Weakest
2 items
All fifteen guidelines were read at first hand, and nine are quoted verbatim in the repository with section-level locators and the guideline's own strength-of-recommendation grading. Reading them changed four of our own earlier decisions, including one reversal.
18

### Notes:
This grading is the answer to the project's weakest assumption. We do not claim silence means invariance. We grade how much inference each item requires and label the two weakest items so a reader can discount them.

<!-- Slide number: 19 -->
Two outcomes, scoring, and the validation that gates it
TWO OUTCOMES, NEVER MIXED UP
SCORING BY POINTWISE MUTUAL INFORMATION
O1, guideline concordance. Probability on the guideline-correct option. This is what a patient experiences as better or worse care.
O2, target-diagnosis endorsement. Probability on the option naming the target diagnosis, correct or not. This is the outcome the corpus mechanism speaks to, and it does not flip sign with the guideline.
Options are scored by PMI, which subtracts each option's unconditional probability. Without that subtraction a common answer string looks like a clinical preference. All three score statistics are computed and reported, so a result that appears under only one of them is visible as such.
Before any result is computed, a four-test validation suite runs against the real scoring path
T1
T2
T3
T4
Determinism
Signal recovery
Nuisance floor
Score-key robustness
Identical inputs must score identically, bit for bit. Any drift means the gender gap is confounded with run-to-run noise.
The scorer must recover an answer planted in the prompt in plain words. If it cannot, a null result is uninterpretable.
A gender token with no clinical content still moves the distribution. That movement is the floor, and an effect below it is not a finding.
No score statistic is length-neutral, so option sets are held within a two-token spread and all three keys are reported.
T3 is the test that failed us. On 3 November the nuisance floor turned out to have been measured on the wrong stimulus geometry, and it was inflated roughly eight and a half times. Slide 23 explains it.
19

### Notes:
The validation suite is what makes a null interpretable. Run it before any interpretation, on every model. T3 is the one that found the measurement error, which is the suite doing its job even though the fault was in the suite itself.

<!-- Slide number: 20 -->
Statistics, pre-registration and the gate
THE UNIT OF INFERENCE
THE RESOLUTION LIMIT
The unit is the vignette, not the prompt. Prompts within a vignette share clinical text and are not independent. Treating them as independent observations rejected a true zero at p = 0.025 in simulation, so the error is not theoretical.

Confidence intervals come from a cluster bootstrap over vignettes with 10,000 resamples, and the four hypotheses carry a Holm correction.
A design with k clusters cannot resolve a p value finer than 2 to the power of minus k. H1 rests on two vignettes, so its finest resolvable p is 0.25. The gate rests on three, giving 0.125.

This caught a real false positive: H1 originally reported p = 0.0001 with reject set to true, on two clusters. Clamped to what the design supports it does not reject, and an exact sign-flip test agrees.
THE PRE-REGISTERED GATE
The four hypotheses were fixed in a dated commit before any model was scored. That document also commits to a gate.
Report the Group 2
effect first
Is it larger than
the model's own floor?
Yes:
results mean something
No:
run declared
insensitive
The gate is the mechanism that stops us presenting insensitivity as fairness. It is the reason this project can report a null honestly.
20

### Notes:
Three defensive points live here: the inference unit, the resolution limit and the gate. Each one removed a false positive we had already produced, which is the strongest evidence that the pre-registration is doing work rather than decorating the project.

<!-- Slide number: 21 -->
From a normative commitment to a mechanism that enforces it
Fifty-seven numbered decisions are logged with dates and reasons. The six below carry the project's values into mechanisms, which is how the design makes its ethics testable rather than merely stated.

| Commitment | Mechanism that enforces it | What it prevents |
| --- | --- | --- |
| A difference is bias only where the answer should not differ | Reference answers quoted from named guidelines with their own grading, plus Group 2 as a positive control | Asserting invariance instead of sourcing it |
| Gender identity is not a clinical sex parameter | The Gender Harmony distinction is built into the prompt grid, with the sex parameter held fixed while identity varies | Treating trans patients as an edge case |
| Non-binary people are patients, not an afterthought | A third gender arm throughout, and a corpus measure that reports absence as a result | Binary-only findings presented as complete |
| A null must be distinguishable from blindness | A measured noise floor per model, and a gate that must pass before any result is reported | Presenting insensitivity as fairness |
| Findings are fixed before they are seen | Append-only pre-registration in a dated commit, with every deviation logged | Choosing the analysis after seeing the result |
| Our own AI use is part of the evidence | Provenance and clinician approval kept as separate fields on every item | Relabelling an item in a way that hides how it was drafted |

21

### Notes:
If a marker asks what makes this an ethics project rather than a measurement project, this is the slide. Each row is a value, a mechanism and a failure mode it closes.

<!-- Slide number: 22 -->
4.  Results and analysis
All model-side numbers are provisional until a clinician passes the vignettes
22

<!-- Slide number: 23 -->
The scale of the run, and one standing caveat
READ THIS BEFORE QUOTING ANY NUMBER
All 11,520 option rows come from vignettes no clinician has passed. Every table and figure in the repository carries verification_status = PROVISIONAL__unverified_ai_drafted, and the stats run prints that these numbers are computed, not reportable, before it prints anything else.
10
384
11,520
1,504
57
models scored
prompts
option rows
corpus queries
logged decisions
7 Pythia sizes, OLMo 2 base and Instruct, Qwen3-8B
From 15 guideline-sourced vignette templates
5,760 matched pairs for each of the two outcomes
Zero failed. Replicates across both corpora at r = 0.931
Each with a date, a reason, and reversals recorded
WHY WE RAN IT EARLY ANYWAY
Our own design rule says no number is reportable on a vignette a clinician has not passed. It does not say the number may not be computed. So we ran the audit now, stamped every row unverified, and we will run it again on the corrected set. The difference between the two runs is a measurement of how much AI-drafted stimulus error moves a bias estimate, which nobody in this literature reports.
23

### Notes:
Say provisional out loud every time you give one of these figures. The justification for running early is methodological, not an excuse: the before and after comparison is itself a contribution.

<!-- Slide number: 24 -->
The gate: can the instrument see a difference that is really there?
The gate flips only the sex parameter and holds every word of clinical text fixed, so a model that understands the task must show a positive margin. A margin inside the model's own noise floor means it does not.

### Chart: Gate margin against each model's own noise floor

| Category | Gate margin | Matched noise floor |
| --- | --- | --- |
| Qwen3-8B | 0.0506 | 0.0131 |
| OLMo-2-7B Instruct | 0.0199 | 0.0106 |
| OLMo-2-7B base | 0.0175 | 0.0078 |
| pythia-410m | 0.0015 | 0.0037 |
| pythia-1b | -0.0007 | 0.0059 |
| pythia-2.8b | -0.0005 | 0.0109 |
| pythia-6.9b | -0.0019 | 0.0025 |
| pythia-1.4b | -0.0035 | 0.0116 |
| pythia-70m | -0.0035 | 0.0049 |
| pythia-160m | -0.0063 | 0.0122 |

3 of 10
models clear their own floor
Qwen 3.86x,  OLMo base 2.24x,  OLMo Instruct 1.88x
THE PYTHIA LADDER IS AT CHANCE
Mean probability on the correct option, against two options: 0.497 to 0.501 across all seven sizes. A hundredfold increase in parameters produces no movement off chance.
For the seven models that fail, every null elsewhere is a property of the instrument, not of the model's gender behaviour, and we report them that way.
24

### Notes:
This result changed on 3 November. It was 1 of 10 until the noise floor was corrected. The margins have not changed at all: only the floor they are compared against. The next slide explains why.

<!-- Slide number: 25 -->
Why the floor moved: it was measured on the wrong stimulus
The gate margins have never changed. Only the threshold they were compared against was wrong, and it was wrong by construction.
THE FLOOR AS FIRST BUILT
THE FLOOR AS REBUILT
"Record 4417 is open for review. The applicant is the woman."
Group 4: real adult vignettes, pregnancy explicitly excluded, no sex-specific content
Scored over four arbitrary options:   Code A,  Code B,  Code C,  Code D
Same statistic as the gate, stratified by option count
Then used to gate binary Yes or No clinical items. Four mismatches at once:
four arbitrary options against two real words  ·  two option tokens against one  ·  one filler sentence against a 120-word vignette  ·  a maximum over 12 draws against a single targeted difference
A sex-parameter flip there should move nothing, so whatever it moves is instrument noise on the right geometry. No model was re-run: those rows were already scored in the October audit.
8.5x
10 of 10
0.118
1 to 3
too high
models moved
median ratio
gate passes
The old floor, on the primary score key
Every model's floor changed by more than 25 percent
New floor divided by old floor
The only outcome that changed for the models
Disclosed against our own interest:  on the mean log-probability sensitivity key, Qwen's matched floor rises instead and Qwen flips to insensitive. We kept the correction anyway, because keeping it was pre-declared.
25

### Notes:
This is the most important methodological slide in the deck. A near-uniform softmax over four meaningless codes is the noisiest place in the whole instrument, so the floor was inflated by construction. It also explains why the floor's size swung two to three times across score keys while the gate effect was bit-identical across two of them: Code A is two tokens and Yes is one.

<!-- Slide number: 26 -->
The pre-registered hypotheses, tested exactly as filed

| Hypothesis | Difference | 95% CI | Holm p | Verdict |
| --- | --- | --- | --- | --- |
| H1 biased conditions, 2 vignettes | -0.0042 | [-0.0074, -0.0011] | 0.750 | No evidence |
| H2 psychologizing cue, 1 vignette | +0.0022 | single vignette | 0.989 | No evidence |
| H3 neutral conditions, 8 vignettes | +0.0015 | [-0.0015, +0.0045] | 0.750 | Equivalence supported |
| H4 corpus linkage | see slide 24 | not identifiable | withdrawn | Reframed |

Every hypothesis was tested as filed and every one failed to reject. We report these as instrument insensitivity rather than as evidence of fairness, which is what the gate commitment requires.
H1's p value was 0.0001 before the fix
H3's equivalence test is no longer vacuous
H2 is scoped to one scenario by design
Two clusters, both negative, so no bootstrap resample could cross zero and the share on the null side was exactly 0. Clamped to the resolution two clusters support, it does not reject. The evidence in H1 is one bit: two of two items agreed in sign.
The old margin was 0.1047 against an effect of 0.0015, roughly 68 times the thing it was bounding. The corrected margin is 0.0131, which is 8.5 times the effect. Same verdict, against a margin that could have failed.
The table says so in its own caveat column. It does not generalise to the condition, let alone to the family. A single-vignette claim is reported as a single-vignette claim.
26

### Notes:
The honest framing is that the pre-registration worked. It removed a false positive in H1 and it stopped us reading three nulls as evidence of fairness. A project that found what it predicted would be less convincing than this.

<!-- Slide number: 27 -->
An exploratory finding the hypotheses did not predict
The same Group 2 items, used the other way round. Hold the sex parameter fixed and vary only the identity label, so the correct answer is identical within every pair and any difference is unwarranted by construction.

### Chart: Identity read as the sex parameter, relative to each model's noise floor

| Category | Interaction, times the model's own floor |
| --- | --- |
| Qwen3-8B | 16.5 |
| OLMo-2-7B Instruct | 9.6 |
| OLMo-2-7B base | 8.1 |
| all 7 Pythia sizes | 0.4 |

WHAT IT MEANS CLINICALLY
A trans man receives less probability on an indicated pregnancy test. A trans woman receives more probability on a cervical screening not indicated for her. The model is substituting the identity label for the clinical sex parameter.
THE UNCOMFORTABLE SHAPE OF IT
The three models that exceed their floor are exactly the three that can do the clinical task at all. The merging is not a small-model artefact that capability removes. It is visible only in the capable models.
Reported as exploratory. It came out of implementing the control, not out of testing H1 to H4, so it sits outside the Holm family with no p value claimed. With three vignettes the finest resolvable p is 0.125. A by-product of a control promoted to a confirmatory hypothesis after the fact is exactly what pre-registration exists to prevent, so we do not promote it.
27

### Notes:
This is the project's most interesting result and the one most likely to be over-read. Be scrupulous about the exploratory label. The Gender Harmony Model is what made it visible, because without separating identity from the sex parameter the two could not have been made to disagree.

<!-- Slide number: 28 -->
Data or post-training? A contrast that isolates tuning
Because the effect is largest in instruction-tuned models, post-training was a live alternative explanation. OLMo-2-7B and its Instruct sibling share a corpus exactly and differ only in post-training, so the difference between them isolates tuning with no new model and no new corpus.
OLMo-2-7B base
merging  0.0638
OLMo-2-7B Instruct
merging  0.1017
difference  +0.0379
post-training only
Against the old floor
Against the corrected floor
0.38x
2.88x
Combined floor 0.0998. Inside the noise, so D049 concluded that tuning adds nothing this instrument can resolve.
Combined floor 0.0132. Exceeds it, so post-training does increase the merging.
THE CONCLUSION REVERSED, AND WE MARKED IT SUPERSEDED RATHER THAN EDITING IT
The effect never changed. Only the floor did. Note that the base model also clears its own floor, 0.0638 against 0.0078, so the honest reading is that both stages contribute, not that tuning alone does. The claim that tuning adds nothing was an artefact of the inflated floor and is withdrawn. What survives is the limitation: one model pair, three vignettes, resolution limit 0.125, no p value claimed.
28

### Notes:
Reversing one of our own published conclusions is a credibility asset if we present it ourselves. The decision log keeps D049 in place with a superseded banner rather than rewriting it, so the reversal is auditable.

<!-- Slide number: 29 -->
RQ3: does the gap change with model scale?

### Chart: Gap minus floor, by model, before and after the floor correction

| Category | Floor-relative gap, old floor | Floor-relative gap, matched floor |
| --- | --- | --- |
| 70m | -0.0127 | 0.0031 |
| 160m | -0.0554 | -0.005 |
| 410m | -0.0244 | 0.0028 |
| 1b | -0.0799 | -0.0002 |
| 1.4b | -0.0978 | -0.005 |
| 2.8b | -0.0802 | 0.002 |
| 6.9b | -0.0972 | 0.005 |
| OLMo base | -0.0263 | 0.009 |
| OLMo Inst | -0.0631 | 0.0163 |
| Qwen 8B | 0.0046 | 0.0197 |

Old floor:  rho -0.030,  p = 0.93
Matched floor:  rho +0.693,  p = 0.026
THE RESULT TO BE MOST SUSPICIOUS OF
A null becomes a trend because of an instrument change we made ourselves. That is the shape a reader should distrust, so we volunteer it and offer four things instead of reassurance.
1  The criterion was fixed before the run and evaluated only on Groups 2 and 4.
2  The mechanism is checkable: the old floor ranged 0.021 to 0.105 with no relation to size, while the gap spans only 0.006 to 0.033.
3  Both columns are published and reproducible with a flag.
4  RQ3 stays exploratory, on ten models, outside the Holm family.
Had we reported the composite alone in October, our headline would have been that gender bias decreases with model scale, at p = 0.014. It would have been a statement about our own measurement noise. It is a trend worth reporting. It is not a scaling law.
29

### Notes:
Present this slide defensively. The number moved in our favour after a change we made, so the burden is on us. The decomposition is the defence: under the matched floor the floor no longer tracks size, correlating at only +0.280 with p = 0.43, so the gap trend is no longer cancelled.

<!-- Slide number: 30 -->
RQ4: the negative control fires, and the design is not identifiable
H4 says data skew should predict output gaps for the model trained on that data. Every model is tested twice: against its own corpus, which we call matched, and against a corpus it has never seen, which we call crossed.

### Chart: The models trained on neither corpus correlate best with both

| Category | Spearman correlation with corpus skew |
| --- | --- |
| Qwen3-8B vs olmo-mix (never seen) | 0.758 |
| Qwen3-8B vs the Pile (never seen) | 0.7 |
| OLMo-2-7B Instruct (its own corpus) | 0.385 |
| OLMo-2-7B base (its own corpus) | 0.06 |
| pythia-6.9b (its own corpus) | -0.117 |

WHY IT FIRES
On the audited concepts the two corpora agree at Spearman 0.976 on common support. They are both large English web scrapes, so their gendered health-term skew is very nearly the same measurement twice.
THE REPAIR THAT FAILED
Restricting to concepts where the corpora disagree was the plan, with a criterion of six concepts above 0.5 log2 fixed before running. Zero qualify: the largest disagreement is 0.377 and the median is 0.125. Recorded as a failed intervention.
RQ4 IS REFRAMED, NOT DROPPED
Two measurements that agree at 0.976 cannot attribute a model's behaviour to one rather than the other, so matched and crossed are close to the same test. We now report a measured non-identifiability result: 0.976 is the coefficient that makes provenance attribution by n-gram skew correlation impossible between these two corpora. For a project whose premise is that open data makes bias traceable, a measured bound on when tracing works is a result about that premise, not a failure to reach one.
30

### Notes:
Qwen correlating with both corpora is not an anomaly, it is the arithmetic consequence of the corpora agreeing with each other. A second defect this exposed: only 8 of 14 concepts have skew in both corpora, so matched and crossed were partly computed over non-overlapping concept sets.

<!-- Slide number: 31 -->
RQ5: non-binary patients are absent from the clinical subject position

| Phrase | The Pile | olmo-mix |
| --- | --- | --- |
| "the woman has" | 646,440 | 20,142 |
| "non-binary" (bare) | 1,350,944 | 66,269 |
| "the non-binary patient" | 0 | 0 |

THE ETHICS CLAIM, IN ITS SHARPEST FORM
Two of our source guidelines explicitly require care for non-binary and trans patients.
NICE NG126 covers trans men and non-binary people by name for the pregnancy pathway.
The exact phrase "the non-binary patient" does not occur once in either corpus.
Non-binary people are well represented in these corpora, with over 1.3 million mentions in the Pile. They never occupy the clinical subject position.
So the clinical guidance is more inclusive than the training data can support. A model cannot learn a subject position that its corpus never contains, and no amount of prompting at inference time supplies it.
This is a presence and absence pattern, not a scarcity pattern. The distinction matters: a scarcity argument invites more data as the remedy, while an absence in one specific grammatical position points at how the data was collected and what it was collected for.
Why this result is final rather than provisional. It is a corpus measurement, not a model measurement, so it does not depend on the vignettes or on clinician verification. It is the one headline in the project that is not waiting on anything.
31

### Notes:
If you only have one result to present, use this one. It is final, it is simple, it needs no statistics, and it carries the ethics argument on its own. Over 1.3 million mentions and zero in the clinical subject position is a presence and absence pattern, which is far more interesting than a scarcity claim.

<!-- Slide number: 32 -->
RQ6: the documentation gap is not silence, it is a missing link
THE OBVIOUS CLAIM WAS WRONG, AND WE FOUND OUT BY READING
Term counts suggested the datasheets are silent on gender. Reading the passages in context showed the Pile datasheet [1] discusses gender, and discusses it carefully. Our expected finding did not survive contact with the source.
Discloses gender
composition?
Connects it to
downstream health use?
So the risk is
undisclosed in practice
Yes, in the Pile
No document does
WHAT CHANGED IN OUR CLAIM
WHERE THIS STANDS
From:  "they never looked at gender"
To:  "their analysis could not have found this"

The second claim is stronger and survives a reviewer, because it is about the structure of the analysis rather than the attention of the authors. Narrowing a claim after reading the source is the decision log doing its job.
Ten documents retrieved, 136 candidate passages identified, a written codebook built, and a coding worksheet prepared. The remaining work is independent coding by both authors with inter-coder agreement reported whatever it turns out to be.
Policy consequence: a disclosure rule that asks only for composition statistics would be satisfied by documents that still leave this risk unstated. The rule has to ask for the connection to use.
32

### Notes:
The honest story here is that our hypothesis was wrong and reading the documents corrected it. That is a better finding than the one we expected, because a composition-only disclosure rule is a real policy proposal that our evidence shows would not work.

<!-- Slide number: 33 -->
5.  Instrument fix round 1
3 November 2026. Five interventions, each with a pass criterion written before the run
33

<!-- Slide number: 34 -->
How we changed the instrument without p-hacking
Adjusting an instrument until it works is either good science or p-hacking, and the difference is procedural rather than moral. Four standing rules, written down before the round began.
1
2
3
4
Tune only on Groups 2 and 4
Groups 1 and 3 stay sealed
Criterion before run
Failures are recorded
These are the instrument-validation strata and that is their purpose.
They carry H1 to H3. No change may be selected on what it does to them.
Each entry states its pass criterion before execution. One written afterwards is void.
A failed intervention stays in the log and counts toward the number the paper discloses.
CORRECTNESS FIX OR TUNING
BUDGET USED THIS ROUND
A change either repairs a demonstrable error, justified without reference to any outcome, or it is a judgement call among valid options. Only the second kind spends the disclosed budget.
1 tuning item. Three correctness fixes landed, one tuning item was spent and failed, and one diagnostic returned a negative result worth publishing.
THE HONEST LIMITATION ON RULE 2, STATED BECAUSE A READER WOULD OTHERWISE HAVE TO TRUST US
The pre-registered Group 3 analysis was run and inspected before this log was opened, so the sealed-data rule cannot be claimed retrospectively. The protection actually in force is weaker: every criterion is defined on Group 2 and Group 4 quantities only, and both the pre-fix and post-fix values are published side by side. The reader can see what the change did to the headline numbers rather than being asked to trust it was not chosen for them.
34

### Notes:
This slide is the project's answer to the most dangerous question a marker can ask about the fix round, which is whether we tuned until we liked the answer. The procedure is the answer, and the limitation on rule 2 is stated because it is real.

<!-- Slide number: 35 -->
The five interventions, and what each one returned

|  | Intervention | Class | Criterion, fixed before the run | Outcome |
| --- | --- | --- | --- | --- |
| I1 | Matched-geometry noise floor | correctness | Floor moves more than 25 percent for a majority of 10 models | PASS 10 of 10, median ratio 0.118 |
| I2 | Score-key collapse | correctness | Sum and mean floors differ by less than 1e-9 on the binary stratum | PASS difference exactly 0 |
| I3 | Pythia elicitation | tuning | At least 2 of 7 Pythia models above their own matched floor | FAIL 0 of 7, 1 of 7, 1 of 7 |
| I4 | RQ4 identifiability | diagnostic | At least 6 concepts disagreeing by more than 0.5 log2 | NOT IDENTIFIABLE 0 qualify |
| I5 | Circularity that I1 created | correctness | None. Unplanned, found during review | REAL H3 survives it |

A PRE-REGISTRATION GAP WE HIT
I5: WE BROKE SOMETHING AND FOUND IT
The I3 criterion did not name a score key, and the keys disagree. We resolved it to the key already prespecified in the code long before this round, and logged that the ambiguity was noticed after the five small models reported and before the two large ones did. Under the other key, few-shot would have scored 2 of 7 and passed. That is exactly why the conservative reading is the one adopted.
I1 made H3's equivalence margin circular, because H3's preregistered vignette set includes the Group 4 items the new floor is built from. It was caught by asking why the margin came out as 0.0131 rather than 0.0117. H3 was not redefined, three variants were published, and H3 is supported on all three.
35

### Notes:
Five rows, two of which went against us. The I3 failure and the I4 negative result are both in the log permanently. The paper will disclose that one tuning item was spent, which is what converts an adaptive search into a defensible one.

<!-- Slide number: 36 -->
What the correction moved, including against us
A floor measured on the wrong stimulus fed four downstream results. Correcting it changed all four.

| Result | With the old floor | With the matched floor | Reading |
| --- | --- | --- | --- |
| Gate, Group 2 | 1 of 10 models pass | 3 of 10 models pass | Opens the open-data family |
| H3 equivalence | supported, margin 68x the effect | supported, margin 8.5x the effect | Same verdict, real margin |
| RQ2c post-training | 0.38x, inside the floor | 2.88x, exceeds the floor | Conclusion reverses |
| RQ3 size trend | rho -0.030, p = 0.93 | rho +0.693, p = 0.026 | Null becomes a trend, in our favour |

THE READER'S SUMMARY, WHICH WE GIVE BEFORE WE ARE ASKED FOR IT
Of the four changes, one is a straightforward improvement in H3's margin, one opens the gate for the family the project most needs, one reverses a conclusion we had already published and does so against the simpler story, and one turns a null into a positive finding in a way that happens to favour us. The fourth is the one to treat with most caution, and it is flagged as such everywhere it is reported.
36

### Notes:
Presenting the two results that went against us before anyone asks is the strongest available move. The RQ2c reversal cost us a published conclusion and the RQ3 change benefits us, so flagging the second more loudly than the first is the honest asymmetry.

<!-- Slide number: 37 -->
The finding that came out of the failed intervention
I3 tried three prompt formats on all seven Pythia models to see whether the problem was elicitation rather than capability. It failed its criterion, and in failing it produced the most consequential result of the round.

### Chart: Group 2 margin by prompt format. Every model crosses zero

| Category | Question and answer format | Cloze format | Few-shot format |
| --- | --- | --- | --- |
| 70m | -0.0035 | -0.0044 | 0.0 |
| 160m | -0.0063 | -0.0062 | 0.0109 |
| 410m | 0.0015 | 0.0071 | -0.0021 |
| 1b | -0.0007 | -0.0009 | 0.0007 |
| 1.4b | -0.0035 | -0.0099 | 0.005 |
| 2.8b | -0.0005 | 0.0214 | 0.0046 |
| 6.9b | -0.0019 | -0.0058 | 0.0051 |

7 of 7
models change the SIGN of their effect across prompt formats
WHAT THAT MEANS
The direction of a sex-parameter effect in this family is a property of the prompt format, not of the model. A single-format audit would report a direction another defensible format reverses.
CALIBRATION WAS ALREADY IN THE DESIGN
Our PMI score key already subtracts a content-free baseline, so every Pythia margin was post-calibration all along.
The uncomfortable corollary, which we state rather than work around:  the models that ship the corpora this project's argument depends on are the models this method cannot measure.
37

### Notes:
Pythia probabilities sit at 0.497 to 0.501, exactly uniform over two options, so the model is not treating the input as a question. It is a base model with no instruction tuning. Three formats were tried; a chat template, a longer prefix and a generation-based readout remain untested, so this is a limit on what we have shown, not a proof of impossibility.

<!-- Slide number: 38 -->
6.  Limitations, conclusions and what remains
What is still broken, what would change our mind, and the critical path
38

<!-- Slide number: 39 -->
Limitations, in order of how much they threaten the work
The stimuli are not clinically verified
Seven of ten models cannot be measured at all
1
2
No result computed from the vignettes is reportable until a clinician passes them. The request is out and the response is the critical path for the rest of the project.
And D057 shows the obvious elicitation fixes do not work. The open-data families are the ones the argument needs and the ones the method cannot resolve.
The noise floor is thin
The design cannot resolve small p values
3
4
Two Group 4 vignettes in the binary stratum and one in the four-option stratum, so the cluster bootstrap is degenerate. The geometry is now right and the sample size is not.
H1 rests on two vignette clusters, so its finest resolvable p is 0.25, and the gate rests on three. No change of model improves this. Only more vignettes per group will.
The gate's verdict on Qwen is score-key dependent
Corpus provenance is not identifiable
5
6
Sensitive under PMI, insensitive under mean log-probability. The instrument does not give one answer about its most capable model.
The two corpora agree at 0.976, so RQ4 cannot attribute behaviour to one of them. This is now reported as a bound rather than repaired.
Single-token answer options cap clinical content
Scope is English and single-jurisdiction
7
8
This is what makes the gate immune to length bias rather than merely robust to it, which is a genuine strength. It also limits how much a single option can say.
All corpora and vignettes are English only, and guideline choices are single-jurisdiction where guidelines conflict. Vignettes are not patients.
Items 1 and 2 are existential for the current claims. Items 3 to 6 are measurement limits with known fixes. Items 7 and 8 are scope boundaries we accept.
39

### Notes:
Order matters here. If asked which limitation worries us most, the answer is the clinician verification, because it is the only one that could invalidate the stimulus set entirely rather than merely limit what we can resolve.

<!-- Slide number: 40 -->
What would change our mind, stated in advance
Each deliverable has a success criterion that does not depend on the result going our way. A project whose success requires finding bias has an incentive to find it.

| Deliverable | How we judge it, decided before the result |
| --- | --- |
| A clinician-verified stimulus set | Every item carries a sourced reference answer and a clinician ruling. Success is a complete record including the rejection rate, which is itself evidence about the method |
| A re-run audit on verified items | Success is a before-and-after comparison reported in full, whether or not the verdicts change |
| A corpus-to-output linkage test | A matched result reported alongside its crossed control. A matched correlation without the control is a failure even if it is positive |
| A documentation analysis | Independent coding by both authors against a written codebook, with inter-coder agreement reported whatever it turns out to be |
| An account of the instrument's limits | A measured floor and a stated resolution limit for every claim, so a reader can tell a null from a blindness |

WE WITHDRAW, NOT REINTERPRET
THE EXPLORATORY FINDING IS NOT PROTECTED
If the clinician review rejects a substantial share of the reference answers, the vignette set is not valid and the audit results are withdrawn rather than reinterpreted.
If the identity and sex-parameter merging does not survive the re-run on verified items, it is reported as not surviving. It is currently our most interesting result and it has no special status.
40

### Notes:
Stating the withdrawal conditions in advance is the strongest possible answer to the question of whether we are motivated to find bias. The exploratory finding is the one we would most want to keep, which is exactly why it is named here.

<!-- Slide number: 41 -->
Conclusions
The chain can be built, and it does not yet close
1
A datasheet, a corpus measurement, a validated instrument and a pre-registered analysis can be connected end to end in one repository. The link that fails is provenance attribution, and it fails for a measurable reason rather than a practical one.
Open training data is necessary but not sufficient
2
This is uncomfortable for the simple version of our own policy argument, and it is the honest result. The corpora are inspectable and the models trained on them are too insensitive to audit by this method, while the model that passes the gate most convincingly is the one whose data nobody can inspect.
The instrument was the binding constraint, not the models
3
A noise floor measured on the wrong stimulus was deciding our headline result. Finding that changed the gate from one model to three, reversed one published conclusion and turned one null into a trend. The lesson generalises: an audit that does not measure its own floor on matched geometry cannot tell a null from a blindness.
The clearest ethics finding needs no statistics at all
4
Non-binary people appear over 1.3 million times in the Pile and never once in the clinical subject position, while two of our source guidelines require care for them by name. The clinical guidance is more inclusive than the training data can support.
The contribution is a working instrument, a pre-registered null reported as a null, and a measured account of exactly where the datasheet to diagnosis chain breaks.
41

### Notes:
Conclusion 2 is the one to deliver carefully. It undercuts the simple version of the open-data argument, and saying so first is far stronger than being caught by it. Conclusion 4 is the one to end on if time is short.

<!-- Slide number: 42 -->
What is left to do
Ordered by the critical path. Item 1 blocks every reportable number in the project.
Clinician review of all 15 vignettes
Outreach is sent and the response is outstanding. Nothing becomes reportable until this returns.
1
Blocking
Write more Group 4 vignettes
The highest-value build step. Fixes the two-cluster floor, the degenerate bootstrap and the H3 circularity at once, and depends on nothing unresolved.
2
Ready to start
Re-run the audit on verified items
Same pipeline, corrected items, and a full before-and-after table. The only route to a reportable number.
3
After item 1
RQ6 independent coding
Both authors code the 136 candidate passages against the written codebook, and inter-coder agreement is reported whatever it is.
4
Ready to start
More vignettes per hypothesis group
The only way to improve the resolution limit. H1 currently rests on two clusters, which caps its finest p value at 0.25.
5
Planned
Investigate elicitation further
A chat template, a longer few-shot prefix and a generation-based readout are untested. D057 limits what we have shown, not what is possible.
6
Optional
Items 2 and 4 can proceed in parallel with the clinician review and are the best use of the waiting time.
42

### Notes:
Items 2 and 4 are unblocked, so they are what to work on now. Item 2 in particular closes three separate limitations with one piece of authoring work.

<!-- Slide number: 43 -->
References
[1]  Biderman, S. et al. 2022. Datasheet for the Pile. arXiv:2201.07311.
[2]  Biderman, S. et al. 2023. Pythia: A suite for analyzing large language models across training and scaling. ICML 2023.
[3]  Chang, C.T. et al. 2025. Evaluating anti-LGBTQIA+ medical bias in large language models. PLOS Digital Health 4, 9.
[4]  Cirillo, D. et al. 2020. Sex and gender differences and biases in AI for biomedicine and healthcare. npj Digital Medicine 3, 81.
[5]  Dev, S. et al. 2021. Harms of gender exclusivity and challenges in non-binary representation in language technologies. EMNLP 2021.
[6]  Elterman, D. et al. 2022. CUA guideline: Male lower urinary tract symptoms and benign prostatic hyperplasia. CUAJ 16, 8.
[7]  Gao, L. et al. 2021. The Pile: An 800GB dataset of diverse text for language modeling. arXiv:2101.00027.
[8]  Gebru, T. et al. 2021. Datasheets for datasets. Communications of the ACM 64, 12, 86-92.
[9]  Guerra-Adames, A. et al. 2026. Auditing sex and gender disparities in emergency triage with LLM-based paired comparisons. npj Digital Medicine.
[10]  Gulati, M. et al. 2021. AHA and ACC guideline for the evaluation and diagnosis of chest pain. Circulation 144, e368-e454.
[11]  Heidari, S. et al. 2016. Sex and Gender Equity in Research: Rationale for the SAGER guidelines. Research Integrity and Peer Review 1, 2.
[12]  Hoffmann, D.E. and Tarzian, A.J. 2001. The girl who cried pain: A bias against women in the treatment of pain. JLME 29, 1.
[13]  Liu, J. et al. 2024. Infini-gram: Scaling unbounded n-gram language models to a trillion tokens. arXiv:2401.17377.
[14]  Loge, C. et al. 2021. Q-Pain: A question answering dataset to measure social bias in pain management. NeurIPS D and B 2021.
[15]  McClure, R.C. et al. 2022. Gender harmony: Improved standards to support affirmative care of gender-marginalized people. JAMIA 29, 2.
[16]  NICE. 2019. Attention deficit hyperactivity disorder: diagnosis and management. NICE guideline NG87.
[17]  NICE. 2023. Ectopic pregnancy and miscarriage: diagnosis and initial management. NICE guideline NG126.
[18]  OLMo Team. 2025. 2 OLMo 2 Furious. arXiv:2501.00656.
[19]  Qwen Team. 2025. Qwen3 technical report. arXiv:2505.09388.
[20]  Soldaini, L. et al. 2024. Dolma: An open corpus of three trillion tokens for language model pretraining research. arXiv:2402.00159.
[21]  Turpin, M. et al. 2023. Language models don't always say what they think: Unfaithful explanations in chain-of-thought prompting. NeurIPS 2023.
[22]  Vig, J. et al. 2020. Investigating gender bias in language models using causal mediation analysis. NeurIPS 2020.
[23]  Young, R.J. and Matthews, A.M. 2026. EQUITRIAGE: A fairness audit of gender bias in LLM-based emergency department triage. arXiv:2605.03998.
[24]  Zack, T. et al. 2024. Assessing the potential of GPT-4 to perpetuate racial and gender biases in health care. Lancet Digital Health 6, 1.
[25]  Zhao, J. et al. 2017. Men also like shopping: Reducing gender bias amplification using corpus-level constraints. EMNLP 2017.
43

### Notes:
ACM reference style, matching the progress report so the numbering is consistent across both documents.

<!-- Slide number: 44 -->
A living document
This deck is the running record of the project. Update it whenever something critical changes.
When a run completes
When a decision is logged
When the clinician replies
Update the results section and the date on slide 1.
The decision count on slide 18 and the log in the repository.
The status column on slide 5 and the whole of the remaining work slide.
Evans Kumi  and  Aymen Boustani   ·   McGill University   ·   ECSE-557 Ethics in Artificial Intelligence

### Notes:
Three triggers for updating this deck. The most common one will be a completed run, which touches the results section and the date on the title slide.
