"""Stop the pipeline if any configured model is missing from the scored set.

WHY THIS EXISTS (D094). `src/score_outputs.py` catches a per-model exception,
prints `FAILED: ...`, and continues to the next model. That is the right
behaviour for a long sequential run: one model running out of memory should not
throw away nine good ones. The problem is what happens next. `src/stats.py`
analyses whatever raw files it finds and never checks the roster, so a model
that died overnight would quietly turn "7 of 10 models fail the positive
control" into a statement about nine, with every table, figure and slide built
from it looking perfectly well formed.

The gate runs between scoring and the floor rebuild, so the run stops *before*
any table is written rather than after.

It checks two things for every model the config says to score:

  1. the model has a manifest entry at all, and
  2. that entry's `prompt_hash` is the hash of the prompt set on disk now.

The second check is what D093 was about. A stale entry is not a scored model;
it is yesterday's numbers wearing today's filename.

Exit codes: 0 all present and current, 1 something missing or stale.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.score_outputs import build_specs          # noqa: E402
from src.vignettes import prompt_set_hash          # noqa: E402

MANIFEST = ROOT / "results/raw/manifest.json"
PROMPTS = ROOT / "data/vignettes/vignettes.csv"
CONFIG = ROOT / "configs/models.yaml"


def main() -> int:
    if not MANIFEST.exists():
        print("GATE FAILED: results/raw/manifest.json does not exist. "
              "Nothing has been scored.")
        return 1

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    specs = build_specs(cfg, False, False)

    prompts = pd.read_csv(PROMPTS)
    ready = prompts[prompts["analysis_ready"] == True]  # noqa: E712
    want = prompt_set_hash(ready)

    completed = json.loads(MANIFEST.read_text(encoding="utf-8"))["completed"]

    missing, stale = [], []
    for spec in specs:
        entry = completed.get(spec.key)
        if entry is None:
            missing.append(spec.key)
        elif entry.get("prompt_hash") != want:
            stale.append((spec.key, entry.get("prompt_hash")))

    print(f"roster: {len(specs)} model(s) configured, "
          f"prompt set {want} ({len(ready)} prompts)")

    if not missing and not stale:
        print(f"  all {len(specs)} scored at the current prompt set")
        return 0

    print()
    print("GATE FAILED. The run is incomplete, and nothing downstream would "
          "have noticed:")
    for key in missing:
        print(f"  NEVER SCORED : {key}")
    for key, had in stale:
        print(f"  STALE        : {key}  (stamped {had}, current is {want})")
    print()
    print("Refusing to rebuild the floor, the statistics or the tables from a "
          "partial roster, because a gate verdict counted over nine models "
          "reads exactly like one counted over ten.")
    print("Scoring resumes and keeps what is already done with:")
    print("  .venv/bin/python -m src.score_outputs --score-key pmi")
    print("Do NOT use scripts/run_full_pipeline.sh to resume: it passes "
          "--force and rescores everything.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
