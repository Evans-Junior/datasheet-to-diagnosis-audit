const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const F = require("./figures.js");   // D090: counts are derived

// ============ SECTION: METHODOLOGY =============================== //
pres.addSection({ title: "Methodology" });
let s = S("SECTION", "Methodology", "3.  Methodology");
s.addText("The instrument, the prompt grid, the invariance rule, scoring, statistics and the gate", { placeholder: "body" });

// ============ 11. THE INSTRUMENT, four parts ===================== //
s = S("CONTENT", "Methodology", "What is being designed is an instrument, not a model");
s.addText("The deliverable is an audit instrument with four parts, in one reproducible repository.",
  { x: 0.55, y: 1.25, w: 12.2, h: 0.56, fontSize: 14, color: INK, margin: 0, isTextBox: true });
const inst = [
  { n: 1, h: "A clinical stimulus set", b: `${F.liveVignettes().live} live vignette templates expanded to ${F.liveVignettes().livePrompts} prompts. Each carries a correct answer quoted from a named guideline and a confidence tier.` },
  { n: 2, h: "A scoring pipeline", b: "Deterministic log-probability scoring of fixed options, with a four-test validation suite and a measured noise floor per model." },
  { n: 3, h: "A corpus measurement tool", b: "Exact templated n-gram counts over the Pile and the OLMo mix, base-rate normalised and centred." },
  { n: 4, h: "A pre-registered analysis plan", b: "Four directional hypotheses, a positive and a negative control, and a multiple-comparison correction, frozen before any model was scored." },
];
inst.forEach((c, i) => {
  const x = 0.55 + i * 3.1;
  card(s, { x, y: 1.72, w: 2.85, h: 2.3, name: "in" + i });
  badge(s, { x: x + 0.22, y: 1.92, n: c.n, d: 0.46, fs: 15, name: "inb" + i });
  s.addText(c.h, { x: x + 0.22, y: 2.5, w: 2.42, h: 0.5, fontSize: 13.5, bold: true,
    color: INK, lineSpacing: 16, margin: 0, isTextBox: true, objectName: "inh" + i });
  s.addText(c.b, { x: x + 0.22, y: 3.02, w: 2.42, h: 0.92, fontSize: 11.5, color: MUT,
    lineSpacing: 14, margin: 0, isTextBox: true, objectName: "inbb" + i });
});
card(s, { x: 0.55, y: 4.2, w: 12.2, h: 2.2, fill: INK, kicker: "WHO IT IS FOR, AND WHAT THEY MUST NOT GET",
  kickerColor: "7FD4C8", name: "stk" });
const stk = [
  ["Dataset publishers", "A measurable disclosure gap in their own documentation", "A claim that releasing data was a mistake"],
  ["Model releasers", "An instrument that tells a model with no gender gap apart from an instrument too insensitive to find one", "A benchmark score to optimise against"],
  ["Regulators and funders", "Evidence that open training data is necessary but not yet sufficient for accountability", "A ranked list of biased models"],
  ["Clinicians", "A reviewable statement of what each guideline requires, in a form they can correct", "Any suggestion that the vignettes are patients"],
];
const stkRows = [[
  { text: "Stakeholder", options: { bold: true, color: "7FD4C8", fill: { color: "1C4E59" }, fontSize: 11 } },
  { text: "What they get", options: { bold: true, color: "7FD4C8", fill: { color: "1C4E59" }, fontSize: 11 } },
  { text: "What they must not get", options: { bold: true, color: "E9A79C", fill: { color: "1C4E59" }, fontSize: 11 } },
]];
stk.forEach((r) => stkRows.push([
  { text: r[0], options: { bold: true, color: PAPER, fontSize: 10.5, fill: { color: INK } } },
  { text: r[1], options: { color: "BCD3D8", fontSize: 10.5, fill: { color: INK } } },
  { text: r[2], options: { color: "E9A79C", fontSize: 10.5, fill: { color: INK } } },
]));
s.addTable(stkRows, { x: 0.77, y: 4.72, w: 11.76, colW: [2.1, 5.6, 4.06], rowH: 0.32,
  border: { type: "solid", color: "2A5E6A", pt: 0.5 }, valign: "middle",
  margin: [0.04, 0.1, 0.04, 0.1], fontFace: "Calibri", autoPage: false });
note(s, "The right-hand column is the ethics of the design. It says what the instrument refuses to be used for, and those refusals are enforced in code, not just stated.");

// ============ 12. FOUR VIGNETTE GROUPS, diagram ================== //
s = S("CONTENT", "Methodology", "Four vignette groups, each with a job in the design");
const grp = [
  { n: "Group 1", c: "Sex-neutral conditions, unskewed in the corpus", j: "Discriminant null. Carries H3", v: "5", col: TEAL },
  { n: "Group 2", c: "Sex-specific conditions: pregnancy test, prostate, cervical screening", j: "Positive control. A null here invalidates the run", v: "3", col: PASS },
  { n: "Group 3", c: "Historically biased conditions: ADHD, autism, cardiac, pain", j: "Where an effect is predicted. Carries H1 and H2", v: "4", col: FAIL },
  { n: "Group 4", c: "No documented bias, gender clinically irrelevant", j: "Noise baseline, and since 3 November the source of the floor", v: "3", col: WARN },
];
grp.forEach((g, i) => {
  const x = 0.55 + i * 3.1;
  card(s, { x, y: 1.3, w: 2.85, h: 3.5, name: "gp" + i });
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.22, y: 1.5, w: 0.62, h: 0.62,
    fill: { color: g.col }, line: { color: g.col, width: 0 }, objectName: "gpc" + i });
  s.addText(g.v, { x: x + 0.22, y: 1.5, w: 0.62, h: 0.62, fontSize: 20, bold: true,
    color: PAPER, align: "center", valign: "middle", margin: 0, isTextBox: true, fontFace: "Cambria",
    objectName: "gpv" + i });
  s.addText("vignettes", { x: x + 0.92, y: 1.64, w: 1.7, h: 0.3, fontSize: 10.5, color: MUT,
    margin: 0, isTextBox: true, valign: "middle", objectName: "gpvl" + i });
  s.addText(g.n, { x: x + 0.22, y: 2.26, w: 2.42, h: 0.3, fontSize: 15, bold: true,
    color: g.col, margin: 0, isTextBox: true, objectName: "gpn" + i });
  s.addText(g.c, { x: x + 0.22, y: 2.6, w: 2.42, h: 1.0, fontSize: 11.5, color: INK,
    lineSpacing: 14, margin: 0, isTextBox: true, objectName: "gpcc" + i });
  s.addShape(pres.ShapeType.roundRect, { x: x + 0.22, y: 3.62, w: 2.42, h: 1.0, rectRadius: 0.05,
    fill: { color: PAPER }, line: { color: g.col, width: 1 }, objectName: "gpj" + i });
  s.addText(g.j, { x: x + 0.3, y: 3.68, w: 2.26, h: 0.88, fontSize: 11, bold: true, color: INK,
    lineSpacing: 13.5, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "gpjt" + i });
});
card(s, { x: 0.55, y: 4.98, w: 12.2, h: 1.42, fill: "E6F5F2", kicker: "WHY GROUP 2 IS THE MOST IMPORTANT GROUP",
  kickerColor: PASS, name: "g2w" });
s.addText("Group 2 is where the guideline answer genuinely does depend on the sex parameter. A model that understands the clinical task must show a difference there. A model that does not cannot be used to argue that an absence of gender difference anywhere else is an absence of bias. This single group is what separates a real null from a blind instrument, and it is reported before every other result.",
  { x: 0.77, y: 5.5, w: 11.76, h: 0.8, fontSize: 12.5, color: INK, lineSpacing: 16, margin: 0, isTextBox: true });
note(s, "Groups 1 and 4 both predict no effect but for different reasons: Group 1 is a clinical claim, Group 4 is an instrument baseline. Keeping them separate is what lets us measure the noise floor without contaminating the hypothesis test. That distinction became important on 3 November.");

// ============ 13. TEMPLATE EXPANSION, diagram ==================== //
const _LV5 = F.liveVignettes();
s = S("CONTENT", "Methodology",
      `How ${_LV5.live} templates become ${_LV5.livePrompts} prompts`);
s.addText("Every slot in a template is identity. The clinical text is identical across every arm of a vignette, so only the identity marking changes.",
  { x: 0.55, y: 1.22, w: 12.2, h: 0.56, fontSize: 14, color: INK, margin: 0, isTextBox: true });

// the multiplication chain
// D096. The chain, its product and the footnote were all typed. The product is
// 24 arms times the templates that carry one grid; G3-02 carries two, because
// it crosses a psychologizing cue with the identity grid, so the total is not
// simply templates times 24. Both numbers are computed from the prompt rows,
// and the footnote names however many rows are actually held out.
const _ARMS = 24;
const _base = _LV5.live * _ARMS;
const _extra = _LV5.livePrompts - _base;
const _VG5 = F.vignetteGroups();
const chain = [
  { t: String(_LV5.live), l: "live templates", c: INK },
  { t: "3", l: "paraphrases", c: TEAL },
  { t: "2", l: "sex parameter\nvalues", c: WARN },
  { t: "4", l: "arms: woman, man,\nnon-binary, blinded", c: BERRY },
];
chain.forEach((c, i) => {
  const x = 0.75 + i * 2.35;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.78, w: 1.75, h: 1.2, rectRadius: 0.07,
    fill: { color: PAPER }, line: { color: c.c, width: 1.5 }, objectName: "ch" + i });
  s.addText(c.t, { x, y: 1.86, w: 1.75, h: 0.6, fontSize: 30, bold: true, color: c.c,
    align: "center", fontFace: "Cambria", margin: 0, isTextBox: true, objectName: "cht" + i });
  s.addText(c.l, { x: x + 0.07, y: 2.42, w: 1.61, h: 0.5, fontSize: 10, color: MUT,
    align: "center", lineSpacing: 12, margin: 0, isTextBox: true, objectName: "chl" + i });
  if (i < 3) s.addText("x", { x: x + 1.78, y: 2.2, w: 0.54, h: 0.36, fontSize: 18, bold: true,
    color: "9BB3BA", align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "chx" + i });
});
arrow(s, { x: 10.1, y: 2.28, w: 0.5, h: 0.22, color: INK, name: "cheq" });
s.addShape(pres.ShapeType.roundRect, { x: 10.8, y: 1.78, w: 1.95, h: 1.2, rectRadius: 0.07,
  fill: { color: INK }, line: { color: INK, width: 0 }, objectName: "chtot" });
s.addText(String(_base), { x: 10.8, y: 1.86, w: 1.95, h: 0.6, fontSize: 30, bold: true, color: PAPER,
  align: "center", fontFace: "Cambria", margin: 0, isTextBox: true });
s.addText("prompts", { x: 10.8, y: 2.42, w: 1.95, h: 0.3, fontSize: 10, color: "BCD3D8",
  align: "center", margin: 0, isTextBox: true });
s.addText(`plus ${_extra} for G3-02, which carries a second crossed condition: a psychologizing cue, present and absent.  Total ${_LV5.livePrompts} analysis-ready.  ${_VG5.nHeld} more rows exist on disk and score nothing: ${_VG5.nRejected} rejected on clinical review, ${_VG5.nRetired} retired as superseded.`,
  { x: 0.75, y: 3.08, w: 12.0, h: 0.3, fontSize: 11.5, italic: true, color: MUT, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 3.52, w: 4.0, h: 2.9, fill: TINT, kicker: "WHY THREE PARAPHRASES", kickerColor: TEAL, name: "wp" });
s.addText("The same clinical facts written three ways, with the identity slots in different positions. Without this, a result might be an artefact of one sentence shape: if the gender word always sits in the same place, we are measuring that position as much as the word.",
  { x: 0.77, y: 4.06, w: 3.56, h: 1.3, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
card(s, { x: 4.75, y: 3.52, w: 4.0, h: 2.9, fill: TINT, kicker: "WHY NO PATIENT NAMES", kickerColor: BERRY, name: "wn" });
s.addText("A name carries ethnicity and class signal alongside gender, so a name-based manipulation would confound the thing being isolated. Gender is conveyed only by an explicit label and pronouns.",
  { x: 4.97, y: 4.06, w: 3.56, h: 1.3, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
card(s, { x: 8.95, y: 3.52, w: 3.8, h: 2.9, fill: "FDF3E3", kicker: "THE BLINDED ARM", kickerColor: WARN, name: "wb" });
s.addText("A fourth arm with identity removed but the sex parameter kept. It is a reference point, not a fourth gender, and every row carries a flag so the statistics cannot pool it into the three-way comparison. The identity clause is nearly empty of meaning there, so pooling it would quietly contaminate the contrast.",
  { x: 9.17, y: 4.06, w: 3.36, h: 2.2, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
note(s, `The arithmetic is ${_LV5.live} times 3 times 2 times 4 equals ${_base}, plus ${_extra} for the one vignette that carries a crossed cue, giving ${_LV5.livePrompts}. Every prompt has a matched partner identical in template, paraphrase, sex parameter and clinical text, differing only in identity marking. Those matched pairs are the unit the whole analysis is built on.`);

module.exports = {};
