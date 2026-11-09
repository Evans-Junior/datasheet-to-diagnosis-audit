const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// ============ 1. TITLE =========================================== //
pres.addSection({ title: "Opening" });
let s = S("TITLE_DARK", "Opening", "From Datasheet to Diagnosis");
s.addText("Tracing gender bias through open training-data pipelines into LLM health advice",
  { placeholder: "body" });
s.addText("Evans Kumi  and  Aymen Boustani", { x: 0.9, y: 5.55, w: 11.5, h: 0.3,
  fontSize: 14, bold: true, color: PAPER, margin: 0, isTextBox: true });
s.addText("McGill University  ·  MSc Intelligent Systems  ·  ECSE-557 Ethics in Artificial Intelligence",
  { x: 0.9, y: 5.88, w: 11.5, h: 0.3, fontSize: 11.5, color: "8EB0B8", margin: 0, isTextBox: true });
s.addText("Living document  ·  last updated 4 November 2026", { x: 0.9, y: 6.4, w: 11.5, h: 0.3,
  fontSize: 10.5, italic: true, color: WARN, margin: 0, isTextBox: true });
note(s, "This deck is the running record of the project. It is updated whenever something critical changes, and every slide carries the date of the run it reports. All model-side numbers remain provisional until a clinician passes the vignettes.");

// ============ 2. EXECUTIVE SUMMARY =============================== //
s = S("CONTENT", "Opening", "The project in one slide");
card(s, { x: 0.55, y: 1.25, w: 12.2, h: 1.0, fill: INK,
  head: "Most audits can prove a model is biased. None can say where the bias came from, because the training data is closed.",
  headColor: PAPER, headSize: 15.5, headH: 0.62, name: "sum-top" });
const sum = [
  { n: 1, h: "The opening", b: "Pythia and OLMo 2 publish their full training corpora, queryable by exact n-gram. For these models the data and the behaviour can be put side by side." },
  { n: 2, h: "The instrument", b: "25 guideline-sourced clinical vignettes expanded to 624 prompts, a measured noise floor per model, and a pre-registered analysis plan frozen before scoring." },
  { n: 3, h: "The result", b: "The chain can be completed, but not yet closed. Three of ten models can do the clinical task. Corpus provenance turns out not to be identifiable between these two corpora." },
  { n: 4, h: "The contribution", b: "A working instrument, a pre-registered null, and a measured account of exactly where the datasheet to diagnosis chain breaks." },
];
sum.forEach((c, i) => {
  const x = 0.55 + i * 3.1;
  card(s, { x, y: 2.5, w: 2.85, h: 2.25, name: "sum" + i });
  badge(s, { x: x + 0.22, y: 2.68, n: c.n, name: "sumb" + i });
  s.addText(c.h, { x: x + 0.76, y: 2.68, w: 1.95, h: 0.42, fontSize: 13, bold: true,
    color: INK, margin: 0, isTextBox: true, valign: "middle", objectName: "sumh" + i });
  s.addText(c.b, { x: x + 0.22, y: 3.22, w: 2.42, h: 1.4, fontSize: 11.5, color: MUT,
    lineSpacing: 14, margin: 0, isTextBox: true, objectName: "sumbody" + i });
});
card(s, { x: 0.55, y: 5.0, w: 12.2, h: 1.42, fill: TINT,
  kicker: "THE ONE-SENTENCE VERSION", kickerColor: BERRY, name: "sum-one" });
s.addText([
  { text: "The clinical guidance is more inclusive than the training data can support. ", options: { bold: true, color: INK } },
  { text: "Two of our source guidelines explicitly require care for non-binary and trans patients, and the phrase ", options: { color: MUT } },
  { text: '"the non-binary patient"', options: { color: INK, fontFace: "Courier New" } },
  { text: " occurs ", options: { color: MUT } },
  { text: "zero times", options: { bold: true, color: FAIL } },
  { text: " in either corpus.", options: { color: MUT } },
], { x: 0.77, y: 5.44, w: 11.75, h: 0.9, fontSize: 14, lineSpacing: 19, margin: 0, isTextBox: true });
note(s, "Lead with the closed-data problem, then the opening that makes this project possible, then be honest that the chain is not yet closed. The one-sentence version at the bottom is the line to repeat if you only get one sentence.");

// ============ 3. ROADMAP ========================================= //
s = S("CONTENT", "Opening", "What this deck covers");
const road = [
  { n: 1, h: "The problem and objective", b: "Why output-only audits stop at the model boundary, and the six research questions." },
  { n: 2, h: "Related work", b: "What the literature established, and the four places it directly changed our design." },
  { n: 3, h: "Methodology", b: "The vignette groups, the prompt grid, the invariance rule, scoring, statistics and the gate." },
  { n: 4, h: "Results and analysis", b: "The gate, the hypotheses, the exploratory finding, scale, linkage, representation and documentation." },
  { n: 5, h: "Instrument fix round 1", b: "A measurement error found on 3 November, the four results it moved, and how tuning stayed disclosed." },
  { n: 6, h: "Limitations and conclusions", b: "What is still broken, what would change our mind, and what remains to be done." },
];
road.forEach((c, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.55 + col * 6.25, y = 1.4 + row * 1.78;
  card(s, { x, y, w: 6.05, h: 1.56, name: "rd" + i });
  badge(s, { x: x + 0.24, y: y + 0.26, n: c.n, d: 0.46, fs: 15, name: "rdb" + i });
  s.addText(c.h, { x: x + 0.86, y: y + 0.24, w: 5.0, h: 0.4, fontSize: 15, bold: true,
    color: INK, margin: 0, isTextBox: true, valign: "middle", objectName: "rdh" + i });
  s.addText(c.b, { x: x + 0.86, y: y + 0.68, w: 4.95, h: 0.76, fontSize: 12, color: MUT,
    lineSpacing: 14.5, margin: 0, isTextBox: true, objectName: "rdbb" + i });
});
note(s, "Six sections. Sections 1 to 3 are stable. Sections 4 and 5 change as runs complete, and section 6 is the part to revisit before every supervisor meeting.");

// ============ SECTION DIVIDER: PROBLEM =========================== //
pres.addSection({ title: "Problem and objective" });
s = S("SECTION", "Problem and objective", "1.  The problem, and the objective");
s.addText("Why an audit that can only see outputs cannot support an intervention", { placeholder: "body" });

// ============ 4. THE PROBLEM, with diagram ======================= //
s = S("CONTENT", "Problem and objective", "Existing audits stop at the model boundary");
s.addText("Gender bias in clinical LLM output is a settled empirical question. Zack et al. [24] showed GPT-4 reproduces racial and gender patterns in clinical vignettes. Chang et al. [3] found anti-LGBTQIA+ bias across four models. Two 2026 emergency-triage audits [9, 23] replicate it at scale.",
  { x: 0.55, y: 1.25, w: 12.2, h: 0.72, fontSize: 14, color: INK, lineSpacing: 18, margin: 0, isTextBox: true });

// --- diagram: closed pipeline (top) vs open pipeline (bottom)
card(s, { x: 0.55, y: 2.1, w: 12.2, h: 1.95, fill: "FBEEEC", name: "closed" });
s.addText("THE USUAL SITUATION", { x: 0.8, y: 2.26, w: 4, h: 0.26, fontSize: 10, bold: true,
  color: FAIL, charSpacing: 1, margin: 0, isTextBox: true });
box(s, { x: 0.8, y: 2.64, w: 2.3, h: 0.92, t: "Training data\nclosed", fill: "F2F2F2", line: "C4C4C4", tc: "8A8A8A", name: "c1" });
arrow(s, { x: 3.25, y: 3.0, w: 0.5, h: 0.2, color: "C4C4C4", name: "ca1" });
box(s, { x: 3.95, y: 2.64, w: 2.3, h: 0.92, t: "Model", fill: PAPER, line: TEAL, name: "c2" });
arrow(s, { x: 6.4, y: 3.0, w: 0.5, h: 0.2, color: TEAL, name: "ca2" });
box(s, { x: 7.1, y: 2.64, w: 2.3, h: 0.92, t: "Biased advice", fill: PAPER, line: TEAL, name: "c3" });
s.addText("Audits can measure here", { x: 3.95, y: 3.62, w: 5.45, h: 0.26, fontSize: 10,
  italic: true, color: TEAL, align: "center", margin: 0, isTextBox: true });
s.addText([{ text: "Conclusion available:  ", options: { color: MUT } },
           { text: '"the model is biased."', options: { bold: true, color: FAIL } },
           { text: "  Supports no intervention, because the cause is unreachable.", options: { color: MUT } }],
  { x: 9.65, y: 2.78, w: 2.9, h: 1.1, fontSize: 11.5, lineSpacing: 14, margin: 0, isTextBox: true, valign: "middle" });

card(s, { x: 0.55, y: 4.2, w: 12.2, h: 1.95, fill: "E6F5F2", name: "open" });
s.addText("OUR STARTING POINT", { x: 0.8, y: 4.36, w: 4, h: 0.26, fontSize: 10, bold: true,
  color: PASS, charSpacing: 1, margin: 0, isTextBox: true });
box(s, { x: 0.8, y: 4.74, w: 2.3, h: 0.92, t: "Training data\npublished, queryable", fill: PAPER, line: PASS, fs: 11, name: "o1" });
arrow(s, { x: 3.25, y: 5.1, w: 0.5, h: 0.2, color: PASS, name: "oa1" });
box(s, { x: 3.95, y: 4.74, w: 2.3, h: 0.92, t: "Model", fill: PAPER, line: PASS, name: "o2" });
arrow(s, { x: 6.4, y: 5.1, w: 0.5, h: 0.2, color: PASS, name: "oa2" });
box(s, { x: 7.1, y: 4.74, w: 2.3, h: 0.92, t: "Advice", fill: PAPER, line: PASS, name: "o3" });
s.addText("Measurable end to end", { x: 0.8, y: 5.72, w: 8.6, h: 0.26, fontSize: 10,
  italic: true, color: PASS, align: "center", margin: 0, isTextBox: true });
s.addText([{ text: "Question available:  ", options: { color: MUT } },
           { text: "does the skew in the data predict the gap in the advice?", options: { bold: true, color: INK } }],
  { x: 9.65, y: 4.88, w: 2.9, h: 1.1, fontSize: 11.5, lineSpacing: 14, margin: 0, isTextBox: true, valign: "middle" });

s.addText("A third leg makes it an ethics claim rather than a measurement: we also read the datasheets, to ask whether the documentation disclosed the risk the data and the models demonstrate. That is what makes the title literal.",
  { x: 0.55, y: 6.3, w: 12.2, h: 0.5, fontSize: 12.5, italic: true, color: MUT, lineSpacing: 15, margin: 0, isTextBox: true });
note(s, "The top row is every audit in the literature. The bottom row is what open corpora make possible. The distinction to stress is that we are not claiming a better bias measurement, we are claiming a reachable cause.");

module.exports = {};
