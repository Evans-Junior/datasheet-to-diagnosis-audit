// SHORT deck, slide 8: the numbered reference list, ACM Reference Format.
//
// Not spoken. It exists so that every bracketed number on slides 1 to 7
// resolves, which is what makes the markers worth using at all. The list and
// the markers come from the same sort in acm.js, so they cannot disagree.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;
const A = require("./acm.js");

const L = A.list();
const GC = F.guidelineCoverage();

const s = S("CONTENT", "4 Limits", "References");
K.mark("refs");

s.addText("ACM Reference Format, numbered alphabetically by first author. Rendered from docs/references.json, so a number on a slide and its entry here cannot drift apart.", {
  x: 0.55, y: 1.12, w: 12.2, h: 0.22, fontSize: 9, color: MUT, italic: true,
  isTextBox: true, margin: 0, objectName: "sub" });

// Two columns, split so the left holds the first half.
const half = Math.ceil(L.length / 2);
const COLS = [L.slice(0, half), L.slice(half)];
const CX = [0.55, 6.74], CW = 6.0;

COLS.forEach((col, ci) => {
  const runs = [];
  col.forEach((e, i) => {
    runs.push({ text: `[${e.num}] `, options: { bold: true, color: TEAL } });
    // breakLine belongs INSIDE options. Spread onto the run object it is
    // silently ignored, and all 13 entries render as one paragraph.
    runs.push({ text: e.cite,
                options: { color: MUT, breakLine: i < col.length - 1 } });
  });
  s.addText(runs, { x: CX[ci], y: 1.42, w: CW, h: 4.0, fontSize: 8,
    lineSpacing: 11, paraSpaceAfter: 3.5, valign: "top", isTextBox: true,
    margin: 0, objectName: `refcol${ci}` });
});

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.62, w: 12.2, h: 0.92, rectRadius: 0.06,
  fill: { color: TINT }, line: { color: TINT, width: 0 }, objectName: "gl-bg" });
s.addText([
  { text: "CLINICAL GUIDELINES OF RECORD   ", options: { bold: true, color: TEAL, charSpacing: 1 } },
  { text: `Each vignette is written against a quoted passage from a named guideline. Of ${GC.total} vignette-guideline pairs, ${GC.verified} carry a verified citation of record, ${GC.identifierOnly} are identified but not read at first hand, and ${GC.pending} are pending. The full list with DOIs is in docs/references.json and on the reference deck; it is not reproduced here, because an incomplete guideline list on a slide reads as a complete one.`,
    options: { color: MUT } },
], { x: 0.77, y: 5.70, w: 11.76, h: 0.76, fontSize: 9, lineSpacing: 11.5,
     valign: "top", isTextBox: true, margin: 0, objectName: "gl-b" });

note(s, `Not spoken. Leave it up during questions.

If anyone asks about guideline provenance, the bottom band is the honest answer: ${GC.verified} of ${GC.total} vignette-guideline pairs have a citation we have read at first hand, ${GC.identifierOnly} are identified but not yet read, and ${GC.pending} are pending. That gap is why this is Tier 1 and not Tier 2.`);
