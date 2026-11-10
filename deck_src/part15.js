const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 36. WHAT IS LEFT TO DO ============================ //
let s = S("CONTENT", "Limitations and conclusions", "What is left to do");
K.mark("remaining");
s.addText("Ordered by the critical path. Item 1 blocks every reportable number in the project.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.3, fontSize: 13.5, color: INK, margin: 0, isTextBox: true });
const todo = [
  { n: 1, h: "Clinician review of all 25 live vignettes", b: "Outreach is sent and the response is outstanding. Nothing becomes reportable until this returns.", st: "Blocking", c: FAIL },
  { n: 2, h: "Write more Group 4 vignettes", b: "The highest-value build step. Fixes the two-cluster floor, the degenerate bootstrap and the H3 circularity at once, and depends on nothing unresolved.", st: "Ready to start", c: PASS },
  { n: 3, h: "Re-run the audit on verified items", b: "Same pipeline, corrected items, and a full before-and-after table. The only route to a reportable number.", st: "After item 1", c: WARN },
  { n: 4, h: "RQ6 independent coding", b: "Both authors code the 136 candidate passages against the written codebook, and inter-coder agreement is reported whatever it is.", st: "Ready to start", c: PASS },
  { n: 5, h: "More vignettes per hypothesis group", b: "The only way to improve the resolution limit. H1 currently rests on two clusters, which caps its finest p value at 0.25.", st: "Planned", c: TEAL },
  { n: 6, h: "Investigate elicitation further", b: "A chat template, a longer few-shot prefix and a generation-based readout are untested. D057 limits what we have shown, not what is possible.", st: "Optional", c: TEAL },
];
todo.forEach((t, i) => {
  const y = 1.58 + i * 0.85;
  card(s, { x: 0.55, y, w: 12.2, h: 0.74, name: "td" + i });
  badge(s, { x: 0.76, y: y + 0.16, n: t.n, d: 0.42, fs: 13, color: t.c, name: "tdb" + i });
  s.addText(t.h, { x: 1.36, y: y + 0.06, w: 3.9, h: 0.62, fontSize: 12.5, bold: true,
    color: INK, lineSpacing: 15, margin: 0, isTextBox: true, valign: "middle", objectName: "tdh" + i });
  s.addText(t.b, { x: 5.4, y: y + 0.06, w: 5.6, h: 0.62, fontSize: 10.5, color: MUT,
    lineSpacing: 12.5, margin: 0, isTextBox: true, valign: "middle", objectName: "tdbb" + i });
  s.addShape(pres.ShapeType.roundRect, { x: 11.2, y: y + 0.19, w: 1.35, h: 0.36, rectRadius: 0.05,
    fill: { color: PAPER }, line: { color: t.c, width: 1 }, objectName: "tds" + i });
  s.addText(t.st, { x: 11.2, y: y + 0.19, w: 1.35, h: 0.36, fontSize: 9.5, bold: true,
    color: t.c, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "tdst" + i });
});
card(s, { x: 0.55, y: 6.76, w: 12.2, h: 0.28, fill: TINT, name: "tdf" });
s.addText("Items 2 and 4 can proceed in parallel with the clinician review and are the best use of the waiting time.",
  { x: 0.77, y: 6.78, w: 11.76, h: 0.24, fontSize: 11, italic: true, color: INK, margin: 0, isTextBox: true });
note(s, "Items 2 and 4 are unblocked, so they are what to work on now. Item 2 in particular closes three separate limitations with one piece of authoring work.");

// ============ 37. REFERENCES ==================================== //
s = S("CONTENT", "Limitations and conclusions", "References");
// D092: one sorted list, numbered by position, split into columns by code.
// Numbers were hand-typed before, so inserting the four guideline sources from
// rounds 5-7 in alphabetical order would have meant renumbering 25 entries by
// hand -- exactly the kind of edit that silently goes wrong.
const REFS = [
  "ACR and SPR. 2023. ACR-SPR practice parameter for imaging pregnant or potentially pregnant patients with ionizing radiation. Revised 2023 (Resolution 31).",
  "Biderman, S. et al. 2022. Datasheet for the Pile. arXiv:2201.07311.",
  "Biderman, S. et al. 2023. Pythia: A suite for analyzing large language models across training and scaling. ICML 2023.",
  "Chang, C.T. et al. 2025. Evaluating anti-LGBTQIA+ medical bias in large language models. PLOS Digital Health 4, 9.",
  "Cirillo, D. et al. 2020. Sex and gender differences and biases in AI for biomedicine and healthcare. npj Digital Medicine 3, 81.",
  "Dev, S. et al. 2021. Harms of gender exclusivity and challenges in non-binary representation in language technologies. EMNLP 2021.",
  "Elterman, D. et al. 2022. CUA guideline: Male lower urinary tract symptoms and benign prostatic hyperplasia. CUAJ 16, 8.",
  "Gao, L. et al. 2021. The Pile: An 800GB dataset of diverse text for language modeling. arXiv:2101.00027.",
  "Gebru, T. et al. 2021. Datasheets for datasets. Communications of the ACM 64, 12, 86-92.",
  "Guerra-Adames, A. et al. 2026. Auditing sex and gender disparities in emergency triage with LLM-based paired comparisons. arXiv:2511.17124.",
  "Gulati, M. et al. 2021. AHA and ACC guideline for the evaluation and diagnosis of chest pain. Circulation 144, e368-e454.",
  "Heidari, S. et al. 2016. Sex and Gender Equity in Research: Rationale for the SAGER guidelines. Research Integrity and Peer Review 1, 2.",
  "Hoffmann, D.E. and Tarzian, A.J. 2001. The girl who cried pain: A bias against women in the treatment of pain. JLME 29, 1.",
  "Liu, J. et al. 2024. Infini-gram: Scaling unbounded n-gram language models to a trillion tokens. arXiv:2401.17377.",
  "Loge, C. et al. 2021. Q-Pain: A question answering dataset to measure social bias in pain management. NeurIPS D and B 2021.",
  "McClure, R.C. et al. 2022. Gender harmony: Improved standards to support affirmative care of gender-marginalized people. JAMIA 29, 2.",
  "NICE. 2018. Sore throat (acute): antimicrobial prescribing. NICE guideline NG84.",
  "NICE. 2019. Attention deficit hyperactivity disorder: diagnosis and management. NICE guideline NG87.",
  "NICE. 2020. Impetigo: antimicrobial prescribing. NICE guideline NG153.",
  "NICE. 2023. Ectopic pregnancy and miscarriage: diagnosis and initial management. NICE guideline NG126.",
  "OLMo Team. 2025. 2 OLMo 2 Furious. arXiv:2501.00656.",
  "Qwen Team. 2025. Qwen3 technical report. arXiv:2505.09388.",
  "Shulman, S.T. et al. 2012. Clinical practice guideline for the diagnosis and management of group A streptococcal pharyngitis: 2012 update by the IDSA. Clinical Infectious Diseases 55, 10, e86-e102.",
  "Soldaini, L. et al. 2024. Dolma: An open corpus of three trillion tokens for language model pretraining research. arXiv:2402.00159.",
  "Turpin, M. et al. 2023. Language models don't always say what they think: Unfaithful explanations in chain-of-thought prompting. NeurIPS 2023.",
  "Vig, J. et al. 2020. Investigating gender bias in language models using causal mediation analysis. NeurIPS 2020.",
  "Young, R.J. and Matthews, A.M. 2026. EQUITRIAGE: A fairness audit of gender bias in LLM-based emergency department triage. arXiv:2605.03998.",
  "Zack, T. et al. 2024. Assessing the potential of GPT-4 to perpetuate racial and gender biases in health care. Lancet Digital Health 6, 1.",
  "Zhao, J. et al. 2017. Men also like shopping: Reducing gender bias amplification using corpus-level constraints. EMNLP 2017.",
];
const numbered = REFS.map((t, i) => `[${i + 1}]  ${t}`);
const half = Math.ceil(numbered.length / 2);
[numbered.slice(0, half), numbered.slice(half)].forEach((col, ci) => {
  s.addText(col.map((t, i) => ({ text: t, options: { breakLine: i < col.length - 1 } })),
    { x: 0.55 + ci * 6.2, w: 5.95, y: 1.22, h: 5.32, fontSize: 8, color: INK,
      lineSpacing: 10.5, paraSpaceAfter: 2, margin: 0, isTextBox: true, valign: "top",
      objectName: "refcol" + ci });
});
note(s, "ACM reference style, matching the progress report. The four guideline sources added in rounds 5 to 7 are the ACR-SPR practice parameter, NICE NG84 and NG153, and the IDSA pharyngitis guideline -- all read at first hand, which is how three citation errors were caught.");

// ============ 38. CLOSING / HOW TO UPDATE ======================= //
s = S("TITLE_DARK", "Limitations and conclusions", "A living document");
s.addText("This deck is the running record of the project. Update it whenever something critical changes.",
  { placeholder: "body" });
const upd = [
  { h: "When a run completes", b: `Update the results section and the date on slide ${K.slideNo("scale")}.` },
  { h: "When a decision is logged", b: `The decision count on slide ${K.slideNo("scale")} and the log in the repository.` },
  { h: "When the clinician replies", b: `The status column on slide ${K.slideNo("remaining")} and the whole of that slide.` },
];
upd.forEach((u, i) => {
  const x = 0.9 + i * 3.9;
  s.addShape(pres.ShapeType.roundRect, { x, y: 4.95, w: 3.6, h: 1.1, rectRadius: 0.06,
    fill: { color: "1C4E59" }, line: { color: "1C4E59", width: 0 }, objectName: "up" + i });
  s.addText(u.h, { x: x + 0.22, y: 5.08, w: 3.16, h: 0.3, fontSize: 12, bold: true,
    color: "7FD4C8", margin: 0, isTextBox: true, objectName: "uph" + i });
  s.addText(u.b, { x: x + 0.22, y: 5.38, w: 3.16, h: 0.56, fontSize: 11, color: "BCD3D8",
    lineSpacing: 13.5, margin: 0, isTextBox: true, objectName: "upb" + i });
});
s.addText("Evans Kumi  and  Aymen Boustani   ·   McGill University   ·   ECSE-557 Ethics in Artificial Intelligence",
  { x: 0.9, y: 6.4, w: 11.5, h: 0.3, fontSize: 11, color: "8EB0B8", margin: 0, isTextBox: true });
note(s, "Three triggers for updating this deck. The most common one will be a completed run, which touches the results section and the date on the title slide.");

module.exports = {};
