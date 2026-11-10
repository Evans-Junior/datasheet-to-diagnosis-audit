const K = require("./part1.js");
const F = require("./figures.js");
const _ch = F.chanceRange();
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 32. D057 SIGN FLIPS =============================== //
let s = S("CONTENT", "Fix round 1", "The finding that came out of the failed intervention");
s.addText("I3 tried three prompt formats on all seven Pythia models to see whether the problem was elicitation rather than capability. It failed its criterion, and in failing it produced the most consequential result of the round.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.4, fontSize: 13.5, color: INK, lineSpacing: 17, margin: 0, isTextBox: true });

// D096. All 21 margins were typed into three arrays. They were still correct,
// because the seven Pythia models were not rescored in this round, but a typed
// array that is right by luck fails silently the first time one of them is.
// The "7 of 7" claim beside the chart is counted from the same rows.
const _I3 = F.i3Grid();
const _I3NAME = { baseline: "Question and answer format", cloze: "Cloze format",
                  fewshot: "Few-shot format" };
s.addChart(pres.ChartType.bar,
  _I3.configs.map(c => ({ name: _I3NAME[c] || c, labels: _I3.order,
                          values: _I3.series[c] })),
  { x: 0.55, y: 1.7, w: 7.6, h: 4.0, barDir: "col", barGrouping: "clustered",
  catAxisLabelPos: "low", valAxisLabelFormatCode: "0.000",
  chartColors: ["9BB3BA", BERRY, TEAL], showTitle: true,
  title: "Group 2 margin by prompt format. Every model crosses zero",
  titleColor: INK, titleFontSize: 12, titleFontFace: "+mn-lt",
  showLegend: true, legendPos: "b", legendColor: MUT, legendFontSize: 10, legendFontFace: "+mn-lt",
  showValue: false, barGapWidthPct: 30,
  catAxisLabelColor: MUT, valAxisLabelColor: MUT, catAxisLabelFontSize: 10,
  valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  valGridLine: { color: "E4EDEE", size: 0.75 }, catGridLine: { style: "none" } });

card(s, { x: 8.4, y: 1.7, w: 4.35, h: 1.5, fill: "FBEEEC", name: "sf1" });
s.addText(`${_I3.nSignFlips} of ${_I3.nModels}`, { x: 8.62, y: 1.84, w: 3.9, h: 0.56, fontSize: 30, bold: true, color: FAIL,
  fontFace: "Cambria", margin: 0, isTextBox: true });
s.addText("models change the SIGN of their effect across prompt formats",
  { x: 8.62, y: 2.38, w: 3.9, h: 0.68, fontSize: 12, bold: true, color: INK, lineSpacing: 15, margin: 0, isTextBox: true });

card(s, { x: 8.4, y: 3.32, w: 4.35, h: 1.26, fill: TINT, kicker: "WHAT THAT MEANS", kickerColor: TEAL, name: "sf2" });
s.addText("The direction of a sex-parameter effect in this family is a property of the prompt format, not of the model. A single-format audit would report a direction another defensible format reverses.",
  { x: 8.62, y: 3.74, w: 3.9, h: 0.76, fontSize: 11, color: INK, lineSpacing: 13.5, margin: 0, isTextBox: true });

card(s, { x: 8.4, y: 4.7, w: 4.35, h: 1.0, fill: TINT, kicker: "CALIBRATION WAS ALREADY IN THE DESIGN", kickerColor: TEAL, name: "sf3" });
s.addText("Our PMI score key already subtracts a content-free baseline, so every Pythia margin was post-calibration all along.",
  { x: 8.62, y: 5.12, w: 3.9, h: 0.52, fontSize: 11, color: INK, lineSpacing: 13.5, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.86, w: 12.2, h: 0.56, fill: INK, name: "sf4" });
s.addText([{ text: "The uncomfortable corollary, which we state rather than work around:  ", options: { bold: true, color: WARN } },
  { text: "the models that ship the corpora this project's argument depends on are the models this method cannot measure.", options: { color: PAPER } }],
  { x: 0.77, y: 5.98, w: 11.76, h: 0.34, fontSize: 12.5, margin: 0, isTextBox: true });
// D095. This note said the probabilities are "exactly uniform over two
// options", which is the same error slide 28 carried: the pooled figure is
// held at 0.5 by the design, because Group 2 flips the correct answer with the
// sex parameter. Within a level the models move a long way. Saying "uniform"
// out loud invites the obvious question and has no answer.
note(s, `Pooled over the sex parameter, Pythia probabilities sit at `
  + `${_ch.pooledLo.toFixed(3)} to ${_ch.pooledHi.toFixed(3)} over two options. `
  + "Do not call that uniform: Group 2 flips the correct answer with the sex "
  + `parameter, so within a level the same models span `
  + `${_ch.withinLo.toFixed(3)} to ${_ch.withinHi.toFixed(3)} and `
  + `${_ch.widestModel} swings ${_ch.maxSwing.toFixed(2)}. They respond to the `
  + "input; the response does not track correctness, which is what a signed "
  + "margin catches and a distance from 0.5 does not. It is a base model with "
  + "no instruction tuning. Three formats were tried; a chat template, a longer "
  + "prefix and a generation-based readout remain untested, so this is a limit "
  + "on what we have shown, not a proof of impossibility.");

// ============ SECTION: FIX ROUND 2 (STIMULI) ==================== //
pres.addSection({ title: "Fix round 2" });
s = S("SECTION", "Fix round 2", "6.  Instrument fix round 2: our own stimuli");
s.addText("A defect we introduced ourselves, how far it reached, and the rule that now prevents it", { placeholder: "body" });
note(s, "Fix round 1 was about the analysis. This round is about the stimulus text, and it is the round where the instrument was wrong rather than merely underpowered.");

// ============ 33. THE PREGNANCY CLAUSE DEFECT =================== //
s = S("CONTENT", "Fix round 2", "A pregnancy clause in 264 impossible prompts");
s.addText("Every vignette ended with one sentence meant to close a loophole: a guideline that prescribes differently in pregnancy could make a gendered arm diverge legitimately. The sentence closed that loophole and introduced a worse problem in the arms where it cannot be true.",
  { x: 0.55, y: 1.18, w: 12.2, h: 0.46, fontSize: 13, color: INK, lineSpacing: 16.5, margin: 0, isTextBox: true });

stat(s, { x: 0.55, y: 1.74, w: 3.7, n: "528 / 624", size: 32, color: TEAL, label: "prompts carried the clause",
  sub: "21 of 25 vignettes ended \"Pregnancy has been excluded.\" (set of 25 at the time)", name: "pg1" });
stat(s, { x: 4.75, y: 1.74, w: 3.7, n: "264", size: 32, color: FAIL, label: "of them were clinically impossible",
  sub: "Sex for clinical use varies INSIDE every vignette: 12 female arms and 12 male arms. The sentence sat in all 24.", name: "pg2" });
stat(s, { x: 8.95, y: 1.74, w: 3.8, n: "0", size: 32, color: PASS, label: "prompts mention pregnancy now",
  sub: "Removed from the templates, the generated set, the workbook and the review form.", name: "pg3" });

card(s, { x: 0.55, y: 3.42, w: 12.2, h: 0.86, fill: INK, name: "pgq" });
s.addText([
  { text: "Sex for clinical use: male. ", options: { bold: true, color: WARN } },
  { text: "The patient is a man, aged 36. He presents with ", options: { color: "D6E6E9" } },
  { text: "[...] ", options: { color: "6E8C94" } },
  { text: "Pregnancy has been excluded.", options: { bold: true, color: "E9A79C" } },
], { x: 0.77, y: 3.56, w: 11.76, h: 0.3, fontSize: 12.5, fontFace: "Calibri", margin: 0, isTextBox: true });
s.addText("A clinical reviewer reads this and marks the vignette wrong, correctly. It was in 264 of our 624 prompts.",
  { x: 0.77, y: 3.9, w: 11.76, h: 0.26, fontSize: 11, italic: true, color: "9BB3BA", margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 4.44, w: 6.05, h: 1.62, fill: "FBEEEC", kicker: "CORRECTING OUR OWN FIRST DIAGNOSIS", kickerColor: FAIL, name: "pgc1" });
s.addText("We first reported that this contaminated the Group 2 gate directly. It does not. The sentence was identical across all 24 arms, and both statistics compare prompts that differ only in the sex-parameter line, so there was no first-order confound. Overstating a defect is its own failure.",
  { x: 0.77, y: 4.86, w: 5.61, h: 1.1, fontSize: 11, color: INK, lineSpacing: 13.5, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 4.44, w: 6.0, h: 1.62, fill: TINT, kicker: "SO WHAT THE REAL COST WAS", kickerColor: TEAL, name: "pgc2" });
s.addText([
  { text: "Face validity. ", options: { bold: true, color: INK } },
  { text: "264 prompts contained a clinical impossibility. This is the cost that matters, because it is the reviewer's confidence in the whole instrument.\n", options: { color: MUT } },
  { text: "A second-order interaction. ", options: { bold: true, color: INK } },
  { text: "A strongly female-associated token sitting inside prompts whose only intended variation is gender identity.", options: { color: MUT } },
], { x: 6.97, y: 4.86, w: 5.56, h: 1.1, fontSize: 11, lineSpacing: 13.5, margin: 0, isTextBox: true });

s.addText("The clause was added to prevent a confound and became one. It is the clearest example in the project of a fix that needed auditing as hard as the thing it fixed.",
  { x: 0.55, y: 6.18, w: 12.2, h: 0.46, fontSize: 11.5, italic: true, color: MUT, margin: 0, isTextBox: true });
note(s, "If asked why the clause was there at all: a guideline that prescribes differently in pregnancy is a real threat, and D018 had already flagged it. The error was applying one blanket sentence to every vignette and every arm instead of checking, per row, whether the branch could actually reach the answer.");

// ============ 34. WHY REMOVAL IS SAFE, AND THE EXCEPTION ======== //
s = S("CONTENT", "Fix round 2", "Why removal is safe, and the one row where it was not");
s.addText("A negation can be deleted only if what it negated cannot change the answer. Audited row by row, not assumed.",
  { x: 0.55, y: 1.18, w: 12.2, h: 0.32, fontSize: 13, color: INK, margin: 0, isTextBox: true });

const pgRows = [[
  { text: "Row", options: { bold: true, color: PAPER, fontSize: 10.5, fill: { color: INK } } },
  { text: "Where the guideline carves pregnancy out", options: { bold: true, color: PAPER, fontSize: 10.5, fill: { color: INK } } },
  { text: "Can it change THIS row's answer?", options: { bold: true, color: PAPER, fontSize: 10.5, fill: { color: INK } } },
]].concat([
  ["G4-04 sinusitis", "The penicillin-allergy branch", "No. The answer is \"do not offer an antibiotic\", so the drug table is never reached", PASS],
  ["G4-05 cellulitis", "The same branch", "No. The answer is \"no swab\"", PASS],
  ["G4-10 impetigo", "The same branch", "No. The answer is topical; the carve-out is between oral alternatives", PASS],
  ["G4-11 meningitis", "Pregnancy is a Listeria risk factor", "No. Amoxicillin is an addition to ceftriaxone and is not an option", PASS],
  ["G1-02 malaria", "An explicit first-trimester rule", "No. WHO specifies artemether-lumefantrine, which IS an artemisinin combination", PASS],
  ["G1-03 asthma", "A dedicated pregnancy section", "No. GINA does not reduce treatment in pregnancy", PASS],
  ["G1-05 diabetes", "Incretins and SGLT2i avoided", "YES, through a distractor", FAIL],
].map((r, i) => [
  { text: r[0], options: { bold: true, color: INK, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { color: MUT, fontSize: 10, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { bold: r[3] === FAIL, color: r[3] === FAIL ? FAIL : MUT, fontSize: 10, fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(pgRows, { x: 0.55, y: 1.58, w: 7.7, colW: [1.75, 2.35, 3.6], rowH: 0.42,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.05, 0.1, 0.05, 0.1], fontFace: "Calibri", autoPage: false });

card(s, { x: 8.45, y: 1.58, w: 4.3, h: 1.74, fill: "FBEEEC", kicker: "THE ONE ROW THAT NEEDED MORE", kickerColor: FAIL, name: "pgx" });
s.addText("Metformin stays first-line in pregnancy, but insulin, one of that row's distractors, becomes the preferred agent. An inferred pregnancy could move probability along a path the guideline itself licenses. Closed by moving the patient's age from 55 to 68.",
  { x: 8.67, y: 2.0, w: 3.86, h: 1.2, fontSize: 10.5, color: INK, lineSpacing: 13, margin: 0, isTextBox: true });

card(s, { x: 8.45, y: 3.46, w: 4.3, h: 1.74, fill: TINT, kicker: "THE RULE WE NOW APPLY", kickerColor: TEAL, name: "pgr" });
s.addText("A noise-floor item is admissible only if no sex- or pregnancy-conditional branch can change its reference answer. If a floor item can be moved by an inferred pregnancy, real bias is absorbed into the floor and the headline test is pushed toward the null.",
  { x: 8.67, y: 3.88, w: 3.86, h: 1.2, fontSize: 10.5, color: INK, lineSpacing: 13, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.3, w: 7.7, h: 1.1, fill: TINT, kicker: "AND THE CHECK WAS NOT WEAKENED TO MAKE THIS PASS", kickerColor: TEAL, name: "pgk" });
s.addText("Our own C4 check still warns on the three rows whose guideline carves pregnancy out, labelling them \"Authors' call\". The calls are written out per row; the warning stays so a reviewer meets the question rather than inheriting a silent decision.",
  { x: 0.77, y: 5.72, w: 7.26, h: 0.6, fontSize: 10.5, color: INK, lineSpacing: 13, margin: 0, isTextBox: true });

card(s, { x: 8.45, y: 5.3, w: 4.3, h: 1.1, fill: INK, name: "pgd" });
s.addText([
  { text: "Not the age change we refused. ", options: { bold: true, color: WARN } },
  { text: "For G4-11, dropping to 17 would have pushed an adult item outside our own \"each item is adult\" rule so a paediatric guideline would fit. The test is whether the instrument's rules move or the stimulus does.", options: { color: "D6E6E9" } },
], { x: 8.67, y: 5.44, w: 3.86, h: 0.84, fontSize: 10, lineSpacing: 12.5, margin: 0, isTextBox: true });

s.addText("What this does not claim: deleting the sentence removes an explicit pregnancy token from the prompt. It does not remove a model's latent gender-to-pregnancy inference, which is part of what the study measures. The instrument simply no longer supplies the cue.",
  { x: 0.55, y: 6.44, w: 12.2, h: 0.48, fontSize: 11, italic: true, color: MUT, margin: 0, isTextBox: true });
note(s, "The honest summary is that we removed our own cue, not the model's inference. If asked whether this weakens the pregnancy safeguard: no, it relocates it from a blanket sentence to a per-row reachability audit plus one age change, and the audit is recorded in docs/vignette_sources.md round 4.");

// ============ SECTION: LIMITATIONS AND CONCLUSIONS ============== //

module.exports = {};
