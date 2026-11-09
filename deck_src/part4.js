const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 8. LIT 3: the sex and gender standard ============== //
let s = S("CONTENT", "Related work", "Sex and gender as an operational standard");
s.addText("We do not invent a definition. Borrowing an existing clinical standard is what lets us separate a legitimate clinical difference from an illegitimate one in code rather than in prose.",
  { x: 0.55, y: 1.25, w: 12.2, h: 0.46, fontSize: 14, color: INK, lineSpacing: 18, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 1.86, w: 6.0, h: 2.5, fill: INK, kicker: "HL7 GENDER HARMONY MODEL  [15]",
  kickerColor: "7FD4C8", name: "gh" });
s.addText("Separates gender identity from the Sex Parameter for Clinical Use, which is the single value a clinical system should consult when a decision depends on physiology.",
  { x: 0.77, y: 2.4, w: 5.56, h: 0.82, fontSize: 12.5, color: PAPER, lineSpacing: 16, margin: 0, isTextBox: true });
box(s, { x: 0.77, y: 3.3, w: 2.6, h: 0.5, t: "Gender identity", fill: "1C4E59", line: "7FD4C8", tc: PAPER, fs: 11.5, name: "gh1" });
box(s, { x: 3.73, y: 3.3, w: 2.6, h: 0.5, t: "Sex parameter", fill: "1C4E59", line: WARN, tc: PAPER, fs: 11.5, name: "gh2" });
s.addText("varies in our prompts", { x: 0.77, y: 3.84, w: 2.6, h: 0.26, fontSize: 9.5, italic: true,
  color: "7FD4C8", align: "center", margin: 0, isTextBox: true });
s.addText("held fixed in our prompts", { x: 3.73, y: 3.84, w: 2.6, h: 0.26, fontSize: 9.5, italic: true,
  color: WARN, align: "center", margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 1.86, w: 6.0, h: 2.5, fill: TINT, kicker: "NON-BINARY REPRESENTATION  [5]",
  kickerColor: BERRY, name: "nb" });
s.addText("Dev et al. show the harms of gender exclusivity in language technologies. Their work is why the non-binary arm is primary throughout rather than an afterthought.",
  { x: 6.97, y: 2.4, w: 5.56, h: 0.82, fontSize: 12.5, color: INK, lineSpacing: 16, margin: 0, isTextBox: true });
s.addText([
  { text: "One mechanical consequence. ", options: { bold: true, color: INK } },
  { text: "Verb forms are carried per arm, so singular they takes plural agreement. If the non-binary arm alone contained ungrammatical text, its sequence probability would fall because it reads as bad English, not because of bias. That would have manufactured a finding.", options: { color: MUT } },
], { x: 6.97, y: 3.26, w: 5.56, h: 0.96, fontSize: 11.5, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 4.52, w: 12.2, h: 1.9, fill: "FDF3E3", kicker: "WHY THIS MATTERS FOR THE RESULT",
  kickerColor: WARN, name: "ghw" });
s.addText([
  { text: "Crossing the two gives transgender configurations without naming them. ", options: { bold: true, color: INK } },
  { text: "Two sex-parameter values times three gender identities yields six combinations. Sex parameter female with identity man is a transgender man. Sex parameter male with identity woman is a transgender woman. The model is never told the patient is transgender: the configuration simply exists in the prompt grid. This is what produced our main exploratory finding, and the standard is the only reason it was available to find.", options: { color: INK } },
], { x: 0.77, y: 5.06, w: 11.76, h: 1.2, fontSize: 13, lineSpacing: 17, margin: 0, isTextBox: true });
note(s, "The Gender Harmony Model is doing real work here, not decorating the method. Without separating identity from the sex parameter there is no way to hold the clinically relevant fact fixed while the label moves, and the transgender configurations would not exist in the data at all.");

// ============ 9. LIT 4: corpora and what the models are for ====== //
s = S("CONTENT", "Related work", "The corpora, and what the models were built for");
const lit4 = [
  { h: "The Pile  [7]  and its datasheet  [1]", b: "The most thoroughly documented large corpus in public. Trained Pythia." },
  { h: "Dolma  [20]  and OLMo 2  [18]", b: "Documents the corpus family behind OLMo 2, our second open-data model." },
  { h: "Datasheets for Datasets  [8]", b: "Supplies the structure for our documentation analysis. Our codebook asks of each document whether it discloses gender composition and connects it to downstream health use." },
  { h: "Infini-gram  [13]", b: "Exact n-gram counts over both corpora through an API. This is the tool that makes corpus measurement possible at all." },
];
lit4.forEach((c, i) => {
  const y = 1.28 + i * 1.08;
  card(s, { x: 0.55, y, w: 6.5, h: 0.96, name: "l4" + i });
  s.addText(c.h, { x: 0.77, y: y + 0.1, w: 6.06, h: 0.28, fontSize: 12.5, bold: true,
    color: TEAL, margin: 0, isTextBox: true, objectName: "l4h" + i });
  s.addText(c.b, { x: 0.77, y: y + 0.38, w: 6.06, h: 0.5, fontSize: 11, color: MUT,
    lineSpacing: 13.5, margin: 0, isTextBox: true, objectName: "l4b" + i });
});
card(s, { x: 7.3, y: 1.28, w: 5.45, h: 4.4, fill: INK,
  kicker: "WHAT EACH FAMILY WAS ACTUALLY BUILT FOR", kickerColor: "7FD4C8", name: "purp" });
s.addText("Neither open-data family was built to answer clinical questions. This is a confound, and we state it rather than treat the models as interchangeable.",
  { x: 7.52, y: 1.82, w: 5.0, h: 0.78, fontSize: 12.5, bold: true, color: PAPER, lineSpacing: 16, margin: 0, isTextBox: true });
s.addText([
  { text: "Pythia  [2]", options: { bold: true, color: "7FD4C8", fontSize: 12.5 } },
  { text: "\n", options: {} },
  { text: "A scientific instrument for studying training dynamics. Eight sizes trained on identical data in identical order, 154 checkpoints each, and no attempt at competitive benchmark performance. It was built to be studied, not to be used.", options: { color: "BCD3D8", fontSize: 11.5 } },
], { x: 7.52, y: 2.72, w: 5.0, h: 1.25, lineSpacing: 14.5, margin: 0, isTextBox: true });
s.addText([
  { text: "OLMo 2  [18]", options: { bold: true, color: "7FD4C8", fontSize: 12.5 } },
  { text: "\n", options: {} },
  { text: "Built to be a genuinely open and capable model, with the full data, code and recipe released. Closer to a usable system, and it shows in the results: both OLMo models now pass our gate and no Pythia model does.", options: { color: "BCD3D8", fontSize: 11.5 } },
], { x: 7.52, y: 4.04, w: 5.0, h: 1.25, lineSpacing: 14.5, margin: 0, isTextBox: true });
card(s, { x: 0.55, y: 5.72, w: 6.5, h: 0.78, fill: "FBEEEC", name: "l4w" });
s.addText([{ text: "A limit we hit. ", options: { bold: true, color: FAIL } },
  { text: "Infini-gram has no prebuilt index for the newer open corpora, so switching to a more capable open model would break the corpus linkage entirely.", options: { color: INK } }],
  { x: 0.77, y: 5.86, w: 6.06, h: 0.56, fontSize: 11.5, lineSpacing: 14, margin: 0, isTextBox: true });
s.addText("Qwen3-8B [19] is included as a closed-data capability reference, not as an audit target.",
  { x: 7.3, y: 5.86, w: 5.45, h: 0.3, fontSize: 11, italic: true, color: MUT, margin: 0, isTextBox: true });
note(s, "The purpose question matters because a marker will ask why the open models perform so badly. The answer is that Pythia was never built to answer questions, and that is a property of the model set we inherited, not a flaw in the instrument.");

// ============ 10. HOW LIT INFLUENCED DESIGN (mapping) ============ //
s = S("CONTENT_DARK", "Related work", "How the literature became design decisions");
s.addText("Each row is a specific mechanism in the repository, traceable to the work that forced it.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.32, fontSize: 13, color: "BCD3D8", margin: 0, isTextBox: true });
const mapRows = [[
  { text: "From the literature", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12 } },
  { text: "What we built because of it", options: { bold: true, color: PAPER, fill: { color: "1C4E59" }, fontSize: 12 } },
]];
[
  ["Clinical correctness sometimes depends on sex [4]", "Every vignette carries a reference answer quoted from a named guideline, with that guideline's own strength-of-recommendation grading"],
  ["Gender identity is not a clinical sex parameter [15]", "The Gender Harmony distinction is built into the prompt grid: the sex parameter is held fixed while identity varies"],
  ["Non-binary erasure in language technology [5]", "A third gender arm throughout, with per-arm verb agreement, and a corpus measure that reports absence as a result"],
  ["The gender token alone can drive the effect [9, 23]", "Patient names excluded entirely, so ethnicity and class signal cannot confound the gender manipulation"],
  ["Chain-of-thought explanations are unfaithful [21]", "Deterministic log-probability scoring of fixed options, never free-text generation"],
  ["Documentation structure for datasets [8]", "A written codebook, coded independently by both authors, with inter-coder agreement reported whatever it is"],
  ["Corpus-level bias amplification [25]", "Corpus skew measured as a base-rate-normalised log ratio and centred, so a raw frequency difference is not read as skew"],
].forEach((r, i) => mapRows.push([
  { text: r[0], options: { color: "D6E6E9", fontSize: 11.5, fill: { color: i % 2 ? "133F49" : "0F3A44" } } },
  { text: r[1], options: { color: PAPER, fontSize: 11.5, fill: { color: i % 2 ? "133F49" : "0F3A44" } } },
]));
s.addTable(mapRows, { x: 0.55, y: 1.62, w: 12.2, colW: [4.6, 7.6], rowH: 0.52,
  border: { type: "solid", color: "2A5E6A", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.12, 0.06, 0.12], fontFace: "Calibri", autoPage: false });
note(s, "This is the slide that answers whether the literature review is decorative. Every row names a mechanism a reader can find in the repository.");

module.exports = {};
