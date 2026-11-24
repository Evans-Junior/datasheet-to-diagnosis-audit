// SHORT deck, slide 6: the findings, as two charts and one fact.
//
// LIGHTENED on 2026-11-12. This slide used to carry two charts, three cards
// and the tier banner, and timed at 112 seconds against a 70 second budget. It
// was the densest slide in the deck and it sits where attention is already
// fading. RQ4 and RQ6 moved to the backup slides, where they cost no speaking
// time and are there when an examiner asks. What stayed is the pair of charts
// and the single most quotable fact in the project, which now gets the space
// it earns instead of a card at the bottom of a crowded row.
//
// RQ3 KEYS (D103). `spearman_rho` is the COMPOSITE, (mean |delta| - floor)
// against size. `spearman_rho_raw_gap` and `spearman_rho_floor` are its two
// components. The raw one used to be called `spearman_rho_gap`, which read as
// if it held the composite, because every table here calls `floor_relative_gap`
// "the gap"; it was renamed so it cannot be misread, and the sidecar now
// carries a `_key_meanings` legend.
//
// `by_family.pythia` is the controlled size series: one corpus, one recipe,
// seven sizes from 0.07B to 6.9B. Across all ten models, size is confounded
// with family AND with corpus, so the all-model figure answers "do bigger
// models differ" while the Pythia figure answers "does scale do this".
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const MG = F.merging().slice().sort((a, b) => a.timesFloor - b.timesFloor);
const ST = F.sizeTrend().slice().sort((a, b) => a.params - b.params);
const R3 = F.rq3Spearman();
const PR = F.rq5Probe();

const RHO_RAW   = R3.spearman_rho_raw_gap;  // mean_abs_delta vs size
const RHO_GAP   = R3.spearman_rho;          // floor_relative_gap vs size
const RHO_FLOOR = R3.spearman_rho_floor;    // the floor itself vs size

// Refuse to draw the slide if the controlled series is missing, rather than
// quietly presenting the confounded all-model figure on its own.
const PY3 = (R3.by_family || {}).pythia;
if (!PY3) {
  throw new Error("s6.js: rq3_size_trend_stats.json has no by_family.pythia. "
    + "Rerun:  .venv/bin/python -m src.stats");
}

const fam = m => (/pythia/.test(m) ? TEAL : /OLMo/.test(m) ? BERRY : WARN);
const zero = PR.subjectZero;
const bare = PR.rows.find(r => r.term === "non-binary");
const top = MG[MG.length - 1];

const s = S("CONTENT", "3 Results", "Identity read as the clinical parameter");
K.mark("results");

// --------------------------------------------- chart A: identity merging ----
s.addText("RQ2  ·  IDENTITY–SPCU MERGING, AS A MULTIPLE OF EACH MODEL'S OWN FLOOR", {
  x: 0.55, y: 1.16, w: 6.1, h: 0.2, fontSize: 8, bold: true, color: TEAL,
  charSpacing: 0.6, isTextBox: true, margin: 0, objectName: "ka" });

s.addChart(pres.ChartType.bar, [{
  name: "Multiple of the model's own noise floor",
  labels: MG.map(r => r.model),
  values: MG.map(r => Number(r.timesFloor.toFixed(2))),
}], {
  x: 0.5, y: 1.38, w: 6.2, h: 2.8,
  barDir: "bar", barGapWidthPct: 38,
  chartColors: MG.map(r => (r.above ? fam(r.model) : "C8D7DB")),
  showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 8,
  dataLabelColor: MUT, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: "0.0×;−0.0×",
  catAxisLabelColor: INK, catAxisLabelFontSize: 8.5, catAxisLabelFontFace: "+mn-lt",
  catAxisLabelPos: "low", catGridLine: { style: "none" },
  valAxisLabelColor: MUT, valAxisLabelFontSize: 8, valAxisLabelFontFace: "+mn-lt",
  valAxisLabelFormatCode: "0", valGridLine: { color: "E6EEF0", size: 0.75 },
  valAxisLineShow: false, catAxisLineShow: false,
  objectName: "merge-chart",
});
s.addText([
  { text: "Coloured bars clear their own floor; grey bars do not.  ", options: { color: MUT } },
  { text: `Largest is ${top.model} at ${top.timesFloor.toFixed(1)}× — the fully open-data model.`,
    options: { bold: true, color: INK } },
], { x: 0.55, y: 4.22, w: 6.1, h: 0.42, fontSize: 9, lineSpacing: 11,
     isTextBox: true, margin: 0, objectName: "la" });

// ------------------------------------------------- chart B: scale trend ----
s.addText("RQ3  ·  FLOOR-SUBTRACTED GENDER GAP, MODELS ORDERED BY PARAMETER COUNT", {
  x: 6.88, y: 1.16, w: 5.9, h: 0.2, fontSize: 8, bold: true, color: BERRY,
  charSpacing: 0.6, isTextBox: true, margin: 0, objectName: "kb" });

s.addChart(pres.ChartType.bar, [{
  name: "Gap above floor",
  labels: ST.map(r => `${r.model} (${r.params}B)`),
  values: ST.map(r => Number(r.gap.toFixed(5))),
}], {
  x: 6.83, y: 1.38, w: 6.0, h: 2.8,
  barDir: "bar", barGapWidthPct: 38,
  chartColors: ST.map(r => fam(r.model)),
  showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 8,
  dataLabelColor: MUT, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: "+0.000;−0.000",
  catAxisLabelColor: INK, catAxisLabelFontSize: 8.5, catAxisLabelFontFace: "+mn-lt",
  catAxisLabelPos: "low", catGridLine: { style: "none" },
  valAxisLabelColor: MUT, valAxisLabelFontSize: 8, valAxisLabelFontFace: "+mn-lt",
  valAxisLabelFormatCode: "0.00", valGridLine: { color: "E6EEF0", size: 0.75 },
  valAxisLineShow: false, catAxisLineShow: false,
  // Without this padding the pythia-160m bar ends flush against the category
  // column and its data label overprints the model name.
  valAxisMinVal: -0.015, valAxisMaxVal: 0.025,
  objectName: "scale-chart",
});
// The floor's own trend is reported beside the gap's on purpose: it is the
// only thing that rules out "the instrument just got noisier with scale".
s.addText([
  { text: "all 10:  raw ", options: { color: MUT } },
  { text: `ρ ${F.f3(RHO_RAW)}`, options: { bold: true, color: INK } },
  { text: "  ·  floor-subtracted ", options: { color: MUT } },
  { text: `ρ ${F.f3(RHO_GAP)}`, options: { bold: true, color: INK } },
  { text: "  ·  the floor itself ", options: { color: MUT } },
  { text: `ρ ${F.f3(RHO_FLOOR)}, ${F.p(R3.spearman_p_floor)}`,
    options: { bold: true, color: FAIL } },
  { text: "\nwithin Pythia alone, the one controlled size series:  ",
    options: { color: MUT } },
  { text: `raw ρ ${F.f3(PY3.spearman_rho_raw_gap)}, ${F.p(PY3.spearman_p_raw_gap)}`,
    options: { bold: true, color: TEAL } },
], { x: 6.88, y: 4.22, w: 5.9, h: 0.46, fontSize: 9, lineSpacing: 11,
     isTextBox: true, margin: 0, objectName: "lb" });

// ------------------------------------------------------------ RQ1, big ----
// This is the most quotable sentence in the project and it used to be a small
// card at the bottom of a crowded row. It gets the width now.
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 4.82, w: 12.23, h: 1.12, rectRadius: 0.06,
  fill: { color: INK }, line: { color: INK, width: 0 }, objectName: "rq1-bg" });
s.addText(String(zero.pile), { x: 0.85, y: 4.92, w: 1.3, h: 0.9, fontSize: 54,
  bold: true, color: WARN, fontFace: "Cambria", align: "center", valign: "middle",
  isTextBox: true, margin: 0, objectName: "rq1-n" });
s.addText([
  { text: `RQ1  ·  occurrences of “${zero.term}” in The Pile, and ${zero.olmo} in olmo-mix-1124.  `,
    options: { bold: true, color: PAPER } },
  { text: `The bare term appears ${(bare.olmo / 1e6).toFixed(2)} million times in OLMo-mix, so these patients are in the text — just never in a clinic.`,
    options: { color: "AFCBD1" } },
  { text: `\nThe guidelines name them. The training data does not. `,
    options: { bold: true, color: PAPER } },
  { text: `Exact n-gram counts, not estimates ${A.m("liu2024", "dev2021")}.`,
    options: { color: "8FB2BA" } },
], { x: 2.3, y: 4.94, w: 10.3, h: 0.9, fontSize: 11, lineSpacing: 15,
     valign: "middle", isTextBox: true, margin: 0, objectName: "rq1-t" });

tierBanner(s, { x: 0.55, y: 6.1, w: 12.23, h: 0.44, fs: 8, name: "tier" });

// 70 seconds, about 158 words.
note(s, `[70s] Two charts and one fact. Do not read the axis labels.

Left: identity-SPCU merging, in multiples of each model's own floor. Three coloured bars cleared their floor. Seven grey ones did not. The largest is ${top.model} at ${top.timesFloor.toFixed(1)} times, and say the uncomfortable part out loud: that is the fully open-data model. We are not claiming open models are fairer. We are claiming they are the only ones we can diagnose.

Right: the gap grows with scale. Raw, ${F.f3(RHO_RAW)}. After subtracting each model's own floor, ${F.f3(RHO_GAP)}. And the floor itself, ${F.f3(RHO_FLOOR)}, not significant. If bigger models were simply noisier, that third number would be the big one. Within Pythia alone, one corpus and seven sizes, ${F.f3(PY3.spearman_rho_raw_gap)}.

Then stop, and point at the black band. The phrase occurs zero times in both corpora, while the bare term is in the millions. The guidelines name these patients. The data never puts them in a clinic.`);
