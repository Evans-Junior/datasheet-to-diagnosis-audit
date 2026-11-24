# Clinical review pack

From datasheet to diagnosis: tracing gender bias through open training-data
pipelines into LLM health advice. Evans Kumi and Aymen Boustani, MSc
Intelligent Systems, McGill.

Everything needed for the review is in this folder. Read them in order.

| | File | What it is |
|---|---|---|
| 1 | `01_START_HERE_what_we_are_asking.md` | One page: what we are testing and why a clinician is needed |
| 2 | `02_REVIEW_FORM.xlsx` | **The form.** Open the `Review` sheet and fill columns N to S |
| 3 | `03_briefing_notes.md` | How to read each column, plus Sections 1, 3 and 4 |
| 4 | `04_vignettes_compendium.md` | Background: every vignette and how it was built |
| 5 | `guidelines/` | The guideline PDFs, one per vignette, named by vignette id |

## Where to spend your time

The `Review` sheet is the whole task. Column G holds the guideline quote and
column I holds the clinical text exactly as the model receives it. The question
is whether a clinician reading column I could reach the reference answer in
column L **and no other answer**. Column H is our own reading of whether the
guideline stratifies by sex anywhere; please contradict it where you disagree.

Group 2 rows appear with both sex-parameter arms, because for those three the
correct answer is meant to differ.

**Please reject rather than repair.** If an item is wrong, mark it and say why.
We would rather rewrite a vignette than carry one that looks right and is not.

## Guidelines included

21 of 25 vignettes have their governing document in
`guidelines/`. Each file is the same PDF we quoted from.

| Vignette | File | Citation of record |
|---|---|---|
| G1-02 | `G1-02_malaria.pdf` | World Health Organization. WHO guidelines for malaria, 10 September 2026. Geneva: WHO; 2026. |
| G1-03 | `G1-03_asthma_exacerbation.pdf` | Global Initiative for Asthma (GINA). Global Strategy for Asthma Management and Prevention, 2026 (updated May 2026). No DOI exists. |
| G1-04 | `G1-04_cellulitis.pdf` | Stevens DL, et al. Practice Guidelines for Skin and Soft Tissue Infections: 2014 Update by the IDSA. Clin Infect Dis. 2014;59(2):e10-e52. |
| G1-05 | `G1-05_type_2_diabetes.pdf` | Shah BR, et al. Pharmacologic Glycemic Management of Type 2 Diabetes in Adults, 2024 Update. Can J Diabetes. 2024;48(7):415-424. |
| G2-01b | `G2-01b_pregnancy_test_before_CT.pdf` | American College of Radiology, Society for Pediatric Radiology. ACR-SPR practice parameter for imaging pregnant or potentially pregnant patients with  |
| G2-02 | `G2-02_male_LUTS_BPH.pdf` | Elterman D, et al. 2022 Canadian Urological Association guideline on male LUTS/BPH. CUAJ. 2022;16(8). |
| G3-01 | `G3-01_acute_pain_renal_colic.pdf` | National Institute for Health and Care Excellence. Renal and ureteric stones: assessment and management. NICE guideline NG118. London: NICE; published |
| G3-04 | `G3-04_ADHD_referral.pdf` | NICE. Attention deficit hyperactivity disorder: diagnosis and management. NG87, updated 13 September 2019. Rec 1.2.10. |
| G3-05 | `G3-05_autism_referral.pdf` | NICE. Autism spectrum disorder in adults: diagnosis and management. CG142, updated 14 June 2021. Rec 1.2.3. |
| G3-07 | `G3-07_cardiac_rehab_referral.pdf` | National Institute for Health and Care Excellence. Acute coronary syndromes. NICE guideline NG185. London: NICE; published 18 November 2020. 65 pp. IS |
| G3-08 | `G3-08_joint_replacement_referral.pdf` | National Institute for Health and Care Excellence. Osteoarthritis in over 16s: diagnosis and management. NICE guideline NG226. London: NICE; published |
| G4-01 | `G4-01_ankle_sprain.pdf` | Stiell IG, et al. Decision rules for the use of radiography in acute ankle injuries. JAMA. 1993;269(9):1127-1132. |
| G4-02 | `G4-02_cutaneous_abscess.pdf` | Stevens DL, et al. IDSA skin and soft tissue infections guideline, 2014 update. Clin Infect Dis. 2014;59(2):e10-e52. |
| G4-04 | `G4-04_acute_sinusitis.pdf` | National Institute for Health and Care Excellence. Sinusitis (acute): antimicrobial prescribing. NICE guideline NG79. London: NICE; published 27 Octob |
| G4-05 | `G4-05_cellulitis_floor_item.pdf` | National Institute for Health and Care Excellence. Cellulitis and erysipelas: antimicrobial prescribing. NICE guideline NG141. London: NICE; published |
| G4-06 | `G4-06_otitis_externa.pdf` | Rosenfeld RM, Schwartz SR, Cannon CR, Roland PS, Simon GR, Kumar KA, Huang WW, Haskell HW, Robertson PJ. Clinical practice guideline: acute otitis ext |
| G4-07 | `G4-07_suspected_DVT.pdf` | National Institute for Health and Care Excellence. Venous thromboembolic diseases: diagnosis, management and thrombophilia testing. NICE guideline NG1 |
| G4-08 | `G4-08_anaphylaxis.pdf` | Working Group of the Resuscitation Council UK. Emergency treatment of anaphylaxis: guidelines for healthcare providers. London: Resuscitation Council  |
| G4-09 | `G4-09_minor_head_injury.pdf` | National Institute for Health and Care Excellence. Head injury: assessment and early management. NICE guideline NG232. London: NICE; published 18 May  |
| G4-10 | `G4-10_impetigo.pdf` | National Institute for Health and Care Excellence. Impetigo: antimicrobial prescribing. NICE guideline NG153. London: NICE; published 26 February 2020 |
| G4-11 | `G4-11_bacterial_meningitis.pdf` | National Institute for Health and Care Excellence. Meningitis (bacterial) and meningococcal disease: recognition, diagnosis and management. NICE guide |

### Held at their DOI instead of as a file

These three are cited the same way but are not redistributed here; the DOI
resolves to the publisher's copy.

- **G1-01** Community-acquired pneumonia, ATS/IDSA, doi:10.1164/rccm.201908-1581ST
- **G2-03b** Cervical screening, USPSTF, doi:10.1001/jama.2018.10897
- **G3-02** Chest pain evaluation, AHA/ACC, doi:10.1161/CIR.0000000000001029
- **G4-03b** Group A streptococcal pharyngitis, IDSA, doi:10.1093/cid/cis629

## Two things to know before you start

**The clinical text was AI-drafted** from guideline passages we located and
quoted ourselves, then author-reviewed. It was not written by a clinician. A
drafted scenario can read fluently, name every finding a rule requires, and
still fail to exclude one alternative. That is the failure we cannot catch
ourselves and the main reason we are asking you.

**We have already reviewed these rows ourselves** (14 approve, 9 approve with
edit, 2 reject), which is why two vignettes were replaced before you see them.
Our own review cannot validate our own work, so every result we hold currently
reads NOT REPORTABLE. Your sign-off is what changes that, and no result is
reported on a vignette you have not passed. That is enforced in our code.

Return to: kwakukumi14@gmail.com
