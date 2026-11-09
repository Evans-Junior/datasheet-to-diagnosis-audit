const K = require("./part1.js");
const { pres, S, card, stat, badge, box, arrow, note,
        INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// Split out of part13.js on 2026-11-09 so the 'Fix rounds 3-7' section
// (part13b.js) lands BEFORE Limitations instead of after it.
let s;

pres.addSection({ title: "Limitations and conclusions" });
s = S("SECTION", "Limitations and conclusions", "7.  Limitations, conclusions and what remains");
s.addText("What is still broken, what would change our mind, and the critical path", { placeholder: "body" });

// ============ 33. LIMITATIONS =================================== //
s = S("CONTENT", "Limitations and conclusions", "Limitations, in order of threat to the work");
const lims = [
  { n: 1, h: "The stimuli are author-reviewed, not clinician-verified", b: "Every number here is tier 1: checked against a guideline passage we quoted at first hand, which caught 2 rejections, 1 correction and 3 citation errors \u2014 and is still not a clinician. Tier 2 is the bar for publication and the review is scheduled, not done.", c: FAIL },
  { n: 2, h: "Seven of ten models cannot be measured at all", b: "And D057 shows the obvious elicitation fixes do not work. The open-data families are the ones the argument needs and the ones the method cannot resolve.", c: FAIL },
  { n: 3, h: "The noise floor is no longer the thin part", b: "Group 4 now holds 11 vignettes, 8 in the binary stratum and 3 in the four-option stratum, so the matched floor is estimable rather than degenerate. The resolution limit below, not the floor, is now the binding constraint.", c: TEAL },
  { n: 4, h: "The design cannot resolve small p values", b: "H1 rests on four vignette clusters, so its finest resolvable exact p is 2\u207B\u2074 = 0.0625 \u2014 alpha = .05 is unreachable by construction, not by weak effect. Group 2 is at k = 3 (0.125). No change of model improves this; only more vignettes per group will.", c: WARN },
  { n: 5, h: "The gate's verdict on Qwen is score-key dependent", b: "Sensitive under PMI, insensitive under mean log-probability. The instrument does not give one answer about its most capable model.", c: WARN },
  { n: 6, h: "Corpus provenance is not identifiable", b: "The two corpora agree at 0.976, so RQ4 cannot attribute behaviour to one of them. This is now reported as a bound rather than repaired.", c: WARN },
  { n: 7, h: "Single-token answer options cap clinical content", b: "This is what makes the gate immune to length bias rather than merely robust to it, which is a genuine strength. It also limits how much a single option can say.", c: TEAL },
  { n: 8, h: "Scope is English and single-jurisdiction", b: "All corpora and vignettes are English only, and guideline choices are single-jurisdiction where guidelines conflict. Vignettes are not patients.", c: TEAL },
  { n: 9, h: "One cluster-independence defect, found and fixed", b: "Group 2 ran at k = 4 over three constructs: G2-01 and G2-01b both tested a pregnancy test before imaging, so a resample could draw one construct twice. G2-01 is retired and Group 2 is at k = 3 \u2014 a worse resolution limit and a correct independence claim.", c: WARN },
];
lims.forEach((l, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.55 + col * 6.25, y = 1.22 + row * 1.16;
  card(s, { x, y, w: 6.05, h: 1.04, name: "lm" + i });
  badge(s, { x: x + 0.2, y: y + 0.14, n: l.n, d: 0.36, fs: 12, color: l.c, name: "lmb" + i });
  s.addText(l.h, { x: x + 0.66, y: y + 0.1, w: 5.14, h: 0.28, fontSize: 11.5, bold: true,
    color: INK, margin: 0, isTextBox: true, valign: "middle", objectName: "lmh" + i });
  s.addText(l.b, { x: x + 0.66, y: y + 0.38, w: 5.19, h: 0.62, fontSize: 9, color: MUT,
    lineSpacing: 13, margin: 0, isTextBox: true, objectName: "lmbb" + i });
});
s.addText("Items 1 and 2 are existential for the current claims. Items 3 to 6 are measurement limits with known fixes. Items 7 and 8 are scope boundaries we accept.",
  { x: 0.55, y: 6.66, w: 12.2, h: 0.3, fontSize: 11.5, italic: true, color: MUT, margin: 0, isTextBox: true });
note(s, "Order matters here. If asked which limitation worries us most, the answer is the clinician verification, because it is the only one that could invalidate the stimulus set entirely rather than merely limit what we can resolve.");

module.exports = {};
