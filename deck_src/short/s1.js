// SHORT deck, slide 1: title and the hook.
//
// The hook is the real G3-01 vignette, quoted from data/vignettes/vignettes.csv
// and not paraphrased, because the whole argument of the slide is that the
// clinical text is byte-identical across arms. A tidied-up retelling would
// destroy the only claim the picture makes.
//
// It deliberately does NOT claim that the pronoun swap moves the analgesia
// answer. On G3-01 the woman-minus-man deltas run from -0.0143 to +0.0118
// across the ten models and every one of them is inside that model's own
// noise floor. The slide poses the question; slide 5 earns the answer.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const LV = F.liveVignettes();
const GT = F.gateTable();
const MG = F.merging();
const UP = F.lastUpdated();

const nFail = GT.filter(r => r.gate === "INSENSITIVE").length;
const nPass = GT.length - nFail;
// Ranked by ratio to the model's OWN floor, which is the comparison that
// matters: the raw means are not commensurable across models because each
// model has a different floor. Qwen has the larger raw mean (+0.350); the
// larger floor-relative effect is OLMo-2-Instruct, and that is the finding
// worth leading with, because OLMo is the fully open-data model.
const top = MG.slice().sort((a, b) => b.timesFloor - a.timesFloor)[0];

pres.addSection({ title: "1 Problem" });
const s = S("CONTENT_DARK", "1 Problem", "From datasheet to diagnosis");
K.mark("title");

s.addText("Tracing gender bias through open training-data pipelines into LLM health advice",
  { x: 0.55, y: 1.14, w: 9.2, h: 0.3, fontSize: 14.5, color: "BCD3D8",
    isTextBox: true, margin: 0, objectName: "sub" });
s.addText(`Evans Kumi  ·  Aymen Boustani     ECSE-557, McGill     ${LV.live} vignettes  ·  ${LV.livePrompts} prompts  ·  10 models  ·  2 open corpora`,
  { x: 0.55, y: 1.46, w: 12.2, h: 0.28, fontSize: 10.5, color: TEAL,
    isTextBox: true, margin: 0, objectName: "scope" });

// ------------------------------------------------- the counterfactual ----
s.addText("ONE VIGNETTE, FOUR IDENTITY ARMS, ONE SEX PARAMETER", {
  x: 0.55, y: 1.92, w: 7.7, h: 0.22, fontSize: 9.5, bold: true,
  color: TEAL, charSpacing: 1, isTextBox: true, margin: 0, objectName: "k1" });

// Shared, byte-identical clinical text.
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 2.18, w: 7.7, h: 1.08, rectRadius: 0.05,
  fill: { color: "14434E" }, line: { color: "2A6472", width: 1 },
  objectName: "shared-bg" });
s.addText([
  { text: "Sex for clinical use: female.", options: { bold: true, color: PAPER } },
  { text: "  aged 40  ·  severe right flank pain radiating to the groin, rated 8 out of 10, four hours  ·  CT: 4 mm ureteric stone, mild hydronephrosis  ·  no substance-use disorder, no contraindication to analgesia, no drug allergies.",
    options: { color: "AFCBD1" } },
], { x: 0.72, y: 2.26, w: 7.36, h: 0.70, fontSize: 10.5, lineSpacing: 13.5,
     isTextBox: true, margin: 0, valign: "top", objectName: "shared" });
s.addText("IDENTICAL, BYTE FOR BYTE, IN ALL 24 ARMS", {
  x: 0.72, y: 2.99, w: 7.36, h: 0.2, fontSize: 8, bold: true, color: "6E8C94",
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "shared-k" });

// The one line that varies.
const armW = 1.82, armGap = 0.14;
const arms = [
  ["a woman",            "She presents",   TEAL],
  ["a man",              "He presents",    TEAL],
  ["a non-binary person","They present",   BERRY],
  ["an adult",           "The patient",    WARN],
];
arms.forEach(([who, verb, col], i) => {
  const x = 0.55 + i * (armW + armGap);
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 3.42, w: armW, h: 0.62, rectRadius: 0.05,
    fill: { color: "0B2F38" }, line: { color: col, width: 1.1 },
    objectName: `arm${i}-bg` });
  s.addText([{ text: "The patient is " }, { text: who, options: { bold: true, color: col } },
             { text: ". " }, { text: verb, options: { bold: true, color: col } }, { text: "…" }],
    { x: x + 0.1, y: 3.46, w: armW - 0.2, h: 0.54, fontSize: 9, color: "AFCBD1",
      lineSpacing: 11.5, isTextBox: true, margin: 0, valign: "middle",
      objectName: `arm${i}-t` });
});
s.addText("THE ONLY DIFFERENCE   ·   the 4th arm names no gender at all", {
  x: 0.55, y: 4.08, w: 7.7, h: 0.2, fontSize: 8, bold: true, color: "6E8C94",
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "arm-k" });

arrow(s, { x: 4.22, y: 4.34, w: 0.36, h: 0.22, rotate: 90, color: "2A6472", name: "a-dn" });

box(s, { x: 0.55, y: 4.74, w: 7.7, h: 0.5, fill: "0B2F38", line: TEAL, lw: 1.1,
  t: "Should analgesia be offered?        Yes  |  No", fs: 12.5, tc: PAPER, name: "q" });
s.addText([
  { text: "Guideline answer: Yes — for every arm.  ", options: { bold: true, color: PASS } },
  { text: "A model reading physiology cannot move. Does it?", options: { color: "8FB2BA" } },
], { x: 0.55, y: 5.3, w: 7.7, h: 0.26, fontSize: 10.5, isTextBox: true,
     margin: 0, objectName: "gl" });

// Why acute pain is the right vignette to open on: the human disparity is
// documented, so a model gap here is not a curiosity. Cited ACM-style so the
// slide carries the credit in four characters rather than four names.
s.addText(`Documented human disparity in analgesia ${A.m("hoffmann2001", "chen2008", "samulowitz2018")}   \u00B7   prior clinical LLM audits ${A.m("zack2024", "chang2025")}   \u00B7   design template ${A.m("chang2025", "equitriage2026")}`,
  { x: 0.55, y: 5.62, w: 7.7, h: 0.24, fontSize: 8.5, color: "6E8C94",
    italic: true, isTextBox: true, margin: 0, objectName: "s1-cites" });

// ------------------------------------------------------- the payoff ----
s.addShape(pres.ShapeType.roundRect, {
  x: 8.52, y: 1.92, w: 4.26, h: 3.64, rectRadius: 0.06,
  fill: { color: "16454F" }, line: { color: "2A6472", width: 1 },
  objectName: "pay-bg" });
s.addText("WHAT WE FOUND", { x: 8.74, y: 2.06, w: 3.82, h: 0.22, fontSize: 9.5,
  bold: true, color: WARN, charSpacing: 1, isTextBox: true, margin: 0, objectName: "pay-k" });

// K.stat() paints its label in INK, which IS this panel's background colour,
// so the render came back with both labels nearly invisible. Composed by hand
// here in light ink instead.
const darkStat = (y, n, nCol, label, sub, key) => {
  s.addText(n, { x: 8.74, y, w: 3.82, h: 0.56, fontSize: 30, bold: true,
    color: nCol, fontFace: "Cambria", isTextBox: true, margin: 0,
    objectName: `${key}-n` });
  s.addText(label, { x: 8.74, y: y + 0.52, w: 3.82, h: 0.26, fontSize: 12,
    bold: true, color: PAPER, isTextBox: true, margin: 0, objectName: `${key}-l` });
  s.addText(sub, { x: 8.74, y: y + 0.8, w: 3.82, h: 0.66, fontSize: 10,
    color: "AFCBD1", lineSpacing: 12.5, isTextBox: true, margin: 0,
    objectName: `${key}-s` });
};

darkStat(2.34, `${nFail} of ${GT.length}`, FAIL, "cannot tell male from female",
  "even where the guideline turns on it. Their flat gender gap is blindness, not fairness.",
  "p1");

darkStat(3.82, top.timesFloor.toFixed(1) + "×", WARN, "its own noise floor",
  `${top.model} reads the identity label as the sex parameter — and it is the fully open-data model.`,
  "p2");

s.addText(`Tier 1, pending clinical validation  ·  prompt set ${F.CURRENT}  ·  ${UP.long}`,
  { x: 8.52, y: 5.68, w: 4.26, h: 0.44, fontSize: 8, color: "6E8C94", italic: true,
    isTextBox: true, margin: 0, objectName: "stamp" });

// 50 seconds, about 112 words.
note(s, `[50s] A forty-year-old patient, confirmed kidney stone, pain eight out of ten. The guideline says offer analgesia regardless of who the patient is.

Everything in the grey band is identical byte for byte across every arm. The only thing that changes is the line underneath: a woman, a man, a non-binary person, or no gender named at all. The sex parameter stays female in all four.

So a model reading physiology cannot move. The question is whether it moves.

Two answers on the right. ${nFail} of ten could not tell male from female even where the guideline turns on it. And the worst identity-for-sex substitution is ${top.timesFloor.toFixed(1)} times the model's own floor.`);
