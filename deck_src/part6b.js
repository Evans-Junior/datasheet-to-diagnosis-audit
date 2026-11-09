// Methodology visuals: the SPCU x identity grid, the end-to-end process, and
// the vignette ledger. Added 2026-11-09 because the design was being explained
// in prose on slides that should have been showing it.
const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ M-A. THE SPCU x IDENTITY GRID ===================== //
let s = S("CONTENT", "Methodology", "The arm grid: what is held fixed and what varies");
s.addText([
  { text: "One vignette becomes 24 arms. ", options: { bold: true, color: INK } },
  { text: "The clinical text is byte-identical down every column — same findings, same observations, same negations. Only the patient descriptor changes. So any movement in the answer is attributable to the descriptor and nothing else.", options: { color: MUT } },
], { x: 0.55, y: 1.14, w: 12.2, h: 0.42, fontSize: 12.5, lineSpacing: 15, margin: 0, isTextBox: true });

// --- the 2 x 4 grid -------------------------------------------------------
const IDS = ["man", "woman", "non-binary", "blinded"];
const SPCUS = [
  { k: "SPCU = female", c: BERRY },
  { k: "SPCU = male", c: TEAL },
];
const gx = 2.15, gy = 1.84, cw = 2.1, ch = 0.62, gap = 0.1;

// column headers = gender identity
IDS.forEach((id, j) => {
  box(s, { x: gx + j * (cw + gap), y: gy, w: cw, h: 0.42,
    t: id, fill: INK, line: INK, tc: PAPER, fs: 11.5, name: "gh" + j });
});
// row headers = sex parameter for clinical use
SPCUS.forEach((sp, i) => {
  box(s, { x: 0.55, y: gy + 0.52 + i * (ch + gap), w: 1.5, h: ch,
    t: sp.k, fill: PAPER, line: sp.c, tc: sp.c, fs: 10.5, name: "sh" + i });
  IDS.forEach((id, j) => {
    const congruent = (i === 0 && id === "woman") || (i === 1 && id === "man");
    const blinded = id === "blinded";
    box(s, { x: gx + j * (cw + gap), y: gy + 0.52 + i * (ch + gap), w: cw, h: ch,
      t: "3 paraphrases",
      fill: blinded ? "F2F6F7" : (congruent ? "EEF4F4" : PAPER),
      line: blinded ? "C3D4D8" : sp.c, lw: congruent ? 1.6 : 1.0,
      tc: MUT, fs: 10, bold: false, name: `c${i}${j}` });
  });
});
s.addText("2 sex parameters  ×  4 gender identities  ×  3 paraphrases  =  24 arms per vignette",
  { x: 0.55, y: gy + 2.0, w: 12.2, h: 0.3, fontSize: 13, bold: true, color: INK,
    align: "center", margin: 0, isTextBox: true });

// --- why the grid is shaped this way -------------------------------------
const why = [
  { h: "Why the sex parameter is separate",
    b: "HL7's Gender Harmony Model splits the single legacy “sex” field into gender identity, recorded sex, and the Sex Parameter for Clinical Use — the value a clinical rule should read. Our invariance rule follows it: when SPCU is fixed, the guideline-indicated action must not move with identity.",
    c: TEAL, src: "McClure et al., JAMIA 2021" },
  { h: "Why a blinded arm exists",
    b: "It is the reference point, not a fourth identity. If a model's answer under “blinded” differs from its answer under “man” on identical findings, the descriptor is doing work the findings do not license. EQUITRIAGE found blinding cut one model's flip rate from 1.34:1 to 0.5%.",
    c: WARN, src: "Young & Matthews, arXiv:2605.03998" },
  { h: "Why a non-binary arm exists",
    b: "Not for coverage. RQ5 found non-binary patients are near-absent from the clinical subject position in both corpora, so the arm measures what a model does with a descriptor it has effectively never seen in this role — which is the situation a real patient is in.",
    c: BERRY, src: "Dev et al., EMNLP 2021" },
];
why.forEach((c, i) => {
  const x = 0.55 + i * 4.1;
  card(s, { x, y: 4.3, w: 3.85, h: 2.1, kicker: c.src.toUpperCase(), kickerColor: c.c,
    head: c.h, headSize: 12.5, headH: 0.5, body: c.b, bodySize: 9.5, name: "wy" + i });
});
note(s, "Walk the grid with a finger: fix the row, move along it, and the only thing that changed is the word for the patient. That is the whole design in one gesture. The congruent cells are shaded only to show that congruence is not what is being tested — every cell is scored.");

// ============ M-B. THE PROCESS, END TO END ====================== //
s = S("CONTENT", "Methodology", "From a guideline sentence to a tiered result");
s.addText("Nine stages, one script. Every stage writes an artefact the next one reads, and four of them can refuse to continue.",
  { x: 0.55, y: 1.14, w: 12.2, h: 0.3, fontSize: 12.5, color: MUT, margin: 0, isTextBox: true });

// Row 1: build
const r1 = [
  { t: "Guideline\nquoted at\nfirst hand", c: BERRY },
  { t: "Vignette\ntemplate\n+ options", c: BERRY },
  { t: "Author review\nvs the quote", c: WARN },
  { t: "Expand\n24 arms", c: TEAL },
  { t: "624\nprompts", c: TEAL },
];
r1.forEach((b, i) => {
  const x = 0.55 + i * 2.52;
  box(s, { x, y: 1.6, w: 2.1, h: 0.92, t: b.t, fill: PAPER, line: b.c, tc: INK,
    fs: 10.5, name: "p1" + i });
  if (i < r1.length - 1) arrow(s, { x: x + 2.14, y: 1.98, w: 0.34, h: 0.16, color: b.c, name: "a1" + i });
});
// Row 2: measure
const r2 = [
  { t: "Score\n10 models", c: TEAL },
  { t: "Score\nplacebos", c: TEAL },
  { t: "Rebuild\nnoise floor", c: TEAL },
  { t: "Hypotheses\n+ floor gate", c: TEAL },
  { t: "Tier gate\n→ report", c: PASS },
];
r2.forEach((b, i) => {
  const x = 0.55 + i * 2.52;
  box(s, { x, y: 3.08, w: 2.1, h: 0.92, t: b.t, fill: PAPER, line: b.c, tc: INK,
    fs: 10.5, name: "p2" + i });
  if (i < r2.length - 1) arrow(s, { x: x + 2.14, y: 3.46, w: 0.34, h: 0.16, color: b.c, name: "a2" + i });
});
// the wrap arrow
arrow(s, { x: 11.2, y: 2.66, w: 0.34, h: 0.16, color: TEAL, rotate: 90, name: "awrap" });

// the four refusals
card(s, { x: 0.55, y: 4.22, w: 12.2, h: 2.18, fill: INK,
  kicker: "FOUR STAGES CAN REFUSE TO CONTINUE — EACH ONE WAS ADDED AFTER IT FAILED SILENTLY ONCE",
  kickerColor: "7FD4C8", name: "ref" });
const refs = [
  { n: "1", h: "Template gate", b: "Blocks an unsourced answer, an unmatched option set, or a pregnancy clause in an impossible arm. Checks all three scoring tokenizers, not one." },
  { n: "2", h: "Drift gate", b: "Refuses if the prompt CSV is behind templates.yaml on any field that changes what is scored — including which rows are live." },
  { n: "3", h: "Floor guard", b: "Refuses if the noise floor was built from a vignette no longer in the study. It once was, for five days, from a rejected row." },
  { n: "4", h: "Provenance audit", b: "Refuses if any table carries a prompt-set hash that is not the current one, or if the current set has never been scored." },
];
refs.forEach((r, i) => {
  const x = 0.77 + i * 2.99;
  badge(s, { x, y: 4.78, n: r.n, d: 0.34, fs: 11, color: "7FD4C8", name: "rb" + i });
  s.addText(r.h, { x: x + 0.42, y: 4.78, w: 2.4, h: 0.3, fontSize: 11.5, bold: true,
    color: PAPER, margin: 0, isTextBox: true });
  s.addText(r.b, { x, y: 5.16, w: 2.82, h: 1.1, fontSize: 9.5, color: "D6E6E9",
    lineSpacing: 12, margin: 0, isTextBox: true });
});
note(s, "The point of this slide is that the refusals are not hygiene, they are findings. Each one exists because the thing it now blocks happened: the floor really was built from a rejected vignette, the hash really was blind to an option rewrite, and a table really was eleven days stale while being read as current.");

// ============ M-C. THE VIGNETTE LEDGER ========================== //
s = S("CONTENT", "Methodology", "The 25 live vignettes, and why two are not");
const LEDGER = [
  ["1", "Sex-neutral conditions", "5", "G1-01 … G1-05", "Carries H3: no gap should appear here", TEAL],
  ["2", "Sex-specific, SPCU-dependent", "3", "G2-01b, G2-02, G2-03b", "Positive control: the gate. A model that cannot move here cannot be read anywhere", WARN],
  ["3", "Historically biased conditions", "6", "G3-01, -02, -04, -05, -07, -08", "Carries H1 and H2", BERRY],
  ["4", "Noise baseline", "11", "G4-01 … G4-11", "Builds the nuisance floor every delta is judged against", MUT],
];
const lRows = [[
  { text: "Group", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
  { text: "What it is", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
  { text: "n", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5, align: "center" } },
  { text: "Items", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
  { text: "Job in the design", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
]].concat(LEDGER.map((r, i) => [
  { text: r[0], options: { bold: true, color: r[5], fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { color: INK, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { color: INK, fontSize: 10.5, align: "center", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[3], options: { color: MUT, fontSize: 9.5, fontFace: "Courier New", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[4], options: { color: MUT, fontSize: 9.5, fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(lRows, { x: 0.55, y: 1.2, w: 12.2, colW: [0.8, 2.9, 0.5, 2.9, 5.1], rowH: 0.42,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.04, 0.1, 0.04, 0.1], fontFace: "Calibri", autoPage: false });

const out = [
  { k: "REJECTED ON CLINICAL REVIEW", c: FAIL, h: "G2-03  ·  G4-03",
    b: "G2-03's history presupposed anatomy, so the SPCU-male arm was incoherent rather than merely wrong. G4-03 had two defensible answers: FeverPAIN scored 4 of 5, where NICE permits an immediate antibiotic, so a floor item carried a real alternative. Both replaced by G2-03b and G4-03b, built to the same construct." },
  { k: "RETIRED AS SUPERSEDED", c: WARN, h: "G2-01",
    b: "Not a clinical rejection — it passed review. Withdrawn because G2-01b tests the same construct from a better source, and keeping both let the cluster bootstrap count one construct twice. Group 2 now runs at k = 3, which costs resolution (2⁻³ = 0.125) and buys a correct independence claim." },
  { k: "WHAT THE REVIEW CAUGHT THAT CODE DID NOT", c: BERRY, h: "2 rejected, 1 corrected, 3 citation errors",
    b: "G4-03b had reproduced the exact defect that got G4-03 rejected, because its negation list was inherited while its findings changed. No validator can catch that: it needs knowing which competing diagnoses the new findings leave open. This is the evidence that author review is a real tier." },
];
out.forEach((c, i) => {
  const x = 0.55 + i * 4.1;
  card(s, { x, y: 3.34, w: 3.85, h: 2.1, kicker: c.k, kickerColor: c.c,
    head: c.h, headSize: 12, headH: 0.32, body: c.b, bodySize: 9, name: "ou" + i });
});
tierBanner(s, { x: 0.55, y: 5.62, w: 12.2, h: 0.78, fs: 9.5, name: "ldt" });
note(s, "If asked why Group 4 is so large: the floor is stratified by option count, and a floor built from one or two items is a point estimate standing in for a distribution. Eleven items is what makes the binary and four-option strata separately estimable.");

module.exports = {};
