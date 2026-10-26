# G3-03 theme — psychologizing of women's physical symptoms

G3-03 was dropped as a vignette (D020) because no guideline governs it. The
**construct** is retained as a codebook category applied to generated rationales
across all vignettes. This file gives the theme, the search vocabulary, and the
anchor citations, so the literature can be found and the codebook grounded.

## The construct in one sentence

A patient reports physical symptoms; the clinician attributes them to a
psychological cause (anxiety, stress, somatization) rather than investigating a
physical one — and does so more readily when the patient is a woman.

## Search vocabulary — use these terms, not "psychologizing"

"Psychologizing" is our working word and returns little. The established terms are:

| Term | Field | Why it helps |
|---|---|---|
| **diagnostic overshadowing** | clinical | The precise clinical term for attributing physical symptoms to a psychiatric cause. Best single search term. |
| **medical gaslighting** | popular / recent academic | Fast-growing literature since ~2022; good for recent empirical work and for public-harm framing. |
| **psychogenic attribution** | clinical psychology | Catches the older attribution literature. |
| **somatization bias** | psychiatry | Overlaps diagnostic overshadowing; more psychiatric framing. |
| **medically unexplained symptoms (MUS)** / **contested illness** | medical sociology | The literature on how unexplained symptoms are managed, heavily gendered. |
| **testimonial injustice** / **epistemic injustice in healthcare** | philosophy of medicine | **Strongest frame for an ethics paper** — the harm is not being believed. |
| **gender bias in pain assessment** | pain medicine | Connects to G3-01 and Q-Pain. |

## Anchor citations — all DOIs resolved at CrossRef

**The canonical reference. Cite this one.**
> Hoffmann DE, Tarzian AJ. The Girl Who Cried Pain: A Bias against Women in the
> Treatment of Pain. *J Law Med Ethics.* 2001;29(1):13–27.
> doi:10.1111/j.1748-720X.2001.tb00037.x

**The theory-guided review — most useful for building the codebook.**
> Samulowitz A, Gremyr I, Eriksson E, Hensing G. "Brave Men" and "Emotional Women":
> A Theory-Guided Literature Review on Gender Bias in Health Care and Gendered Norms
> towards Patients with Chronic Pain. *Pain Res Manag.* 2018;2018:6358624.
> doi:10.1155/2018/6358624

**Empirical, and directly parallel to our design.**
> Chen EH, Shofer FS, Dean AJ, et al. Gender Disparity in Analgesic Treatment of
> Emergency Department Patients with Acute Abdominal Pain. *Acad Emerg Med.*
> 2008;15(5):414–418. doi:10.1111/j.1553-2712.2008.00100.x

**The ethics frame — recommended for an Ethics in AI paper.**
> Carel H, Kidd IJ. Epistemic injustice in healthcare: a philosophical analysis.
> *Med Health Care Philos.* 2014;17(4):529–540. doi:10.1007/s11019-014-9560-2
> *(Note: CrossRef's metadata misspells the title as "philosophial" — cite the paper,
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
   signal is measurable — "he was anxious" returns 21,073 hits in the Pile against
   8,723 for "she was anxious", which **must** be base-rate normalised before it
   means anything.
3. **Framing.** Hoffmann & Tarzian for the introduction; Carel & Kidd for the
   discussion; Chen et al. as the human-clinician comparator.

## What to look for when you read

- A **categorisation** of psychologizing behaviours we can turn into codes
- Any **measurement instrument** already validated — reuse beats inventing
- Whether any study used **vignettes**, and how they anchored correctness
- Whether any addresses **trans or non-binary** patients (we expect almost nothing,
  which is itself citable)
