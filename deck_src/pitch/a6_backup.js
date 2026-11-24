// The backup slides that are not charts. Split out of a4_close.js when the
// chart backups were added (D125), so that the order in build.js is the order
// a presenter flips through.
//
// THE TWO PER-MODEL TABLES ARE GONE (D126). One listed every model's Group 2
// margin against its floor and the other the three survivors against both
// floors, which is exactly what the charts on the slides before plot, down to
// the same numbers. Two renderings of one result is not a backup, it is a
// thing to lose your place in. The charts' data labels went to four decimals
// in the same change, so nothing the tables carried was lost with them.
//
// What is left is the corpus argument, which the charts cannot make on their
// own, and the limits.
const K = require("./kit.js");
const F = require("../figures.js");
const path = require("path");
const fs = require("fs");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, TINT } = K;
{
  const s = S("CONTENT", "Backup", "Backup: why the two corpora cannot be told apart");
  const CA = F.corpusAgreement();
  card(s, { x: 0.55, y: 1.3, w: 12.2, h: 1.5, fill: TINT, name: "h4",
    kicker: "RQ4, NOT IDENTIFIABLE", kickerColor: WARN,
    head: `The Pile and OLMo-mix agree on which concepts are gendered: Spearman ρ = ${CA.rho.toFixed(3)}`,
    headSize: 17, headH: 0.42,
    body: "Both are built largely from the same web text: OLMo-mix draws most of "
        + "its tokens from DCLM, a filtered Common Crawl corpus, and the Pile "
        + "carries a Common Crawl subset of its own. With two corpora this alike "
        + "an n-gram count cannot attribute a model's gap to one rather than the "
        + "other." });
  s.addText("A model's own corpus predicted its gaps better than a corpus it "
    + "never saw in only 2 of 9 cases. We report a limit of identifiability, "
    + "not a causal link: the skew describes how English talks about illness "
    + "rather than one training set.",
    { x: 0.55, y: 3.0, w: 12.2, h: 0.8, fontSize: 14, color: INK, lineSpacing: 19,
      isTextBox: true, margin: 0, objectName: "b" });
  note(s, "[0s] Backup. The honest answer to 'so does the data cause it?' "
    + "The slide after this one is the evidence for it.");
}

// --------------------------------- the same claim, concept by concept
// D126. The slide above asserts that the two corpora carry the same skew.
// This one shows it, which is what the correlation is a summary OF. It sits
// here rather than with the four result charts because it is the second half
// of that argument and a presenter reaches it by flipping forward, not by
// hunting.
{
  const CD = F.corpusSkewPairs();
  const CA = F.corpusAgreement();
  const s = S("CONTENT", "Backup",
    "Chart: the same concepts lean the same way in both corpora");

  // The paper's Figure A1, redrawn for a projector by
  // scripts/build_slide_corpora_figure.py. It replaces the paired-bar chart
  // this slide used to carry, at the authors' request: the scatter shows the
  // agreement as a shape, a cloud sitting on the diagonal, where the bars
  // made the reader compare sixteen lengths two at a time.
  //
  // The image is GENERATED from results/tables by the same function that draws
  // the appendix figure, so the slide and the paper cannot disagree. Rebuild
  // it whenever the corpus tables change; the build fails below if it is
  // missing rather than shipping a deck with a hole in it.
  const CORPORA = path.join(__dirname, "..", "..", "results", "figures",
                            "slides", "fig_corpora_slide.png");
  if (!fs.existsSync(CORPORA)) {
    throw new Error("a6_backup.js: " + CORPORA + " is missing.\n" +
      "  Run: .venv/bin/python scripts/build_slide_corpora_figure.py");
  }
  s.addImage({ path: CORPORA, x: 0.62, y: 1.26, w: 5.62, h: 4.96,
               objectName: "corpora" });
  s.addText("Each dot is one clinical concept. Above zero the concept is "
    + "written about female patients more often than male ones, below zero "
    + "the reverse, after correcting for how often each gender is written "
    + "about at all. The dashed line is perfect agreement between the two "
    + "corpora, and every concept sits on it.",
    { x: 0.62, y: 6.26, w: 5.62, h: 0.62, fontSize: 10.5, color: MUT,
      lineSpacing: 13, isTextBox: true, margin: 0, objectName: "axis" });

  card(s, { x: 6.55, y: 1.26, w: 6.2, h: 2.4, fill: TINT, name: "p1",
    kicker: "THIS IS THE AGREEMENT", kickerColor: TEAL,
    head: `Spearman rho = ${CA.rho.toFixed(3)}`, headSize: 17, headH: 0.42,
    body: `Over ${CA.n} concepts. The slide before gives that number; this is `
        + "the pattern it summarises. Two corpora built largely from the same "
        + "web text do not provide two independent readings of how English "
        + "writes about illness." });
  // Both halves of this card were typed once and one of them was false. The
  // rankings are NOT identical: rho = 0.976 over 8 concepts is arithmetically
  // one adjacent pair out of place, and it is asthma against type 2 diabetes.
  // Naming concepts by hand is how a slide goes stale, so both the extremes
  // and the swap are derived from the rows.
  const male = CD.slice(0, 2).map(r => r.concept);
  const female = CD.slice(-2).reverse().map(r => r.concept);
  const rank = (key) => {
    const order = CD.slice().sort((a, b) => a[key] - b[key]).map(r => r.concept);
    return Object.fromEntries(order.map((c, i) => [c, i]));
  };
  const ro = rank("olmo"), rp = rank("pile");
  const moved = CD.map(r => r.concept).filter(c => ro[c] !== rp[c]);
  const ranking = moved.length === 0
    ? "The two rankings are identical."
    : moved.length === 2
      ? `The two rankings differ by one pair: ${moved[0]} and ${moved[1]} `
        + "change places, and nothing else moves."
      : `The two rankings differ on ${moved.length} of ${CD.length} concepts.`;

  const cap = s0 => s0.charAt(0).toUpperCase() + s0.slice(1);
  card(s, { x: 6.55, y: 3.84, w: 6.2, h: 2.5, fill: "FDF4E3", name: "p2",
    kicker: "AND IT IS NOT NOISE", kickerColor: WARN,
    head: `${cap(male.join(" and "))} lean male, `
        + `${female.join(" and ")} lean female`,
    headSize: 13, headH: 0.86,
    body: ranking + " That is a real pattern in how illness gets written "
        + "about, which is what makes it worth auditing and what makes it "
        + "impossible to pin on one dataset." });
  note(s, "[0s] Backup chart. Use it straight after the slide before: they "
    + "agree because they are nearly the same text. Say the direction out "
    + "loud, because the axis is signed and the sign is the whole point: "
    + "left is male-leaning, right is female-leaning. If anyone asks what "
    + "rho = 0.976 means concretely, it is one adjacent pair out of place in "
    + "eight, which the second card names.");
}
// THE LIMITS SLIDE IS OFF (D131).
//
// The authors asked for the corpus bias chart to take this slide's place at
// the end of the deck, so the deck now finishes on the chart. The code is
// kept rather than deleted because nothing in this repository is committed
// yet and a deleted block would be unrecoverable: set INCLUDE_LIMITS to true
// and the slide comes back exactly as it was, as the last slide.
//
// Worth knowing before you leave it off: this slide was the prepared answer
// to 'did you check X?', it costs no spoken seconds, and the same five
// limitations are in the paper's Limitations section either way.
const INCLUDE_LIMITS = false;
if (INCLUDE_LIMITS) {
  const s = S("CONTENT", "Backup", "Backup: what this study cannot tell you");
  [["The vignettes are not clinician-validated.",
    "Author-reviewed against a guideline passage quoted at first hand, but no clinician has signed them off, so everything is reported at tier 1."],
   ["It is small where it matters most.",
    "With three to eight vignettes per test the smallest attainable p-value lies between 0.125 and 0.004, and several results sit exactly at that limit."],
   ["Fixed options, not free text.",
    "We read the probability of each answer option, which is deterministic but less realistic than an open conversation."],
   ["Exact-phrase counts are not meaning.",
    "They miss paraphrase and pronoun ambiguity, and only the first training stage of OLMo 2 is searchable."],
   ["English only, one jurisdiction.",
    "Where national guidelines disagree we followed one rather than reconciling them."],
  ].forEach(([h, b], i) => {
    const y = 1.28 + i * 1.08;
    s.addText(h, { x: 0.55, y, w: 5.3, h: 0.5, fontSize: 14, bold: true, color: INK,
      lineSpacing: 17, isTextBox: true, margin: 0, objectName: `l${i}-h` });
    s.addText(b, { x: 6.0, y, w: 6.75, h: 0.92, fontSize: 12, color: MUT,
      lineSpacing: 15, isTextBox: true, margin: 0, objectName: `l${i}-b` });
  });
  note(s, "[0s] Backup. Say these before you are asked, if there is time.");
}
