const K = require("./part1.js");
const F = require("./figures.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// D095. These two tables are a BEFORE and AFTER of the floor correction, so
// they are not symmetric and must not be treated as such:
//
//   the "with the old floor" column is a HISTORICAL RECORD of what the October
//   run reported. It is deliberately left as typed text. Recomputing it would
//   erase the thing the slide exists to show.
//
//   the "with the matched floor" column is a CLAIM ABOUT THE CURRENT DATA, so
//   every figure in it is read from the tables. All four were stale: the median
//   ratio, the H3 margin multiple, the RQ2c ratios and the RQ3 rho.
const _fc = F.floorComparison();
const _gr = F.gateRerun();
const _h3 = F.hypothesis("H3");
const _pt = F.postTraining();
const _sp = F.rq3Spearman();
const _ob = (_fc.byModel[_pt.base] || {}).oldFloor;
const _ot = (_fc.byModel[_pt.tuned] || {}).oldFloor;
const _ptOldTimes = _pt.delta / Math.sqrt(_ob * _ob + _ot * _ot);
const _h3Times = _h3.margin / Math.abs(_h3.delta);
const _rho = v => (v >= 0 ? "+" : "\u2212") + Math.abs(v).toFixed(3);
const _pv = v => (v < 0.001 ? "p < 0.001" : "p = " + v.toFixed(3));

// ============ SECTION: FIX ROUND ================================ //
pres.addSection({ title: "Fix round 1" });
let s = S("SECTION", "Fix round 1", "5.  Instrument fix round 1");
s.addText("3 November 2026. Five interventions, each with a pass criterion written before the run", { placeholder: "body" });

// ============ 29. THE GOVERNANCE RULES ========================== //
s = S("CONTENT", "Fix round 1", "How we changed the instrument without p-hacking");
s.addText("Adjusting an instrument until it works is either good science or p-hacking, and the difference is procedural rather than moral. Four standing rules, written down before the round began.",
  { x: 0.55, y: 1.22, w: 12.2, h: 0.56, fontSize: 13.5, color: INK, margin: 0, isTextBox: true });
const rules = [
  { n: 1, h: "Tune only on Groups 2 and 4", b: "These are the instrument-validation strata and that is their purpose." },
  { n: 2, h: "Groups 1 and 3 stay sealed", b: "They carry H1 to H3. No change may be selected on what it does to them." },
  { n: 3, h: "Criterion before run", b: "Each entry states its pass criterion before execution. One written afterwards is void." },
  { n: 4, h: "Failures are recorded", b: "A failed intervention stays in the log and counts toward the number the paper discloses." },
];
rules.forEach((r, i) => {
  const x = 0.55 + i * 3.1;
  card(s, { x, y: 1.7, w: 2.85, h: 1.9, name: "ru" + i });
  badge(s, { x: x + 0.22, y: 1.88, n: r.n, d: 0.44, fs: 14, name: "rub" + i });
  s.addText(r.h, { x: x + 0.22, y: 2.42, w: 2.42, h: 0.52, fontSize: 13, bold: true,
    color: INK, lineSpacing: 16, margin: 0, isTextBox: true, objectName: "ruh" + i });
  s.addText(r.b, { x: x + 0.22, y: 2.96, w: 2.42, h: 0.56, fontSize: 11.5, color: MUT,
    lineSpacing: 14, margin: 0, isTextBox: true, objectName: "rubb" + i });
});
card(s, { x: 0.55, y: 3.76, w: 6.0, h: 1.3, fill: TINT, kicker: "CORRECTNESS FIX OR TUNING", kickerColor: TEAL, name: "cls" });
s.addText("A change either repairs a demonstrable error, justified without reference to any outcome, or it is a judgement call among valid options. Only the second kind spends the disclosed budget.",
  { x: 0.77, y: 4.3, w: 5.56, h: 0.68, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
card(s, { x: 6.75, y: 3.76, w: 6.0, h: 1.3, fill: "FDF3E3", kicker: "BUDGET USED THIS ROUND", kickerColor: WARN, name: "bud" });
s.addText([{ text: "1 tuning item. ", options: { bold: true, color: INK, fontSize: 13 } },
  { text: "Three correctness fixes landed, one tuning item was spent and failed, and one diagnostic returned a negative result worth publishing.", options: { color: MUT, fontSize: 11.5 } }],
  { x: 6.97, y: 4.3, w: 5.56, h: 0.68, fontSize: 11.5, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.22, w: 12.2, h: 1.2, fill: "FBEEEC", kicker: "THE HONEST LIMITATION ON RULE 2, STATED BECAUSE A READER WOULD OTHERWISE HAVE TO TRUST US",
  kickerColor: FAIL, name: "hon" });
s.addText("The pre-registered Group 3 analysis was run and inspected before this log was opened, so the sealed-data rule cannot be claimed retrospectively. The protection in force is weaker: every criterion is defined on Group 2 and Group 4 quantities only, and both pre-fix and post-fix values are published side by side. The reader can see what the change did rather than being asked to trust us.",
  { x: 0.77, y: 5.74, w: 11.76, h: 0.62, fontSize: 12, color: INK, lineSpacing: 15, margin: 0, isTextBox: true });
note(s, "This slide is the project's answer to the most dangerous question a marker can ask about the fix round, which is whether we tuned until we liked the answer. The procedure is the answer, and the limitation on rule 2 is stated because it is real.");

// ============ 30. THE FIVE INTERVENTIONS ======================== //
s = S("CONTENT", "Fix round 1", "The five interventions, and what each one returned");
const iRows = [[
  { text: "", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11 } },
  { text: "Intervention", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11 } },
  { text: "Class", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11 } },
  { text: "Criterion, fixed before the run", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11 } },
  { text: "Outcome", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11 } },
]];
[
  ["I1", "Matched-geometry noise floor", "correctness",
   `Floor moves more than 25 percent for a majority of ${_fc.n} models`,
   `PASS   ${_fc.nMoved} of ${_fc.n}, median ratio ${_fc.medianRatio.toFixed(3)}`, PASS],
  ["I2", "Score-key collapse", "correctness", "Sum and mean floors differ by less than 1e-9 on the binary stratum", "PASS   difference exactly 0", PASS],
  ["I3", "Pythia elicitation", "tuning", "At least 2 of 7 Pythia models above their own matched floor", "FAIL   0 of 7, 1 of 7, 1 of 7", FAIL],
  ["I4", "RQ4 identifiability", "diagnostic", "At least 6 concepts disagreeing by more than 0.5 log2", "NOT IDENTIFIABLE   0 qualify", FAIL],
  ["I5", "Circularity that I1 created", "correctness", "None. Unplanned, found during review", "REAL   H3 survives it", WARN],
].forEach((r, i) => iRows.push([
  { text: r[0], options: { bold: true, color: TEAL, fontSize: 12, fontFace: "Courier New", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { bold: true, color: INK, fontSize: 11, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { color: r[2] === "tuning" ? WARN : MUT, fontSize: 10.5, italic: true, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[3], options: { color: MUT, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[4], options: { bold: true, color: r[5], fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(iRows, { x: 0.55, y: 1.25, w: 12.2, colW: [0.6, 3.1, 1.3, 4.3, 2.9], rowH: 0.56,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.1, 0.06, 0.1], fontFace: "Calibri", autoPage: false });

card(s, { x: 0.55, y: 4.55, w: 6.0, h: 1.86, fill: TINT, kicker: "A PRE-REGISTRATION GAP WE HIT", kickerColor: WARN, name: "gap" });
s.addText("The I3 criterion did not name a score key, and the keys disagree. We resolved it to the key already prespecified in the code long before this round, and logged that the ambiguity was noticed after the five small models reported and before the two large ones did. Under the other key, few-shot would have scored 2 of 7 and passed. That is exactly why the conservative reading is the one adopted.",
  { x: 0.77, y: 5.09, w: 5.56, h: 1.2, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 4.55, w: 6.0, h: 1.86, fill: TINT, kicker: "I5: WE BROKE SOMETHING AND FOUND IT", kickerColor: WARN, name: "i5c" });
s.addText("I1 made H3's equivalence margin circular, because H3's preregistered vignette set includes the Group 4 items the new floor is built from. It was caught by asking why the margin came out as 0.0131 rather than 0.0117. H3 was not redefined, three variants were published, and H3 is supported on all three.",
  { x: 6.97, y: 5.09, w: 5.56, h: 1.2, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
note(s, "Five rows, two of which went against us. The I3 failure and the I4 negative result are both in the log permanently. The paper will disclose that one tuning item was spent, which is what converts an adaptive search into a defensible one.");

// ============ 31. THE FOUR DOWNSTREAM CHANGES =================== //
s = S("CONTENT_DARK", "Fix round 1", "What the correction moved, including against us");
s.addText("A floor measured on the wrong stimulus fed four downstream results. Correcting it changed all four.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.32, fontSize: 13.5, color: "BCD3D8", margin: 0, isTextBox: true });
const dRows = [[
  { text: "Result", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12 } },
  { text: "With the old floor", options: { bold: true, color: "C8B4AE", fill: { color: "1C4E59" }, fontSize: 12 } },
  { text: "With the matched floor", options: { bold: true, color: "7FD4C8", fill: { color: "1C4E59" }, fontSize: 12 } },
  { text: "Reading", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12 } },
]];
[
  ["Gate, Group 2", `${_gr.oldPasses} of ${_gr.n} models pass`,
   `${_gr.newPasses} of ${_gr.n} models pass`, "Opens the open-data family", PASS],
  ["H3 equivalence", "supported, margin 68x the effect",
   `${_h3.tost ? "supported" : "NOT supported"}, margin `
   + `${_h3Times.toFixed(0)}x the effect`, "Same verdict, real margin", PASS],
  ["RQ2c post-training", "0.38x, inside the floor",
   `${_ptOldTimes.toFixed(2)}x old floor, ${_pt.timesFloor.toFixed(2)}x matched`,
   _ptOldTimes < 1 ? "Conclusion reverses" : "Withdrawn twice over", WARN],
  ["RQ3 size trend", "rho -0.030, p = 0.93",
   `rho ${_rho(_sp.spearman_rho)}, ${_pv(_sp.spearman_p)}`,
   "Null becomes a trend, in our favour", FAIL],
].forEach((r, i) => dRows.push([
  { text: r[0], options: { bold: true, color: PAPER, fontSize: 11.5, fill: { color: i % 2 ? "133F49" : INK } } },
  { text: r[1], options: { color: "C8B4AE", fontSize: 11.5, fill: { color: i % 2 ? "133F49" : INK } } },
  { text: r[2], options: { bold: true, color: PAPER, fontSize: 11.5, fill: { color: i % 2 ? "133F49" : INK } } },
  { text: r[3], options: { bold: true, color: r[4], fontSize: 11, fill: { color: i % 2 ? "133F49" : INK } } },
]));
s.addTable(dRows, { x: 0.55, y: 1.62, w: 12.2, colW: [2.7, 3.3, 3.3, 2.9], rowH: 0.62,
  border: { type: "solid", color: "2A5E6A", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.12, 0.06, 0.12], fontFace: "Calibri", autoPage: false });

card(s, { x: 0.55, y: 4.56, w: 12.2, h: 1.86, fill: "1C4E59", kicker: "THE READER'S SUMMARY, WHICH WE GIVE BEFORE WE ARE ASKED FOR IT",
  kickerColor: "7FD4C8", name: "sumr" });
s.addText([
  { text: "Of the four changes, one is a straightforward improvement in H3's margin, one opens the gate for the family the project most needs, ", options: { color: "D6E6E9" } },
  { text: "one reverses a conclusion we had already published and does so against the simpler story, ", options: { bold: true, color: WARN } },
  { text: "and one turns a null into a positive finding in a way that happens to favour us. ", options: { bold: true, color: "E9A79C" } },
  { text: "The fourth is the one to treat with most caution, and it is flagged as such everywhere it is reported.", options: { color: PAPER } },
], { x: 0.77, y: 5.1, w: 11.76, h: 1.16, fontSize: 13, lineSpacing: 17, margin: 0, isTextBox: true });
note(s, "Presenting the two results that went against us before anyone asks is the strongest available move. The RQ2c reversal cost us a published conclusion and the RQ3 change benefits us, so flagging the second more loudly than the first is the honest asymmetry.");

module.exports = {};
