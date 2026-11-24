// The audit vocabulary. Two slides on WHAT was counted in the corpora and WHY
// each family of terms is there.
//
// WHY THIS IS METHODOLOGY AND NOT RESULTS. Which terms you search for decides
// what a corpus audit can find, and the exclusions decide it just as much as
// the inclusions. configs/terms.yaml says so in as many words: "term selection
// is a methodological choice that changes results, not a detail." Until now the
// deck showed the skew numbers without ever showing the vocabulary they came
// from, which invites the fair question of whether the terms were picked after
// seeing the counts. They were not, and this is where we say so.
//
// EDITORIAL VS READ. The term NAMES and the reasons for each family are
// editorial and live here, the way fig_skew's concept list lives in its own
// generator. Every COUNT and every skew value is read from results/tables, and
// F.termSkew throws on a term that has dropped out of the audit, so a name on
// this slide cannot quietly stop being measured.
const K = require("./part1.js");
const { pres, S, card, box, arrow, note, srcLine,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const F = require("./figures.js");

const TI = F.termInventory();

// ============ THE FRAME AND THE FOUR FAMILIES ==================== //
let s = S("CONTENT", "Methodology", "The audit vocabulary, and why each term is in it");
K.mark("auditterms");

s.addText(`${TI.diagnosis} diagnosis terms, of which ${TI.diagnosisVignette} come from our own vignettes and ${TI.diagnosisPsych} from the dismissal literature, plus ${TI.decision} decision terms. Searched across ${TI.indexes} corpora inside eight fixed sentence frames. None was chosen after seeing a count.`,
  { x: 0.55, y: 1.14, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
    isTextBox: true, margin: 0, objectName: "sub" });

// ---- the frame itself, because the denominator is the whole method ----
card(s, { x: 0.55, y: 1.58, w: 12.2, h: 1.32, fill: TINT,
  kicker: "THE FRAME: EVERY TERM IS COUNTED INSIDE A SENTENCE, NEVER ON ITS OWN",
  kickerColor: TEAL, name: "frame" });

box(s, { x: 0.78, y: 2.1, w: 3.15, h: 0.52, t: '"she has  <term>"', fs: 12.5,
  line: BERRY, name: "fr-f" });
s.addText("÷", { x: 3.97, y: 2.1, w: 0.3, h: 0.52, fontSize: 17, bold: true,
  color: MUT, align: "center", valign: "middle", isTextBox: true, margin: 0,
  objectName: "fr-d" });
box(s, { x: 4.3, y: 2.1, w: 2.5, h: 0.52, t: '"she has"', fs: 12.5,
  line: MUT, name: "fr-b" });
arrow(s, { x: 6.94, y: 2.3, w: 0.42, h: 0.14, name: "fr-a" });
s.addText([
  { text: "the female rate for that term.  ", options: { bold: true, color: INK } },
  { text: "Dividing by the frame's own prefix count removes two things at once: that “he” simply occurs 2.4 times as often as “she”, and that some frames are commoner than others. Raw co-occurrence counts carry both and are meaningless without it.",
    options: { color: MUT } },
], { x: 7.5, y: 2.0, w: 5.05, h: 0.78, fontSize: 10, lineSpacing: 13,
     isTextBox: true, margin: 0, valign: "middle", objectName: "fr-t" });

// ---- the four families ----
const FAM = [
  { k: "FROM OUR OWN VIGNETTES", c: TEAL, n: String(TI.diagnosisVignette),
    h: "Diagnosis terms",
    ex: "pneumonia · malaria · asthma · prostate · cervical cancer · type 2 diabetes",
    b: "Every condition the vignettes test, plus its drugs and synonyms. Taken from the vignettes on purpose, so the data audit and the output audit speak about the same illnesses and a per-concept link between them is possible at all." },
  { k: "FROM THE LITERATURE ON DISMISSAL", c: BERRY, n: String(TI.diagnosisPsych),
    h: "Psychologizing terms",
    ex: "anxiety · depression · a panic attack · psychosomatic symptoms · hysteria",
    b: "The construct a dropped vignette was meant to carry. It survives here as corpus terms: the vocabulary by which a woman's physical complaint becomes a psychological one. Noun phrases only, so they fit the frame." },
  { k: "BECAUSE OUR HYPOTHESES ARE ABOUT DECISIONS", c: WARN, n: String(TI.decision),
    h: "Decision terms",
    ex: "an x-ray · a CT scan · a specialist · morphine · painkillers · surgery",
    b: "Counted in their own frames (“was referred for”, “was prescribed”), because nobody “has” an x-ray. Without this family the corpus evidence for H1 and H2 would be one inferential step away from what the models are actually scored on." },
  { k: "THE ONLY CLEAN THREE-WAY COMPARISON", c: PASS, n: "6",
    h: "Explicit subjects",
    ex: "“the woman” · “the man” · “the non-binary patient”",
    b: "Named subjects instead of pronouns. Counts are far smaller, and that is the price of avoiding the ambiguity in “they”, which is overwhelmingly plural in corpus text and so can never isolate non-binary reference." },
];
FAM.forEach((f, i) => {
  const x = 0.55 + i * 3.09;
  card(s, { x, y: 3.06, w: 2.95, h: 2.76, kicker: f.k, kickerColor: f.c,
    head: f.h, headSize: 13, headH: 0.3, name: "fam" + i });
  s.addText(f.n, { x: x + 2.1, y: 3.14, w: 0.72, h: 0.44, fontSize: 21, bold: true,
    color: f.c, fontFace: "Cambria", align: "right", isTextBox: true, margin: 0,
    objectName: "famn" + i });
  s.addText(f.ex, { x: x + 0.22, y: 3.9, w: 2.51, h: 0.74, fontSize: 9,
    color: f.c, fontFace: "Courier New", lineSpacing: 11.5, isTextBox: true,
    margin: 0, objectName: "famx" + i });
  s.addText(f.b, { x: x + 0.22, y: 4.68, w: 2.51, h: 1.0, fontSize: 8.8,
    color: MUT, lineSpacing: 11.5, isTextBox: true, margin: 0,
    objectName: "famb" + i });
});

card(s, { x: 0.55, y: 5.98, w: 12.2, h: 0.68, fill: "FDF3E3", name: "pw" });
s.addText([
  { text: `Measured is not the same as answerable. `, options: { bold: true, color: INK } },
  { text: `Of the ${TI.diagnosis} diagnosis terms, olmo-mix holds enough of ${TI.diagnosisPoweredOlmo} to support a reading and the Pile only ${TI.diagnosisPoweredPile}. A term with too few occurrences is reported as unpowered rather than as a zero, because a thin count and an absence are different findings.`,
    options: { color: MUT } },
], { x: 0.77, y: 6.1, w: 11.76, h: 0.46, fontSize: 10.5, lineSpacing: 13.5,
     isTextBox: true, margin: 0, valign: "middle", objectName: "pwt" });

srcLine(s, ["samulowitz2018", "hoffmann2001", "gao2020", "soldaini2024"]);
note(s, `[30s] This slide answers the question that decides whether the corpus audit means anything: where did the search terms come from.

Four families. The diagnosis terms are lifted from our own vignettes, so the data audit and the output audit are about the same illnesses. The psychologizing terms come from the dismissal literature. The decision terms exist because our hypotheses are about referrals and tests, not diagnoses. The explicit subjects are the one clean three-way comparison.

The frame is the part to dwell on. We never count a word on its own. We count it inside "she has", and we divide by how often "she has" occurs at all, which removes the pronoun base rate and the frame's own popularity in one step.

And ${TI.diagnosisPoweredOlmo} of ${TI.diagnosis} are powered in olmo-mix against ${TI.diagnosisPoweredPile} in the Pile, so the two corpora are not equally informative and we do not pretend they are.`);

// ============ WHAT THE TERMS RETURNED, AND WHAT WAS THROWN OUT === //
s = S("CONTENT", "Methodology", "What the vocabulary returns, and the terms we threw away");

// Two calibration terms whose answer is known in advance, then the pattern.
// If these two do not come out right, nothing else on the slide is readable.
const CAL = ["cervical cancer", "prostate"];
// Each term gets its own reading. Six rows all saying "matches the pattern"
// is a column that carries no information and reads as padding.
const PAT = [
  ["panic attacks", "psychologising of women's symptoms"],
  ["anxiety", "the same pattern, and the association behind our opening case"],
  ["depression", "documented over-attribution in women"],
  ["heart attack", "under-recognition of heart disease in women"],
  ["autism", "under-diagnosis in women and girls"],
  ["ADHD", "the same under-diagnosis, same direction"],
];
const sk = c => F.termSkew(c);

s.addText("Positive is female-skewed, negative is male-skewed, after the base rates are divided out. The first two are the calibration pair: their answer is known before we start, so if they come out wrong nothing below them is worth reading.",
  { x: 0.55, y: 1.14, w: 12.2, h: 0.34, fontSize: 12.5, color: MUT,
    isTextBox: true, margin: 0, objectName: "sub2" });

const trow = (c, cal, reading) => {
  const r = sk(c);
  const col = r.skew >= 0 ? BERRY : TEAL;
  return [
    { text: c, options: { color: INK, fontSize: 11.5, bold: cal,
      fill: { color: cal ? "FDF3E3" : PAPER } } },
    { text: (r.skew >= 0 ? "+" : "") + r.skew.toFixed(2), options: { color: col,
      fontSize: 11.5, bold: true, align: "right", fontFace: "Courier New",
      fill: { color: cal ? "FDF3E3" : PAPER } } },
    { text: r.female.toLocaleString("en-US"), options: { color: MUT, fontSize: 10.5,
      align: "right", fill: { color: cal ? "FDF3E3" : PAPER } } },
    { text: r.male.toLocaleString("en-US"), options: { color: MUT, fontSize: 10.5,
      align: "right", fill: { color: cal ? "FDF3E3" : PAPER } } },
    { text: reading, options: { color: cal ? WARN : MUT, fontSize: 9.5,
      italic: !cal, fill: { color: cal ? "FDF3E3" : PAPER } } },
  ];
};
const hd = t => ({ text: t, options: { bold: true, color: PAPER,
  fill: { color: INK }, fontSize: 10.5 } });
const hdR = t => ({ text: t, options: { bold: true, color: PAPER,
  fill: { color: INK }, fontSize: 10.5, align: "right" } });
s.addTable([[hd("Term"), hdR("Skew, log₂"), hdR("with “she”"),
             hdR("with “he”"), hd("Reading")]]
  .concat(CAL.map(c => trow(c, true, "known in advance")))
  .concat(PAT.map(([c, why]) => trow(c, false, why))),
  { x: 0.55, y: 1.58, w: 6.6, colW: [1.85, 0.95, 0.9, 0.85, 2.05], rowH: 0.38,
    border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
    margin: [0.03, 0.09, 0.03, 0.09], fontFace: "Calibri", autoPage: false });

card(s, { x: 7.4, y: 1.58, w: 5.35, h: 1.72, fill: TINT,
  kicker: "WHY THE CALIBRATION PAIR IS ON THE SLIDE", kickerColor: TEAL,
  body: "Cervical cancer and prostate have answers no measurement should get wrong. They are not findings. They are the evidence that the instrument points the right way before it is used on the terms whose answers we do not know, and they would catch a sign error that no amount of reading the code would.",
  bodySize: 10.5, name: "cal" });

card(s, { x: 7.4, y: 3.46, w: 5.35, h: 2.2, fill: "FBEEEC",
  kicker: "EIGHT TERMS WERE EXCLUDED, AND THE REASONS ARE PUBLISHED",
  kickerColor: FAIL, name: "exc" });
s.addText("stressed · stress · anxious · imagining · exaggerating · dramatic · hysterical · emotional",
  { x: 7.62, y: 3.98, w: 4.91, h: 0.5, fontSize: 10, color: FAIL,
    fontFace: "Courier New", lineSpacing: 12.5, isTextBox: true, margin: 0,
    objectName: "exct" });
s.addText([
  { text: "Every one is polysemous in the frame. ", options: { bold: true, color: INK } },
  { text: "“Stressed” is dominated by the speech verb, as in “he stressed that”, and the feasibility probe returned −0.858 on contaminated counts. “Anxious” is an adjective and does not fit “has X” at all; its probe counts were 6 and 9, unusable. Each was dropped BEFORE the main run, with the reason written into the config rather than into a paragraph nobody reads.",
    options: { color: MUT } },
], { x: 7.62, y: 4.52, w: 4.91, h: 1.02, fontSize: 9.5, lineSpacing: 12.5,
     isTextBox: true, margin: 0, objectName: "excb" });

card(s, { x: 0.55, y: 5.86, w: 12.2, h: 0.8, fill: INK, name: "tsel" });
s.addText([
  { text: "Term selection is a result, not a detail. ", options: { bold: true, color: PAPER } },
  { text: "A corpus audit can be steered by choosing what to search for, so the inclusions, the exclusions and the reasons for both are in configs/terms.yaml under version control, fixed before the counts were run. That file is the audit's answer to “how do we know you did not pick the terms that worked”.",
    options: { color: "BCD3D8" } },
], { x: 0.77, y: 6.0, w: 11.76, h: 0.56, fontSize: 11, lineSpacing: 14,
     isTextBox: true, margin: 0, valign: "middle", objectName: "tselt" });

note(s, `[28s] Read the top two rows first. Cervical cancer at ${sk("cervical cancer").skew.toFixed(1)} and prostate at ${sk("prostate").skew.toFixed(1)} are the calibration pair: their answers are known in advance, and getting them right is what licenses reading the rest.

Then the pattern underneath. Panic attacks, anxiety and depression lean female. Heart attack, autism and ADHD lean male. That is the documented human bias, found in the training text, before any model is involved.

The right-hand box is the one that protects us. Eight terms were excluded for polysemy before the main run, with the reasons written into the config. "He stressed that" is not a symptom. If somebody asks whether we picked terms that worked, the answer is that the file is in version control and dated.`);

module.exports = {};
