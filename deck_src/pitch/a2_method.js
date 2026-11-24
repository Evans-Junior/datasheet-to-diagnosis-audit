// ACT 2, the instrument. Messages 5 to 7, 80 seconds.
// The three-audit diagram is redrawn here as native shapes rather than placed
// as the paper's fig_method.pdf, because a picture cannot be revealed one
// column at a time and that reveal is the point of this slide.
const K = require("./kit.js");
const F = require("../figures.js");
const A = require("../short/acm.js");
const { pres, S, message, box, card, arrow, ink, mut, line, fill, on,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY, GH } = K;

const LV = F.liveVignettes();

// ------------------------------------------- 5. the three audits, 4 clicks
const COLS = [
  ["OUTPUT AUDIT", "RQ2, RQ3, RQ5", [
    [`${LV.live} clinical vignettes`, "four groups; the correct answer\nquoted from a named guideline"],
    [`${LV.livePrompts} prompts`, "sex parameter held fixed,\nidentity label varied"],
    ["10 models scored", "17,280 answer options, against\ntwo floors and a control"]]],
  ["DATA AUDIT", "RQ1", [
    ["Two open corpora", "the Pile (Pythia) and\nOLMo-mix (OLMo 2)"],
    ["Exact-phrase counts", "infini-gram, over matched\nillness-narration templates"],
    ["Skew per concept", "log₂(female rate / male rate),\ncompared concept to concept"]]],
  ["DOCUMENTATION AUDIT", "RQ6", [
    ["10 cards and reports", "for the corpora and the models\nwe actually queried"],
    ["A 30-term search", "sex, gender and health terms,\nper document"],
    ["What each discloses", "was gender measured, was\nhealth use declared"]]],
];

message({
  section: "Method", title: "Three audits over the same clinical concepts",
  secs: 33, steps: 4,
  notes: "Say what this is first: what we built is not a clinical system, it "
    + "is an audit instrument, and it is built for three people. Someone "
    + "procuring a model, who gets a test it has to pass before any fairness "
    + "claim counts. Someone publishing a corpus, who gets the three "
    + "documentation fields whose absence made this necessary. And an auditor "
    + "with no access to training data, who gets a worked example. Then the "
    + "three audits. The output audit builds the vignettes and scores the models. A "
    + "clinical vignette is just a short written patient case, a few lines of "
    + "history and findings and then a question, the kind used to examine "
    + "medical students. The data audit measures gender skew around those same "
    + "concepts in the corpora. The documentation audit reads the datasheets. "
    + "The reason they can be put together is that the first two measure the "
    + "SAME concepts, so a gap in a model's answers can be set beside the skew "
    + "in the corpus it was trained on.",
  draw: (s, st) => {
    const CW = 3.95, BH = 0.95, Y0 = 1.42, VG = 0.26;
    COLS.forEach(([head, rq, steps], ci) => {
      const live = st >= ci + 1;
      const x = 0.55 + ci * (CW + 0.17);
      s.addText(head, { x, y: 1.0, w: CW, h: 0.26, fontSize: 11.5, bold: true,
        color: live ? TEAL : GH.ink, align: "center", charSpacing: 0.8,
        isTextBox: true, margin: 0, objectName: `h${ci}` });
      s.addText(rq, { x, y: 1.21, w: CW, h: 0.2, fontSize: 9.5, italic: true,
        color: live ? MUT : GH.mut, align: "center", isTextBox: true, margin: 0,
        objectName: `r${ci}` });
      steps.forEach(([t, b], ri) => {
        const y = Y0 + ri * (BH + VG);
        s.addShape(pres.ShapeType.roundRect, { x, y, w: CW, h: BH, rectRadius: 0.06,
          fill: { color: live ? TINT : GH.tint },
          line: { color: live ? "CFE0E3" : GH.line, width: 1 },
          objectName: `c${ci}${ri}-bg` });
        s.addText(t, { x: x + 0.1, y: y + 0.12, w: CW - 0.2, h: 0.26, fontSize: 12.5,
          bold: true, color: live ? INK : GH.ink, align: "center", isTextBox: true,
          margin: 0, objectName: `c${ci}${ri}-t` });
        s.addText(b, { x: x + 0.1, y: y + 0.4, w: CW - 0.2, h: 0.48, fontSize: 10,
          color: live ? MUT : GH.mut, align: "center", lineSpacing: 12.5,
          isTextBox: true, margin: 0, objectName: `c${ci}${ri}-b` });
        if (ri < 2) arrow(s, { x: x + CW / 2 - 0.09, y: y + BH + 0.05, w: 0.18, h: 0.16,
          rotate: 90, color: live ? "9BB3BA" : GH.line, name: `a${ci}${ri}` });
      });
    });
    const live4 = st >= 4;
    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 5.08, w: 12.2, h: 0.92,
      rectRadius: 0.07, fill: { color: live4 ? "E6F6F2" : GH.tint },
      line: { color: live4 ? PASS : GH.line, width: 1.4 }, objectName: "syn-bg" });
    s.addText("Does a model's gap follow the skew in its OWN corpus, and did "
      + "that corpus's datasheet warn anyone?",
      { x: 0.75, y: 5.08, w: 11.8, h: 0.92, fontSize: 17, bold: true,
        color: live4 ? INK : GH.ink, align: "center", valign: "middle",
        fontFace: "Cambria", isTextBox: true, margin: 0, objectName: "syn" });

    // The design objective, present from the first click because it frames
    // every column above it: what was built, and who it is built for. The
    // deck used to leave this implicit until the ask, twelve slides later.
    s.addText("WHAT THIS BUILDS", { x: 0.55, y: 6.17, w: 2.4, h: 0.24,
      fontSize: 10, bold: true, color: TEAL, charSpacing: 1.1, isTextBox: true,
      margin: 0, objectName: "obj-k" });
    s.addText("An audit instrument, not a clinical system. For a team "
      + "procuring a model, a team publishing a corpus, and an auditor with no "
      + "access to the training data.",
      { x: 2.95, y: 6.13, w: 9.8, h: 0.5, fontSize: 12.5, color: MUT,
        lineSpacing: 15, isTextBox: true, margin: 0, objectName: "obj-b" });
  },
});

// ----------------------------------------- 6. the design rule, 2 clicks
message({
  section: "Method", title: "Every commitment decided something in the build",
  secs: 30, steps: 3,
  notes: "This is the rule the whole instrument rests on, and it is why this "
    + "is harder than a normal fairness audit. Some clinical decisions SHOULD "
    + "turn on sex. An audit that cannot tell a legitimate difference from an "
    + "illegitimate one is worse than useless. So we separate the two fields "
    + "the way the HL7 Gender Harmony model separates them: sex for clinical "
    + "use is what a guideline reasons over, gender identity is how the patient "
    + "is described. We hold the first fixed and vary only the second. When the "
    + "two disagree, that is a transgender patient, and the clinical text is "
    + "byte-identical in every arm. Last click: three more. Dev and colleagues "
    + "show that treating gender as binary is itself a harm, so there is a "
    + "non-binary arm in every vignette and it is never pooled with the other "
    + "two. EQUITRIAGE removes one cue at a time, so we dropped patient names, "
    + "because a name carries class and ethnicity as well as gender. Yoo shows "
    + "wording alone moves a model, so nothing is ever judged against zero. "
    + "None of these is our opinion; each is a published finding and each one "
    + "decided a field, an arm or a line of code.",
  draw: (s, st) => {
    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 1.3, w: 12.2, h: 0.95,
      rectRadius: 0.07, fill: { color: TINT }, line: { color: TEAL, width: 1.3 },
      objectName: "rule-bg" });
    s.addText("A gender difference counts as bias only where the clinically "
      + "correct answer is the same for every patient.",
      { x: 0.8, y: 1.3, w: 11.7, h: 0.95, fontSize: 19, bold: true, color: INK,
        align: "center", valign: "middle", fontFace: "Cambria", isTextBox: true,
        margin: 0, objectName: "rule" });
    s.addText("Some clinical decisions should turn on sex. An audit that cannot "
      + "tell those apart from the rest is worse than useless " + A.m("cirillo2020") + ".",
      { x: 0.55, y: 2.38, w: 12.2, h: 0.34, fontSize: 13, color: MUT,
        isTextBox: true, margin: 0, objectName: "rulesub" });

    // click 2: the two fields
    const L = st >= 2;
    s.addText("SO THE PROMPT CARRIES TWO FIELDS, NOT ONE " + (L ? A.m("mcclure2021") : ""),
      { x: 0.55, y: 2.95, w: 12.2, h: 0.26, fontSize: 10.5, bold: true,
        color: L ? MUT : GH.mut, charSpacing: 1.1, isTextBox: true, margin: 0,
        objectName: "k2" });
    [["Sex for clinical use", "what the guideline reasons over", "HELD FIXED", PASS],
     ["Gender identity label", "how the patient is described", "VARIED", WARN],
    ].forEach(([h, b, tag, c], i) => {
      const x = 0.55 + i * 6.3;
      s.addShape(pres.ShapeType.roundRect, { x, y: 3.3, w: 5.9, h: 1.3,
        rectRadius: 0.07, fill: { color: L ? PAPER : GH.fill },
        line: { color: L ? c : GH.line, width: 1.4 }, objectName: `f${i}-bg` });
      s.addText(tag, { x: x + 0.2, y: 3.44, w: 5.5, h: 0.24, fontSize: 10,
        bold: true, color: L ? c : GH.mut, charSpacing: 1.1, isTextBox: true,
        margin: 0, objectName: `f${i}-k` });
      s.addText(h, { x: x + 0.2, y: 3.7, w: 5.5, h: 0.34, fontSize: 17, bold: true,
        color: L ? INK : GH.ink, isTextBox: true, margin: 0, objectName: `f${i}-h` });
      s.addText(b, { x: x + 0.2, y: 4.06, w: 5.5, h: 0.3, fontSize: 12,
        color: L ? MUT : GH.mut, isTextBox: true, margin: 0, objectName: `f${i}-b` });
    });
    s.addText("When the two disagree, that is a transgender patient. The clinical "
      + "text is byte-identical in every arm.",
      { x: 0.55, y: 4.72, w: 12.2, h: 0.34, fontSize: 15, bold: true,
        color: ink(st, 2), isTextBox: true, margin: 0, objectName: "f-foot" });

    // Click 3: three more commitments, each with the thing it decided. This is
    // the element the report rubric asks for by name, translating a normative
    // position into an implementation choice, and the deck used to carry two
    // of these silently (Cirillo above, HL7 beside it) without ever saying
    // that was what it was doing.
    const T = st >= 3;
    s.addText("AND THE SAME MOVE, THREE MORE TIMES", { x: 0.55, y: 5.2,
      w: 12.2, h: 0.24, fontSize: 10.5, bold: true, color: T ? MUT : GH.mut,
      charSpacing: 1.1, isTextBox: true, margin: 0, objectName: "k3" });
    [["Binary gender is itself a harm " + (T ? A.m("dev2021") : ""),
      "a non-binary arm in every vignette,\nnever pooled with the other two"],
     ["Remove one cue at a time " + (T ? A.m("equitriage2026") : ""),
      "patient names dropped: a name carries\nclass and ethnicity too"],
     ["Wording alone moves a model " + (T ? A.m("yoo2026") : ""),
      "no effect judged against zero,\nonly against a measured floor"],
    ].forEach(([h, b], i) => {
      const x = 0.55 + i * 4.11;
      s.addShape(pres.ShapeType.roundRect, { x, y: 5.52, w: 4.0, h: 1.12,
        rectRadius: 0.06, fill: { color: T ? TINT : GH.tint },
        line: { color: T ? "CFE0E3" : GH.line, width: 1 },
        objectName: `v${i}-bg` });
      s.addText(h, { x: x + 0.16, y: 5.64, w: 3.68, h: 0.3, fontSize: 11.5,
        bold: true, color: T ? INK : GH.ink, isTextBox: true, margin: 0,
        objectName: `v${i}-h` });
      s.addText(b, { x: x + 0.16, y: 5.96, w: 3.68, h: 0.56, fontSize: 10.5,
        color: T ? MUT : GH.mut, lineSpacing: 13, isTextBox: true, margin: 0,
        objectName: `v${i}-b` });
    });
  },
});

// -------------------------------- 7. the positive control idea, 2 clicks
message({
  section: "Method", title: "Before trusting any null, test that the model can see",
  secs: 22, steps: 2,
  notes: "This is the contribution I would most like you to take away, because "
    + "it is free and it transfers to any audit. We built a group of vignettes "
    + "where the guideline's OWN answer changes with the sex parameter. A "
    + "pregnancy test is indicated before abdominal imaging when the sex "
    + "parameter is female and not when it is male. A model that does not move "
    + "there is not reading the clinical record at all, so nothing you measure "
    + "anywhere else about that model means anything. Neither of the two "
    + "closest prior audits has such a control.",
  draw: (s, st) => {
    card(s, { x: 0.55, y: 1.3, w: 12.2, h: 1.45, fill: TINT, name: "g2",
      kicker: "THE POSITIVE CONTROL", kickerColor: TEAL,
      head: "A group of vignettes where the guideline's own answer changes with sex",
      headSize: 18, headH: 0.38,
      body: "A pregnancy test is indicated before abdominal imaging when the sex "
          + "parameter is female, and not when it is male. The model is supposed "
          + "to move here." });
    const L = st >= 2;
    [["Model moves here", "then its answers elsewhere can be read", PASS, "E6F6F2"],
     ["Model does not move", "it is not reading the clinical record,\nso nothing about it can be read", FAIL, "FBEEEC"],
    ].forEach(([h, b, c, bg], i) => {
      const x = 0.55 + i * 6.3;
      s.addShape(pres.ShapeType.roundRect, { x, y: 3.05, w: 5.9, h: 1.3,
        rectRadius: 0.07, fill: { color: L ? bg : GH.fill },
        line: { color: L ? c : GH.line, width: 1.4 }, objectName: `o${i}-bg` });
      s.addText(h, { x: x + 0.2, y: 3.22, w: 5.5, h: 0.34, fontSize: 17, bold: true,
        color: L ? c : GH.ink, isTextBox: true, margin: 0, objectName: `o${i}-h` });
      s.addText(b, { x: x + 0.2, y: 3.6, w: 5.5, h: 0.6, fontSize: 12.5,
        color: L ? MUT : GH.mut, lineSpacing: 15, isTextBox: true, margin: 0,
        objectName: `o${i}-b` });
    });
    s.addText("A model with no measured gender gap may be blind, not fair. "
      + "Only a positive control tells the two apart.",
      { x: 0.55, y: 4.58, w: 12.2, h: 0.4, fontSize: 17, bold: true,
        color: ink(st, 2), fontFace: "Cambria", isTextBox: true, margin: 0,
        objectName: "pc-foot" });
  },
});
