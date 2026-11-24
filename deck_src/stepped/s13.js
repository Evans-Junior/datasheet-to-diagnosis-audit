// SPOKEN 13 of 16: RQ1, the corpus fact, alone. [20s]
// The most quotable sentence in the project. It used to be a small card at the
// bottom of a crowded results slide; here it is the whole slide.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const PR = F.rq5Probe();
const zero = PR.subjectZero;
const bare = PR.rows.find(r => r.term === "non-binary");
const woman = PR.rows.find(r => r.term === "the woman has");
const CQ = F.corpusQueries();

const s = S("CONTENT_DARK", "3 Results", "The guidelines name them. The data does not.");
K.mark("corpus");

s.addText(`RQ1 · exact n-gram counts over both open corpora ${A.m("liu2024")}. Nothing sampled, nothing estimated.`, {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: "BCD3D8",
  isTextBox: true, margin: 0, objectName: "sub" });

// The zero, at the size it deserves.
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 1.68, w: 12.23, h: 2.3, rectRadius: 0.08,
  fill: { color: "2E1F1E" }, line: { color: WARN, width: 1.4 }, objectName: "z-bg" });
s.addText("0", { x: 0.9, y: 1.84, w: 2.4, h: 1.98, fontSize: 108, bold: true,
  color: WARN, fontFace: "Cambria", align: "center", valign: "middle",
  isTextBox: true, margin: 0, objectName: "z-n" });
s.addText([
  { text: `occurrences of “${zero.term}”\n`, options: { bold: true, color: PAPER, fontSize: 22 } },
  { text: `in The Pile, and ${zero.olmo} in olmo-mix-1124.`, options: { color: "E8C9C3", fontSize: 16 } },
], { x: 3.5, y: 1.9, w: 9.1, h: 1.0, lineSpacing: 28, valign: "middle",
     isTextBox: true, margin: 0, objectName: "z-t" });
s.addText(`Meanwhile the bare term “non-binary” appears ${bare.olmo.toLocaleString("en-US")} times in olmo-mix and ${bare.pile.toLocaleString("en-US")} in the Pile. These patients are in the text. They are never in a clinic.`, {
  x: 3.5, y: 2.98, w: 9.1, h: 0.88, fontSize: 13, color: "AFCBD1",
  lineSpacing: 17, valign: "top", isTextBox: true, margin: 0, objectName: "z-b" });

// Context row.
const CTX = [
  [`${woman.olmo.toLocaleString("en-US")}`, "“the woman has” in olmo-mix", TEAL],
  [`${bare.olmo.toLocaleString("en-US")}`, "“non-binary” in olmo-mix", TEAL],
  ["0", `“${zero.term}” in either corpus`, WARN],
];
CTX.forEach(([n, lab, col], i) => {
  const x = 0.55 + i * 4.11;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 4.26, w: 4.0, h: 1.12, rectRadius: 0.06,
    fill: { color: "16454F" }, line: { color: "2A6472", width: 1 },
    objectName: `cx${i}-bg` });
  s.addText(n, { x: x + 0.2, y: 4.38, w: 3.6, h: 0.56, fontSize: 24, bold: true,
    color: col, fontFace: "Cambria", isTextBox: true, margin: 0, objectName: `cx${i}-n` });
  s.addText(lab, { x: x + 0.2, y: 4.94, w: 3.6, h: 0.34, fontSize: 11,
    color: "AFCBD1", isTextBox: true, margin: 0, objectName: `cx${i}-l` });
});

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.58, w: 12.23, h: 0.8, rectRadius: 0.06,
  fill: { color: "14434E" }, line: { color: "2A6472", width: 1 }, objectName: "f-bg" });
s.addText([
  { text: "Guidelines require care for these patients. The corpora that taught these models never show one being treated.  ",
    options: { bold: true, color: PAPER } },
  { text: `${CQ.cached.toLocaleString("en-US")} cached exact-count queries, ${CQ.failed} failures ${A.m("dev2021")}.`,
    options: { color: "8FB2BA" } },
], { x: 0.8, y: 5.66, w: 11.73, h: 0.64, fontSize: 12, lineSpacing: 15,
     valign: "middle", isTextBox: true, margin: 0, objectName: "f" });

// 20 seconds, about 43 words.
note(s, `[20s] Stop on this one.

The phrase occurs zero times in The Pile and zero times in olmo-mix, while the bare term is in the millions.

So these patients exist in the text, but never in a clinic. The guidelines name them. The training data does not.`);
