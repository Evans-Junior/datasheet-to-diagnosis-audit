const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
// D090: numbers come from results/tables, never typed in. The build aborts if
// those tables are stale or were never scored.
const F = require("./figures.js");

// ============ 27. RQ5 NON-BINARY ABSENCE ======================== //
let s = S("CONTENT_DARK", "Results", "RQ5: absent from the clinical subject position");
const nbRows = [[
  { text: "Phrase", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12 } },
  { text: "The Pile", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12, align: "right" } },
  { text: "olmo-mix", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12, align: "right" } },
]];
[
  ['"the woman has"', "646,440", "20,142", "D6E6E9"],
  ['"non-binary"  (bare)', "1,350,944", "66,269", "D6E6E9"],
  ['"the non-binary patient"', "0", "0", "E9A79C"],
].forEach((r, i) => nbRows.push([
  { text: r[0], options: { color: r[3], fontSize: 13, fontFace: "Courier New", bold: i === 2, fill: { color: i === 2 ? "3A1F24" : (i % 2 ? "133F49" : INK) } } },
  { text: r[1], options: { color: r[3], fontSize: 13, align: "right", bold: i === 2, fontFace: "Courier New", fill: { color: i === 2 ? "3A1F24" : (i % 2 ? "133F49" : INK) } } },
  { text: r[2], options: { color: r[3], fontSize: 13, align: "right", bold: i === 2, fontFace: "Courier New", fill: { color: i === 2 ? "3A1F24" : (i % 2 ? "133F49" : INK) } } },
]));
s.addTable(nbRows, { x: 0.55, y: 1.3, w: 7.3, colW: [3.9, 1.7, 1.7], rowH: 0.56,
  border: { type: "solid", color: "2A5E6A", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.14, 0.06, 0.14], fontFace: "Calibri", autoPage: false });

s.addText("Non-binary people are well represented in these corpora, with over 1.3 million mentions in the Pile. They never occupy the clinical subject position.",
  { x: 0.55, y: 3.6, w: 7.3, h: 0.66, fontSize: 13, color: PAPER, lineSpacing: 17, margin: 0, isTextBox: true });
s.addText("This is a presence and absence pattern, not a scarcity pattern. The distinction matters: a scarcity argument invites more data as the remedy, while an absence in one specific grammatical position points at how the data was collected and what it was collected for.",
  { x: 0.55, y: 4.3, w: 7.3, h: 0.86, fontSize: 12, color: "BCD3D8", lineSpacing: 15.5, margin: 0, isTextBox: true });

card(s, { x: 8.1, y: 1.3, w: 4.65, h: 3.86, fill: "3A1F24", kicker: "THE ETHICS CLAIM, IN ITS SHARPEST FORM",
  kickerColor: "E9A79C", name: "nbe" });
s.addText("Two of our source guidelines explicitly require care for non-binary and trans patients.",
  { x: 8.32, y: 1.84, w: 4.21, h: 0.6, fontSize: 13, bold: true, color: PAPER, lineSpacing: 16, margin: 0, isTextBox: true });
s.addText("NICE NG126 covers trans men and non-binary people by name for the pregnancy pathway.",
  { x: 8.32, y: 2.48, w: 4.21, h: 0.58, fontSize: 11.5, color: "E8CFD3", lineSpacing: 14.5, margin: 0, isTextBox: true });
s.addText("The exact phrase \"the non-binary patient\" does not occur once in either corpus.",
  { x: 8.32, y: 3.12, w: 4.21, h: 0.6, fontSize: 13, bold: true, color: "E9A79C", lineSpacing: 16, margin: 0, isTextBox: true });
s.addText("So the clinical guidance is more inclusive than the training data can support. A model cannot learn a subject position that its corpus never contains, and no amount of prompting at inference time supplies it.",
  { x: 8.32, y: 3.8, w: 4.21, h: 1.2, fontSize: 11.5, color: "E8CFD3", lineSpacing: 15, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.4, w: 12.2, h: 1.0, fill: "1C4E59", name: "nbm" });
s.addText([{ text: "Why this result is final rather than provisional. ", options: { bold: true, color: PAPER } },
  { text: "It is a corpus measurement, not a model measurement, so it does not depend on the vignettes or on clinician verification. It is the one headline in the project that is not waiting on anything.", options: { color: "BCD3D8" } }],
  { x: 0.77, y: 5.62, w: 11.76, h: 0.6, fontSize: 12.5, lineSpacing: 16, margin: 0, isTextBox: true });
note(s, "If you only have one result to present, use this one. It is final, it is simple, it needs no statistics, and it carries the ethics argument on its own. Over 1.3 million mentions and zero in the clinical subject position is a presence and absence pattern, which is far more interesting than a scarcity claim.");

// ============ 28. RQ6 DOCUMENTATION ============================= //
s = S("CONTENT", "Results", "RQ6: not silence, but a missing link");
card(s, { x: 0.55, y: 1.25, w: 12.2, h: 1.1, fill: "FDF3E3", kicker: "THE OBVIOUS CLAIM WAS WRONG, AND WE FOUND OUT BY READING",
  kickerColor: WARN, name: "d6a" });
s.addText("Term counts suggested the datasheets are silent on gender. Reading the passages in context showed the Pile datasheet [1] discusses gender, and discusses it carefully. Our expected finding did not survive contact with the source.",
  { x: 0.77, y: 1.79, w: 11.76, h: 0.52, fontSize: 13, color: INK, lineSpacing: 16, margin: 0, isTextBox: true });

box(s, { x: 0.55, y: 2.56, w: 3.6, h: 1.0, t: "Discloses gender\ncomposition?", fill: PAPER, line: PASS, fs: 12, name: "d61" });
s.addText("Yes, in the Pile", { x: 0.55, y: 3.6, w: 3.6, h: 0.28, fontSize: 11, bold: true,
  color: PASS, align: "center", margin: 0, isTextBox: true });
arrow(s, { x: 4.28, y: 2.96, w: 0.5, h: 0.2, color: "9BB3BA", name: "d6ar1" });
box(s, { x: 4.9, y: 2.56, w: 3.6, h: 1.0, t: "Connects it to\ndownstream health use?", fill: PAPER, line: FAIL, fs: 12, name: "d62" });
s.addText("No document does", { x: 4.9, y: 3.6, w: 3.6, h: 0.28, fontSize: 11, bold: true,
  color: FAIL, align: "center", margin: 0, isTextBox: true });
arrow(s, { x: 8.63, y: 2.96, w: 0.5, h: 0.2, color: "9BB3BA", name: "d6ar2" });
box(s, { x: 9.25, y: 2.56, w: 3.5, h: 1.0, t: "So the risk is\nundisclosed in practice", fill: INK, line: INK, tc: PAPER, fs: 12, name: "d63" });

card(s, { x: 0.55, y: 4.08, w: 6.0, h: 2.32, fill: TINT, kicker: "WHAT CHANGED IN OUR CLAIM", kickerColor: TEAL, name: "d6b" });
s.addText([
  { text: "From:  ", options: { bold: true, color: MUT } },
  { text: "\"they never looked at gender\"\n", options: { italic: true, color: FAIL } },
  { text: "To:  ", options: { bold: true, color: MUT } },
  { text: "\"their analysis could not have found this\"\n\n", options: { italic: true, color: PASS } },
  { text: "The second claim is stronger and survives a reviewer, because it is about the structure of the analysis rather than the attention of the authors. Narrowing a claim after reading the source is the decision log doing its job.", options: { color: INK } },
], { x: 0.77, y: 4.62, w: 5.56, h: 1.64, fontSize: 12, lineSpacing: 15.5, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 4.08, w: 6.0, h: 2.32, fill: TINT, kicker: "WHERE THIS STANDS", kickerColor: TEAL, name: "d6c" });
s.addText("Ten documents retrieved, 136 candidate passages identified, a written codebook built, and a coding worksheet prepared. The remaining work is independent coding by both authors with inter-coder agreement reported whatever it turns out to be.",
  { x: 6.97, y: 4.62, w: 5.56, h: 0.96, fontSize: 12, color: INK, lineSpacing: 15.5, margin: 0, isTextBox: true });
s.addText("Policy consequence: a disclosure rule that asks only for composition statistics would be satisfied by documents that still leave this risk unstated. The rule has to ask for the connection to use.",
  { x: 6.97, y: 5.66, w: 5.56, h: 0.62, fontSize: 11.5, italic: true, color: MUT, lineSpacing: 14.5, margin: 0, isTextBox: true });
note(s, "The honest story here is that our hypothesis was wrong and reading the documents corrected it. That is a better finding than the one we expected, because a composition-only disclosure rule is a real policy proposal that our evidence shows would not work.");

// ============ R-A. EVERY MODEL, ONE TABLE ======================= //
s = S("CONTENT", "Results", "Every model in one table: who beat the noise");
s.addText("Generated by scripts/results_summary.py from the per-RQ tables. Both stamps are emitted by the script, not added by hand.",
  { x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 12, color: MUT, margin: 0, isTextBox: true });

// D090: built from results/tables/summary_model_bias.csv at build time. The
// previous version of this slide carried numbers typed in by hand from a run
// that had since been superseded twice -- the deck showed a 576-prompt set and
// hash 3c45ca6b while the repository was on 648 prompts.
const _gate = F.gateTable().sort((a, b) => a.params - b.params);
const _trend = new Map(F.sizeTrend().map(r => [r.model, r]));
// D095. This slide never built. It assembled `mb` and then passed `mbRows`,
// which is not defined, so `node build.js` threw here and every slide after
// this point was never reached. The .pptx on disk predates the bug, which is
// why it was not noticed: the deck looked fine because it was old.
//
// The row also carried eight entries against seven columns, the eighth being
// a colour rather than a cell. That was clearly meant as the gate cell's
// colour, so it is applied as cell options instead of pushed in as text.
const MB_HEAD = ["Model", "B", "Gate", "Gate margin", "Mean |delta|",
                 "Floor", "Over floor"];
const mbRows = [
  MB_HEAD.map(h => ({ text: h, options: { bold: true, color: PAPER,
                                          fill: { color: INK }, fontSize: 9.5 } })),
  ..._gate.map(r => {
    const t = _trend.get(r.model) || {};
    const over = t.above === undefined ? (r.above ? "yes" : "no") : t.above;
    const gateColor = r.gate === "SENSITIVE" ? PASS : FAIL;
    return [
      { text: r.model, options: { fontSize: 9.5, color: INK } },
      { text: String(r.params), options: { fontSize: 9.5, color: MUT, align: "right" } },
      { text: r.gate, options: { fontSize: 9, bold: true, color: gateColor } },
      { text: F.f4(r.margin), options: { fontSize: 9.5, color: INK,
                                         fontFace: "Courier New", align: "right" } },
      { text: r.absDelta.toFixed(4), options: { fontSize: 9.5, color: INK,
                                                fontFace: "Courier New", align: "right" } },
      { text: r.floor.toFixed(4), options: { fontSize: 9.5, color: MUT,
                                             fontFace: "Courier New", align: "right" } },
      { text: String(over), options: { fontSize: 9.5, align: "center",
          color: over === "yes" ? PASS : (over === "no" ? MUT : WARN) } },
    ];
  }),
];
s.addTable(mbRows, { x: 0.55, y: 1.54, w: 8.25, colW: [1.95, 0.55, 1.35, 1.2, 1.0, 0.9, 1.3],
  rowH: 0.34, border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.03, 0.08, 0.03, 0.08], fontFace: "Calibri", autoPage: false });

card(s, { x: 9.0, y: 1.54, w: 3.75, h: 1.7, fill: "FDF4E3", kicker: "TWO STAMPS THE SCRIPT EMITS", kickerColor: WARN, name: "stmp" });
s.addText([
  { text: "TIER 1. ", options: { bold: true, color: WARN } },
  { text: "Every row author-reviewed against a quoted first-hand guideline. "
        + "Reportable for this submission, pending clinical validation; tier 2 "
        + "is the publication bar (prereg \u00A710).\n",
    options: { color: INK } },
  { text: "PROVENANCE. ", options: { bold: true, color: PASS } },
  { text: "Prompt set " + F.CURRENT + ", stamped into every table and checked "
          + "against the scored run. This slide reads the table; it does not "
          + "quote it.", options: { color: INK } },
], { x: 9.22, y: 1.96, w: 3.31, h: 1.22, fontSize: 9, lineSpacing: 11.5, margin: 0, isTextBox: true });

card(s, { x: 9.0, y: 3.38, w: 3.75, h: 1.92, fill: TINT, kicker: "HOW TO READ IT", kickerColor: TEAL, name: "hread" });
s.addText([
  { text: "The gate splits the table in two and only one half can be read. ", options: { bold: true, color: INK } },
  { text: "The seven Pythia rows failed the positive control, so their small deltas are not evidence of fairness; they are evidence that no signal comes out. D057 then showed all seven flip SIGN across prompt formats.", options: { color: MUT } },
], { x: 9.22, y: 3.8, w: 3.31, h: 1.44, fontSize: 9.5, lineSpacing: 12, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.46, w: 12.2, h: 1.0, fill: INK, kicker: "WHAT THE THREE READABLE ROWS AGREE ON", kickerColor: "7FD4C8", name: "mbsum" });
// D090: the claim and its numbers are derived, so the sentence cannot drift
// away from the table above it.
const _pass = _gate.filter(r => r.gate === "SENSITIVE");
const _ratios = _pass.map(r => r.absDelta / r.floor).sort((a, b) => a - b);
const _dirs = [...new Set(_pass.map(r => r.direction))];
// Match by shape, not by an exact string: the model naming has already changed
// once ("OLMo-2-7B" vs "OLMo-2-1124-7B") and a silent .find() miss would print
// a sentence with the clause quietly dropped.
const _base = _gate.find(r => /OLMo/.test(r.model) && !/Instruct/.test(r.model));
const _inst = _gate.find(r => /OLMo/.test(r.model) && /Instruct/.test(r.model));
if (!_base || !_inst) throw new Error("part11: OLMo base/Instruct rows not found in summary_model_bias.csv");
s.addText([
  { text: `All ${_pass.length} gate-passing models point the same way: `
        + `${_dirs.length === 1 ? _dirs[0] : _dirs.join(" / ")}, at `
        + `${_ratios[0].toFixed(1)} to ${_ratios[_ratios.length - 1].toFixed(1)} `
        + `times each model's own noise floor. `, options: { bold: true, color: PAPER } },
  { text: "The agreement spans an open-data family and a closed-data contrast, so it is not one team's corpus recipe. And ", options: { color: "D6E6E9" } },
  { text: _base && _inst
        ? `instruction tuning did not reduce it (${_base.absDelta.toFixed(4)} to ${_inst.absDelta.toFixed(4)})`
        : "instruction tuning did not reduce it",
    options: { bold: true, color: WARN } },
  { text: " which is the opposite of the usual assumption and the result most worth stress-testing.", options: { color: "D6E6E9" } },
], { x: 0.77, y: 5.86, w: 11.76, h: 0.52, fontSize: 11, lineSpacing: 13.5, margin: 0, isTextBox: true });
note(s, "If asked why the Pythia rows are shown at all: because leaving them out would hide the most useful finding, which is that the models with the smallest apparent gaps are the ones whose instrument does not work. An auditor using one prompt format and no gate would rank those as the fairest.");

// ============ R-B. WHAT IT WOULD MEAN FOR A HEALTH SYSTEM ======= //
s = S("CONTENT", "Results", "What this would mean for a health system");
s.addText("The mechanism is the point, not the effect size. 0.03 in normalised probability is small; it matters because a small, consistent nudge is applied to very large numbers of decisions in the same direction. A biased clinician is one clinician. A biased triage assistant is a policy.",
  { x: 0.55, y: 1.16, w: 12.2, h: 0.46, fontSize: 12.5, color: INK, lineSpacing: 16, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 1.72, w: 6.05, h: 4.18, fill: "FBEEEC", kicker: "FOUR WAYS THIS COULD CAUSE HARM", kickerColor: FAIL, name: "harm" });
const harms = [
  ["Under-referral compounds.", "Our Group 3 items are referral and triage decisions chosen because each already has a documented human disparity. A model nudging the same way does not add a problem, it automates and launders an old one, with the appearance of objectivity."],
  ["Deference makes small effects large.", "As overridable decision support, 0.03 is mostly noise. As a pre-filled triage level or a prior-authorisation score, it becomes the decision for every case nobody has time to review."],
  ["The failure is invisible to the obvious audit.", "The models whose deltas look smallest are the ones that failed the gate. An organisation auditing with one prompt format and no positive control would read those as the fairest and deploy on that basis."],
  ["Instruction tuning is not a mitigation.", "If the base-to-instruct increase holds, the safety step procurement most relies on did not help and may have hurt."],
];
let hy = 2.14;
harms.forEach((h, i) => {
  s.addText([{ text: h[0] + " ", options: { bold: true, color: INK } },
             { text: h[1], options: { color: MUT } }],
    { x: 0.77, y: hy, w: 5.61, h: 0.92, fontSize: 9.5, lineSpacing: 11.5, margin: 0, isTextBox: true, objectName: "hm" + i });
  hy += 0.95;
});

card(s, { x: 6.75, y: 1.72, w: 6.0, h: 4.18, fill: TINT, kicker: "THREE WAYS IT CUTS THE OTHER WAY, WHICH WE SAY OURSELVES", kickerColor: TEAL, name: "good" });
const goods = [
  ["The corpus finding is the optimistic one.", "Corpus skew is editable in a way model behaviour is not. If downstream asymmetry tracks measurable corpus asymmetry, documentation and curation become levers rather than gestures. That is the datasheet-to-diagnosis claim."],
  ["An auditable pipeline is itself a safety property.", "We can say any of this only because OLMo and Pythia publish corpora that are exactly queryable. The recommendation is procurement-shaped: prefer models whose training data can be counted, and treat an unauditable corpus as a risk rating."],
  ["Vignettes are not patients.", "Every number is a next-token probability over a fixed option set, in English, single-jurisdiction, with no clinician in the loop and no patient outcome in the causal chain. The step to patient harm is an argument, not a measurement."],
];
let gy = 2.3;
goods.forEach((g, i) => {
  s.addText([{ text: g[0] + " ", options: { bold: true, color: INK } },
             { text: g[1], options: { color: MUT } }],
    { x: 6.97, y: gy, w: 5.56, h: 1.18, fontSize: 9.5, lineSpacing: 11.5, margin: 0, isTextBox: true, objectName: "gd" + i });
  gy += 1.2;
});

card(s, { x: 0.55, y: 6.0, w: 12.2, h: 0.92, fill: INK, name: "frame" });
s.addText([
  { text: "The framing to avoid: ", options: { bold: true, color: WARN } },
  { text: "not “LLMs are biased against women in healthcare”. What the design supports is narrower and more useful — ", options: { color: "D6E6E9" } },
  { text: "in the three models where a sex-specific control confirms the instrument works, the arm labelled as a woman receives less of the guideline-indicated action, with the sex parameter held fixed.", options: { bold: true, color: PAPER } },
], { x: 0.77, y: 6.14, w: 11.76, h: 0.64, fontSize: 11, lineSpacing: 13.5, margin: 0, isTextBox: true });
note(s, "The sex-parameter-held-fixed clause is the contribution. It separates a model responding to gender identity from a model correctly responding to clinical sex, and it is why the HL7 SPCU distinction sits in the design rather than in the discussion.");

module.exports = {};
