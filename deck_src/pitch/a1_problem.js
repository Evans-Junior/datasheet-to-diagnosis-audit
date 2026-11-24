// ACT 1, the problem. Messages 1 to 4, 79 seconds.
const K = require("./kit.js");
const F = require("../figures.js");
const A = require("../short/acm.js");
const { pres, S, message, box, card, stat, arrow, note, ink, mut, line, fill, on,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY, GH } = K;

// ---------------------------------------------------------------- 1. title
{
  const s = S("TITLE_DARK", "Open", "From Datasheet to Diagnosis");
  s.addText("Tracing gender bias through open training-data pipelines into the "
    + "health advice of large language models", { placeholder: "body" });
  s.addText("Evans Kumi  ·  Aymen Boustani      M.Sc. Intelligent Systems, McGill University",
    { x: 0.9, y: 5.6, w: 11.5, h: 0.3, fontSize: 13, color: "8FB2BA",
      isTextBox: true, margin: 0, objectName: "auth" });
  note(s, "[12s] Five minutes. I am going to show you one question, one "
    + "instrument and four results, and the fourth one is the one that should "
    + "change what a datasheet contains.");
}

// ------------------------------------------------- 2. the case, 2 clicks
message({
  section: "Problem", title: "A patient asks a chatbot about her symptoms",
  secs: 26, steps: 2,
  notes: "This is not hypothetical. Zack and colleagues showed GPT-4 changing "
    + "its diagnosis and its management plan with the patient's stated gender "
    + "on otherwise identical cases. And attributing a woman's physical "
    + "symptoms to emotion is one of the best-documented biases in human "
    + "medicine. The machine did not invent this. It learned it.",
  draw: (s, st) => {
    card(s, { x: 0.55, y: 1.35, w: 6.0, h: 2.5, fill: TINT, name: "case",
      kicker: "THE CASE", kickerColor: TEAL,
      head: "Sudden breathlessness,\nsharp chest pain, racing heart",
      headSize: 19, headH: 0.9,
      body: "The clinical facts are a pulmonary embolism: a clot in the lungs, "
          + "and a medical emergency." });

    // the two answers, revealed together on click 2
    const live = st >= 2;
    box(s, { x: 6.95, y: 1.35, w: 5.8, h: 1.1, fs: 15,
      t: live ? "Told she is a man:\n“let us rule out a clot”" : " ",
      fill: live ? "E6F6F2" : GH.fill, line: live ? PASS : GH.line,
      tc: live ? INK : GH.ink, name: "ans-m" });
    box(s, { x: 6.95, y: 2.62, w: 5.8, h: 1.23, fs: 15,
      t: live ? "Told she is a woman:\n“this may be a panic attack”" : " ",
      fill: live ? "FBEEEC" : GH.fill, line: live ? FAIL : GH.line,
      tc: live ? INK : GH.ink, name: "ans-f" });

    s.addText("Same clinical text. The only thing that changed was the word for "
      + "the patient.", { x: 0.55, y: 4.15, w: 12.2, h: 0.4, fontSize: 16,
      bold: true, color: ink(st, 2), isTextBox: true, margin: 0, objectName: "pt" });
    s.addText(`Documented for GPT-4 across diagnosis and management ${A.m("zack2024")}; `
      + `the underlying human bias is older than the models ${A.m("hoffmann2001", "samulowitz2018")}.`,
      { x: 0.55, y: 4.62, w: 12.2, h: 0.5, fontSize: 13, color: mut(st, 2),
        isTextBox: true, margin: 0, objectName: "cite" });
  },
});

// ------------------------------------------- 3. why nobody can say why
message({
  section: "Problem", title: "Every audit stops at the same wall",
  secs: 22,
  notes: "Here is the structural problem. The training data of a commercial "
    + "model is a trade secret, so the only thing an auditor can observe is the "
    + "answer. The strongest finding available is 'this model is biased', and "
    + "that sentence supports no particular action. You cannot fix data you "
    + "cannot see, you cannot require a disclosure you cannot check, and "
    + "'decline to deploy' is not a decision anyone makes on one word.",
  draw: (s) => {
    s.addText("The strongest thing an output-only audit can say:",
      { x: 0.55, y: 1.3, w: 12.2, h: 0.32, fontSize: 14, color: MUT,
        isTextBox: true, margin: 0, objectName: "lead" });
    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 1.74, w: 12.2, h: 0.92,
      rectRadius: 0.07, fill: { color: "FBEEEC" }, line: { color: FAIL, width: 1.3 },
      objectName: "claim-bg" });
    s.addText("“This model is biased.”", { x: 0.55, y: 1.74, w: 12.2, h: 0.92,
      fontSize: 26, bold: true, color: FAIL, align: "center", valign: "middle",
      fontFace: "Cambria", isTextBox: true, margin: 0, objectName: "claim" });

    s.addText("WHICH SUPPORTS NONE OF THESE", { x: 0.55, y: 2.95, w: 12.2, h: 0.26,
      fontSize: 10.5, bold: true, color: MUT, charSpacing: 1.1, isTextBox: true,
      margin: 0, objectName: "kick" });
    ["Fix the data", "Require the disclosure", "Decline to deploy"]
      .forEach((t, i) => {
        const x = 0.55 + i * 4.11;
        s.addShape(pres.ShapeType.roundRect, { x, y: 3.3, w: 4.0, h: 0.8,
          rectRadius: 0.06, fill: { color: "F6F1F0" },
          line: { color: "D9C4C0", width: 1 }, objectName: `d${i}-bg` });
        s.addText(t, { x, y: 3.3, w: 4.0, h: 0.8, fontSize: 15, bold: true,
          color: "A8827C", strike: "sngStrike", align: "center", valign: "middle",
          isTextBox: true, margin: 0, objectName: `d${i}-t` });
      });

    s.addText("The data is closed, so the cause cannot be named, so nothing "
      + "follows from the finding.", { x: 0.55, y: 4.45, w: 12.2, h: 0.4,
      fontSize: 16, bold: true, color: INK, isTextBox: true, margin: 0,
      objectName: "why" });
  },
});

// ---------------------------------------------- 4. the opening we use
message({
  section: "Problem", title: "Two model families publish their training data",
  secs: 19,
  notes: "A small number of families publish the whole corpus. Pythia trained "
    + "on the Pile, OLMo 2 on OLMo-mix, and both corpora can be searched for "
    + "exact phrases. For these models, and almost no others, you can put the "
    + "data, the behaviour and the documentation on one scale and ask whether "
    + "they line up. That is the entire opening this project walks through.",
  draw: (s) => {
    const W = 3.85, Y = 1.65, H = 1.5;
    [["Training corpus", "the Pile  ·  OLMo-mix\nsearchable, exact phrase", TEAL],
     ["Model behaviour", "Pythia  ·  OLMo 2\n10 models, scored", TEAL],
     ["The datasheet", "what it says about\nsex, gender and health", TEAL],
    ].forEach(([h, b, c], i) => {
      const x = 0.55 + i * (W + 0.39);
      s.addShape(pres.ShapeType.roundRect, { x, y: Y, w: W, h: H, rectRadius: 0.07,
        fill: { color: PAPER }, line: { color: c, width: 1.4 }, objectName: `n${i}-bg` });
      s.addText(h, { x: x + 0.12, y: Y + 0.22, w: W - 0.24, h: 0.34, fontSize: 16,
        bold: true, color: INK, align: "center", isTextBox: true, margin: 0,
        objectName: `n${i}-h` });
      s.addText(b, { x: x + 0.12, y: Y + 0.62, w: W - 0.24, h: 0.7, fontSize: 12,
        color: MUT, align: "center", lineSpacing: 15, isTextBox: true, margin: 0,
        objectName: `n${i}-b` });
    });
    arrow(s, { x: 4.49, y: Y + 0.65, w: 0.42, h: 0.22, color: "9BB3BA", name: "a1" });
    arrow(s, { x: 8.73, y: Y + 0.65, w: 0.42, h: 0.22, color: "9BB3BA", name: "a2" });

    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 3.52, w: 12.2, h: 0.95,
      rectRadius: 0.07, fill: { color: "E6F6F2" }, line: { color: PASS, width: 1.3 },
      objectName: "ans-bg" });
    s.addText("“This model is biased, the bias is in its training data, and "
      + "the documentation never warned anyone.”",
      { x: 0.75, y: 3.52, w: 11.8, h: 0.95, fontSize: 19, bold: true, color: INK,
        align: "center", valign: "middle", fontFace: "Cambria", isTextBox: true,
        margin: 0, objectName: "ans" });
    s.addText("That sentence supports three actions. Getting from the last slide "
      + "to this one is the whole project.",
      { x: 0.55, y: 4.66, w: 12.2, h: 0.36, fontSize: 14, color: MUT,
        isTextBox: true, margin: 0, objectName: "foot" });
  },
});
