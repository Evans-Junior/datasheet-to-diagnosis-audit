# G3-03 theme, psychologizing of women's physical symptoms

G3-03 was dropped as a vignette (D020) because no guideline governs it. The
**construct** is retained as a codebook category applied to generated rationales
across all vignettes. This file gives the theme, the search vocabulary, and the
anchor citations, so the literature can be found and the codebook grounded.

## The construct in one sentence

A patient reports physical symptoms; the clinician attributes them to a
psychological cause (anxiety, stress, somatization) rather than investigating a
physical one, and does so more readily when the patient is a woman.

## Search vocabulary, use these terms, not "psychologizing"

"Psychologizing" is our working word and returns little. The established terms are:

| Term | Field | Why it helps |
|---|---|---|
| **diagnostic overshadowing** | clinical | The precise clinical term for attributing physical symptoms to a psychiatric cause. Best single search term. |
| **medical gaslighting** | popular / recent academic | Fast-growing literature since ~2022; good for recent empirical work and for public-harm framing. |
| **psychogenic attribution** | clinical psychology | Catches the older attribution literature. |
| **somatization bias** | psychiatry | Overlaps diagnostic overshadowing; more psychiatric framing. |
| **medically unexplained symptoms (MUS)** / **contested illness** | medical sociology | The literature on how unexplained symptoms are managed, heavily gendered. |
| **testimonial injustice** / **epistemic injustice in healthcare** | philosophy of medicine | **Strongest frame for an ethics paper**: the harm is not being believed. |
| **gender bias in pain assessment** | pain medicine | Connects to G3-01 and Q-Pain. |

## Anchor citations, all DOIs resolved at CrossRef

**The canonical reference. Cite this one.**
> Hoffmann DE, Tarzian AJ. The Girl Who Cried Pain: A Bias against Women in the
> Treatment of Pain. *J Law Med Ethics.* 2001;29(1):13–27.
> doi:10.1111/j.1748-720X.2001.tb00037.x

**The theory-guided review, most useful for building the codebook.**
> Samulowitz A, Gremyr I, Eriksson E, Hensing G. "Brave Men" and "Emotional Women":
> A Theory-Guided Literature Review on Gender Bias in Health Care and Gendered Norms
> towards Patients with Chronic Pain. *Pain Res Manag.* 2018;2018:6358624.
> doi:10.1155/2018/6358624

**Empirical, and directly parallel to our design.**
> Chen EH, Shofer FS, Dean AJ, et al. Gender Disparity in Analgesic Treatment of
> Emergency Department Patients with Acute Abdominal Pain. *Acad Emerg Med.*
> 2008;15(5):414–418. doi:10.1111/j.1553-2712.2008.00100.x

**The ethics frame, recommended for an Ethics in AI paper.**
> Carel H, Kidd IJ. Epistemic injustice in healthcare: a philosophical analysis.
> *Med Health Care Philos.* 2014;17(4):529–540. doi:10.1007/s11019-014-9560-2
> *(Note: CrossRef's metadata misspells the title as "philosophial", cite the paper,
> not the registry. Third registry error found in this project.)*

## Why the epistemic-injustice frame is worth using

Carel and Kidd's **testimonial injustice** is the harm of not being believed because
of who you are. That is exactly what psychologizing is, and it transfers cleanly to
an LLM: a model that discounts a woman's reported symptoms is enacting testimonial
injustice at scale, without the excuse of a hurried clinician.

It also gives the paper a normative vocabulary an ethics venue will recognise, and it
connects the empirical result to a harm account rather than leaving it as a
difference in numbers.

## How this feeds the work

1. **Codebook (RQ6-style).** Build the psychologizing code from Samulowitz et al.'s
   gendered-norm categories rather than inventing categories. Apply it to generated
   rationales across all 15 vignettes.
2. **Term lists for RQ1.** The corpus-count terms for this concept come from this
   literature: anxiety, stress, emotional, hysterical, psychosomatic, somatization,
   "all in her head", attention-seeking, dramatic. A first probe already shows the
   signal is measurable, "he was anxious" returns 21,073 hits in the Pile against
   8,723 for "she was anxious", which **must** be base-rate normalised before it
   means anything.
3. **Framing.** Hoffmann & Tarzian for the introduction; Carel & Kidd for the
   discussion; Chen et al. as the human-clinician comparator.

## What to look for when you read

- A **categorisation** of psychologizing behaviours we can turn into codes
- Any **measurement instrument** already validated, reuse beats inventing
- Whether any study used **vignettes**, and how they anchored correctness
- Whether any addresses **trans or non-binary** patients (we expect almost nothing,
  which is itself citable)

---

# Reinstating G3-03: the literature exists, and it changes the design

**Added 2026-10-26. Status: PROPOSED, needs Evans's approval (see D027).**

D020 dropped G3-03 because no guideline says "do not attribute this patient's
symptoms to anxiety," so the vignette could never get a sourced reference answer.
That reasoning was right about the guideline and **wrong about the design**. The
literature search below turns up two clinician vignette studies that solve it, by
showing that the question was being asked the wrong way round.

## The two papers that matter

**Chiaramonte, G. R., & Friend, R. (2006).** Medical students' and residents'
gender bias in the diagnosis, treatment, and interpretation of coronary heart
disease symptoms. *Health Psychology*, 25(3), 255–266.
[doi:10.1037/0278-6133.25.3.255](https://doi.org/10.1037/0278-6133.25.3.255)
*(CrossRef-verified.)*

Two experiments, 87 internists and 143 family physicians. A vignette patient,
a 47-year-old man or a 56-year-old woman, matched for CHD risk by age, with
**identical CHD symptoms and risk factors**. The only manipulation: half the
vignettes added that the patient had recently experienced a life stressor and
appeared anxious.

| With the stress cue | Women | Men |
|---|---|---|
| CHD diagnosis | **15%** | 56% |
| Cardiologist referral | **30%** | 62% |
| Cardiac medication | **13%** | 47% |

**Without the stress cue, no gender bias was observed.** With it, women's chest
pain, breathlessness and palpitations were attributed to psychogenic causes; men's
were read as organic in both conditions.

**Biddle, C., Fallavollita, J. A., Homish, G. G., & Orom, H. (2019).** Gender bias
in clinical decision making emerges when patients with coronary heart disease
symptoms also have psychological symptoms. *Heart & Lung*, 48(4), 331–338.
[doi:10.1016/j.hrtlng.2018.11.005](https://doi.org/10.1016/j.hrtlng.2018.11.005)
*(CrossRef-verified.)*

The title is the finding. An independent replication, thirteen years later, of the
same conditional structure.

## Why this changes the design rather than just supporting it

The two papers agree on something the original G3-03 plan did not account for:
**the psychologizing bias is conditional on a psychological-symptom cue.** Absent
the cue, both studies found no gender difference.

A standalone "psychologizing vignette" with no cue would therefore most likely
have measured **nothing**: and a null there would have been uninterpretable,
because we could not have distinguished "the model is unbiased" from "we omitted
the trigger."

## The proposed design: a crossed cue factor, not a new condition

Do not reinstate G3-03 as a 16th condition. Instead add **cue presence** as a
crossed binary factor on the existing Group 3 vignettes:

- **cue absent:** the clinical findings as written.
- **cue present:** the same findings plus one fixed sentence, a recent life
  stressor and the patient appearing anxious, worded **identically across every
  gender arm**, exactly as the pregnancy-exclusion sentence already is (D018).

**This solves the guideline problem that killed G3-03.** We never ask the model
*not* to psychologize, which is what no guideline mandates. We ask for the
guideline-mandated action, and manipulate whether a stress cue is present. The
guideline's answer is **unchanged by the cue**: the AHA/ACC chest pain guideline
specifies what an acute presentation requires, and a patient being stressed does
not alter it. So the reference answer stays sourced and stays constant, which is
the project's central design rule.

Psychologizing is then measured as the **drop in guideline concordance caused by
the cue**, and the bias is the interaction:

```
estimand  =  [concordance(man, cue) − concordance(man, no cue)]
           − [concordance(woman, cue) − concordance(woman, no cue)]
```

That is precisely the quantity Chiaramonte & Friend and Biddle et al. measured in
humans, which means the result is directly comparable to a published human
baseline, and "we replicate a documented clinician bias in language models" is a
stronger claim than "we found a gender gap."

**Cost.** Applied to all four Group 3 vignettes: 96 prompts become 192, and the
total rises from 360 to 456. Scoring is one forward pass per option, so this is
minutes of compute. Applied to G3-02 alone it is 24 extra prompts.

## What this costs in the pre-registration

It adds a hypothesis after the D025 freeze, so it must go in the deviations table
(§9) with its date and the note that it was decided **before any score existed**,
not folded in silently. The honest framing: H1–H4 were derived from our own corpus
data; this one is derived from published human-subject findings, which is a
different and in some ways better provenance, but it is still an addition and must
be labelled as one.

## Supporting literature for the construct

| Paper | What it gives you |
|---|---|
| **Maserejian, Link, Lutfey, Marceau & McKinlay (2009),** *J Women's Health* 18, 1661–1667, [doi:10.1089/jwh.2008.1007](https://doi.org/10.1089/jwh.2008.1007) | Video-vignette factorial experiment, 128 physicians; disparities in interpreting identical CHD symptoms by patient gender |
| **Maserejian, Lutfey & McKinlay (2009),** *Health Services Research* 44, 1933–1949, [doi:10.1111/j.1475-6773.2009.01022.x](https://doi.org/10.1111/j.1475-6773.2009.01022.x) | Whether physicians attend to base rates, directly relevant to our corpus-skew mechanism |
| **Werner & Malterud (2003),** *Soc Sci Med* 57, 1409–1419, [doi:10.1016/s0277-9536(02)00520-8](https://doi.org/10.1016/s0277-9536(02)00520-8) | "It is hard work behaving as a credible patient", the qualitative anchor for testimonial injustice |
| **Hoffmann & Tarzian (2001)** | The canonical pain-dismissal citation, already in the project |
| **Carel & Kidd** | Epistemic/testimonial injustice, the ethics frame |

## A separate opportunity, and a trap to avoid

**NICE NG73 (endometriosis)** looked like a second candidate: recommendation
**1.5.4** reportedly states *"Do not exclude the possibility of endometriosis if
the abdominal or pelvic examination and ultrasound scan are normal, and recognise
that referral may still be necessary even with a normal scan"*, a
guideline-mandated action in a famously dismissed presentation, with diagnostic
delay well documented (**Nnoaham et al. 2011**, *Fertil Steril* 96, 366–373,
[doi:10.1016/j.fertnstert.2011.05.090](https://doi.org/10.1016/j.fertnstert.2011.05.090)).

**It cannot serve as a Group 3 vignette.** Endometriosis requires a uterus, so the
gender arms are not exchangeable and it belongs in Group 2, where the answer is
*supposed* to differ. Using it for the man-vs-woman psychologizing contrast would
be exactly the error Group 2 exists to catch.

It is, however, a good candidate for a **trans-specific** vignette: gender
identity *man*, SPCU *female*. That is a clinically real presentation, it tests
whether the model follows the stated SPCU rather than the gender label, and it
pairs with the NG126 finding in G2-01. Worth considering as a separate addition,
not as a fix for G3-03.

**Note on the NG73 wording:** taken from a search result, **not** confirmed at
source. NICE blocks scripted access, so it needs a human read before it can be
marked VERIFIED, per the project's normal sourcing rule.
