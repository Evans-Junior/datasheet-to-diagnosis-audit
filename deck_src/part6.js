const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 14. THE CROSSING, the key diagram ================== //
let s = S("CONTENT", "Methodology", "Crossing the sex parameter with identity");
s.addText("Two sex-parameter values times three gender identities gives six configurations. The model is never told a patient is transgender. The configuration simply exists in the prompt grid.",
  { x: 0.55, y: 1.22, w: 12.2, h: 0.56, fontSize: 14, color: INK, margin: 0, isTextBox: true });

// column headers (identity)
const ids = ["Identity:  woman", "Identity:  man", "Identity:  non-binary"];
ids.forEach((t, i) => {
  s.addText(t, { x: 3.2 + i * 3.2, y: 1.72, w: 3.0, h: 0.3, fontSize: 12, bold: true,
    color: TEAL, align: "center", margin: 0, isTextBox: true, objectName: "idh" + i });
});
// row headers (spcu)
["Sex parameter:\nfemale", "Sex parameter:\nmale"].forEach((t, r) => {
  s.addText(t, { x: 0.55, y: 2.12 + r * 1.52, w: 2.5, h: 1.3, fontSize: 12, bold: true,
    color: WARN, align: "right", valign: "middle", lineSpacing: 15, margin: 0,
    isTextBox: true, objectName: "sph" + r });
});
// the six cells
const cells = [
  [{ t: "cisgender woman", c: "9BB3BA", hl: false }, { t: "transgender man", c: BERRY, hl: true }, { t: "non-binary,\nfemale parameter", c: TEAL, hl: false }],
  [{ t: "transgender woman", c: BERRY, hl: true }, { t: "cisgender man", c: "9BB3BA", hl: false }, { t: "non-binary,\nmale parameter", c: TEAL, hl: false }],
];
cells.forEach((row, r) => row.forEach((cl, i) => {
  const x = 3.2 + i * 3.2, y = 2.12 + r * 1.52;
  s.addShape(pres.ShapeType.roundRect, { x, y, w: 3.0, h: 1.3, rectRadius: 0.07,
    fill: { color: cl.hl ? "F6EAEE" : PAPER }, line: { color: cl.c, width: cl.hl ? 2 : 1 },
    objectName: "cl" + r + i });
  s.addText(cl.t, { x: x + 0.08, y, w: 2.84, h: 1.3, fontSize: cl.hl ? 14 : 12.5,
    bold: cl.hl, color: cl.hl ? BERRY : INK, align: "center", valign: "middle",
    lineSpacing: cl.hl ? 18 : 15, margin: 0, isTextBox: true, objectName: "clt" + r + i });
}));
card(s, { x: 0.55, y: 5.26, w: 12.2, h: 1.16, fill: INK, name: "crw" });
s.addText([
  { text: "The two highlighted cells are where identity and the sex parameter disagree, which is the situation of a transgender patient. ", options: { bold: true, color: PAPER } },
  { text: "A trans man receives less probability on an indicated pregnancy test. A trans woman receives more probability on a cervical screening not indicated for her. This is the configuration our main exploratory finding sits in.", options: { color: "BCD3D8" } },
], { x: 0.77, y: 5.44, w: 11.76, h: 0.84, fontSize: 13, lineSpacing: 17, margin: 0, isTextBox: true });
note(s, "This is the single most important methodology slide. Walk the grid slowly. The point to land is that the transgender configurations are produced by the design rather than written into any prompt, so the model cannot be responding to the word transgender.");

// ============ 15. THE INVARIANCE RULE =========================== //
s = S("CONTENT", "Methodology", "The invariance rule, and how we grade it");
card(s, { x: 0.55, y: 1.22, w: 12.2, h: 0.96, fill: INK, name: "inv" });
s.addText([
  { text: "A gender difference counts as bias only where the correct answer is the same for every patient. ", options: { bold: true, color: PAPER } },
  { text: "Guidelines state management but are usually silent on gender, and reading silence as invariance is a judgement. So we grade it per item rather than assume it.", options: { color: "BCD3D8" } },
], { x: 0.77, y: 1.38, w: 11.76, h: 0.74, fontSize: 13, lineSpacing: 16, margin: 0, isTextBox: true });

const grades = [
  { g: "Strongest", d: "The guideline names the disparity we predict, in our own outcome variable. NICE NG87 [16] does this for ADHD referral.", n: "1 item", c: PASS },
  { g: "Strong", d: "The guideline states invariance within its scope. NICE NG126 [17] does this for the pregnancy item and explicitly covers trans men and non-binary people.", n: "several", c: TEAL },
  { g: "Moderate", d: "The guideline stratifies by sex elsewhere in the same document but not for our condition. The authors demonstrably had sex in mind and chose not to stratify, which makes the silence a considered omission.", n: "several", c: WARN },
  { g: "Weakest", d: "Silence alone, in a document that never stratifies by sex anywhere. These are labelled as such and are the ones to challenge first.", n: "2 items", c: FAIL },
];
grades.forEach((g, i) => {
  const y = 2.26 + i * 1.04;
  card(s, { x: 0.55, y, w: 12.2, h: 0.92, name: "gr" + i });
  s.addShape(pres.ShapeType.ellipse, { x: 0.77, y: y + 0.23, w: 0.46, h: 0.46,
    fill: { color: g.c }, line: { color: g.c, width: 0 }, objectName: "grc" + i });
  s.addText(String(4 - i), { x: 0.77, y: y + 0.23, w: 0.46, h: 0.46, fontSize: 15, bold: true,
    color: PAPER, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "grn" + i });
  s.addText(g.g, { x: 1.4, y: y + 0.26, w: 1.5, h: 0.4, fontSize: 13.5, bold: true,
    color: g.c, margin: 0, isTextBox: true, valign: "middle", objectName: "grg" + i });
  s.addText(g.d, { x: 3.0, y: y + 0.14, w: 8.4, h: 0.66, fontSize: 11.5, color: MUT,
    lineSpacing: 14, margin: 0, isTextBox: true, valign: "middle", objectName: "grd" + i });
  s.addText(g.n, { x: 11.5, y: y + 0.26, w: 1.05, h: 0.4, fontSize: 11, bold: true,
    color: INK, align: "right", margin: 0, isTextBox: true, valign: "middle", objectName: "grq" + i });
});
s.addText("All fifteen guidelines were read at first hand, and nine are quoted verbatim in the repository with section-level locators and the guideline's own strength-of-recommendation grading. Reading them changed four of our own earlier decisions, including one reversal.",
  { x: 0.55, y: 6.5, w: 12.2, h: 0.42, fontSize: 11.5, italic: true, color: MUT, lineSpacing: 14, margin: 0, isTextBox: true });
note(s, "This grading is the answer to the project's weakest assumption. We do not claim silence means invariance. We grade how much inference each item requires and label the two weakest items so a reader can discount them.");

// ============ 16. OUTCOMES AND SCORING ========================== //
s = S("CONTENT", "Methodology", "Two outcomes, scoring, and its validation gate");
card(s, { x: 0.55, y: 1.28, w: 6.0, h: 1.9, fill: TINT, kicker: "TWO OUTCOMES, NEVER MIXED UP", kickerColor: TEAL, name: "o1c" });
s.addText([
  { text: "O1, guideline concordance. ", options: { bold: true, color: INK } },
  { text: "Probability on the guideline-correct option. This is what a patient experiences as better or worse care.\n", options: { color: MUT } },
  { text: "O2, target-diagnosis endorsement. ", options: { bold: true, color: INK } },
  { text: "Probability on the option naming the target diagnosis, correct or not. This is the outcome the corpus mechanism speaks to, and it does not flip sign with the guideline.", options: { color: MUT } },
], { x: 0.77, y: 1.82, w: 5.56, h: 1.28, fontSize: 11.5, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 1.28, w: 6.0, h: 1.9, fill: TINT, kicker: "SCORING BY POINTWISE MUTUAL INFORMATION", kickerColor: TEAL, name: "o2c" });
s.addText("Options are scored by PMI, which subtracts each option's unconditional probability. Without that subtraction a common answer string looks like a clinical preference. All three score statistics are computed and reported, so a result that appears under only one of them is visible as such.",
  { x: 6.97, y: 1.82, w: 5.56, h: 1.28, fontSize: 11.5, color: MUT, lineSpacing: 14.5, margin: 0, isTextBox: true });

s.addText("Before any result is computed, a four-test validation suite runs against the real scoring path",
  { x: 0.55, y: 3.34, w: 12.2, h: 0.32, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true });
const val = [
  { n: "T1", h: "Determinism", b: "Identical inputs must score identically, bit for bit. Any drift means the gender gap is confounded with run-to-run noise." },
  { n: "T2", h: "Signal recovery", b: "The scorer must recover an answer planted in the prompt in plain words. If it cannot, a null result is uninterpretable." },
  { n: "T3", h: "Nuisance floor", b: "A gender token with no clinical content still moves the distribution. That movement is the floor, and an effect below it is not a finding." },
  { n: "T4", h: "Score-key robustness", b: "No score statistic is length-neutral, so option sets are held within a two-token spread and all three keys are reported." },
];
val.forEach((v, i) => {
  const x = 0.55 + i * 3.1;
  card(s, { x, y: 3.76, w: 2.85, h: 1.74, name: "v" + i });
  s.addText(v.n, { x: x + 0.22, y: 3.9, w: 0.7, h: 0.3, fontSize: 12, bold: true,
    color: TEAL, fontFace: "Courier New", margin: 0, isTextBox: true, objectName: "vn" + i });
  s.addText(v.h, { x: x + 0.22, y: 4.2, w: 2.42, h: 0.3, fontSize: 13, bold: true,
    color: INK, margin: 0, isTextBox: true, objectName: "vh" + i });
  s.addText(v.b, { x: x + 0.22, y: 4.52, w: 2.42, h: 0.9, fontSize: 11, color: MUT,
    lineSpacing: 13.5, margin: 0, isTextBox: true, objectName: "vb" + i });
});
card(s, { x: 0.55, y: 5.66, w: 12.2, h: 0.78, fill: "FBEEEC", name: "valw" });
s.addText([{ text: "T3 is the test that failed us. ", options: { bold: true, color: FAIL } },
  { text: "On 3 November the nuisance floor turned out to have been measured on the wrong stimulus geometry, and it was inflated roughly eight and a half times. Slide 23 explains it.", options: { color: INK } }],
  { x: 0.77, y: 5.84, w: 11.76, h: 0.5, fontSize: 12.5, lineSpacing: 15, margin: 0, isTextBox: true });
note(s, "The validation suite is what makes a null interpretable. Run it before any interpretation, on every model. T3 is the one that found the measurement error, which is the suite doing its job even though the fault was in the suite itself.");

module.exports = {};
