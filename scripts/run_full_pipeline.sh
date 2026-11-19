#!/bin/sh
# The full scoring-to-tables pipeline, in the one order that is correct.
#
# This file exists because the order is not obvious and getting it wrong is
# silent. Two orderings bit this project on 2026-11-08:
#
#   * Editing templates.yaml without rebuilding vignettes.csv. Everything
#     downstream reads the CSV, including the staleness stamp, which hashes it
#     -- so a stale CSV reports itself CURRENT (D086).
#   * Running stats without rebuilding the matched floor. The floor is a build
#     artefact of a PREVIOUS scoring run, so it survives a full rescore
#     untouched. It was found five days stale and built partly from G4-03, a
#     vignette REJECTED on clinical review, while gating every
#     exceeds_floor / margin_over_floor / times_floor value in every table
#     (D087).
#
# Both are now guarded (check_templates.py exits non-zero on CSV drift;
# src/stats.py prints a loud MATCHED FLOOR IS STALE), but a guard reports a
# mistake and this script prevents it. The floor step is between scoring and
# stats, because it is computed FROM scored rows and consumed BY stats.
#
# Usage:  sh scripts/run_full_pipeline.sh            (~2.5 h on mps, 10 models)
#         sh scripts/run_full_pipeline.sh --no-score  (tables only, seconds)
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python

echo "=========== 1/10 BUILD PROMPTS        $(date) ==========="
$PY -m src.vignettes --build
echo "=========== 2/10 BUILD PLACEBOS       $(date) ==========="
$PY scripts/build_placebo_prompts.py
echo "=========== 3/10 DRIFT GATE           $(date) ==========="
$PY scripts/check_templates.py

if [ "$1" != "--no-score" ]; then
  echo "=========== 4/10 SCORE MAIN SET       $(date) ==========="
  $PY -m src.score_outputs --score-key pmi --force
  echo "=========== 5/10 SCORE PLACEBOS       $(date) ==========="
  $PY -m src.score_outputs --score-key pmi --force \
      --prompts data/vignettes/placebo_prompts.csv --raw-subdir raw_placebo
else
  echo "=========== 4-5/10 SCORING SKIPPED (--no-score) ==========="
fi

echo "=========== 6/10 ROSTER GATE         $(date) ==========="
# D094. score_outputs catches a per-model failure, prints FAILED, and carries on
# to the next model. Nothing downstream checks the roster: src/stats.py analyses
# whatever raw files exist, so one model dying overnight would turn "7 of 10
# models fail the positive control" into a claim about nine, and every table and
# slide built from it would look perfectly well formed. This gate runs before
# the floor rebuild so the run stops BEFORE any table is written.
$PY scripts/check_scored_models.py

# MUST run after scoring and before stats. See the header.
echo "=========== 7/10 REBUILD FLOOR        $(date) ==========="
$PY scripts/matched_floor.py

echo "=========== 8/10 STATS + SUMMARY      $(date) ==========="
$PY -m src.stats
$PY scripts/results_summary.py

# D090. These six tables were NOT in the pipeline and nothing reported it. One
# of them (rq4_linkage) was 11 days and several vignette rounds old while being
# read as current. They are all cheap re-analyses of the rows just scored, so
# there is no reason they were ever separate.
#
# Deliberately NOT here:
#   scripts/i3_elicitation.py    loads models and rescores; ~40 min. Run by hand
#                                when the elicitation question is reopened.
#   scripts/contamination_audit.py  probes GUIDELINE spans against external
#                                corpora over the network. Its input is not the
#                                prompt set, so a prompt change cannot stale it
#                                (see NOT_PROMPT_DERIVED in src/provenance.py).
echo "=========== 9/10 DOWNSTREAM ANALYSES  $(date) ==========="
$PY -m src.link_analysis
$PY scripts/permutation_null.py
$PY scripts/paraphrase_consistency.py
$PY scripts/i1_regate.py
$PY scripts/i3_analyse.py

# D090. Every table now carries the prompt-set hash it was built from, so a
# stale table is a fact on disk instead of something a reader must infer from
# file timestamps. Non-zero exit if any table is stale or unstamped.
echo "=========== 10/10 PROVENANCE AUDIT     $(date) ==========="
$PY -m src.provenance

echo "=========== HASH CHECK               $(date) ==========="
$PY -c "
import sys; sys.path.insert(0, '.')
from scripts.results_summary import current_prompt_hash, scored_prompt_hashes
h, n = current_prompt_hash()
ok = h in scored_prompt_hashes()
print(f'prompt hash {h} ({n} prompts) -- matches a scored run: {ok}')
raise SystemExit(0 if ok else 1)
"
echo "=========== PIPELINE COMPLETE        $(date) ==========="
