// SPOKEN 8 of 16: the three harness defences. [26s]
// The honest framing is "here are three ways this harness could hand us a
// result that is not real", so each card names the failure before the fix.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const VG = F.vignetteGroups();
const floors = F.gateTable().map(r => r.floor);

const s = S("CONTENT", "2 Method", "Three ways this harness could lie to us");
K.mark("defences");

s.addText("Each of these is a failure we could have shipped without noticing. The fix is underneath it.", {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

const DY = 1.84, DW = 4.0, DG = 0.11, DH = 3.9;

// 1. PMI. Drawn by hand rather than through card(), because card() sizes its
// body box to fill the card and the formula panel would sit inside it.
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: DY, w: DW, h: DH, rectRadius: 0.07, fill: { color: TINT },
  line: { color: TINT, width: 0 }, objectName: "d1-bg" });
s.addText("THE MODEL JUST LIKES THE WORD “YES”", { x: 0.75, y: DY + 0.18,
  w: DW - 0.4, h: 0.24, fontSize: 9.5, bold: true, color: FAIL, charSpacing: 0.6,
  isTextBox: true, margin: 0, objectName: "d1-k" });
s.addText("Score with PMI, not raw likelihood", { x: 0.75, y: DY + 0.46, w: DW - 0.4,
  h: 0.3, fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  objectName: "d1-h" });
s.addText("Every option string carries a standing likelihood that has nothing to do with the vignette. A model that prefers “Yes” everywhere would look like one that agrees with every clinical proposition.",
  { x: 0.75, y: DY + 0.86, w: DW - 0.4, h: 1.1, fontSize: 11, color: MUT,
    lineSpacing: 13.5, valign: "top", isTextBox: true, margin: 0, objectName: "d1-b" });
s.addShape(pres.ShapeType.roundRect, {
  x: 0.75, y: DY + 2.06, w: DW - 0.4, h: 0.62, rectRadius: 0.04,
  fill: { color: PAPER }, line: { color: "C8D7DB", width: 0.75 }, objectName: "d1-f" });
s.addText("PMI(o) = log P(o | prompt)\n            − log P(o | content-free prior)", {
  x: 0.85, y: DY + 2.1, w: DW - 0.6, h: 0.54, fontSize: 9.5,
  fontFace: "Courier New", color: INK, lineSpacing: 12, valign: "middle",
  isTextBox: true, margin: 0, objectName: "d1-fx" });
s.addText("Subtracting the content-free prior removes that standing preference, so a lexical habit cannot read as clinical agreement.",
  { x: 0.75, y: DY + 2.8, w: DW - 0.4, h: 0.9, fontSize: 11, color: MUT,
    lineSpacing: 13.5, valign: "top", isTextBox: true, margin: 0, objectName: "d1-b2" });

// 2. O1 / O2.
card(s, { x: 0.55 + DW + DG, y: DY, w: DW, h: DH, fill: TINT, name: "d2",
  kicker: "A “NO” ANSWER FLIPS THE SIGN", kickerColor: FAIL,
  head: "Score two outcomes, never one", headH: 0.34, headSize: 14, bodySize: 11,
  body: "O1  mass on the guideline-correct answer — is the advice right?\n\n"
      + "O2  mass on the target action — did it move toward the intervention?\n\n"
      + "On a vignette whose correct answer is “No”, those point in "
      + "opposite directions. A study reporting only one inverts the sign of its "
      + "own finding on exactly the items where the guideline says to withhold.\n\n"
      + "Both are computed for every arm, and a claim is only made where they agree." });

// 3. Matched floor.
card(s, { x: 0.55 + 2 * (DW + DG), y: DY, w: DW, h: DH, fill: "FDF4E3", name: "d3",
  kicker: "ANY NUMBER LOOKS LIKE A FINDING", kickerColor: WARN,
  head: "Compare against a matched floor", headH: 0.34, headSize: 14, bodySize: 11,
  body: `Group 4 flips the same identity words on cases with no documented bias, `
      + `so its movement IS the noise.\n\n`
      + `The floor is per model AND matched on option count: ${VG.g4Binary} `
      + `two-option items set the floor for two-option vignettes, `
      + `${VG.g4Multi} four-option items for the rest.\n\n`
      + `Measured range across the ten models:\n`
      + `${Math.min(...floors).toFixed(4)} to ${Math.max(...floors).toFixed(4)}.\n\n`
      + `There is no single floor, and a result is only a result above its own `
      + `model's.` });

// 26 seconds, about 55 words.
note(s, `[26s] Three ways this harness could hand us a result that is not real.

The model might just like the word yes, so we score with PMI and subtract the content-free prior. A "no" answer inverts the sign, so we compute both outcomes and make them agree. And any number looks like a finding until you know the noise.`);
