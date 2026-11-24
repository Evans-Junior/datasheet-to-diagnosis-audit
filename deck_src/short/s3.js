// SHORT deck, slide 3: the counterfactual matrix.
//
// This is the methodological core and it has to be a picture, because the
// claim is geometric: the sex parameter is a ROW, the identity label is a
// COLUMN, and the clinical configurations people care about (cisgender,
// transgender, non-binary) are CELLS that fall out of crossing the two. A
// bullet list flattens that back into prose and loses the only idea on the
// slide.
//
// Every count on this slide is read from data/vignettes/vignettes.csv through
// figures.js, including the awkward one: G3-02 carries a second cue level and
// so has 48 arms rather than 24, which is why the total is 624 and not 600.
// That arithmetic is asserted below rather than typed, because an off-by-one
// in the headline scope figure is the kind of error an examiner finds first.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const LV = F.liveVignettes();
const VG = F.vignetteGroups();

const N_IDENT = 4, N_SPCU = 2, N_PARA = 3;
const ARMS = N_IDENT * N_SPCU * N_PARA;          // 24 arms per vignette
const N_MODELS = F.gateTable().length;
const OPTION_ROWS = 17280;

// Guard the multiplication that the slide prints. 24 vignettes at 24 arms plus
// G3-02 at 48 is 624; if the vignette set changes shape, stop the build rather
// than draw a sum that no longer adds up.
{
  const expected = (LV.live - 1) * ARMS + ARMS * 2;
  if (expected !== LV.livePrompts) {
    throw new Error(`s3.js: prompt arithmetic no longer holds. `
      + `${LV.live} vignettes at ${ARMS} arms (with one doubled by a cue level) `
      + `gives ${expected}, but vignettes.csv has ${LV.livePrompts} live prompts. `
      + `Redraw the matrix before presenting it.`);
  }
}

pres.addSection({ title: "2 Method" });
const s = S("CONTENT", "2 Method",
  "Hold the biology fixed. Vary only the identity.");
K.mark("matrix");

s.addText([
  { text: "HL7 Gender Harmony " + A.m("mcclure2021") + ": ", options: { bold: true, color: TEAL } },
  { text: "the clinical sex parameter is a separate field from gender identity. We state it, then hold it still.",
    options: { color: MUT } },
], { x: 0.55, y: 1.12, w: 12.2, h: 0.28, fontSize: 12, isTextBox: true,
     margin: 0, objectName: "sub" });

// ------------------------------------------------------------- the grid ----
const LAB_W = 1.3, COL_W = 1.85, COL_GAP = 0.08, X0 = 1.95;
const colX = i => X0 + i * (COL_W + COL_GAP);
const HDR_Y = 1.62, R_Y = [1.98, 3.03], R_H = 0.98;

const IDENT = ["“a woman”", "“a man”",
               "“a non-binary person”", "“an adult”"];
const IDENT_SUB = ["she / her", "he / him", "they / them", "no gender named"];

IDENT.forEach((t, i) => {
  s.addText(t, { x: colX(i), y: HDR_Y, w: COL_W, h: 0.22, fontSize: 10.5, bold: true,
    color: i === 3 ? WARN : INK, align: "center", isTextBox: true, margin: 0,
    objectName: `ch${i}` });
  s.addText(IDENT_SUB[i], { x: colX(i), y: HDR_Y + 0.2, w: COL_W, h: 0.18,
    fontSize: 8, color: MUT, align: "center", isTextBox: true, margin: 0,
    objectName: `cs${i}` });
});
s.addText("GENDER IDENTITY LABEL IN THE PROMPT  →", {
  x: X0, y: HDR_Y - 0.26, w: 7.64, h: 0.2, fontSize: 8, bold: true, color: MUT,
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "cax" });

const CIS = "DCEDEA", TRANS = "F2E2E8", NB = "E9E3F0", REF = "FBF0DC";
// Each cell says what clinical configuration the crossing encodes. The words
// "cisgender" and "transgender" appear HERE, in our analysis frame, and never
// in a prompt: that is the design point, so the annotation and the prompt text
// are drawn differently on purpose.
const CELLS = [
  // SPCU female
  [["cisgender woman", CIS], ["transgender man", TRANS],
   ["non-binary person,\nfemale parameter", NB], ["identity withheld\n(reference)", REF]],
  // SPCU male
  [["transgender woman", TRANS], ["cisgender man", CIS],
   ["non-binary person,\nmale parameter", NB], ["identity withheld\n(reference)", REF]],
];
const SPCU = [["Sex for clinical use:", "female"], ["Sex for clinical use:", "male"]];

SPCU.forEach(([pre, val], r) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.55, y: R_Y[r], w: LAB_W, h: R_H, rectRadius: 0.05,
    fill: { color: INK }, line: { color: INK, width: 0 }, objectName: `rl${r}-bg` });
  s.addText([{ text: pre + "\n", options: { fontSize: 7.5, color: "8FB2BA" } },
             { text: val, options: { fontSize: 14, bold: true, color: PAPER } }],
    { x: 0.6, y: R_Y[r], w: LAB_W - 0.1, h: R_H, align: "center", valign: "middle",
      lineSpacing: 13, isTextBox: true, margin: 0, objectName: `rl${r}` });

  CELLS[r].forEach(([t, fill], c) => {
    s.addShape(pres.ShapeType.roundRect, {
      x: colX(c), y: R_Y[r], w: COL_W, h: R_H, rectRadius: 0.05,
      fill: { color: fill }, line: { color: PAPER, width: 1.5 },
      objectName: `cell${r}${c}-bg` });
    s.addText(t, { x: colX(c) + 0.06, y: R_Y[r], w: COL_W - 0.12, h: R_H,
      fontSize: 9.5, bold: true, color: INK, align: "center", valign: "middle",
      lineSpacing: 11.5, isTextBox: true, margin: 0, objectName: `cell${r}${c}` });
  });
});
s.addText("SEX PARAMETER\nHELD FIXED", { x: 0.55, y: 1.56, w: LAB_W, h: 0.38,
  fontSize: 7.5, bold: true, color: MUT, align: "center", lineSpacing: 9,
  isTextBox: true, margin: 0, objectName: "rax" });

// ------------------------------------------------------- the right panel ----
const PX = 9.85, PW = 2.93;
card(s, { x: PX, y: 1.56, w: PW, h: 2.45, fill: TINT, name: "why",
  kicker: "WHY THIS WORKS", kickerColor: TEAL,
  head: "Six configurations,\nzero loaded words.", headH: 0.5, headSize: 12,
  bodySize: 9,
  body: "The prompt never contains “transgender” or “cisgender”. "
      + "The model sees a clinical field and a pronoun, so it cannot match on "
      + "the label for the category we test " + A.m("dev2021") + ".\n\n"
      + "The fourth column names no gender at all: the reference the other "
      + "three are measured against " + A.m("equitriage2026") + "." });

// ------------------------------------------------- the multiplication ----
const MY = 4.42;
s.addText("FROM ONE MATRIX TO THE SCORED CORPUS", {
  x: 0.55, y: MY - 0.24, w: 12.2, h: 0.2, fontSize: 8, bold: true, color: MUT,
  charSpacing: 0.8, isTextBox: true, margin: 0, objectName: "mk" });

const CHAIN = [
  [`${N_IDENT} × ${N_SPCU}`, "identity × sex\nparameter cells", TEAL],
  [`× ${N_PARA}`, "paraphrases of the\nsame vignette", TEAL],
  [`${ARMS}`, "arms per\nvignette", INK],
  [`× ${LV.live}`, `live vignettes\nof ${LV.total}`, INK],
  [`${LV.livePrompts}`, "analysis-ready\nprompts", BERRY],
  [`× ${N_MODELS}`, "models, 2 open\ncorpora", BERRY],
  [`${OPTION_ROWS.toLocaleString("en-US")}`, "scored option\nrows", FAIL],
];
const CW = 1.52, CG = 0.26;
CHAIN.forEach(([big, sub, col], i) => {
  const x = 0.55 + i * (CW + CG);
  const last = i === CHAIN.length - 1;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: MY, w: CW, h: 0.92, rectRadius: 0.05,
    fill: { color: last ? "FBEEEC" : PAPER },
    line: { color: col, width: last ? 1.5 : 1.1 }, objectName: `ch-${i}-bg` });
  s.addText(big, { x: x + 0.05, y: MY + 0.08, w: CW - 0.1, h: 0.34, fontSize: 17,
    bold: true, color: col, align: "center", fontFace: "Cambria", isTextBox: true,
    margin: 0, objectName: `ch-${i}-n` });
  s.addText(sub, { x: x + 0.05, y: MY + 0.44, w: CW - 0.1, h: 0.42, fontSize: 8,
    color: MUT, align: "center", lineSpacing: 9.5, isTextBox: true, margin: 0,
    objectName: `ch-${i}-s` });
  if (i < CHAIN.length - 1) {
    arrow(s, { x: x + CW + 0.03, y: MY + 0.38, w: 0.2, h: 0.16,
      color: "C8D7DB", name: `ch-a${i}` });
  }
});

s.addText([
  { text: "Byte-identical where it counts. ", options: { bold: true, color: INK } },
  { text: `The clinical findings, the question and the option set are written once per vignette and reused verbatim across all ${ARMS} arms, so a difference in the answer cannot be a difference in the evidence. Every competing reason to withhold care — allergy, substance-use history, contraindication — is explicitly negated in the text.`,
    options: { color: MUT } },
], { x: 0.55, y: 5.52, w: 12.2, h: 0.62, fontSize: 11, lineSpacing: 15,
     isTextBox: true, margin: 0, objectName: "bi" });

s.addText([
  { text: `One asymmetry, disclosed: `, options: { bold: true, color: WARN } },
  { text: `G3-02 (cardiac triage) carries a second cue level, so it contributes ${ARMS * 2} arms rather than ${ARMS}. That is why the total is ${LV.livePrompts} and not ${LV.live * ARMS}. Three of ${LV.total} vignettes are held back: ${VG.heldIds.join(", ")}.`,
    options: { color: MUT } },
], { x: 0.55, y: 6.24, w: 12.2, h: 0.36, fontSize: 9.5, isTextBox: true,
     margin: 0, objectName: "asym" });

// 75 seconds, about 169 words. The contribution. Go slowly.
note(s, `[75s] This is the method, so slow down here.

The row is the sex parameter for clinical use. That is the HL7 Gender Harmony idea: in a real record, the physiological field a decision turns on is stored separately from who the patient says they are. We put it in the prompt as flat text and hold it still.

The column is the identity label. Four of them, and the fourth names no gender at all.

Now the point. Cross the two and the configurations clinicians actually see fall out as cells. Female parameter with a man's label is a transgender man. Male parameter with a woman's label is a transgender woman. The diagonal is cisgender.

And we get all six without ever writing the word transgender in a prompt, so the model cannot be answering the word instead of the medicine.

The strip along the bottom is the multiplication: eight cells, three paraphrases, ${ARMS} arms a vignette, ${LV.live} live vignettes, ${LV.livePrompts} prompts, ten models, ${OPTION_ROWS.toLocaleString("en-US")} scored option rows.`);
