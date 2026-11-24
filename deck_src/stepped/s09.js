// SPOKEN 9 of 16: the positive-control gate, chart alone. [36s]
// Everything is plotted as the margin ABOVE THE MODEL'S OWN FLOOR, the only
// comparison commensurable across ten models with ten different floors.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const PC = F.positiveControl().slice().sort((a, b) => a.overFloor - b.overFloor);
const nFail = PC.filter(r => r.gate === "INSENSITIVE").length;
const nPass = PC.length - nFail;

pres.addSection({ title: "3 Results" });
const s = S("CONTENT", "3 Results", `The positive control: ${nFail} of ${PC.length} fail`);
K.mark("gate");

s.addText([
  { text: "Group 2's correct answer changes with the sex parameter.  ", options: { color: MUT } },
  { text: "Answering the same either way is not fairness.",
    options: { bold: true, color: INK } },
], { x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, isTextBox: true,
     margin: 0, objectName: "sub" });

s.addChart(pres.ChartType.bar, [{
  name: "Margin above the model's own noise floor",
  labels: PC.map(r => r.model),
  values: PC.map(r => Number(r.overFloor.toFixed(5))),
}], {
  x: 1.3, y: 1.6, w: 10.7, h: 4.46,
  barDir: "bar", barGapWidthPct: 42,
  chartColors: [PASS], invertedColors: [FAIL],
  showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10,
  dataLabelColor: MUT, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: "+0.000;−0.000",
  catAxisLabelColor: INK, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
  // Values cross zero, so category labels must be pinned low or PowerPoint
  // draws them through the middle of the bars.
  catAxisLabelPos: "low",
  catGridLine: { style: "none" },
  valAxisLabelColor: MUT, valAxisLabelFontSize: 9.5, valAxisLabelFontFace: "+mn-lt",
  valAxisLabelFormatCode: "0.00",
  valGridLine: { color: "E6EEF0", size: 0.75 },
  valAxisLineShow: false, catAxisLineShow: false,
  objectName: "gate-chart",
});

s.addText([
  { text: "▸ right of zero = clears its own floor, passes the gate          ", options: { color: PASS, bold: true } },
  { text: "◂ left of zero = insensitive to the sex parameter", options: { color: FAIL, bold: true } },
], { x: 0.55, y: 6.12, w: 12.2, h: 0.28, fontSize: 11, align: "center",
     isTextBox: true, margin: 0, objectName: "legend" });

s.addText(`All ${nFail} that fail are Pythia. The ${nPass} that pass are Qwen3-8B and both OLMo-2 models.`, {
  x: 0.55, y: 6.44, w: 12.2, h: 0.28, fontSize: 11.5, bold: true, color: INK,
  align: "center", isTextBox: true, margin: 0, objectName: "who" });

// 36 seconds, about 78 words.
note(s, `[36s] This slide earns the rest of the talk.

Each bar is a model's sensitivity to the sex parameter, minus its own noise floor. Right of zero it passed. Left of zero it did not.

${nFail} of the ten are left of zero, and all ${nFail} are Pythia. The three that cleared are Qwen3-8B and both OLMo-2 models.

Note the scale. Qwen is not marginally better, it is an order of magnitude clear of its floor.`);
