// Talk deck, beats 7, 8 and 9: what the models do, where it comes from, and
// what the documentation said about it.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, srcLine, card, stat, box, note, badge, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const PC = F.positiveControl();
const MG = F.merging();
const PT = F.postTraining();
const H1 = F.hypothesis("H1"), H2 = F.hypothesis("H2"), H3 = F.hypothesis("H3");
const R3 = F.rq3Spearman();
const R4C = F.rq4Control();
const R4T = F.rq4Trend();
const CR = F.corpusReplication();
const CA = F.corpusAgreement();
const CQ = F.corpusQueries();
const Q6 = F.rq6Status();
const VG = F.vignetteGroups();

pres.addSection({ title: "5 Findings" });

// --------------------------------------- 7. what the models actually do ----
{
  const s = S("CONTENT", "5 Findings",
    "Finding 1: capability and identity-confusion arrive together");

  const above = MG.filter(m => m.above);
  s.addChart(pres.ChartType.bar, [{
    name: "Identity/SPCU merging, multiples of the model's own noise floor",
    labels: MG.map(m => m.model),
    values: MG.map(m => m.timesFloor),
  }], {
    x: 0.55, y: 1.3, w: 7.5, h: 3.5,
    barDir: "bar", chartColors: MG.map(m => m.above ? FAIL : "9BB3BA"),
    showLegend: false, showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: "0.0", dataLabelFontSize: 9, dataLabelColor: INK,
    catAxisLabelColor: INK, catAxisLabelFontSize: 9.5, catAxisLabelPos: "low",
    catAxisLabelFontFace: "+mn-lt",
    valAxisLabelColor: MUT, valAxisLabelFontSize: 9,
    valAxisLabelFormatCode: "0.0", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3ECEE", size: 0.75 }, catGridLine: { style: "none" },
    barGapWidthPct: 45, showTitle: true,
    title: "How far a gender-identity label moves a sex-dependent clinical answer",
    titleFontSize: 11.5, titleColor: INK, titleFontFace: "+mn-lt",
  });

  card(s, { x: 8.28, y: 1.3, w: 4.5, h: 1.68, fill: "FBEEEC", name: "mg1",
    kicker: "IDENTITY/SPCU MERGING", kickerColor: FAIL,
    head: `${above.length} of ${MG.length} models above their own floor`,
    headH: 0.52, headSize: 13.5,
    body: `${above.map(m => m.model).join(", ")}. Same direction on all `
        + `${MG[0].nVignettes} control vignettes in each case. Every other model `
        + `sits inside its floor with mixed signs, which is the signature of `
        + `noise, not of fairness.` });

  card(s, { x: 8.28, y: 3.12, w: 4.5, h: 1.68, fill: "FDF4E3", name: "mg2",
    kicker: "AND POST-TRAINING MAKES IT WORSE", kickerColor: WARN,
    head: `${PT.timesFloor.toFixed(1)}× the combined floor`, headH: 0.38, headSize: 15,
    body: `${PT.base} merges at ${PT.mergingBase.toFixed(3)}, already above its `
        + `own floor. The tuned model of the same size, corpus and pretraining `
        + `merges at ${PT.mergingTuned.toFixed(3)} — ${PT.ratio.toFixed(1)} times as `
        + `much, a rise of ${PT.delta.toFixed(3)} against a combined floor of `
        + `${PT.floorCombined.toFixed(4)}.` });

  const hyp = [
    { n: "H1", t: `Referral endorsed less readily for the woman arm`,
      v: `p = ${H1.pExact.toFixed(4)} at a resolution limit of ${H1.pResolution.toFixed(4)}`,
      d: `k = ${H1.k} vignettes. A PERFECT sign flip, and still not below .05. Unresolvable by design, not null.`, c: WARN },
    { n: "H3", t: `No systematic gap where the corpus is unskewed`,
      v: `Equivalence SUPPORTED, 95% CI [${H3.ciLo.toFixed(4)}, ${H3.ciHi.toFixed(4)}]`,
      d: `Inside a margin of ${H3.margin.toFixed(4)}, at k = ${H3.k} the test could have reached p = ${H3.pResolution.toFixed(4)}. It had the power to reject and did not.`, c: PASS },
  ];
  hyp.forEach((h, i) => {
    const y = 4.86 + i * 0.80;
    card(s, { x: 0.55, y, w: 12.2, h: 0.72, fill: TINT, name: "hy" + i });
    badge(s, { x: 0.74, y: y + 0.16, n: h.n, d: 0.4, fs: 11, color: h.c, name: "hb" + i });
    s.addText(h.t, { x: 1.26, y: y + 0.06, w: 3.5, h: 0.6, fontSize: 11.5,
      bold: true, color: INK, isTextBox: true, margin: 0, valign: "middle",
      lineSpacing: 13, objectName: "hyt" + i });
    s.addText(h.v, { x: 4.84, y: y + 0.06, w: 3.3, h: 0.6, fontSize: 11.5,
      bold: true, color: h.c, isTextBox: true, margin: 0, valign: "middle",
      lineSpacing: 13, objectName: "hyv" + i });
    s.addText(h.d, { x: 8.24, y: y + 0.06, w: 4.3, h: 0.6, fontSize: 10.5,
      color: MUT, isTextBox: true, margin: 0, valign: "middle", lineSpacing: 12.5,
      objectName: "hyd" + i });
  });
  tierBanner(s, { x: 0.55, y: 6.62, w: 12.2, h: 0.40, name: "tb7" });
  srcLine(s, ["mcclure2021", "hoffmann2001", "chen2008"], { y: 6.34, name: "src8" });
  note(s, "The merging result is the project's strongest single finding and it is "
   + "an ethics finding, not a benchmark score. Read the chart with the gate "
   + "slide: the three models that pass the gate are the three that merge. So "
   + "capability at reading clinical sex and the error of treating a stated "
   + "identity as clinical sex arrive together. For a trans patient that is the "
   + "worst possible combination, because the model is confident and wrong in a "
   + "direction that reroutes care. On H1, be precise: we are NOT claiming a "
   + "null. With four vignettes the arithmetic cannot produce a p below 0.0625, "
   + "and we observed the most extreme outcome available.");
}

// ----------------------------------------- 8. where does it come from? ----
{
  const s = S("CONTENT", "5 Findings",
    "Finding 2: the link is real, and it is post-training");

  card(s, { x: 0.55, y: 1.3, w: 3.95, h: 2.2, fill: TINT, name: "l1",
    kicker: "RQ1  ·  THE CORPUS", kickerColor: TEAL,
    head: "Skew is measurable and it replicates", headH: 0.52, headSize: 13,
    body: `${CQ.cached.toLocaleString("en-US")} exact-substring queries, `
        + `${CQ.failed === 0 ? "zero" : CQ.failed} failed. The health-concept skew `
        + `measure replicates across corpora at r = ${CR.r.toFixed(3)} over `
        + `${CR.n} concepts powered in both, so it is not an artefact of one corpus.` });

  card(s, { x: 4.69, y: 1.3, w: 3.95, h: 2.2, fill: TINT, name: "l2",
    kicker: "RQ3  ·  SCALE", kickerColor: BERRY,
    head: `Gap grows with size, ρ = ${R3.spearman_rho_raw_gap.toFixed(3)}`, headH: 0.52, headSize: 13,
    body: `Within the Pythia family, training data held constant. Decomposed on `
        + `purpose: the gap tracks size at ρ = ${R3.spearman_rho_raw_gap.toFixed(3)} `
        + `while the noise floor does not (ρ = ${R3.spearman_rho_floor.toFixed(3)}, `
        + `p = ${R3.spearman_p_floor.toFixed(2)}), so the trend is the signal and `
        + `not the instrument.` });

  card(s, { x: 8.83, y: 1.3, w: 3.95, h: 2.2, fill: "FBEEEC", name: "l3",
    kicker: "RQ4  ·  THE CONTROL THAT FAILS", kickerColor: FAIL,
    head: `Matched beats crossed in ${R4C.wins} of ${R4C.n}`, headH: 0.52, headSize: 13,
    body: `Pre-registration: a model should track ITS OWN corpus more closely `
        + `than one it never saw. It does not. On the audited concepts the two `
        + `corpora agree at ρ = ${CA.rho.toFixed(3)}, so provenance is not `
        + `recoverable. Open data is necessary for this question and not sufficient.` });

  s.addText("The linkage is not a scale effect. It is a post-training effect.",
    { x: 0.55, y: 3.72, w: 12.2, h: 0.3, fontSize: 15, bold: true, color: INK,
      isTextBox: true, margin: 0, objectName: "lh" });

  // The Pythia ladder flat, then the two OLMo points. Null leaves a gap, which
  // is what keeps the two series honest about not sharing an x position.
  const lab = R4T.rows.map(r => r.model);
  s.addChart(pres.ChartType.bar, [
    { name: "Pythia ladder (Pile, pretrained only)",
      labels: lab,
      values: R4T.rows.map(r => r.family === "pythia" ? r.rho : null) },
    { name: "OLMo 2 (olmo-mix)",
      labels: lab,
      values: R4T.rows.map(r => r.family === "olmo" ? r.rho : null) },
  ], {
    x: 0.55, y: 4.1, w: 8.4, h: 2.18,
    barDir: "col", chartColors: ["9BB3BA", PASS],
    showLegend: true, legendPos: "b", legendFontSize: 9.5, legendColor: INK,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00",
    dataLabelFontSize: 8.5, dataLabelColor: INK,
    catAxisLabelColor: INK, catAxisLabelFontSize: 8.5, catAxisLabelPos: "low",
    catAxisLabelFontFace: "+mn-lt",
    valAxisLabelColor: MUT, valAxisLabelFontSize: 9,
    valAxisLabelFormatCode: "0.00", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3ECEE", size: 0.75 }, catGridLine: { style: "none" },
    barGapWidthPct: 45, showTitle: true,
    title: "Corpus skew against output gap, per model (Spearman ρ, model's own corpus)",
    titleFontSize: 11, titleColor: INK, titleFontFace: "+mn-lt",
  });

  card(s, { x: 9.18, y: 4.1, w: 3.6, h: 2.18, fill: "E6F6F2", name: "l4",
    kicker: "READ THE TWO TOGETHER", kickerColor: PASS,
    head: `+${R4T.postTrainingDelta.toFixed(3)} from alignment alone`,
    headH: 0.52, headSize: 14,
    body: `A hundredfold in parameters with the corpus held constant gives no `
        + `linkage: \u03C1 = ${R4T.pyRho.toFixed(3)}, ${R4T.nNegative} of `
        + `${R4T.pythia.length} sizes NEGATIVE. Base ${R4T.base.rho.toFixed(3)} `
        + `against Instruct ${R4T.inst.rho.toFixed(3)} is the same size, corpus `
        + `and pretraining.` });
  tierBanner(s, { x: 0.55, y: 6.62, w: 12.2, h: 0.40, name: "tb8" });
  srcLine(s, ["liu2024", "feng2023", "gao2020", "olmo2025", "li2024"], { y: 6.34, name: "src9" });
  note(s, "This is where the project answers its own title question, and the "
   + "answer has two halves that must not be merged. Yes, corpus skew predicts "
   + "the output gap, but in exactly one model of nine, and that model is the "
   + "instruction-tuned one. Seven pretrained-only models across a hundredfold "
   + "range of scale show nothing, six of them negative. So pretraining scale is "
   + "not the mechanism; the alignment step is where corpus statistics become "
   + "clinical behaviour. The second half is the negative result we pre-registered "
   + "a control for and the control failed: because the two corpora are near "
   + "duplicates on these concepts, no causal path to a NAMED corpus can be "
   + "claimed. That is a requirement for whoever runs this design next.");
}

// ------------------------------------------------- 9. the datasheets ------
{
  const s = S("CONTENT", "5 Findings",
    "Finding 3: the documentation never joins gender to health");

  const cells = [
    { n: "9", l: "of 10 documents", c: FAIL,
      b: "never join demographic composition to health-domain risk in a single "
       + "passage. The one that does, the Pile datasheet, joins them to assert "
       + "adequacy rather than risk. Tested mechanically: in eight of the ten, no "
       + "demographic term and health term fall within 400 characters of each other." },
    { n: "0", l: "of 30 search terms", c: FAIL,
      b: "return a single hit in the olmo-mix-1124 dataset card, the document a "
       + "practitioner reads before using the corpus OLMo 2 is trained on. It is "
       + "a schema block, a size table and a licence." },
    { n: "2×", l: "asked, never answered", c: WARN,
      b: "The Datasheets-for-Datasets question asks for subpopulations “and "
       + "what is their distribution”. The Pile datasheet is asked twice and "
       + "answers with the PRESENCE of papers that study gender. Presence is not "
       + "distribution, and the distribution is what RQ1 then measured." },
  ];
  cells.forEach((c, i) => {
    const x = 0.55 + i * 4.17;
    card(s, { x, y: 1.3, w: 3.86, h: 2.42, fill: TINT, name: "d6" + i });
    stat(s, { x: x + 0.24, y: 1.48, w: 3.4, n: c.n, label: c.l, color: c.c,
      size: 38, nh: 0.74, name: "d6s" + i });
    s.addText(c.b, { x: x + 0.24, y: 2.46, w: 3.4, h: 1.12, fontSize: 10.5,
      color: MUT, isTextBox: true, margin: 0, lineSpacing: 12.5,
      objectName: "d6b" + i });
  });

  card(s, { x: 0.55, y: 3.94, w: 6.0, h: 1.5, fill: "E6F6F2", name: "d6a",
    kicker: "WHAT THEY DID DISCLOSE, STATED FAIRLY", kickerColor: PASS,
    head: "The Pile paper measured gender in the corpus", headH: 0.32, headSize: 13,
    body: "Section 6.4.1 reports pronoun co-occurrence with a stated method, and "
        + "the Pythia card names gender among documented biases and points at it. "
        + "So the finding is not that nobody looked." });

  card(s, { x: 6.78, y: 3.94, w: 6.0, h: 1.5, fill: "FBEEEC", name: "d6b2",
    kicker: "WHAT THAT MAKES THE FINDING", kickerColor: FAIL,
    head: "Gender was measured. Medical content was advertised. Never together.",
    headH: 0.52, headSize: 13,
    body: "“We included PMC in the hopes that it will benefit potential "
        + "downstream applications to the medical domain.” The intersection "
        + "is the empty cell." });

  s.addText(`Status: the ${Q6.nTerms}-term sweep across ${Q6.nDocs} documents and the `
    + `window test are complete and are mechanical text facts. The graded coding on `
    + `eight dimensions is NOT a result yet: the codebook requires two independent `
    + `human passes and Cohen's κ ≥ 0.70 before any code is citable, and `
    + `${Q6.coded ? "that is done" : "those passes are outstanding"}.`,
    { x: 0.55, y: 5.62, w: 12.2, h: 0.62, fontSize: 11, color: WARN, bold: true,
      isTextBox: true, margin: 0, lineSpacing: 13, objectName: "d6st" });
  s.addText("Documents coded: the Pile paper and datasheet, the Pythia paper and "
    + "card, Dolma, the olmo-mix card, the OLMo 2 report and card, and the Qwen3 "
    + "report and card as a closed-data comparator.",
    { x: 0.55, y: 6.3, w: 12.2, h: 0.44, fontSize: 10.5, color: MUT,
      isTextBox: true, margin: 0, lineSpacing: 12.5, objectName: "d6l" });
  srcLine(s, ["gebru2021", "gao2020", "biderman2022", "soldaini2024", "qwen2025"], { name: "src241" });
  note(s, "Be scrupulous here, because this is the slide most open to a fair "
   + "objection. Do not say the documentation ignores gender: the Pile paper "
   + "measures it, and saying otherwise is a factual error a reviewer who knows "
   + "the paper will catch immediately. The finding is the empty intersection. "
   + "They measured gender, they advertised the medical content, and no document "
   + "in the set connects the two. Also state plainly that the graded coding is "
   + "not finished, because presenting an AI-drafted code as a human-coded result "
   + "would be exactly the kind of thing this project exists to criticise.");
}

module.exports = {};
