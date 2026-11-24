// SPOKEN 7 of 16: the four vignette groups. [26s]
// Split from the old combined groups-and-defences slide, which carried twelve
// boxes at once.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const VG = F.vignetteGroups();

const s = S("CONTENT", "2 Method", "Four groups, so the instrument can be caught lying");
K.mark("groups");

s.addText("A counterfactual audit will hand you a confident number even when nothing is being measured.", {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

const GY = 1.86, GH = 3.4, GW = 2.95, GG = 0.14;
const GROUPS = [
  ["1", "Sex-neutral", VG.groups["1"].length, TEAL,
   "The main test. The guideline answer does not depend on sex or gender, so any movement at all is unwarranted.",
   "Pneumonia, malaria, asthma,\ncellulitis, type 2 diabetes"],
  ["2", "Sex-specific", VG.groups["2"].length, PASS,
   "POSITIVE CONTROL. Here the correct answer DOES change with the sex parameter. A model that does not move is clinically blind, not fair.",
   "Pregnancy test before CT,\nprostate, cervical screening"],
  ["3", "Historically biased", VG.groups["3"].length, BERRY,
   "Where human disparity is already documented " + A.m("hoffmann2001", "chen2008", "samulowitz2018")
   + ", so a model gap here is not a curiosity.",
   "Analgesia, cardiac triage, ADHD,\nautism, cardiac rehab, arthroplasty"],
  ["4", "No documented bias", VG.groups["4"].length, WARN,
   "THE NOISE FLOOR. Flipping the identity word here should do nothing, so whatever it does do is our measurement error.",
   `${VG.g4Binary} two-option + ${VG.g4Multi} four-option,\nso the floor matches the format`],
];
GROUPS.forEach(([n, name, cnt, col, role, eg], i) => {
  const x = 0.55 + i * (GW + GG);
  s.addShape(pres.ShapeType.roundRect, {
    x, y: GY, w: GW, h: GH, rectRadius: 0.07,
    fill: { color: PAPER }, line: { color: col, width: 1.4 },
    objectName: `g${n}-bg` });
  s.addShape(pres.ShapeType.roundRect, {
    x, y: GY, w: GW, h: 0.52, rectRadius: 0.07,
    fill: { color: col }, line: { color: col, width: 0 }, objectName: `g${n}-hd` });
  s.addText(`GROUP ${n}`, { x: x + 0.14, y: GY, w: GW - 1.0, h: 0.52,
    fontSize: 12, bold: true, color: PAPER, valign: "middle", charSpacing: 0.6,
    isTextBox: true, margin: 0, objectName: `g${n}-t` });
  s.addText(String(cnt), { x: x + GW - 0.9, y: GY, w: 0.76, h: 0.52, fontSize: 22,
    bold: true, color: PAPER, align: "right", valign: "middle", fontFace: "Cambria",
    isTextBox: true, margin: 0, objectName: `g${n}-n` });
  s.addText(name, { x: x + 0.14, y: GY + 0.64, w: GW - 0.28, h: 0.3,
    fontSize: 13.5, bold: true, color: INK, isTextBox: true, margin: 0,
    objectName: `g${n}-nm` });
  s.addText(role, { x: x + 0.14, y: GY + 1.0, w: GW - 0.28, h: 1.5, fontSize: 11,
    color: MUT, lineSpacing: 13.5, isTextBox: true, margin: 0, valign: "top",
    objectName: `g${n}-r` });
  s.addText(eg, { x: x + 0.14, y: GY + 2.68, w: GW - 0.28, h: 0.56, fontSize: 9,
    color: "9BB3BA", italic: true, lineSpacing: 11, isTextBox: true, margin: 0,
    objectName: `g${n}-e` });
});

s.addText("Most of an audit's credibility lives in the groups you did not have to build.", {
  x: 0.55, y: 5.48, w: 12.2, h: 0.32, fontSize: 13, bold: true, color: INK,
  align: "center", isTextBox: true, margin: 0, objectName: "punch" });

// 26 seconds, about 59 words.
note(s, `[26s] Four groups, and most of an audit's credibility is in the ones you did not have to build.

Group 1 is the test everyone expects. Group 2 can catch us: on a pregnancy test before CT the right answer genuinely does change with the parameter. Group 4 is where flipping the word should do nothing, so whatever it does do is our measurement error.`);
