// SPOKEN 10 of 16: what the gate result MEANS. The ethical turn. [28s]
// Split from the gate chart so the interpretation gets its own beat; it is the
// single most important sentence in the talk and it used to share a slide with
// a ten-bar chart.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const GT = F.gateTable();
const CR = F.chanceRange();
const nFail = GT.filter(r => r.gate === "INSENSITIVE").length;

const s = S("CONTENT_DARK", "3 Results", "A flat gender gap is not fairness");
K.mark("blind");

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 1.34, w: 12.23, h: 1.9, rectRadius: 0.07,
  fill: { color: "2E1F1E" }, line: { color: FAIL, width: 1.2 }, objectName: "big-bg" });
s.addText([
  { text: `Those ${nFail} models show almost no gender gap anywhere in our set.\n`,
    options: { color: "E8C9C3" } },
  { text: "Read without a positive control, that is a clean bill of health.\n",
    options: { color: "E8C9C3" } },
  { text: "Read with one, it is a model that cannot distinguish male from female when the guideline demands it.",
    options: { bold: true, color: PAPER } },
], { x: 0.9, y: 1.46, w: 11.53, h: 1.66, fontSize: 17, lineSpacing: 26,
     valign: "middle", isTextBox: true, margin: 0, objectName: "big" });

const TILE = [
  ["What it looks like", "No treatment gap between arms. Nothing to report. The model appears equitable on every metric an audit without a control would compute.", "6E8C94"],
  ["What it is", "A model that cannot read the clinical field at all. The gap is flat because nothing is being distinguished, not because it is being distinguished fairly.", WARN],
  ["Why it is worse", `Deploying it would be the more dangerous choice, because it fails silently and it fails in the direction that looks like success ${A.m("yoo2026")}.`, FAIL],
];
TILE.forEach(([h, b, col], i) => {
  const x = 0.55 + i * 4.11;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 3.48, w: 4.0, h: 1.86, rectRadius: 0.06,
    fill: { color: "16454F" }, line: { color: "2A6472", width: 1 },
    objectName: `t${i}-bg` });
  s.addText(h, { x: x + 0.22, y: 3.62, w: 3.56, h: 0.3, fontSize: 12.5, bold: true,
    color: col, isTextBox: true, margin: 0, objectName: `t${i}-h` });
  s.addText(b, { x: x + 0.22, y: 3.96, w: 3.56, h: 1.26, fontSize: 11,
    color: "AFCBD1", lineSpacing: 14, valign: "top", isTextBox: true, margin: 0,
    objectName: `t${i}-b` });
});

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.56, w: 12.23, h: 0.86, rectRadius: 0.06,
  fill: { color: "14434E" }, line: { color: "2A6472", width: 1 }, objectName: "pool-bg" });
s.addText([
  { text: "And why we never show a pooled number alone.  ", options: { bold: true, color: TEAL } },
  { text: `Group 2 flips the correct answer with the sex parameter, so pooling across levels is pinned near 0.5 by construction: the ${CR.nModels} Pythia models sit between ${CR.pooledLo.toFixed(4)} and ${CR.pooledHi.toFixed(4)}, which reads as chance. Within a level they span ${CR.withinLo.toFixed(3)} to ${CR.withinHi.toFixed(3)}, and ${CR.widestModel} swings ${CR.maxSwing.toFixed(3)} while pooling to ${CR.widestPooled.toFixed(4)}.`,
    options: { color: "AFCBD1" } },
], { x: 0.8, y: 5.64, w: 11.73, h: 0.7, fontSize: 10.5, lineSpacing: 13.5,
     valign: "middle", isTextBox: true, margin: 0, objectName: "pool" });

// 28 seconds, about 63 words.
note(s, `[28s] Now the sentence to land.

Those seven show almost no gender gap anywhere in our set. Without Group 2 we would have called them seven fair models. With it we can say what it is: a model that cannot tell male from female where the guideline turns on it.

That is not equity. It is blindness, and it is more dangerous, because it looks like the thing you wanted.`);
