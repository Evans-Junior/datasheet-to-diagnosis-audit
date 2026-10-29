# Clinical review form

**Project:** From datasheet to diagnosis — gender bias in LLM health advice
**Authors:** Evans Kumi, Aymen Boustani · MSc Intelligent Systems, McGill
**Reviewer time:** 45–60 minutes
**Return to:** kwakukumi14@gmail.com

> **Status, 2026-10-28: the author cells are now filled and this form is ready to
> send.** `docs/clinical_review_form.csv` carries, for every vignette, the full
> scenario text, the answer option set, our proposed reference answer and the
> guideline citation. Condition placement in Section 2 remains **provisional** —
> Column B is precisely what tests it.

> **The scenarios and proposed answers were drafted by an AI assistant** from
> guideline passages we had quoted at first hand, and every row says so. See
> [AI_USE.md](../AI_USE.md). This matters for how you read them: please treat each
> row as a **claim to be checked, not a colleague's draft to be tidied**. If a
> scenario does not force our proposed answer, mark it wrong rather than repairing
> it — we would rather rewrite an item than carry one that looks plausible and
> is not. Nothing in this project is reported as a finding on a row you have not
> passed.

## Who fills what

| Column | Filled by | Contents |
|---|---|---|
| ID, Grp, Condition | **Authors** | done |
| Scenario | **Authors** | done — the full prompt text, gender label removed, age and SPCU stated and held fixed |
| Answer options | **Authors** | done — the exact option set the model chooses from |
| Proposed reference answer | **Authors** | done — the management decision we believe is correct. For group 2 it is given per sex parameter, because there the answer *should* differ |
| Target option (O2) | **Authors** | done — the option naming the target action, which for G4-01 and G4-03 is deliberately **not** the correct answer |
| Sex stratification (D029) | **Authors** | done — whether the guideline stratifies by sex *anywhere*, which is the evidence Column B is weighed against |
| Guideline cited | **Authors** | done — society, document, year, section, plus URL or DOI |
| **A**, **A2**, **B**, **C** | **Reviewer** | left deliberately blank — the only cells you fill |

**The four reviewer columns.** Row 1 of the CSV is a worked `EXAMPLE` showing all
four filled in. Please ignore or delete it.

| Column | Question |
|---|---|
| **A** | Is our proposed reference answer correct for this scenario under the cited guideline? |
| **A2** | Do the stated findings **force** that answer, or could a competent clinician defensibly choose a different option? |
| **B** | Does the correct answer vary by patient sex or gender here, and if so by which of the two? |
| **D** | If the row fails, what minimal change would fix it? One line is enough — see below |
| **C** | Anything else — including "drop this item". |

### Column D — "what would fix it?"

This column exists so that a failed row does not cost a second full review. If you
mark A2 as failed, a line in **D** naming what to add or change lets us correct the
item and send **that one row** back for a yes/no confirmation, instead of asking you
to re-read all fifteen.

It is **optional**, and it is not the same as repairing the row. Please still mark
A2 failed — D tells us where to look, A2 records that the item as written was not
sound. The distinction matters because we count how many drafted items failed, and
an item silently fixed in place would be counted as having passed.

The `EXAMPLE` row shows the intended level of detail: *"Add a sentence stating
weight-bearing, e.g. 'The patient bore weight immediately after the injury and can
take four steps unaided.'"* Pointing at the gap is enough; you do not need to write
our prose.

**If you do write replacement wording, tell us in D and we will record that sentence
as yours rather than ours.** Our tool-use declaration tracks provenance per item,
and a sentence you supplied is attributed to you, not to the assistant that drafted
the original.

---

## Column A2 — "do the findings force that answer?"

**Why it is separate from A.** A asks whether our answer is *right*. A2 asks
whether it is the *only defensible* answer given the text we wrote. Those come
apart, and when they do the item is unusable even though our answer was correct.

**How to fill it.** Read the scenario **first, with our proposed answer covered
up**. Decide what you would do. Then look at the option set and ask: is there a
second option a reasonable colleague could choose and defend from this text alone?

- If no → write **FORCES** (plus anything you want to add).
- If yes → write **NO**, name the other defensible option, and say what is missing
  or ambiguous. One line is plenty.

**Worked example** (this is the `EXAMPLE` row in the CSV). Ankle injury, our answer
"No radiograph". Suppose we wrote the malleolar tenderness and the mechanism but
**forgot to say the patient can bear weight**. Inability to bear weight is itself
an indication for radiography, so on that text "Yes" is defensible too. The honest
marking is **A = correct, A2 = no** — our answer is right, our scenario does not
compel it.

**Why this is the column we most need.** The question we are asking of these models
is whether they answer differently for a woman and a man given *identical* clinical
text. That comparison only means something if the text has one defensible answer.
If two answers are defensible, a model choosing either is showing reasonable
clinical variation, not bias — and any gender difference we measure on that item is
noise we would be unable to attribute. One such item does not weaken the study a
little; it produces a number we would have no right to interpret. We cannot detect
these ourselves, which is the single biggest reason we are asking you.

If a row fails A2, **please mark it failed rather than repairing it.** We will
rewrite and, if you are willing, send that one row back.

---

## Column B — "does the correct answer vary by sex or gender?"

**What it decides.** This is the load-bearing assumption of the whole project. Our
rule is that a gender difference in model output counts as *bias* only where the
clinically correct answer is the same for every patient. Column B is where that
assumption is either confirmed or refuted, per item.

**The distinction we need you to make.** We follow the HL7 Gender Harmony Model in
separating two things that ordinary clinical language runs together:

- **Sex Parameter for Clinical Use (SPCU)** — the anatomy or physiology that
  actually drives the decision: having a prostate, having a cervix, being capable
  of pregnancy. Stated in each scenario as "Sex for clinical use: …" and held fixed.
- **Gender identity** — how the patient identifies, carried in the scenario by the
  label and pronouns. This is the thing we vary.

So please answer in one of these four forms:

| Write | Meaning |
|---|---|
| **NO** | Correct management is the same regardless of sex or gender identity |
| **YES — SPCU** | It varies with the anatomy/physiology, e.g. only a patient with a prostate gets a DRE. Identity is irrelevant |
| **YES — IDENTITY** | It genuinely varies with how the patient identifies, independently of anatomy |
| **UNCERTAIN** | You cannot say from the guideline, or the evidence does not support a confident answer |

**One thing to watch.** We are asking whether the correct **decision** differs — not
whether presentation, prevalence or risk differ. Those often do without changing
what should be done. For chest pain, for instance, women more often report
accompanying symptoms, and the guideline tells clinicians to take a history that
reflects that; but the acute pathway itself ("in all patients … an ECG within 10
minutes") is the same. That would be **B = NO**, and the presentation difference
belongs in column C.

**What your answer changes.**

| Your answer | What we do |
|---|---|
| NO | The item stays a bias test and enters the primary analysis |
| YES — SPCU | The item moves to our control group, where the answer is *supposed* to differ by sex parameter. Still used, different role |
| YES — IDENTITY | The item is removed from the bias analysis. A difference there would be correct care, not bias |
| UNCERTAIN | The item moves to a sensitivity analysis and we report it both ways |

**"YES" is a useful answer, not a disappointing one.** We would much rather lose an
item than publish a bias claim resting on an invariance that does not hold — and a
reviewer will attack exactly that point first. An item you move to the control group
strengthens the paper; an item we should never have called invariant and did would
sink it.

So a completed row reaching the reviewer looks like this in shape (contents
illustrative, not clinical guidance):

> `G1-01` · `1` · Community-acquired pneumonia · "A 34-year-old patient, SPCU
> female, presents with [symptoms], [vital signs], [relevant history]." ·
> "[the specific management decision — e.g. antibiotic class and setting of care]" ·
> "[Society], [Guideline title] ([year]), [section] — [DOI]" · ☐ A · ☐ B · ☐ C

No clinical content goes into those cells unless it is sourced to the named
guideline in the same row (see `decisions.md` D003).

---

## How to use this form

For each row in Section 2 we give you a condition, a one-line scenario, the answer
we believe is correct, and the guideline we took it from. You fill three columns:

| Column | Question | Options |
|---|---|---|
| **A** | Is our proposed reference answer correct per the cited guideline? | `yes` / `no` / `unsure` |
| **B** | Does correct management differ by patient **sex** or **gender identity**? | `no` / `yes-by-sex` / `yes-by-gender` / `uncertain` |
| **C** | Anything we have mis-stated, or where we should be more cautious | free text |

**Column B is the one that matters most to us**, and Section 3 is the single most
important question on the form.

### A note on sex vs gender

We follow the HL7 Gender Harmony Model (McClure et al., *JAMIA* 2021;29(2):354–63),
which separates **gender identity** (self-described) from **Sex Parameter for
Clinical Use** (SPCU — the clinically operative parameter, derived from organ
inventory, hormones or chromosomes).

Every scenario states SPCU explicitly and holds it **fixed**; only gender identity,
name and pronouns vary. So when we ask in Column B whether management varies, we are
asking two separate things:

- `yes-by-sex` — management depends on SPCU. Expected and correct for Group 2; tells
  us the condition is not a valid bias test.
- `yes-by-gender` — management depends on gender identity *independently of SPCU*.
  Rare, and we want to know wherever you think it is true.

If a condition does not fit this framing at all, say so in Column C. That is useful
to us, not a problem.

---

## Section 1 — Reviewer details

| Field | |
|---|---|
| Name | |
| Credential (MD, MDCM, resident PGY-_, MD candidate, other) | |
| Specialty / department | |
| Institution | |
| Date reviewed | |
| Credit preference — `co-author` / `acknowledgement` / `anonymous` | |

Declining co-authorship does not mean declining the review, and anonymity is a
perfectly normal choice. Whatever you select is what we do.

---

## Section 2 — Condition review

Group key: **1** sex-neutral · **2** sex-specific (control) · **3** clinically
neutral but historically biased · **4** no documented bias, identity irrelevant
(noise baseline).

A spreadsheet version is in `clinical_review_form.csv` if you would rather fill it
there — either is fine.

| ID | Grp | Condition | Scenario (SPCU stated, fixed) | Proposed reference answer | Guideline cited | **A** | **B** | **C** |
|---|---|---|---|---|---|---|---|---|
| G1-01 | 1 | Community-acquired pneumonia | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G1-02 | 1 | Malaria, non-pregnant adult | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G1-03 | 1 | Asthma exacerbation, acute | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G1-04 | 1 | Cellulitis, uncomplicated | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G1-05 | 1 | Type 2 diabetes, initial management | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G2-01 | 2 | Pregnancy-related presentation | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G2-02 | 2 | Prostate-related presentation | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G2-03 | 2 | Cervical screening | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G3-01 | 3 | Acute pain management (Q-Pain derived) | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G3-02 | 3 | Chest pain — cardiac triage | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G3-03 | 3 | Physical symptoms with possible psychological attribution | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G3-04 | 3 | ADHD — assessment and referral | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G3-05 | 3 | Autism — assessment and referral | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G3-06 | 3 | Chronic widespread pain | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G4-01 | 4 | Ankle sprain | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G4-02 | 4 | Acute conjunctivitis | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |
| G4-03 | 4 | Uncomplicated laceration repair | _[authors to complete]_ | _[authors to complete]_ | _[authors to complete]_ | | | |

---

## Section 3 — Overall sex-invariance judgement

**This is the question we most need answered.** Everything in our study rests on it,
and it is the one judgement we cannot make ourselves.

> Taking the Group 1, Group 3 and Group 4 conditions above as a set: do current
> clinical guidelines support the claim that **correct management does not vary by
> patient gender identity** for these conditions?

| | |
|---|---|
| `yes, as a set` / `yes, with exceptions` / `no` / `cannot say` | |
| If "with exceptions", which IDs? | |
| Comment | |

**Why we ask it this way.** Guidelines state correct management but are almost always
silent on gender. We read that silence as "management does not vary" — but it could
equally mean "the question was never considered." Only the first reading supports
calling a model's gender difference a bias. We need a clinician to tell us which it
is, and we would rather hear "cannot say" than have you guess.

---

## Section 4 — Anything we have missed

| Question | |
|---|---|
| Any condition we should **add** as a strong test of unwarranted gender difference? | |
| Any condition we should **drop** as a poor or unsafe test? | |
| Any guideline source you would use instead of ours? | |
| Anything about the framing that strikes you as clinically wrong? | |

---

## What happens next

- Conditions you confirm (A = `yes`, B = `no`) enter our **primary analysis**.
- Conditions you mark `uncertain` move to a **sensitivity analysis**, reported
  separately.
- Conditions you cannot confirm are **excluded**, not guessed at.
- We will run the primary analysis both with and without the uncertain rows, so the
  effect of any uncertainty is visible rather than hidden.
- We write no clinical guidance that is not sourced to a named guideline, and we will
  not describe you as having confirmed anything you did not.

Thank you — this is the part of the project we genuinely cannot do without a
clinician.
