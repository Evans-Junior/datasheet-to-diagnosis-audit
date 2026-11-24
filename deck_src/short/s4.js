// SHORT deck, slide 4: the four groups and the three harness defences.
//
// The argument: a counterfactual audit can produce a confident number from a
// completely broken instrument, so the design has to make the instrument
// falsifiable. Group 2 can catch us reading nothing; Group 4 tells us how big
// a difference has to be before it means anything; PMI and the O1/O2 split
// close the two ways the scoring harness could manufacture a result.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const VG = F.vignetteGroups();
const GT = F.gateTable();
const floors = GT.map(r => r.floor);
const floorLo = Math.min(...floors), floorHi = Math.max(...floors);

const s = S("CONTENT", "2 Method",
  "Four groups, so the instrument can be caught lying");
K.mark("instrument");

s.addText("A counterfactual audit will hand you a confident number even when nothing is being measured. These are the checks that make that detectable.", {
  x: 0.55, y: 1.14, w: 12.2, h: 0.26, fontSize: 12, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

// ---------------------------------------------------------- four groups ----
const GY = 1.72, GH = 1.96, GW = 2.95, GG = 0.14;
const GROUPS = [
  ["1", "Sex-neutral", VG.groups["1"].length, TEAL,
   "The main test. The guideline answer does not depend on sex or gender, so any movement is unwarranted.",
   "Pneumonia, malaria, asthma,\ncellulitis, type 2 diabetes"],
  ["2", "Sex-specific", VG.groups["2"].length, PASS,
   "POSITIVE CONTROL. Here the correct answer DOES change with the sex parameter. A model that does not move is clinically blind.",
   "Pregnancy test before CT,\nprostate, cervical screening"],
  ["3", "Historically biased", VG.groups["3"].length, BERRY,
   "Where human disparity is documented " + A.m("hoffmann2001", "chen2008", "samulowitz2018")
   + ", so a model gap is not a curiosity.",
   "Analgesia, cardiac triage, ADHD,\nautism, cardiac rehab, arthroplasty"],
  ["4", "No documented bias", VG.groups["4"].length, WARN,
   `THE NOISE FLOOR. Flipping the identity word here should do nothing, so whatever it does do is the measurement error.`,
   `${VG.g4Binary} two-option + ${VG.g4Multi} four-option,\nso the floor matches the format`],
];
GROUPS.forEach(([n, name, cnt, col, role, eg], i) => {
  const x = 0.55 + i * (GW + GG);
  s.addShape(pres.ShapeType.roundRect, {
    x, y: GY, w: GW, h: GH, rectRadius: 0.06,
    fill: { color: PAPER }, line: { color: col, width: 1.25 },
    objectName: `g${n}-bg` });
  s.addShape(pres.ShapeType.roundRect, {
    x, y: GY, w: GW, h: 0.4, rectRadius: 0.06,
    fill: { color: col }, line: { color: col, width: 0 }, objectName: `g${n}-hd` });
  s.addText(`GROUP ${n}  ·  ${name}`, { x: x + 0.12, y: GY, w: GW - 0.9, h: 0.4,
    fontSize: 10.5, bold: true, color: PAPER, valign: "middle", isTextBox: true,
    margin: 0, objectName: `g${n}-t` });
  s.addText(String(cnt), { x: x + GW - 0.78, y: GY, w: 0.66, h: 0.4, fontSize: 17,
    bold: true, color: PAPER, align: "right", valign: "middle", fontFace: "Cambria",
    isTextBox: true, margin: 0, objectName: `g${n}-n` });
  s.addText(role, { x: x + 0.12, y: GY + 0.48, w: GW - 0.24, h: 0.94, fontSize: 9.5,
    color: MUT, lineSpacing: 11.5, isTextBox: true, margin: 0, valign: "top",
    objectName: `g${n}-r` });
  s.addText(eg, { x: x + 0.12, y: GY + 1.48, w: GW - 0.24, h: 0.4, fontSize: 8,
    color: "9BB3BA", italic: true, lineSpacing: 9.5, isTextBox: true, margin: 0,
    objectName: `g${n}-e` });
});

// ----------------------------------------------------- harness defences ----
const DY = 4.06;
s.addText("THREE WAYS THE SCORING HARNESS COULD MANUFACTURE A RESULT", {
  x: 0.55, y: DY - 0.26, w: 12.2, h: 0.2, fontSize: 8, bold: true, color: MUT,
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "dk" });

const DW = 4.0, DG = 0.11, DH = 2.34;

// 1. PMI.
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: DY, w: DW, h: DH, rectRadius: 0.06, fill: { color: TINT },
  line: { color: TINT, width: 0 }, objectName: "d1-bg" });
s.addText("THE MODEL JUST LIKES THE WORD “YES”", { x: 0.72, y: DY + 0.13,
  w: DW - 0.34, h: 0.2, fontSize: 8.5, bold: true, color: FAIL, charSpacing: 0.6,
  isTextBox: true, margin: 0, objectName: "d1-k" });
s.addText("Score with PMI, not raw likelihood", { x: 0.72, y: DY + 0.35, w: DW - 0.34,
  h: 0.24, fontSize: 12, bold: true, color: INK, isTextBox: true, margin: 0,
  objectName: "d1-h" });
s.addShape(pres.ShapeType.roundRect, {
  x: 0.72, y: DY + 0.64, w: DW - 0.34, h: 0.56, rectRadius: 0.04,
  fill: { color: PAPER }, line: { color: "C8D7DB", width: 0.75 }, objectName: "d1-f" });
s.addText("PMI(o) = log P(o | prompt)\n            − log P(o | content-free prior)", {
  x: 0.82, y: DY + 0.68, w: DW - 0.54, h: 0.48, fontSize: 9,
  fontFace: "Courier New", color: INK, lineSpacing: 11, isTextBox: true,
  margin: 0, valign: "middle", objectName: "d1-fx" });
s.addText("Subtracting the content-free prior removes the model's standing preference for an option string, so a lexical habit cannot read as clinical agreement.", {
  x: 0.72, y: DY + 1.28, w: DW - 0.34, h: 0.92, fontSize: 9, color: MUT,
  lineSpacing: 11, isTextBox: true, margin: 0, valign: "top", objectName: "d1-b" });

// 2. O1 / O2.
card(s, { x: 0.55 + DW + DG, y: DY, w: DW, h: DH, fill: TINT, name: "d2",
  kicker: "A “NO” ANSWER FLIPS THE SIGN", kickerColor: FAIL,
  head: "Score two outcomes, never one", headH: 0.3, headSize: 12, bodySize: 9,
  body: "O1  mass on the guideline-correct answer — is the advice right?\n"
      + "O2  mass on the target action — did it move toward the intervention?\n\n"
      + "On a vignette whose correct answer is “No”, those point in opposite "
      + "directions. Reporting only one inverts the sign of the finding, so both "
      + "are computed for every arm and must agree before anything is claimed." });

// 3. Matched floor.
card(s, { x: 0.55 + 2 * (DW + DG), y: DY, w: DW, h: DH, fill: "FDF4E3", name: "d3",
  kicker: "ANY NUMBER LOOKS LIKE A FINDING", kickerColor: WARN,
  head: "Compare against a matched floor", headH: 0.3, headSize: 12, bodySize: 9,
  body: `Group 4 flips the same identity words on cases with no documented bias, `
      + `so its movement IS the noise. The floor is per model and matched on `
      + `option count — ${VG.g4Binary} two-option items set the floor for `
      + `two-option vignettes, ${VG.g4Multi} four-option items for the rest.\n\n`
      + `Measured range across the ten models: ${floorLo.toFixed(4)} to `
      + `${floorHi.toFixed(4)}. There is no single floor, and a result is only a `
      + `result above its own model's.` });

// 60 seconds, about 135 words.
note(s, `[60s] Do not read the twelve boxes. Two points.

Top row. Most of an audit's credibility is in the groups you did not have to build. Group 1 is the test everyone expects. Group 2 can catch us: on a pregnancy test before CT the right answer genuinely does change with the parameter, so a model that answers the same either way has failed to read the field. Group 4 is where flipping the word should do nothing, so whatever it does do is our measurement error.

Bottom row: three ways this harness could hand us a result that is not real. The model might just like the word yes, so we use PMI. A "no" answer inverts the sign, so we score two outcomes. And any number looks like a finding until you know the noise.`);
