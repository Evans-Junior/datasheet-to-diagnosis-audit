// Talk deck, beats 1 and 2. See talk/build.js for why this deck exists.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, srcLine, card, stat, box, arrow, note, tierBanner,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const LV = F.liveVignettes();
const VG = F.vignetteGroups();
const MG = F.merging();
const UP = F.lastUpdated();

// ---------------------------------------------------------------- title ----
pres.addSection({ title: "Open" });
{
  const s = S("TITLE_DARK", "Open", "From datasheet to diagnosis");
  s.addText("Tracing gender bias through open training-data pipelines into LLM health advice",
    { placeholder: "body" });
  s.addText("Evans Kumi  ·  Aymen Boustani        ECSE-557 Ethics in Artificial Intelligence, McGill",
    { x: 0.9, y: 5.75, w: 11.5, h: 0.3, fontSize: 13, color: "8FB2BA",
      isTextBox: true, margin: 0, objectName: "authors" });
  s.addText(`Research track  ·  ${LV.live} vignettes  ·  ${LV.livePrompts.toLocaleString("en-US")} prompts  ·  10 models  ·  2 open corpora`,
    { x: 0.9, y: 6.12, w: 11.5, h: 0.3, fontSize: 11.5, color: TEAL,
      isTextBox: true, margin: 0, objectName: "scope" });
  s.addText(`Tier 1 result, pending clinical validation  ·  last updated ${UP.long}`,
    { x: 0.9, y: 6.52, w: 11.5, h: 0.3, fontSize: 10.5, color: "6E8C94",
      isTextBox: true, margin: 0, italic: true, objectName: "tier" });
  note(s, "Fifteen to twenty minutes. Ten beats. The spine is: why this matters, "
   + "what nobody could do before, how we built a measuring instrument, how we "
   + "know the instrument is not broken, what it measured, and what that means "
   + "ethically. The one thing to say in the first thirty seconds is that this "
   + "is the first audit of its kind that can look at the training data, because "
   + "that is what makes every other claim possible.");
}

// ------------------------------------------------- 1. hook: one vignette ----
pres.addSection({ title: "1 The problem" });
{
  const s = S("CONTENT", "1 The problem", "The same patient. The same physiology. A different answer.");
  const top = MG[0], second = MG[1];

  card(s, { x: 0.55, y: 1.28, w: 6.0, h: 2.55, fill: TINT, name: "vig",
    kicker: "ONE VIGNETTE, TWO ARMS", kickerColor: TEAL,
    head: "Sex parameter held FIXED. Only the identity label changes.",
    headH: 0.52, headSize: 14,
    body: "Arm A:  “A 34-year-old woman presents with …”\n"
        + "Arm B:  “A 34-year-old non-binary person presents with …”\n\n"
        + "Same clinical findings, same sex parameter for clinical use, same "
        + "question, same option set. The guideline gives one correct answer to "
        + "both. A model that is reading physiology cannot move." });

  card(s, { x: 6.78, y: 1.28, w: 6.0, h: 2.55, fill: "FBEEEC", name: "res",
    kicker: "WHAT THE MODELS DO", kickerColor: FAIL,
    head: "They move, and they move a long way.", headH: 0.52, headSize: 14,
    body: `${top.model} shifts probability mass by ${top.mean.toFixed(3)}, which is `
        + `${top.timesFloor.toFixed(1)} times its own measured noise floor, in the `
        + `same direction on all ${top.nVignettes} positive-control vignettes.\n\n`
        + `${second.model} does the same at ${second.timesFloor.toFixed(1)} times its floor. `
        + "The models are treating a social label as a clinical parameter." });

  s.addText("And the people the guidelines name are the ones the data does not contain",
    { x: 0.55, y: 4.08, w: 12.2, h: 0.3, fontSize: 15, bold: true, color: INK,
      isTextBox: true, margin: 0, objectName: "zh" });

  // Read the counts out of the probe by term rather than by position, and
  // refuse a missing one. A typo in a key would otherwise print "undefined"
  // onto the slide, which is the exact failure D095 was logged for.
  const pr = F.rq5Probe();
  const probe = t => {
    const r = pr.rows.find(x => x.term === t);
    if (!r) throw new Error(`t1.js: rq5Probe has no term "${t}". ` +
      `Has: ${pr.rows.map(x => x.term).join(" | ")}`);
    return r;
  };
  const cells = [
    { t: '"the woman has"', v: probe("the woman has").olmo, c: TEAL },
    { t: '"non-binary"', v: probe("non-binary").olmo, c: WARN },
    { t: '"the non-binary patient"', v: probe("the non-binary patient").olmo, c: FAIL },
  ];
  cells.forEach((c, i) => {
    const x = 0.55 + i * 4.17;
    card(s, { x, y: 4.46, w: 3.86, h: 1.3, fill: TINT, name: "pb" + i });
    stat(s, { x: x + 0.24, y: 4.62, w: 3.4, n: c.v.toLocaleString("en-US"),
      label: c.t, color: c.c, size: 26, nh: 0.56, name: "pbs" + i });
  });
  s.addText("Occurrences in olmo-mix-1124, the corpus OLMo 2 is trained on. "
    + "The clinical guidelines in this study name trans and non-binary patients "
    + "explicitly. The corpus does not.",
    { x: 0.55, y: 5.9, w: 12.2, h: 0.44, fontSize: 11, color: MUT,
      isTextBox: true, margin: 0, lineSpacing: 13, objectName: "zc" });

  tierBanner(s, { x: 0.55, y: 6.42, w: 12.2, h: 0.46, name: "tb1" });
  srcLine(s, ["mcclure2021", "dev2021", "liu2024"], { name: "src91" });
  note(s, "Open on the vignette, not on the method. The audience has to feel the "
   + "problem before they will sit through how it was measured. Say the sex "
   + "parameter is held fixed twice, because that is the move everything else "
   + "rests on: we are not asking whether the model knows women and men differ "
   + "clinically, we are asking whether it changes a clinical answer when only "
   + "the social label moves. Then the zero. The zero is the ethical centre of "
   + "the talk: a guideline that names non-binary patients, and a corpus that "
   + "has never seen the phrase.");
}

// --------------------------------------------- 2. related work and gap ----
{
  const s = S("CONTENT", "1 The problem", "Everyone can see the bias. Nobody could see its source.");

  card(s, { x: 0.55, y: 1.28, w: 3.92, h: 2.5, fill: TINT, name: "rw1",
    kicker: "WHAT EXISTS", kickerColor: TEAL,
    head: "Output audits, at scale", headH: 0.34,
    body: "EQUITRIAGE (2026): 374,275 evaluations, 18,714 vignettes, 5 closed "
        + "models. All exceed a 5% flip-rate threshold.\n\n"
        + "Guerra-Adames (2025): 140,000+ admissions, MIMIC-IV.\n\n"
        + "Chang et al. (2025), PLOS Digit Health: paired prompts, the design "
        + "this study builds on." });

  card(s, { x: 4.69, y: 1.28, w: 3.92, h: 2.5, fill: "FBEEEC", name: "rw2",
    kicker: "WHAT NONE OF THEM CAN DO", kickerColor: FAIL,
    head: "Say why", headH: 0.34,
    body: "Every one of them audits a model whose training data is "
        + "proprietary, or trains on records it cannot release.\n\n"
        + "So the finding stops at “the model is biased”. No corpus "
        + "measurement, no provenance, and no way to ask whether the "
        + "documentation disclosed the risk." });

  card(s, { x: 8.83, y: 1.28, w: 3.95, h: 2.5, fill: "E6F6F2", name: "rw3",
    kicker: "WHAT OPENNESS BUYS", kickerColor: PASS,
    head: "The whole pipeline", headH: 0.34,
    body: "Pythia is trained on the Pile. OLMo 2 is trained on "
        + "olmo-mix-1124. Both corpora are published and both are "
        + "exact-substring queryable through infini-gram.\n\n"
        + "So the corpus, the model and the datasheet can be measured in the "
        + "same study." });

  s.addText("The question", { x: 0.55, y: 4.02, w: 12.2, h: 0.3, fontSize: 15,
    bold: true, color: INK, isTextBox: true, margin: 0, objectName: "qh" });
  s.addText("Can gender bias in LLM health advice be traced back through an open "
    + "training-data pipeline to measurable skew in the corpus, and did the "
    + "corpus documentation disclose that risk?",
    { x: 0.55, y: 4.36, w: 12.2, h: 0.56, fontSize: 14, color: INK,
      isTextBox: true, margin: 0, lineSpacing: 18, italic: true, objectName: "qb" });

  const steps = [
    { t: "Corpus\nRQ1", c: TEAL }, { t: "Model\nRQ2, RQ3", c: TEAL },
    { t: "Linkage\nRQ4", c: WARN }, { t: "Closed contrast\nRQ5", c: BERRY },
    { t: "Datasheet\nRQ6", c: PASS },
  ];
  steps.forEach((st, i) => {
    const x = 0.9 + i * 2.44;
    box(s, { x, y: 5.14, w: 1.96, h: 0.72, t: st.t, fs: 11.5, line: st.c,
      tc: st.c, name: "st" + i });
    if (i < steps.length - 1) arrow(s, { x: x + 2.02, y: 5.42, w: 0.36, h: 0.16,
      color: "9BB3BA", name: "sa" + i });
  });
  s.addText("Six research questions, one pipeline. RQ1 measures the corpus, RQ2 "
    + "and RQ3 the models, RQ4 asks whether the two are linked, RQ5 contrasts a "
    + "model whose data is closed, RQ6 reads what the documentation disclosed.",
    { x: 0.55, y: 6.06, w: 12.2, h: 0.46, fontSize: 11, color: MUT,
      isTextBox: true, margin: 0, lineSpacing: 13, objectName: "sc" });
  srcLine(s, ["equitriage2026", "guerra2025", "chang2025", "zack2024", "feng2023", "elazar2024"], { name: "src158" });
  note(s, "Two things to land. First, concede the ground: output-level gender "
   + "bias in clinical LLMs is already established, by studies far larger than "
   + "ours, and EQUITRIAGE overlaps one of our vignettes directly at a thousand "
   + "times the scale. Do not compete there. Second, name what survives: none of "
   + "them can open the training data, so RQ1, RQ3 and RQ4 are impossible for "
   + "them. Our contribution is the link, not the gap.");
}

module.exports = {};
