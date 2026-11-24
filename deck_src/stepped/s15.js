// SPOKEN 15 of 16: the remedy that held, and the three limits. [20s]
//
// A critique with no actionable finding is weak, so the remedy gets its own
// slide beside the limits rather than being a card on the conclusion slide.
//
// The blinded figures are computed here from rq2_deltas.csv because no
// accessor produces them yet. A negative mean means the BLINDED arm scored
// HIGHER on giving the guideline-correct answer.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const GT = F.gateTable();
const GC = F.guidelineCoverage();
const PARA = F.paraphrase();
const CT = F.contamination();

const blinded = (() => {
  const rows = F.table("rq2_deltas.csv").filter(r =>
    r.score_key === F.KEY && r.outcome === "o1" && /_minus_blinded$/.test(r.contrast));
  if (!rows.length) throw new Error("s15.js: no *_minus_blinded o1 rows");
  const by = {};
  for (const r of rows) (by[r.model_id] = by[r.model_id] || []).push(F.num(r.delta));
  const out = Object.entries(by).map(([m, v]) =>
    ({ model: F.SHORT(m), mean: v.reduce((a, b) => a + b, 0) / v.length }));
  const pass = new Set(GT.filter(r => r.gate === "SENSITIVE").map(r => r.model));
  return { passers: out.filter(r => pass.has(r.model)).sort((a, b) => a.mean - b.mean),
           n: out.length };
})();

const s = S("CONTENT", "4 Limits", "One remedy held. Three limits stand.");
K.mark("remedy");

card(s, { x: 0.55, y: 1.3, w: 6.06, h: 3.02, fill: "E6F6F2", name: "rem",
  kicker: "THE ONE REMEDY WE CAN EVIDENCE", kickerColor: PASS,
  head: "Withholding the identity label restores concordance", headH: 0.56,
  headSize: 14, bodySize: 10,
  body: `In all ${blinded.passers.length} models that pass the positive control, the `
      + `gender-blinded arm scores highest on guideline-correct advice `
      + `(gendered minus blinded, so below zero favours blinding):\n`
      + blinded.passers.map(r => `   ${r.model}  ${F.f4(r.mean)}`).join("\n")
      + `\n\nIn the ${blinded.n - blinded.passers.length} that fail the gate the `
      + `direction is mixed and every difference sits inside the floor — `
      + `blinding a model that was never reading the field changes nothing `
      + A.m("equitriage2026") + "." });

card(s, { x: 6.72, y: 1.3, w: 6.06, h: 3.02, fill: TINT, name: "lim",
  kicker: "WHAT WE ARE NOT CLAIMING", kickerColor: MUT,
  head: "Three limits, stated before anyone asks", headH: 0.56, headSize: 14,
  bodySize: 10,
  body: `1  Tier 1 only: author-reviewed against a quoted guideline, with `
      + `${GC.verified} of ${GC.total} carrying a citation of record. No clinician `
      + `has signed off a single vignette. Review is scheduled and the paper waits.\n\n`
      + `2  Low power by construction, as the ladder shows.\n\n`
      + `3  No causal attribution to either corpus: RQ4 returns a `
      + `non-identifiability limit, not a mechanism.` });

s.addText("WHAT DOES HOLD", { x: 0.55, y: 4.5, w: 12.2, h: 0.22, fontSize: 9.5,
  bold: true, color: TEAL, charSpacing: 1, isTextBox: true, margin: 0,
  objectName: "hk" });
[[`${(PARA.pctUnanimous * 100).toFixed(1)}%`, `of floor-clearing effects keep direction across all three paraphrases, over ${PARA.nCells.toLocaleString("en-US")} cells`, TEAL],
 [`${CT.targetLongPresent} of ${CT.nTargetLong}`, `long target guideline spans appear in either corpus, while ${CT.ctrlPresent} of ${CT.nCtrl} positive controls do ${A.m("liu2024")}`, TEAL],
 [`${GC.verified} of ${GC.total}`, "vignette-guideline pairs carry a verified, first-hand citation of record", WARN]]
 .forEach(([n, t, col], i) => {
  const x = 0.55 + i * 4.11;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 4.76, w: 4.0, h: 1.18, rectRadius: 0.06,
    fill: { color: PAPER }, line: { color: col, width: 1.1 }, objectName: `h${i}-bg` });
  s.addText(n, { x: x + 0.2, y: 4.86, w: 3.6, h: 0.4, fontSize: 18, bold: true,
    color: col, fontFace: "Cambria", isTextBox: true, margin: 0, objectName: `h${i}-n` });
  s.addText(t, { x: x + 0.2, y: 5.26, w: 3.6, h: 0.6, fontSize: 9.5,
    color: MUT, lineSpacing: 11.5, valign: "top", isTextBox: true, margin: 0,
    objectName: `h${i}-t` });
});

K.tierBanner(s, { x: 0.55, y: 6.06, w: 12.23, h: 0.44, fs: 8.5, name: "tier" });

// 20 seconds, about 44 words.
note(s, `[20s] A critique with no actionable finding is weak, so here is ours.

In every model that can read the clinical field, withholding the identity label gave the most guideline-concordant advice. In the models that cannot, blinding changes nothing.

Three limits, stated before anyone asks.`);
