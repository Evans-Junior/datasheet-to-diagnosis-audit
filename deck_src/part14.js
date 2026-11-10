const K = require("./part1.js");
const F = require("./figures.js");   // D096: the RQ5 probe counts
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 34. WHAT WOULD CHANGE OUR MIND ==================== //
let s = S("CONTENT_DARK", "Limitations and conclusions", "What would change our mind, stated in advance");
s.addText("Each deliverable has a success criterion that does not depend on the result going our way. A project whose success requires finding bias has an incentive to find it.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.36, fontSize: 13.5, color: "BCD3D8", margin: 0, isTextBox: true });
const judge = [[
  { text: "Deliverable", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 11.5 } },
  { text: "How we judge it, decided before the result", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 11.5 } },
]];
[
  ["A clinician-verified stimulus set", "Every item carries a sourced reference answer and a clinician ruling. Success is a complete record including the rejection rate, which is itself evidence about the method"],
  ["A re-run audit on verified items", "Success is a before-and-after comparison reported in full, whether or not the verdicts change"],
  ["A corpus-to-output linkage test", "A matched result reported alongside its crossed control. A matched correlation without the control is a failure even if it is positive"],
  ["A documentation analysis", "Independent coding by both authors against a written codebook, with inter-coder agreement reported whatever it turns out to be"],
  ["An account of the instrument's limits", "A measured floor and a stated resolution limit for every claim, so a reader can tell a null from a blindness"],
].forEach((r, i) => judge.push([
  { text: r[0], options: { bold: true, color: PAPER, fontSize: 11.5, fill: { color: i % 2 ? "133F49" : INK } } },
  { text: r[1], options: { color: "BCD3D8", fontSize: 11.5, fill: { color: i % 2 ? "133F49" : INK } } },
]));
s.addTable(judge, { x: 0.55, y: 1.64, w: 12.2, colW: [3.6, 8.6], rowH: 0.58,
  border: { type: "solid", color: "2A5E6A", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.12, 0.06, 0.12], fontFace: "Calibri", autoPage: false });

card(s, { x: 0.55, y: 4.78, w: 6.0, h: 1.64, fill: "3A1F24", kicker: "WE WITHDRAW, NOT REINTERPRET", kickerColor: "E9A79C", name: "wd1" });
s.addText("If the clinician review rejects a substantial share of the reference answers, the vignette set is not valid and the audit results are withdrawn rather than reinterpreted.",
  { x: 0.77, y: 5.32, w: 5.56, h: 0.96, fontSize: 12.5, color: PAPER, lineSpacing: 16, margin: 0, isTextBox: true });
card(s, { x: 6.75, y: 4.78, w: 6.0, h: 1.64, fill: "3A1F24", kicker: "THE EXPLORATORY FINDING IS NOT PROTECTED", kickerColor: "E9A79C", name: "wd2" });
s.addText("If the identity and sex-parameter merging does not survive the re-run on verified items, it is reported as not surviving. It is currently our most interesting result and it has no special status.",
  { x: 6.97, y: 5.32, w: 5.56, h: 0.96, fontSize: 12.5, color: PAPER, lineSpacing: 16, margin: 0, isTextBox: true });
note(s, "Stating the withdrawal conditions in advance is the strongest possible answer to the question of whether we are motivated to find bias. The exploratory finding is the one we would most want to keep, which is exactly why it is named here.");

// ============ 35. CONCLUSIONS =================================== //
s = S("CONTENT", "Limitations and conclusions", "Conclusions");
const conc = [
  { n: 1, h: "The chain can be built, and it does not yet close", b: "A datasheet, a corpus measurement, a validated instrument and a pre-registered analysis can be connected end to end in one repository. The link that fails is provenance attribution, and it fails for a measurable reason rather than a practical one.", c: TEAL },
  { n: 2, h: "Open training data is necessary but not sufficient", b: "This is uncomfortable for the simple version of our own policy argument, and it is the honest result. The corpora are inspectable and the models trained on them are too insensitive to audit by this method, while the model that passes the gate most convincingly is the one whose data nobody can inspect.", c: BERRY },
  { n: 3, h: "The instrument was the binding constraint, not the models", b: "A noise floor measured on the wrong stimulus was deciding our headline result. Finding that changed the gate from one model to three, reversed one published conclusion and turned one null into a trend. The lesson generalises: an audit that does not measure its own floor on matched geometry cannot tell a null from a blindness.", c: WARN },
  { n: 4, h: "The clearest ethics finding needs no statistics at all", b: `Non-binary people appear over ${F.rq5Probe().bareMaxMillions} million times in ${F.rq5Probe().bareMaxCorpus} and never once in the clinical subject position, while two of our source guidelines require care for them by name. The clinical guidance is more inclusive than the training data can support.`, c: FAIL },
];
conc.forEach((c, i) => {
  const y = 1.26 + i * 1.33;
  card(s, { x: 0.55, y, w: 12.2, h: 1.2, name: "cc" + i });
  badge(s, { x: 0.78, y: y + 0.36, n: c.n, d: 0.48, fs: 15, color: c.c, name: "ccb" + i });
  s.addText(c.h, { x: 1.42, y: y + 0.14, w: 11.1, h: 0.32, fontSize: 14.5, bold: true,
    color: c.c, margin: 0, isTextBox: true, objectName: "cch" + i });
  s.addText(c.b, { x: 1.42, y: y + 0.48, w: 11.1, h: 0.64, fontSize: 11.5, color: MUT,
    lineSpacing: 14, margin: 0, isTextBox: true, objectName: "ccbb" + i });
});
card(s, { x: 0.55, y: 6.6, w: 12.2, h: 0.42, fill: INK, name: "ccf" });
s.addText("The contribution is a working instrument, a pre-registered null reported as a null, and a measured account of exactly where the datasheet to diagnosis chain breaks.",
  { x: 0.77, y: 6.66, w: 11.76, h: 0.3, fontSize: 12, bold: true, color: PAPER, margin: 0, isTextBox: true });
note(s, "Conclusion 2 is the one to deliver carefully. It undercuts the simple version of the open-data argument, and saying so first is far stronger than being caught by it. Conclusion 4 is the one to end on if time is short.");

module.exports = {};
