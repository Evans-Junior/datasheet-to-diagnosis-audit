// SPOKEN 4 of 16: what a closed model costs you. The argument for working on
// weaker open models. [20s]
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, arrow, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const CQ = F.corpusQueries();

const s = S("CONTENT", "1 Problem", "A closed model breaks the first link");
K.mark("closed");

s.addText(`Qwen3-8B is a good model and we audit it ${A.m("qwen2025")}. Its training corpus was never released.`, {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

const NODE_W = 2.71, NODE_H = 1.0, XS = [0.55, 3.72, 6.89, 10.06];
const Y = 1.9;
// The corpus is drawn as a hole, not a box. That is the entire point.
s.addShape(pres.ShapeType.roundRect, {
  x: XS[0], y: Y, w: NODE_W, h: NODE_H, rectRadius: 0.07,
  fill: { color: "F6F1F0" }, line: { color: FAIL, width: 1.5, dashType: "dash" },
  objectName: "c0-bg" });
s.addText("Training corpus", { x: XS[0] + 0.1, y: Y + 0.16, w: NODE_W - 0.2, h: 0.3,
  fontSize: 14, bold: true, color: FAIL, align: "center", isTextBox: true,
  margin: 0, objectName: "c0-t" });
s.addText("NOT RELEASED", { x: XS[0] + 0.1, y: Y + 0.5, w: NODE_W - 0.2, h: 0.3,
  fontSize: 12, bold: true, color: FAIL, align: "center", charSpacing: 1.2,
  isTextBox: true, margin: 0, objectName: "c0-s" });

["Model weights", "Clinical advice", "Datasheet"].forEach((t, i) => {
  const x = XS[i + 1];
  s.addShape(pres.ShapeType.roundRect, {
    x, y: Y, w: NODE_W, h: NODE_H, rectRadius: 0.07,
    fill: { color: PAPER }, line: { color: "9BB3BA", width: 1.1 },
    objectName: `c${i}-bg` });
  s.addText(t, { x: x + 0.1, y: Y + 0.32, w: NODE_W - 0.2, h: 0.36,
    fontSize: 13.5, bold: true, color: MUT, align: "center", isTextBox: true,
    margin: 0, objectName: `c${i}-t` });
});
[3.26, 6.43, 9.60].forEach((x, i) => arrow(s, { x, y: Y + 0.38, w: 0.44, h: 0.24,
  color: i === 0 ? "E0CFCB" : "C8D7DB", name: `ca${i}` }));

// The three questions that die, shown as struck-out badges.
s.addText("WHAT YOU CAN NO LONGER ASK", {
  x: 0.55, y: 3.3, w: 12.2, h: 0.24, fontSize: 10, bold: true, color: FAIL,
  charSpacing: 1, isTextBox: true, margin: 0, objectName: "dk" });
[[1, "How skewed is the training data?"],
 [4, "Does that skew predict the gap?"],
 [6, "Did the datasheet disclose it?"]].forEach(([n, t], i) => {
  const x = 0.55 + i * 4.11;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 3.6, w: 4.0, h: 0.86, rectRadius: 0.06,
    fill: { color: "FBEEEC" }, line: { color: FAIL, width: 1.1 },
    objectName: `d${n}-bg` });
  K.badge(s, { x: x + 0.2, y: 3.84, d: 0.38, n, color: FAIL, fs: 13.5, name: `db${n}` });
  s.addText(t, { x: x + 0.68, y: 3.6, w: 3.12, h: 0.86, fontSize: 11,
    bold: true, color: INK, valign: "middle", isTextBox: true, margin: 0,
    objectName: `d${n}-t` });
});

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 4.76, w: 12.23, h: 0.82, rectRadius: 0.06,
  fill: { color: INK }, line: { color: INK, width: 0 }, objectName: "pb" });
s.addText([
  { text: "We can still say “this model is biased”. We can no longer say why.  ",
    options: { bold: true, color: PAPER } },
  { text: "That is why we work on weaker open models: they are the only ones where “why” is a question you are allowed to ask.",
    options: { color: "AFCBD1" } },
], { x: 0.8, y: 4.84, w: 11.73, h: 0.66, fontSize: 12.5, lineSpacing: 16,
     valign: "middle", isTextBox: true, margin: 0, objectName: "punch" });

s.addText([
  { text: "Instrument:  ", options: { bold: true, color: TEAL } },
  { text: `infini-gram over ${CQ.nIndexes} indexes ${A.m("liu2024")}, ${CQ.cached.toLocaleString("en-US")} cached exact-count queries, ${CQ.failed} failures.    `, options: { color: MUT } },
  { text: "Framing:  ", options: { bold: true, color: TEAL } },
  { text: `HL7 Gender Harmony ${A.m("mcclure2021")}, demographic blinding ${A.m("equitriage2026")}, prior clinical audits ${A.m("zack2024", "chang2025")}.`, options: { color: MUT } },
], { x: 0.55, y: 5.78, w: 12.2, h: 0.5, fontSize: 10.5, lineSpacing: 13.5,
     isTextBox: true, margin: 0, objectName: "instr" });

// 20 seconds, about 48 words.
note(s, `[20s] Now the point of working on weaker models.

Qwen is good and we audit it, but its corpus was never released. Delete that first box and questions one, four and six are not hard, they are impossible.

We can still say this model is biased. We can no longer say why.`);
