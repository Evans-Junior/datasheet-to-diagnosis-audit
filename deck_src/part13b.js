// Rounds 3 to 7: the instrument's own failure log, and the provenance apparatus
// that came out of it. Added 2026-11-09 -- the deck stopped at round 2 while the
// repository ran five more.
const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const F = require("./figures.js");

pres.addSection({ title: "Fix rounds 3-7" });
let s = S("SECTION", "Fix rounds 3-7", "7.  Five more rounds, and what each one broke");
s.addText("Every entry below is a fault that passed a clean validator run", { placeholder: "body" });

// ============ FR-A. THE ROUNDS TABLE ============================ //
s = S("CONTENT", "Fix rounds 3-7", "Five rounds, five classes of silent failure");
s.addText("None of these was found by a test going red. Each was found by reading an artefact that nothing was checking.",
  { x: 0.55, y: 1.14, w: 12.2, h: 0.3, fontSize: 12.5, color: MUT, margin: 0, isTextBox: true });

const ROUNDS = [
  ["3", "Stimulus sourcing", "Guideline quotes closed at first hand for every item; 7 sourcing rounds",
   "Two DOIs circulating for one IDSA guideline; a “Shell” record on the Ottawa Ankle Rules. Hence scripts/verify_dois.py", BERRY],
  ["4", "Floor geometry", "Nuisance floor rebuilt from matched Group 4 rows, stratified by option count",
   "The legacy floor used a 4-option bureaucratic frame to gate binary clinical items — four mismatches at once, inflating it ~8.5×", WARN],
  ["5", "Clinical review", "2 vignettes rejected, 1 corrected, 3 citation errors caught",
   "G4-03b reproduced the exact defect that got G4-03 rejected: its negation list was inherited while its findings changed", FAIL],
  ["6", "Provenance", "Every table stamps the prompt set it was built from; pipeline grew to 9 steps",
   "Six tables were outside the pipeline. rq4_linkage was 11 days and several vignette rounds stale while being read as current", FAIL],
  ["7", "Tokenisation", "Option-length limit enforced against all 3 scoring tokenizers, not 1",
   "G4-10 was spread 2 on pythia (a warning) and 4 on Qwen3 and OLMo-2 (a blocker). It sets H3's equivalence margin", FAIL],
];
const rRows = [[
  { text: "Rd", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5, align: "center" } },
  { text: "What it was about", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
  { text: "What changed", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
  { text: "The fault that prompted it", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 10.5 } },
]].concat(ROUNDS.map((r, i) => [
  { text: r[0], options: { bold: true, color: r[4], fontSize: 12, align: "center", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { bold: true, color: INK, fontSize: 10.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { color: MUT, fontSize: 9.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[3], options: { color: INK, fontSize: 9.5, fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(rRows, { x: 0.55, y: 1.52, w: 12.2, colW: [0.6, 2.3, 4.0, 5.3], rowH: 0.78,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.05, 0.1, 0.05, 0.1], fontFace: "Calibri", autoPage: false });

card(s, { x: 0.55, y: 5.6, w: 12.2, h: 0.82, fill: INK,
  kicker: "THE PATTERN, WHICH IS THE ACTUAL CONTRIBUTION", kickerColor: "7FD4C8", name: "pat" });
s.addText([
  { text: "Every one of these was a derived artefact drifting from its source with nothing asserting the drift. ", options: { bold: true, color: PAPER } },
  { text: "A staleness check is only as wide as its field list, and three separate times the list was narrower than the thing it guarded — so it passed. That is a transferable finding about auditing pipelines, not a confession about ours.", options: { color: "D6E6E9" } },
], { x: 0.77, y: 6.0, w: 11.76, h: 0.38, fontSize: 10.5, lineSpacing: 13, margin: 0, isTextBox: true });
note(s, "If asked whether this is just a list of our own bugs: the useful version of the question is how many audits in this literature would survive the same scrutiny. Nobody reports their instrument's failure log, which is why nobody knows.");

// ============ FR-B. THE TWO-TIER RULE ========================== //
s = S("CONTENT_DARK", "Fix rounds 3-7", "Why reporting has two tiers now");
s.addText("The original rule said clinician verification or nothing. It was changed on 2026-11-09 by dated amendment, not by editing the sentence.",
  { x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 12.5, color: "BCD3D8", margin: 0, isTextBox: true });

const TIERS = [
  { n: "0", h: "Not reviewed", b: "Nobody has checked the vignette against a guideline quote. Not citable, at any tier, unchanged by the amendment.", c: FAIL, cnt: "0 rows" },
  { n: "1", h: "Author-reviewed", b: "Checked against a guideline passage we quoted at first hand. Numbers may be presented as results, carrying “pending clinical validation”. This submission.", c: WARN, cnt: "25 rows" },
  { n: "2", h: "Clinician-verified", b: "A qualified clinician confirms the findings force the stated answer. Required for the public paper. Scheduled, not yet done.", c: PASS, cnt: "0 rows" },
];
TIERS.forEach((t, i) => {
  const x = 0.55 + i * 4.1;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.66, w: 3.85, h: 2.1, rectRadius: 0.06,
    fill: { color: "16454F" }, line: { color: t.c, width: 1.25 }, objectName: "tr" + i });
  badge(s, { x: x + 0.22, y: 1.86, n: t.n, d: 0.42, fs: 15, color: t.c, name: "tb" + i });
  s.addText(t.h, { x: x + 0.76, y: 1.88, w: 2.3, h: 0.32, fontSize: 14, bold: true,
    color: PAPER, margin: 0, isTextBox: true });
  s.addText(t.cnt, { x: x + 2.4, y: 1.9, w: 1.22, h: 0.28, fontSize: 11, bold: true,
    color: t.c, align: "right", margin: 0, isTextBox: true });
  s.addText(t.b, { x: x + 0.22, y: 2.42, w: 3.41, h: 1.2, fontSize: 10.5,
    color: "D6E6E9", lineSpacing: 13, margin: 0, isTextBox: true });
});

card(s, { x: 0.55, y: 3.96, w: 6.0, h: 2.44, fill: "16454F",
  kicker: "WHY THE CHANGE IS DEFENSIBLE", kickerColor: "7FD4C8", name: "wd" });
s.addText([
  { text: "Because it separates two claims the old rule confused. ", options: { bold: true, color: PAPER } },
  { text: "That 7 of 10 models fail our own positive control, and that k = 4 clusters cap an exact test at p = 0.0625, are facts about the apparatus — a clinician cannot make them more or less true. What needs a clinician is whether a vignette's findings force its answer.\n\n", options: { color: "D6E6E9" } },
  { text: "And author review earned it: ", options: { bold: true, color: PAPER } },
  { text: "2 vignettes rejected, 1 corrected after reproducing a rejected row's defect, 3 citation errors no validator saw.", options: { color: "D6E6E9" } },
], { x: 0.77, y: 4.42, w: 5.56, h: 1.86, fontSize: 10.5, lineSpacing: 13.5, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 3.96, w: 6.0, h: 2.44, fill: "4A2730",
  kicker: "WHAT WOULD SHOW THE CHANGE WAS WRONG", kickerColor: "E8A0B4", name: "wf" });
s.addText([
  { text: "Pre-committed, before the review happens. ", options: { bold: true, color: PAPER } },
  { text: "If clinical review overturns a direction or a gate verdict, tier 1 was too weak a bar for the claims made at it and the amendment was a mistake.\n\n", options: { color: "F0D8DE" } },
  { text: "Review merely moving magnitudes does not vindicate it", options: { bold: true, color: PAPER } },
  { text: ", because every tier-1 claim here is directional and floor-relative. The test is in the preregistration as §10, where a reader finds it without being pointed at it.", options: { color: "F0D8DE" } },
], { x: 6.97, y: 4.42, w: 5.56, h: 1.86, fontSize: 10.5, lineSpacing: 13.5, margin: 0, isTextBox: true });
note(s, "Expect to be challenged on this. The answer is that a preregistration changed by silent edit is worth nothing, and changed by dated amendment with a pre-committed falsifier it is still worth something. Section 9's original sentence is not edited. Section 10 says what it used to say, what it says now, who decided, when, and that it was after seeing scores.");

module.exports = {};
