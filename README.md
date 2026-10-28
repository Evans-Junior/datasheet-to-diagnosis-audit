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
# 0. Confirm the pipeline end-to-end on the smallest model (~1 min)
.venv/bin/python -m src.score_outputs --smoke

# 1. Benchmark forward-pass latency for scheduling
.venv/bin/python scripts/bench_forward.py        # -> results/tables/rq0_bench.json

# 2. Vignette set (Phase 1)
.venv/bin/python -m src.vignettes --build         # -> data/vignettes/

# 3. Output audit (Phases 2; RQ2, RQ3, RQ5)
#    Hypotheses are fixed in advance: see docs/preregistration.md
.venv/bin/python -m src.score_outputs --config configs/models.yaml
.venv/bin/python -m src.score_outputs --config configs/models.yaml --checkpoints

# 4. Data audit (Phase 3; RQ1) — cached, so queries never repeat
.venv/bin/python -m src.corpus_counts --run --family diagnosis
.venv/bin/python -m src.corpus_counts --run --family decision   # H1/H2 basis
.venv/bin/python -m src.corpus_counts --run --family explicit   # non-binary arm

# 5. Linking (Phase 4; RQ4)
.venv/bin/python -m src.link_analysis

# 6. Statistics and figures
.venv/bin/python -m src.stats
.venv/bin/python -m src.plots
```

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
  decisions.md         every methodological choice, with its reason (D001-D033)
  preregistration.md   RQ2 directional predictions, frozen before any scoring
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
