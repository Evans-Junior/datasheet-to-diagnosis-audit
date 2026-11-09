const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const F = require("./figures.js");   // D090/D091

// ============ 17. STATISTICS AND PRE-REGISTRATION =============== //
let s = S("CONTENT", "Methodology", "Statistics, pre-registration and the gate");
card(s, { x: 0.55, y: 1.28, w: 6.0, h: 2.5, fill: TINT, kicker: "THE UNIT OF INFERENCE", kickerColor: TEAL, name: "st1" });
s.addText([
  { text: "The unit is the vignette, not the prompt. ", options: { bold: true, color: INK } },
  { text: "Prompts within a vignette share clinical text and are not independent. Treating them as independent observations rejected a true zero at p = 0.025 in simulation, so the error is not theoretical.\n\n", options: { color: MUT } },
  { text: "Confidence intervals come from a cluster bootstrap over vignettes with 10,000 resamples, and the four hypotheses carry a Holm correction.", options: { color: MUT } },
], { x: 0.77, y: 1.82, w: 5.56, h: 1.86, fontSize: 11.5, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 1.28, w: 6.0, h: 2.5, fill: "FDF3E3", kicker: "THE RESOLUTION LIMIT", kickerColor: WARN, name: "st2" });
s.addText([
  { text: "A design with k clusters cannot resolve a p value finer than 2 to the power of minus k. ", options: { bold: true, color: INK } },
  { text: "H1 rests on two vignettes, so its finest resolvable p is 0.25. The gate rests on three, giving 0.125.\n\n", options: { color: INK } },
  { text: "This caught a real false positive: H1 originally reported p = 0.0001 with reject set to true, on two clusters. Clamped to what the design supports it does not reject, and an exact sign-flip test agrees.", options: { color: MUT } },
], { x: 6.97, y: 1.82, w: 5.56, h: 1.86, fontSize: 11.5, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 3.96, w: 12.2, h: 2.46, fill: INK, kicker: "THE PRE-REGISTERED GATE", kickerColor: "7FD4C8", name: "gate" });
s.addText("The four hypotheses were fixed in a dated commit before any model was scored. That document also commits to a gate.",
  { x: 0.77, y: 4.5, w: 11.76, h: 0.3, fontSize: 13, color: PAPER, margin: 0, isTextBox: true });
box(s, { x: 0.77, y: 4.9, w: 2.9, h: 0.82, t: "Report the Group 2\neffect first", fill: "1C4E59", line: "7FD4C8", tc: PAPER, fs: 11.5, name: "gt1" });
arrow(s, { x: 3.78, y: 5.22, w: 0.44, h: 0.18, color: "7FD4C8", name: "gta1" });
box(s, { x: 4.33, y: 4.9, w: 2.9, h: 0.82, t: "Is it larger than\nthe model's own floor?", fill: "1C4E59", line: "7FD4C8", tc: PAPER, fs: 11.5, name: "gt2" });
arrow(s, { x: 7.34, y: 5.22, w: 0.44, h: 0.18, color: PASS, name: "gta2" });
box(s, { x: 7.89, y: 4.9, w: 2.2, h: 0.82, t: "Yes:\nresults mean something", fill: "1C4E59", line: PASS, tc: PAPER, fs: 11, name: "gt3" });
arrow(s, { x: 10.2, y: 5.22, w: 0.44, h: 0.18, color: FAIL, name: "gta3" });
box(s, { x: 10.75, y: 4.9, w: 1.78, h: 0.82, t: "No:\nrun declared\ninsensitive", fill: "1C4E59", line: FAIL, tc: PAPER, fs: 11, name: "gt4" });
s.addText("The gate is the mechanism that stops us presenting insensitivity as fairness. It is the reason this project can report a null honestly.",
  { x: 0.77, y: 5.9, w: 11.76, h: 0.42, fontSize: 12, italic: true, color: "BCD3D8", margin: 0, isTextBox: true });
note(s, "Three defensive points live here: the inference unit, the resolution limit and the gate. Each one removed a false positive we had already produced, which is the strongest evidence that the pre-registration is doing work rather than decorating the project.");

// ============ 18. COMMITMENT TO MECHANISM ======================= //
s = S("CONTENT", "Methodology", "From commitment to enforcing mechanism");
s.addText("Fifty-seven numbered decisions are logged with dates and reasons. The six below carry the project's values into mechanisms, which is how the design makes its ethics testable rather than merely stated.",
  { x: 0.55, y: 1.22, w: 12.2, h: 0.56, fontSize: 13.5, color: INK, margin: 0, isTextBox: true });
const comRows = [[
  { text: "Commitment", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5 } },
  { text: "Mechanism that enforces it", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5 } },
  { text: "What it prevents", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5 } },
]];
[
  ["A difference is bias only where the answer should not differ", "Reference answers quoted from named guidelines with their own grading, plus Group 2 as a positive control", "Asserting invariance instead of sourcing it"],
  ["Gender identity is not a clinical sex parameter", "The Gender Harmony distinction is built into the prompt grid, with the sex parameter held fixed while identity varies", "Treating trans patients as an edge case"],
  ["Non-binary people are patients, not an afterthought", "A third gender arm throughout, and a corpus measure that reports absence as a result", "Binary-only findings presented as complete"],
  ["A null must be distinguishable from blindness", "A measured noise floor per model, and a gate that must pass before any result is reported", "Presenting insensitivity as fairness"],
  ["Findings are fixed before they are seen", "Append-only pre-registration in a dated commit, with every deviation logged", "Choosing the analysis after seeing the result"],
  ["Our own AI use is part of the evidence", "Provenance and clinician approval kept as separate fields on every item", "Relabelling an item in a way that hides how it was drafted"],
].forEach((r, i) => comRows.push([
  { text: r[0], options: { bold: true, color: INK, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { color: MUT, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { color: FAIL, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(comRows, { x: 0.55, y: 1.68, w: 12.2, colW: [3.3, 5.6, 3.3], rowH: 0.66,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.12, 0.06, 0.12], fontFace: "Calibri", autoPage: false });
note(s, "If a marker asks what makes this an ethics project rather than a measurement project, this is the slide. Each row is a value, a mechanism and a failure mode it closes.");

// ============ SECTION: RESULTS ================================== //
pres.addSection({ title: "Results" });
s = S("SECTION", "Results", "4.  Results and analysis");
s.addText("Tier 1 results: every vignette author-reviewed against a quoted guideline, pending clinical validation", { placeholder: "body" });

// ============ 19. PROVISIONAL WARNING + SCALE OF RUN ============ //
s = S("CONTENT", "Results", "The scale of the run, and one standing caveat");
card(s, { x: 0.55, y: 1.22, w: 12.2, h: 1.3, fill: "FDF4E3", kicker: "READ THIS BEFORE QUOTING ANY NUMBER",
  kickerColor: WARN, name: "prov" });
s.addText([
  { text: "These are tier 1 results. ", options: { bold: true, color: INK } },
  { text: "All 26 live vignettes are author-reviewed against a guideline passage we quoted at first hand, which is the bar fixed for this submission (prereg \u00A710). That bar earned the tier: author review rejected two vignettes outright, corrected a third, and caught three citation errors no validator saw. ", options: { color: MUT } },
  { text: "It is not clinician verification. ", options: { bold: true, color: WARN } },
  { text: "Clinical review is scheduled; the public paper waits for it, and we report its effect either way.", options: { color: MUT } },
], { x: 0.77, y: 1.68, w: 11.76, h: 0.8, fontSize: 11.5, lineSpacing: 14.5, margin: 0, isTextBox: true });
// D090: counts derived, so this slide cannot be the one still saying 384.
const _nRows = F.table("rq2_deltas.csv").length;
const _nModels = F.gateTable().length;
const _nDec = 93;
const nums = [
  { n: String(_nModels), l: "models scored", s: "7 Pythia sizes, OLMo 2 base and Instruct, Qwen3-8B", c: TEAL },
  { n: "648", l: "prompts", s: "From 26 live guideline-sourced templates; 2 rejected on review", c: TEAL },
  { n: _nRows.toLocaleString("en-US"), l: "matched contrast rows", s: "Across both outcomes, 24 arms per vignette", c: TEAL },
  { n: "1,504", l: "corpus queries", s: "Zero failed. Replicates across both corpora at r = 0.931", c: PASS },
  { n: String(_nDec), l: "logged decisions", s: "Each with a date, a reason, and reversals recorded", c: BERRY },
];
nums.forEach((v, i) => {
  const x = 0.55 + i * 2.48;
  card(s, { x, y: 2.62, w: 2.3, h: 2.0, name: "nu" + i });
  stat(s, { x: x + 0.22, y: 2.8, w: 1.86, n: v.n, label: v.l, sub: v.s, color: v.c,
    size: v.n.length > 4 ? 26 : 34, nh: 0.7, name: "nus" + i });
});
card(s, { x: 0.55, y: 4.84, w: 12.2, h: 1.56, fill: INK, kicker: "WHY THE REPORTING RULE HAS TWO TIERS", kickerColor: "7FD4C8", name: "why" });
s.addText("The original rule was all-or-nothing: clinician verification or nothing reportable. It conflated two different claims. That 7 of 10 models fail our own positive control, and that k = 4 clusters cap an exact test at p = 0.0625, are facts about the apparatus \u2014 clinician review cannot make them more or less true. What needs a clinician is whether a vignette's findings force its answer. So reporting was split into two tiers, in a dated amendment with a pre-committed test that would show the split was wrong: if clinical review overturns a direction or a gate verdict, tier 1 was too weak a bar.",
  { x: 0.77, y: 5.38, w: 11.76, h: 0.9, fontSize: 12, color: PAPER, lineSpacing: 15.5, margin: 0, isTextBox: true });
note(s, "Say 'pending clinical validation' out loud every time you give one of these figures. If asked why the rule changed: because the old one made the honest label and the useless label the same label. The amendment is dated, it is in the preregistration as section 10, and it names in advance what would prove it wrong.");

module.exports = {};
