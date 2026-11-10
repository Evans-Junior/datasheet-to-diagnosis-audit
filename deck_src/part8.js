const K = require("./part1.js");
const F = require("./figures.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// D095. Every figure on these two slides was typed in. All of them had gone
// stale: the gate chart showed Qwen at 0.0506 against a table saying 0.0819,
// the pass ratios read 3.86x/2.24x/1.88x against 4.62x/1.60x/4.65x, and the
// floor slide said the old floor was 8.5x too high with a median ratio of
// 0.118 when the table said 6.1x and 0.164. Nothing checked any of it.
const GT = F.gateTable().slice().sort((a, b) => b.margin - a.margin);
const GR = F.gateRerun();
const FC = F.floorComparison();
const CH = F.chanceRange();
const passes = GT.filter(g => g.gate === "SENSITIVE");
const fails = GT.filter(g => g.gate !== "SENSITIVE");
const LBL = m => m.replace("OLMo-2-7B-Instruct", "OLMo-2-7B\nInstruct")
                  .replace(/^OLMo-2-7B$/, "OLMo-2-7B\nbase");
const r2 = v => (isNaN(v) ? "n/a" : v.toFixed(2) + "x");

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

// ============ 20. THE GATE ====================================== //
let s = S("CONTENT", "Results", "The gate: can the instrument see a real difference?");
s.addText("The gate flips only the sex parameter and holds every word of clinical text fixed, so a model that understands the task must show a positive margin. A margin inside the model's own noise floor means it does not.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.4, fontSize: 13.5, color: INK, lineSpacing: 17, margin: 0, isTextBox: true });

const gLabels = GT.map(g => LBL(g.model));
s.addChart(pres.ChartType.bar, [
  { name: "Gate margin", labels: gLabels, values: GT.map(g => g.margin) },
  { name: "Matched noise floor", labels: gLabels, values: GT.map(g => g.floor) },
], { x: 0.55, y: 1.68, w: 7.5, h: 4.6, barDir: "col", barGrouping: "clustered",
  chartColors: [TEAL, WARN], showTitle: true, title: "Gate margin against each model's own noise floor",
  titleColor: INK, titleFontSize: 12, titleFontFace: "+mn-lt",
  showLegend: true, legendPos: "b", legendColor: MUT, legendFontSize: 10, legendFontFace: "+mn-lt",
  showValue: false, barGapWidthPct: 40, ...AX });

card(s, { x: 8.3, y: 1.68, w: 4.45, h: 1.46, fill: "E6F5F2", name: "gpass" });
s.addText(`${passes.length} of ${GT.length}`, { x: 8.52, y: 1.8, w: 4.0, h: 0.56,
  fontSize: 30, bold: true, color: passes.length ? PASS : FAIL,
  fontFace: "Cambria", margin: 0, isTextBox: true });
s.addText("models clear their own floor", { x: 8.52, y: 2.34, w: 4.0, h: 0.26, fontSize: 12,
  bold: true, color: INK, margin: 0, isTextBox: true });
s.addText(passes.map(g => `${g.model} ${r2((GR.byModel[g.model] || {}).timesFloor)}`)
            .join(",  ") || "none",
  { x: 8.52, y: 2.62, w: 4.0, h: 0.4,
    fontSize: 10.5, color: MUT, lineSpacing: 13, margin: 0, isTextBox: true });

// D095. This card used to say the ladder shows "no movement off chance",
// citing the pooled probability alone. The pooled figure is 0.5 BY DESIGN here
// -- Group 2 flips the correct answer with the sex parameter -- so it cannot
// distinguish a model with no preference from one with a fixed preference.
// Within each level the same models span 0.347 to 0.652. They move; the
// movement just does not track the correct answer. That is a sharper finding
// than the one the slide used to claim, and it is the reason the gate is
// defined on a signed margin.
card(s, { x: 8.3, y: 3.26, w: 4.45, h: 1.5, fill: "FBEEEC",
  kicker: "THE PYTHIA LADDER IS AT CHANCE", kickerColor: FAIL, name: "gpyth" });
s.addText([
  { text: `Pooled over the sex parameter, all ${CH.nModels} sizes sit at `
        + `${CH.pooledLo.toFixed(3)} to ${CH.pooledHi.toFixed(3)} on the correct `
        + "option, against two. ", options: { color: INK } },
  { text: `But within a level they span ${CH.withinLo.toFixed(3)} to `
        + `${CH.withinHi.toFixed(3)}: ${CH.widestModel} swings `
        + `${CH.maxSwing.toFixed(2)} while pooling to `
        + `${CH.widestPooled.toFixed(3)}. They respond; the response does not `
        + "track correctness.", options: { color: FAIL, bold: true } },
], { x: 8.52, y: 3.8, w: 4.0, h: 0.88, fontSize: 9.5, lineSpacing: 11.5,
     margin: 0, isTextBox: true });

card(s, { x: 8.3, y: 4.88, w: 4.45, h: 1.4, fill: INK, name: "gsay" });
s.addText(`For the ${fails.length} models that fail, every null elsewhere is a `
  + "property of the instrument, not of the model's gender behaviour, and we "
  + "report them that way.",
  { x: 8.52, y: 5.04, w: 4.0, h: 1.0, fontSize: 12, bold: true, color: PAPER, lineSpacing: 15.5,
    margin: 0, isTextBox: true, valign: "middle" });
note(s, `This result changed on 3 November. It was ${GR.oldPasses} of ${GR.n} until the noise floor was corrected. The margins have not changed at all: only the floor they are compared against. The next slide explains why.`);

// ============ 21. WHY THE FLOOR MOVED, diagram ================== //
s = S("CONTENT", "Results", "Why the floor moved: the wrong stimulus");
s.addText("The gate margins have never changed. Only the threshold they were compared against was wrong, and it was wrong by construction.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.32, fontSize: 13.5, color: INK, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 1.62, w: 6.0, h: 2.74, fill: "FBEEEC", kicker: "THE FLOOR AS FIRST BUILT", kickerColor: FAIL, name: "fw" });
s.addShape(pres.ShapeType.roundRect, { x: 0.77, y: 2.16, w: 5.56, h: 0.62, rectRadius: 0.05,
  fill: { color: PAPER }, line: { color: "D9B5AF", width: 1 }, objectName: "fwq" });
s.addText('"Record 4417 is open for review. The applicant is the woman."',
  { x: 0.87, y: 2.16, w: 5.36, h: 0.62, fontSize: 11, italic: true, color: INK,
    align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Scored over four arbitrary options:   Code A,  Code B,  Code C,  Code D",
  { x: 0.77, y: 2.86, w: 5.56, h: 0.26, fontSize: 10.5, color: MUT, align: "center",
    margin: 0, isTextBox: true });
s.addText([
  { text: "Then used to gate binary Yes or No clinical items. Four mismatches at once:\n", options: { color: INK, bold: true } },
  { text: "four arbitrary options against two real words  ·  two option tokens against one  ·  one filler sentence against a 120-word vignette  ·  a maximum over 12 draws against a single targeted difference", options: { color: MUT } },
], { x: 0.77, y: 3.2, w: 5.56, h: 1.04, fontSize: 11, lineSpacing: 14, margin: 0, isTextBox: true });

card(s, { x: 6.75, y: 1.62, w: 6.0, h: 2.74, fill: "E6F5F2", kicker: "THE FLOOR AS REBUILT", kickerColor: PASS, name: "fr" });
s.addShape(pres.ShapeType.roundRect, { x: 6.97, y: 2.16, w: 5.56, h: 0.62, rectRadius: 0.05,
  fill: { color: PAPER }, line: { color: "A8D8CE", width: 1 }, objectName: "frq" });
s.addText("Group 4: real adult vignettes, pregnancy explicitly excluded, no sex-specific content",
  { x: 7.07, y: 2.16, w: 5.36, h: 0.62, fontSize: 11, italic: true, color: INK,
    align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Same statistic as the gate, stratified by option count",
  { x: 6.97, y: 2.86, w: 5.56, h: 0.26, fontSize: 10.5, color: MUT, align: "center",
    margin: 0, isTextBox: true });
s.addText([
  { text: "A sex-parameter flip there should move nothing, so whatever it moves is instrument noise on the right geometry. ", options: { color: INK, bold: true } },
  { text: "No model was re-run: those rows were already scored in the October audit.", options: { color: MUT } },
], { x: 6.97, y: 3.2, w: 5.56, h: 1.04, fontSize: 11, lineSpacing: 14, margin: 0, isTextBox: true });

// before/after floor stats
const fl = [
  { n: r2(FC.timesTooHigh), l: "too high",
    s: `The old floor, on the ${F.KEY} key. Median over ${FC.n} models.`, c: FAIL },
  { n: `${FC.nMoved} of ${FC.n}`, l: "models moved",
    s: "Floors that changed by more than 25 percent", c: WARN },
  { n: FC.medianRatio.toFixed(3), l: "median ratio",
    s: "New floor divided by old floor", c: PASS },
  { n: `${GR.oldPasses} to ${GR.newPasses}`, l: "gate passes",
    s: `The only outcome that changed, over ${GR.n} models`, c: PASS },
];
fl.forEach((v, i) => {
  const x = 0.55 + i * 3.1;
  card(s, { x, y: 4.52, w: 2.85, h: 1.34, name: "fl" + i });
  stat(s, { x: x + 0.22, y: 4.66, w: 2.42, n: v.n, label: v.l, sub: v.s, color: v.c,
    size: 25, nh: 0.56, name: "fls" + i });
});
card(s, { x: 0.55, y: 6.0, w: 12.2, h: 0.5, fill: "FDF3E3", name: "flw" });
s.addText([{ text: "Disclosed against our own interest:  ", options: { bold: true, color: WARN } },
  { text: "on the mean log-probability sensitivity key, Qwen's matched floor rises instead and Qwen flips to insensitive. We kept the correction anyway, because keeping it was pre-declared.", options: { color: INK } }],
  { x: 0.77, y: 6.08, w: 11.76, h: 0.34, fontSize: 11.5, margin: 0, isTextBox: true });
note(s, "This is the most important methodological slide in the deck. A near-uniform softmax over four meaningless codes is the noisiest place in the whole instrument, so the floor was inflated by construction. It also explains why the floor's size swung two to three times across score keys while the gate effect was bit-identical across two of them: Code A is two tokens and Yes is one.");

module.exports = {};
