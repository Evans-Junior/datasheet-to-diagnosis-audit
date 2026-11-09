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
  })).sort((a, b) => a.params - b.params);
}

function merging() {
  return table("rq2b_identity_spcu_merging.csv").map(r => ({
    model: SHORT(r.model_id), mean: num(r.mean_merging),
    floor: num(r.nuisance_floor), timesFloor: num(r.times_floor),
    above: String(r.exceeds_floor) === "True",
    allSameSign: String(r.all_same_sign) === "True",
    nPositive: num(r.n_positive),
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

module.exports = {
  CURRENT, table, hypothesis, gateTable, sizeTrend, merging, postTraining,
  reportable, f4, f3, fx, p, ci, SHORT, num,
};
