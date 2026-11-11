// Talk deck, beats 5 and 6: calibrating the instrument, then trying to break it.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, note, badge, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const VG = F.vignetteGroups();
const PC = F.positiveControl();
const H1 = F.hypothesis("H1");
const PA = F.paraphrase();
const CT = F.contamination();
const I3 = F.i3Grid();
const GR = F.gateRerun();

pres.addSection({ title: "3 Calibration" });

// ----------------------------------- 5. the floor and the §6 gate ----------
{
  const s = S("CONTENT", "3 Calibration",
    "First, measure what no gap looks like");

  card(s, { x: 0.55, y: 1.26, w: 6.0, h: 1.78, fill: TINT, name: "fl",
    kicker: "THE NUISANCE FLOOR  ·  GROUP 4", kickerColor: WARN,
    head: `${VG.groups[4].length} clinically inert vignettes`, headH: 0.32, headSize: 13.5,
    body: "Nothing about them should depend on gender, so whatever gap appears "
        + "is the instrument's own jitter. Measured per model AND per option "
        + "geometry, because the floor is not a constant: it is not even "
        + "monotonic in model size." });

  const nIns = PC.filter(r => r.gate !== "SENSITIVE").length;
  card(s, { x: 6.78, y: 1.26, w: 6.0, h: 1.78, fill: "FBEEEC", name: "gt",
    kicker: "THE POSITIVE-CONTROL GATE  ·  GROUP 2", kickerColor: FAIL,
    head: `${nIns} of ${PC.length} models cannot see clinical sex at all`,
    headH: 0.52, headSize: 13.5,
    body: "Group 2 is where the guideline says the correct answer DOES differ by "
        + "sex. A model that does not move here is not unbiased. It is blind, "
        + "and every null it produces elsewhere is uninterpretable." });

  // The gate, drawn from the table. Margin over floor, so the zero line is the
  // model's own measured resolution rather than an arbitrary threshold.
  const ord = PC.slice().sort((a, b) => a.overFloor - b.overFloor);
  s.addChart(pres.ChartType.bar, [{
    name: "Gate margin over the model's own noise floor",
    labels: ord.map(r => r.model),
    values: ord.map(r => r.overFloor),
  }], {
    x: 0.55, y: 3.18, w: 12.2, h: 2.72,
    barDir: "col", chartColors: ord.map(r => r.gate === "SENSITIVE" ? PASS : FAIL),
    showLegend: false, showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: "0.000", dataLabelFontSize: 9, dataLabelColor: INK,
    catAxisLabelColor: INK, catAxisLabelFontSize: 9.5, catAxisLabelPos: "low",
    catAxisLabelFontFace: "+mn-lt", catAxisLabelRotate: 0,
    valAxisLabelColor: MUT, valAxisLabelFontSize: 9,
    valAxisLabelFormatCode: "0.00", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3ECEE", size: 0.75 },
    catGridLine: { style: "none" }, barGapWidthPct: 55,
    showTitle: true, title: "Can the model detect sex where the guideline says it must? (margin over its own floor)",
    titleFontSize: 11.5, titleColor: INK, titleFontFace: "+mn-lt",
  });
  s.addText("Green passes. Red is insensitive. The three that pass are the three "
    + "largest and most capable models in the roster.",
    { x: 0.55, y: 5.96, w: 12.2, h: 0.3, fontSize: 11, color: MUT,
      isTextBox: true, margin: 0, objectName: "gc" });
  tierBanner(s, { x: 0.55, y: 6.34, w: 12.2, h: 0.46, name: "tb5" });
  note(s, "This is a gate, not a result, and the distinction matters for the "
   + "ethics argument. If a model shows no gender effect on the sex-neutral "
   + "vignettes, there are two explanations: it is fair, or it cannot read "
   + "gender. Group 2 separates them, and seven of ten models turn out to be in "
   + "the second category. So for seven of ten, a report saying 'no bias "
   + "detected' would be true and completely misleading. That is the false-equity "
   + "finding and it comes straight out of this chart.");
}

// ------------------------- 6. stress-testing the apparatus (the insertion) --
pres.addSection({ title: "4 Validation" });
{
  const s = S("CONTENT_DARK", "4 Validation",
    "Four ways we tried to break our own result");

  const nIns = PC.filter(r => r.gate !== "SENSITIVE").length;
  const cells = [
    { k: "1  FLOOR GEOMETRY", h: `${GR.oldPasses} of ${GR.n}  \u2192  ${GR.newPasses} of ${GR.n}`,
      b: "The first floor was measured in an abstract 4-option frame and applied "
       + "to binary items. Re-measured in the matched geometry, the gate verdict "
       + "changed for two models. A floor in the wrong frame does not add noise, "
       + "it manufactures or destroys the finding.", c: WARN },
    { k: "2  EXACT PERMUTATION NULLS", h: `p cannot go below 2⁻ᵏ`,
      b: `With k clusters the finest one-sided p that exists is 2⁻ᵏ. H1 `
       + `runs on k = ${H1.k} referral vignettes, so its floor is `
       + `p = ${H1.pResolution.toFixed(4)}. The observed p IS that value: a `
       + `perfect sign flip on every cluster, and still not below .05. That is a `
       + `limit of the design, not a null result.`, c: FAIL },
    { k: "3  PARAPHRASE STABILITY", h: `${(PA.pctUnanimous * 100).toFixed(1)}% keep their sign`,
      b: `Of the ${PA.nClears.toLocaleString("en-US")} effects large enough to `
       + `clear their own floor, ${PA.nUnanimous.toLocaleString("en-US")} keep the `
       + `same sign under all three paraphrasings and ${PA.nNotUnanimous} do not. `
       + `Those ${PA.nNotUnanimous} are one rewording away from vanishing and are `
       + `not reported as robust.`, c: TEAL },
    { k: "4  MEMORISATION AUDIT", h: `${CT.targetLongPresent} of ${CT.nTargetLong} long spans found`,
      b: `If a model were reciting the guideline it would be answering from `
       + `memory, not from corpus statistics. No long guideline span from any `
       + `target vignette occurs in either corpus, while the deliberately generic `
       + `control span appears in all ${CT.nCtrl} of its queries, so the probe works.`, c: PASS },
  ];
  cells.forEach((c, i) => {
    const x = 0.55 + (i % 2) * 6.23;
    const y = 1.3 + Math.floor(i / 2) * 2.3;
    card(s, { x, y, w: 5.97, h: 2.14, fill: "14454F", name: "vl" + i,
      kicker: c.k, kickerColor: c.c, head: c.h, headH: 0.38, headSize: 16,
      headColor: PAPER, body: c.b, bodyColor: "B9D2D7", bodySize: 11 });
  });

  s.addText(`A fifth, reported against our own interest: across three elicitation `
    + `formats, all ${I3.nSignFlips} Pythia models CHANGE THE SIGN of their Group 2 `
    + `margin. A direction that unstable across formats cannot be assumed stable `
    + `anywhere, and that is why stability is measured rather than assumed.`,
    { x: 0.55, y: 6.04, w: 12.2, h: 0.62, fontSize: 11.5, color: "7FD4C8",
      isTextBox: true, margin: 0, lineSpacing: 14, objectName: "i3" });
  note(s, "This is the slide that should win the defence, so do not rush it. The "
   + "argument is not 'we ran an audit'. It is 'we ran an audit, then spent "
   + "longer trying to falsify it than running it'. Each box changed a number we "
   + "had already written down. Box 1 changed a verdict. Box 2 means our headline "
   + "hypothesis provably cannot reach significance with four vignettes, which we "
   + "state rather than hide. Box 3 disqualifies 267 of our own effects. Box 5 is "
   + "the one to volunteer: it is evidence against the stability of our own "
   + "instrument and we report it anyway.");
}

module.exports = {};
