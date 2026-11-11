// Talk deck, beats 10 to 12: the ethics argument, the honest limits, and what
// is left behind.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, stat, box, note, badge, arrow,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const PC = F.positiveControl();
const MG = F.merging();
const H1 = F.hypothesis("H1"), H3 = F.hypothesis("H3");
const R4C = F.rq4Control();
const R4T = F.rq4Trend();
const VG = F.vignetteGroups();
const LV = F.liveVignettes();
const CA = F.corpusAgreement();
const ND = F.decisionCount();
const PA = F.paraphrase();

const nIns = PC.filter(r => r.gate !== "SENSITIVE").length;
const merge = MG.filter(m => m.above).map(m => m.model).sort();
const pass = PC.filter(r => r.gate === "SENSITIVE").map(r => r.model).sort();

pres.addSection({ title: "6 Ethics" });

// -------------------------------------------- 10. the ethics argument -----
{
  const s = S("CONTENT_DARK", "6 Ethics",
    "What this means for how fairness gets reported");

  card(s, { x: 0.55, y: 1.3, w: 5.97, h: 2.6, fill: "14454F", name: "e1",
    kicker: "1  FALSE EQUITY", kickerColor: FAIL,
    head: `“No bias detected” is true of ${nIns} of ${PC.length} models here, and it is misleading in every one`,
    headH: 0.86, headSize: 15, headColor: PAPER,
    body: `Those ${nIns} models cannot distinguish clinical sex where the `
        + `guideline says they must. Their flat response to gender is not `
        + `fairness, it is blindness, and reporting it as fairness would convert `
        + `an incapacity into a safety claim.\n\n`
        + `A fairness audit without a positive control cannot tell the two apart. `
        + `This is a reporting-standard problem, not a model problem.`,
    bodyColor: "B9D2D7", bodySize: 11.5 });

  card(s, { x: 6.81, y: 1.3, w: 5.97, h: 2.6, fill: "14454F", name: "e2",
    kicker: "2  CAPABILITY AND HARM ARRIVE TOGETHER", kickerColor: WARN,
    head: "The models good enough to use clinically are the ones that misread identity as physiology",
    headH: 0.86, headSize: 15, headColor: PAPER,
    body: `The ${pass.length} models that pass the control are `
        + `${pass.join(", ")}. The ${merge.length} that merge gender identity `
        + `into the sex parameter are ${merge.join(", ")}.\n\n`
        + `It is the same set. So this is not a defect that capability will `
        + `outgrow, and for a trans or non-binary patient it is the worst `
        + `combination: confident, and wrong in a direction that reroutes care.`,
    bodyColor: "B9D2D7", bodySize: 11.5 });

  card(s, { x: 0.55, y: 4.1, w: 5.97, h: 2.52, fill: "14454F", name: "e3",
    kicker: "3  OPENNESS IS NECESSARY, NOT SUFFICIENT", kickerColor: TEAL,
    head: "Open data made the question askable. It did not make it answerable.",
    headH: 0.58, headSize: 15, headColor: PAPER,
    body: `No closed-model study can attempt RQ1 or RQ4 at all, so openness is `
        + `the precondition. But on the audited health concepts the two open `
        + `corpora agree at ρ = ${CA.rho.toFixed(3)}, and the pre-registered `
        + `provenance control holds in only ${R4C.wins} of ${R4C.n} models. `
        + `Auditability requires corpora that are open AND that actually differ.`,
    bodyColor: "B9D2D7", bodySize: 11.5 });

  card(s, { x: 6.81, y: 4.1, w: 5.97, h: 2.52, fill: "14454F", name: "e4",
    kicker: "4  THE DOCUMENTATION GAP IS AN INTERSECTION GAP", kickerColor: BERRY,
    head: "Both halves were disclosed. The joint risk was not.", headH: 0.58,
    headSize: 15, headColor: PAPER,
    body: `The Pile paper measures gender in the corpus. It also says the medical `
        + `content was included to benefit downstream medical applications. No `
        + `document in the set puts the two in one claim.\n\n`
        + `Datasheets ask about composition and about intended use as separate `
        + `questions, so a conscientious author can answer both and still never `
        + `state the risk this study measured.`,
    bodyColor: "B9D2D7", bodySize: 11.5 });
  note(s, "This is the ethics core, so slow down and do not read the cards out. "
   + "Pick the second one and dwell on it, because it is the counterintuitive "
   + "result and it is the one a marker will remember: the set of models that "
   + "pass our clinical-sensitivity control and the set that confuse identity "
   + "with physiology are the SAME SET. The optimistic reading, that this is a "
   + "small-model artefact that scale will fix, is contradicted by our own data. "
   + "On the third card, concede openly that our own design is limited by the "
   + "corpora we chose, and that we found it with a control we committed to in "
   + "advance rather than discovering it in review.");
}

// ------------------------------------ 11. limitations and contributions ---
pres.addSection({ title: "7 Close" });
{
  const s = S("CONTENT", "7 Close", "What this cannot support, and what it leaves behind");

  s.addText("Limitations, stated before anyone asks", { x: 0.55, y: 1.24, w: 6.0,
    h: 0.3, fontSize: 14, bold: true, color: FAIL, isTextBox: true, margin: 0,
    objectName: "lh" });
  const lims = [
    [`Tier 1, not tier 2`, `Every vignette is author-reviewed against a quoted `
      + `first-hand guideline. Clinician verification is scheduled and the paper `
      + `waits for it. Every number here carries that condition.`],
    [`Resolution, not null`, `H1 runs on k = ${H1.k} vignettes, so the finest `
      + `one-sided p that exists is ${H1.pResolution.toFixed(4)}. A perfect sign `
      + `flip cannot reach .05. The fix is more vignettes, not more models.`],
    [`${PA.nNotUnanimous} of our own effects disqualified`, `Of the effects that `
      + `clear their floor, ${(100 - PA.pctUnanimous * 100).toFixed(1)}% change `
      + `sign under at least one paraphrase and are not reported as robust.`],
    [`RQ6 coding incomplete`, `The term sweep is done; the graded coding needs `
      + `two independent human passes and κ ≥ 0.70 before any code is citable.`],
    [`Ten documents, three projects`, `A case study. It cannot speak to dataset `
      + `documentation practice in general, and its force comes from being paired `
      + `with the corpus and model measurements, not from breadth.`],
  ];
  lims.forEach((l, i) => {
    const y = 1.6 + i * 1.0;
    s.addText(l[0], { x: 0.55, y, w: 2.2, h: 0.86, fontSize: 11.5, bold: true,
      color: INK, isTextBox: true, margin: 0, lineSpacing: 13, valign: "top",
      objectName: "lt" + i });
    s.addText(l[1], { x: 2.82, y, w: 3.73, h: 0.86, fontSize: 10.5, color: MUT,
      isTextBox: true, margin: 0, lineSpacing: 12.5, valign: "top",
      objectName: "lb" + i });
  });

  s.addText("Contributions", { x: 6.9, y: 1.24, w: 5.88, h: 0.3, fontSize: 14,
    bold: true, color: PASS, isTextBox: true, margin: 0, objectName: "ch" });
  const cons = [
    [`The pipeline`, `Corpus, model and datasheet measured in one study on two `
      + `fully open families. ${LV.livePrompts.toLocaleString("en-US")} prompts, `
      + `10 models, ${ND} dated decisions, every figure read from its table at build time.`],
    [`SPCU held fixed, identity varied`, `With a sex-specific positive control, `
      + `which is what makes the invariance rule testable in both directions. No `
      + `clinical LLM audit we found separates the two this way.`],
    [`The matched nuisance floor`, `Measured per model and per option geometry. `
      + `Re-measuring it in the right frame changed the gate verdict for two models.`],
    [`Identity/SPCU merging`, `An empirical finding: the ${merge.length} most `
      + `capable models treat a stated gender identity as a clinical sex parameter, `
      + `at 6 to 22 times their own floors.`],
    [`Linkage is post-training`, `+${R4T.postTrainingDelta.toFixed(3)} from `
      + `alignment alone, flat across a hundredfold of pretraining scale; and a `
      + `preregistered provenance control that fails, which is a design requirement `
      + `for the next study.`],
  ];
  cons.forEach((c, i) => {
    const y = 1.6 + i * 1.0;
    s.addText(c[0], { x: 6.9, y, w: 2.2, h: 0.86, fontSize: 11.5, bold: true,
      color: INK, isTextBox: true, margin: 0, lineSpacing: 13, valign: "top",
      objectName: "ct" + i });
    s.addText(c[1], { x: 9.17, y, w: 3.61, h: 0.86, fontSize: 10.5, color: MUT,
      isTextBox: true, margin: 0, lineSpacing: 12.5, valign: "top",
      objectName: "cb" + i });
  });
  s.addShape(pres.ShapeType.line, { x: 6.72, y: 1.28, w: 0, h: 5.3,
    line: { color: "D7E4E7", width: 1 }, objectName: "div" });
  note(s, "Say the limitations yourself, in your own words, before the questions. "
   + "The strongest of them is the resolution limit, because it is a limit we "
   + "proved rather than suspected: with four vignettes no p below 0.0625 exists, "
   + "so H1 could not have been significant however large the effect. Volunteering "
   + "that is worth more than any result on the previous slides. Same for the 267 "
   + "effects we disqualified on our own paraphrase check.");
}

// -------------------------------------------------- 12. future work -------
{
  const next = [
    [`1`, `A fifth referral vignette`, `Takes H1 from k = ${H1.k} to k = 5 and its `
      + `resolution limit from ${H1.pResolution.toFixed(4)} to 0.031, which makes `
      + `the hypothesis testable at all. Cheapest change with the largest effect.`, PASS],
    [`2`, `Corpora that actually differ`, `The provenance control fails because `
      + `the two corpora agree at ρ = ${CA.rho.toFixed(3)} on these concepts. `
      + `Selecting concepts on corpus DISAGREEMENT, not on clinical interest, is `
      + `the fix, and it has to happen before scoring.`, WARN],
    [`3`, `Tier 2, and report what it changes`, `Clinician verification on every `
      + `row. If it overturns a direction or a gate verdict, the tier 1 bar was `
      + `too weak and we have said so in advance.`, TEAL],
    [`4`, `Checkpoint tracing, and a causal method`, `Pythia publishes 154 `
      + `checkpoints per model, so the step at which merging appears is `
      + `observable. Causal mediation would move RQ4 from association to mechanism.`, BERRY],
  ];
  const s = S("CONTENT", "7 Close", "What we would do next");
  next.forEach((n, i) => {
    const y = 1.3 + i * 1.34;
    card(s, { x: 0.55, y, w: 12.2, h: 1.2, fill: TINT, name: "fw" + i });
    badge(s, { x: 0.78, y: y + 0.36, n: n[0], d: 0.46, fs: 15, color: n[3],
      name: "fwb" + i });
    s.addText(n[1], { x: 1.42, y: y + 0.16, w: 3.6, h: 0.86, fontSize: 14,
      bold: true, color: INK, isTextBox: true, margin: 0, lineSpacing: 16,
      valign: "middle", objectName: "fwt" + i });
    s.addText(n[2], { x: 5.1, y: y + 0.16, w: 7.4, h: 0.88, fontSize: 11.5,
      color: MUT, isTextBox: true, margin: 0, lineSpacing: 14, valign: "middle",
      objectName: "fwd" + i });
  });
  s.addText("Repository, decision log and the full 56-slide reference deck are "
    + "available; every figure in this talk is read from its results table at "
    + "build time rather than typed.",
    { x: 0.55, y: 6.7, w: 12.2, h: 0.3, fontSize: 10.5, color: MUT, italic: true,
      isTextBox: true, margin: 0, objectName: "repo" });
  note(s, "Close on item 1. It is concrete, it is cheap, and it shows we know "
   + "which single number is binding on the headline hypothesis.");
}

module.exports = {};
