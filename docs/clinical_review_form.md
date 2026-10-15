# Clinical review form

**Project:** From datasheet to diagnosis — gender bias in LLM health advice
**Authors:** Evans Kumi, Aymen Boustani · MSc Intelligent Systems, McGill
**Reviewer time:** 45–60 minutes
**Return to:** kwakukumi14@gmail.com

> **Authors' note — do not send this form until Section 2 is complete.**
> Cells marked _[authors to complete]_ are filled by **us**, from primary guideline
> sources, before the form is sent. A reviewer cannot answer Column A against a blank
> reference answer, and sending an unfilled form wastes the one ask we get. Condition
> placement in Section 2 is **provisional** — Column B is precisely what tests it.

## Who fills what

| Column | Filled by | Contents |
|---|---|---|
| ID, Grp, Condition | **Authors** | already done |
| Scenario | **Authors** | one line; patient age and SPCU stated and held fixed |
| Proposed reference answer | **Authors** | the management decision we believe is correct |
| Guideline cited | **Authors** | society, document, year, section, plus URL or DOI |
| **A**, **B**, **C** | **Reviewer** | left deliberately blank — the only cells they fill |

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
