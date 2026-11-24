// BACKUP 4: the robustness checks and the state of the RQ6 datasheet audit.
// The honest "what is not finished" slide.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("../short/acm.js");

const PARA = F.paraphrase();
const CT = F.contamination();
const R6 = F.rq6Status();
const GC = F.guidelineCoverage();
const GR = F.gateRerun();

const s = S("CONTENT", "5 Backup", "Backup: robustness, and what is not finished");
K.mark("bk-rob");

const B = [
  ["PARAPHRASE STABILITY", TEAL,
   `${(PARA.pctUnanimous * 100).toFixed(1)}% hold across all three wordings`,
   `Each vignette is written three ways. Of ${PARA.nCells.toLocaleString("en-US")} cells, `
   + `${PARA.nClears.toLocaleString("en-US")} clear their floor, and `
   + `${PARA.nUnanimous.toLocaleString("en-US")} of those keep the same direction in all `
   + `three paraphrases. The ${PARA.nNotUnanimous} that do not are reported as `
   + `unstable rather than averaged into agreement.`],
  ["CONTAMINATION", TEAL,
   `${CT.targetLongPresent} of ${CT.nTargetLong} long target spans found in either corpus`,
   `If a guideline sentence were memorised verbatim, a model could answer from `
   + `recall rather than reasoning. We probed ${CT.nSpans} spans against the `
   + `corpora. None of the ${CT.nTargetLong} long target spans appears, while `
   + `${CT.ctrlPresent} of ${CT.nCtrl} positive controls do, which is what shows `
   + `the probe works ` + A.m("liu2024") + `.`],
  // Disclosed against our own interest: this is the change that MADE the
  // headline result, and it was a change we made ourselves.
  ["THE CORRECTION THAT HELPED US", WARN,
   `The gate went from ${GR.oldPasses} of ${GR.n} to ${GR.newPasses} of ${GR.n}`,
   `Our first floor was not matched on option count and was roughly `
   + `${F.floorComparison().timesTooHigh.toFixed(1)} times too high, which `
   + `suppressed almost every effect. Correcting it moved all `
   + `${F.floorComparison().nMoved} models and turned a one-model result into a `
   + `three-model one. A null that becomes a finding after an instrument change `
   + `the authors made is exactly the shape a reader should distrust, so the `
   + `criterion was fixed before the run, both columns are published, and RQ3 `
   + `stays outside the confirmatory family.`],
];
B.forEach(([k, col, head, body], i) => {
  const x = 0.55 + i * 4.11;
  card(s, { x, y: 1.2, w: 4.0, h: 2.5, fill: TINT, name: `b${i}`,
    kicker: k, kickerColor: col, head, headH: 0.52, headSize: 11.5,
    bodySize: 9.5, body });
});

card(s, { x: 0.55, y: 3.86, w: 6.06, h: 2.44, fill: "FDF4E3", name: "rq6",
  kicker: "RQ6  ·  NOT YET CODED", kickerColor: WARN,
  head: "The datasheet audit is built but not scored", headH: 0.3, headSize: 13,
  bodySize: 9.5,
  body: `The dossier covers ${R6.nDocs} model cards and dataset sheets against `
      + `${R6.nTerms} gender-health search terms. ${R6.zeroDocs.length} of the `
      + `${R6.nDocs} documents mention none of them at all: `
      + R6.zeroDocs.join(", ") + `.\n\n`
      + `What is NOT done: the two independent human coding passes. Both coder `
      + `columns are deliberately empty, and no agreement statistic is claimed, `
      + `because a single-coder reading of a disclosure document is an opinion `
      + `and not a measurement. Until that is finished, RQ6 is reported as `
      + `search counts and nothing more ` + A.m("gebru2021", "biderman2022") + `.` });

card(s, { x: 6.72, y: 3.86, w: 6.06, h: 2.44, fill: "FBEEEC", name: "tier",
  kicker: "WHY THIS IS TIER 1 AND NOT TIER 2", kickerColor: FAIL,
  head: "No clinician has signed off a single vignette", headH: 0.3, headSize: 13,
  bodySize: 9.5,
  body: `Tier 1 means every vignette was reviewed by the authors against a `
      + `quoted, first-hand guideline passage. That is the bar we fixed for this `
      + `submission, and it is not the bar for publication.\n\n`
      + `Of ${GC.total} vignette-guideline pairs, ${GC.verified} carry a verified `
      + `citation of record, ${GC.identifierOnly} are identified but not yet read `
      + `at first hand, and ${GC.pending} are pending. Clinical review is `
      + `scheduled. The public paper waits for it, and the tier label is derived `
      + `from the rows rather than declared, so it cannot be upgraded by `
      + `editing a slide.` });

note(s, "Backup. Turn here for “how do you know it is not memorised”, “does it hold under a different scoring key” (it narrows, say so), or “what is the status of RQ6”.");
