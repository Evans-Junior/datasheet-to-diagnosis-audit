const K = require("./part1.js");
require("./part2.js"); require("./part3.js"); require("./part3b.js"); require("./part4.js");
require("./part5.js"); require("./part6.js"); require("./part6b.js"); require("./part7.js");
require("./part8.js"); require("./part9.js"); require("./part10.js");
require("./part11.js"); require("./part12.js"); require("./part13.js"); require("./part13b.js"); require("./part13c.js");
require("./part14.js"); require("./part15.js");
const path = require("path");
const { applyTheme } = require("./theme.js");
// The repo root, not the working directory: README points readers at the deck
// there, so a build run from inside deck_src must not leave that copy stale.
const OUT = path.join(__dirname, "..", "Datasheet_to_Diagnosis_Presentation.pptx");
(async () => {
  await K.pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, K.THEME);
  console.log("built " + OUT);
})();
