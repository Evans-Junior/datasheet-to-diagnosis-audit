# RQ6 codebook, what the dataset documentation discloses

**RQ6.** Do the datasheets for the Pile and OLMo-mix-1124 disclose gender
composition, and do they disclose the downstream risk in health advice that such
composition creates?

This codebook is the instrument for that question. It is written **before** the
documents are coded, for the same reason the hypotheses were registered before any
score existed: "does this datasheet mention gender?" has an answer that moves
depending on how hard you want it to move.

> **Status: structure complete, anchor examples deliberately empty.** Every
> `ANCHOR:` line below is filled during the calibration pass (§6) with a verbatim
> quotation from the document it came from. They are **not** pre-filled from
> memory. An invented or half-remembered anchor would be worse than none, because
> every later coding decision is calibrated against it. See `AI_USE.md`.

---

## 1. Why this is a measurement and not a reading

The finding RQ6 is positioned to deliver is an **absence**: that the documentation
does not disclose a risk the project then demonstrates. Absence claims are the
easiest thing in qualitative work to get wrong, in both directions:

- **False absence.** The disclosure is there, in a section we did not read, under
  wording we did not search for. Publishing "they never mention it" when they do,
  once, in an appendix, is a straightforward factual error and the kind a reviewer
  who knows the document will find immediately.
- **False presence.** A document says "the Pile reflects biases present in its
  sources" and we code that as disclosing gender composition. It does not. It
  asserts a generic risk without measuring anything, and treating the two as
  equivalent destroys the distinction RQ6 exists to draw.

So the codebook does two things the usual thematic-coding setup does not: it fixes
an **exhaustive search protocol** (§4) so that "absent" means "absent after this
specific search", and it separates **assertion from measurement** on its own
dimension (D7), so a generic bias caveat can never be scored as composition
disclosure.

---

## 2. Document inventory

Coded at the level of the **document**, with evidence recorded at passage level.
Each document is coded independently; they are **not** merged into one "the Pile
documentation" unit, because which document carries a disclosure is itself part of
the answer, a risk stated in a paper's limitations section but absent from the
dataset card reaches a different audience.

| # | Document | Family | Retrieved? |
|---|---|---|---|
| 1 | Gao et al., *The Pile: An 800GB Dataset of Diverse Text for Language Modeling*, arXiv:2101.00027 | Pythia | ☐ |
| 2 | Biderman et al., *Datasheet for the Pile*, arXiv:2201.07311 | Pythia | ☐ |
| 3 | Pythia model card / `EleutherAI/pythia-*` Hugging Face card | Pythia | ☐ |
| 4 | Biderman et al., *Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling*, arXiv:2304.01373 | Pythia | ☐ |
| 5 | Soldaini et al., *Dolma: an Open Corpus of Three Trillion Tokens…*, arXiv:2402.00159 | OLMo 2 | ☐ |
| 6 | `allenai/olmo-mix-1124` dataset card | OLMo 2 | ☐ |
| 7a | *2 OLMo 2 Furious* (OLMo 2 report), arXiv:2501.00656 | OLMo 2 | ☑ 2026-10-28 |
| 7b | `allenai/OLMo-2-1124-7B` model card | OLMo 2 | ☑ 2026-10-28 |
| 8a | *Qwen3 Technical Report*, arXiv:2505.09388 | Contrast (RQ5) | ☑ 2026-10-28 |
| 8b | `Qwen/Qwen3-8B` model card | Contrast (RQ5) | ☑ 2026-10-28 |

**Ten coding units, not eight.** Entries 7 and 8 each split into a report and a
card. They are coded separately for the reason given above: a risk stated in a
58-page report and absent from the model card a practitioner actually reads are
different facts, and collapsing them would hide the more important one. Documents
1–6 were retrieved on the same date; see `data/raw/rq6/manifest.json`.

Retrieval is `scripts/rq6_fetch.py`, which checks each file against an expected
title fragment and refuses a mismatch rather than coding the wrong document.

**Document 8 is coded for a specific reason.** Qwen3 is the weights-only contrast
model: its training data is not released. Coding its documentation makes the RQ5
comparison symmetrical and prevents an easy misreading of RQ6, that open-data
projects document *worse*. They document more; the question is whether what they
document covers this risk. Without the closed-data comparator we could not say
which it is.

**Tick the Retrieved box, with the access date, before coding.** Dataset and model
cards are living documents and are edited without version notice. Record the
retrieval date and commit the retrieved text to `data/raw/rq6/` (git-ignored; the
manifest is tracked) so a later reader can see the version coded. This is the same
failure D033 recorded for clinical PDFs: the artefact's own identity must be read
before it is trusted.

---

## 3. Dimensions

Eight dimensions. D1–D6 are ordinal and the levels are mutually exclusive; code the
**highest** level the document supports. D7 and D8 are qualifiers applied to any
D1/D2 code above 0.

### D1, Gender composition of the corpus

Does the document say anything about the gender distribution of the text?

| Level | Definition |
|---|---|
| 0 | No reference to gender composition anywhere |
| 1 | **Generic bias caveat only.** Gender named in a list of biases the corpus may contain, with no claim about this corpus's distribution. E.g. a sentence of the form "may contain biases relating to gender, race and religion" |
| 2 | **Qualitative claim about this corpus.** States or implies a skew without a number, e.g. that the sources over-represent some group |
| 3 | **Quantified.** Reports a measured statistic about gender distribution in this corpus, with enough method detail to know what was counted |

ANCHOR 1: _[calibration]_
ANCHOR 2: _[calibration]_
ANCHOR 3: _[calibration]_

**Boundary rule, 1 vs 2.** The test is whether the sentence would still be true if
written about a *different* corpus. "Large web corpora reflect societal biases" is
level 1 however prominently placed. "Our Books3 subset skews toward male authors"
is level 2. If the sentence is transferable verbatim to any corpus, it is level 1.

**Boundary rule, 2 vs 3.** Level 3 requires a number *and* a statable unit. "Mostly
male-authored" is 2. "68% of authors were identified as male, by first-name
matching against X" is 3. A number with no stated method is coded 2 with a note,
because an unmethodised number cannot be checked and functions rhetorically as a
qualitative claim.

### D2, Gender-related downstream risk

Does the document state a *consequence* of gender composition for model behaviour?

| Level | Definition |
|---|---|
| 0 | No statement of gender-related downstream risk |
| 1 | Generic harm language, gender not specified ("may produce harmful outputs") |
| 2 | Gender-specific harm named, domain unspecified ("may produce gender-stereotyped text") |
| 3 | Gender-specific harm named **in a specified high-stakes domain** (medical, legal, hiring, lending) |

ANCHOR: _[calibration]_

### D3, Health or medical content acknowledgement

| Level | Definition |
|---|---|
| 0 | No reference to medical or health content in the corpus |
| 1 | Health sources listed in a composition table only (e.g. PubMed Central, PubMed Abstracts), with no commentary |
| 2 | Health content discussed as a content category, including what it is expected to be good for |
| 3 | Health content discussed **with its limitations or risks** as training data |

ANCHOR: _[calibration]_

**Note.** The Pile is expected to score at least 1 on D3 by construction: PubMed
Central and PubMed Abstracts are named components. That makes D3 and D4 the
sharpest pair in the codebook, a corpus that *advertises* medical text while
saying nothing about demographic skew in it is a stronger RQ6 finding than one that
contains medical text incidentally.

### D4, Health × demographic intersection

The dimension RQ6 exists for. Does the document connect demographic composition to
health-domain use **in the same claim**?

| Level | Definition |
|---|---|
| 0 | Absent. The two topics may each appear; they are never joined |
| 1 | Joined vaguely, a list in which both appear without an asserted relation |
| 2 | Joined explicitly, as a possibility ("demographic skew could affect clinical applications") |
| 3 | Joined explicitly, with evidence or a measurement |

ANCHOR: _[calibration]_

**Coding rule.** Co-occurrence in a document is not a join. The two topics must be
related **within one sentence or one clearly continuous passage**, and the coder
must record that passage. A bias caveat in §7 and a PubMed row in a table in §2 is
**level 0**, not level 1.

### D5, Gender identity beyond the binary

| Level | Definition |
|---|---|
| 0 | No reference |
| 1 | Named in a list of identities or protected attributes |
| 2 | Discussed as a representation issue for this corpus |
| 3 | Measured or quantified for this corpus |

ANCHOR: _[calibration]_

**Why this is a separate dimension.** D34 established that two clinical guidelines
in our set state the gender-identity/anatomy decoupling themselves, while RQ1
measured `"the non-binary patient"` at **zero occurrences** in both corpora in a
frame where `"the woman has"` occurs 646,440 and 20,142 times. There is therefore a
documented clinical requirement to measure this absence against, which is what
separates it from a general diversity observation.

### D6, Stated scope of appropriate use

| Level | Definition |
|---|---|
| 0 | No use-scope statement |
| 1 | Generic research-only or as-is language |
| 2 | Named out-of-scope uses, medical use **not** among them |
| 3 | Medical, clinical or health-advice use explicitly named as out of scope or requiring caution |

ANCHOR: _[calibration]_

**Why this cuts both ways, and must be reported either way.** A document scoring 3
has discharged a real part of its duty, it told users not to do this. That is a
point *for* the documentation and against a naive "they failed to warn us" reading,
and it must be reported as such even though it complicates the paper's argument.
But it does not answer RQ6: a scope statement is a disclaimer about *use*, not a
disclosure about *content*, and a model trained on the corpus will be used for
health questions regardless of what the card says. The honest framing is that D6
and D1–D4 measure different obligations, and the paper should not let a high D6
stand in for a low D4.

### D7, Measurement or assertion (qualifier)

Applied to every D1 or D2 code above 0.

| Code | Definition |
|---|---|
| M | A measurement is reported: something was counted, with a method |
| A | An assertion is made with no supporting measurement in the document |
| R | A measurement is reported but attributed to another source, with a citation |

**Why it is a qualifier rather than a level.** Without D7, a document that asserts
gender bias loudly and one that measures it would be indistinguishable in the
results table. The distinction is the project's own standard: our RQ1 numbers exist
precisely because asserting corpus skew is not the same as measuring it.

### D8, Traceability (qualifier)

| Code | Definition |
|---|---|
| T | A reader could reproduce the claim from what the document provides |
| P | Partially, method named, parameters or data missing |
| N | Not reproducible from the document |

---

## 4. Search protocol, what "absent" is allowed to mean

A level-0 code is a positive claim about a document, so it may be recorded only
after **all three** steps below, and the coder records that they were done.

**Step 1, full read.** Read the document end to end, including footnotes,
appendices, limitations sections and any datasheet-question annexes. For model and
dataset cards, expand every collapsed section.

**Step 2, term search.** Case-insensitive search for every term, and record the
hit count for each (zero counts are data):

`gender` · `sex` · `woman` · `women` · `man` · `men` · `male` · `female` ·
`non-binary` · `nonbinary` · `transgender` · `trans ` · `identity` ·
`demographic` · `representation` · `underrepresent` · `skew` · `imbalance` ·
`bias` · `stereotype` · `fairness` · `harm` · `medical` · `clinical` · `health` ·
`patient` · `diagnosis` · `PubMed` · `disparity` · `equity`

**Step 3, structural check.** Confirm whether the document answers the *Datasheets
for Datasets* composition and distribution questions (Gebru et al.) at all. A
document that does not use the datasheet format is not thereby non-compliant, but
whether it addresses those questions in some form is recorded.

A level 0 without all three steps recorded is not a finding. It is an unfinished
coding.

---

## 5. Unit, and what counts as evidence

- **Unit of coding:** the document.
- **Unit of evidence:** the passage. Every code above 0 carries at least one
  verbatim quotation with a locator (section number, page, or card heading).
- **Quotation, not paraphrase.** A paraphrase is already a coding decision, and it
  is the specific error D030 caught in the clinical sourcing, a secondary source's
  "noncardiac" for the guideline's "nonischemic". Record the words.
- **No cross-document inference.** If the Pile paper discloses something the Pile
  datasheet does not, both codes stand as they are. The difference is a result.

---

## 6. Calibration, double coding and reliability

1. **Calibration.** Both coders independently code **document 2** (Datasheet for
   the Pile), chosen because it is the most likely in the set to contain real
   disclosures and therefore exercises the upper levels of every dimension. They
   then compare, fill in the `ANCHOR:` lines above with the verbatim passages they
   agreed on, and record any rule they had to add. Calibration is not counted
   toward reliability.
2. **Independent coding.** Both coders code all 8 documents independently, with no
   discussion.
3. **Reliability.** Cohen's κ per dimension, over 8 documents, reported for every
   dimension including those where it is low.
4. **Threshold.** κ ≥ 0.70 per dimension, the same threshold the LLM judge must
   clear. A dimension below 0.70 is **either** reported as unreliable and excluded
   from conclusions, **or** its definition is revised and *all* documents recoded
   from scratch, never patched selectively on the rows that disagreed.
5. **Adjudication.** Disagreements are resolved by discussion, and the resolution
   rule is added to this file. Reliability is reported on the **pre-adjudication**
   codes, since post-hoc agreement is not agreement.

**A limit to state in the paper, not hide.** κ over 8 documents is unstable: one
disagreement moves it a long way, and on an ordinal scale with a skewed marginal
distribution, which is expected here, since most codes will be 0 or 1,  κ can be
low even at high raw agreement. So report **raw percent agreement alongside κ** for
every dimension, and treat the κ threshold as a screen rather than a result. The
honest version of this limitation is that RQ6 is a close reading of 8 documents by
two coders, with its agreement reported; it is not a survey, and the n does not
support a claim about documentation practice in general.

---

## 7. Output

| File | Contents |
|---|---|
| `results/tables/rq6_codes.csv` | one row per (document × dimension): code, D7, D8, quotation, locator, coder |
| `results/tables/rq6_reliability.csv` | per dimension: κ, raw agreement, n disagreements |
| `results/tables/rq6_search_counts.csv` | per document × term: hit count from §4 step 2 |

The search-count table is published as a result in its own right. It is the
evidence behind every level-0 code, and it lets a reader check an absence claim
without re-reading eight documents.

---

## 8. The claim this can and cannot support

**Can.** That these specific documents, read in full on a stated date, do or do not
join demographic composition to health-domain risk, with the passages shown, and
with a closed-data comparator for contrast.

**Cannot.** That dataset documentation in general fails to do so. Eight documents
from three projects is a case study. The finding's force comes from the pairing
with RQ1 and RQ2, that a measurable skew and a measurable output gap exist *in the
same corpus and models* whose documentation did not flag them, not from the
breadth of the documentation sample.


---

## 9. How to code from a passage, the procedure

`docs/rq6_passages.csv` holds 136 candidate passages extracted by
`scripts/rq6_worksheet.py`, each tagged with the dimensions it *may* bear on.
`docs/rq6_coding_sheet.csv` is the blank sheet: 10 documents × 8 dimensions = 80
rows, with separate columns per coder.

**The candidate tags are not codes and the extraction is over-inclusive on
purpose.** A tag means "a human must look at this", nothing more. Reading a false
candidate costs thirty seconds; missing a real one produces a published absence
claim that is false.

### The five steps, per document × dimension

1. **Filter** `rq6_passages.csv` to that document and that dimension tag.
2. **Read each candidate** and ask the dimension's own question, using the
   boundary rules in §3. Most candidates will support nothing.
3. **Choose the level** the strongest passage supports, the *highest* level the
   document genuinely reaches, not the average of its passages.
4. **Record the evidence.** Paste the `passage_id` and the verbatim quote into
   your column. A code with no quote is not a code; it is an impression.
5. **Record which search steps you completed** (§4) in the last column. A level 0
   without all three is an unfinished coding, not a finding.

Then add D7 (measurement / assertion / reported) and D8 (traceability) for any
D1 or D2 code above 0.

### What this looks like in practice

Three worked examples follow. They are chosen because the judgement in each is
**hard**, and they are written as a *reasoning pattern, not as this project's
codes*. You assign the codes, independently, and you may disagree with every one
of these.

> ⚠ **Anchoring risk, stated plainly.** Reading someone else's reasoning before
> coding biases you toward it, and κ computed over anchored coding overstates
> agreement. If you find yourself agreeing with any example below *without having
> checked the document yourself*, recode that document from the passages alone
> and ignore what is written here. The §3 `ANCHOR:` lines are still empty for
> exactly this reason: they are filled from what the two of you agree on at
> calibration, not from this section.

**Example 1, the referral, and why D7 exists.**
The Pythia model card says:

> "This model was trained on the Pile, a dataset known to contain profanity and
> texts that are lewd or otherwise offensive. See Section 6 of the Pile paper for
> a discussion of documented biases with regards to gender, religion, and race."

The reasoning to run: gender is named, so D1 is not obviously 0. But does the card
make a claim about the Pile's gender distribution? No, it points somewhere else
that does. So the question becomes whether a pointer is a disclosure. Both answers
are arguable, and **the D7 qualifier is what makes the choice recordable rather
than hidden**: `R` means "a measurement exists and is cited, not reproduced here".
Whatever level you give D1, mark D7 = R, and the distinction between a card that
discloses and a card that refers survives into the results table.

**Example 2, the false positive the term search cannot filter.**
The OLMo 2 report returns three `health` hits. All three are:

> "embedding norms settle in a **healthy** region as training progresses"
> "GPU **health** checks: Beaker executes a simple program prior to running
> workloads"
> "Cordoning: Beaker supports cordoning nodes as an override for the automatic
> **health** checks"

None is medical. Its five `bias` hits are likewise all architectural, *"No
biases: we exclude all bias terms from our architecture"*. So on D3 the correct
code is 0 **despite three hits**, and on D2 it is 0 despite five.

This is the single most important thing to internalise: **a hit count is a place to
look, never a code.** Had the hit counts been written up directly, this project
would have reported that the OLMo 2 report discusses health and bias. It does not
discuss either. The opposite error is just as live, the Pythia paper's 60 `bias`
hits are real discussions of bias, but of *model behaviour and mitigation*, not of
corpus composition, and whether any of them says what the Pile's gender
distribution **is** has to be read, not counted.

**Example 3, a dimension where the honest code is uncomfortable.**
The Pythia card's out-of-scope section is unusually strong:

> "The Pythia Suite is **not** intended for deployment. It is not a in itself a
> product and cannot be used for human-facing interactions."

It then names specific out-of-scope uses, translation, non-English generation,
genre prose, commercial chatbots, and **medical or health use is not among
them**, though "not for human-facing interactions" arguably covers it. Under §3 D6
that is the 2-versus-3 boundary, and it has to be argued rather than felt.

Note what the code does *not* do: a high D6 is a point in the documentation's
favour and must be reported as one, even though it complicates the paper's
argument. It still does not answer RQ6, because a scope statement is a disclaimer
about **use** while D1–D4 are disclosures about **content**. Do not let a strong
D6 pull your D4 upward, and do not let a weak D4 pull your D6 down.

### When you disagree

Record both codes, resolve by discussion, and **write the resolving rule into §3**
so the next disagreement of that shape resolves itself. Reliability is computed on
the **pre-adjudication** codes (§6.5), so do not quietly align before recording,
or the κ you report will measure your conversation rather than the codebook.
