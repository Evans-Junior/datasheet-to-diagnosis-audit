// BACKUP 3: RQ4, the linkage question and why it returns a limit rather than
// a mechanism. This is the slide for "so did the data cause it?"
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const CTRL = F.rq4Control().rows;
const CA = F.corpusAgreement();
const CD = F.corpusDisagreement();
// Name both indexes explicitly. The default pair is olmo-mix against the
// PILE (rho 0.936, n 15); this card is about olmo-mix against DCLM, which is
// a different and much tighter pair, and the two were conflated once.
const CRD = F.corpusReplication("v4_olmo-mix-1124_llama", "v4_dclm-baseline_llama");
const CQ = F.corpusQueries();
const wins = CTRL.filter(r => r.matchedWins).length;

const s = S("CONTENT", "5 Backup", "Backup: why RQ4 returns a limit, not a mechanism");
K.mark("bk-rq4");

s.addText("Does a model's gap track the corpus it was trained on? The control: does the MATCHED corpus predict better than one it never saw?", {
  x: 0.55, y: 1.12, w: 12.2, h: 0.3, fontSize: 11.5, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

// The control table: matched vs best crossed, per model.
s.addText("MATCHED CORPUS vs BEST CROSSED CORPUS, SPEARMAN RHO OVER 8 COMMON-SUPPORT CONCEPTS", {
  x: 0.55, y: 1.52, w: 7.6, h: 0.2, fontSize: 8, bold: true, color: MUT,
  charSpacing: 0.6, isTextBox: true, margin: 0, objectName: "kt" });
[["model", 0.62, 2.5], ["own corpus", 3.16, 1.5], ["matched", 4.72, 1.0],
 ["best crossed", 5.78, 1.2], ["matched wins?", 7.02, 1.1]]
  .forEach(([t, x, w]) => s.addText(t, { x, y: 1.74, w, h: 0.2, fontSize: 8,
    bold: true, color: MUT, isTextBox: true, margin: 0, objectName: "th-" + t }));

CTRL.forEach((r, i) => {
  const y = 1.96 + i * 0.37;
  s.addShape(pres.ShapeType.rect, { x: 0.55, y, w: 7.6, h: 0.35,
    fill: { color: i % 2 ? PAPER : TINT }, line: { color: PAPER, width: 0 },
    objectName: `r4r${i}` });
  const tx = (x, w, t, col, bold, mono) => s.addText(t, { x, y, w, h: 0.35,
    fontSize: 9, bold: !!bold, color: col || INK, valign: "middle",
    isTextBox: true, margin: 0, ...(mono ? { fontFace: "Courier New" } : {}),
    objectName: `r4c${i}-${x}` });
  tx(0.62, 2.5, F.SHORT(r.model), INK, true);
  tx(3.16, 1.5, r.ownCorpus, MUT);
  tx(4.72, 1.0, F.f3(r.matched), INK, false, true);
  tx(5.78, 1.2, F.f3(r.crossedMax), MUT, false, true);
  tx(7.02, 1.1, r.matchedWins ? "yes" : "no",
     r.matchedWins ? PASS : FAIL, true);
});

card(s, { x: 8.3, y: 1.52, w: 4.48, h: 2.16, fill: "FBEEEC", name: "verdict",
  kicker: "THE CONTROL FAILS", kickerColor: FAIL,
  head: `Matched beats crossed in only ${wins} of ${CTRL.length}`, headH: 0.3, headSize: 13,
  bodySize: 9.5,
  body: `If corpus skew drove the output gap, a model's own corpus should `
      + `predict its behaviour better than a corpus it was never trained on. `
      + `It does not. We report that as a failed control rather than burying `
      + `it, because it is the result that constrains our own thesis hardest.` });

card(s, { x: 8.3, y: 3.8, w: 4.48, h: 2.76, fill: TINT, name: "why",
  kicker: "WHY, AND WHAT IT MEANS", kickerColor: TEAL,
  head: "The corpora are too alike to tell apart", headH: 0.3, headSize: 13,
  bodySize: 9,
  body: `The Pile and olmo-mix-1124 agree at rho ${CA.rho.toFixed(3)} over `
      + `${CA.n} common-support concepts. olmo-mix against DCLM-baseline is `
      + `tighter still: rho ${CRD.rho.toFixed(3)} over ${CRD.n} concepts, with a `
      + `maximum difference of ${CRD.maxDiff.toFixed(3)}. Web-scale corpora are `
      + `drawn from overlapping crawls, so an n-gram count cannot attribute an `
      + `effect to one of them rather than another.\n\n`
      + `So the honest finding is NON-IDENTIFIABILITY: at this granularity, `
      + `provenance cannot be assigned, and anyone claiming a causal link from `
      + `n-gram frequency alone is overreading ` + A.m("elazar2024", "feng2023") + `.\n`
      + `Median disagreement ${CD.medianDisagreement.toFixed(3)}, max `
      + `${CD.maxDisagreement.toFixed(3)}, and ${CD.nAboveHalfLog2} concepts `
      + `differ by more than half a log2 unit.` });

s.addText(`All counts are exact n-gram lookups over ${CQ.nIndexes} infini-gram indexes: ${CQ.cached.toLocaleString("en-US")} cached queries, ${CQ.failed} failures. Nothing is sampled or estimated.`, {
  x: 0.55, y: 5.9, w: 7.6, h: 0.4, fontSize: 9.5, color: MUT, italic: true,
  isTextBox: true, margin: 0, objectName: "cq" });

note(s, "Backup. Turn here for “did the training data cause it”. The answer is that the control fails and we say so: matched beats crossed in only " + wins + " of " + CTRL.length + ", and the two corpora correlate at " + CA.rho.toFixed(3) + ", so provenance is not identifiable at n-gram granularity.");
