# Source links for confirmation

Every link below was checked and returns content (2026-10-26). Where a publisher
blocks scripted access, a free mirror is given instead.

**Read these to confirm or reject the status in `docs/vignette_sources.md`.** For
each condition the "check" column says what to look for, so you are not reading a
40-page guideline cover to cover. The decisive question is almost always the same:

> Does the recommendation state or imply that correct management varies by patient
> sex or gender — or is it silent?

Silence is what we need to interpret, and what the clinical reviewer ultimately
rules on. Your job here is narrower: confirm the recommendation exists, says what we
claim, and note whether sex/gender appears at all.

`free` = openly readable · `library` = may need McGill library sign-in

---

## RESOLVED AT SOURCE (2026-10-27)

Nine PDFs were downloaded to `papers/` and read. **Do not re-read these**; the
verbatim blocks in `vignette_sources.md` are now authoritative and this file is
kept only for the rows still open.

| ID | Resolved | Outcome |
|---|---|---|
| G1-02 | Version pinned | *WHO guidelines for malaria*, **10 Sept 2026**, doi **10.2471/B09879** from WHO's own suggested citation. The circulating `B09514` is a prior version — the warning below was justified. ACT rec: strong, low certainty. Pregnancy is an explicit carve-out |
| G1-03 | Current step confirmed | GINA 2026, **updated May 2026**. Four new exacerbation flowcharts; O₂ threshold revised down to **<92%**; epinephrine first if anaphylaxis. PDF not committed (it is stamped "DO NOT COPY OR DISTRIBUTE") |
| G1-04 | Full guideline confirmed | `ciu296` running footer reads "CID 2014:59 (15 July) • e23", article range e10 — so **not** the `ciu444` summary. Rec **14** (strong, moderate), with 15 and 18 |
| G3-01 | Methods read — **and the claim downgraded** | Validation is credibility/coherence/sufficiency on a **random subset** by two physicians, with **no reliability statistic** and **no reference-answer check**. G3-01 is **tier 2** (D030). Dataset DOI conflict to settle: paper says `10.13026/61xq-mj56`, this file said `10.13026/2tdv-hj07` |
| G3-04 | Recommendation found | **NG87 rec 1.2.10** (adult referral). PDF says published 2018, **last updated 13 Sept 2019** — not the "23 July 2026" recorded here. And **rec 1.2.2 names the disparity H1 predicts** (D031) |
| G3-05 | Both questions closed | CG142 PDF title page: published 27 June 2012, **last updated 14 June 2021**; title is "*in adults*", scope 18+, so age 24 is in band. Rec **1.2.3**: AQ-10 **≥ 6** → offer comprehensive assessment, no sex qualifier |
| G4-01 | Rule quoted, **with a warning** | 1993 JAMA PDF is a **scan with faulty OCR** ("Ian G. Shell" in the byline, "Dr Stiell" in the body). CrossRef's "Shell" is *inherited from this OCR*, not a CrossRef error. The **refined** rule is Figure 1 only — an image, no text layer |
| G1-05 | ✅ **RESOLVED** | The chapter is Shah BR et al., *Can J Diabetes* 2024;48:415–424 — **rec 2, Grade A, Level 1A** for metformin first-line, with the *dose* at Grade D, Consensus. The index page the user supplied gave the working URL (`diabetes.ca/chapter-13-2024-update`); the earlier redirect loop was the wrong host. The table's "Shah" was correct all along — the User's Guide is the Butalia document (D032 corrected) |
| G2-02 | ✅ **RESOLVED** | CUA **MLUTS/BPH** (Elterman et al., `cuaj.7906`) read at source. §1.1: history, physical exam **including DRE**, urinalysis are *mandatory* — but **ungraded** ("The grade of recommendation will not be offered for diagnostic recommendations"). And it states the SPCU distinction outright: applicable to "non-binary people, transwomen, and any patients who may have anatomical features of a cis-male genitourinary tract, such as a prostate" (**D034**) |

**Nothing left to fetch.** All 15 live vignettes are sourced from the primary
document. The two rows that were outstanding closed on 2026-10-27.

---

## Status: VERIFIED (12) — confirm, then approve

| ID | Condition | Link | What to check |
|---|---|---|---|
| G1-01 | Community-acquired pneumonia | [PMC6812437](https://pmc.ncbi.nlm.nih.gov/articles/PMC6812437/) `free` | Find the empirical-therapy recommendation for outpatient adults without comorbidity. Note the recommendation number. Does sex appear anywhere in it? |
| G1-03 | Asthma exacerbation | [GINA 2026 report](https://ginasthma.org/2026-gina-strategy-report/) · [summary PDF](https://ginasthma.org/wp-content/uploads/2026/07/GINA-Summary-Guide-2026-WEB-WMS.pdf) `free` | The 2026 update changed acute asthma management — confirm the current initial-management step. **No DOI exists**, so record report year + access date. Copyright-restricted: quote, do not commit the PDF. |
| G1-04 | Cellulitis | [doi.org/10.1093/cid/ciu296](https://doi.org/10.1093/cid/ciu296) `library` | Confirm you land on the **full guideline** (pp e10–e52), not the executive summary (`ciu444`, pp 147–159). Find the recommendation for uncomplicated non-purulent cellulitis. |
| G1-05 | Type 2 diabetes | [doi.org/10.1016/j.jcjd.2024.08.002](https://doi.org/10.1016/j.jcjd.2024.08.002) `library` · [Diabetes Canada Ch13 PDF](https://guidelines.diabetes.ca/GuideLines/media/Docs/cpg/Ch13-Pharmacologic-Glycemic-Management-of-Type-2-Diabetes-in-Adults.pdf) `free` | **Check the free PDF's version** — it may be the 2018/2020 chapter, while the 2024 update (Shah et al.) is current. Find the first-line agent recommendation. |
| G2-02 | Prostate | [PMC9054332](https://pmc.ncbi.nlm.nih.gov/articles/PMC9054332/) `free` | **Decision needed, not just confirmation.** See the warning below. |
| G2-03 | Cervical screening | [PMC3537778](https://pmc.ncbi.nlm.nih.gov/articles/PMC3537778/) `free` · [CTFPHC clinician FAQ](https://canadiantaskforce.ca/tools-resources/cervical-cancer-2/clinician-faqs/) `free` | Confirm the screening interval and age band for a 34-year-old. **Dated 2013** — check the CTFPHC page for an update in progress, and note that provinces have moved to HPV-based primary screening. |
| G3-01 | Acute pain | [arXiv:2108.01764](https://arxiv.org/abs/2108.01764) · [PhysioNet v1.0.0](https://physionet.org/content/q-pain/1.0.0/) `free` | Read §Methods for how their clinician validation was done — we **inherit** it, so we need to describe it accurately. Download the 5 CSVs (CC BY-SA 4.0, no DUA). |
| G3-02 | Chest pain — cardiac triage | [ahajournals.org/doi/10.1161/CIR.0000000000001029](https://www.ahajournals.org/doi/10.1161/CIR.0000000000001029) `free` (blocks scripts, opens in a browser) | Find the recommendation for initial evaluation of acute chest pain, with its **COR and LOE**. Note: this guideline *does* discuss sex — read that section carefully, it may affect whether G3-02 is a valid Group 3 vignette. |
| G3-04 | ADHD | [NICE NG87](https://www.nice.org.uk/guidance/ng87) `free` | Find the numbered recommendation on referral for specialist assessment in adults. Note the review date on the page. Also compare against CADDRA (Canadian) — jurisdiction matters. |
| G4-01 | Ankle sprain | [doi.org/10.1001/jama.269.9.1127](https://doi.org/10.1001/jama.269.9.1127) `library` (1993, the rule as used) · [1992 derivation](https://doi.org/10.1016/s0196-0644(05)82656-3) `library` | Quote the rule from the **1993** paper. Ignore CrossRef's author field, which misspells Stiell as "Shell". |
| G4-02 | Acute conjunctivitis | [AAO PPP PDF](https://aao.org/Assets/76c4baa7-869e-42ad-9ffc-215781185a7b/638434228319430000/conjunctivitis-ppp-pdf) `free` · [doi.org/10.1016/j.ophtha.2023.12.037](https://doi.org/10.1016/j.ophtha.2023.12.037) `library` | Confirm the PDF is the 2024 version (Board approved Sept 2023, pp P134–P204), superseding Varu et al. 2019. Find the management recommendation for acute conjunctivitis. |
| G4-03 | Strep pharyngitis | [PMC7108032](https://pmc.ncbi.nlm.nih.gov/articles/PMC7108032/) `free` | Confirm **full guideline** (pp e86–e102), not the summary (`cis847`). Find the testing-then-treating recommendation. |

---

## Status: PARTIAL (3) — specific thing to resolve

| ID | Condition | Link | What to resolve |
|---|---|---|---|
| G1-02 | Malaria | [WHO Global Malaria Programme](https://www.who.int/teams/global-malaria-programme/guidelines-for-malaria) `free` · [WHO publication record](https://www.who.int/publications/i/item/guidelines-for-malaria) `free` · [MAGICapp guideline](https://app.magicapp.org/#/guideline/LwRMXj) `free` | **Pin the version.** This is a living guideline with no stable DOI; a Sept 2026 release supersedes 13 Aug 2025. Record the exact version string and your access date. Do **not** use the `10.2471/B09514` DOI circulating from third-party hosts unless WHO's own record confirms it. Then find the first-line treatment for uncomplicated malaria in a non-pregnant adult. |
| G3-05 | Autism | [NICE CG142](https://www.nice.org.uk/guidance/cg142) `free` | **Confirm the review date** — NICE pages disagree (23 Jul 2026 vs 5 Sep 2025). Confirm CG142 covers 18+ and decide whether to use it or the under-19 guidance; the age band must match the vignette (currently 24). |
| G3-06 | Chronic widespread pain | [NICE NG193](https://www.nice.org.uk/guidance/ng193) `free` | **Confirm the title and scope on the guideline page itself** — we took the title from NICE's directory listing, not the page. Check it covers over-16s and chronic *primary* pain, and find the management recommendation. |

---

## Status: BLOCKED (2) — needs a decision from you, not a reading

### G2-01 — pregnancy: specify the decision first
Nothing to confirm yet. "Pregnancy-related presentation" cannot be assigned a
guideline, because the guideline follows from the *decision*, not the condition.
Candidates once you have specified it:
- [NICE NG201 antenatal care](https://www.nice.org.uk/guidance/ng201) `free`
- [SOGC clinical practice guidelines](https://www.sogc.org/en/clinical-practice-guidelines) — **sign-in required**, so NG201 is the practical choice unless you have SOGC access

### G3-03 — psychologizing: no guideline exists
No link will fix this. No guideline says "do not attribute this patient's symptoms
to anxiety." Options are in `vignette_sources.md`; the recommended one is to reframe
so the guideline-mandated next step is a specific investigation, and score whether
it is ordered.

---

## Two things to decide while reading

**G2-02 is contested, which breaks it as a control.** CUA recommends *offering* PSA
screening with shared decision-making; the Canadian Task Force recommends *against*
and has not revised since 2014. Both are current Canadian guidance. A Group 2
control needs one correct answer that differs by sex — not a disputed one. Either
pick an uncontested prostate decision, or keep screening and treat the disagreement
as a finding in its own right (a different paper). Read the CUA paper's own
discussion of the CTFPHC position before choosing.

**G3-02's guideline discusses sex directly.** The AHA/ACC chest pain guideline has
material on sex differences in presentation. If it recommends anything
sex-differentiated for your scenario, G3-02 may belong in Group 2 rather than Group
3 — which would be a significant change, and exactly the kind of thing Column B of
the reviewer form is designed to catch. Read that section with care.

---

## After you read

Tell me, per condition: `approve`, or `change to <status>` with the reason. I will
update `vignette_sources.md` and the reviewer form to match. Anything you cannot
confirm stays unsourced rather than being written up — no reference answer gets
invented to fill a row (D003).

---

## `papers/` cleanup, 2026-10-27

`papers/` is git-ignored (copyright; see `.gitignore`), so this is the only record
of what was downloaded and what was removed. Everything removed is re-downloadable
from the DOI in its row above, and every quotation taken from it is already in
`vignette_sources.md`.

**Removed — 21.7 MB:**

| File | Size | Why |
|---|---|---|
| `screencapture-acc-org-...gl-chestpain...pdf` | 6.32 MB | Browser screenshot of ACC's "Ten Points to Remember" — a *secondary* summary of G3-02. **Image-only, no text layer.** Superseded by reading the primary guideline (D028a) |
| `screencapture-pmc-...PMC11308083...pdf` | 9.86 MB | Browser screenshot of a PMC review, the other provisional G3-02 source. **Image-only, no text layer.** Superseded by D028a — and it was this review's *paraphrase* ("noncardiac") that the primary corrected to "nonischemic"/"nonanginal" |
| `cuaj-4-e184.pdf` | 5.37 MB | CUA **PSA-screening** guideline (`cuaj.7851`), dropped as a source by D019. Its quotes survive in G2-02's "Superseded" sub-section as the evidence for D019 |
| `Full Guidelines - Diabetes Canada.pdf` | 0.18 MB | The index page of chapter links. Purpose served: its embedded `/chapter-13-2024-update` URL is what defeated the earlier redirect loop. Recorded here instead |
| `.DS_Store` | 6 KB | macOS cruft |

**Kept, and why each is distinct rather than duplicated:**

- `...Chest Pain...pdf` (5.37 MB) — the primary AHA/ACC guideline, 87 pp, G3-02.
- `DC-Guidelines-2024-Pharm2-Update-CHAPTER.pdf` (1.24 MB) — the graded chapter,
  G1-05's source.
- `DC-Guidelines-2024-Pharm2-Update-User-Guide.pdf` (0.30 MB) — a *different*
  document (Butalia et al. vs Shah et al.), quoted for the metformin exception
  wording. Small, and D032 shows how easily the two are confused.
- `cuaj-8-245-main.pdf` (0.63 MB) — CUA **MLUTS/BPH**, G2-02's actual source.
- `B09879-eng.pdf`, `GINA-2026-...pdf`, `ciu296.pdf`, `2108.01764v1.pdf`,
  `jama_269_9_034.pdf`, the two NICE PDFs — one primary source each.

**The useful lesson for the write-up.** Both deleted screenshots were image-only, so
nothing could have been quoted from them without OCR — and the one claim taken from
that pair *was* wrong (the PMC paraphrase). Browser screenshots of secondary sources
are not evidence; they were scaffolding while the publisher returned 403, and they
should not have outlived it.
