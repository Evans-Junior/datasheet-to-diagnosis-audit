const K = require("./part1.js");
require("./part2.js"); require("./part3.js"); require("./part3b.js"); require("./part4.js");
require("./part5.js"); require("./part6.js"); require("./part6b.js"); require("./part7.js");
require("./part8.js"); require("./part9.js"); require("./part10.js");
require("./part11.js"); require("./part12.js"); require("./part13.js"); require("./part13b.js"); require("./part13c.js");
require("./part14.js"); require("./part15.js");
const { applyTheme } = require("/Users/evanskumi/.claude/skills/synced/04e3f3bb-ceb9-4f3f-8abc-2b91f6fdb0d5_c2db35a4-b59a-426c-bad1-90836548e9ef/pptx/scripts/apply_theme.js");
const OUT = "Datasheet_to_Diagnosis_Presentation.pptx";
(async () => {
  await K.pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, K.THEME);
  console.log("built " + OUT);
})();
