// SPOKEN 12 of 16: does the gap grow with scale? Chart alone. [26s]
//
// RQ3 KEYS (D103). `spearman_rho` is the COMPOSITE, (mean |delta| - floor)
// against size. `spearman_rho_raw_gap` and `spearman_rho_floor` are its two
// components. The raw one used to be called `spearman_rho_gap`, which read as
// if it held the composite; it was renamed so it cannot be misread.
// `by_family.pythia` is the controlled size series: one corpus, one recipe,
// seven sizes. Across all ten, size is confounded with family AND corpus.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const ST = F.sizeTrend().slice().sort((a, b) => a.params - b.params);
const R3 = F.rq3Spearman();
const RHO_RAW = R3.spearman_rho_raw_gap;
const RHO_GAP = R3.spearman_rho;
const RHO_FLOOR = R3.spearman_rho_floor;
const PY3 = (R3.by_family || {}).pythia;
if (!PY3) {
  throw new Error("s12.js: rq3_size_trend_stats.json has no by_family.pythia. "
    + "Rerun:  .venv/bin/python -m src.stats");
}
const fam = m => (/pythia/.test(m) ? TEAL : /OLMo/.test(m) ? BERRY : WARN);

const s = S("CONTENT", "3 Results", "The gap grows with scale");
K.mark("scaletrend");

s.addText("Gender gap with each model's own noise floor subtracted, models ordered by parameter count.", {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

s.addChart(pres.ChartType.bar, [{
  name: "Gap above floor",
  labels: ST.map(r => `${r.model} (${r.params}B)`),
  values: ST.map(r => Number(r.gap.toFixed(5))),
}], {
  x: 1.5, y: 1.6, w: 10.4, h: 3.5,
  barDir: "bar", barGapWidthPct: 38,
  chartColors: ST.map(r => fam(r.model)),
  showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10,
  dataLabelColor: MUT, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: "+0.000;−0.000",
  catAxisLabelColor: INK, catAxisLabelFontSize: 10.5, catAxisLabelFontFace: "+mn-lt",
  catAxisLabelPos: "low", catGridLine: { style: "none" },
  valAxisLabelColor: MUT, valAxisLabelFontSize: 9, valAxisLabelFontFace: "+mn-lt",
  valAxisLabelFormatCode: "0.00", valGridLine: { color: "E6EEF0", size: 0.75 },
  valAxisLineShow: false, catAxisLineShow: false,
  // Padding so the most negative bar's label cannot overprint the model name.
  valAxisMinVal: -0.015, valAxisMaxVal: 0.025,
  objectName: "scale-chart",
});

// The floor's own trend is shown beside the gap's on purpose: it is the only
// thing that rules out "the instrument simply got noisier with scale".
const STAT = [
  ["raw gap vs size", F.f3(RHO_RAW), INK, "all 10 models"],
  ["floor-subtracted", F.f3(RHO_GAP), INK, "all 10 models"],
  ["the floor itself", `${F.f3(RHO_FLOOR)}, ${F.p(R3.spearman_p_floor)}`, FAIL, "no trend"],
  ["within Pythia only", `${F.f3(PY3.spearman_rho_raw_gap)}, ${F.p(PY3.spearman_p_raw_gap)}`, TEAL, "one corpus, 7 sizes"],
];
STAT.forEach(([lab, val, col, sub], i) => {
  const x = 0.55 + i * 3.09;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 5.22, w: 2.98, h: 0.92, rectRadius: 0.05,
    fill: { color: i === 3 ? "E6F6F2" : TINT }, line: { color: i === 3 ? TEAL : TINT, width: i === 3 ? 1.1 : 0 },
    objectName: `st${i}-bg` });
  s.addText(lab, { x: x + 0.16, y: 5.3, w: 2.66, h: 0.22, fontSize: 9,
    bold: true, color: MUT, charSpacing: 0.4, isTextBox: true, margin: 0,
    objectName: `st${i}-l` });
  s.addText("ρ " + val, { x: x + 0.16, y: 5.5, w: 2.66, h: 0.3, fontSize: 14,
    bold: true, color: col, isTextBox: true, margin: 0, objectName: `st${i}-v` });
  s.addText(sub, { x: x + 0.16, y: 5.82, w: 2.66, h: 0.22, fontSize: 8.5,
    color: "9BB3BA", italic: true, isTextBox: true, margin: 0, objectName: `st${i}-s` });
});

s.addText("If bigger models were simply noisier, the third number would be the big one. It is not.", {
  x: 0.55, y: 6.28, w: 12.2, h: 0.28, fontSize: 12, bold: true, color: INK,
  align: "center", isTextBox: true, margin: 0, objectName: "punch" });

// 26 seconds, about 56 words.
note(s, `[26s] The gap grows with scale, and the four boxes pre-empt the obvious objection.

Raw, ${F.f3(RHO_RAW)}. After subtracting each model's own floor, ${F.f3(RHO_GAP)}. The floor itself, ${F.f3(RHO_FLOOR)}, not significant.

If bigger models were simply noisier, that third number would be the big one. Within Pythia alone, ${F.f3(PY3.spearman_rho_raw_gap)}.`);
