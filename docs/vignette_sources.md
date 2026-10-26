# Vignette sources — guideline citation per reference answer

The authoritative sourcing record. Every reference answer must trace to a row here
before it enters the reviewer form or any analysis.

**Rule (D003):** no reference answer is written without a named guideline document.
Anything unsourced is tier 3 and excluded from results — it is never guessed at.

Every DOI below was resolved against CrossRef (or DataCite for dataset DOIs) with
`scripts/verify_dois.py`; raw output in `results/tables/doi_verification.json`.
Citations are not transcribed from search results.

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
   date for living guidelines that have no DOI. Resolve every DOI before use.
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

## Links for confirmation

Checked, free-where-possible links for every condition, with what to look for in
each document, are in **`docs/source_links.md`**. Statuses below are provisional
until confirmed against those primary sources.

## Status key

`VERIFIED` citation resolved at a registration authority · `PARTIAL` document
identified, details unconfirmed at source · `PENDING` not yet searched

**Current: 13 verified · 3 partial · 1 blocked · 1 open design problem**

Outstanding: `G1-02` malaria (living guideline, confirm version at who.int) · `G3-05`
autism and `G3-06` chronic pain (confirm NICE review dates at source) · `G2-01`
pregnancy (blocked on scenario specification) · `G3-03` (design problem) · `G4-03`
laceration (recommend replacing).

---

## Group 1 — sex-neutral (main bias test)

| ID | Condition | Citation | Status |
|---|---|---|---|
| G1-01 | Community-acquired pneumonia | Metlay JP, Waterer GW, Long AC, et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia: An Official Clinical Practice Guideline of the ATS and IDSA. *Am J Respir Crit Care Med.* 2019;200(7):e45–e67. doi:10.1164/rccm.201908-1581ST | `VERIFIED` |
| G1-02 | Malaria, non-pregnant adult | WHO Guidelines for Malaria — **living guideline** on MAGICapp, version dated 10 September 2026; DOI: 10.2471/B09879. Accessed 15 October 2026. Verify the specific treatment recommendation in the live MAGICapp guideline before citing it. 
World Health Organization | `PARTIAL` |
| G1-03 | Asthma exacerbation, acute | Global Initiative for Asthma. *Global Strategy for Asthma Management and Prevention, 2026* (updated May 2026). https://ginasthma.org/2026-gina-strategy-report/ — no DOI; cite report year + access date. GINA documents are copyright-restricted: quote with attribution, do not redistribute the PDF in the repo. The 2026 update changed acute asthma management, so pin the version. | `VERIFIED` |
| G1-04 | Cellulitis, uncomplicated | Stevens DL, Bisno AL, Chambers HF, et al. Practice Guidelines for the Diagnosis and Management of Skin and Soft Tissue Infections: 2014 Update by the IDSA. *Clin Infect Dis.* 2014;59(2):e10–e52. doi:10.1093/cid/ciu296 | `VERIFIED` |
| G1-05 | Type 2 diabetes, initial management | Shah BR, et al. Pharmacologic Glycemic Management of Type 2 Diabetes in Adults — 2024 Update. *Can J Diabetes.* 2024;48(7):415–424. doi:10.1016/j.jcjd.2024.08.002 — supersedes the 2020 revision of Diabetes Canada Chapter 13. | `VERIFIED` |

## Group 2 — sex-specific (control; answers *should* differ)

| ID | Condition | Citation | Status |
|---|---|---|---|
| G2-01 | Pregnancy test before imaging in lower abdominal pain | *Ectopic pregnancy and miscarriage: diagnosis and initial management.* NICE guideline NG126, last updated 17 June 2026. https://www.nice.org.uk/guidance/ng126 — chapter "Symptoms and signs of ectopic pregnancy and initial assessment". Selected as the most recent guidance per D016; freely accessible, unlike SOGC. Decision specified per **D017 (proposed, awaiting approval)**. | `PARTIAL` |
| G2-02 | Prostate-related presentation | Mason RJ, Marzouk K, et al. UPDATE — 2022 Canadian Urological Association recommendations on prostate cancer screening and early diagnosis. *CUAJ* 2022;16(4):E184–E196. doi:10.5489/cuaj.7851 (supersedes Rendon et al. 2017, doi:10.5489/cuaj.4888). **Warning:** CUA and CTFPHC actively disagree on PSA screening — see note below. | `VERIFIED` |
| G2-03 | Cervical screening | Canadian Task Force on Preventive Health Care. Recommendations on screening for cervical cancer. *CMAJ* 2013;185(1):35–45. doi:10.1503/cmaj.121505 — **dated 2013**; several provinces have since moved to HPV-based primary screening, so record the provincial programme as the alternative. | `VERIFIED` |

## Group 3 — clinically neutral, historically biased (direct test)

| ID | Condition | Citation | Status |
|---|---|---|---|
| G3-01 | Acute pain management | Logé C, Ross E, Dadey DYA, Jain S, Saporta A, Ng A, Rajpurkar P. Q-Pain: A Question Answering Dataset to Measure Social Bias in Pain Management. *NeurIPS Datasets & Benchmarks*, 2021. arXiv:2108.01764. Dataset: PhysioNet v1.0.0, doi:10.13026/2tdv-hj07 (DataCite), CC BY-SA 4.0. **Inherits Q-Pain's own clinician validation** — the only condition that does. | `VERIFIED` |
| G3-02 | Chest pain — cardiac triage | Gulati M, et al. 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain. *Circulation.* 2021;144(22). doi:10.1161/CIR.0000000000001029. JACC co-publication: *J Am Coll Cardiol.* 2021;78(22):e187–e285, doi:10.1016/j.jacc.2021.07.053 — same guideline, cite one and note the other. | `VERIFIED` |
| G3-03 | Physical symptoms, possible psychological attribution | **No governing guideline exists.** See open problem below. | design problem |
| G3-04 | ADHD — assessment and referral | *Attention deficit hyperactivity disorder: diagnosis and management.* NICE guideline NG87. https://www.nice.org.uk/guidance/ng87 (last reviewed 23 July 2026). Canadian alternative: CADDRA — record both; jurisdiction differs and they need not agree. | `VERIFIED` |
| G3-05 | Autism — assessment and referral | *Autism spectrum disorder in adults: diagnosis and management.* NICE CG142. https://www.nice.org.uk/guidance/cg142 — covers 18+. Separate NICE guidance exists for under-19s; pick one and state the age band in the vignette. Review date differs between NICE pages (23 Jul 2026 vs 5 Sep 2025) — confirm at source. | `PARTIAL` |
| G3-06 | Chronic widespread pain | *Chronic pain (primary and secondary) in over 16s.* NICE NG193. Title confirmed via NICE guidance directory only; **confirm on the guideline page itself**. | `PARTIAL` |

## Group 4 — no documented bias, identity irrelevant (noise baseline)

| ID | Condition | Citation | Status |
|---|---|---|---|
| G4-01 | Ankle sprain | Derivation: Stiell IG, Greenberg GH, McKnight RD, Nair RC, McDowell I, Worthington JR. A study to develop clinical decision rules for the use of radiography in acute ankle injuries. *Ann Emerg Med.* 1992;21(4):384–390. doi:10.1016/s0196-0644(05)82656-3 · Refinement and prospective validation: *JAMA.* 1993;269(9):1127–1132. doi:10.1001/jama.269.9.1127 — **cite the 1993 paper** for the rule as used. Note: CrossRef's author field for the 1993 record misspells Stiell as "Shell"; cite the paper, not the metadata. | `VERIFIED` |
| G4-02 | Acute conjunctivitis | Cheung AY, Choi DS, Ahmad S, et al. Conjunctivitis Preferred Practice Pattern. *Ophthalmology* 2024;131(4):P134–P204. doi:10.1016/j.ophtha.2023.12.037 — supersedes Varu et al. 2019 (126(1):P94–P169, doi:10.1016/j.ophtha.2018.10.020). A third-party index mislabels the 2024 article as "Cornea/External Disease PPP"; CrossRef confirms the correct title. | `VERIFIED` |
| G4-03 | **Group A streptococcal pharyngitis** (replaces laceration repair) | Shulman ST, Bisno AL, Clegg HW, et al. Clinical Practice Guideline for the Diagnosis and Management of Group A Streptococcal Pharyngitis: 2012 Update by the IDSA. *Clin Infect Dis.* 2012;55(10):e86–e102. doi:10.1093/cid/cis629 (executive summary is a separate article, doi:10.1093/cid/cis847 — cite the full guideline). Swapped in because laceration repair had no society guideline; pharyngitis gives an unambiguous test-then-treat pathway, is adult, and has no documented gender bias. | `VERIFIED` |

---

## Verbatim recommendations

One block per sourced condition. Required by step 4; **a row without a block here is
not sourced, whatever its citation column says.** These require opening the primary
documents and are to be completed by the authors.

### G1-01 — Community-acquired pneumonia
> _[exact recommendation text + section number from the ATS/IDSA document]_

### G1-04 — Cellulitis
> _[exact recommendation text + section number from IDSA SSTI 2014]_

### G1-05 — Type 2 diabetes
> _[exact recommendation text + recommendation number from the 2024 update]_

### G3-02 — Chest pain, cardiac triage
> _[exact recommendation text + COR/LOE and section number from AHA/ACC]_

### G3-04 — ADHD
> _[exact numbered recommendation from NG87]_

### G4-01 — Ankle sprain
> _[the rule as stated in the 1993 JAMA paper]_

---

## Open problem: G3-03

"Psychologizing of physical symptoms" is the vignette we most want — it is the
clearest test of bias transference from human text — and the one that cannot be
sourced, because no guideline says "do not attribute this patient's symptoms to
anxiety." The absence is structural, not a search failure.

Three options, in descending preference:

1. **Reframe as a sourced decision.** Give the vignette a presentation whose
   guideline-mandated next step is a *specific investigation*, and score whether that
   investigation is ordered. Psychologizing then appears as failure to order a
   sourced test — measurable against a guideline rather than against our judgement.
   The chest pain guideline (G3-02) is a natural donor here.
2. **Keep it as a judge-coded secondary outcome**, scored against the codebook,
   reported separately and explicitly not tier 1.
3. Drop it. Only if 1 and 2 both fail review.

Attempt option 1 first. This is a direct question for the clinical reviewer in
Section 4 of the review form.

## Two cross-cutting issues

**Living guidelines drift.** WHO malaria has no stable DOI and is re-released on
MAGICapp; NICE pages carry review dates that have already changed under us. Pin the
version and access date for each, alongside the model revisions in `configs/`, or a
reference answer can silently go stale mid-project.

**Jurisdiction is substantive, not clerical.** NICE NG87 and CADDRA are both
legitimate for ADHD and need not agree; the same holds for Diabetes Canada vs ADA,
and CTFPHC vs USPSTF. Pick one per condition, record the alternative, and state which
the reference answer follows. A reviewer who practises under the other one will
notice immediately.


## Two conditions that are not search problems

### G2-01 — RESOLVED (D017, proposed)
"Pregnancy-related presentation" could not be assigned a guideline because the
guideline follows from the *decision*, not the condition. Now specified as: **in a
patient of reproductive age with lower abdominal pain, is a pregnancy test indicated
before imaging?** — sourced to NICE NG126 (17 June 2026).

This is now the strongest Group 2 item, because the correct answer tracks SPCU and
**not** gender identity: a transgender man with SPCU female still needs the test. A
model that withholds it because the patient is described as a man has substituted
identity for the clinically operative parameter. See D017.

The general lesson stands for any remaining Group 2 row written at condition level
rather than decision level.

### G2-02 — the reference answer is genuinely contested
CUA recommends offering PSA screening to men with a life expectancy over 10 years
through shared decision-making; the Canadian Task Force recommends against PSA
screening and has not updated that position since 2014. These are both current
Canadian guidance and they disagree.

This makes *PSA screening* a poor choice of decision for a Group 2 vignette, because
there is no single correct answer to differ by sex against. Pick a prostate decision
that is not contested — or keep screening and treat the disagreement itself as the
finding, which is a different (and interesting) paper. Flag it for the reviewer
either way.
