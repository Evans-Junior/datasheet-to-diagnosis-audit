// BACKUP 2: the scoring harness in detail. PMI, the two outcomes, and the
// matched floor, each with the failure it exists to prevent.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const GT = F.gateTable();
const FC = F.floorComparison();
const VG = F.vignetteGroups();
const floors = GT.map(r => r.floor);

const s = S("CONTENT", "5 Backup", "Backup: how an option is scored");
K.mark("bk-score");

card(s, { x: 0.55, y: 1.2, w: 6.0, h: 2.9, fill: TINT, name: "pmi",
  kicker: "SCORING", kickerColor: TEAL,
  head: "Pointwise mutual information", headH: 0.3, headSize: 13 });
s.addText("Every option string carries a standing likelihood that has nothing to "
      + "do with the vignette. “Yes” is a more probable token sequence "
      + "than “No” in most contexts, so a model preferring it everywhere "
      + "would look like one that agrees with every clinical proposition.\n\n"
      + "Subtracting the option's log-probability under a content-free prior "
      + "removes that standing preference. Primary key is pmi; mean_logprob and "
      + "sum_logprob are computed for every arm as robustness keys.",
  { x: 0.77, y: 1.96, w: 5.56, h: 1.42, fontSize: 10, color: MUT,
    lineSpacing: 13, valign: "top", isTextBox: true, margin: 0,
    objectName: "pmi-b" });
s.addShape(pres.ShapeType.roundRect, {
  x: 0.77, y: 3.46, w: 5.56, h: 0.44, rectRadius: 0.04,
  fill: { color: PAPER }, line: { color: "C8D7DB", width: 0.75 }, objectName: "fx-bg" });
s.addText("PMI(o) = log P(o | prompt) − log P(o | content-free prior)", {
  x: 0.87, y: 3.46, w: 5.36, h: 0.44, fontSize: 9.5, fontFace: "Courier New",
  color: INK, valign: "middle", isTextBox: true, margin: 0, objectName: "fx" });

card(s, { x: 6.78, y: 1.2, w: 6.0, h: 2.9, fill: TINT, name: "o12",
  kicker: "TWO OUTCOMES, ALWAYS BOTH", kickerColor: TEAL,
  head: "O1 and O2 disagree on purpose", headH: 0.3, headSize: 13, bodySize: 10,
  body: "O1 is probability mass on the guideline-correct answer: is the advice "
      + "right?\n"
      + "O2 is mass on the target option: did the model move toward the "
      + "intervention?\n\n"
      + "On a vignette whose correct answer is “No”, these point in "
      + "opposite directions, so a study that reports one of them inverts the "
      + "sign of its own finding on exactly the items where the guideline says "
      + "to withhold. Both are computed for every arm, and a claim is only made "
      + "where they agree. H1 and H3 are O1 tests; H4 is an O2 test." });

card(s, { x: 0.55, y: 4.24, w: 12.23, h: 2.1, fill: "FDF4E3", name: "floor",
  kicker: "THE MATCHED NUISANCE FLOOR", kickerColor: WARN,
  head: "There is no single floor, and that is the point", headH: 0.3, headSize: 13,
  bodySize: 9,
  body: `Group 4 flips the same identity words on conditions with no documented `
      + `gender disparity, so whatever movement appears there is measurement `
      + `error rather than signal. The floor is computed per model AND matched `
      + `on option count, because a two-option item and a four-option item do `
      + `not have the same noise: ${VG.g4Binary} two-option Group 4 vignettes `
      + `set the floor for two-option items, and ${VG.g4Multi} four-option ones `
      + `set it for the rest.\n`
      + `Measured range across the ten models: ${Math.min(...floors).toFixed(4)} `
      + `to ${Math.max(...floors).toFixed(4)}. A gap that clears one model's `
      + `floor can sit inside another's, so every effect in this deck is `
      + `reported against its own model's floor and never against a pooled one.\n`
      + `The earlier unmatched floor spanned ${FC.oldFloorLo.toFixed(3)} to `
      + `${FC.oldFloorHi.toFixed(3)} and was about ${FC.timesTooHigh.toFixed(1)} `
      + `times too high. All ${FC.nMoved} models moved when it was corrected, `
      + `which is why RQ3 stays exploratory: a null became a trend after a `
      + `change we made ourselves.` });

note(s, "Backup. Turn here for “why PMI”, “why two outcomes”, or “where does the floor come from”.");
