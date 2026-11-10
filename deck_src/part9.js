const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
// D090: read from results/tables/rq2_hypothesis_tests.csv at build time.
const F = require("./figures.js");
// D095: k and the resolution limit for the exploratory merging finding
// were typed as "three vignettes" and 0.125. Both come from the table.
const _mg0 = F.merging()[0];

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

// ============ 22. THE HYPOTHESES ================================ //
let s = S("CONTENT", "Results", "The pre-registered hypotheses, tested exactly as filed");
const hRows = [[
  { text: "Hypothesis", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5 } },
  { text: "Difference", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5, align: "center" } },
  { text: "95% CI", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5, align: "center" } },
  { text: "Holm p", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5, align: "center" } },
  { text: "Verdict", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 11.5 } },
]];
// D090: every cell derived. The hand-typed version of this table was two
// scoring rounds behind -- it showed H1 at -0.0042 with Holm 0.750 and H3 at
// +0.0015 against a 0.0131 margin, none of which was current.
const _h1 = F.hypothesis("H1"), _h2 = F.hypothesis("H2"), _h3 = F.hypothesis("H3");
[
  [`H1   biased conditions, ${_h1.k} vignettes`, _h1.txt.delta, _h1.txt.ci,
   _h1.txt.pHolm, _h1.rejects ? "Rejects at FWER .05" : "No evidence",
   _h1.rejects ? PASS : FAIL],
  [`H2   psychologizing cue, ${_h2.k} vignette`, _h2.txt.delta, "single vignette",
   _h2.txt.pHolm, _h2.rejects ? "Rejects at FWER .05" : "No evidence",
   _h2.rejects ? PASS : FAIL],
  [`H3   neutral conditions, ${_h3.k} vignettes`, _h3.txt.delta, _h3.txt.ci,
   _h3.txt.pHolm, _h3.tost ? "Equivalence supported" : "Equivalence NOT supported",
   _h3.tost ? PASS : FAIL],
  ["H4   corpus linkage", "see RQ4 slide", "not identifiable", "withdrawn", "Reframed", WARN],
].forEach((r, i) => hRows.push([
  { text: r[0], options: { bold: true, color: INK, fontSize: 11, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { color: INK, fontSize: 11, align: "center", fontFace: "Courier New", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { color: MUT, fontSize: 10.5, align: "center", fontFace: "Courier New", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[3], options: { color: MUT, fontSize: 11, align: "center", fontFace: "Courier New", fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[4], options: { bold: true, color: r[5], fontSize: 11, fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(hRows, { x: 0.55, y: 1.25, w: 12.2, colW: [4.0, 1.7, 2.6, 1.4, 2.5], rowH: 0.46,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.12, 0.06, 0.12], fontFace: "Calibri", autoPage: false });

// D090: the old version of this line said "every one failed to reject" and
// called all three instrument insensitivity. That is no longer accurate: H3's
// equivalence IS supported, and H1's failure to reject is a resolution limit
// rather than an absence of signal. Both distinctions are the point.
s.addText([
  { text: "Every hypothesis was tested exactly as filed. ", options: { bold: true, color: INK } },
  { text: `H1 does not reject at FWER .05, but its interval excludes zero and `
        + `k = ${_h1.k} clusters cap the exact p at ${_h1.txt.pExact}: that is a `
        + `resolution limit, not a null. H3's equivalence is `
        + `${_h3.tost ? "supported" : "NOT supported"}. `
        + `Nothing here is read as evidence of fairness, because the gate `
        + `commitment forbids it and `
        + `${F.reportable().ok ? "" : "no row is clinician-verified yet"}.`,
    options: { color: MUT } },
], { x: 0.55, y: 3.6, w: 12.2, h: 0.4, fontSize: 12.5, margin: 0, isTextBox: true });

const hn = [
  { h: `H1 is resolution-limited, not null`,
    b: `Its interval excludes zero (${_h1.txt.ci}) and the unclamped bootstrap `
     + `reads 0.0001. But with k = ${_h1.k} clusters an exact sign-flip test `
     + `cannot go below 1/2^${_h1.k} = ${_h1.txt.pExact}, so alpha = .05 was `
     + `unreachable by construction. Holm then gives ${_h1.txt.pHolm}. `
     + `A fifth referral vignette is the only honest route to .05.`, c: WARN },
  { h: "H3's equivalence margin is set by one cell",
    b: `The margin is ${_h3.txt.margin}, bounding an effect of ${_h3.txt.delta} `
     + `-- and it comes from a single model-item pair in the four-option floor `
     + `stratum. Tightening it is an instrument job, not a statistics job: `
     + `D090 token-matched that item's options across all three scoring `
     + `tokenizers, where the limit had never been enforced.`, c: PASS },
  { h: "H2 is scoped to one scenario by design", b: "The table says so in its own caveat column. It does not generalise to the condition, let alone to the family. A single-vignette claim is reported as a single-vignette claim.", c: TEAL },
];
hn.forEach((c, i) => {
  const x = 0.55 + i * 4.1;
  card(s, { x, y: 4.06, w: 3.85, h: 2.34, name: "hn" + i });
  s.addText(c.h, { x: x + 0.22, y: 4.24, w: 3.42, h: 0.62, fontSize: 12.5, bold: true,
    color: c.c, lineSpacing: 15, margin: 0, isTextBox: true, objectName: "hnh" + i });
  s.addText(c.b, { x: x + 0.22, y: 4.92, w: 3.42, h: 1.36, fontSize: 11.5, color: MUT,
    lineSpacing: 14.5, margin: 0, isTextBox: true, objectName: "hnb" + i });
});
note(s, "The honest framing is that the pre-registration worked. It removed a false positive in H1 and it stopped us reading three nulls as evidence of fairness. A project that found what it predicted would be less convincing than this.");

// ============ 23. THE EXPLORATORY FINDING ======================= //
s = S("CONTENT_DARK", "Results", "An exploratory finding the hypotheses did not predict");
s.addText("The same Group 2 items, used the other way round. Hold the sex parameter fixed and vary only the identity label, so the correct answer is identical within every pair and any difference is unwarranted by construction.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.4, fontSize: 13.5, color: "BCD3D8", lineSpacing: 17, margin: 0, isTextBox: true });

// D096. These four bars were typed, and all four had moved: the chart still
// read 16.5 / 9.6 / 8.1 / 0.4 from an earlier roster, and the order was wrong
// as well, because OLMo-2-7B-Instruct has overtaken Qwen3-8B. D095 missed this
// one because it is a values array rather than a string, so the stale-text scan
// could not see it. The Pythia bar is the LARGEST of the seven, not their mean:
// a bar that fails on its best member is a claim about all seven, while a mean
// could hide a single size that clears its floor.
const _MG = F.merging();
const _mgTop = _MG.filter(m => !/pythia/.test(m.model))
                  .sort((a, b) => b.timesFloor - a.timesFloor);
const _mgPy = _MG.filter(m => /pythia/.test(m.model))
                 .sort((a, b) => b.timesFloor - a.timesFloor);
const _mgLbl = m => m.replace("OLMo-2-7B-Instruct", "OLMo-2-7B Instruct")
                     .replace(/^OLMo-2-7B$/, "OLMo-2-7B base");
s.addChart(pres.ChartType.bar, [
  { name: "Interaction, times the model's own floor",
    labels: [..._mgTop.map(m => _mgLbl(m.model)),
             `best of ${_mgPy.length} Pythia sizes`],
    values: [..._mgTop.map(m => Number(m.timesFloor.toFixed(1))),
             Number(_mgPy[0].timesFloor.toFixed(1))] },
], { x: 0.55, y: 1.74, w: 6.6, h: 3.5, barDir: "bar", catAxisLabelPos: "low",
  chartColors: [PASS], showTitle: true,
  title: "Identity read as the sex parameter, relative to each model's noise floor",
  titleColor: PAPER, titleFontSize: 11.5, titleFontFace: "+mn-lt",
  showLegend: false, showValue: true, dataLabelPosition: "outEnd",
  dataLabelColor: PAPER, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
  dataLabelFormatCode: '0.0"x"',
  catAxisLabelColor: "BCD3D8", valAxisLabelColor: "BCD3D8",
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  valGridLine: { color: "1C4E59", size: 0.75 }, catGridLine: { style: "none" },
  barGapWidthPct: 45 });

card(s, { x: 7.4, y: 1.74, w: 5.35, h: 1.72, fill: "1C4E59", kicker: "WHAT IT MEANS CLINICALLY",
  kickerColor: "7FD4C8", name: "ex1" });
s.addText("A trans man receives less probability on an indicated pregnancy test. A trans woman receives more probability on a cervical screening not indicated for her. The model is substituting the identity label for the clinical sex parameter.",
  { x: 7.62, y: 2.28, w: 4.91, h: 1.06, fontSize: 12, color: PAPER, lineSpacing: 15, margin: 0, isTextBox: true });

card(s, { x: 7.4, y: 3.58, w: 5.35, h: 1.66, fill: "1C4E59", kicker: "THE UNCOMFORTABLE SHAPE OF IT",
  kickerColor: WARN, name: "ex2" });
s.addText("The three models that exceed their floor are exactly the three that can do the clinical task at all. The merging is not a small-model artefact that capability removes. It is visible only in the capable models.",
  { x: 7.62, y: 4.12, w: 4.91, h: 1.0, fontSize: 12, color: "D6E6E9", lineSpacing: 15, margin: 0, isTextBox: true });

card(s, { x: 0.55, y: 5.44, w: 12.2, h: 1.0, fill: "1C4E59", name: "ex3" });
s.addText([
  { text: "Reported as exploratory. ", options: { bold: true, color: WARN } },
  { text: "It came out of implementing the control, not out of testing H1 to "
        + "H4, so it sits outside the Holm family with no p value claimed. "
        + `With ${_mg0.nVignettes} vignettes the finest resolvable p is `
        + `${_mg0.pResolution}. `, options: { color: "D6E6E9" } },
  { text: "A by-product of a control promoted to a confirmatory hypothesis after the fact is exactly what pre-registration exists to prevent, so we do not promote it.", options: { bold: true, color: PAPER } },
], { x: 0.77, y: 5.62, w: 11.76, h: 0.68, fontSize: 12, lineSpacing: 15.5, margin: 0, isTextBox: true });
note(s, "This is the project's most interesting result and the one most likely to be over-read. Be scrupulous about the exploratory label. The Gender Harmony Model is what made it visible, because without separating identity from the sex parameter the two could not have been made to disagree.");

// ============ 24. RQ2c DATA OR TUNING =========================== //
s = S("CONTENT", "Results", "Data or post-training? A contrast that isolates tuning");
s.addText("Post-training was a live alternative explanation, because the effect is largest in instruction-tuned models. OLMo-2-7B and its Instruct sibling share a corpus exactly and differ only in post-training, so their difference isolates tuning.",
  { x: 0.55, y: 1.2, w: 12.2, h: 0.44, fontSize: 13.5, color: INK, lineSpacing: 17, margin: 0, isTextBox: true });

// D095. Every number on this slide was typed, and the slide was still
// presenting the 0.38x / 2.88x framing from D049 with a 3-vignette resolution
// limit. The contrast now runs over 4 vignettes, so the limit is 1/2^4, and
// both floors have moved. The old-floor column is kept because the reversal
// is the point of the slide -- but it is now COMPUTED from the recorded old
// floors in quadrature, the same way the current one is, instead of being a
// remembered pair of numbers.
const PT = F.postTraining();
const _fc = F.floorComparison();
const _oldBase = (_fc.byModel[PT.base] || {}).oldFloor;
const _oldTuned = (_fc.byModel[PT.tuned] || {}).oldFloor;
const _oldCombined = Math.sqrt(_oldBase * _oldBase + _oldTuned * _oldTuned);
const _timesOld = PT.delta / _oldCombined;
const _r4 = v => v.toFixed(4);
const _rx = v => v.toFixed(2) + "x";

box(s, { x: 0.55, y: 1.86, w: 3.1, h: 1.0,
  t: `${PT.base}\nmerging  ${_r4(PT.mergingBase)}`, fill: PAPER, line: TEAL, fs: 12, name: "rc1" });
arrow(s, { x: 3.78, y: 2.26, w: 0.6, h: 0.2, color: TEAL, name: "rca" });
// D096. This label sat in a box from x 3.5 to 4.7 while the card beside it
// starts at 4.5, so "only" was drawn underneath the card and the reader saw
// "post-training onl". Confined to the 0.85in gap between the two cards and
// wrapped over two lines.
s.addText("post-training\nonly", { x: 3.65, y: 2.46, w: 0.85, h: 0.36, fontSize: 8,
  italic: true, lineSpacing: 9.5,
  color: MUT, align: "center", margin: 0, isTextBox: true });
box(s, { x: 4.5, y: 1.86, w: 3.1, h: 1.0,
  t: `${PT.tuned}\nmerging  ${_r4(PT.mergingTuned)}`, fill: PAPER, line: TEAL, fs: 12, name: "rc2" });
arrow(s, { x: 7.73, y: 2.26, w: 0.6, h: 0.2, color: INK, name: "rcb" });
box(s, { x: 8.45, y: 1.86, w: 4.3, h: 1.0,
  t: `difference  ${F.f4(PT.delta)}`, fill: INK, line: INK, tc: PAPER, fs: 14, name: "rc3" });

// D095. "Inside the noise" was typed as a fact. Whether the contrast sits
// inside the OLD floor depends on a delta that has since grown, so it has to
// be read off the ratio. On the current tables the delta clears even the old
// floor, which means D049's conclusion now fails for two independent reasons
// rather than one -- a stronger statement, and the opposite of what the
// hand-typed card claimed.
const _oldInside = _timesOld < 1;
const rq2c = [
  { h: "Against the old floor", n: _rx(_timesOld),
    s: `Combined floor ${_r4(_oldCombined)}. `
     + (_oldInside
         ? "Inside the noise, so D049 concluded that tuning adds nothing this "
           + "instrument can resolve."
         : "D049 read this as inside the noise on a smaller delta. On the "
           + "current set it clears even the inflated floor, so that reading "
           + "no longer holds on its own terms either."),
    c: _oldInside ? FAIL : WARN },
  { h: "Against the corrected floor", n: _rx(PT.timesFloor),
    s: `Combined floor ${_r4(PT.floorCombined)}. `
     + (PT.timesFloor > 1
         ? "Exceeds it, so post-training does increase the merging."
         : "Does not exceed it, so this instrument cannot resolve a "
           + "post-training effect."),
    c: PT.timesFloor > 1 ? PASS : FAIL },
];
rq2c.forEach((c, i) => {
  const x = 0.55 + i * 6.25;
  card(s, { x, y: 3.1, w: 6.05, h: 1.5, fill: i ? "E6F5F2" : "FBEEEC", name: "rq2c" + i });
  s.addText(c.h, { x: x + 0.22, y: 3.24, w: 3.3, h: 0.3, fontSize: 11.5, bold: true,
    color: c.c, margin: 0, isTextBox: true, objectName: "rqh" + i });
  s.addText(c.n, { x: x + 0.22, y: 3.54, w: 1.8, h: 0.5, fontSize: 28, bold: true, color: c.c,
    fontFace: "Cambria", margin: 0, isTextBox: true, objectName: "rqn" + i });
  s.addText(c.s, { x: x + 2.1, y: 3.56, w: 3.72, h: 0.9, fontSize: 11, color: INK,
    lineSpacing: 13.5, margin: 0, isTextBox: true, objectName: "rqs" + i });
});
card(s, { x: 0.55, y: 4.8, w: 12.2, h: 1.6, fill: INK,
  kicker: (_oldInside
    ? "THE CONCLUSION REVERSED, AND WE MARKED IT SUPERSEDED RATHER THAN EDITING IT"
    : "THE CONCLUSION IS WITHDRAWN TWICE OVER, AND MARKED SUPERSEDED RATHER THAN EDITED"),
  kickerColor: WARN, name: "rqrev" });
s.addText("The effect never changed. Only the floor did. "
  + (PT.baseInsideOwnFloor
      ? `Note that the base model stays inside its own floor, `
        + `${_r4(PT.mergingBase)} against ${_r4(PT.floorBase)}, so on this `
        + "instrument the increase is attributable to post-training."
      : `Note that the base model also clears its own floor, `
        + `${_r4(PT.mergingBase)} against ${_r4(PT.floorBase)}, so the honest `
        + "reading is that both stages contribute, not that tuning alone does.")
  + " The claim that tuning adds nothing was an artefact of the inflated floor "
  + "and is withdrawn. What survives is the limitation: one model pair, "
  + `${PT.nVignettes} vignettes, resolution limit ${PT.pResolution}, no p value claimed.`,
  { x: 0.77, y: 5.34, w: 11.76, h: 0.98, fontSize: 12.5, color: PAPER, lineSpacing: 16, margin: 0, isTextBox: true });
note(s, "Reversing one of our own published conclusions is a credibility asset if we present it ourselves. The decision log keeps D049 in place with a superseded banner rather than rewriting it, so the reversal is auditable.");

module.exports = {};
