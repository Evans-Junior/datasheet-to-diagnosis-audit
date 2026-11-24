// Builds the SHORT deck: a seven-slide, seven-minute defence talk, a reference
// slide, and four backup slides for questions.
//
// WHY A THIRD DECK. `Datasheet_to_Diagnosis_Presentation.pptx` is the 56-slide
// reference and `Datasheet_to_Diagnosis_Talk.pptx` is the 15-to-20 minute
// version. Neither fits a seven-minute slot: cutting the talk deck down loses
// the positive-control argument, which is the one thing that cannot be left
// out, because without it every other number reads as a null result.
//
// SLIDES 1-7 ARE SPOKEN and are budgeted to 420 seconds in total. The budget
// is written into each slide's speaker notes as a [NNs] prefix. Slides 8 to 12
// are never presented; they exist so that a question is answered by turning to
// a slide rather than from memory.
//
// All three decks read the SAME accessors in figures.js, so a figure cannot
// differ between them. This deck additionally uses short/acm.js for numbered
// citations, which is presentation only and changes no figure.
const K = require("../part1.js");
[// spoken, 7 minutes
 "./s1.js", "./s2.js", "./s3.js", "./s4.js", "./s5.js", "./s6.js", "./s7.js",
 // not spoken
 "./s8.js",
 // backup, for questions
 "./s9.js", "./s10.js", "./s11.js", "./s12.js",
].forEach(f => require(f));

const path = require("path");
const { applyTheme } = require("../theme.js");
// Repository root, resolved against __dirname and not the working directory
// (D096): a build run from inside deck_src used to leave the tracked root copy
// stale for a day while reporting success.
const OUT = path.join(__dirname, "..", "..", "Datasheet_to_Diagnosis_7min.pptx");

(async () => {
  await K.pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, K.THEME);
  console.log(`built ${OUT}  (${K.pres.slides.length} slides)`);
})();
