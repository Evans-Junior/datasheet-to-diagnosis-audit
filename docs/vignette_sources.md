# Vignette sources — guideline citation per reference answer

The authoritative sourcing record. Every reference answer must trace to a row here
before it enters the reviewer form or any analysis.

**Rule (D003):** no reference answer is written without a named guideline document.
Anything unsourced is tier 3 and excluded from results — it is never guessed at.

## How to fill a row — procedure

Work one condition at a time, in this order. Do not skip step 4.

1. **Find the governing guideline.** Prefer, in order: a specialty society clinical
   practice guideline (IDSA, AHA/ACC, ATS), a national body (NICE, WHO, Diabetes
   Canada, CADDRA), then a systematic review. Never a textbook, UpToDate, or a
   journal narrative review — those orient you, they do not source you.
2. **Open the primary document** and find the specific recommendation. Not the
   abstract, not a summary site, not a "top ten takeaways" page. The recommendation
   text itself, with its section or recommendation number.
3. **Record the citation** with DOI where one exists, or a stable URL plus an access
   date for living guidelines that have no DOI.
4. **Quote the recommendation verbatim** into `verbatim_recommendation` below, with
   its section number. This is the step that makes the claim checkable and the step
   most easily skipped. If you cannot quote it, you have not sourced it.
5. **Write the reference answer** as the single decision the vignette asks for
   (e.g. a drug class, a triage level, a yes/no referral) — not a paragraph of
   management.
6. **Assign a tier:** 1 = sourced and clinician-confirmed · 2 = sourced only ·
   3 = `needs_clinician_review`.
7. **Note the jurisdiction.** Guidelines conflict across countries. Where UK (NICE)
   and North American guidance differ, record both and say which the reference
   answer follows — a reviewer will ask.

## Verification status key

- `VERIFIED` — citation confirmed against a primary or publisher record
- `PARTIAL` — document identified, citation details still to confirm at source
- `PENDING` — not yet searched

---

## Group 1 — sex-neutral (main bias test)

| ID | Condition | Guideline | Citation | Status |
|---|---|---|---|---|
| G1-01 | Community-acquired pneumonia | ATS/IDSA 2019 | Metlay JP, Waterer GW, Long AC, et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia. *Am J Respir Crit Care Med.* 2019;200(7):e45–e67. doi:10.1164/rccm.201908-1581ST | `VERIFIED` |
| G1-02 | Malaria, non-pregnant adult | WHO Guidelines for Malaria (living guideline, MAGICapp) | Version-dated; a Sept 2026 release supersedes 13 Aug 2025. Cite the exact version plus access date. A DOI of 10.2471/B09514 is circulating for the Aug 2025 version but came from a third-party host — **confirm at who.int before use**. | `PARTIAL` |
| G1-03 | Asthma exacerbation, acute | GINA report / CTS | — | `PENDING` |
| G1-04 | Cellulitis, uncomplicated | IDSA skin and soft tissue infections | — | `PENDING` |
| G1-05 | Type 2 diabetes, initial management | Diabetes Canada / ADA Standards of Care | — | `PENDING` |

## Group 2 — sex-specific (control; answers *should* differ)

| ID | Condition | Guideline | Citation | Status |
|---|---|---|---|---|
| G2-01 | Pregnancy-related presentation | SOGC / NICE NG201 | — | `PENDING` |
| G2-02 | Prostate-related presentation | CUA / AUA / EAU | — | `PENDING` |
| G2-03 | Cervical screening | Canadian Task Force / USPSTF | — | `PENDING` |

## Group 3 — clinically neutral, historically biased (direct test)

| ID | Condition | Guideline | Citation | Status |
|---|---|---|---|---|
| G3-01 | Acute pain management | Inherits Q-Pain's clinician validation | Logé C, et al. Q-Pain: A Question Answering Dataset to Measure Social Bias in Pain Management. *NeurIPS Datasets & Benchmarks*, 2021. PhysioNet, CC BY-SA 4.0. | `PARTIAL` |
| G3-02 | Chest pain — cardiac triage | 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR | Gulati M, et al. 2021 Guideline for the Evaluation and Diagnosis of Chest Pain. *Circulation.* 2021. doi:10.1161/CIR.0000000000001029 (PMID 34709879). JACC co-publication: doi:10.1016/j.jacc.2021.07.053 | `VERIFIED` |
| G3-03 | Physical symptoms, possible psychological attribution | **No single governing guideline identified** | Likely irreducibly tier 3. See note below. | `PENDING` |
| G3-04 | ADHD — assessment and referral | NICE NG87 | *Attention deficit hyperactivity disorder: diagnosis and management.* NICE guideline NG87. https://www.nice.org.uk/guidance/ng87 (last reviewed 23 July 2026). Canadian alternative: CADDRA guidelines — record both, jurisdiction differs. | `VERIFIED` |
| G3-05 | Autism — assessment and referral | NICE CG142 (adults) | *Autism spectrum disorder in adults: diagnosis and management.* NICE clinical guideline CG142. https://www.nice.org.uk/guidance/cg142 — covers 18+. Separate NICE guidance exists for under-19s; pick one and state the age band in the vignette. Review date differs between NICE pages (23 July 2026 vs 5 Sept 2025) — confirm at source. | `PARTIAL` |
| G3-06 | Chronic widespread pain | NICE NG193 | *Chronic pain (primary and secondary) in over 16s: assessment of all chronic pain and management of chronic primary pain.* NICE guideline NG193. Title confirmed via NICE guidance directory; **confirm on the guideline page itself**. | `PARTIAL` |

## Group 4 — no documented bias, identity irrelevant (noise baseline)

| ID | Condition | Guideline | Citation | Status |
|---|---|---|---|---|
| G4-01 | Ankle sprain | Ottawa Ankle Rules (Stiell et al.) | — | `PENDING` |
| G4-02 | Acute conjunctivitis | AAO Preferred Practice Pattern | — | `PENDING` |
| G4-03 | Uncomplicated laceration repair | — | — | `PENDING` |

---

## Verbatim recommendations

One block per sourced condition. Required by step 4; a row without a block here is
not sourced, whatever its citation column says.

### G1-01 — Community-acquired pneumonia
> _[paste the exact recommendation text and its section number from the ATS/IDSA
> document]_

### G3-02 — Chest pain, cardiac triage
> _[paste the exact recommendation text and its COR/LOE and section number from the
> AHA/ACC document]_

### G3-04 — ADHD
> _[paste the exact numbered recommendation from NG87]_

---

## Open problem: G3-03

"Psychologizing of physical symptoms" is the vignette we most want — it is the
clearest test of bias transference from human text — and the one least likely to
have a governing guideline, because no guideline says "do not attribute this
patient's symptoms to anxiety."

Three options, in descending preference:

1. **Reframe as a sourced decision.** Instead of scoring whether the model
   psychologizes, give the vignette a presentation whose guideline-mandated next
   step is a specific investigation, and score whether that investigation is
   ordered. Psychologizing then shows up as *failure to order a sourced test* — which
   is measurable against a guideline rather than against our judgement.
2. **Keep it as a coded secondary outcome**, scored by the judge against the
   codebook, reported separately from the guideline-anchored results and explicitly
   not tier 1.
3. Drop it. Only if 1 and 2 both fail review.

Option 1 is the one to attempt first, and it is a question for the clinical reviewer
in Section 4 of the review form.
