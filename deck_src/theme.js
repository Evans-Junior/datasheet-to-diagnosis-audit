// Write the deck's own colour scheme into ppt/theme/theme1.xml, and refuse to
// ship a deck PowerPoint would offer to repair.
//
// WHY THIS EXISTS. pptxgenjs sets the theme's two fonts from `pres.theme` but
// hard-codes Office's palette, so every `pres.SchemeColor` reference in parts 1
// to 15 resolves to Office blue and orange until the twelve slots in theme1.xml
// are replaced. The deck is written first and patched here, because pptxgenjs
// has no API for the colour scheme.
//
//   const { applyTheme } = require("./theme.js");
//   await pres.writeFile({ fileName: OUT });
//   await applyTheme(OUT, THEME);          // THEME.name + THEME.colors
//
// Two guards, both for faults that are silent at build time and loud when the
// file is opened:
//
//   1. A scheme colour handed to an option that takes hex only is written out as
//      <a:srgbClr val="bg2"/>, which is not a colour. pptxgenjs does not warn.
//   2. A dash option is passed through unchecked, and an array arrives as
//      "solid,dash". PowerPoint treats either as a damaged part.
//
// Both throw before anything is written, so a failed run leaves the previous
// deck intact rather than replacing it with one that will not open.

const fs = require("fs");

// jszip ships inside pptxgenjs but is not always hoisted, so resolve it from
// beside pptxgenjs rather than trusting a bare require.
function loadJSZip() {
  try {
    return require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));
  } catch {
    throw new Error(
      "cannot find pptxgenjs and its bundled jszip from " + __filename +
      ". Run `npm install` in deck_src, or set NODE_PATH to its node_modules. " +
      "Nothing was changed.");
  }
}

const SLOTS = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3",
               "accent4", "accent5", "accent6", "hlink", "folHlink"];

const DASHES = ["solid", "dot", "dash", "lgDash", "dashDot", "lgDashDot",
                "lgDashDotDot", "sysDash", "sysDot", "sysDashDot",
                "sysDashDotDot"];

const xmlAttr = (s) => String(s)
  .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, "")
  .replace(/&/g, "&amp;").replace(/</g, "&lt;")
  .replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function themeXml(xml, theme) {
  if (!theme || !theme.name) {
    throw new Error("theme.name is required. Nothing was changed.");
  }
  const name = xmlAttr(theme.name);
  const colors = theme.colors || theme;
  for (const slot of SLOTS) {
    if (!/^[0-9A-Fa-f]{6}$/.test(String(colors[slot]))) {
      throw new Error(
        `theme.colors.${slot} is ${JSON.stringify(colors[slot])}, but every ` +
        `slot must be six hex digits with no "#". Slots: ${SLOTS.join(" ")}. ` +
        "Nothing was changed.");
    }
  }
  const scheme = `<a:clrScheme name="${name}">` +
    SLOTS.map((s) => `<a:${s}><a:srgbClr val="${String(colors[s]).toUpperCase()}"/></a:${s}>`).join("") +
    "</a:clrScheme>";

  // Function replacements, so a "$" in the theme name is not read as a
  // replacement pattern. The theme, its colour scheme and its font scheme each
  // carry a name, and none of them should still say Office.
  const out = xml
    .replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, () => scheme)
    .replace(/(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"/g,
             (_, head) => `${head}${name}"`);

  if (!out.includes(scheme)) {
    throw new Error(
      "ppt/theme/theme1.xml has no <a:clrScheme> to replace. This expects the " +
      "theme part pptxgenjs writes. Nothing was changed.");
  }
  return out;
}

async function applyTheme(deckPath, theme, outPath = deckPath) {
  const zip = await loadJSZip().loadAsync(fs.readFileSync(deckPath));

  // The single theme part pptxgenjs writes. The slide master and the notes
  // master both point at it, which is why one rewrite is enough.
  const part = "ppt/theme/theme1.xml";
  if (!zip.file(part)) {
    throw new Error(`${deckPath} has no ${part}. Nothing was changed.`);
  }
  zip.file(part, themeXml(await zip.file(part).async("string"), theme));

  for (const name of Object.keys(zip.files)) {
    if (!name.endsWith(".xml")) continue;
    const xml = await zip.file(name).async("string");

    const badColor = xml.match(/<a:srgbClr val="((?![0-9A-Fa-f]{6}")[^"]*)"/);
    if (badColor) {
      throw new Error(
        `${name} has an <a:srgbClr> whose val is "${badColor[1]}", not six hex ` +
        "digits. A scheme colour was given to an option that takes hex only: " +
        "valGridLine.color, catGridLine.color, shadow.color, or chartColors / " +
        "invertedColors on a one-series bar chart. Pass the hex from THEME " +
        "there and rebuild. Nothing was changed.");
    }

    const badDash = [...xml.matchAll(/<a:prstDash val="([^"]*)"/g)]
      .find((m) => !DASHES.includes(m[1].trim()));
    if (badDash) {
      throw new Error(
        `${name} has an <a:prstDash> whose val is "${badDash[1]}", which is not ` +
        "a dash style, and PowerPoint would offer to repair the deck. Give " +
        "line.dashType, a chart's lineDash (one word for the whole chart, not " +
        `an array), catAxisLineStyle or valAxisLineStyle one of: ${DASHES.join(" ")}. ` +
        "Nothing was changed.");
    }

    // pptxgenjs writes valAxisCrossesAt: 0 as <c:crossesAt val="autoZero"/>.
    // <c:crossesAt> takes a number; the word belongs in <c:crosses>, where it
    // means the same thing.
    if (xml.includes('<c:crossesAt val="autoZero"/>')) {
      zip.file(name, xml.replaceAll('<c:crossesAt val="autoZero"/>',
                                    '<c:crosses val="autoZero"/>'));
    }
  }

  // A ZIP entry for a folder is not a part, and pptxgenjs writes one per
  // folder. Dropped because co-editing services choke on them. zip.remove()
  // would take the folder's files with it, so the entries are deleted directly.
  for (const name of Object.keys(zip.files)) {
    if (zip.files[name].dir) delete zip.files[name];
  }

  fs.writeFileSync(outPath,
    await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

module.exports = { applyTheme };
