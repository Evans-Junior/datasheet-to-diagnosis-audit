// SPOKEN 16 of 16: the close. One sentence, nothing else on it. [17s]
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const GT = F.gateTable();
const nFail = GT.filter(r => r.gate === "INSENSITIVE").length;

const s = S("CONTENT_DARK", "4 Limits", "From datasheet to diagnosis");
K.mark("close");

// Two stacked boxes, not one box with newlines: centred runs inside a single
// paragraph wrap against each other and came out ragged in the render.
s.addText("An LLM with no treatment gap may be clinically blind rather than equitable,",
  { x: 0.9, y: 1.66, w: 11.53, h: 1.0, fontSize: 29, bold: true, color: PAPER,
    lineSpacing: 40, align: "center", valign: "middle", isTextBox: true,
    margin: 0, objectName: "line1" });
s.addText("and only a positive control tells the two apart.",
  { x: 0.9, y: 2.74, w: 11.53, h: 0.56, fontSize: 29, bold: true, color: WARN,
    align: "center", valign: "middle", isTextBox: true, margin: 0,
    objectName: "line1b" });

s.addShape(pres.ShapeType.line, { x: 5.0, y: 3.62, w: 3.33, h: 0,
  line: { color: "2A6472", width: 1.2 }, objectName: "rule" });

s.addText("Opening the training pipeline is what let us name the mechanism — identity read as sex parameter — instead of only scoring the symptom.", {
  x: 1.6, y: 3.9, w: 10.13, h: 0.8, fontSize: 15, color: "AFCBD1",
  lineSpacing: 22, align: "center", valign: "middle", isTextBox: true,
  margin: 0, objectName: "line2" });

const F3 = [[`${nFail} of ${GT.length}`, "failed the positive control"],
            ["0", "occurrences of “the non-binary patient”"],
            ["Tier 1", "pending clinical validation"]];
F3.forEach(([n, l], i) => {
  const x = 0.55 + i * 4.11;
  s.addText(n, { x, y: 5.14, w: 4.0, h: 0.5, fontSize: 22, bold: true,
    color: i === 2 ? WARN : TEAL, fontFace: "Cambria", align: "center",
    isTextBox: true, margin: 0, objectName: `f${i}-n` });
  s.addText(l, { x, y: 5.64, w: 4.0, h: 0.34, fontSize: 11, color: "8FB2BA",
    align: "center", isTextBox: true, margin: 0, objectName: `f${i}-l` });
});

s.addText("Evans Kumi  ·  Aymen Boustani        ECSE-557 Ethics in Artificial Intelligence, McGill", {
  x: 0.55, y: 6.3, w: 12.23, h: 0.3, fontSize: 11, color: "6E8C94",
  align: "center", isTextBox: true, margin: 0, objectName: "auth" });

// 17 seconds, about 38 words.
note(s, `[17s] Close on this and stop.

A model with no treatment gap may be blind rather than fair, and only a positive control tells you which.

Opening the pipeline let us name the mechanism instead of scoring the symptom.

Thank you.`);
