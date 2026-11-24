// SHORT deck, slide 5: the positive-control gate. The proof slide.
//
// Everything is plotted as the margin ABOVE THE MODEL'S OWN FLOOR, because
// that is the only comparison that is commensurable across ten models with ten
// different floors. A chart of raw margins would make pythia-160m look like a
// near miss when it is in fact the furthest from passing.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const PC = F.positiveControl().slice().sort((a, b) => a.overFloor - b.overFloor);
const CR = F.chanceRange();
const nFail = PC.filter(r => r.gate === "INSENSITIVE").length;
const nPass = PC.length - nFail;

pres.addSection({ title: "3 Results" });
const s = S("CONTENT", "3 Results",
  `Positive control: ${nFail} of ${PC.length} cannot read the clinical field`);
K.mark("gate");

s.addText([
  { text: "Group 2's correct answer changes with the sex parameter. ",
    options: { color: MUT } },
  { text: "A model that answers the same either way is not fair. It cannot read the field.",
    options: { bold: true, color: INK } },
], { x: 0.55, y: 1.12, w: 12.2, h: 0.3, fontSize: 12, isTextBox: true,
     margin: 0, objectName: "sub" });

// ------------------------------------------------------------- the chart ----
s.addChart(pres.ChartType.bar, [{
  name: "Margin above the model's own noise floor",
  labels: PC.map(r => r.model),
  values: PC.map(r => Number(r.overFloor.toFixed(5))),
}], {
  x: 0.5, y: 1.62, w: 7.5, h: 4.74,
  barDir: "bar", barGapWidthPct: 42,
  chartColors: [PASS], invertedColors: [FAIL],
  showLegend: false,
  showTitle: true, title: "Sensitivity to the sex parameter, minus each model's own floor",
  titleFontSize: 11, titleColor: INK, titleFontFace: "+mn-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 8.5,
  dataLabelColor: MUT, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: "+0.000;−0.000",
  catAxisLabelColor: INK, catAxisLabelFontSize: 9.5, catAxisLabelFontFace: "+mn-lt",
  // Values cross zero, so the category labels must be pinned to the low end or
  // PowerPoint draws them through the middle of the bars.
  catAxisLabelPos: "low",
  catGridLine: { style: "none" },
  valAxisLabelColor: MUT, valAxisLabelFontSize: 8.5, valAxisLabelFontFace: "+mn-lt",
  valAxisLabelFormatCode: "0.00",
  valGridLine: { color: "E6EEF0", size: 0.75 },
  valAxisLineShow: false, catAxisLineShow: false,
  objectName: "gate-chart",
});
s.addText("▸ right of zero = passes the gate        ◂ left of zero = insensitive", {
  x: 0.55, y: 6.34, w: 7.5, h: 0.22, fontSize: 8.5, color: MUT, italic: true,
  isTextBox: true, margin: 0, objectName: "legend" });

// ------------------------------------------------------- the right panel ----
const PX = 8.28, PW = 4.5;

stat(s, { x: PX, y: 1.68, w: PW, n: `${nFail} of ${PC.length}`, size: 34, nh: 0.62,
  color: FAIL, label: "fail the positive control",
  sub: `All ${nFail} are Pythia. The ${nPass} that pass are Qwen3-8B and both OLMo-2 models.`,
  name: "s5a" });

card(s, { x: PX, y: 3.0, w: PW, h: 1.74, fill: "FBEEEC", name: "fe",
  kicker: "THE INTERPRETATION THAT MATTERS", kickerColor: FAIL,
  head: "A flat gender gap is not fairness.", headH: 0.28, headSize: 12.5,
  bodySize: 9.5,
  body: "Seven models show almost no gender gap anywhere in our set. Read "
      + "without a positive control, that is a clean bill of health. Read with "
      + "one, it is a model that cannot distinguish male from female when the "
      + "guideline demands it. Deploying it would be the more dangerous choice "
      + A.m("yoo2026") + "." });

card(s, { x: PX, y: 4.84, w: PW, h: 2.02, fill: TINT, name: "pool",
  kicker: "WHY WE REPORT WITHIN-LEVEL, NOT POOLED", kickerColor: TEAL,
  head: "Pooling hides the whole effect.", headH: 0.28, headSize: 12.5,
  bodySize: 9,
  body: `Group 2 flips the correct answer with the sex parameter, so pooling `
      + `across levels is pinned near 0.5 by construction: the ${CR.nModels} `
      + `Pythia models sit between ${CR.pooledLo.toFixed(4)} and `
      + `${CR.pooledHi.toFixed(4)}, which reads as chance.\n`
      + `Within a level they span ${CR.withinLo.toFixed(3)} to `
      + `${CR.withinHi.toFixed(3)}, and ${CR.widestModel} swings `
      + `${CR.maxSwing.toFixed(3)} while pooling to `
      + `${CR.widestPooled.toFixed(4)}. We never show the pooled figure alone.` });

// 75 seconds, about 169 words. The finding. Give it the time.
note(s, `[75s] This slide earns the rest of the talk.

Each bar is a model's sensitivity to the sex parameter, minus its own floor. Right of zero it passed; left of zero it did not. ${nFail} of ten are left of zero, and all ${nFail} are Pythia. The three that cleared are Qwen3-8B and both OLMo-2 models.

Now the sentence to land. Those seven show almost no gender gap anywhere in our set. Without Group 2 we would have written that up as seven fair models. With it we can say what it actually is: a model that cannot tell male from female where the guideline turns on it.

That is not equity. It is blindness, and in a clinical setting it is the more dangerous failure, because it looks exactly like the thing you wanted.

If there is time: Group 2 flips the correct answer with the parameter, so pooling pins everything near one half. ${CR.widestModel} swings ${CR.maxSwing.toFixed(3)} within a level and still pools to ${CR.widestPooled.toFixed(4)}.`);
