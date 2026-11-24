// SHORT deck, slide 7: the resolution limit, the one remedy that worked, and
// the ethical conclusion.
//
// The ladder is the most important diagram in the deck after the matrix,
// because it is the slide that stops an examiner asking the question we cannot
// answer. An exact sign-flip test over k vignette clusters cannot return a
// p below 2^-k, no matter how large the effect is. So with k = 4, p = 0.0625
// is not a near miss: it is the floor of the test, and H1 landing exactly on
// it means unresolvable, NOT absent.
//
// NOTE the exponent. It is 2^-k, not 2^-(k-1): H3 at k = 8 has a resolution of
// 0.00390625 = 2^-8, and the accessor confirms it. An earlier draft of this
// deck's source material had the formula off by one.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const H1 = F.hypothesis("H1"), H2 = F.hypothesis("H2"), H3 = F.hypothesis("H3");
const MG = F.merging();
const GT = F.gateTable();
const VG = F.vignetteGroups();
const PARA = F.paraphrase();
const CT = F.contamination();
const GC = F.guidelineCoverage();

// Assert the exponent the diagram is built on, rather than trusting it. If a
// future k/p pair stops satisfying p_min = 2^-k, the formula on the slide is
// wrong and the build should stop instead of teaching it.
[["H1", H1], ["H2", H2], ["H3", H3]].forEach(([nm, h]) => {
  if (h.k == null) return;
  const want = Math.pow(2, -h.k);
  if (Math.abs(h.pResolution - want) > 1e-12) {
    throw new Error(`s7.js: ${nm} has k = ${h.k} and resolution `
      + `${h.pResolution}, but 2^-${h.k} is ${want}. The exponent printed on `
      + `the slide no longer matches the tables.`);
  }
});

// The gender-blinded arm, measured against the three gendered arms on O1
// (guideline concordance). Computed here from the delta table rather than
// quoted, because there is no accessor for it yet; a negative mean means the
// blinded arm scored HIGHER on giving the guideline-correct answer.
const blinded = (() => {
  const rows = F.table("rq2_deltas.csv").filter(r =>
    r.score_key === F.KEY && r.outcome === "o1" &&
    /_minus_blinded$/.test(r.contrast));
  if (!rows.length) throw new Error("s7.js: no *_minus_blinded o1 rows");
  const by = {};
  for (const r of rows) {
    (by[r.model_id] = by[r.model_id] || []).push(F.num(r.delta));
  }
  const out = Object.entries(by).map(([m, v]) =>
    ({ model: F.SHORT(m), mean: v.reduce((a, b) => a + b, 0) / v.length }));
  const pass = new Set(GT.filter(r => r.gate === "SENSITIVE").map(r => r.model));
  return {
    all: out,
    passers: out.filter(r => pass.has(r.model)).sort((a, b) => a.mean - b.mean),
    nBlindedHigher: out.filter(r => r.mean < 0).length,
    n: out.length,
  };
})();

pres.addSection({ title: "4 Limits" });
const s = S("CONTENT", "4 Limits", "Resolution limits, and the remedy that held");
K.mark("limits");

// ------------------------------------------------------------- the ladder ----
s.addText("THE HARD LIMIT: AN EXACT SIGN-FLIP TEST OVER k CLUSTERS CANNOT RETURN p < 2⁻ᵏ", {
  x: 0.55, y: 1.14, w: 6.6, h: 0.22, fontSize: 8.5, bold: true, color: INK,
  charSpacing: 0.5, isTextBox: true, margin: 0, objectName: "lk" });

const AX_Y = 2.72, AX_X = 0.95, AX_W = 5.4, STEP = AX_W / 7;
const kx = k => AX_X + (k - 1) * STEP;

s.addShape(pres.ShapeType.line, { x: AX_X, y: AX_Y, w: AX_W, h: 0,
  line: { color: "9BB3BA", width: 1.25 }, objectName: "axis" });

for (let k = 1; k <= 8; k++) {
  const x = kx(k);
  s.addShape(pres.ShapeType.line, { x, y: AX_Y, w: 0, h: 0.09,
    line: { color: "9BB3BA", width: 1 }, objectName: `tk${k}` });
  s.addText(`k=${k}`, { x: x - 0.26, y: AX_Y + 0.11, w: 0.52, h: 0.18,
    fontSize: 8, bold: true, color: MUT, align: "center", isTextBox: true,
    margin: 0, objectName: `kl${k}` });
  s.addText(Math.pow(2, -k) < 0.01 ? Math.pow(2, -k).toFixed(4)
                                   : Math.pow(2, -k).toFixed(4).replace(/0+$/, ""),
    { x: x - 0.33, y: AX_Y + 0.28, w: 0.66, h: 0.18, fontSize: 7,
      color: "9BB3BA", align: "center", isTextBox: true, margin: 0,
      objectName: `pl${k}` });
}
s.addText("smallest p the test can return  →", { x: AX_X, y: AX_Y + 0.5,
  w: AX_W, h: 0.18, fontSize: 7.5, color: "9BB3BA", italic: true, align: "center",
  isTextBox: true, margin: 0, objectName: "axl" });

// alpha = .05 falls between k = 4 (0.0625) and k = 5 (0.03125). Everything to
// the left of this line is a test that CANNOT reach significance at .05.
const AX_A = kx(4) + STEP * 0.5;
s.addShape(pres.ShapeType.line, { x: AX_A, y: 1.46, w: 0, h: AX_Y - 1.46 + 0.1,
  line: { color: FAIL, width: 1.25, dashType: "dash" }, objectName: "alpha" });
s.addText("α = .05", { x: AX_A - 0.42, y: 1.26, w: 0.84, h: 0.18, fontSize: 8,
  bold: true, color: FAIL, align: "center", isTextBox: true, margin: 0,
  objectName: "alpha-l" });
s.addText("cannot reach .05\nat any effect size", { x: AX_X - 0.1, y: 1.46, w: 1.9,
  h: 0.34, fontSize: 7.5, color: FAIL, italic: true, lineSpacing: 9,
  isTextBox: true, margin: 0, objectName: "alpha-lft" });
s.addText("significance\nreachable", { x: AX_A + 0.12, y: 1.46, w: 1.3, h: 0.34,
  fontSize: 7.5, color: PASS, italic: true, lineSpacing: 9, isTextBox: true,
  margin: 0, objectName: "alpha-rgt" });

// Our tests, pinned to their own k.
const PINS = [
  [H2.k, "H2", `one cluster · p can never fall below ${H2.pResolution}`, MUT, 0],
  [MG[0].nVignettes, "Group 2 + merging", `${MG[0].nVignettes} clusters · limit ${MG[0].pResolution}`, TEAL, 1],
  [H1.k, "H1", `p = ${H1.txt.pExact}, exactly its own limit`, WARN, 2],
  [VG.groups["3"].length, "Group 3", `${VG.groups["3"].length} clusters · first design that can reach .05`, PASS, 3],
  [H3.k, "H3", `equivalence supported, margin ${H3.txt.margin}`, PASS, 0],
];
PINS.forEach(([k, label, sub, col, lane]) => {
  const x = kx(k), y = 2.0 + lane * 0.0;
  s.addShape(pres.ShapeType.line, { x, y: AX_Y - 0.34, w: 0, h: 0.34,
    line: { color: col, width: 1.5 }, objectName: `pin-${label}` });
  s.addShape(pres.ShapeType.ellipse, { x: x - 0.055, y: AX_Y - 0.055, w: 0.11, h: 0.11,
    fill: { color: col }, line: { color: col, width: 0 }, objectName: `dot-${label}` });
});
// Labels in their own stack, so pins at adjacent k cannot overprint.
const LY = 3.46;
PINS.forEach(([k, label, sub, col], i) => {
  const y = LY + i * 0.3;
  s.addShape(pres.ShapeType.ellipse, { x: 0.62, y: y + 0.045, w: 0.12, h: 0.12,
    fill: { color: col }, line: { color: col, width: 0 }, objectName: `lg-${i}` });
  s.addText([
    { text: `${label}  `, options: { bold: true, color: INK } },
    { text: `k = ${k}  ·  ${sub}`, options: { color: MUT } },
  ], { x: 0.84, y, w: 6.3, h: 0.24, fontSize: 9, isTextBox: true, margin: 0,
       valign: "middle", objectName: `lgt-${i}` });
});

s.addText([
  { text: "So H1 is unresolvable, not absent. ", options: { bold: true, color: WARN } },
  { text: `Its gap is ${H1.txt.delta} with a confidence interval of ${H1.txt.ci} that excludes zero, and its exact p is ${H1.txt.pExact} — the smallest number four clusters can produce. One more referral vignette takes k to 5 and the limit to 0.031.`,
    options: { color: MUT } },
], { x: 0.55, y: 5.06, w: 6.6, h: 0.5, fontSize: 9.5, lineSpacing: 12,
     isTextBox: true, margin: 0, objectName: "h1note" });

// -------------------------------------------------------- right-hand column ----
const PX = 7.38, PW = 5.4;

card(s, { x: PX, y: 1.38, w: PW, h: 1.86, fill: "E6F6F2", name: "rem",
  kicker: "THE ONE REMEDY WE CAN EVIDENCE", kickerColor: PASS,
  head: "Withholding the identity label restores concordance", headH: 0.3, headSize: 12,
  bodySize: 9,
  body: `In all ${blinded.passers.length} models that pass the positive control, the `
      + `gender-blinded arm scores highest on guideline-correct advice `
      + `(gendered minus blinded, so below zero favours blinding): `
      + blinded.passers.map(r => `${r.model} ${F.f4(r.mean)}`).join(", ")
      + `. In the ${blinded.n - blinded.passers.length} that fail it the direction is `
      + `mixed and every difference sits inside the floor — blinding a model that `
      + `was never reading the field changes nothing ` + A.m("equitriage2026") + "." });

card(s, { x: PX, y: 3.34, w: PW, h: 2.24, fill: TINT, name: "lim",
  kicker: "WHAT WE ARE NOT CLAIMING", kickerColor: MUT,
  head: "Three limits, stated before anyone asks", headH: 0.3, headSize: 12,
  bodySize: 9,
  body: `Tier 1 only: author-reviewed against a quoted guideline, with `
      + `${GC.verified} of ${GC.total} carrying a citation of record. Clinician `
      + `sign-off is scheduled and the paper waits for it.\n`
      + `Low power by construction, as the ladder shows.\n`
      + `No causal attribution to either corpus.\n\n`
      + `What does hold: ${(PARA.pctUnanimous * 100).toFixed(1)}% of floor-clearing `
      + `effects keep direction across all three paraphrases, and `
      + `${CT.targetLongPresent} of ${CT.nTargetLong} long target spans appear in `
      + `either corpus ` + A.m("liu2024", "elazar2024") + "." });

// ------------------------------------------------------------- conclusion ----
s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.72, w: 12.23, h: 0.74, rectRadius: 0.06,
  fill: { color: INK }, line: { color: INK, width: 0 }, objectName: "concl-bg" });
s.addText([
  { text: "An LLM with no treatment gap may be clinically blind rather than equitable, and only a positive control tells the two apart.  ",
    options: { bold: true, color: PAPER } },
  { text: "Opening the training pipeline is what let us name the mechanism — identity read as sex parameter — instead of only scoring the symptom.",
    options: { color: "AFCBD1" } },
], { x: 0.78, y: 5.8, w: 11.77, h: 0.58, fontSize: 11.5, lineSpacing: 15,
     valign: "middle", isTextBox: true, margin: 0, objectName: "concl" });

tierBanner(s, { x: 0.55, y: 6.56, w: 12.23, h: 0.38, fs: 8, name: "tier" });

// 45 seconds, about 101 words. Close cleanly; do not add to the dark band.
note(s, `[45s] The ladder pre-empts the hardest question. Our tests are exact sign-flip tests over vignette clusters, and such a test cannot return a p below two to the minus k. With four clusters the smallest possible p is 0.0625. H1 came in at exactly 0.0625, with an interval that excludes zero. Say it in these words: unresolvable, not absent.

Then the remedy, because a critique with no finding is weak. In every model that can read the clinical field, withholding the identity label gave the most guideline-concordant advice.

Close on the band and stop. A model with no treatment gap may be blind rather than fair. Thank you.`);
