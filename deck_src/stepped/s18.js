// BACKUP 1: the preregistered hypothesis table in full.
//
// Not spoken. It exists so that "what exactly did H1 say, and what came back?"
// is answered by turning to a slide instead of from memory. Every column is
// read from rq2_hypothesis_tests.csv.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const H = ["H1", "H2", "H3"].map(h => ({ id: h, ...F.hypothesis(h) }));
const CLAIM = {
  H1: ["Neurodevelopmental referral", "Referral endorsed less readily for the woman arm."],
  H2: ["Cardiac triage urgency", "Less mass on the more urgent triage option."],
  H3: ["Discriminant null", "No gap where the corpus is unskewed. TOST."],
};

pres.addSection({ title: "5 Backup" });
const s = S("CONTENT", "5 Backup", "Backup: the preregistered tests, in full");
K.mark("bk-hyp");

s.addText("Holm-Bonferroni across H1 to H4 at family-wise alpha = .05. RQ3 and the merging result are exploratory and sit outside this family.", {
  x: 0.55, y: 1.12, w: 12.2, h: 0.26, fontSize: 11, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

const COLS = [
  ["", 0.55, 1.95], ["k", 2.56, 0.42], ["mean Δ", 3.04, 1.02],
  ["95% CI", 4.12, 1.72], ["exact p", 5.90, 0.86], ["limit 2⁻ᵏ", 6.82, 0.86],
  ["Holm p", 7.74, 0.86], ["verdict", 8.66, 4.12],
];
COLS.forEach(([t, x, w]) => s.addText(t, { x, y: 1.5, w, h: 0.22, fontSize: 8.5,
  bold: true, color: MUT, charSpacing: 0.6, isTextBox: true, margin: 0,
  objectName: "h-" + t }));

const VERDICT = {
  H1: [`Unresolvable, not absent. p equals the resolution limit exactly, and the interval excludes zero. One more referral vignette takes k to 5 and the limit to 0.031.`, WARN],
  H2: [`Single vignette, so the exact test can only return 0.5 or 1.0. The claim is about this scenario only and does not generalise.`, MUT],
  H3: [`Equivalence SUPPORTED at margin ${F.hypothesis("H3").txt.margin}, with k = 8 where a rejection was available. The discriminant null holds.`, PASS],
};

H.forEach((h, i) => {
  const y = 1.78 + i * 1.3;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.55, y, w: 12.23, h: 1.18, rectRadius: 0.05,
    fill: { color: i % 2 ? PAPER : TINT }, line: { color: "E1EBED", width: 0.75 },
    objectName: `row${i}` });
  s.addText([
    { text: `${h.id}  `, options: { bold: true, color: INK, fontSize: 12 } },
    { text: CLAIM[h.id][0], options: { bold: true, color: TEAL, fontSize: 9.5 } },
    { text: "\n" + CLAIM[h.id][1], options: { color: MUT, fontSize: 8.5 } },
  ], { x: 0.72, y: y + 0.08, w: 1.9, h: 1.02, lineSpacing: 11, valign: "top",
       isTextBox: true, margin: 0, objectName: `c0-${i}` });

  const cell = (x, w, t, col, bold) => s.addText(t, { x, y: y + 0.08, w, h: 1.02,
    fontSize: 10, bold: !!bold, color: col || INK, align: "center",
    valign: "middle", isTextBox: true, margin: 0, fontFace: "Courier New",
    objectName: `cx-${i}-${x}` });

  cell(2.56, 0.42, String(h.k), INK, true);
  cell(3.04, 1.02, h.txt.delta, INK, true);
  cell(4.12, 1.72, isNaN(h.ciLo) ? "—" : h.txt.ci, MUT);
  cell(5.90, 0.86, h.txt.pExact, INK, true);
  cell(6.82, 0.86, h.pResolution.toFixed(4), MUT);
  cell(7.74, 0.86, h.txt.pHolm, MUT);

  s.addText(VERDICT[h.id][0], { x: 8.66, y: y + 0.08, w: 4.0, h: 1.02,
    fontSize: 9.5, color: VERDICT[h.id][1], lineSpacing: 11.5, valign: "middle",
    isTextBox: true, margin: 0, objectName: `v-${i}` });
});

s.addText([
  { text: "Why the exact column and not the Holm column is the honest one.  ", options: { bold: true, color: INK } },
  { text: "An exact sign-flip test over k vignette clusters cannot return a p below 2⁻ᵏ. Three of our tests sit at or near their own limit, so a non-rejection here is a statement about resolution, not about effect size. That is a property of the design, fixed before the run, and not a result.",
    options: { color: MUT } },
], { x: 0.55, y: 5.76, w: 12.23, h: 0.62, fontSize: 10.5, lineSpacing: 13.5,
     isTextBox: true, margin: 0, objectName: "foot" });

note(s, "Backup. Turn here if asked what H1 actually predicted, or why a p of 0.0625 is not a null result.");
