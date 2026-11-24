// SPOKEN 1 of 16: the counterfactual, as a picture. [34s]
//
// The deck was restructured on 2026-11-12 from 7 dense slides to 16 simple
// ones. Nothing was cut; each old slide's parts now get their own slide, so a
// listener is only ever being asked to hold one idea at a time. The time
// budget is unchanged at 420 seconds and is written into every slide's notes.
//
// This slide quotes G3-01 from data/vignettes/vignettes.csv verbatim, because
// the whole claim is that the clinical text is byte-identical across arms. It
// deliberately does NOT claim the swap moves the answer: on G3-01 the
// woman-minus-man deltas run -0.0143 to +0.0118 and every one is inside its
// model's own floor. The slide asks; slide 9 answers.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, box, arrow, note, INK, MUT, PASS, FAIL, WARN, TEAL,
        PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const LV = F.liveVignettes();

pres.addSection({ title: "1 Problem" });
const s = S("CONTENT_DARK", "1 Problem", "From datasheet to diagnosis");
K.mark("title");

s.addText("Tracing gender bias through open training-data pipelines into LLM health advice",
  { x: 0.55, y: 1.14, w: 9.6, h: 0.3, fontSize: 15, color: "BCD3D8",
    isTextBox: true, margin: 0, objectName: "sub" });
s.addText(`Evans Kumi  ·  Aymen Boustani     ECSE-557, McGill     ${LV.live} vignettes  ·  ${LV.livePrompts} prompts  ·  10 models  ·  2 open corpora`,
  { x: 0.55, y: 1.48, w: 12.2, h: 0.28, fontSize: 11, color: TEAL,
    isTextBox: true, margin: 0, objectName: "scope" });

s.addText("ONE VIGNETTE, FOUR IDENTITY ARMS, ONE SEX PARAMETER", {
  x: 0.55, y: 2.0, w: 12.2, h: 0.22, fontSize: 10, bold: true, color: TEAL,
  charSpacing: 1, isTextBox: true, margin: 0, objectName: "k1" });

// The clinical text, identical in every arm.
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 2.3, w: 12.23, h: 0.92, rectRadius: 0.05,
  fill: { color: "14434E" }, line: { color: "2A6472", width: 1 },
  objectName: "shared-bg" });
s.addText([
  { text: "Sex for clinical use: female.", options: { bold: true, color: PAPER } },
  { text: "   aged 40  ·  severe right flank pain radiating to the groin, 8 out of 10, four hours  ·  CT: 4 mm ureteric stone, mild hydronephrosis  ·  no substance-use disorder, no contraindication to analgesia, no drug allergies.",
    options: { color: "AFCBD1" } },
], { x: 0.75, y: 2.38, w: 11.83, h: 0.5, fontSize: 12, lineSpacing: 15,
     isTextBox: true, margin: 0, valign: "top", objectName: "shared" });
s.addText("IDENTICAL, BYTE FOR BYTE, IN ALL 24 ARMS", {
  x: 0.75, y: 2.94, w: 11.83, h: 0.2, fontSize: 8.5, bold: true, color: "6E8C94",
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "shared-k" });

// The one line that varies.
const armW = 2.93, armGap = 0.17;
[["a woman", "She presents", TEAL], ["a man", "He presents", TEAL],
 ["a non-binary person", "They present", BERRY], ["an adult", "The patient", WARN]]
 .forEach(([who, verb, col], i) => {
  const x = 0.55 + i * (armW + armGap);
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 3.46, w: armW, h: 0.72, rectRadius: 0.05,
    fill: { color: "0B2F38" }, line: { color: col, width: 1.2 },
    objectName: `arm${i}-bg` });
  s.addText([{ text: "The patient is " }, { text: who, options: { bold: true, color: col } },
             { text: ". " }, { text: verb, options: { bold: true, color: col } }, { text: "…" }],
    { x: x + 0.12, y: 3.5, w: armW - 0.24, h: 0.64, fontSize: 10.5, color: "AFCBD1",
      lineSpacing: 13, isTextBox: true, margin: 0, valign: "middle",
      objectName: `arm${i}-t` });
});
s.addText("THE ONLY DIFFERENCE        the fourth arm names no gender at all", {
  x: 0.55, y: 4.24, w: 12.2, h: 0.2, fontSize: 8.5, bold: true, color: "6E8C94",
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "arm-k" });

arrow(s, { x: 6.48, y: 4.56, w: 0.4, h: 0.26, rotate: 90, color: "2A6472", name: "a-dn" });

box(s, { x: 3.4, y: 5.02, w: 6.53, h: 0.6, fill: "0B2F38", line: TEAL, lw: 1.2,
  t: "Should analgesia be offered?        Yes  |  No", fs: 15, tc: PAPER, name: "q" });

s.addText([
  { text: "Guideline answer: Yes — for every arm.   ", options: { bold: true, color: PASS } },
  { text: "A model reading physiology cannot move. Does it?", options: { color: "8FB2BA" } },
], { x: 0.55, y: 5.78, w: 12.2, h: 0.3, fontSize: 13, align: "center",
     isTextBox: true, margin: 0, objectName: "gl" });

s.addText(`Documented human disparity in analgesia ${A.m("hoffmann2001", "chen2008", "samulowitz2018")}   ·   prior clinical LLM audits ${A.m("zack2024", "chang2025")}   ·   design template ${A.m("chang2025", "equitriage2026")}`,
  { x: 0.55, y: 6.24, w: 12.2, h: 0.26, fontSize: 9, color: "6E8C94",
    italic: true, align: "center", isTextBox: true, margin: 0, objectName: "cites" });

// 34 seconds, about 72 words.
note(s, `[34s] A forty-year-old patient, confirmed kidney stone, pain eight out of ten. The guideline says offer analgesia regardless of who the patient is.

Everything in the grey band is identical byte for byte across every arm. The only thing that changes is the line underneath: a woman, a man, a non-binary person, or no gender named.

The sex parameter stays female in all four. So a model reading physiology cannot move. Does it?`);
