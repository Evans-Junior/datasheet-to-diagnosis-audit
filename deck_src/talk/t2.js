// Talk deck, beats 3 and 4: the design, and the measurement biases it defeats.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note, badge,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const LV = F.liveVignettes();
const VG = F.vignetteGroups();

pres.addSection({ title: "2 The instrument" });

// ------------------------------- 3. separating sex from gender identity ----
{
  const s = S("CONTENT", "2 The instrument",
    "Separating what is clinical from what is social");

  s.addText("HL7 Gender Harmony Model (McClure et al., JAMIA 2021). "
    + "The sex parameter for clinical use is held FIXED; gender identity varies.",
    { x: 0.55, y: 1.24, w: 12.2, h: 0.32, fontSize: 13, color: INK,
      isTextBox: true, margin: 0, objectName: "hl7" });

  // The arm grid, stated correctly: both SPCU values are crossed with all four
  // identity labels INCLUDING blinded, and the whole grid is run at three
  // paraphrases. A grid quoted without the paraphrase layer understates the
  // design by a factor of three and quietly removes the robustness check that
  // slide 6 then claims.
  const cols = [
    { h: "2 sex parameters", b: "female  ·  male\n\nPhysiology. Held fixed within a comparison.", c: TEAL },
    { h: "4 identity labels", b: "woman  ·  man  ·  non-binary  ·  gender-blinded\n\nThe blinded arm is the reference.", c: BERRY },
    { h: "3 paraphrases", b: "Same clinical facts, three wordings.\n\nSo wording sensitivity can be separated from bias.", c: WARN },
  ];
  cols.forEach((c, i) => {
    const x = 0.55 + i * 3.06;
    card(s, { x, y: 1.66, w: 2.84, h: 1.74, fill: TINT, name: "ag" + i,
      kicker: c.h.toUpperCase(), kickerColor: c.c, body: c.b, bodySize: 11 });
  });
  card(s, { x: 9.73, y: 1.66, w: 3.05, h: 1.74, fill: INK, name: "agt" });
  stat(s, { x: 9.95, y: 1.80, w: 2.6, n: "24", label: "arms per vignette",
    sub: "2 \u00D7 4 \u00D7 3. Every prompt has a matched partner differing "
       + "only in the identity label.",
    color: "7FD4C8", size: 38, nh: 0.70, name: "agts" });
  s.addText("Four vignette groups, each doing a different job",
    { x: 0.55, y: 3.62, w: 12.2, h: 0.3, fontSize: 15, bold: true, color: INK,
      isTextBox: true, margin: 0, objectName: "gh" });
  const groups = [
    { n: VG.groups[1].length, h: "Sex-neutral", b: "Guideline is identical for everyone. Any gap here is bias.", c: TEAL },
    { n: VG.groups[2].length, h: "Sex-specific", b: "Correct answer DOES differ by sex. The positive control.", c: PASS },
    { n: VG.groups[3].length, h: "Historically biased", b: "Conditions with documented clinical disparities. H1, H2.", c: FAIL },
    { n: VG.groups[4].length, h: "Noise baseline", b: "Clinically inert. Measures the instrument's own jitter.", c: WARN },
  ];
  groups.forEach((g, i) => {
    const x = 0.55 + i * 3.12;
    card(s, { x, y: 4.0, w: 2.94, h: 1.52, fill: TINT, name: "gg" + i });
    badge(s, { x: x + 0.22, y: 4.18, n: g.n, d: 0.44, fs: 15, color: g.c, name: "gb" + i });
    s.addText(g.h, { x: x + 0.76, y: 4.2, w: 2.0, h: 0.4, fontSize: 12.5, bold: true,
      color: INK, isTextBox: true, margin: 0, objectName: "gt" + i });
    s.addText(g.b, { x: x + 0.22, y: 4.72, w: 2.5, h: 0.72, fontSize: 10.5,
      color: MUT, isTextBox: true, margin: 0, lineSpacing: 12.5, objectName: "gd" + i });
  });

  s.addText([
    { text: "Two outcomes, because one of them inverts.  ", options: { bold: true, color: INK } },
    { text: "O1 is probability mass on the guideline-correct option. "
      + "O2 is mass on the target diagnosis. Concordance flips sign with how the "
      + "question is posed; endorsement does not, so the linkage hypothesis is "
      + "pre-registered on O2.", options: { color: MUT } },
  ], { x: 0.55, y: 5.66, w: 12.2, h: 0.62, fontSize: 11.5, isTextBox: true,
       margin: 0, lineSpacing: 14, objectName: "oc" });

  s.addText(`${VG.nLive} live vignettes of ${VG.nTotal} authored  ·  `
    + `${LV.livePrompts.toLocaleString("en-US")} analysis-ready prompts  ·  `
    + `${VG.nRejected} rejected at review, ${VG.nRetired} superseded`,
    { x: 0.55, y: 6.42, w: 12.2, h: 0.3, fontSize: 11, color: TEAL,
      isTextBox: true, margin: 0, bold: true, objectName: "sc3" });
  note(s, "This is the slide that earns the right to call anything bias. The "
   + "invariance rule is: a gender difference counts as bias only where the "
   + "clinically correct answer is identical across patients, and that is "
   + "established from a quoted guideline, not asserted. Group 2 is what makes "
   + "it testable in both directions: it contains the cases where the answer "
   + "SHOULD differ, so a model that never moves fails it. Mention that both "
   + "sex parameter values are run against every identity label, which is what "
   + "lets us tell an SPCU effect from an identity effect rather than confusing "
   + "the two.");
}

// ------------------------------ 4. the apparatus and measurement biases ----
{
  const s = S("CONTENT", "2 The instrument",
    "The harness can manufacture bias on its own");

  const items = [
    { k: "OPTION GEOMETRY", h: "A 4-option frame is not a 2-option frame",
      b: "Probability mass is split differently by the number and length of the "
       + "options, so a gap measured in one geometry is not comparable to a gap "
       + "measured in another. Every noise floor is now measured in the SAME "
       + "geometry as the item it is applied to.", c: TEAL },
    { k: "TOKEN LENGTH", h: "Longer options attract mass",
      b: "Option strings are length-matched within a set, so the model cannot "
       + "score an answer simply for being the wordiest one on offer.", c: BERRY },
    { k: "LEXICAL HABIT", h: "Models prefer “Yes” before they read anything",
      b: "Raw likelihood confounds the answer with the model's standing "
       + "preference for a token. Scoring is pointwise mutual information "
       + "against an unconditioned baseline, which divides that habit out.", c: WARN },
  ];
  items.forEach((it, i) => {
    const y = 1.3 + i * 1.46;
    card(s, { x: 0.55, y, w: 12.2, h: 1.32, fill: TINT, name: "ap" + i });
    s.addText(it.k, { x: 0.8, y: y + 0.16, w: 2.2, h: 0.24, fontSize: 9.5,
      bold: true, color: it.c, charSpacing: 1, isTextBox: true, margin: 0,
      objectName: "apk" + i });
    s.addText(it.h, { x: 0.8, y: y + 0.44, w: 4.5, h: 0.66, fontSize: 13.5,
      bold: true, color: INK, isTextBox: true, margin: 0, lineSpacing: 16,
      objectName: "aph" + i });
    s.addText(it.b, { x: 5.5, y: y + 0.18, w: 7.0, h: 1.0, fontSize: 11.5,
      color: MUT, isTextBox: true, margin: 0, lineSpacing: 14, valign: "middle",
      objectName: "apb" + i });
  });

  card(s, { x: 0.55, y: 5.72, w: 12.2, h: 1.14, fill: "FDF4E3", name: "prec",
    kicker: "AND ONE THAT IS NOT A CHOICE", kickerColor: WARN,
    head: "Float32 throughout, body and head", headH: 0.3, headSize: 13,
    body: "At half precision the differences being measured are the same order "
        + "as the arithmetic error, so a reduced-precision run measures rounding. "
        + "Non-negotiable, and it is why the full roster takes hours rather than "
        + "minutes." });
  note(s, "The point of this slide in an ethics defence is that we treated our "
   + "own instrument as a suspect. Each of these three would have produced a "
   + "number that looks exactly like bias and is not. The PMI one is the easiest "
   + "to explain: ask the model a yes-or-no clinical question and it has a "
   + "standing preference for yes before it has read the vignette, so any raw "
   + "comparison between two arms inherits that preference. Dividing by the "
   + "unconditioned baseline removes it.");
}

module.exports = {};
