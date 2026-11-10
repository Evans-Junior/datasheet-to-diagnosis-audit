const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 5. OBJECTIVE + RQ TABLE ============================ //
let s = S("CONTENT", "Problem and objective", "Objective and the six research questions");
card(s, { x: 0.55, y: 1.25, w: 12.2, h: 1.12, fill: INK, kicker: "OBJECTIVE", kickerColor: "7FD4C8",
  head: "To test whether the chain from a published datasheet to a specific piece of clinical advice can be completed at all, and to report on where it breaks.",
  headColor: PAPER, headSize: 14.5, headH: 0.6, name: "obj" });
s.addText("The contribution is not another demonstration that models show gender bias, which is established. It is a working instrument, a pre-registered null, and a measured account of the break points.",
  { x: 0.55, y: 2.48, w: 12.2, h: 0.42, fontSize: 12.5, italic: true, color: MUT, margin: 0, isTextBox: true });

const rq = [
  ["RQ1", "Is there a measurable gender skew in how illnesses are described in the open corpora?", "Final", PASS],
  ["RQ2", "Do models give different clinical advice when only the patient's gender changes?", "Provisional", WARN],
  ["RQ3", "Does that difference grow with model size?", "Provisional", WARN],
  ["RQ4", "Does a model's output gap follow the skew in its own training corpus?", "Not identifiable", FAIL],
  ["RQ5", "Are non-binary patients represented at all in the corpora?", "Final", PASS],
  ["RQ6", "Do the published datasheets disclose gender composition and connect it to health use?", "Final", PASS],
];
const rows = [[
  { text: "", options: { fill: { color: INK } } },
  { text: "Research question", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 12 } },
  { text: "Status", options: { bold: true, color: PAPER, fill: { color: INK }, fontSize: 12, align: "center" } },
]];
rq.forEach((r, i) => rows.push([
  { text: r[0], options: { bold: true, color: TEAL, fontSize: 12.5, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[1], options: { color: INK, fontSize: 12, fill: { color: i % 2 ? PAPER : TINT } } },
  { text: r[2], options: { bold: true, color: r[3], fontSize: 11.5, align: "center", fill: { color: i % 2 ? PAPER : TINT } } },
]));
s.addTable(rows, { x: 0.55, y: 3.0, w: 12.2, colW: [0.9, 9.2, 2.1], rowH: 0.42,
  border: { type: "solid", color: "DCE8EA", pt: 0.75 }, valign: "middle",
  margin: [0.06, 0.12, 0.06, 0.12], fontFace: "Calibri", autoPage: false });
card(s, { x: 0.55, y: 5.72, w: 12.2, h: 0.82, fill: "FDF3E3",
  head: "RQ4 changed status on 3 November. It is now reported as a measured non-identifiability result rather than a provenance estimate.",
  headColor: INK, headSize: 12.5, headH: 0.5, name: "rqnote" });
// D096. This note said "slide 24", which is the statistics slide; RQ4 is on
// 34. It is a forward reference, so no number can be resolved while this
// slide is being built. Naming the slide removes the class of bug.
note(s, "Three of six research questions are final. RQ2 and RQ3 are tier 1 -- reportable for this submission, pending clinical validation, and not publishable until tier 2. RQ4's status change is the most significant revision since the interim report, and the RQ4 results slide explains it.");

// ============ SECTION: LITERATURE ================================ //
pres.addSection({ title: "Related work" });
s = S("SECTION", "Related work", "2.  Related work, and how it changed the design");
s.addText("Four bodies of work, and the specific design decision each one forced", { placeholder: "body" });

// ============ 6. LIT 1: clinical LLM bias ======================== //
s = S("CONTENT", "Related work", "Gender bias in clinical language model outputs");
const lit1 = [
  { h: "Cirillo et al. 2020  [4]", b: "Sets out why sex and gender bias in health AI differs from other domains: clinical correctness sometimes genuinely depends on sex, so an audit that cannot separate a legitimate clinical difference from an illegitimate one is useless.", c: BERRY },
  { h: "Zack et al. 2024  [24]", b: "GPT-4 reproduces racial and gender patterns in clinical vignettes. Established that the effect is real in a frontier model, and set the vignette-based method we build on.", c: TEAL },
  { h: "Chang et al. 2025  [3]", b: "Anti-LGBTQIA+ medical bias across four large language models. Extends the question past the gender binary, which most audits do not do.", c: TEAL },
  { h: "Loge et al. 2021  [14]", b: "Q-Pain measures social bias in pain management through question answering. A direct precedent for scoring fixed answer options rather than free text.", c: TEAL },
];
lit1.forEach((c, i) => {
  const y = 1.3 + i * 1.26;
  card(s, { x: 0.55, y, w: 7.6, h: 1.12, name: "l1" + i });
  s.addText(c.h, { x: 0.77, y: y + 0.13, w: 7.1, h: 0.3, fontSize: 13, bold: true,
    color: c.c, margin: 0, isTextBox: true, objectName: "l1h" + i });
  s.addText(c.b, { x: 0.77, y: y + 0.44, w: 7.16, h: 0.6, fontSize: 11.5, color: MUT,
    lineSpacing: 14, margin: 0, isTextBox: true, objectName: "l1b" + i });
});
card(s, { x: 8.4, y: 1.3, w: 4.35, h: 3.12, fill: INK, kicker: "WHAT THIS ESTABLISHED",
  kickerColor: "7FD4C8", name: "l1x" });
s.addText("That clinical LLM gender bias exists is not in question. Our contribution cannot be another demonstration of it.",
  { x: 8.62, y: 1.84, w: 3.9, h: 0.85, fontSize: 13.5, bold: true, color: PAPER,
    lineSpacing: 17, margin: 0, isTextBox: true });
s.addText("Cirillo's observation drove our central design rule: a gender difference counts as bias only where the clinically correct answer is the same for every patient. That rule is what Group 2 of our vignette set exists to enforce.",
  { x: 8.62, y: 2.82, w: 3.9, h: 1.45, fontSize: 11.5, color: "BCD3D8", lineSpacing: 15,
    margin: 0, isTextBox: true });
card(s, { x: 8.4, y: 4.56, w: 4.35, h: 1.86, fill: "FBEEEC", kicker: "THE GAP WE TARGET",
  kickerColor: FAIL, name: "l1g" });
s.addText("Every model these studies audit was trained on data the public cannot inspect, so the question stops at the model boundary. None can say where the bias originates.",
  { x: 8.62, y: 5.1, w: 3.9, h: 1.2, fontSize: 12, color: INK, lineSpacing: 15.5,
    margin: 0, isTextBox: true });
note(s, "Four papers, one conclusion: the phenomenon is established, so a project that only re-demonstrates it adds nothing. Cirillo is the one that shaped our method rather than our motivation.");

// ============ 7. LIT 2: the 2026 triage audits =================== //
s = S("CONTENT", "Related work", "What the 2026 triage audits changed for us");
s.addText("Two 2026 emergency-triage audits [9, 23] cover gender bias in triage at far greater scale than we could. Our cardiac vignette is demoted from a headline result to one condition among fifteen. Three things survive, and two of our existing choices gain support.",
  { x: 0.55, y: 1.25, w: 12.2, h: 0.68, fontSize: 14, color: INK, lineSpacing: 18, margin: 0, isTextBox: true });
const surv = [
  { h: "Neither has corpus access", b: "So neither can ask where the bias originates. This is the whole space our project occupies." },
  { h: "Both treat gender as binary", b: "So neither speaks to non-binary patients. Our third gender arm is carried throughout, not added as an extra." },
  { h: "Neither has a sex-specific control", b: "So neither can show its models correctly differentiate where they should. Our Group 2 does exactly this, and it is why we can tell a null from a blind instrument." },
];
surv.forEach((c, i) => {
  const x = 0.55 + i * 4.1;
  card(s, { x, y: 2.12, w: 3.85, h: 2.0, name: "sv" + i });
  badge(s, { x: x + 0.22, y: 2.3, n: i + 1, d: 0.4, fs: 13, name: "svb" + i });
  s.addText(c.h, { x: x + 0.72, y: 2.3, w: 2.9, h: 0.4, fontSize: 12.5, bold: true,
    color: INK, margin: 0, isTextBox: true, valign: "middle", objectName: "svh" + i });
  s.addText(c.b, { x: x + 0.22, y: 2.82, w: 3.42, h: 1.14, fontSize: 11.5, color: MUT,
    lineSpacing: 14.5, margin: 0, isTextBox: true, objectName: "svb2" + i });
});
s.addText("Their findings also support two choices we had already made", { x: 0.55, y: 4.36, w: 12.2, h: 0.32,
  fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true });
card(s, { x: 0.55, y: 4.78, w: 6.0, h: 1.62, fill: "E6F5F2", kicker: "SUPPORTS EXCLUDING PATIENT NAMES",
  kickerColor: PASS, name: "sp1" });
s.addText("In one model the effect arose from the gender token alone. A name carries ethnicity and class signal alongside gender, so a name-based manipulation would confound the variable we are isolating. Our prompts use an explicit label and pronouns only.",
  { x: 0.77, y: 5.3, w: 5.56, h: 1.0, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
card(s, { x: 7.3, y: 4.78, w: 5.45, h: 1.62, fill: "E6F5F2", kicker: "SUPPORTS SCORING OPTIONS, NOT FREE TEXT",
  kickerColor: PASS, name: "sp2" });
s.addText("Chain-of-thought prompting reduced accuracy in all five models they tested, which matches Turpin et al. [21] on unfaithful explanations. We score probability on fixed options instead, which buys determinism.",
  { x: 7.52, y: 5.3, w: 5.0, h: 1.0, fontSize: 11.5, color: INK, lineSpacing: 14.5, margin: 0, isTextBox: true });
note(s, "This slide is the honest response to a reviewer asking whether recent work scooped us. It did on the cardiac condition, and we say so. What survives is the corpus access, the non-binary arm and the positive control, and their results independently back two of our method choices.");

module.exports = {};
