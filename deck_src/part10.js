const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const AX = { catAxisLabelColor: MUT, valAxisLabelColor: MUT,
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  valGridLine: { color: "E4EDEE", size: 0.75 }, catGridLine: { style: "none" } };

// ============ 25. RQ3 SCALE ===================================== //
let s = S("CONTENT", "Results", "RQ3: does the gap change with model scale?");
s.addChart(pres.ChartType.bar, [
  { name: "Floor-relative gap, old floor",
    labels: ["70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "OLMo base", "OLMo Inst", "Qwen 8B"],
    values: [-0.0127, -0.0554, -0.0244, -0.0799, -0.0978, -0.0802, -0.0972, -0.0263, -0.0631, 0.0046] },
  { name: "Floor-relative gap, matched floor",
    labels: ["70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "OLMo base", "OLMo Inst", "Qwen 8B"],
    values: [0.0031, -0.0050, 0.0028, -0.0002, -0.0050, 0.0020, 0.0050, 0.0090, 0.0163, 0.0197] },
], { x: 0.55, y: 1.25, w: 7.6, h: 4.0, barDir: "col", barGrouping: "clustered",
  chartColors: ["C8B4AE", TEAL], showTitle: true,
  title: "Gap minus floor, by model, before and after the floor correction",
  titleColor: INK, titleFontSize: 12, titleFontFace: "+mn-lt",
  showLegend: true, legendPos: "b", legendColor: MUT, legendFontSize: 10, legendFontFace: "+mn-lt",
  showValue: false, barGapWidthPct: 40, ...AX });

card(s, { x: 8.4, y: 1.25, w: 4.35, h: 1.3, fill: TINT, name: "r3a" });
s.addText([{ text: "Old floor:  ", options: { color: MUT, fontSize: 12 } },
  { text: "rho -0.030,  p = 0.93\n", options: { bold: true, color: FAIL, fontSize: 13, fontFace: "Courier New" } },
  { text: "Matched floor:  ", options: { color: MUT, fontSize: 12 } },
  { text: "rho +0.693,  p = 0.026", options: { bold: true, color: PASS, fontSize: 13, fontFace: "Courier New" } }],
  { x: 8.62, y: 1.44, w: 3.9, h: 0.95, lineSpacing: 19, margin: 0, isTextBox: true, valign: "middle" });

card(s, { x: 8.4, y: 2.67, w: 4.35, h: 2.58, fill: "FBEEEC", kicker: "THE RESULT TO BE MOST SUSPICIOUS OF",
  kickerColor: FAIL, name: "r3b" });
s.addText("A null becomes a trend because of an instrument change we made ourselves. That is the shape a reader should distrust, so we volunteer it and offer four things instead of reassurance.",
  { x: 8.62, y: 3.21, w: 3.9, h: 0.84, fontSize: 11.5, bold: true, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
s.addText([
  { text: "1  ", options: { bold: true, color: FAIL } }, { text: "Criterion fixed before the run, on Groups 2 and 4 only.\n", options: { color: MUT } },
  { text: "2  ", options: { bold: true, color: FAIL } }, { text: "The old floor spanned 0.021 to 0.105 with no relation to size, while the gap spans only 0.006 to 0.033.\n", options: { color: MUT } },
  { text: "3  ", options: { bold: true, color: FAIL } }, { text: "Both columns published, reproducible with a flag.\n", options: { color: MUT } },
  { text: "4  ", options: { bold: true, color: FAIL } }, { text: "RQ3 stays exploratory, outside the Holm family.", options: { color: MUT } },
], { x: 8.62, y: 4.08, w: 3.9, h: 1.1, fontSize: 10.5, lineSpacing: 13, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.42, w: 12.2, h: 1.0, fill: INK, name: "r3c" });
s.addText([
  { text: "Had we reported the composite alone in October, our headline would have been that gender bias decreases with model scale, at p = 0.014. ", options: { color: "BCD3D8" } },
  { text: "It would have been a statement about our own measurement noise. It is a trend worth reporting. It is not a scaling law.", options: { bold: true, color: PAPER } },
], { x: 0.77, y: 5.6, w: 11.76, h: 0.68, fontSize: 12.5, lineSpacing: 16, margin: 0, isTextBox: true });
note(s, "Present this slide defensively. The number moved in our favour after a change we made, so the burden is on us. The decomposition is the defence: under the matched floor the floor no longer tracks size, correlating at only +0.280 with p = 0.43, so the gap trend is no longer cancelled.");

// ============ 26. RQ4 LINKAGE =================================== //
s = S("CONTENT", "Results", "RQ4: the negative control fires");
s.addText("H4 says data skew should predict output gaps for the model trained on that data. Every model is tested twice: against its own corpus, which we call matched, and against a corpus it has never seen, which we call crossed.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.4, fontSize: 13.5, color: INK, lineSpacing: 17, margin: 0, isTextBox: true });

s.addChart(pres.ChartType.bar, [
  { name: "Spearman correlation with corpus skew",
    labels: ["Qwen3-8B vs olmo-mix\n(never seen)", "Qwen3-8B vs the Pile\n(never seen)", "OLMo-2-7B Instruct\n(its own corpus)", "OLMo-2-7B base\n(its own corpus)", "pythia-6.9b\n(its own corpus)"],
    values: [0.758, 0.700, 0.385, 0.060, -0.117] },
], { x: 0.55, y: 1.7, w: 7.0, h: 3.5, barDir: "bar", chartColors: [BERRY],
  showTitle: true, title: "The models trained on neither corpus correlate best with both",
  titleColor: INK, titleFontSize: 11.5, titleFontFace: "+mn-lt",
  showLegend: false, showValue: true, dataLabelPosition: "outEnd",
  dataLabelColor: INK, dataLabelFontSize: 10.5, dataLabelFontFace: "+mn-lt",
  barGapWidthPct: 45, ...AX });

card(s, { x: 7.8, y: 1.7, w: 4.95, h: 1.62, fill: INK, kicker: "WHY IT FIRES", kickerColor: WARN, name: "r4a" });
s.addText("On the audited concepts the two corpora agree at Spearman 0.976 on common support. They are both large English web scrapes, so their gendered health-term skew is very nearly the same measurement twice.",
  { x: 8.02, y: 2.24, w: 4.51, h: 1.0, fontSize: 11.5, color: PAPER, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 7.8, y: 3.44, w: 4.95, h: 1.76, fill: "FBEEEC", kicker: "THE REPAIR THAT FAILED", kickerColor: FAIL, name: "r4b" });
s.addText("Restricting to concepts where the corpora disagree was the plan, with a criterion of six concepts above 0.5 log2 fixed before running. Zero qualify: the largest disagreement is 0.377 and the median is 0.125. Recorded as a failed intervention.",
  { x: 8.02, y: 3.98, w: 4.51, h: 1.12, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.24, w: 12.2, h: 1.2, fill: "E6F5F2", kicker: "RQ4 IS REFRAMED, NOT DROPPED",
  kickerColor: PASS, name: "r4c" });
s.addText("Two measurements that agree at 0.976 cannot attribute behaviour to one rather than the other, so matched and crossed are close to the same test. We report a measured bound instead: 0.976 is the coefficient that makes provenance attribution by n-gram skew correlation impossible between these corpora. For a project premised on open data making bias traceable, that bound is a result about the premise, not a failure to reach one.",
  { x: 0.77, y: 5.62, w: 11.76, h: 0.78, fontSize: 11.5, color: INK, lineSpacing: 14, margin: 0, isTextBox: true });
note(s, "Qwen correlating with both corpora is not an anomaly, it is the arithmetic consequence of the corpora agreeing with each other. A second defect this exposed: only 8 of 14 concepts have skew in both corpora, so matched and crossed were partly computed over non-overlapping concept sets.");

module.exports = {};
