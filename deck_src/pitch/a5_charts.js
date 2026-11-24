// ACT 5, the chart backups. Nothing here is spoken in the five minutes.
//
// WHY THESE EXIST AND WHY THERE ARE ONLY FOUR. The ask was "the important
// graphs, in the backup, in case we are given a minute more". A chart you flip
// to under time pressure has about ten seconds to land, so each of these
// carries ONE claim, states it in the title, and puts the sentence a presenter
// would say in a card beside it. The paper's figures are not reused: they are
// drawn at 3.3in column width for print and would be unreadable from the back
// of a room.
//
// They are native PowerPoint charts, not images, for the same reason the rest
// of the decks use addChart: the numbers stay inspectable, they take the theme,
// and there is no PNG to go stale against the tables.
//
// ORDER IS DELIBERATE. One chart per result, in the order the pitch makes the
// argument, so "a minute more" is answered by flipping forward from here
// rather than hunting.
const K = require("./kit.js");
const F = require("../figures.js");
const { pres, S, card, note, srcLine,
        INK, MUT, PASS, FAIL, WARN, TEAL, TINT } = K;

// Every chart on these slides sits in the same frame, and the quiet-frame
// options are the same every time. pptxgenjs MUTATES an options object it is
// given, so this has to be a factory and not a shared constant.
const FRAME = (o = {}) => Object.assign({
  x: 0.55, y: 1.34, w: 8.35, h: 4.86,
  showLegend: false, catGridLine: { style: "none" },
  valGridLine: { color: "E3ECEE", size: 0.75 },
  catAxisLabelColor: INK, catAxisLabelFontSize: 10.5, catAxisLabelFontFace: "+mn-lt",
  valAxisLabelColor: MUT, valAxisLabelFontSize: 9.5, valAxisLabelFontFace: "+mn-lt",
  dataLabelFontSize: 9.5, dataLabelColor: INK, dataLabelFontFace: "+mn-lt",
  showTitle: true, titleFontSize: 11.5, titleColor: MUT, titleFontFace: "+mn-lt",
  legendFontSize: 10, legendColor: INK, legendFontFace: "+mn-lt",
  barGapWidthPct: 45,
}, o);

// The one-line caption under every chart: what the axis is, in words.
const axisNote = (s, t) => s.addText(t, {
  x: 0.55, y: 6.3, w: 8.35, h: 0.42, fontSize: 11, color: MUT, lineSpacing: 14,
  isTextBox: true, margin: 0, objectName: "axis",
});

// ------------------------------------------- C1. the positive control
{
  const PC = F.positiveControl().slice().sort((a, b) => a.margin - b.margin);
  const passes = PC.filter(r => r.gate === "SENSITIVE");
  const s = S("CONTENT", "Backup",
    `Chart: ${PC.length - passes.length} of ${PC.length} move less than their own noise floor`);

  s.addChart(pres.ChartType.bar, [
    { name: "Movement when only the sex parameter flips",
      labels: PC.map(r => r.model), values: PC.map(r => r.margin) },
    { name: "That model's own measured noise floor",
      labels: PC.map(r => r.model), values: PC.map(r => r.floor) },
  ], FRAME({
    barDir: "bar", chartColors: [TEAL, "C9D8DC"],
    showLegend: true, legendPos: "b",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0000",
    valAxisLabelFormatCode: "0.00", catAxisLabelPos: "low",
    title: "Group 2, where the guideline's own answer changes with the sex parameter",
  }));
  axisNote(s, "Both bars are probability mass on the guideline's correct answer. "
    + "A model is readable only where the teal bar clears the grey one.");

  card(s, { x: 9.15, y: 1.34, w: 3.6, h: 2.5, fill: "FBEEEC", name: "r1",
    kicker: "THE POSITIVE CONTROL", kickerColor: FAIL,
    head: `${PC.length - passes.length} of ${PC.length} fail it`, headSize: 17, headH: 0.42,
    body: "These vignettes are the ones where a clinician would answer "
        + "differently for a male and a female patient. A model that does not "
        + "move here is not even-handed, it is blind, and its small gender gaps "
        + "elsewhere cannot be read as fairness." });
  card(s, { x: 9.15, y: 4.0, w: 3.6, h: 2.2, fill: TINT, name: "r1b",
    kicker: "THE THREE THAT PASS", kickerColor: TEAL,
    head: passes.map(r => r.model).join(", "), headSize: 13.5, headH: 0.62,
    body: `Only these three clear their own floor, on ${PC[0].nVignettes} `
        + "vignettes each. Everything the pitch reports about gender gaps is "
        + "reported about them." });
  note(s, "[0s] Backup chart 1 of 4. The one to show if someone asks what "
    + "'fails the positive control' means in numbers. Teal is how far the "
    + "answer moved, grey is how far it moves when nothing clinical changes.");
}

// ------------------------------------------- C2. identity read as sex
{
  const MG = F.merging().slice().sort((a, b) => a.timesFloor - b.timesFloor);
  const above = MG.filter(m => m.above);
  const PT = F.postTraining();
  // Keep this title under about 60 characters. At 30pt in a 12.2in box it
  // wraps to two lines above that, and the second line lands on the chart.
  const s = S("CONTENT", "Backup",
    "Chart: capability and identity-confusion arrive together");

  s.addChart(pres.ChartType.bar, [{
    name: "Identity/SPCU merging",
    labels: MG.map(m => m.model), values: MG.map(m => m.timesFloor),
  }], FRAME({
    barDir: "bar", chartColors: MG.map(m => m.above ? FAIL : "9BB3BA"),
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
    valAxisLabelFormatCode: "0", catAxisLabelPos: "low",
    title: "Multiples of each model's own noise floor",
  }));
  axisNote(s, "1.0 would be an effect exactly the size of the model's own noise. "
    + "The three capable models sit between "
    + `${Math.min(...above.map(m => m.timesFloor)).toFixed(1)} and `
    + `${Math.max(...above.map(m => m.timesFloor)).toFixed(1)} times it.`);

  card(s, { x: 9.15, y: 1.34, w: 3.6, h: 2.5, fill: "FBEEEC", name: "r2",
    kicker: "IDENTITY/SPCU MERGING", kickerColor: FAIL,
    head: `${above.length} of ${MG.length} above their own floor`,
    headSize: 15, headH: 0.62,
    body: "The patient's stated gender identity moves an answer that should "
        + "turn only on the sex parameter a guideline reasons over. Same "
        + `direction on all ${MG[0].nVignettes} control vignettes in each case, `
        + "which noise does not do." });
  card(s, { x: 9.15, y: 4.0, w: 3.6, h: 2.2, fill: "FDF4E3", name: "r2b",
    kicker: "AND TUNING MAKES IT WORSE", kickerColor: WARN,
    head: `${PT.mergingBase.toFixed(4)} to ${PT.mergingTuned.toFixed(4)}`,
    headSize: 16, headH: 0.42,
    body: `${PT.base} against ${PT.tuned}: same size, same corpus, same `
        + `pretraining, ${PT.ratio.toFixed(1)} times the merging, against a `
        + `combined floor of ${PT.floorCombined.toFixed(4)}.` });
  note(s, "[0s] Backup chart 2 of 4. The strongest positive finding, and the "
    + "one to show if someone says the study only found nulls. The grey bars "
    + "are the models that cannot do the task at all.");
}

// ------------------------------------------- C3. the placebo floor
{
  const PL = F.placeboRegate();
  const V = PL.survivors.slice().sort((a, b) => a.margin - b.margin);
  const s = S("CONTENT", "Backup",
    "Chart: every surviving effect falls under the placebo floor");

  s.addChart(pres.ChartType.bar, [
    { name: "The gender gap measured",
      labels: V.map(r => r.model), values: V.map(r => r.margin) },
    { name: "Floor 1: right manipulation, wrong vignette",
      labels: V.map(r => r.model), values: V.map(r => r.genderFloor) },
    { name: "Floor 2: right vignette, clinically inert edit",
      labels: V.map(r => r.model), values: V.map(r => r.placeboFloor) },
  ], FRAME({
    h: 4.3, barDir: "bar", chartColors: [TEAL, "C9D8DC", FAIL],
    showLegend: true, legendPos: "b",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0000",
    valAxisLabelFormatCode: "0.00", catAxisLabelPos: "low", barGapWidthPct: 60,
    title: "The three models that cleared the first floor, against both floors",
  }));
  axisNote(s, "The teal bar beats the grey one in all three rows and the red "
    + "one in none. Changing the patient's appointment time or their "
    + "occupation moves these models more than changing their gender does.");

  card(s, { x: 9.15, y: 1.34, w: 3.6, h: 2.5, fill: "FBEEEC", name: "r3",
    kicker: "THE PLACEBO FLOOR", kickerColor: FAIL,
    head: `${PL.passGenderFloor} of ${PL.n} becomes ${PL.passBothFloors} of ${PL.n}`,
    headSize: 16, headH: 0.42,
    body: "A gender effect has to beat a clinically meaningless edit to the "
        + "SAME vignette, not a gender flip on a different one. Once it has "
        + "to, nothing in this study survives as a gender effect." });
  card(s, { x: 9.15, y: 4.0, w: 3.6, h: 2.2, fill: TINT, name: "r3b",
    kicker: "DECIDED BEFORE THE NUMBERS", kickerColor: TEAL,
    head: "The aggregation was fixed in advance", headSize: 13.5, headH: 0.62,
    body: "Maximum over the two patient-descriptive attributes, as reported: "
        + "0 of 10. Mean instead: 1 of 10. All three attributes: 0 of 10. The "
        + "choice was logged before the floors were computed." });
  note(s, "[0s] Backup chart 3 of 4. The methodological contribution, and the "
    + "slide to show if someone asks why we report nulls so confidently, or "
    + "whether the aggregation choice drove the result.");
}

// ------------------------------------------- C4. the size trend
{
  const PY = F.sizeTrend().filter(r => /^pythia/.test(r.model));
  const RQ3 = F.rq3Spearman();
  const P = RQ3.by_family.pythia;
  const s = S("CONTENT", "Backup",
    "Chart: inside one controlled family, the gap grows with size");

  // WHY BARS AND NOT A LINE. The first version drew both series as lines over
  // equal-spaced categories. Two things were wrong with it: a line says the
  // points lie on a trajectory, when the claim is a RANK correlation, and
  // equal spacing hides that 70M to 6.9B is a hundredfold. The paper's panel
  // uses a log axis to say that; a slide cannot, so it says it in words and
  // drops the trajectory. The floor stays as a line because it is a reference
  // against the bars, on the same axis -- never a second one.
  s.addChart([
    { type: pres.ChartType.bar,
      data: [{ name: "The gender gap, mean |delta|",
               labels: PY.map(r => r.model), values: PY.map(r => r.absDelta) }],
      options: { chartColors: [TEAL], barGapWidthPct: 55,
                 showValue: true, dataLabelPosition: "outEnd",
                 dataLabelFormatCode: "0.0000" } },
    { type: pres.ChartType.line,
      data: [{ name: "That model's own noise floor",
               labels: PY.map(r => r.model), values: PY.map(r => r.floor) }],
      options: { chartColors: ["B9CBD0"], lineSize: 2.25, lineSmooth: false,
                 lineDataSymbol: "circle", lineDataSymbolSize: 7 } },
  ], FRAME({
    showLegend: true, legendPos: "b", valAxisLabelFormatCode: "0.000",
    title: `${P.n_models} Pythia models: one corpus, one recipe, seven sizes`,
  }));
  axisNote(s, "Sizes are not evenly spaced: 70M to 6.9B is a hundredfold, and "
    + "the claim is a rank correlation, not a straight line. This is the only "
    + "size series here that is not confounded with family and corpus.");

  card(s, { x: 9.15, y: 1.34, w: 3.6, h: 2.5, fill: TINT, name: "r4",
    kicker: "RQ3, WITHIN PYTHIA", kickerColor: TEAL,
    head: `Gap against size: rho = ${P.spearman_rho_raw_gap.toFixed(3)}`,
    headSize: 15, headH: 0.62,
    body: `p = ${P.spearman_p_raw_gap.toFixed(4)} over ${P.n_models} sizes. The `
        + `floor itself does not follow size (rho = ${P.spearman_rho_floor.toFixed(3)}), `
        + "so the trend is in the gap and not in the instrument that measures it." });
  card(s, { x: 9.15, y: 4.0, w: 3.6, h: 2.2, fill: "FDF4E3", name: "r4b",
    kicker: "WHAT IT DOES NOT SHOW", kickerColor: WARN,
    head: "Floor-relative, it does not reach significance", headSize: 13, headH: 0.62,
    body: `Subtracting each model's floor first gives rho = `
        + `${P.spearman_rho_composite.toFixed(3)}, p = ${P.spearman_p_composite.toFixed(3)}. `
        + "With seven models that is the resolution limit, not a null." });
  note(s, "[0s] Backup chart 4 of 4. Show it if someone asks whether scale "
    + "fixes this. State the caveat on the right out loud: the raw gap tracks "
    + "size, the floor-relative one does not reach significance at seven models.");
  srcLine(s, ["biderman2023"]);
}
