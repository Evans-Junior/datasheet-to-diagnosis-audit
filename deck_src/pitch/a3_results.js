// ACT 3, the four results. Messages 8 to 11, 110 seconds.
// Every number on these slides comes through figures.js from results/tables.
// Nothing here is typed.
const K = require("./kit.js");
const F = require("../figures.js");
const A = require("../short/acm.js");
const { pres, S, message, box, card, stat, arrow, tierBanner, ink, mut, on,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY, GH } = K;

const PC   = F.positiveControl();
const MG   = F.merging();
const PT   = F.postTraining();
const PL   = F.placeboRegate();
const NFAIL = PC.filter(r => r.gate !== "SENSITIVE").length;
const TOP   = MG.filter(m => m.above).sort((a, b) => b.timesFloor - a.timesFloor)[0];

// ------------------------------------------------- 8. result 1, the gate
message({
  section: "Results", title: "Result 1: most models cannot see a real difference",
  secs: 26,
  notes: `${NFAIL} of ${PC.length} models never move, even where the guideline `
    + "itself says the answer changes. Here is why that matters more than it "
    + "sounds. Those seven models show the SMALLEST gender gaps in the whole "
    + "study. An audit without this control would have ranked them the fairest "
    + "systems we tested and recommended them. They are not fair. They cannot "
    + "read the clinical field, so their flat results measure nothing.",
  draw: (s) => {
    stat(s, { x: 0.55, y: 1.35, w: 3.5, n: `${NFAIL} of ${PC.length}`, size: 54, nh: 1.0,
      color: FAIL, label: "FAIL THE POSITIVE CONTROL", name: "g1",
      sub: "Their answer shifts by less than their own\nmeasured noise floor." });
    card(s, { x: 4.6, y: 1.35, w: 8.15, h: 2.25, fill: "FBEEEC", name: "trap",
      kicker: "AND HERE IS THE TRAP", kickerColor: FAIL,
      head: "Those are also the models with the smallest gender gaps in the study",
      headSize: 17, headH: 0.72,
      body: "A fairness audit without a positive control would have ranked them "
          + "the fairest systems we tested, and recommended them. They are not "
          + "fair. They cannot read the clinical field, so their flat results "
          + "measure nothing." });
    s.addText("Only " + PC.filter(r => r.gate === "SENSITIVE").map(r => r.model).join(", ")
      + " move when the sex parameter flips.",
      { x: 0.55, y: 3.95, w: 12.2, h: 0.34, fontSize: 13.5, color: MUT,
        isTextBox: true, margin: 0, objectName: "pass" });
    s.addText("“No measured gap” is not evidence of fairness. It is "
      + "evidence of nothing until the control passes.",
      { x: 0.55, y: 4.38, w: 12.2, h: 0.4, fontSize: 18, bold: true, color: INK,
        fontFace: "Cambria", isTextBox: true, margin: 0, objectName: "pt2" });
    tierBanner(s, { x: 0.55, y: 5.0, w: 12.2, h: 0.5, name: "tb1" });
  },
});

// -------------------------- 9. result 2, identity read as sex, 2 clicks
message({
  section: "Results", title: "Result 2: the models read gender identity as clinical sex",
  secs: 28, steps: 2,
  notes: "Now take the three models that DO pass, hold the sex parameter fixed "
    + "and change only the identity label. The correct answer cannot change, so "
    + `any movement is unwarranted by construction. ${TOP.model} moves by `
    + `${TOP.timesFloor.toFixed(1)} times its own noise floor. That is the `
    + "configuration of a transgender patient: a trans man whose sex parameter "
    + "is female gets less weight on an indicated pregnancy test, a trans woman "
    + "more weight on a cervical screening she does not need. And the second "
    + "line is the one procurement should hear: on identical pretraining data, "
    + "instruction tuning more than tripled the effect. The aligned version was "
    + "worse.",
  draw: (s, st) => {
    s.addText("Sex parameter held fixed. Only the identity label changes, so the "
      + "correct answer cannot change.",
      { x: 0.55, y: 1.25, w: 12.2, h: 0.32, fontSize: 14, color: MUT,
        isTextBox: true, margin: 0, objectName: "lead" });
    MG.filter(m => m.above).sort((a, b) => b.timesFloor - a.timesFloor)
      .forEach((m, i) => {
        const x = 0.55 + i * 4.11;
        s.addShape(pres.ShapeType.roundRect, { x, y: 1.7, w: 4.0, h: 1.55,
          rectRadius: 0.07, fill: { color: i === 0 ? "FBEEEC" : TINT },
          line: { color: i === 0 ? FAIL : "CFE0E3", width: 1.3 },
          objectName: `m${i}-bg` });
        s.addText(m.timesFloor.toFixed(1) + "×", { x: x + 0.2, y: 1.84, w: 3.6,
          h: 0.72, fontSize: 40, bold: true, fontFace: "Cambria",
          color: i === 0 ? FAIL : TEAL, isTextBox: true, margin: 0,
          objectName: `m${i}-n` });
        s.addText("its own noise floor", { x: x + 0.2, y: 2.54, w: 3.6, h: 0.26,
          fontSize: 11, bold: true, color: INK, isTextBox: true, margin: 0,
          objectName: `m${i}-l` });
        s.addText(m.model, { x: x + 0.2, y: 2.82, w: 3.6, h: 0.28, fontSize: 12.5,
          color: MUT, isTextBox: true, margin: 0, objectName: `m${i}-m` });
      });
    s.addText("That configuration, identity and clinical sex disagreeing, is a "
      + "transgender patient " + A.m("mcclure2021", "dev2021") + ".",
      { x: 0.55, y: 3.4, w: 12.2, h: 0.34, fontSize: 15, bold: true, color: INK,
        isTextBox: true, margin: 0, objectName: "tg" });

    const L = st >= 2;
    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 3.92, w: 12.2, h: 1.18,
      rectRadius: 0.07, fill: { color: L ? "FDF4E3" : GH.fill },
      line: { color: L ? WARN : GH.line, width: 1.3 }, objectName: "pt-bg" });
    s.addText("INSTRUCTION TUNING MADE IT WORSE", { x: 0.8, y: 4.06, w: 11.7, h: 0.26,
      fontSize: 10.5, bold: true, color: L ? WARN : GH.mut, charSpacing: 1.1,
      isTextBox: true, margin: 0, objectName: "pt-k" });
    s.addText(`On identical pretraining data the effect went from `
      + `${PT.mergingBase.toFixed(3)} to ${PT.mergingTuned.toFixed(3)}, more than `
      + `tripling, an increase ${PT.timesFloor.toFixed(0)} times the two models' `
      + `combined floor. Procurement is often reassured that a deployment uses `
      + `“the aligned version”.`,
      { x: 0.8, y: 4.32, w: 11.7, h: 0.66, fontSize: 13.5,
        color: L ? INK : GH.ink, lineSpacing: 17, isTextBox: true, margin: 0,
        objectName: "pt-b" });
    tierBanner(s, { x: 0.55, y: 5.26, w: 12.2, h: 0.5, name: "tb2" });
  },
});

// ------------------------------ 10. result 3, the placebo floor, 2 clicks
message({
  section: "Results", title: "Result 3: and then we tried to break our own finding",
  secs: 26, steps: 2,
  notes: "This is the result I am least comfortable with and the one I most "
    + "want to report. We asked whether those effects beat a clinically "
    + "MEANINGLESS edit to the very same vignette. Changing the patient's eye "
    + "colour moves these models further than changing the sex parameter does. "
    + `Requiring both floors takes the interpretable set from ${PL.passGenderFloor} `
    + `of ${PL.n} to ${PL.passBothFloors} of ${PL.n}. The rule was fixed in `
    + "writing before any placebo number was read, which is the only reason "
    + "this is a finding and not an embarrassment, and Yoo reports the same "
    + "phenomenon independently. The honest reading is not that the models are "
    + "fair. It is that an instrument this size cannot separate the effect from "
    + "the models' own instability.",
  draw: (s, st) => {
    card(s, { x: 0.55, y: 1.25, w: 12.2, h: 1.1, fill: TINT, name: "q",
      kicker: "THE HARDER QUESTION WE SET OURSELVES", kickerColor: TEAL,
      head: "Does a gender effect beat a clinically meaningless edit to the SAME vignette?",
      headSize: 18, headH: 0.4,
      body: "Not a gender flip on a different case. The patient's eye colour, on this one." });

    const L = st >= 2;
    s.addText("ANSWER", { x: 0.55, y: 2.55, w: 2.5, h: 0.26, fontSize: 10.5,
      bold: true, color: L ? FAIL : GH.mut, charSpacing: 1.1, isTextBox: true,
      margin: 0, objectName: "ak" });
    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 2.85, w: 5.6, h: 1.35,
      rectRadius: 0.07, fill: { color: L ? "FBEEEC" : GH.fill },
      line: { color: L ? FAIL : GH.line, width: 1.4 }, objectName: "a-bg" });
    s.addText(`${PL.passGenderFloor} of ${PL.n}   →   ${PL.passBothFloors} of ${PL.n}`,
      { x: 0.55, y: 2.95, w: 5.6, h: 0.8, fontSize: 38, bold: true,
        fontFace: "Cambria", color: L ? FAIL : GH.ink, align: "center",
        isTextBox: true, margin: 0, objectName: "a-n" });
    s.addText("models survive once both floors must be cleared",
      { x: 0.55, y: 3.78, w: 5.6, h: 0.3, fontSize: 12, bold: true,
        color: L ? INK : GH.ink, align: "center", isTextBox: true, margin: 0,
        objectName: "a-l" });

    s.addText([
      { text: "Why we report it anyway.  ", options: { bold: true, color: L ? INK : GH.ink } },
      { text: "The aggregation rule was fixed in writing before any placebo "
            + "number was read: under the median the gate returns exactly the "
            + "answer we already had, and a test whose only available outcome "
            + "is the one you hold is not a test. Yoo finds the same thing "
            + "independently " + A.m("yoo2026") + ". The honest reading is not "
            + "that the models are fair, but that an instrument this size "
            + "cannot separate a real effect from the models' own instability. "
            + "That bound is itself a result.",
        options: { color: L ? MUT : GH.mut } },
    ], { x: 6.45, y: 2.85, w: 6.3, h: 1.9, fontSize: 12.5, lineSpacing: 16,
         isTextBox: true, margin: 0, valign: "top", objectName: "a-why" });
    tierBanner(s, { x: 0.55, y: 4.95, w: 12.2, h: 0.5, name: "tb3" });
  },
});

// ------------------- 11. result 4, the two findings with no model, 2 clicks
message({
  section: "Results", title: "Result 4: two findings that need no model at all",
  secs: 24, steps: 2,
  notes: "These two need no model and no statistics, and they are the ones I "
    + "would put in front of a regulator. Non-binary people are plainly present "
    + "in both corpora, over a million times in OLMo-mix. The phrase 'the "
    + "non-binary patient' occurs zero times in either. They are in the text "
    + "and never in the clinic, so the sentence in which their care would be "
    + "described is not in the data to be learned from. And the OLMo-mix "
    + "dataset card contains no occurrence of gender, sex, female, demographic, "
    + "bias or health. The Pile's authors DID measure gender, and advertised "
    + "medical text. Nobody joined the two up. So disclosure is a choice, not a "
    + "property of being open.",
  draw: (s, st) => {
    const NB_O = F.corpusProbe("the non-binary patient", "olmo");
    const NB_P = F.corpusProbe("the non-binary patient", "pile");
    const W_O  = F.corpusProbe("the woman has", "olmo");
    const TERM = F.corpusProbe("non-binary", "olmo");
    const R6 = F.rq6Status();

    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 1.25, w: 5.95, h: 2.25,
      rectRadius: 0.07, fill: { color: "FBEEEC" }, line: { color: FAIL, width: 1.4 },
      objectName: "nb-bg" });
    s.addText(String(NB_O + NB_P), { x: 0.75, y: 1.38, w: 5.55, h: 0.95,
      fontSize: 56, bold: true, fontFace: "Cambria", color: FAIL, isTextBox: true,
      margin: 0, objectName: "nb-n" });
    s.addText("occurrences of “the non-binary patient” in either corpus",
      { x: 0.75, y: 2.3, w: 5.55, h: 0.5, fontSize: 14, bold: true, color: INK,
        lineSpacing: 17, isTextBox: true, margin: 0, objectName: "nb-l" });
    s.addText(`Against ${TERM.toLocaleString("en-US")} for the bare term in `
      + `OLMo-mix and ${W_O.toLocaleString("en-US")} for “the woman has”. `
      + `They are in the text and never in the clinic.`,
      { x: 0.75, y: 2.84, w: 5.55, h: 0.56, fontSize: 11.5, color: MUT,
        lineSpacing: 14, isTextBox: true, margin: 0, objectName: "nb-s" });

    const L = st >= 2;
    s.addShape(pres.ShapeType.roundRect, { x: 6.8, y: 1.25, w: 5.95, h: 2.25,
      rectRadius: 0.07, fill: { color: L ? "FDF4E3" : GH.fill },
      line: { color: L ? WARN : GH.line, width: 1.4 }, objectName: "dc-bg" });
    s.addText("0", { x: 7.0, y: 1.38, w: 5.55, h: 0.95, fontSize: 56, bold: true,
      fontFace: "Cambria", color: L ? WARN : GH.ink, isTextBox: true, margin: 0,
      objectName: "dc-n" });
    s.addText("mentions of gender, sex, female, demographic, bias or health in "
      + "the OLMo-mix dataset card",
      { x: 7.0, y: 2.3, w: 5.55, h: 0.5, fontSize: 14, bold: true,
        color: L ? INK : GH.ink, lineSpacing: 17, isTextBox: true, margin: 0,
        objectName: "dc-l" });
    s.addText(`The Pile's authors did measure gender, and advertised medical `
      + `text ${A.m("gao2020", "biderman2022")}. Nobody joined the two up. `
      + `${R6.zeroDocs.length} of ${R6.nDocs} documents mention none of our `
      + `${R6.nTerms} terms.`,
      { x: 7.0, y: 2.84, w: 5.55, h: 0.56, fontSize: 11.5,
        color: L ? MUT : GH.mut, lineSpacing: 14, isTextBox: true, margin: 0,
        objectName: "dc-s" });

    s.addText("Disclosure is a choice, not a property of being open.",
      { x: 0.55, y: 3.72, w: 12.2, h: 0.44, fontSize: 20, bold: true,
        color: ink(st, 2), fontFace: "Cambria", align: "center", isTextBox: true,
        margin: 0, objectName: "foot" });
    s.addText("The guidelines we quote require care for exactly this population. "
      + "The data holds no instance of the sentence in which that care would be "
      + "described.",
      { x: 0.55, y: 4.2, w: 12.2, h: 0.36, fontSize: 13, color: mut(st, 2),
        align: "center", isTextBox: true, margin: 0, objectName: "foot2" });
  },
});
