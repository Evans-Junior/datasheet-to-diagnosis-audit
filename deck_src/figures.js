// Numbers for the deck, read from results/tables at build time (D090).
//
// WHY THIS EXISTS
// ---------------
// Every number in this deck used to be typed in by hand. That is how the deck
// came to be showing pre-round-5 figures while the tables on disk had moved on,
// and it is the same defect as D086/D087/D090 in a different medium: a derived
// artefact drifting from its source with nothing to say so.
//
// Now the deck reads the tables. If a table carries a prompt_hash that is not
// the current one, the build ABORTS rather than rendering a stale figure onto a
// slide somebody will present. `results/tables/_current_prompt_hash.txt` is
// published by `python -m src.provenance`, so run the pipeline before building.
const fs = require("fs");
const path = require("path");

const T = path.join(__dirname, "..", "results", "tables");

// Minimal RFC4180-ish parser: quoted fields, doubled quotes, embedded commas
// and newlines. No dependency, because adding one to a deck build is worse.
function parseCSV(text) {
  const rows = [];
  let row = [], field = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else q = false; }
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
    else if (c !== "\r") field += c;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  const head = rows.shift();
  return rows.filter(r => r.length === head.length)
             .map(r => Object.fromEntries(head.map((h, j) => [h, r[j]])));
}

const CURRENT = (() => {
  const f = path.join(T, "_provenance.json");
  if (!fs.existsSync(f)) {
    throw new Error(
      "figures.js: results/tables/_provenance.json is missing.\n" +
      "  Run the pipeline first:  sh scripts/run_full_pipeline.sh\n" +
      "  (or at minimum:          .venv/bin/python -m src.provenance)");
  }
  const prov = JSON.parse(fs.readFileSync(f, "utf8"));
  // A table stamped with the current hash can still hold numbers computed from
  // rows scored under a previous prompt set: write_table() stamps the CSV as it
  // stands when the table is written, not the raw it was computed from. The
  // audit resolves that by checking the manifest, and refuses here too, because
  // a slide is the last place anyone will notice.
  if (prov.scored === false) {
    throw new Error(
      `figures.js: prompt set ${prov.prompt_hash} has NEVER BEEN SCORED.\n` +
      "  The tables carry its hash because that is when they were written, but\n" +
      "  their numbers came from a different prompt set. Refusing to put them\n" +
      "  on a slide. Run:  sh scripts/run_full_pipeline.sh");
  }
  return prov.prompt_hash;
})();

const _cache = {};
function table(name) {
  if (_cache[name]) return _cache[name];
  const f = path.join(T, name);
  if (!fs.existsSync(f)) throw new Error(`figures.js: no such table: ${name}`);
  const rows = parseCSV(fs.readFileSync(f, "utf8"));
  if (rows.length && "prompt_hash" in rows[0]) {
    const bad = [...new Set(rows.map(r => r.prompt_hash))].filter(h => h !== CURRENT);
    if (bad.length) {
      throw new Error(
        `figures.js: ${name} was built from prompt set ${bad.join(", ")}, ` +
        `but the current set is ${CURRENT}.\n` +
        "  This deck will NOT be built from a stale table. Re-run:\n" +
        "    sh scripts/run_full_pipeline.sh");
    }
  }
  return (_cache[name] = rows);
}

const num = v => (v === "" || v == null ? NaN : Number(v));
const row = (name, pred) => table(name).find(pred);

// ---- formatting helpers, so slides never disagree on rounding -------------
const f4 = v => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(4);   // +0.0043
const f3 = v => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(3);
const fx = v => v.toFixed(1) + "×";                               // 16.0x
const p  = v => (v < 0.0001 ? "p < 0.0001" : "p = " + v.toFixed(4));
const ci = (lo, hi) => `[${f4(lo)}, ${f4(hi)}]`;
const SHORT = m => m.replace("EleutherAI/", "").replace("allenai/", "")
                    .replace("Qwen/", "").replace("-1124", "");

// ---- the figures the slides actually use ---------------------------------
function hypothesis(h) {
  const r = row("rq2_hypothesis_tests.csv", x => x.hypothesis === h);
  if (!r) throw new Error(`figures.js: no row for ${h}`);
  return {
    delta: num(r.mean_delta), ciLo: num(r.ci_lo), ciHi: num(r.ci_hi),
    pExact: num(r.p_cluster_signflip_exact), pHolm: num(r.p_holm),
    pResolution: num(r["p_resolution_limit_2^-k"]),
    nPairs: num(r.n_pairs), k: num(r.n_vignettes),
    margin: num(r.equivalence_margin),
    tost: r.tost_supported === "True",
    rejects: r.reject_at_fwer_05 === "True",
    containsZero: r.ci_contains_zero === "True",
    status: r.verification_status,
    // Formatted, for direct use on a slide.
    txt: {
      delta: f4(num(r.mean_delta)), ci: ci(num(r.ci_lo), num(r.ci_hi)),
      pExact: num(r.p_cluster_signflip_exact).toFixed(4),
      pHolm: num(r.p_holm).toFixed(4),
      margin: isNaN(num(r.equivalence_margin)) ? "" : num(r.equivalence_margin).toFixed(4),
    },
  };
}

function gateTable() {
  // Name every model through SHORT(model_id), NOT through the summary table's
  // own `model` column: that one keeps the "-1124" date and sizeTrend() does
  // not, so joining the two on it silently drops both OLMo rows.
  return table("summary_model_bias.csv").map(r => ({
    model: SHORT(r.model_id), params: num(r.params_b),
    gate: r.gate, margin: num(r.gate_margin),
    absDelta: num(r.mean_abs_delta), floor: num(r.nuisance_floor),
    above: String(r.exceeds_floor) === "True",
    direction: r.direction, status: r.verification_status,
  }));
}

function sizeTrend() {
  return table("rq3_size_trend.csv").map(r => ({
    model: SHORT(r.model_id), params: num(r.n_params_b),
    absDelta: num(r.mean_abs_delta), floor: num(r.nuisance_floor),
    gap: num(r.floor_relative_gap),
    // D089: a boolean that flips on the 5th decimal is reporting rounding.
    // Anything inside 1e-4 of its own floor is reported "at floor", not T/F.
    above: Math.abs(num(r.floor_relative_gap)) < 1e-4
             ? "at floor" : (String(r.exceeds_floor) === "True" ? "yes" : "no"),
    nPairs: num(r.n_pairs),
    // D045: the placebo check says whether this model's null can be read at
    // all. Without it on the object, a slide that wanted the count silently
    // filtered on an undefined field and printed "0 of 10".
    nullInterpretable: String(r.null_is_interpretable) === "True",
    t2Recovered: String(r.t2_pmi_recovered) === "True",
  })).sort((a, b) => a.params - b.params);
}

function merging() {
  return table("rq2b_identity_spcu_merging.csv").map(r => ({
    model: SHORT(r.model_id), mean: num(r.mean_merging),
    floor: num(r.nuisance_floor), timesFloor: num(r.times_floor),
    above: String(r.exceeds_floor) === "True",
    allSameSign: String(r.all_same_sign) === "True",
    nPositive: num(r.n_positive),
    // D095: the slide said "with three vignettes the finest resolvable p is
    // 0.125". Both halves of that are now read from the table, because the
    // contrast runs over more vignettes than it did and understating k
    // overstates what the design can resolve.
    nVignettes: num(r.n_vignettes), pResolution: num(r.p_resolution_limit),
  })).sort((a, b) => b.mean - a.mean);
}

function postTraining() {
  const r = table("rq2c_post_training_contrast.csv")[0];
  return {
    base: SHORT(r.base_model), tuned: SHORT(r.tuned_model),
    mergingBase: num(r.merging_base), mergingTuned: num(r.merging_tuned),
    delta: num(r.rq2c_delta), floorCombined: num(r.floor_combined),
    timesFloor: num(r.times_combined_floor),
    baseInsideOwnFloor: String(r.base_inside_own_floor) === "True",
    tunedExceedsOwnFloor: String(r.tuned_exceeds_own_floor) === "True",
    // D095: the slide needs these too. The resolution limit in particular was
    // typed as 0.125 (k=3) and the contrast now runs over 4 vignettes, so the
    // true limit is 1/2^4. A hand-typed resolution limit is the worst kind of
    // stale number: it understates how little the design can resolve.
    floorBase: num(r.floor_base), floorTuned: num(r.floor_tuned),
    nVignettes: num(r.n_vignettes), pResolution: num(r.p_resolution_limit),
  };
}

// Is ANY input reportable? Drives the provisional banner on every results slide.
function reportable() {
  const seen = new Set(table("rq2_hypothesis_tests.csv")
                        .map(r => r.verification_status).filter(Boolean));
  return { statuses: [...seen],
           ok: [...seen].every(s => !s.startsWith("PROVISIONAL")
                                 && !s.startsWith("unverified")) };
}

// ---- D095: figures that were hand-typed onto slides -----------------------
// Everything below exists because a slide was carrying a number no build step
// could check. Each one was WRONG on the deck as it stood:
//   floorComparison  slide said 0.118 / 8.5x, the table said 0.164 / 6.1x
//   rq3Spearman      slide said rho +0.693 p 0.026, the run printed +0.857
//   liveVignettes    the tier banner said 26, the set holds 25
// The fix is not to retype them. It is to stop typing them.

// The primary score key for every reported result (configs/models.yaml,
// --score-key pmi). The i1_* tables hold one row per model PER KEY, so a
// helper that forgets to filter silently averages three instruments.
const KEY = "pmi";

// Live vignettes: DISTINCT vignette_id among rows that are analysis_ready and
// not blocked. The live/blocked predicate mirrors src/provenance.py exactly --
// if that changes, this must change with it.
//
// vignettes.csv is the PROMPT csv: one row per prompt, 696 rows over 28
// vignettes. Counting its rows gives 624/696, which is the prompt count, not
// the vignette count. The deck says "vignettes", so it must count vignettes.
function liveVignettes() {
  const f = path.join(__dirname, "..", "data", "vignettes", "vignettes.csv");
  if (!fs.existsSync(f)) throw new Error("figures.js: no vignettes.csv");
  const rows = parseCSV(fs.readFileSync(f, "utf8"));
  const live = rows.filter(r =>
    String(r.analysis_ready).trim() === "True" &&
    String(r.blocked_on || "").trim() === "");
  const uniq = a => new Set(a.map(r => r.vignette_id)).size;
  return { live: uniq(live), total: uniq(rows),
           livePrompts: live.length, totalPrompts: rows.length };
}

// The positive-control gate, per model, on the primary key.
function positiveControl() {
  return table("rq0_positive_control.csv").map(r => ({
    model: SHORT(r.model_id), margin: num(r.mean_margin),
    floor: num(r.nuisance_floor), overFloor: num(r.margin_over_floor),
    gate: r.gate, nVignettes: num(r.n_vignettes), nPairs: num(r.n_pairs),
  }));
}

// I1: the floor as first built against the floor as rebuilt.
function floorComparison() {
  const rows = table("i1_floor_comparison.csv").filter(r => r.score_key === KEY);
  if (!rows.length) throw new Error(`figures.js: no ${KEY} rows in i1_floor_comparison.csv`);
  const ratios = rows.map(r => num(r.ratio_new_over_old)).filter(v => !isNaN(v))
                     .sort((a, b) => a - b);
  const mid = ratios.length % 2
    ? ratios[(ratios.length - 1) / 2]
    : (ratios[ratios.length / 2 - 1] + ratios[ratios.length / 2]) / 2;
  return {
    n: rows.length,
    medianRatio: mid,
    // "The old floor was N times too high" is the reciprocal of the median
    // ratio, not a separate measurement. Deriving it here keeps the two
    // numbers on the slide from disagreeing, which they did.
    timesTooHigh: 1 / mid,
    nMoved: rows.filter(r => Math.abs(num(r.ratio_new_over_old) - 1) > 0.25).length,
    oldFloorLo: Math.min(...rows.map(r => num(r.old_floor))),
    oldFloorHi: Math.max(...rows.map(r => num(r.old_floor))),
    byModel: Object.fromEntries(rows.map(r =>
      [SHORT(r.model_id), { oldFloor: num(r.old_floor),
                            newFloor: num(r.floor_max_abs_vignette),
                            ratio: num(r.ratio_new_over_old) }])),
  };
}

// I1: how many models passed the gate before and after the floor correction.
function gateRerun() {
  const rows = table("i1_gate_rerun.csv").filter(r => r.score_key === KEY);
  if (!rows.length) throw new Error(`figures.js: no ${KEY} rows in i1_gate_rerun.csv`);
  const pass = v => v === "SENSITIVE";
  return {
    n: rows.length,
    oldPasses: rows.filter(r => pass(r.old_gate)).length,
    newPasses: rows.filter(r => pass(r.new_gate)).length,
    byModel: Object.fromEntries(rows.map(r =>
      [SHORT(r.model_id), { margin: num(r.mean_margin),
                            oldFloor: num(r.old_floor),
                            newFloor: num(r.matched_floor),
                            timesFloor: num(r.times_matched_floor),
                            oldGate: r.old_gate, newGate: r.new_gate }])),
  };
}

// RQ3: the Spearman rho and its decomposition. D095 made src/stats.py persist
// this; before that it was printed to stdout and then lost, which is why the
// slide drifted.
function rq3Spearman() {
  const f = path.join(T, "rq3_size_trend_stats.json");
  if (!fs.existsSync(f)) {
    throw new Error(
      "figures.js: results/tables/rq3_size_trend_stats.json is missing.\n" +
      "  It is written by src/stats.py (D095). Run:  .venv/bin/python -m src.stats");
  }
  const j = JSON.parse(fs.readFileSync(f, "utf8"));
  if (j.prompt_hash !== CURRENT) {
    throw new Error(
      `figures.js: rq3_size_trend_stats.json was written for prompt set ` +
      `${j.prompt_hash}, but the current set is ${CURRENT}.\n` +
      "  Refusing to put a stale correlation on the slide that exists to be " +
      "distrusted.");
  }
  return j;
}

// RQ4: the corpus-linkage correlations, on the pre-registered variant.
// One row per model PER SKEW INDEX, so each model has one `matched` corpus
// (the one it was trained on) and the rest `crossed`. Qwen declares no
// corpus, so every row for it is `unknown` -- that is the negative control.
function rq4Linkage(variant = "centred", support = "common") {
  const rows = table("rq4_linkage.csv")
    .filter(r => r.skew_variant === variant && r.support === support);
  if (!rows.length) throw new Error(`figures.js: no rq4 rows for ${variant}/${support}`);
  const corpus = s => String(s).replace(/^v4_/, "").replace(/_llama$/, "");
  const by = {};
  for (const r of rows) {
    const m = SHORT(r.model_id);
    (by[m] = by[m] || { model: m, rows: [] }).rows.push({
      corpus: corpus(r.skew_index), pairing: r.pairing,
      rho: num(r.spearman_rho), p: num(r.p_one_sided),
      nVignettes: num(r.n_vignettes), propConcordant: num(r.prop_concordant),
    });
  }
  for (const m of Object.values(by)) {
    m.matched = m.rows.find(x => x.pairing === "matched") || null;
    m.crossed = m.rows.filter(x => x.pairing === "crossed");
    m.unknown = m.rows.filter(x => x.pairing === "unknown");
    const pool = m.crossed.length ? m.crossed : m.unknown;
    m.bestCrossed = pool.length
      ? pool.reduce((a, b) => (b.rho > a.rho ? b : a)) : null;
    m.declaresCorpus = m.matched !== null;
  }
  const all = Object.values(by);
  const best = all.flatMap(m => m.rows).reduce((a, b) => (b.rho > a.rho ? b : a));
  const bestOwner = all.find(m => m.rows.includes(best));
  return {
    models: all, variant, support,
    // The claim on the slide used to be typed: "the models trained on neither
    // corpus correlate best with both". Whether that is still true is a fact
    // about the table, so compute it instead of asserting it.
    strongest: { model: bestOwner.model, ...best },
    strongestIsUndeclared: !bestOwner.declaresCorpus,
    strongestIsMatched: best.pairing === "matched",
  };
}

// Mean probability on the target option on the positive-control group, both
// POOLED over the sex parameter and WITHIN each level. Both are needed, and
// reporting only the first is how the slide came to say something false.
//
// Group 2 arms pair complementary conditions: the correct answer flips with
// the sex parameter. So a model that ignores the clinical text and always
// favours the same option lands at a pooled 0.5 exactly as a model that has
// no preference at all. Pooled 0.5 is therefore necessary for "at chance" and
// nowhere near sufficient.
//
// Measured: the Pythia ladder pools to 0.495-0.501, which is chance. Within a
// level the same models span 0.347-0.652, and pythia-1b swings 0.304 between
// the two. They are not failing to respond; they are responding in a direction
// that does not track the correct answer. That is what the gate margin, which
// is signed, correctly reports as null -- and it is why the gate cannot be
// replaced by "is it near 0.5".
function chanceRange(match = /pythia/) {
  const rows = table("rq2_deltas.csv").filter(r =>
    r.outcome === "o1" && r.score_key === KEY &&
    String(r.vignette_id).startsWith("G2-") &&
    r.man !== "" && r.woman !== "");
  if (!rows.length) throw new Error("figures.js: no G2 o1 rows in rq2_deltas.csv");
  const cells = {};                       // model -> spcu -> [p, ...]
  for (const r of rows) {
    const m = SHORT(r.model_id);
    const v = (num(r.man) + num(r.woman)) / 2;
    if (isNaN(v)) continue;
    cells[m] = cells[m] || {};
    (cells[m][r.spcu] = cells[m][r.spcu] || []).push(v);
  }
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  const byModel = {};
  for (const [m, bySpcu] of Object.entries(cells)) {
    const lv = Object.fromEntries(
      Object.entries(bySpcu).map(([k, v]) => [k, mean(v)]));
    const vals = Object.values(lv);
    byModel[m] = {
      levels: lv,
      pooled: mean(vals),
      // |female - male|. Zero means the model treats the two levels alike;
      // large means it responds strongly, whatever the direction.
      swing: vals.length === 2 ? Math.abs(vals[0] - vals[1]) : NaN,
    };
  }
  const hit = Object.entries(byModel).filter(([m]) => match.test(m));
  if (!hit.length) throw new Error(`figures.js: chanceRange matched no model: ${match}`);
  const pooled = hit.map(([, v]) => v.pooled);
  const within = hit.flatMap(([, v]) => Object.values(v.levels));
  const swings = hit.map(([, v]) => v.swing).filter(v => !isNaN(v));
  const widest = hit.reduce((a, b) => (b[1].swing > a[1].swing ? b : a));
  return {
    byModel, nModels: hit.length,
    pooledLo: Math.min(...pooled), pooledHi: Math.max(...pooled),
    withinLo: Math.min(...within), withinHi: Math.max(...within),
    maxSwing: Math.max(...swings),
    widestModel: widest[0], widestPooled: widest[1].pooled,
  };
}

// Spearman's rho: Pearson on ranks, with ties averaged. Implemented here
// because the deck has no scientific-computing dependency and should not grow
// one to avoid typing a number in by hand.
function _spearman(xs, ys) {
  const rank = a => {
    const idx = a.map((v, i) => [v, i]).sort((p, q) => p[0] - q[0]);
    const r = new Array(a.length);
    for (let i = 0; i < idx.length;) {
      let j = i;
      while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
      const avg = (i + j) / 2 + 1;              // 1-based, ties averaged
      for (let k = i; k <= j; k++) r[idx[k][1]] = avg;
      i = j + 1;
    }
    return r;
  };
  const rx = rank(xs), ry = rank(ys), n = xs.length;
  const mx = rx.reduce((a, b) => a + b, 0) / n;
  const my = ry.reduce((a, b) => a + b, 0) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    const dx = rx[i] - mx, dy = ry[i] - my;
    sxy += dx * dy; sxx += dx * dx; syy += dy * dy;
  }
  return sxy / Math.sqrt(sxx * syy);
}

// How closely the two corpora agree on the concepts where both have support.
// This is the bound RQ4 is reported as: two measurements this close cannot be
// told apart by skew correlation, so provenance is not identifiable.
function corpusAgreement() {
  const rows = table("i4_corpus_disagreement.csv")
    .filter(r => String(r.common_support).trim() === "True");
  if (rows.length < 3) throw new Error("figures.js: too few common-support concepts");
  const a = rows.map(r => num(r["olmo-mix-1124"]));
  const b = rows.map(r => num(r.piletrain));
  return { rho: _spearman(a, b), n: rows.length };
}

// I4: how far apart the two corpora are on the audited concepts. Not prompt-
// derived (it probes corpora, not the prompt set), so it carries no hash.
function corpusDisagreement() {
  const rows = table("i4_corpus_disagreement.csv");
  // `disagreement` is SIGNED: it is one corpus's log2 skew minus the other's,
  // so pneumonia is -0.377. The pre-registered criterion ("six concepts above
  // 0.5 log2") and the slide both mean magnitude. Taking the raw max returns
  // the largest POSITIVE disagreement, which here is 0.057 -- a sixth of the
  // real largest -- and the raw median comes out negative, which reads as
  // nonsense for a distance.
  const d = rows.map(r => Math.abs(num(r.disagreement))).filter(v => !isNaN(v))
                .sort((a, b) => a - b);
  const mid = d.length % 2 ? d[(d.length - 1) / 2]
                           : (d[d.length / 2 - 1] + d[d.length / 2]) / 2;
  const common = rows.filter(r => String(r.common_support).trim() === "True");
  return { n: rows.length, nCommonSupport: common.length,
           maxDisagreement: d.length ? d[d.length - 1] : NaN,
           medianDisagreement: mid,
           // Pre-registered criterion: >= 6 concepts above 0.5 log2.
           nAboveHalfLog2: d.filter(v => v > 0.5).length };
}

// How many distinct corpus queries the study actually issued, and how many of
// them failed. Slide 27 said "1,504 corpus queries", which is the n_templates
// column of rq1_corpus_skew_explicit.csv summed: a count of template
// occurrences, not of requests. The real figure is the cache, because
// src/corpus_counts.py writes one file per distinct request keyed by its hash,
// so the cache IS the query log. It is roughly six times larger.
//
// `failed` is read from the skew tables rather than the cache, because a query
// that failed is still cached (D-note in corpus_counts.py: a blocked query once
// came back as a cached 0), so the cache cannot tell success from failure.
function corpusQueries() {
  const dir = path.join(__dirname, "..", "data", "cache", "infinigram");
  let cached = NaN;
  try {
    cached = fs.readdirSync(dir).filter(f => f.endsWith(".json")).length;
  } catch {
    throw new Error("figures.js: no corpus query cache at " + dir +
                    ". Run `python -m src.corpus_counts` before building.");
  }
  const mpath = path.join(__dirname, "..", "data", "cache", "manifest.json");
  let indexes = [];
  try {
    indexes = JSON.parse(fs.readFileSync(mpath, "utf8")).indexes || [];
  } catch { /* the manifest is provenance, not a requirement */ }

  // Every rq1 table carries failed_queries. Sum across all of them, so a
  // failure in the probe or the explicit set cannot hide behind the main one.
  let failed = 0;
  for (const name of ["rq1_corpus_skew.csv", "rq1_corpus_skew_explicit.csv",
                      "rq1_corpus_skew_probe.csv",
                      "rq1_corpus_skew_decision.csv",
                      "rq1_corpus_skew_probe_decision.csv"]) {
    let rows;
    try { rows = table(name); } catch { continue; }
    for (const r of rows) {
      const v = num(r.failed_queries);
      if (!isNaN(v)) failed += v;
    }
  }
  return { cached, failed, nIndexes: indexes.length, indexes };
}

// The decision count on slide 27 was typed (93) and the log has moved past it
// four times. docs/decisions.md is the register; one "## D" heading per entry.
function decisionCount() {
  const f = path.join(__dirname, "..", "docs", "decisions.md");
  const text = fs.readFileSync(f, "utf8");
  const n = (text.match(/^## D/gm) || []).length;
  if (n < 50) throw new Error("figures.js: docs/decisions.md parsed to only " +
                              n + " decisions, which cannot be right");
  return n;
}

// The I3 elicitation grid: 7 Pythia models x 3 prompt formats, on the scored
// key. Slide 43 carried all 21 margins as three typed arrays. They happened to
// still be right, because the small Pythia models were not rescored, but a
// typed array that is right by luck is a figure waiting to go wrong quietly.
// `sign` is what the slide's "7 of 7" claim rests on, so it is counted here
// rather than asserted.
function i3Grid(order = ["70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b"]) {
  const rows = table("i3_gate_by_config.csv").filter(r => r.score_key === KEY);
  if (!rows.length) throw new Error("figures.js: i3_gate_by_config.csv has no " + KEY + " rows");
  const short = m => SHORT(m).replace(/^pythia-/, "");
  const configs = [...new Set(rows.map(r => r.config))];
  const series = {};
  for (const c of configs) {
    series[c] = order.map(lbl => {
      const hit = rows.find(r => r.config === c && short(r.model_id) === lbl);
      if (!hit) throw new Error(`figures.js: no ${KEY}/${c} row for pythia-${lbl}`);
      return num(hit.margin);
    });
  }
  // How many models change the sign of their margin across the formats.
  const nSignFlips = order.filter((_, i) => {
    const vs = configs.map(c => series[c][i]);
    return vs.some(v => v > 0) && vs.some(v => v < 0);
  }).length;
  const passes = {};
  for (const c of configs) {
    passes[c] = rows.filter(r => r.config === c && num(r.times_floor) > 1).length;
  }
  return { order, configs, series, nSignFlips, nModels: order.length, passes };
}

// Per-group counts of the live vignettes, and the Group 4 option-count split
// the floor is stratified on. The vignette ledger slide typed all of these, and
// its title typed the number of held-out rows as two when three are held out:
// two clinical rejections plus one retirement under D092. The slide's own body
// listed all three, so the slide contradicted itself.
function vignetteGroups() {
  const f = path.join(__dirname, "..", "data", "vignettes", "vignettes.csv");
  if (!fs.existsSync(f)) throw new Error("figures.js: no vignettes.csv");
  const rows = parseCSV(fs.readFileSync(f, "utf8"));
  const seen = new Map();
  for (const r of rows) {
    if (!seen.has(r.vignette_id)) seen.set(r.vignette_id, r);
  }
  const all = [...seen.values()];
  const isLive = r => String(r.analysis_ready).trim() === "True"
                   && !String(r.blocked_on || "").trim();
  const live = all.filter(isLive);
  const held = all.filter(r => !isLive(r));

  const groups = {};
  for (const r of live) {
    const g = (r.vignette_id.match(/^G(\d)/) || [])[1];
    if (!g) continue;
    (groups[g] = groups[g] || []).push(r.vignette_id);
  }
  for (const g of Object.keys(groups)) groups[g].sort();

  // The floor is stratified by option count, so the Group 4 split matters.
  const g4 = live.filter(r => r.vignette_id.startsWith("G4"));
  const nOpts = r => String(r.answer_options || "").split("|").filter(Boolean).length;
  const g4Binary = g4.filter(r => nOpts(r) === 2).length;

  return {
    nLive: live.length, nTotal: all.length, nHeld: held.length,
    heldIds: held.map(r => r.vignette_id).sort(),
    // A retirement is not a clinical rejection, and the slide says so.
    nRejected: held.filter(r => /REJECTED/i.test(r.blocked_on || "")).length,
    nRetired: held.filter(r => /RETIRED/i.test(r.blocked_on || "")).length,
    groups,
    n: g => (groups[String(g)] || []).length,
    g4Binary, g4Multi: g4.length - g4Binary, g4Total: g4.length,
  };
}

// RQ5's corpus probe counts, read back out of the query cache.
//
// WHY THIS IS NOT JUST READ FROM A TABLE. These counts are not produced by the
// scoring pipeline and no results table holds them; they are single Infini-gram
// count queries. src/corpus_counts.py caches every response under
// sha256(json.dumps(payload, sort_keys=True))[:24], so the cache can be read as
// a lookup table if the key is recomputed the same way. Python's json.dumps
// uses ", " and ": " separators, which JSON.stringify does not, so the payload
// is serialised by hand below. The hash is a self-check: a key that does not
// resolve means the probe was never run with that exact payload, and this
// throws rather than guessing.
//
// It exists because the slide had the two corpora the wrong way round. It
// credited the Pile with 646,440 occurrences of "the woman has" and OLMo-mix
// with 20,142, while the cache says the opposite, and the same inversion was
// repeated in prose as "over 1.3 million mentions in the Pile".
const INDEX = { pile: "v4_piletrain_llama",
                olmo: "v4_olmo-mix-1124_llama",
                dclm: "v4_dclm-baseline_llama" };

function corpusProbe(term, which) {
  const index = INDEX[which];
  if (!index) throw new Error(`figures.js: unknown corpus "${which}"`);
  // Must match Python's json.dumps(..., sort_keys=True) byte for byte.
  const payload = '{"index": ' + JSON.stringify(index)
                + ', "query": ' + JSON.stringify(term)
                + ', "query_type": "count"}';
  const key = require("crypto").createHash("sha256")
                .update(payload).digest("hex").slice(0, 24);
  const f = path.join(__dirname, "..", "data", "cache", "infinigram", key + ".json");
  if (!fs.existsSync(f)) {
    throw new Error(`figures.js: no cached corpus probe for ${JSON.stringify(term)} `
                  + `in ${index}. Run \`python -m src.corpus_counts\` or correct the term.`);
  }
  const j = JSON.parse(fs.readFileSync(f, "utf8"));
  if (j.error) throw new Error(`figures.js: cached probe for ${term}/${index} is an error`);
  return Number(j.count);
}

// The three rows of the RQ5 table, with both corpora, formatted.
function rq5Probe() {
  const terms = ['the woman has', 'non-binary', 'the non-binary patient'];
  const rows = terms.map(t => ({
    term: t, pile: corpusProbe(t, "pile"), olmo: corpusProbe(t, "olmo"),
  }));
  const bare = rows.find(r => r.term === "non-binary");
  const biggest = Math.max(bare.pile, bare.olmo);
  return {
    rows,
    // Which corpus carries the headline "over N million" claim, so the prose
    // cannot name the wrong one again.
    bareMaxCorpus: bare.olmo >= bare.pile ? "OLMo-mix" : "the Pile",
    bareMaxMillions: (biggest / 1e6).toFixed(2).replace(/0$/, ""),
    subjectZero: rows.find(r => r.term === "the non-binary patient"),
  };
}

// The "last updated" line on the title slide. It said 4 November while the
// decision log had moved five days past it, which is the one date on the deck
// an examiner can check against the repository in one step. A living document
// that reports a stale date undercuts the claim it is making about itself.
//
// The newest ISO date anywhere in docs/decisions.md is used, not the build
// clock: rebuilding the deck changes nothing about the work, so a build-time
// date would advance on its own and mean nothing.
const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"];
function lastUpdated() {
  const f = path.join(__dirname, "..", "docs", "decisions.md");
  const text = fs.readFileSync(f, "utf8");
  const all = text.match(/\b(20\d{2})-(\d{2})-(\d{2})\b/g) || [];
  if (!all.length) throw new Error("figures.js: no ISO date in docs/decisions.md");
  const newest = all.sort().at(-1);
  const [y, m, d] = newest.split("-").map(Number);
  return { iso: newest, long: `${d} ${MONTHS[m - 1]} ${y}` };
}

// RQ1's cross-corpus replication: does the SKEW MEASURE reproduce when the
// same concepts are counted in an independently built corpus?
//
// This is NOT corpusAgreement(). The two are easy to confuse and were confused
// once already. corpusAgreement() is the RQ4 non-identifiability figure: rho
// over the 8 concepts of common support in i4_corpus_disagreement.csv, and it
// answers "can provenance be attributed to one corpus rather than the other?".
// This one is a validation claim over the 15 concepts powered in both corpora
// of a pair, and it answers "is the measurement an artefact of one corpus?".
// Different n, different filter, different question. Report each where it
// belongs and never substitute one for the other.
function corpusReplication(a = "v4_olmo-mix-1124_llama", b = "v4_piletrain_llama") {
  const rows = table("rq1_corpus_skew.csv")
    .filter(r => String(r.powered).trim() === "True");
  const by = {};
  for (const r of rows) {
    (by[r.concept] = by[r.concept] || {})[r.index] = num(r.skew_log2);
  }
  const xs = [], ys = [], diffs = [];
  for (const c of Object.keys(by)) {
    const va = by[c][a], vb = by[c][b];
    if (va == null || vb == null || isNaN(va) || isNaN(vb)) continue;
    xs.push(va); ys.push(vb); diffs.push(Math.abs(va - vb));
  }
  if (xs.length < 3) throw new Error("figures.js: too few concepts powered in both corpora");
  diffs.sort((p, q) => p - q);
  const mid = diffs.length % 2 ? diffs[(diffs.length - 1) / 2]
                               : (diffs[diffs.length / 2 - 1] + diffs[diffs.length / 2]) / 2;
  // Pearson on the raw values, beside the Spearman the project also reports.
  const mean = v => v.reduce((t, x) => t + x, 0) / v.length;
  const mx = mean(xs), my = mean(ys);
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < xs.length; i++) {
    const dx = xs[i] - mx, dy = ys[i] - my;
    sxy += dx * dy; sxx += dx * dx; syy += dy * dy;
  }
  return { n: xs.length, r: sxy / Math.sqrt(sxx * syy), rho: _spearman(xs, ys),
           maxDiff: diffs[diffs.length - 1], medianDiff: mid };
}

// --------------------------------------------------------------------------
// D099. RQ4 run as H4 was preregistered: open-data models only, and the
// cross-pairing treated as the negative control the prereg said it was rather
// than as a column beside the matched one. Two separate claims come out, and
// the deck must not merge them: skew predicts the gap in exactly one model,
// and WHICH corpus cannot be recovered.
function rq4Control() {
  const rows = table("rq4_matched_vs_crossed.csv").map(r => ({
    model: r.model, family: r.family, size: num(r.n_params_b),
    tuned: String(r.instruction_tuned) === "True",
    ownCorpus: r.own_corpus, n: num(r.n_concepts),
    matched: num(r.rho_matched), crossedMax: num(r.rho_crossed_max),
    matchedWins: String(r.matched_beats_crossed) === "True",
  }));
  const wins = rows.filter(r => r.matchedWins).length;
  return { rows, wins, n: rows.length };
}

function rq4Trend() {
  const rows = table("rq4_linkage_trend.csv").map(r => ({
    model: r.model, family: r.family, size: num(r.n_params_b),
    tuned: String(r.instruction_tuned) === "True",
    n: num(r.n_concepts), rho: num(r.rho_matched), p: num(r.p_one_sided),
  })).sort((a, b) => a.size - b.size || Number(a.tuned) - Number(b.tuned));
  const py = rows.filter(r => r.family === "pythia").sort((a, b) => a.size - b.size);
  const base = rows.find(r => r.family === "olmo" && !r.tuned);
  const inst = rows.find(r => r.family === "olmo" && r.tuned);
  if (!base || !inst) throw new Error("figures.js: rq4Trend needs an OLMo base/Instruct pair");
  // Spearman over the Pythia ladder only, which is the row that holds training
  // data constant and therefore the only one that speaks to scale.
  const pyRho = _spearman(py.map(r => r.size), py.map(r => r.rho));
  return { rows, pythia: py, pyRho, base, inst,
           postTrainingDelta: inst.rho - base.rho,
           nNegative: py.filter(r => r.rho < 0).length };
}

// Validation C (D061). The headline is not the mean delta, it is what fraction
// of the effects big enough to be reported keep their sign under all three
// paraphrasings. An audit that omits it reports wording sensitivity as bias.
function paraphrase() {
  const rows = table("v_c_paraphrase_cells.csv");
  const clears = rows.filter(r => String(r.clears_floor) === "True");
  const unan = clears.filter(r => String(r.unanimous) === "True").length;
  return { nCells: rows.length, nClears: clears.length, nUnanimous: unan,
           pctUnanimous: clears.length ? unan / clears.length : 0,
           nNotUnanimous: clears.length - unan };
}

// Validation D. If a model were reciting the guideline it would be answering
// from memory, not from the corpus statistics the linkage claim is about.
function contamination() {
  const rows = table("v_d_contamination.csv");
  const isCtrl = r => /NEGATIVE_CONTROL/.test(String(r.vignette));
  const grp = r => String(r.vignette).slice(0, 2);
  // The claim a slide wants is about the TARGET vignettes, Groups 1 and 3. The
  // deliberately generic negative-control span is SUPPOSED to be present, and
  // Group 4 is the noise baseline, so folding either into one "long spans
  // absent" headline would either overstate or understate the check. Counted
  // separately, because a reviewer will ask which of the six hits mattered.
  const long = rows.filter(r => r.span_kind === "long" && !isCtrl(r));
  const short = rows.filter(r => r.span_kind === "short" && !isCtrl(r));
  const tgtLong = long.filter(r => grp(r) === "G1" || grp(r) === "G3");
  const present = a => a.filter(r => String(r.present) === "True").length;
  const ctrl = rows.filter(isCtrl);
  return { nSpans: rows.length,
           nLong: long.length, longPresent: present(long),
           nShort: short.length, shortPresent: present(short),
           nTargetLong: tgtLong.length, targetLongPresent: present(tgtLong),
           maxTargetLongCount: Math.max(0, ...tgtLong.map(r => num(r.count))),
           nCtrl: ctrl.length, ctrlPresent: present(ctrl),
           failed: rows.filter(r => String(r.query_failed) === "True").length };
}

// RQ6, and the distinction the slide has to keep. The term sweep and the
// joint-window test are mechanical text facts and may be shown as results. The
// graded D1-D8 codes are NOT: codebook section 6 needs two independent human
// passes before any code is citable, and only the machine draft exists (D098).
function rq6Status() {
  const counts = table("rq6_search_counts.csv");
  const docs = [...new Set(counts.map(r => r.document))];
  const zeroDocs = docs.filter(d =>
    counts.filter(r => r.document === d).every(r => num(r.hits) === 0));
  const nTerms = new Set(counts.map(r => r.term)).size;
  const relPath = path.join(T, "rq6_reliability.csv");
  return { nDocs: docs.length, nTerms: nTerms, zeroDocs,
           coded: fs.existsSync(relPath) };
}

module.exports = {
  CURRENT, KEY, table, hypothesis, gateTable, sizeTrend, merging, postTraining,
  reportable, liveVignettes, positiveControl, floorComparison, gateRerun,
  rq3Spearman, rq4Linkage, corpusDisagreement, chanceRange,
  corpusAgreement, corpusQueries, decisionCount, i3Grid, vignetteGroups,
  corpusProbe, rq5Probe, lastUpdated, corpusReplication,
  rq4Control, rq4Trend, paraphrase, contamination, rq6Status,
  f4, f3, fx, p, ci, SHORT, num,
};
