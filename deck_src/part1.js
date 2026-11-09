const pptxgen = require("pptxgenjs");

const THEME = {
  name: "Datasheet to Diagnosis",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0F3A44", lt1: "FFFFFF", dk2: "20606E", lt2: "EEF4F4",
    accent1: "2E8C9A", accent2: "00A88F", accent3: "C2503F",
    accent4: "D4941F", accent5: "6E8C94", accent6: "8E4E64",
    hlink: "2E8C9A", folHlink: "6E8C94",
  },
};

const INK = "0F3A44", MUT = "5A7883", PASS = "00A88F", FAIL = "C2503F",
      WARN = "D4941F", TEAL = "2E8C9A", PAPER = "FFFFFF", TINT = "EEF4F4",
      BERRY = "8E4E64";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Evans Kumi and Aymen Boustani";
pres.title = "From Datasheet to Diagnosis";
pres.subject = "Ethics in AI final project, research track";

const FOOT = "From Datasheet to Diagnosis  |  Kumi and Boustani  |  ECSE-557";

pres.defineSlideMaster({
  title: "TITLE_DARK", background: { color: INK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 2.1, w: 11.5, h: 1.9,
      fontSize: 42, bold: true, color: PAPER, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.9, y: 4.15, w: 11.5, h: 1.5,
      fontSize: 16, color: "BCD3D8", valign: "top" }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "SECTION", background: { color: INK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 2.7, w: 11.5, h: 1.3,
      fontSize: 38, bold: true, color: PAPER, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.9, y: 4.05, w: 11.5, h: 1.1,
      fontSize: 15, color: "BCD3D8", valign: "top" }, text: "" } },
  ],
  slideNumber: { x: 12.6, y: 7.0, fontSize: 10, color: "6E8C94", fontFace: "Calibri" },
});

pres.defineSlideMaster({
  title: "CONTENT", background: { color: PAPER },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.55, y: 0.46, w: 12.2, h: 0.72,
      fontSize: 30, bold: true, color: INK, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.55, y: 1.22, w: 12.2, h: 5.5,
      fontSize: 15, color: INK, valign: "top" }, text: "" } },
    { text: { text: FOOT, options: { x: 0.55, y: 7.0, w: 9, h: 0.3, fontSize: 9,
      color: "9BB3BA", fontFace: "Calibri", isTextBox: true } } },
  ],
  slideNumber: { x: 12.6, y: 7.0, fontSize: 10, color: "9BB3BA", fontFace: "Calibri" },
});

pres.defineSlideMaster({
  title: "CONTENT_DARK", background: { color: INK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.55, y: 0.46, w: 12.2, h: 0.72,
      fontSize: 30, bold: true, color: PAPER, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.55, y: 1.22, w: 12.2, h: 5.5,
      fontSize: 15, color: "D6E6E9", valign: "top" }, text: "" } },
    { text: { text: FOOT, options: { x: 0.55, y: 7.0, w: 9, h: 0.3, fontSize: 9,
      color: "6E8C94", fontFace: "Calibri", isTextBox: true } } },
  ],
  slideNumber: { x: 12.6, y: 7.0, fontSize: 10, color: "6E8C94", fontFace: "Calibri" },
});

function S(master, section, title) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  if (title) s.addText(title, { placeholder: "title" });
  return s;
}

function card(s, o) {
  s.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.06,
    fill: { color: o.fill || TINT }, line: { color: o.fill || TINT, width: 0 },
    objectName: (o.name || "card") + "-bg",
  });
  let yy = o.y + 0.16;
  if (o.kicker) {
    s.addText(o.kicker, { x: o.x + 0.22, y: yy, w: o.w - 0.44, h: 0.24,
      fontSize: 10, bold: true, color: o.kickerColor || TEAL, charSpacing: 1,
      margin: 0, isTextBox: true, objectName: (o.name || "card") + "-k" });
    yy += 0.26;
  }
  if (o.head) {
    s.addText(o.head, { x: o.x + 0.22, y: yy, w: o.w - 0.44, h: o.headH || 0.34,
      fontSize: o.headSize || 15, bold: true, color: o.headColor || INK,
      margin: 0, isTextBox: true, objectName: (o.name || "card") + "-h" });
    yy += (o.headH || 0.34) + 0.04;
  }
  if (o.body) {
    s.addText(o.body, { x: o.x + 0.22, y: yy, w: o.w - 0.44, h: o.y + o.h - yy - 0.14,
      fontSize: o.bodySize || 12.5, color: o.bodyColor || MUT, lineSpacing: 15,
      margin: 0, isTextBox: true, valign: "top", objectName: (o.name || "card") + "-b" });
  }
  return s;
}

function stat(s, o) {
  s.addText(o.n, { x: o.x, y: o.y, w: o.w, h: o.nh || 0.82, fontSize: o.size || 40,
    bold: true, color: o.color || TEAL, fontFace: "Cambria", margin: 0,
    isTextBox: true, align: o.align || "left", objectName: (o.name || "stat") + "-n" });
  s.addText(o.label, { x: o.x, y: o.y + (o.nh || 0.82) - 0.04, w: o.w, h: 0.3,
    fontSize: 12, bold: true, color: INK, margin: 0, isTextBox: true,
    align: o.align || "left", objectName: (o.name || "stat") + "-l" });
  if (o.sub) s.addText(o.sub, { x: o.x, y: o.y + (o.nh || 0.82) + 0.26, w: o.w, h: 0.62,
    fontSize: 10.5, color: MUT, margin: 0, isTextBox: true, lineSpacing: 13,
    align: o.align || "left", objectName: (o.name || "stat") + "-s" });
}

function badge(s, o) {
  s.addShape(pres.ShapeType.ellipse, { x: o.x, y: o.y, w: o.d || 0.42, h: o.d || 0.42,
    fill: { color: o.color || TEAL }, line: { color: o.color || TEAL, width: 0 },
    objectName: (o.name || "badge") + "-c" });
  s.addText(String(o.n), { x: o.x, y: o.y, w: o.d || 0.42, h: o.d || 0.42,
    fontSize: o.fs || 14, bold: true, color: PAPER, align: "center", valign: "middle",
    margin: 0, isTextBox: true, objectName: (o.name || "badge") + "-t" });
}

function box(s, o) {
  s.addShape(pres.ShapeType.roundRect, { x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.07,
    fill: { color: o.fill || PAPER }, line: { color: o.line || TEAL, width: o.lw || 1.25 },
    objectName: (o.name || "box") + "-r" });
  s.addText(o.t, { x: o.x + 0.06, y: o.y, w: o.w - 0.12, h: o.h, fontSize: o.fs || 12,
    bold: o.bold !== false, color: o.tc || INK, align: "center", valign: "middle",
    margin: 0, isTextBox: true, objectName: (o.name || "box") + "-t" });
}

function arrow(s, o) {
  s.addShape(pres.ShapeType.rightArrow, { x: o.x, y: o.y, w: o.w || 0.42, h: o.h || 0.2,
    fill: { color: o.color || "9BB3BA" }, line: { color: o.color || "9BB3BA", width: 0 },
    rotate: o.rotate || 0, objectName: (o.name || "arr") });
}


// ---------------------------------------------------------------------------
// D091: the tier label, rendered from the tables rather than typed per slide.
// Tier 1 numbers MAY be presented as results; the condition must travel with
// them, so this is a helper and not a sentence somebody remembers to add.
function tierBanner(s, o) {
  const F = require("./figures.js");
  const st = F.reportable().statuses.join(", ");
  const t1 = /REPORTABLE_TIER1/.test(st);
  const t2 = /REPORTABLE_TIER2/.test(st);
  const col = t2 ? PASS : (t1 ? WARN : FAIL);
  const head = t2 ? "TIER 2 \u2014 CLINICIAN-VERIFIED"
            : (t1 ? "TIER 1 RESULT \u2014 PENDING CLINICAL VALIDATION"
                  : "NOT REPORTABLE AT ANY TIER");
  const body = t2
    ? "Every vignette carries a clinician ruling."
    : (t1 ? "Every one of the 26 live vignettes is author-reviewed against a "
          + "quoted, first-hand guideline passage \u2014 the bar fixed for this "
          + "submission (prereg \u00A710, D091). Clinical review is scheduled; "
          + "the public paper waits for it."
          : "At least one vignette has never been checked against a guideline "
          + "quote, so nothing here is citable.");
  s.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h || 0.46, rectRadius: 0.05,
    fill: { color: t2 ? "E6F6F2" : (t1 ? "FDF4E3" : "FBEEEC") },
    line: { color: col, width: 0.75 }, objectName: o.name || "tier" });
  s.addText([
    { text: head + "  ", options: { bold: true, color: col } },
    { text: body, options: { color: MUT } },
  ], { x: o.x + 0.14, y: o.y + 0.04, w: o.w - 0.28, h: (o.h || 0.46) - 0.08,
       fontSize: o.fs || 9, lineSpacing: (o.fs || 9) + 2.5, margin: 0,
       valign: "middle", isTextBox: true });
}

function note(s, t) { s.addNotes(t); }

module.exports = { pres, THEME, S, card, stat, badge, box, arrow, note, tierBanner,
  INK, MUT, PASS, FAIL, WARN, TEAL, PAPER, TINT, BERRY };
