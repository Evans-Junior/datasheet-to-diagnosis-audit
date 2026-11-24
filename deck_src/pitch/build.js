// Builds the FIVE-MINUTE PITCH deck.
//
// WHAT IS DIFFERENT ABOUT THIS ONE. The 7-minute decks carry the full
// argument. This one carries the pitch: thirteen messages, one idea each, and
// nothing on a slide that the speaker is not saying out loud at that moment.
// Where a message genuinely has two or three parts, the slide is emitted once
// per part as a build sequence, so advancing it reads as an animation. See
// kit.js for why it is done that way and not with <p:timing>.
//
// Every number is read through ../figures.js from results/tables. Nothing on
// any slide is typed, which is the rule that keeps this deck from drifting
// away from the paper the way the first deck once did (D095).
const K = require("./kit.js");

// Sections must exist before the first addSlide that names one.
["Open", "Problem", "Method", "Results", "What follows", "Close", "Backup"]
  .forEach(title => K.pres.addSection({ title }));

require("./a1_problem.js");
require("./a2_method.js");
require("./a3_results.js");
require("./a4_close.js");
require("./a5_charts.js");   // chart backups, not spoken
require("./a6_backup.js");   // table backups and the limits, not spoken

const path = require("path");
const { applyTheme } = require("../theme.js");
// D096: resolve against __dirname, never the working directory.
const OUT = path.join(__dirname, "..", "..", "Datasheet_to_Diagnosis_5min_Pitch.pptx");

const SPOKEN = K.budget() + 8 + 10;    // + the title slide and the close
// The title slide was budgeted 12s and does not need it: the deck's first
// real sentence is on the slide after it. The 4s went to the design-context
// material the report rubric asks for by name.
const LIMIT = 300;

(async () => {
  await K.pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, K.THEME);
  console.log(`built ${OUT}`);
  console.log(`  ${K.pres.slides.length} slides, of which the last ${K.notSpoken()} are not spoken`);
  console.log(`  spoken budget: ${SPOKEN}s of ${LIMIT}s`);
  if (SPOKEN > LIMIT) {
    console.error(`  OVER BUDGET by ${SPOKEN - LIMIT}s. Cut a message, do not `
      + "speak faster.");
    process.exit(1);
  }
})();
