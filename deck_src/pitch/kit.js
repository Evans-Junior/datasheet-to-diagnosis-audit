// The build-sequence kit for the five-minute pitch deck.
//
// WHY THIS EXISTS. The ask was "one thing on a slide, and animate the rest in
// step by step". PowerPoint animations are a <p:timing> tree, and pptxgenjs
// writes no such thing: there is no API for it and hand-patching the OOXML
// would put a fragile, invisible structure into a file nobody can diff. So the
// deck uses what professional decks use instead, a BUILD SEQUENCE. A slide
// that has three parts is emitted three times, each copy showing one more
// part. Advancing the slide looks exactly like an entrance animation, works in
// PowerPoint, Keynote, Google Slides and a PDF export alike, and cannot break.
//
// The part that makes it read as animation rather than as three slides is
// GHOSTING. A part that has not arrived yet is still drawn, in a tint barely
// off the background, so nothing moves when it lights up. Without that the eye
// sees a new layout each click and the illusion is gone.
//
// A step() slide inherits the title and the section from the message it
// belongs to, so a message is one call and the steps are its content.
const K = require("../part1.js");
const { pres, S, note, INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY } = K;

// Barely-there versions of the palette, for a part that has not arrived yet.
const GH = { ink: "DFE8EB", mut: "E8EFF1", line: "ECF2F3", fill: "FBFCFC",
             tint: "F7FAFA" };

// on(step, n, live, dead) -> the live value once this step has reached n.
const on = (step, n, live, dead) => (step >= n ? live : dead);

// The colour a part should be drawn in at this step.
const ink  = (st, n) => on(st, n, INK,  GH.ink);
const mut  = (st, n) => on(st, n, MUT,  GH.mut);
const hue  = (st, n, c) => on(st, n, c, GH.ink);
const line = (st, n, c) => on(st, n, c || TEAL, GH.line);
const fill = (st, n, c) => on(st, n, c || TINT, GH.tint);

let BUDGET = 0;   // running total of the spoken seconds, checked by build.js

// A message. `secs` is what it is budgeted to say, `steps` how many clicks it
// takes. The body is called once per step with (slide, step), step starting
// at 1, and only the LAST step carries the speaker notes, so the presenter
// view does not repeat the same paragraph three times.
function message({ section, title, secs, steps = 1, master = "CONTENT",
                   notes = "", draw }) {
  BUDGET += secs;
  const made = [];
  for (let st = 1; st <= steps; st++) {
    const s = S(master, section, title);
    draw(s, st);
    if (st === steps) {
      note(s, `[${secs}s] ` + notes +
        (steps > 1 ? `\n\n(This message is ${steps} clicks. Say the line, click, `
                   + "say the next one. Nothing moves on the slide when you do.)"
                   : ""));
    } else {
      note(s, `[build ${st} of ${steps}] Click for the next part.`);
    }
    made.push(s);
  }
  return made;
}

const budget = () => BUDGET;

// How many slides are not spoken. build.js used to print a hard-coded 5, which
// was wrong the moment a backup slide was added. A note that starts "[0s]" is
// the deck's own marker for "not spoken", so count that instead of trusting a
// number typed in another file.
let NOT_SPOKEN = 0;
function counted(s, t) { if (/^\[0s\]/.test(t)) NOT_SPOKEN += 1; return note(s, t); }
const notSpoken = () => NOT_SPOKEN;

module.exports = { ...K, message, budget, note: counted, notSpoken, on, ink, mut, hue, line, fill, GH };
