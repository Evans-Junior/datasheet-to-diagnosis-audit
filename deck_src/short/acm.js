// ACM-style numeric citations for the short deck.
//
// WHY. The talk and reference decks print author-year markers ("Young et al.
// 2026") through F.citeShort. In a seven-minute deck that is too many words on
// the slide for the amount of credit it carries, so this deck uses the ACM
// Reference Format instead: a bracketed number in the text, and one numbered
// list at the back.
//
// The numbering is ALPHABETICAL by first-author surname, which is what the ACM
// format specifies, and it is computed from docs/references.json rather than
// typed. That matters for the same reason D101 matters: a hand-kept number is
// a number that goes wrong the first time a reference is added, and a citation
// that points at the wrong row is worse than no citation at all.
const F = require("../figures.js");

// First-author surname, for the sort. The `cite` strings are "Surname IN, et
// al. Title..." so the surname is the leading token.
function surname(cite) {
  const first = cite.split(/[,.]/)[0].trim();
  return first.replace(/\s+[A-Z]{1,3}$/, "").toLowerCase();
}
function year(cite) {
  const plain = cite.replace(/arXiv:\S+/gi, " ").replace(/doi:\S+/gi, " ")
                    .replace(/https?:\/\/\S+/gi, " ");
  return Number((plain.match(/\b(19|20)\d{2}\b/) || [])[0] || 0);
}

const ORDER = F.refs().literature
  .map(e => ({ id: e.id, cite: e.cite, doi: e.doi, key: surname(e.cite), yr: year(e.cite) }))
  .sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 :
                   a.yr - b.yr || (a.id < b.id ? -1 : 1)));

const NUM = {};
ORDER.forEach((e, i) => { NUM[e.id] = i + 1; });

// A single citation number. Throws on an unknown id for the reason figures.js
// throws: a mistyped attribution must stop the build, not print "[undefined]".
function n(id) {
  if (!NUM[id]) {
    throw new Error(`acm.js: no reference with id "${id}". `
      + `Known: ${Object.keys(NUM).sort().join(", ")}`);
  }
  return NUM[id];
}

// An in-text marker: m("gebru2021", "chang2025") -> "[5, 11]", ascending, as
// the ACM format requires, so the reader can find each one in the list.
function m(...ids) {
  const ns = ids.map(n).sort((a, b) => a - b);
  return "[" + ns.join(", ") + "]";
}

// The numbered list for the references slide, in citation order.
function list() {
  return ORDER.map((e, i) => ({ num: i + 1, cite: e.cite, doi: e.doi, id: e.id }));
}

module.exports = { n, m, list, ORDER };
