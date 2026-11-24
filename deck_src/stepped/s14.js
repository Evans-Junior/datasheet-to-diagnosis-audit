// SPOKEN 14 of 16: the resolution ladder. [30s]
//
// The slide that pre-empts the hardest question. An exact sign-flip test over
// k clusters cannot return a p below 2^-k, so with k = 4 a p of 0.0625 is the
// FLOOR of the test, not a near miss. H1 landing exactly on it means
// unresolvable, NOT absent.
//
// NOTE the exponent: 2^-k, not 2^-(k-1). H3 at k = 8 resolves to 0.00390625,
// and the assertion below refuses to build if that ever stops holding.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const H1 = F.hypothesis("H1"), H2 = F.hypothesis("H2"), H3 = F.hypothesis("H3");
const MG = F.merging();
const VG = F.vignetteGroups();

[["H1", H1], ["H2", H2], ["H3", H3]].forEach(([nm, h]) => {
  if (h.k == null) return;
  const want = Math.pow(2, -h.k);
  if (Math.abs(h.pResolution - want) > 1e-12) {
    throw new Error(`s14.js: ${nm} has k = ${h.k} and resolution ${h.pResolution}, `
      + `but 2^-${h.k} is ${want}. The exponent printed on the slide is wrong.`);
  }
});

pres.addSection({ title: "4 Limits" });
const s = S("CONTENT", "4 Limits", "What the design cannot resolve");
K.mark("ladder");

s.addText("An exact sign-flip test over k clusters cannot return a p below 2⁻ᵏ, however large the effect is.", {
  x: 0.55, y: 1.16, w: 12.2, h: 0.3, fontSize: 13, color: MUT,
  isTextBox: true, margin: 0, objectName: "sub" });

const AX_Y = 3.34, AX_X = 1.5, AX_W = 10.3, STEP = AX_W / 7;
const kx = k => AX_X + (k - 1) * STEP;

s.addShape(pres.ShapeType.line, { x: AX_X, y: AX_Y, w: AX_W, h: 0,
  line: { color: "9BB3BA", width: 1.4 }, objectName: "axis" });
for (let k = 1; k <= 8; k++) {
  const x = kx(k);
  s.addShape(pres.ShapeType.line, { x, y: AX_Y, w: 0, h: 0.11,
    line: { color: "9BB3BA", width: 1 }, objectName: `tk${k}` });
  s.addText(`k=${k}`, { x: x - 0.34, y: AX_Y + 0.14, w: 0.68, h: 0.22,
    fontSize: 10, bold: true, color: MUT, align: "center", isTextBox: true,
    margin: 0, objectName: `kl${k}` });
  const p = Math.pow(2, -k);
  s.addText(p < 0.01 ? p.toFixed(4) : p.toFixed(4).replace(/0+$/, ""),
    { x: x - 0.42, y: AX_Y + 0.36, w: 0.84, h: 0.2, fontSize: 8.5,
      color: "9BB3BA", align: "center", isTextBox: true, margin: 0,
      objectName: `pl${k}` });
}
s.addText("smallest p the test can return  →", { x: AX_X, y: AX_Y + 0.6,
  w: AX_W, h: 0.2, fontSize: 9, color: "9BB3BA", italic: true, align: "center",
  isTextBox: true, margin: 0, objectName: "axl" });

// alpha = .05 falls between k = 4 (0.0625) and k = 5 (0.03125).
const AX_A = kx(4) + STEP * 0.5;
s.addShape(pres.ShapeType.line, { x: AX_A, y: 1.84, w: 0, h: AX_Y - 1.84 + 0.12,
  line: { color: FAIL, width: 1.4, dashType: "dash" }, objectName: "alpha" });
s.addText("α = .05", { x: AX_A - 0.5, y: 1.62, w: 1.0, h: 0.22, fontSize: 10,
  bold: true, color: FAIL, align: "center", isTextBox: true, margin: 0,
  objectName: "alpha-l" });
s.addText("cannot reach .05 at any effect size", { x: AX_X - 0.2, y: 1.86, w: 3.4,
  h: 0.24, fontSize: 9.5, color: FAIL, italic: true, isTextBox: true, margin: 0,
  objectName: "alpha-lft" });
s.addText("significance reachable", { x: AX_A + 0.2, y: 1.86, w: 2.6, h: 0.24,
  fontSize: 9.5, color: PASS, italic: true, isTextBox: true, margin: 0,
  objectName: "alpha-rgt" });

const PINS = [
  [H2.k, "H2", MUT], [MG[0].nVignettes, "G2", TEAL],
  [H1.k, "H1", WARN], [VG.groups["3"].length, "G3", PASS], [H3.k, "H3", PASS],
];
PINS.forEach(([k, label, col]) => {
  const x = kx(k);
  s.addShape(pres.ShapeType.line, { x, y: AX_Y - 0.42, w: 0, h: 0.42,
    line: { color: col, width: 1.8 }, objectName: `pin-${label}` });
  s.addShape(pres.ShapeType.ellipse, { x: x - 0.065, y: AX_Y - 0.065, w: 0.13, h: 0.13,
    fill: { color: col }, line: { color: col, width: 0 }, objectName: `dot-${label}` });
  s.addText(label, { x: x - 0.4, y: AX_Y - 0.68, w: 0.8, h: 0.24, fontSize: 11,
    bold: true, color: col, align: "center", isTextBox: true, margin: 0,
    objectName: `pt-${label}` });
});

const LEG = [
  ["H2", `k = ${H2.k}  ·  one cluster, so p can never fall below ${H2.pResolution}`, MUT],
  ["G2", `k = ${MG[0].nVignettes}  ·  control + merging  ·  limit ${MG[0].pResolution}`, TEAL],
  ["H1", `k = ${H1.k}  ·  p = ${H1.txt.pExact}, exactly its own limit`, WARN],
  ["G3", `k = ${VG.groups["3"].length}  ·  the first design that can reach .05`, PASS],
  ["H3", `k = ${H3.k}  ·  equivalence supported, margin ${H3.txt.margin}`, PASS],
];
LEG.forEach(([lab, txt, col], i) => {
  const x = 0.55 + (i % 3) * 4.11, y = 4.34 + Math.floor(i / 3) * 0.34;
  s.addShape(pres.ShapeType.ellipse, { x, y: y + 0.05, w: 0.14, h: 0.14,
    fill: { color: col }, line: { color: col, width: 0 }, objectName: `lg${i}` });
  s.addText([{ text: `${lab}  `, options: { bold: true, color: INK } },
             { text: txt, options: { color: MUT } }],
    { x: x + 0.24, y, w: 3.84, h: 0.3, fontSize: 9, valign: "middle",
      isTextBox: true, margin: 0, objectName: `lgt${i}` });
});

s.addShape(pres.ShapeType.roundRect, {
  x: 0.55, y: 5.2, w: 12.23, h: 1.0, rectRadius: 0.06,
  fill: { color: "FDF4E3" }, line: { color: WARN, width: 1.1 }, objectName: "h1-bg" });
s.addText([
  { text: "So H1 is unresolvable, not absent.  ", options: { bold: true, color: WARN } },
  { text: `Its gap is ${H1.txt.delta} with a 95% interval of ${H1.txt.ci} that excludes zero, and its exact p is ${H1.txt.pExact} — the smallest number four clusters can produce. One more referral vignette takes k to 5 and the limit to 0.031.`,
    options: { color: MUT } },
], { x: 0.8, y: 5.3, w: 11.73, h: 0.82, fontSize: 12, lineSpacing: 15.5,
     valign: "middle", isTextBox: true, margin: 0, objectName: "h1" });

// 30 seconds, about 67 words.
note(s, `[30s] This pre-empts the hardest question you will get.

Our tests are exact sign-flip tests over vignette clusters, and such a test cannot return a p below two to the minus k. With four clusters the smallest possible p is 0.0625.

H1 came in at exactly 0.0625, with an interval excluding zero. Say it in these words: unresolvable, not absent. Everything left of the red line cannot reach .05 at any effect size.`);
