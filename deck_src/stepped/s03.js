// SPOKEN 3 of 16: the open pipeline and the six questions. [26s]
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, arrow, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const VG = F.vignetteGroups();

const s = S("CONTENT", "1 Problem", "Six questions on one causal chain");
K.mark("open");

s.addText("Text becomes a corpus, the corpus becomes weights, the weights give clinical advice.", {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

// 0.55 + 4*2.71 + 3*0.46 = 12.77, inside the 12.78 right edge.
const NODE_W = 2.71, NODE_H = 1.15, XS = [0.55, 3.72, 6.89, 10.06];
const AX = [3.26, 6.43, 9.60];
const NODES = [
  ["Training corpus", `2 released corpora ${A.m("gao2020", "soldaini2024")}\nqueryable by exact n-gram ${A.m("liu2024")}`],
  ["Model weights",   `7 Pythia sizes ${A.m("biderman2023")}\nOLMo-2 base + Instruct ${A.m("olmo2025")}`],
  ["Clinical advice", `${VG.nLive} vignettes\n17,280 scored option rows`],
  ["Datasheet",       `10 model and\ndataset cards ${A.m("gebru2021")}`],
];
const Y = 2.72;
NODES.forEach(([t, sub], i) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: XS[i], y: Y, w: NODE_W, h: NODE_H, rectRadius: 0.07,
    fill: { color: TINT }, line: { color: TEAL, width: 1.4 },
    objectName: `o${i}-bg` });
  s.addText(t, { x: XS[i] + 0.1, y: Y + 0.14, w: NODE_W - 0.2, h: 0.32,
    fontSize: 14.5, bold: true, color: INK, align: "center", isTextBox: true,
    margin: 0, objectName: `o${i}-t` });
  s.addText(sub, { x: XS[i] + 0.1, y: Y + 0.5, w: NODE_W - 0.2, h: 0.56,
    fontSize: 9.5, color: MUT, align: "center", lineSpacing: 12,
    isTextBox: true, margin: 0, objectName: `o${i}-s` });
});
AX.forEach((x, i) => arrow(s, { x, y: Y + 0.46, w: 0.44, h: 0.24,
  color: "9BB3BA", name: `oa${i}` }));

const rq = (n, x, label, col) => {
  K.badge(s, { x, y: 2.08, d: 0.4, n, color: col || TEAL, fs: 14, name: `rq${n}` });
  s.addText(label, { x: x + 0.47, y: 2.1, w: 2.0, h: 0.36, fontSize: 11, bold: true,
    color: col || TEAL, isTextBox: true, margin: 0, valign: "middle",
    objectName: `rq${n}-l` });
};
rq(1, 0.75, "Corpus skew");
rq(2, 7.09, "Unwarranted gaps");
rq(6, 10.26, "Did the card say so?");

s.addShape(pres.ShapeType.line, { x: 3.9, y: Y + NODE_H + 0.2, w: 2.4, h: 0,
  line: { color: BERRY, width: 1.4 }, objectName: "rq3-br" });
K.badge(s, { x: 4.3, y: Y + NODE_H + 0.32, d: 0.38, n: 3, color: BERRY, fs: 13.5, name: "rq3" });
s.addText("Does the gap grow with scale?", { x: 4.76, y: Y + NODE_H + 0.34,
  w: 3.0, h: 0.34, fontSize: 11, bold: true, color: BERRY, isTextBox: true,
  margin: 0, valign: "middle", objectName: "rq3-l" });

// RQ4 spans corpus to advice. The badge and label sit BELOW the rule, never on
// it: drawn at the same y the rule struck straight through the words.
const SPAN_Y = 5.12;
s.addShape(pres.ShapeType.line, { x: 2.1, y: SPAN_Y, w: 6.4, h: 0,
  line: { color: WARN, width: 1.6, dashType: "dash" }, objectName: "rq4-sp" });
[2.1, 8.5].forEach((x, i) => s.addShape(pres.ShapeType.line, {
  x, y: Y + NODE_H, w: 0, h: SPAN_Y - (Y + NODE_H),
  line: { color: WARN, width: 1.6, dashType: "dash" }, objectName: `rq4-l${i}` }));
K.badge(s, { x: 4.6, y: SPAN_Y + 0.16, d: 0.4, n: 4, color: WARN, fs: 14, name: "rq4" });
s.addText("Does the data skew predict the output gap?", { x: 5.08, y: SPAN_Y + 0.18,
  w: 4.0, h: 0.36, fontSize: 11, bold: true, color: WARN, isTextBox: true,
  margin: 0, valign: "middle", objectName: "rq4-l" });

s.addText("Each question cuts into the chain at a different point. That is the whole design.", {
  x: 0.55, y: 6.18, w: 12.2, h: 0.3, fontSize: 12.5, bold: true, color: INK,
  align: "center", isTextBox: true, margin: 0, objectName: "punch" });

// 26 seconds, about 58 words.
note(s, `[26s] One causal chain. Text becomes a corpus, the corpus becomes weights, the weights give clinical advice, and a datasheet says what was in it.

Our six questions cut into that chain at six different points: skew in the data, gaps in the advice, whether it tracks scale, whether the data predicts the gap, and whether the card disclosed any of it.`);
