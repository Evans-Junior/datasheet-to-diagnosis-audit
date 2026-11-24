// ACT 4, what follows. Messages 12 and 13, 36 seconds, then the reference
// slide, which is not spoken. The backup slides live in a5_charts.js (charts)
// and a6_backup.js (tables and limits).
const K = require("./kit.js");
const F = require("../figures.js");
const A = require("../short/acm.js");
const { pres, S, message, box, card, stat, note, tierBanner, srcLine, ink, mut,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY, GH } = K;

// ------------------------------------------------- 12. the ask, 2 clicks
message({
  section: "What follows", title: "What we are asking for",
  secs: 26, steps: 2,
  notes: "Two asks. For anyone writing a datasheet, three health-specific "
    + "fields, because the Pile measured gender and advertised medical text and "
    + "never joined them up, and that gap is a documentation gap, not a "
    + "research gap. For anyone procuring or regulating a model, one line: a "
    + "sex-specific positive control before any fairness claim is accepted. It "
    + "costs almost nothing and it is the thing that stops a blind model being "
    + "approved as a fair one.",
  draw: (s, st) => {
    s.addText("FOR ANYONE WRITING A DATASHEET " + A.m("gebru2021"),
      { x: 0.55, y: 1.25, w: 12.2, h: 0.26, fontSize: 10.5, bold: true,
        color: TEAL, charSpacing: 1.1, isTextBox: true, margin: 0, objectName: "k1" });
    [["Is there clinical text?", "and from which sources"],
     ["How are sex and gender\nrepresented?", "non-binary people as patients\nincluded, measured not assumed"],
     ["Which health uses are\nintended?", "and which are explicitly\nout of scope"],
    ].forEach(([h, b], i) => {
      const x = 0.55 + i * 4.11;
      s.addShape(pres.ShapeType.roundRect, { x, y: 1.6, w: 4.0, h: 1.7,
        rectRadius: 0.07, fill: { color: TINT }, line: { color: "CFE0E3", width: 1.2 },
        objectName: `a${i}-bg` });
      s.addText(String(i + 1), { x: x + 0.2, y: 1.72, w: 0.5, h: 0.32, fontSize: 13,
        bold: true, color: TEAL, isTextBox: true, margin: 0, objectName: `a${i}-n` });
      s.addText(h, { x: x + 0.2, y: 2.06, w: 3.6, h: 0.62, fontSize: 15, bold: true,
        color: INK, lineSpacing: 18, isTextBox: true, margin: 0, objectName: `a${i}-h` });
      s.addText(b, { x: x + 0.2, y: 2.7, w: 3.6, h: 0.5, fontSize: 11.5, color: MUT,
        lineSpacing: 14, isTextBox: true, margin: 0, objectName: `a${i}-b` });
    });

    const L = st >= 2;
    s.addText("FOR ANYONE PROCURING OR REGULATING A MODEL",
      { x: 0.55, y: 3.58, w: 12.2, h: 0.26, fontSize: 10.5, bold: true,
        color: L ? FAIL : GH.mut, charSpacing: 1.1, isTextBox: true, margin: 0,
        objectName: "k2" });
    s.addShape(pres.ShapeType.roundRect, { x: 0.55, y: 3.92, w: 12.2, h: 1.0,
      rectRadius: 0.07, fill: { color: L ? "FBEEEC" : GH.fill },
      line: { color: L ? FAIL : GH.line, width: 1.4 }, objectName: "ask2-bg" });
    s.addText("Require a sex-specific positive control before you accept any "
      + "fairness result about a model.",
      { x: 0.8, y: 3.92, w: 11.7, h: 1.0, fontSize: 19, bold: true,
        color: L ? INK : GH.ink, align: "center", valign: "middle",
        fontFace: "Cambria", isTextBox: true, margin: 0, objectName: "ask2" });
    s.addText("It costs almost nothing, and it is what stops a blind model being "
      + "approved as a fair one.",
      { x: 0.55, y: 5.04, w: 12.2, h: 0.34, fontSize: 13, color: mut(st, 2),
        align: "center", isTextBox: true, margin: 0, objectName: "ask2s" });
  },
});

// ------------------------------------------------------------ 13. close
{
  const s = S("SECTION", "Close", "Open data is necessary. It is not sufficient.");
  s.addText("Without open data we could not have shown that non-binary patients "
    + "are absent from the clinical subject position, or that two major corpora "
    + "carry nearly the same skew. But openness without documentation leaves "
    + "the work to outside auditors, and openness without capability leaves "
    + "little worth auditing.", { placeholder: "body" });
  s.addText(`Code, vignettes, every results table and ${F.decisionCount()} numbered design decisions:\n`
    + "github.com/Evans-Junior/datasheet-to-diagnosis-audit",
    { x: 0.9, y: 5.45, w: 11.5, h: 0.7, fontSize: 13, color: "8FB2BA",
      lineSpacing: 18, isTextBox: true, margin: 0, objectName: "repo" });
  note(s, "[10s] Thank you. Everything is in the repository, including the "
    + "decisions that reversed earlier conclusions. Happy to take questions.");
}

// ------------------------------------------------- references, not spoken
{
  const s = S("CONTENT", "Close", "References");
  const L = A.list();
  const half = Math.ceil(L.length / 2);
  [L.slice(0, half), L.slice(half)].forEach((col, c) => {
    s.addText(col.map(e => ({
      text: `[${e.num}] ${e.cite}`,
      options: { breakLine: true, fontSize: 8.4, color: MUT, lineSpacing: 10.6 },
    })), { x: 0.55 + c * 6.2, y: 1.25, w: 5.95, h: 5.4, isTextBox: true,
           margin: 0, valign: "top", objectName: `ref${c}` });
  });
  note(s, "[0s] Not spoken. ACM numeric order, computed from "
    + "docs/references.json rather than typed.");
}

