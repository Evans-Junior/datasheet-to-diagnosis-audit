// Builds the TALK deck: a 10-beat, ~15 to 20 minute presentation, plus an
// appendix for questions.
//
// WHY A SECOND DECK (D100). `Datasheet_to_Diagnosis_Presentation.pptx` is a
// 56-slide living reference: it carries every decision, every validity check
// and every table, and it is the right artefact for a reader working through
// the project. It is the wrong artefact to stand up and present, because a
// talk needs one argument carried through ten beats, not a catalogue. Both are
// built from the SAME accessors in figures.js, so a number cannot differ
// between them; only the selection and the ordering differ.
const K = require("../part1.js");
["./t1.js", "./t2.js", "./t3.js", "./t4.js", "./t5.js", "./t6.js"]
  .forEach(f => require(f));

const path = require("path");
const { applyTheme } = require("../theme.js");
// Repository root, resolved against __dirname and not the working directory,
// for the reason recorded in D096: a build run from inside deck_src used to
// leave the tracked copy stale for a day while reporting success.
const OUT = path.join(__dirname, "..", "..", "Datasheet_to_Diagnosis_Talk.pptx");

(async () => {
  await K.pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, K.THEME);
  console.log(`built ${OUT}  (${K.pres.slides.length} slides)`);
})();
