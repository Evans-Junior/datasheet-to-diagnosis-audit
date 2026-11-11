// Talk deck appendix. Not presented: these answer the questions the ten-slide
// spine deliberately leaves on the table, so a defence has the number to hand
// instead of promising to look it up.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, srcLine, card, stat, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const PC = F.positiveControl();
const ST = F.sizeTrend();
const R3 = F.rq3Spearman();
const R4C = F.rq4Control();
const I3 = F.i3Grid();
const CR = F.corpusReplication();
const CA = F.corpusAgreement();

pres.addSection({ title: "Appendix" });

// ---------------------------------------------- A1. the RQ3 decomposition --
{
  const s = S("CONTENT", "Appendix",
    "Appendix A: the scaling trend, reported three ways");
  const rows = [
    [`All ten models, floor-relative gap vs size`,
     `ρ = +${R3.spearman_rho.toFixed(3)}, p = ${R3.spearman_p.toFixed(4)}`,
     `Varies family, corpus and instruction tuning alongside size. A between-family contrast, not a scaling result.`, MUT],
    [`Gap component vs size`,
     `ρ = +${R3.spearman_rho_gap.toFixed(3)}, p = ${R3.spearman_p_gap.toFixed(5)}`,
     `The signal.`, PASS],
    [`Floor component vs size`,
     `ρ = +${R3.spearman_rho_floor.toFixed(3)}, p = ${R3.spearman_p_floor.toFixed(3)}`,
     `Not significant, which is what rules out "the instrument just got noisier".`, TEAL],
  ];
  rows.forEach((r, i) => {
    const y = 1.3 + i * 1.08;
    card(s, { x: 0.55, y, w: 12.2, h: 0.96, fill: TINT, name: "a1" + i });
    s.addText(r[0], { x: 0.8, y: y + 0.1, w: 4.1, h: 0.76, fontSize: 12, bold: true,
      color: INK, isTextBox: true, margin: 0, valign: "middle", lineSpacing: 14,
      objectName: "a1t" + i });
    s.addText(r[1], { x: 5.0, y: y + 0.1, w: 3.1, h: 0.76, fontSize: 12.5, bold: true,
      color: r[3], isTextBox: true, margin: 0, valign: "middle", objectName: "a1v" + i });
    s.addText(r[2], { x: 8.2, y: y + 0.1, w: 4.3, h: 0.76, fontSize: 10.5,
      color: MUT, isTextBox: true, margin: 0, valign: "middle", lineSpacing: 12.5,
      objectName: "a1d" + i });
  });
  card(s, { x: 0.55, y: 4.62, w: 12.2, h: 1.1, fill: "FDF4E3", name: "a1w",
    kicker: "THE TRAP THIS AVOIDS", kickerColor: WARN,
    head: "A floor that grows with scale can produce a scaling trend on its own",
    headH: 0.3, headSize: 13,
    body: "An earlier version of this analysis reported a significant NEGATIVE "
        + "trend that disappeared entirely once the gap and the floor were "
        + "separated. The decomposition is reported every time for that reason." });
  s.addText(`Interpretability caveat: ${ST.filter(r => r.nullInterpretable).length} of `
    + `${ST.length} models have an interpretable null under the placebo check, so `
    + `the trend is reported as exploratory.`,
    { x: 0.55, y: 5.86, w: 12.2, h: 0.4, fontSize: 11, color: MUT,
      isTextBox: true, margin: 0, objectName: "a1c" });
  tierBanner(s, { x: 0.55, y: 6.38, w: 12.2, h: 0.44, name: "tba1" });
  srcLine(s, ["biderman2023"], { name: "src58" });
  note(s, "If anyone asks why the headline is +0.948 and not +0.881, this is the "
   + "slide. The all-model number confounds three things at once.");
}

// ------------------------------------------- A2. elicitation sensitivity --
{
  const s = S("CONTENT", "Appendix",
    "Appendix B: the result we report against ourselves");
  s.addText(`Across three elicitation formats, all ${I3.nSignFlips} Pythia models `
    + `change the SIGN of their Group 2 margin. Same models, same vignettes, same `
    + `scoring: only the way the question is posed changes.`,
    { x: 0.55, y: 1.26, w: 12.2, h: 0.5, fontSize: 13, color: INK,
      isTextBox: true, margin: 0, lineSpacing: 16, objectName: "a2h" });
  // i3Grid returns series as {config: values[]}, not as a chart data array.
  // Reshape it the way part13.js does, so the two decks draw the same chart.
  const I3NAME = { baseline: "Question and answer format", cloze: "Cloze format",
                   fewshot: "Few-shot format" };
  s.addChart(pres.ChartType.bar,
    I3.configs.map(c => ({ name: I3NAME[c] || c, labels: I3.order,
                           values: I3.series[c] })), {
    x: 0.55, y: 1.9, w: 12.2, h: 3.5,
    barDir: "col", barGrouping: "clustered",
    chartColors: ["9BB3BA", BERRY, TEAL],
    showLegend: true, legendPos: "b", legendFontSize: 9.5, legendColor: INK,
    showValue: false,
    catAxisLabelColor: INK, catAxisLabelFontSize: 9.5, catAxisLabelPos: "low",
    catAxisLabelFontFace: "+mn-lt",
    valAxisLabelColor: MUT, valAxisLabelFontSize: 9,
    valAxisLabelFormatCode: "0.000", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3ECEE", size: 0.75 }, catGridLine: { style: "none" },
    barGapWidthPct: 30, showTitle: true,
    title: "Group 2 margin by elicitation format: every model crosses zero",
    titleFontSize: 11.5, titleColor: INK, titleFontFace: "+mn-lt",
  });
  card(s, { x: 0.55, y: 5.56, w: 12.2, h: 1.22, fill: "FBEEEC", name: "a2c",
    kicker: "WHY THIS IS IN THE DECK AT ALL", kickerColor: FAIL,
    head: "Because it limits our own claims, and omitting it would be the dishonest choice",
    headH: 0.3, headSize: 13,
    body: "A direction this unstable across formats cannot be assumed stable "
        + "across paraphrases, which is why paraphrase unanimity is measured and "
        + "reported for every effect rather than assumed. It is also the reason "
        + "the Pythia nulls are described as uninterpretable rather than as "
        + "evidence of fairness." });
  srcLine(s, ["yoo2026"], { name: "src102" });
  note(s, "Volunteer this one. An examiner who finds it themselves will weight it "
   + "far more heavily than one who is handed it.");
}

// ------------------------------------------ A3. the identifiability proof --
{
  const s = S("CONTENT", "Appendix",
    "Appendix C: why provenance is not recoverable, in one table");
  const rows = R4C.rows.slice().sort((a, b) => b.matched - a.matched);
  s.addTable([
    [{ text: "Model", options: { bold: true, color: PAPER, fill: { color: INK } } },
     { text: "Own corpus", options: { bold: true, color: PAPER, fill: { color: INK } } },
     { text: "ρ, own corpus", options: { bold: true, color: PAPER, fill: { color: INK }, align: "center" } },
     { text: "ρ, best other corpus", options: { bold: true, color: PAPER, fill: { color: INK }, align: "center" } },
     { text: "Own corpus wins?", options: { bold: true, color: PAPER, fill: { color: INK }, align: "center" } }],
    ...rows.map(r => [
      { text: r.model, options: { color: INK } },
      { text: r.ownCorpus, options: { color: MUT } },
      { text: r.matched.toFixed(3), options: { color: INK, align: "center" } },
      { text: r.crossedMax.toFixed(3), options: { color: INK, align: "center" } },
      { text: r.matchedWins ? "yes" : "no",
        options: { color: r.matchedWins ? PASS : FAIL, bold: true, align: "center" } },
    ]),
  ], { x: 0.55, y: 1.3, w: 12.2, colW: [3.0, 2.6, 2.1, 2.4, 2.1],
       rowH: 0.3, fontSize: 11, border: { type: "solid", color: "E3ECEE", pt: 0.5 },
       fill: { color: PAPER }, autoPage: false });
  s.addText(`Common support throughout: every cell is n = ${rows[0].n} over the same `
    + `concepts, so the only thing varying is which corpus the skew came from. `
    + `H4 predicted the own-corpus column would win. It wins ${R4C.wins} of ${R4C.n} `
    + `times, and the two corpora agree at ρ = ${CA.rho.toFixed(3)} on these `
    + `concepts, which is why.`,
    { x: 0.55, y: 5.0, w: 12.2, h: 0.62, fontSize: 11.5, color: INK,
      isTextBox: true, margin: 0, lineSpacing: 14, objectName: "a3c" });
  card(s, { x: 0.55, y: 5.74, w: 12.2, h: 1.04, fill: TINT, name: "a3n",
    kicker: "NOT THE SAME NUMBER AS THE REPLICATION FIGURE", kickerColor: TEAL,
    head: "", headH: 0,
    body: `r = ${CR.r.toFixed(3)} over ${CR.n} concepts answers "is the skew measure `
        + `an artefact of one corpus?" and the answer is no. ρ = ${CA.rho.toFixed(3)} `
        + `over ${CA.n} concepts answers "can provenance be attributed to one corpus `
        + `rather than the other?" and the answer is also no. They are different `
        + `questions over different concept sets and must not be swapped.` });
  srcLine(s, ["liu2024", "li2024", "elazar2024"], { name: "src144" });
  note(s, "This table is the answer to the hardest question we are likely to get, "
   + "which is 'if the corpora are interchangeable, what was the point of using "
   + "open data?' The answer: open data is what let us discover that they are "
   + "interchangeable on these concepts. No closed-model study could have found "
   + "it, and the next study can now select concepts on disagreement.");
}

module.exports = {};
