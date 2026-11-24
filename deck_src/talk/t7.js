// Talk deck, references. Rendered from docs/references.json (D101), never from
// a literal, so the list on the slide and the project's sourcing record cannot
// disagree. scripts/check_references.py gates that file against the live
// vignette set before a build is worth making.
const K = require("../part1.js");
const F = require("../figures.js");
const { pres, S, card, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

const R = F.refs();
const COV = F.guidelineCoverage();

pres.addSection({ title: "References" });

// ------------------------------------------------ works cited, part 1 -----
function litSlide(title, entries, kicker) {
  const s = S("CONTENT", "References", title);
  if (kicker) {
    s.addText(kicker, { x: 0.55, y: 1.2, w: 12.2, h: 0.26, fontSize: 11,
      color: TEAL, bold: true, isTextBox: true, margin: 0, objectName: "kick" });
  }
  const top = kicker ? 1.54 : 1.26;
  const perCol = Math.ceil(entries.length / 2);
  entries.forEach((e, i) => {
    const col = Math.floor(i / perCol);
    const row = i % perCol;
    const x = 0.55 + col * 6.23;
    const h = (6.6 - top) / perCol;
    const y = top + row * h;
    const doi = e.doi ? `  doi:${e.doi}` : (e.url ? "  " + e.url : "");
    s.addText([
      { text: e.cite, options: { color: INK } },
      { text: doi, options: { color: TEAL } },
    ], { x, y, w: 5.97, h: h - 0.06, fontSize: 9, isTextBox: true, margin: 0,
         lineSpacing: 10.5, valign: "top", objectName: "ref" + i });
  });
  return s;
}

// Split so neither slide is a wall: the works the method rests on, then the
// corpora, models and the clinical-bias literature behind the hypotheses.
const METHOD = ["chang2025", "zack2024", "mcclure2021", "cirillo2020",
                "heidari2016", "dev2021", "gebru2021", "yoo2026",
                "equitriage2026", "guerra2025", "feng2023", "elazar2024",
                "bender2021"];
const DATA = ["gao2020", "biderman2022", "biderman2023", "olmo2025",
              "soldaini2024", "li2024", "liu2024", "qwen2025", "loge2021",
              "hoffmann2001", "chen2008", "samulowitz2018", "carel2014"];

const byId = Object.fromEntries(R.literature.map(e => [e.id, e]));
const missing = [...METHOD, ...DATA].filter(id => !byId[id]);
if (missing.length) {
  throw new Error(`t7.js: reference id(s) not in docs/references.json: ${missing}`);
}
const unlisted = R.literature.map(e => e.id)
  .filter(id => !METHOD.includes(id) && !DATA.includes(id));
if (unlisted.length) {
  // A work in the file but on no slide is a citation the audience never sees.
  throw new Error(`t7.js: reference(s) in references.json but on no slide: `
    + `${unlisted.join(", ")}. Add them to METHOD or DATA.`);
}

{
  const s = litSlide("References: method, measurement and prior work",
    METHOD.map(id => byId[id]),
    "Design, sex and gender standards, documentation, and the audits this study positions against");
  note(s, "Do not read this out. It is here so the claims on the earlier slides "
   + "are checkable, and so the three works that matter most can be pointed at "
   + "if asked: Chang et al. for the paired-prompt design, McClure et al. for "
   + "the sex and gender separation the whole study rests on, and Yoo for the "
   + "independent peer-reviewed convergence on the noise floor.");
}

{
  const s = litSlide("References: corpora, models and the clinical literature",
    DATA.map(id => byId[id]),
    "The two open pipelines, the closed comparator, the corpus instrument, and the documented disparities behind H1 and H2");
  note(s, "The bottom four are the clinical-bias literature that gives H1 its "
   + "pre-registered direction. All four were verified against CrossRef by "
   + "scripts/verify_dois.py; the raw response is in "
   + "results/tables/doi_verification.json.");
}

// ------------------------------------- clinical guidelines, with the gap --
{
  const s = S("CONTENT", "References",
    "Clinical guidelines: one per vignette, quoted at first hand");

  // THREE columns, not two. At 15 verified the two-column list ended at y 5.25
  // and the gap card below it fitted. Every vignette now carries a citation, so
  // the same code ran 25 entries down to y 7.5 on a 7.5in slide: three rows off
  // the canvas and eight overlapping the card. The column count has to follow
  // the data, because the data is what moved.
  const ver = F.guidelines("verified");
  const NCOL = 3, CW = 3.92, FS = 7.2, LS = 8.8, ROW = 0.524, TOP = 1.5;
  const perCol = Math.ceil(ver.length / NCOL);

  // Size the row against the LONGEST entry, not against a guess. The ACR-SPR
  // parameter carries a full author list and runs to 300 characters, two and a
  // half times the median, so a height that suits the median clips exactly one
  // box on the slide and nothing says so.
  const widest = ver.reduce((m, g) => Math.max(m,
    (g.vignettes.join(", ") + "  " + g.cite +
     (g.doi ? "  doi:" + g.doi : "")).length), 0);
  const perLine = CW / (0.5 * FS / 72);
  const needed = Math.ceil(widest / perLine) * (LS / 72);
  if (needed > ROW - 0.02) throw new Error(
    "t7.js: the longest citation is " + widest + " characters, which needs " +
    needed.toFixed(2) + "in but the row gives " + (ROW - 0.02).toFixed(2) +
    "in. Drop the font size or add a column.");

  ver.forEach((g, i) => {
    const col = Math.floor(i / perCol), row = i % perCol;
    const x = 0.55 + col * 4.18;
    const h = ROW;
    const y = TOP + row * h;
    s.addText([
      { text: g.vignettes.join(", ") + "  ", options: { bold: true, color: TEAL } },
      { text: g.cite, options: { color: INK } },
      { text: g.doi ? `  doi:${g.doi}` : "", options: { color: MUT } },
    ], { x, y, w: CW, h: h - 0.02, fontSize: FS, isTextBox: true, margin: 0,
         lineSpacing: LS, valign: "top", objectName: "g" + i });
  });
  const listBottom = TOP + perCol * ROW;
  if (listBottom > 6.3) throw new Error(
    "t7.js: the guideline list ends at y " + listBottom.toFixed(2) +
    ", which leaves no room for the citation-gap card. Add a column.");

  s.addText(`${COV.verified} of ${COV.total} live vignettes carry a formal citation of record`,
    { x: 0.55, y: 1.2, w: 12.2, h: 0.26, fontSize: 11, color: TEAL, bold: true,
      isTextBox: true, margin: 0, objectName: "gk" });

  // The honest part. A reference list that silently drops ten of twenty-five
  // reads as a complete one, so the remainder is named rather than omitted.
  const rest = [...F.guidelines("identifier_only"), ...F.guidelines("pending")];
  const restVign = rest.reduce((a, g) => a.concat(g.vignettes), []);
  const nGap = COV.identifierOnly + COV.pending;
  // The card stays on the slide when the gap closes. A reference list that
  // quietly stops disclosing its own gap reads the same whether the gap is zero
  // or merely unreported, so the zero is stated.
  card(s, { x: 0.55, y: 6.32, w: 12.2, h: nGap ? 1.24 : 0.56, fill: "FDF4E3",
    name: "gap",
    kicker: "WHAT IS NOT YET IN FORMAL CITATION FORM, STATED RATHER THAN OMITTED",
    kickerColor: WARN,
    head: nGap
      ? `${nGap} vignettes: ${restVign.join(", ")}`
      : `None. All ${COV.total} carry a written citation of record.`,
    headH: 0.3, headSize: 11.5,
    body: nGap
      ? `Each carries its governing passage quoted at first hand in `
        + `docs/vignettes_compendium.md, and each is author-reviewed against `
        + `that quote. ${COV.identifierOnly} have a named guideline identifier `
        + `(NICE NG226, NG153, NG240/NG91) but no written citation; `
        + `${COV.pending} have neither yet. G3-07's governing sentence has not `
        + `been read at first hand at all and is flagged in the compendium.`
      : ``,
    bodySize: 10 });
  note(s, nGap
    ? "If asked why some vignettes have no formal citation: they are the "
    + "noise-baseline items added late, plus two Group 3 additions. Every one "
    + "is author-reviewed against a passage quoted at first hand in the "
    + "compendium, so they are sourced; what is missing is the written "
    + "citation, which is bookkeeping rather than evidence."
    : "The gap closed on 2026-11-17. Ten citations were written up, and three "
    + "wrong attributions were corrected: G3-07 went to NICE NG185, whose PDF "
    + "had been in papers/ the whole time; G3-01's reference answer to NG118, "
    + "with Q-Pain keeping only the invariance warrant; G2-01b to the ACR-SPR "
    + "parameter after D088. The gap was always bibliographic. Every reference "
    + "answer was quoted at first hand throughout.");
}

module.exports = {};
