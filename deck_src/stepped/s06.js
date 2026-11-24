// SPOKEN 6 of 16: from one matrix to the scored corpus. [20s]
// Split off slide 5 so the matrix and its arithmetic are two separate beats.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, arrow, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const LV = F.liveVignettes();
const VG = F.vignetteGroups();
const N_MODELS = F.gateTable().length;
const ARMS = 4 * 2 * 3;
const OPTION_ROWS = 17280;

// Guard the multiplication the slide prints: 24 vignettes at 24 arms plus
// G3-02 doubled by its cue level is 624. If the set changes shape, stop the
// build rather than draw a sum that no longer adds up.
{
  const expected = (LV.live - 1) * ARMS + ARMS * 2;
  if (expected !== LV.livePrompts) {
    throw new Error(`s06.js: prompt arithmetic no longer holds. ${LV.live} `
      + `vignettes at ${ARMS} arms (one doubled by a cue level) gives ${expected}, `
      + `but vignettes.csv has ${LV.livePrompts} live prompts.`);
  }
}

const s = S("CONTENT", "2 Method", "From one matrix to the scored corpus");
K.mark("scale");

const CHAIN = [
  [`${4} × ${2}`, "identity × sex\nparameter cells", TEAL],
  [`× 3`, "paraphrases of the\nsame vignette", TEAL],
  [`${ARMS}`, "arms per\nvignette", INK],
  [`× ${LV.live}`, `live vignettes\nof ${LV.total}`, INK],
  [`${LV.livePrompts}`, "analysis-ready\nprompts", BERRY],
  [`× ${N_MODELS}`, "models, 2 open\ncorpora", BERRY],
  [`${OPTION_ROWS.toLocaleString("en-US")}`, "scored option\nrows", FAIL],
];
const CW = 1.52, CG = 0.26, MY = 1.9;
CHAIN.forEach(([big, sub, col], i) => {
  const x = 0.55 + i * (CW + CG);
  const last = i === CHAIN.length - 1;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: MY, w: CW, h: 1.5, rectRadius: 0.06,
    fill: { color: last ? "FBEEEC" : PAPER },
    line: { color: col, width: last ? 1.8 : 1.3 }, objectName: `ch-${i}-bg` });
  s.addText(big, { x: x + 0.05, y: MY + 0.2, w: CW - 0.1, h: 0.56, fontSize: 24,
    bold: true, color: col, align: "center", fontFace: "Cambria", isTextBox: true,
    margin: 0, objectName: `ch-${i}-n` });
  s.addText(sub, { x: x + 0.05, y: MY + 0.82, w: CW - 0.1, h: 0.56, fontSize: 9.5,
    color: MUT, align: "center", lineSpacing: 11.5, isTextBox: true, margin: 0,
    objectName: `ch-${i}-s` });
  if (!last) arrow(s, { x: x + CW + 0.03, y: MY + 0.66, w: 0.2, h: 0.18,
    color: "C8D7DB", name: `ch-a${i}` });
});

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 3.82, w: 12.23, h: 1.1, rectRadius: 0.06,
  fill: { color: TINT }, line: { color: TINT, width: 0 }, objectName: "bi-bg" });
s.addText([
  { text: "Byte-identical where it counts.  ", options: { bold: true, color: INK } },
  { text: `The clinical findings, the question and the option set are written once per vignette and reused verbatim across all ${ARMS} arms, so a difference in the answer cannot be a difference in the evidence. Every competing reason to withhold care — allergy, substance-use history, contraindication — is explicitly negated in the text.`,
    options: { color: MUT } },
], { x: 0.8, y: 3.92, w: 11.73, h: 0.92, fontSize: 12.5, lineSpacing: 16,
     valign: "middle", isTextBox: true, margin: 0, objectName: "bi" });

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.14, w: 12.23, h: 0.96, rectRadius: 0.06,
  fill: { color: "FDF4E3" }, line: { color: WARN, width: 1 }, objectName: "as-bg" });
s.addText([
  { text: "One asymmetry, disclosed.  ", options: { bold: true, color: WARN } },
  { text: `G3-02 (cardiac triage) carries a second cue level, so it contributes ${ARMS * 2} arms rather than ${ARMS}. That is why the total is ${LV.livePrompts} and not ${LV.live * ARMS}. Three of ${LV.total} vignettes are held back: ${VG.heldIds.join(", ")}.`,
    options: { color: MUT } },
], { x: 0.8, y: 5.22, w: 11.73, h: 0.8, fontSize: 11.5, lineSpacing: 15,
     valign: "middle", isTextBox: true, margin: 0, objectName: "as" });

// 20 seconds, about 44 words.
note(s, `[20s] The arithmetic, quickly. Eight cells, three paraphrases, ${ARMS} arms a vignette, ${LV.live} live vignettes, ${LV.livePrompts} prompts, ten models, ${OPTION_ROWS.toLocaleString("en-US")} scored option rows.

If asked why ${LV.livePrompts} and not ${LV.live * ARMS}: the cardiac triage vignette has a second cue level and contributes double.`);
