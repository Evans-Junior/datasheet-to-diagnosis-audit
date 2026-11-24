// Builds the STEPPED deck: the same seven-minute content as the short deck,
// but split one message to a slide.
//
// WHY THIS EXISTS. `Datasheet_to_Diagnosis_7min.pptx` carries the same argument
// on seven dense slides. Each of those slides asked a listener to hold two or
// three ideas at once: the matrix AND its arithmetic, the four groups AND the
// three harness defences, two charts AND three result cards. That reads well on
// paper and badly in a room. Here every one of those parts gets its own slide,
// so the audience is only ever following one thing.
//
// NOTHING WAS CUT. The two decks say exactly the same things and quote exactly
// the same figures from the same accessors in figures.js. The short deck is
// kept because it is the better handout; this one is the better talk.
//
// Slides 1 to 16 are spoken and budgeted to 420 seconds in total, with each
// slide's budget written into its speaker notes as a [NNs] prefix. Slide 17 is
// references. Slides 18 to 21 are backup for questions and are never presented.
const K = require("../part1.js");
[// spoken, 7 minutes, one message each
 "./s01.js", "./s02.js", "./s03.js", "./s04.js", "./s05.js", "./s06.js",
 "./s07.js", "./s08.js", "./s09.js", "./s10.js", "./s11.js", "./s12.js",
 "./s13.js", "./s14.js", "./s15.js", "./s16.js",
 // not spoken
 "./s17.js",
 // backup, for questions
 "./s18.js", "./s19.js", "./s20.js", "./s21.js",
].forEach(f => require(f));

const path = require("path");
const { applyTheme } = require("../theme.js");
// Repository root, resolved against __dirname and not the working directory
// (D096): a build run from inside deck_src used to leave the tracked root copy
// stale for a day while reporting success.
const OUT = path.join(__dirname, "..", "..", "Datasheet_to_Diagnosis_7min_Stepped.pptx");

(async () => {
  await K.pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, K.THEME);
  console.log(`built ${OUT}  (${K.pres.slides.length} slides)`);
})();
