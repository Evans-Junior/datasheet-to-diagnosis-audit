# From datasheet to diagnosis

Tracing gender bias through open training-data pipelines into LLM health advice.

Most LLM bias audits can only inspect outputs, because training data is closed.
Fully open model families release theirs — Pythia (the Pile) and OLMo 2
(OLMo-mix-1124) — so gender skew in the data can be linked to gender bias in model
health advice, and dataset documentation can be checked for whether it discloses
that risk.

**Key design rule.** A gender difference in output counts as bias only when the
clinically correct answer is the same for every patient. Every vignette therefore
carries a guideline-sourced reference answer, and vignettes are arranged on two
axes (see `docs/decisions.md` D002).

## Research questions

| RQ | Question | Code |
|---|---|---|
| RQ1 | How skewed is gender representation around health concepts in the Pile and OLMo-mix-1124? | `src/corpus_counts.py` |
| RQ2 | Do Pythia and OLMo give clinically unwarranted gender differences? | `src/score_outputs.py` |
| RQ3 | Does the gap change with model size and across training checkpoints? | `src/score_outputs.py` |
| RQ4 | Does data skew predict the size and direction of output gaps? | `src/link_analysis.py` |
| RQ5 | How does a weights-only model compare? | `src/score_outputs.py` |
| RQ6 | Do the datasheets disclose gender composition and downstream health risks? | `docs/codebook.md` |

Every result table and figure is named by the RQ it answers.

## Status, as of 2026-11-09

| | |
|---|---|
| **Stimulus set** | **25 live vignettes** → **624 analysis-ready prompts**. 3 rows excluded and kept for audit: 2 rejected on clinical review, 1 retired as superseded. |
| **Models** | 10 scored: 7 Pythia sizes, OLMo 2 7B base and Instruct, Qwen3-8B (closed-data contrast). |
| **Reporting tier** | **Tier 1** — every live vignette author-reviewed against a guideline passage quoted at first hand. Reportable for coursework, **pending clinical validation**. Tier 2 (clinician-verified) is the bar for publication and is not yet met. |
| **Decision log** | 95 dated entries in [`docs/decisions.md`](docs/decisions.md), reversals included. |
| **Every table** | stamps the `prompt_hash` it was built from; `python -m src.provenance` fails if any table is stale or the current prompt set has never been scored. |

### What "tier 1" means, and why the rule has two tiers

The original rule was all-or-nothing: clinician verification or nothing
reportable. It conflated two different claims. That 7 of 10 models fail the
project's own positive control, and that an exact sign-flip test on *k* clusters
cannot resolve below 2⁻ᵏ, are facts about the **apparatus** — no clinician ruling
makes them more or less true. What needs a clinician is whether a vignette's
findings force its stated answer.

Reporting was therefore split into two tiers by **dated amendment**
([`docs/preregistration.md`](docs/preregistration.md) §10, D091). The original §9
sentence is not edited. The amendment states what the document said before, what
it says now, who decided, when, that it was decided **after** seeing scores, and
**what would show the change was wrong**: if clinical review overturns a
direction or a gate verdict, tier 1 was too weak a bar.

Author review earned the tier rather than being granted it: it **rejected two
vignettes outright**, **corrected a third** that had reproduced the rejected
row's exact defect, and caught **three guideline-citation errors no validator
detected**.

### Where to start reading

| If you want | Read |
|---|---|
| The whole stimulus set, every vignette with its guideline quote | [`docs/vignettes_compendium.md`](docs/vignettes_compendium.md) — **generated**, never hand-edited |
| What was predicted, and every deviation | [`docs/preregistration.md`](docs/preregistration.md) |
| Why anything is the way it is | [`docs/decisions.md`](docs/decisions.md) |
| How AI was used, and what that costs the claims | [`AI_USE.md`](AI_USE.md) |
| The current numbers | `results/tables/` — each file stamped with its prompt set |
| The talk | `Datasheet_to_Diagnosis_Presentation.pptx`, generated from `deck_src/` |

## Setup

Requires macOS on Apple silicon (the pipeline targets MPS; there is no CUDA path).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
```

Verify:

```bash
.venv/bin/python -c "import torch; print(torch.backends.mps.is_available())"
```

### Verified environment

| | |
|---|---|
| Hardware | Apple M4 Pro, 14 cores, 48 GB unified memory |
| Python | 3.12.15 (arm64) |
| torch | 2.14.1, MPS available |
| transformers | 5.19.0 |
| mlx / mlx-lm | 0.32.3 / 0.32.0 |

## Reproducing the analysis, in order

Execution is strictly sequential with one model resident at a time; runs are
resumable from a manifest. See `docs/decisions.md` D007.

```bash
# 0a. Validate the instrument before trusting any Delta (RQ0; ~1 min/model)
#     Determinism, signal recovery, nuisance floor, score-key robustness.
#     REQUIRED per model and per checkpoint: the floor is not constant and is
#     not monotonic in size (D035). Output is slugged per model, so a model with
#     no floor file is DROPPED from the RQ3 trend rather than silently
#     contributing a raw gap to a floor-relative series.
.venv/bin/python -m scripts.validate_instrument --model EleutherAI/pythia-70m
.venv/bin/python -m scripts.validate_instrument --model EleutherAI/pythia-160m
.venv/bin/python -m scripts.validate_instrument --model EleutherAI/pythia-410m
# ... one per entry in configs/models.yaml; --revision for checkpoints

# 0b. Confirm the pipeline end-to-end on the smallest model (~1 min)
.venv/bin/python -m src.score_outputs --smoke

# 1. Benchmark forward-pass latency for scheduling
.venv/bin/python scripts/bench_forward.py        # -> results/tables/rq0_bench.json

# 2-6. THE WHOLE PIPELINE, in the one order that is correct (D090).
#       Nine steps: build prompts, build placebos, drift gate, score the main
#       set, score the placebos, REBUILD THE FLOOR (between scoring and stats --
#       getting this backwards gated results against a floor from the previous
#       prompt set), stats + summary, the downstream analyses, provenance audit.
#       Exits non-zero if any table is stale or the prompt set was never scored.
sh scripts/run_full_pipeline.sh
sh scripts/run_full_pipeline.sh --no-score     # steps 1-3 and 6-9 only, ~1 min

# Or step by step:
.venv/bin/python scripts/check_templates.py      # 0 blockers; checks ALL 3
                                                 # scoring tokenizers (D090)
.venv/bin/python -m src.vignettes --build        # -> data/vignettes/
.venv/bin/python scripts/build_vignette_compendium.py   # -> docs/
.venv/bin/python -m src.score_outputs --score-key pmi --force
.venv/bin/python scripts/matched_floor.py        # AFTER scoring, BEFORE stats
.venv/bin/python -m src.stats
.venv/bin/python scripts/results_summary.py
.venv/bin/python -m src.link_analysis            # RQ4; report rho WITH its n
.venv/bin/python -m src.plots
.venv/bin/python -m src.provenance               # every table's prompt set

# Data audit (Phase 3; RQ1) — cached, so queries never repeat
.venv/bin/python -m src.corpus_counts --run --family diagnosis
.venv/bin/python -m src.corpus_counts --run --family decision   # H1/H2 basis
.venv/bin/python -m src.corpus_counts --run --family explicit   # non-binary arm

# 7. Sensitivity: repeat the whole analysis under a non-primary score key.
#    Re-softmaxes columns already on disk, so no model is re-run. Required
#    wherever a model that failed T2 under `pmi` carries a claim (D042).
#    NOTE: rebuild the floor for that key first -- the floor is per score key,
#    and the mean_logprob/sum_logprob strata are known stale (D090 finding 3b).
.venv/bin/python -m scripts.sensitivity_score_key --key mean_logprob
```

## Building the deck

```bash
sh scripts/run_full_pipeline.sh          # FIRST -- see below
cd deck_src && npm install
NODE_PATH="$PWD/node_modules" node build.js      # -> ../Datasheet_to_Diagnosis_Presentation.pptx
```

**The deck reads `results/tables/*.csv` at build time and refuses to build from
a stale or never-scored prompt set.** Numbers used to be typed into the slides by
hand, which is how it came to be showing a 576-prompt set while the repository
was on 648 (D090). Do not hand-edit the `.pptx`: edit `deck_src/part*.js` and
rebuild, or the next rebuild discards the edit.

## Measured performance

Forward-pass latency at a 256-token prompt, bf16 on MPS, 20 trials
(`results/tables/rq0_bench.json`):

| Model | Params | Weights | Forward pass |
|---|---|---|---|
| pythia-70m | 0.070 B | 0.14 GB | 6.5 ms |
| pythia-160m | 0.162 B | 0.32 GB | 15.5 ms |
| pythia-410m | 0.405 B | 0.81 GB | 39.6 ms |
| pythia-1.4b | 1.415 B | 2.83 GB | 116.7 ms |

Latency scales linearly at ~83–98 ms per billion parameters, so the rest of the
ladder projects to ~250 ms (2.8b), ~600 ms (6.9b) and ~1.05 s (12b). Log-probability
scoring is one forward pass per item, which puts the **entire** scoring design well
under an hour of compute. Download bandwidth, not compute, is the binding
constraint. Short-generation runs for the secondary method are the expensive part
(hours, not minutes) and are scheduled overnight.

## Data

Nothing under `data/raw/` is committed; fetch it with the scripts in `scripts/`.

| Source | Access | Notes |
|---|---|---|
| Q-Pain | Open, CC BY-SA 4.0, ~98 KB | 5 CSVs by pain context; no DUA |
| infini-gram API | `https://api.infini-gram.io/`, no documented rate limit | Responses cached to `data/cache/` |
| OLMoTrace | Manual (Ai2 Playground) | No public API; see `docs/decisions.md` D009 |

## Repository layout

```
configs/      models, checkpoints, term lists, seeds
data/
  raw/        downloaded sources (git-ignored)
  vignettes/  our vignette set, one CSV per group + reference answers
  terms/      gender and health term lists for corpus counts
  cache/      cached infini-gram responses (git-ignored; manifest tracked)
src/          analysis modules, one per RQ cluster
notebooks/    exploration only; final results come from src/
results/      tables and figures, each named by RQ
docs/
  PROJECT_STATUS.md    full orientation: design, results, faults, what is left
  decisions.md         every methodological choice, with its reason (D001-D039)
  preregistration.md   RQ2 directional predictions, frozen before any scoring
  instrument_validation.md  RQ0: determinism, positive control, nuisance floor
  authoring_worksheet.md    guideline quote beside each blank, for filling templates
  paper_notes.md       difficulties, measured numbers and limitations, for the write-up
  vignette_sources.md  guideline citation and confidence tier per vignette
  codebook.md          RQ6 qualitative codebook
  clinical_review_*    materials for the clinical reviewer
  outreach_email.md    reviewer outreach templates
scripts/      environment and data-fetching utilities
```

## Authorship and tooling

See [AI_USE.md](AI_USE.md) for the project's declaration of tool use. All clinical
reference answers, qualitative coding and interpretation are the authors' own; see
`docs/decisions.md` D003 for how reference answers are sourced and tiered.
