const K = require("./part1.js");
const F = require("./figures.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// D095. Both slides in this file were entirely hand-typed, including the one
// number the deck tells the audience to distrust: the RQ3 Spearman rho. It
// read rho +0.693, p = 0.026 while the run was printing +0.857, p = 0.0015,
// because the rho lived only in stdout. src/stats.py now persists it.
const ST = F.sizeTrend();                      // ascending by params
const SP = F.rq3Spearman();
const FC = F.floorComparison();
const r3 = v => (v >= 0 ? "+" : "\u2212") + Math.abs(v).toFixed(3);
const pf = v => (v < 0.001 ? "p < 0.001" : "p = " + v.toFixed(3));
const LBL = m => m.replace("pythia-", "").replace("OLMo-2-7B-Instruct", "OLMo Inst")
                  .replace(/^OLMo-2-7B$/, "OLMo base").replace("Qwen3-8B", "Qwen 8B");

// D096. catAxisLabelPos "low" pins the category labels to the edge of the plot
// area. The default puts them at the value axis crossing, so on any chart with
// negative values they are drawn over the bars that run the other way, which is
// what buried six of the ten model names on the RQ4 chart.
// valAxisLabelFormatCode exists because the zero tick was rendering as
// 6.93889390390723E-18: the axis steps accumulate float error, and with no
// format the renderer prints the result verbatim.
const AX = { catAxisLabelColor: MUT, valAxisLabelColor: MUT,
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  catAxisLabelPos: "low", valAxisLabelFormatCode: "0.00",
  valGridLine: { color: "E4EDEE", size: 0.75 }, catGridLine: { style: "none" } };

// ============ 25. RQ3 SCALE ===================================== //
let s = S("CONTENT", "Results", "RQ3: does the gap change with model scale?");
// The old-floor column is the same gap measured against the floor as first
// built: mean_abs_delta minus that model's OLD floor. Recomputed here from the
// recorded old floors rather than remembered, so the two columns cannot drift
// apart.
const r3Labels = ST.map(m => LBL(m.model));
s.addChart(pres.ChartType.bar, [
  { name: "Floor-relative gap, old floor", labels: r3Labels,
    values: ST.map(m => m.absDelta - (FC.byModel[m.model] || {}).oldFloor) },
  { name: "Floor-relative gap, matched floor", labels: r3Labels,
    values: ST.map(m => m.gap) },
], { x: 0.55, y: 1.25, w: 7.6, h: 4.0, barDir: "col", barGrouping: "clustered",
  chartColors: ["C8B4AE", TEAL], showTitle: true,
  title: "Gap minus floor, by model, before and after the floor correction",
  titleColor: INK, titleFontSize: 12, titleFontFace: "+mn-lt",
  showLegend: true, legendPos: "b", legendColor: MUT, legendFontSize: 10, legendFontFace: "+mn-lt",
  showValue: false, barGapWidthPct: 40, ...AX });

card(s, { x: 8.4, y: 1.25, w: 4.35, h: 1.34, fill: TINT, name: "r3a" });
// The composite rho is what the headline would have been; the decomposition
// into gap-vs-size and floor-vs-size is the defence, and it is the thing an
// examiner will ask for. Show both, from the persisted sidecar.
s.addText([
  { text: "Composite:  ", options: { color: MUT, fontSize: 12 } },
  { text: `rho ${r3(SP.spearman_rho)},  ${pf(SP.spearman_p)}\n`,
    options: { bold: true, color: PASS, fontSize: 13, fontFace: "Courier New" } },
  { text: "Gap vs size:  ", options: { color: MUT, fontSize: 11 } },
  { text: `rho ${r3(SP.spearman_rho_gap)},  ${pf(SP.spearman_p_gap)}\n`,
    options: { bold: true, color: INK, fontSize: 11.5, fontFace: "Courier New" } },
  { text: "Floor vs size:  ", options: { color: MUT, fontSize: 11 } },
  { text: `rho ${r3(SP.spearman_rho_floor)},  ${pf(SP.spearman_p_floor)}`,
    options: { bold: true, color: SP.carried_by_floor ? FAIL : MUT,
               fontSize: 11.5, fontFace: "Courier New" } }],
  { x: 8.62, y: 1.38, w: 3.9, h: 1.08, lineSpacing: 15, margin: 0, isTextBox: true,
    valign: "middle" });

card(s, { x: 8.4, y: 2.67, w: 4.35, h: 2.58, fill: "FBEEEC", kicker: "THE RESULT TO BE MOST SUSPICIOUS OF",
  kickerColor: FAIL, name: "r3b" });
s.addText("A null becomes a trend because of an instrument change we made ourselves. That is the shape a reader should distrust, so we volunteer it and offer four things instead of reassurance.",
  { x: 8.62, y: 3.21, w: 3.9, h: 0.84, fontSize: 11.5, bold: true, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
s.addText([
  { text: "1  ", options: { bold: true, color: FAIL } }, { text: "Criterion fixed before the run, on Groups 2 and 4 only.\n", options: { color: MUT } },
  { text: "2  ", options: { bold: true, color: FAIL } }, { text: `The old floor spanned ${FC.oldFloorLo.toFixed(3)} to `
      + `${FC.oldFloorHi.toFixed(3)} with no relation to size, while the gap `
      + `spans only ${Math.min(...ST.map(m => m.absDelta)).toFixed(3)} to `
      + `${Math.max(...ST.map(m => m.absDelta)).toFixed(3)}.\n`,
  options: { color: MUT } },
  { text: "3  ", options: { bold: true, color: FAIL } }, { text: "Both columns published, reproducible with a flag.\n", options: { color: MUT } },
  { text: "4  ", options: { bold: true, color: FAIL } }, { text: "RQ3 stays exploratory, outside the Holm family.", options: { color: MUT } },
], { x: 8.62, y: 4.08, w: 3.9, h: 1.1, fontSize: 10.5, lineSpacing: 13, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.42, w: 12.2, h: 1.0, fill: INK, name: "r3c" });
s.addText([
  { text: "Had we reported the composite alone in October, our headline would "
        + `have been that gender bias changes with model scale, at `
        + `${pf(SP.spearman_p)}. `, options: { color: "BCD3D8" } },
  { text: "It would have been a statement about our own measurement noise. It is a trend worth reporting. It is not a scaling law.", options: { bold: true, color: PAPER } },
], { x: 0.77, y: 5.6, w: 11.76, h: 0.68, fontSize: 12.5, lineSpacing: 16, margin: 0, isTextBox: true });
note(s, "Present this slide defensively. The number moved in our favour after "
  + "a change we made, so the burden is on us. The decomposition is the "
  + `defence: under the matched floor the floor correlates with size at `
  + `rho ${r3(SP.spearman_rho_floor)} (${pf(SP.spearman_p_floor)}) while the `
  + `gap correlates at rho ${r3(SP.spearman_rho_gap)} `
  + `(${pf(SP.spearman_p_gap)}). `
  + (SP.carried_by_floor
      ? "WARNING: the floor correlates MORE strongly than the gap, so the "
        + "composite trend is carried by the instrument. Do not present it as "
        + "bias changing with scale."
      : "The gap, not the floor, carries the trend, so the composite is not "
        + "an artefact of the instrument changing with size."));

// ============ 26. RQ4 LINKAGE =================================== //
s = S("CONTENT", "Results", "RQ4: the negative control fires");
s.addText("H4 says data skew should predict output gaps for the model trained on that data. Every model is tested twice: against its own corpus, which we call matched, and against a corpus it has never seen, which we call crossed.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.4, fontSize: 13.5, color: INK, lineSpacing: 17, margin: 0, isTextBox: true });

// D095. This chart was five hand-typed bars on an assumption that no longer
// holds: that each model has one matched corpus and one crossed one. The table
// carries THREE skew indices (olmo-mix, piletrain, dclm-baseline), so every
// model has one matched and two crossed -- and Qwen declares no corpus, so all
// of its rows are "unknown". The hand-typed values appear nowhere in the
// current table at all.
//
// The title was also an assertion: "the models trained on neither corpus
// correlate best with both". Whether that is still true is a fact about the
// table, so it is computed and the title states whichever is the case.
const R4 = F.rq4Linkage();
const r4rows = R4.models
  .map(m => ({
    model: m.model,
    own: m.matched ? m.matched.rho : NaN,
    other: m.bestCrossed ? m.bestCrossed.rho : NaN,
    declares: m.declaresCorpus,
  }))
  .sort((a, b) => (isNaN(b.own) ? b.other : b.own) - (isNaN(a.own) ? a.other : a.own));
const r4Title = R4.strongestIsUndeclared
  ? "The model trained on neither corpus correlates best with both"
  : (R4.strongestIsMatched
      ? `The strongest correlation is a model against its OWN corpus `
        + `(${R4.strongest.model}, ${R4.strongest.corpus})`
      : `The strongest correlation is a model against a corpus it never saw `
        + `(${R4.strongest.model}, ${R4.strongest.corpus})`);
// A model that discloses no training corpus has no matched test at all, which
// is not the same as a matched correlation of zero. Plotting NaN as 0 drew Qwen
// a zero-length bar in the "own corpus" series, which reads as "no relationship
// with its own data" when the truth is that there is no such measurement. null
// leaves the category empty, and the series name says who is missing and why.
const _undeclared = r4rows.filter(r => !r.declares).map(r => r.model);
const r4OwnName = "Against its own corpus"
  + (_undeclared.length
      ? ` (not disclosed: ${_undeclared.join(", ")})`
      : "");
s.addChart(pres.ChartType.bar, [
  { name: r4OwnName, labels: r4rows.map(r => LBL(r.model)),
    values: r4rows.map(r => (isNaN(r.own) ? null : r.own)) },
  { name: "Best against a corpus it never saw", labels: r4rows.map(r => LBL(r.model)),
    values: r4rows.map(r => (isNaN(r.other) ? null : r.other)) },
], { x: 0.55, y: 1.7, w: 7.0, h: 3.5, barDir: "bar", barGrouping: "clustered",
  chartColors: [BERRY, "C8B4AE"],
  showTitle: true, title: r4Title,
  titleColor: INK, titleFontSize: 11, titleFontFace: "+mn-lt",
  showLegend: true, legendPos: "b", legendColor: MUT, legendFontSize: 9.5,
  legendFontFace: "+mn-lt",
  showValue: false, barGapWidthPct: 35, ...AX });

card(s, { x: 7.8, y: 1.7, w: 4.95, h: 1.62, fill: INK, kicker: "WHY IT FIRES", kickerColor: WARN, name: "r4a" });
const CD = F.corpusDisagreement();
s.addText(`On the audited concepts the two corpora agree closely on their `
  + `${CD.nCommonSupport} concepts of common support: the largest `
  + `disagreement is ${CD.maxDisagreement.toFixed(3)} log2 and the median is `
  + `${CD.medianDisagreement.toFixed(3)}. They are both large English web `
  + "scrapes, so their gendered health-term skew is very nearly the same "
  + "measurement twice.",
  { x: 8.02, y: 2.24, w: 4.51, h: 1.0, fontSize: 11.5, color: PAPER, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 7.8, y: 3.44, w: 4.95, h: 1.76, fill: "FBEEEC", kicker: "THE REPAIR THAT FAILED", kickerColor: FAIL, name: "r4b" });
s.addText("Restricting to concepts where the corpora disagree was the plan, "
  + "with a criterion of six concepts above 0.5 log2 fixed before running. "
  + `${CD.nAboveHalfLog2 === 0 ? "Zero qualify" : CD.nAboveHalfLog2 + " qualify"}, `
  + `out of ${CD.n} audited. Recorded as a failed intervention.`,
  { x: 8.02, y: 3.98, w: 4.51, h: 1.12, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.24, w: 12.2, h: 1.2, fill: "E6F5F2", kicker: "RQ4 IS REFRAMED, NOT DROPPED",
  kickerColor: PASS, name: "r4c" });
s.addText("Two corpora this close cannot attribute behaviour to one rather than "
  + "the other, so matched and crossed are close to the same test. We report a "
  + `measured bound instead: across ${CD.n} audited concepts the largest `
  + `disagreement between the corpora is ${CD.maxDisagreement.toFixed(3)} log2, `
  + "which is what makes provenance attribution by n-gram skew correlation "
  + "impossible between them. For a project premised on open data making bias "
  + "traceable, that bound is a result about the premise, not a failure to "
  + "reach one.",
  { x: 0.77, y: 5.62, w: 11.76, h: 0.78, fontSize: 11.5, color: INK, lineSpacing: 14, margin: 0, isTextBox: true });
note(s, "A model correlating with corpora it never saw is not an anomaly, it "
  + "is the arithmetic consequence of the corpora agreeing with each other. A "
  + `second defect this exposed: only ${CD.nCommonSupport} of ${CD.n} concepts `
  + "have skew in both corpora, so matched and crossed were partly computed "
  + "over non-overlapping concept sets. The strongest correlation on the "
  + `current tables is ${R4.strongest.model} against ${R4.strongest.corpus} `
  + `(rho ${R4.strongest.rho.toFixed(3)}, p = ${R4.strongest.p.toFixed(4)}), `
  + `which is a ${R4.strongest.pairing} pairing. Be ready to say which.`);

module.exports = {};
