// The story spine: the whole argument in six moves, each with the paper that
// forced it. Added 2026-11-09 so the deck reads as an argument rather than as
// a tour of research questions.
const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

let s = S("CONTENT", "Related work", "The argument in six moves, and the paper behind each");
s.addText("Read down the left column and the thesis is one sentence long. Read the right column and every step is somebody else's result we are standing on.",
  { x: 0.55, y: 1.14, w: 12.2, h: 0.3, fontSize: 12.5, color: MUT, margin: 0, isTextBox: true });

const MOVES = [
  { n: "1", claim: "Clinical LLM bias is real and measurable with paired vignettes.",
    detail: "Established, not assumed. We inherit the design rather than re-argue it.",
    src: "Zack et al., Lancet Digit Health 2024 · Chang et al., PLOS Digit Health 2025",
    c: TEAL },
  { n: "2", claim: "Audits almost all stop at the model boundary.",
    detail: "They measure outputs and infer the cause. The training data stays a black box, so “where did this come from” is never answered.",
    src: `Our gap claim — surveyed in slide ${K.slideNo("relatedWork")}`,
    c: TEAL },
  { n: "3", claim: "“Sex” and “gender” are not one field, and a standard already says so.",
    detail: "HL7 splits them into gender identity, recorded sex, and the Sex Parameter for Clinical Use. That split IS our manipulation: hold SPCU, vary identity.",
    src: "McClure et al., JAMIA 2021 (Gender Harmony) · Heidari et al., SAGER 2016",
    c: BERRY },
  { n: "4", claim: "So we can ask a question the field cannot: does the gap appear where the corpus skew is?",
    detail: "Open-data models (Pythia, OLMo 2) let us count concept-level gender skew in the actual pretraining corpus and line it up against the decision gap.",
    src: "Our contribution — RQ1 × RQ4",
    c: WARN },
  { n: "5", claim: "But the corpus-to-behaviour link was already shown causally — for Pythia, by Pythia.",
    detail: "Their “Mitigating Gender Bias” section counterfactually retrains on modified pronoun frequencies. We cite it and narrow our claim: clinical guideline-concordance, at concept level, not pronoun stereotyping.",
    src: "Biderman et al., Pythia (ICML 2023) — found by us, and it costs us a novelty claim",
    c: FAIL },
  { n: "6", claim: "And a result is worthless if the instrument cannot see anything.",
    detail: "Hence a positive control before any finding, a nuisance floor beside every delta, and a reporting tier that says which claims the evidence supports.",
    src: "Turpin et al. & Lanham et al. 2023 (stated reasoning is not faithful) · Gebru et al., Datasheets",
    c: PASS },
];
MOVES.forEach((m, i) => {
  const y = 1.56 + i * 0.82;
  s.addShape(pres.ShapeType.roundRect, { x: 0.55, y, w: 12.2, h: 0.74, rectRadius: 0.05,
    fill: { color: i % 2 ? PAPER : TINT }, line: { color: i % 2 ? "E4EDEE" : TINT, width: 0.75 },
    objectName: "mv" + i });
  badge(s, { x: 0.72, y: y + 0.2, n: m.n, d: 0.34, fs: 12, color: m.c, name: "mb" + i });
  s.addText(m.claim, { x: 1.18, y: y + 0.07, w: 7.1, h: 0.3, fontSize: 12, bold: true,
    color: INK, margin: 0, isTextBox: true });
  s.addText(m.detail, { x: 1.18, y: y + 0.36, w: 7.1, h: 0.34, fontSize: 9.5,
    color: MUT, lineSpacing: 11.5, margin: 0, isTextBox: true });
  s.addText(m.src, { x: 8.45, y: y + 0.14, w: 4.15, h: 0.48, fontSize: 9,
    italic: true, color: m.c, lineSpacing: 11, margin: 0, valign: "middle", isTextBox: true });
});
note(s, "Move 5 is the one to say out loud. We found the Pythia paper's own counterfactual-retraining result ourselves, and it is a stronger design than our RQ4 correlation. Saying so, and narrowing the claim to clinical concept-level guideline concordance, is better than letting a reviewer find it. If asked what we would do with more compute: intervene on clinical concept frequencies and retrain, using the mechanism Pythia's authors built.");

module.exports = {};
