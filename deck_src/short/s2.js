// SHORT deck, slide 2: why open data, and the six research questions drawn as
// POSITIONS ON THE PIPELINE rather than a bullet list. The point of the slide
// is that each RQ is a different stage of one causal chain, and that a closed
// model deletes the first stage, so three of the six questions become
// unaskable. A list cannot show that; the picture can.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const CQ = F.corpusQueries();
const VG = F.vignetteGroups();
const GT = F.gateTable();

const s = S("CONTENT", "1 Problem", "Why open data is the whole point");
K.mark("why");

s.addText("Six questions, one causal chain. Existing audits can say a model is biased; only an open pipeline lets you ask why.", {
  x: 0.55, y: 1.14, w: 12.2, h: 0.3, fontSize: 12.5, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

const NODE_W = 2.5, NODE_H = 0.8;
const XS = [0.75, 3.85, 6.95, 10.05];
const AX = [3.37, 6.47, 9.57];

// -------------------------------------------------------- open pipeline ----
const yOpen = 2.42;
s.addText("OPEN PIPELINE   ·   Pythia / The Pile   ·   OLMo-2 / olmo-mix-1124", {
  x: 0.55, y: 1.56, w: 8.0, h: 0.22, fontSize: 9.5, bold: true, color: TEAL,
  charSpacing: 1, isTextBox: true, margin: 0, objectName: "k-open" });

const NODES = [
  ["Training corpus",   `2 released corpora ${A.m("gao2020", "soldaini2024")},\nqueryable by exact n-gram ${A.m("liu2024")}`],
  ["Model weights",     `7 Pythia sizes ${A.m("biderman2023")},\nOLMo-2 base + Instruct ${A.m("olmo2025")}`],
  ["Clinical advice",   `${VG.nLive} vignettes,\n17,280 scored option rows`],
  ["Datasheet",         `10 model and\ndataset cards ${A.m("gebru2021")}`],
];
NODES.forEach(([t, sub], i) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: XS[i], y: yOpen, w: NODE_W, h: NODE_H, rectRadius: 0.06,
    fill: { color: TINT }, line: { color: TEAL, width: 1.25 },
    objectName: `o${i}-bg` });
  s.addText(t, { x: XS[i] + 0.1, y: yOpen + 0.08, w: NODE_W - 0.2, h: 0.26,
    fontSize: 12.5, bold: true, color: INK, align: "center", isTextBox: true,
    margin: 0, objectName: `o${i}-t` });
  s.addText(sub, { x: XS[i] + 0.1, y: yOpen + 0.35, w: NODE_W - 0.2, h: 0.4,
    fontSize: 9, color: MUT, align: "center", lineSpacing: 11, isTextBox: true,
    margin: 0, objectName: `o${i}-s` });
});
AX.forEach((x, i) => arrow(s, { x, y: yOpen + 0.3, w: 0.4, h: 0.2,
  color: "9BB3BA", name: `oa${i}` }));

// RQ badges above the stages they interrogate.
const rq = (n, x, label, col) => {
  K.badge(s, { x, y: 1.86, d: 0.34, n, color: col || TEAL, fs: 12, name: `rq${n}` });
  s.addText(label, { x: x + 0.4, y: 1.88, w: 1.94, h: 0.3, fontSize: 9.5, bold: true,
    color: col || TEAL, isTextBox: true, margin: 0, valign: "middle",
    objectName: `rq${n}-l` });
};
rq(1, 1.08, "Corpus skew");
rq(2, 7.28, "Unwarranted gaps");
rq(6, 10.38, "Did the card say so?");

// RQ3 bracket under the weights node.
s.addShape(pres.ShapeType.line, { x: 3.95, y: yOpen + NODE_H + 0.16, w: 2.3, h: 0,
  line: { color: BERRY, width: 1.25 }, objectName: "rq3-br" });
K.badge(s, { x: 4.33, y: yOpen + NODE_H + 0.26, d: 0.32, n: 3, color: BERRY, fs: 11.5, name: "rq3" });
s.addText("Does the gap grow with scale?", { x: 4.72, y: yOpen + NODE_H + 0.28,
  w: 2.6, h: 0.28, fontSize: 9.5, bold: true, color: BERRY, isTextBox: true,
  margin: 0, valign: "middle", objectName: "rq3-l" });

// RQ4 spans corpus -> advice: the linkage question.
s.addShape(pres.ShapeType.line, { x: 2.0, y: 4.16, w: 6.2, h: 0,
  line: { color: WARN, width: 1.5, dashType: "dash" }, objectName: "rq4-sp" });
s.addShape(pres.ShapeType.line, { x: 2.0, y: yOpen + NODE_H, w: 0, h: 0.16,
  line: { color: WARN, width: 1.5, dashType: "dash" }, objectName: "rq4-l1" });
s.addShape(pres.ShapeType.line, { x: 8.2, y: yOpen + NODE_H, w: 0, h: 0.16,
  line: { color: WARN, width: 1.5, dashType: "dash" }, objectName: "rq4-l2" });
// Below the span line, not on it: at y 3.99 the label was struck through by
// the dashed rule, which qa_geom cannot catch because it only tests text
// against text.
K.badge(s, { x: 4.84, y: 4.26, d: 0.34, n: 4, color: WARN, fs: 12, name: "rq4" });
s.addText("Does the data skew predict the output gap?", { x: 5.24, y: 4.26,
  w: 3.4, h: 0.34, fontSize: 9.5, bold: true, color: WARN, isTextBox: true,
  margin: 0, valign: "middle", objectName: "rq4-l" });

// ------------------------------------------------------ closed pipeline ----
const yCl = 5.14;
s.addText("CLOSED PIPELINE   ·   Qwen3-8B, weights only", {
  x: 0.55, y: 4.74, w: 8.0, h: 0.22, fontSize: 9.5, bold: true, color: FAIL,
  charSpacing: 1, isTextBox: true, margin: 0, objectName: "k-cl" });

// The corpus node is drawn as a hole, not a box: that is the whole point.
s.addShape(pres.ShapeType.roundRect, {
  x: XS[0], y: yCl, w: NODE_W, h: NODE_H, rectRadius: 0.06,
  fill: { color: "F6F1F0" }, line: { color: FAIL, width: 1.25, dashType: "dash" },
  objectName: "c0-bg" });
s.addText("Training corpus", { x: XS[0] + 0.1, y: yCl + 0.08, w: NODE_W - 0.2, h: 0.26,
  fontSize: 12.5, bold: true, color: FAIL, align: "center", isTextBox: true,
  margin: 0, objectName: "c0-t" });
s.addText("NOT RELEASED", { x: XS[0] + 0.1, y: yCl + 0.38, w: NODE_W - 0.2, h: 0.24,
  fontSize: 10, bold: true, color: FAIL, align: "center", charSpacing: 1,
  isTextBox: true, margin: 0, objectName: "c0-s" });

[1, 2, 3].forEach(i => {
  s.addShape(pres.ShapeType.roundRect, {
    x: XS[i], y: yCl, w: NODE_W, h: NODE_H, rectRadius: 0.06,
    fill: { color: PAPER }, line: { color: "9BB3BA", width: 1 },
    objectName: `c${i}-bg` });
  s.addText(NODES[i][0], { x: XS[i] + 0.1, y: yCl + 0.26, w: NODE_W - 0.2, h: 0.28,
    fontSize: 12, bold: true, color: MUT, align: "center", isTextBox: true,
    margin: 0, objectName: `c${i}-t` });
});
AX.forEach((x, i) => arrow(s, { x, y: yCl + 0.3, w: 0.4, h: 0.2,
  color: i === 0 ? "E0CFCB" : "C8D7DB", name: `ca${i}` }));
K.badge(s, { x: 7.28, y: 4.72, d: 0.34, n: 5, color: FAIL, fs: 12, name: "rq5" });
s.addText(`Contrast against open models ${A.m("qwen2025")}`, { x: 7.68, y: 4.74, w: 3.0, h: 0.3,
  fontSize: 9.5, bold: true, color: FAIL, isTextBox: true, margin: 0,
  valign: "middle", objectName: "rq5-l" });

s.addText([
  { text: "Break the first link and questions 1, 4 and 6 stop being askable. ",
    options: { bold: true, color: INK } },
  { text: `We can still say "this model is biased"; we can no longer say why, or check whether the card disclosed it.`,
    options: { color: MUT } },
], { x: 0.55, y: 6.04, w: 12.2, h: 0.42, fontSize: 11.5, isTextBox: true,
     margin: 0, objectName: "punch" });

s.addText([
  { text: "Instrument:  ", options: { bold: true, color: TEAL } },
  { text: `infini-gram over ${CQ.nIndexes} indexes ${A.m("liu2024")}, ${CQ.cached.toLocaleString("en-US")} cached exact-count queries, ${CQ.failed} failures.   Framing: HL7 Gender Harmony ${A.m("mcclure2021")}, demographic blinding ${A.m("equitriage2026")}, prior clinical audits ${A.m("zack2024", "chang2025")}.`,
    options: { color: MUT } },
], { x: 0.55, y: 6.5, w: 12.2, h: 0.4, fontSize: 10, isTextBox: true,
     margin: 0, objectName: "instr" });

// References are numbered ACM-style on the final slide; the markers above
// are rendered from docs/references.json through acm.js, so a slide and the
// reference list cannot disagree about which number is whose.

// 45 seconds, about 101 words.
note(s, `[45s] One causal chain. Text becomes a corpus, the corpus becomes weights, the weights give clinical advice, and a datasheet is supposed to say what was in the corpus.

Our six questions are six places to cut into that chain. Do not read them out; point at them.

The bottom row is the argument. Qwen is a good model and we audit it, but its corpus was never released. Delete that first box and questions one, four and six are not hard, they are impossible.

That is why we work on weaker open models. They are the only ones where "why" is a question you are allowed to ask.`);
