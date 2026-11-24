// SPOKEN 5 of 16: the counterfactual matrix, alone on its slide. [45s]
//
// This is the contribution and it gets the single largest budget in the deck.
// The claim is geometric: the sex parameter is a ROW, the identity label is a
// COLUMN, and the configurations clinicians see are CELLS. The multiplication
// to 624 prompts used to share this slide and now has its own, so a listener
// holds one idea here and not two.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

pres.addSection({ title: "2 Method" });
const s = S("CONTENT", "2 Method", "Hold the biology fixed. Vary only the identity.");
K.mark("matrix");

s.addText([
  { text: `HL7 Gender Harmony ${A.m("mcclure2021")}: `, options: { bold: true, color: TEAL } },
  { text: "the clinical sex parameter is a separate field from gender identity. We state it, then hold it still.",
    options: { color: MUT } },
], { x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, isTextBox: true,
     margin: 0, objectName: "sub" });

const LAB_W = 1.62, COL_W = 2.3, COL_GAP = 0.1, X0 = 2.37;
const colX = i => X0 + i * (COL_W + COL_GAP);
const HDR_Y = 1.96, R_Y = [2.42, 3.72], R_H = 1.22;

const IDENT = ["“a woman”", "“a man”",
               "“a non-binary person”", "“an adult”"];
const IDENT_SUB = ["she / her", "he / him", "they / them", "no gender named"];
IDENT.forEach((t, i) => {
  s.addText(t, { x: colX(i), y: HDR_Y, w: COL_W, h: 0.26, fontSize: 12, bold: true,
    color: i === 3 ? WARN : INK, align: "center", isTextBox: true, margin: 0,
    objectName: `ch${i}` });
  s.addText(IDENT_SUB[i], { x: colX(i), y: HDR_Y + 0.24, w: COL_W, h: 0.2,
    fontSize: 9, color: MUT, align: "center", isTextBox: true, margin: 0,
    objectName: `cs${i}` });
});
s.addText("GENDER IDENTITY LABEL IN THE PROMPT  →", {
  x: X0, y: HDR_Y - 0.28, w: 9.5, h: 0.22, fontSize: 9, bold: true, color: MUT,
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "cax" });

const CIS = "DCEDEA", TRANS = "F2E2E8", NB = "E9E3F0", REF = "FBF0DC";
// The words "cisgender" and "transgender" appear HERE, in our analysis frame,
// and never in a prompt. That is the design point, so the annotation and the
// prompt text are styled differently on purpose.
const CELLS = [
  [["cisgender woman", CIS], ["transgender man", TRANS],
   ["non-binary person,\nfemale parameter", NB], ["identity withheld\n(reference)", REF]],
  [["transgender woman", TRANS], ["cisgender man", CIS],
   ["non-binary person,\nmale parameter", NB], ["identity withheld\n(reference)", REF]],
];
[["female"], ["male"]].forEach(([val], r) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.55, y: R_Y[r], w: LAB_W, h: R_H, rectRadius: 0.06,
    fill: { color: INK }, line: { color: INK, width: 0 }, objectName: `rl${r}-bg` });
  s.addText([{ text: "Sex for clinical use:\n", options: { fontSize: 8.5, color: "8FB2BA" } },
             { text: val, options: { fontSize: 17, bold: true, color: PAPER } }],
    { x: 0.6, y: R_Y[r], w: LAB_W - 0.1, h: R_H, align: "center", valign: "middle",
      lineSpacing: 16, isTextBox: true, margin: 0, objectName: `rl${r}` });
  CELLS[r].forEach(([t, fill], c) => {
    s.addShape(pres.ShapeType.roundRect, {
      x: colX(c), y: R_Y[r], w: COL_W, h: R_H, rectRadius: 0.06,
      fill: { color: fill }, line: { color: PAPER, width: 2 },
      objectName: `cell${r}${c}-bg` });
    s.addText(t, { x: colX(c) + 0.08, y: R_Y[r], w: COL_W - 0.16, h: R_H,
      fontSize: 11.5, bold: true, color: INK, align: "center", valign: "middle",
      lineSpacing: 14, isTextBox: true, margin: 0, objectName: `cell${r}${c}` });
  });
});
s.addText("SEX PARAMETER\nHELD FIXED", { x: 0.55, y: 1.9, w: LAB_W, h: 0.44,
  fontSize: 8.5, bold: true, color: MUT, align: "center", lineSpacing: 10.5,
  isTextBox: true, margin: 0, objectName: "rax" });

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.22, w: 12.23, h: 0.92, rectRadius: 0.06,
  fill: { color: TINT }, line: { color: TINT, width: 0 }, objectName: "why-bg" });
s.addText([
  { text: "Six configurations, zero loaded words.  ", options: { bold: true, color: TEAL } },
  { text: `The prompt never contains “transgender” or “cisgender”. The model sees a clinical field and a pronoun, so it cannot match on the label for the category we are testing ${A.m("dev2021")}. `,
    options: { color: MUT } },
  { text: `The fourth column names no gender at all: the reference the other three are measured against ${A.m("equitriage2026")}.`,
    options: { color: MUT } },
], { x: 0.8, y: 5.3, w: 11.73, h: 0.76, fontSize: 11.5, lineSpacing: 15,
     valign: "middle", isTextBox: true, margin: 0, objectName: "why" });

// 45 seconds, about 103 words. The contribution. Go slowly.
note(s, `[45s] This is the method, so slow down.

The row is the sex parameter for clinical use. That is the HL7 Gender Harmony idea: in a real record the physiological field a decision turns on is stored separately from who the patient says they are. We put it in the prompt and hold it still.

The column is the identity label, and the fourth names no gender at all.

Now the point. Cross the two and the configurations clinicians actually see fall out as cells. Female parameter with a man's label is a transgender man. The diagonal is cisgender.

And we get all six without ever writing the word transgender in a prompt.`);
