// SPOKEN 11 of 16: identity-SPCU merging, chart alone. [26s]
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, tierBanner, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const MG = F.merging().slice().sort((a, b) => a.timesFloor - b.timesFloor);
const PT = F.postTraining();
const fam = m => (/pythia/.test(m) ? TEAL : /OLMo/.test(m) ? BERRY : WARN);
const top = MG[MG.length - 1];

const s = S("CONTENT", "3 Results", "Capable models read identity as the sex parameter");
K.mark("merge");

s.addText("How far a model moves when the identity label contradicts the stated sex parameter, in multiples of that model's own noise floor.", {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

s.addChart(pres.ChartType.bar, [{
  name: "Multiple of the model's own noise floor",
  labels: MG.map(r => r.model),
  values: MG.map(r => Number(r.timesFloor.toFixed(2))),
}], {
  x: 1.3, y: 1.6, w: 10.7, h: 3.5,
  barDir: "bar", barGapWidthPct: 38,
  chartColors: MG.map(r => (r.above ? fam(r.model) : "C8D7DB")),
  showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10,
  dataLabelColor: MUT, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: "0.0×;−0.0×",
  catAxisLabelColor: INK, catAxisLabelFontSize: 10.5, catAxisLabelFontFace: "+mn-lt",
  catAxisLabelPos: "low", catGridLine: { style: "none" },
  valAxisLabelColor: MUT, valAxisLabelFontSize: 9, valAxisLabelFontFace: "+mn-lt",
  valAxisLabelFormatCode: "0", valGridLine: { color: "E6EEF0", size: 0.75 },
  valAxisLineShow: false, catAxisLineShow: false,
  objectName: "merge-chart",
});
s.addText("Coloured bars clear their own floor. Grey bars do not.", {
  x: 0.55, y: 5.16, w: 12.2, h: 0.26, fontSize: 10.5, color: MUT, italic: true,
  align: "center", isTextBox: true, margin: 0, objectName: "lg" });

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.5, w: 12.23, h: 0.86, rectRadius: 0.06,
  fill: { color: INK }, line: { color: INK, width: 0 }, objectName: "pb" });
s.addText([
  { text: `The largest effect is ${top.model} at ${top.timesFloor.toFixed(1)}× — the fully open-data model.  `,
    options: { bold: true, color: PAPER } },
  { text: `Instruction tuning on the same corpus multiplied it ${PT.ratio.toFixed(1)}-fold, from ${F.f3(PT.mergingBase)} to ${F.f3(PT.mergingTuned)} — a rise of ${PT.timesFloor.toFixed(1)} combined floors, so this points at post-training and not only at data.`,
    options: { color: "AFCBD1" } },
], { x: 0.8, y: 5.58, w: 11.73, h: 0.7, fontSize: 12, lineSpacing: 15,
     valign: "middle", isTextBox: true, margin: 0, objectName: "pt" });

tierBanner(s, { x: 0.55, y: 6.48, w: 12.23, h: 0.4, fs: 8, name: "tier" });

// 26 seconds, about 52 words.
note(s, `[26s] Identity-SPCU merging: how far a model moves when the identity label contradicts the sex parameter, in multiples of its own floor.

Three coloured bars cleared their floor; seven grey ones did not. The biggest is ${top.model} at ${top.timesFloor.toFixed(1)} times, and say the uncomfortable part out loud: that is the fully open-data model.`);
