// SPOKEN 2 of 16: the two headline findings, up front. [20s]
// Split out of the old slide 1's right-hand panel so it gets its own beat.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const GT = F.gateTable();
const MG = F.merging();
const UP = F.lastUpdated();
const nFail = GT.filter(r => r.gate === "INSENSITIVE").length;
const nPass = GT.length - nFail;
// Ranked by ratio to each model's OWN floor: raw means are not commensurable
// across models with different floors.
const top = MG.slice().sort((a, b) => b.timesFloor - a.timesFloor)[0];

const s = S("CONTENT_DARK", "1 Problem", "What we found");
K.mark("found");

const panel = (x, n, nCol, label, sub, key) => {
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 1.6, w: 5.98, h: 3.5, rectRadius: 0.07,
    fill: { color: "16454F" }, line: { color: "2A6472", width: 1 },
    objectName: `${key}-bg` });
  s.addText(n, { x: x + 0.3, y: 1.9, w: 5.38, h: 1.3, fontSize: 64, bold: true,
    color: nCol, fontFace: "Cambria", isTextBox: true, margin: 0,
    objectName: `${key}-n` });
  s.addText(label, { x: x + 0.3, y: 3.2, w: 5.38, h: 0.5, fontSize: 17,
    bold: true, color: PAPER, lineSpacing: 21, isTextBox: true, margin: 0,
    objectName: `${key}-l` });
  s.addText(sub, { x: x + 0.3, y: 3.82, w: 5.38, h: 1.0, fontSize: 12,
    color: "AFCBD1", lineSpacing: 15, isTextBox: true, margin: 0,
    objectName: `${key}-s` });
};

panel(0.55, `${nFail} of ${GT.length}`, FAIL, "cannot tell male from female",
  "even where the guideline turns on it. A flat gender gap is blindness, not fairness. "
  + `Only ${nPass} of ten could read the clinical field at all.`, "p1");

panel(6.8, top.timesFloor.toFixed(1) + "×", WARN, "its own noise floor",
  `${top.model} reads the identity label as the sex parameter — and it is the fully open-data model. `
  + "We are not claiming open models are fairer, only that they are the ones we can diagnose.", "p2");

s.addText(`Tier 1, pending clinical validation   ·   prompt set ${F.CURRENT}   ·   ${UP.long}`,
  { x: 0.55, y: 5.4, w: 12.23, h: 0.3, fontSize: 10, color: "6E8C94", italic: true,
    align: "center", isTextBox: true, margin: 0, objectName: "stamp" });

// 20 seconds, about 46 words.
note(s, `[20s] Two answers, and the first surprised us.

${nFail} of ten could not tell male from female even where the guideline turns on it. Among those that could, the worst identity-for-sex substitution is ${top.timesFloor.toFixed(1)} times the model's own floor.

Hold both. The rest of the talk earns them.`);
