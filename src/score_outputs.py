"""Log-probability scoring of answer options (Phase 2; RQ2, RQ3, RQ5).

Primary method. For each prompt we score every answer option as a continuation
and record its log-probability. This works on base models (which cannot follow
instructions), is deterministic, and needs one forward pass per option — no
generation loop.

Execution is strictly sequential: one model resident at a time, results persisted
per model, memory freed before the next load (D007). Runs are resumable from a
manifest, so a crash costs one model rather than the run.

Three scores are recorded per option, because they disagree and the disagreement
matters:

  sum_logprob   raw sum over option tokens. Biased toward SHORT options.
  mean_logprob  per-token mean. Removes most length bias.
  pmi           sum_logprob minus the option's log-probability under a neutral
                context. Removes the option's unconditional frequency, so a
                model that simply likes the token "Yes" does not look like a
                model that thinks the answer is yes.

`norm_prob` is the softmax over the option set, computed from whichever score
`--score-key` names (default: pmi), and is the quantity the statistics operate on.

Usage:
    .venv/bin/python -m src.score_outputs --smoke --allow-unready
    .venv/bin/python -m src.score_outputs --config configs/models.yaml
    .venv/bin/python -m src.score_outputs --config configs/models.yaml --checkpoints
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import platform
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
VIGNETTES = ROOT / "data/vignettes/vignettes.csv"
RAW = ROOT / "results/raw"
MANIFEST = RAW / "manifest.json"

# Context used for the PMI baseline: carries the task framing but no patient.
NEUTRAL_CONTEXT = "Question: {question}\nAnswer:"
PROMPT_FMT = "{prompt_text}\nQuestion: {question}\nAnswer:"


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    revision: str = "main"
    dtype: str = "float32"
    role: str = "audit"
    corpus_index: str | None = None

    @property
    def key(self) -> str:
        return f"{self.model_id}@{self.revision}:{self.dtype}"

    @property
    def slug(self) -> str:
        return (f"{self.model_id}__{self.revision}__{self.dtype}"
                .replace("/", "_").replace(".", "-"))


def set_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def env_record(seed: int) -> dict:
    import transformers
    return {
        "seed": seed,
        "python": platform.python_version(),
        "machine": platform.machine(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def fp32_head(model) -> tuple[torch.Tensor, torch.Tensor | None]:
    """A float32 copy of the output embedding, built once per model.

    MUST NOT be skipped. Pythia's logits reach magnitudes around 1080, where
    bfloat16's spacing is wider than the gap between competing option tokens —
    so "Yes" and "No" round to the *same* bf16 value and every option ties at
    p=0.5. That produces a clean, entirely spurious null result.

    Casting the logits after the forward pass does not help: the precision is
    already gone. The final projection itself has to happen in float32. Only
    the head is upcast, not the body, so the memory cost is ~1 GB even for
    pythia-12b while the 40 transformer layers stay in bfloat16.
    """
    head = model.get_output_embeddings()
    w = head.weight.detach().to(torch.float32)
    b = head.bias.detach().to(torch.float32) if getattr(head, "bias", None) is not None else None
    return w, b


@torch.no_grad()
def option_logprob(model, tok, context: str, option: str, device: str,
                   head: tuple[torch.Tensor, torch.Tensor | None]) -> tuple[float, int]:
    """Total log P(option tokens | context), and the option's token count."""
    ctx_ids = tok(context, return_tensors="pt").input_ids
    # Leading space so the option tokenises as a continuation, not a new word.
    opt_ids = tok(" " + option.strip(), add_special_tokens=False,
                  return_tensors="pt").input_ids
    if opt_ids.shape[1] == 0:
        return float("nan"), 0

    ids = torch.cat([ctx_ids, opt_ids], dim=1).to(device)
    ctx_len = ctx_ids.shape[1]

    out = model(ids, output_hidden_states=True)
    # Position i predicts token i+1, so option token j is predicted from the
    # hidden state at ctx_len + j - 1.
    h = out.hidden_states[-1][0, ctx_len - 1 : -1, :].to(torch.float32)

    w, b = head
    logits = h @ w.T
    if b is not None:
        logits = logits + b

    logprobs = torch.log_softmax(logits, dim=-1)
    tgt = ids[0, ctx_len:]
    picked = logprobs.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
    return float(picked.sum().item()), int(opt_ids.shape[1])


def score_model(spec: ModelSpec, prompts: pd.DataFrame, device: str,
                score_key: str) -> pd.DataFrame:
    tok = AutoTokenizer.from_pretrained(spec.model_id, revision=spec.revision)
    t0 = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        spec.model_id, revision=spec.revision,
        dtype=getattr(torch, spec.dtype),
    )
    model.to(device).eval()
    load_s = time.perf_counter() - t0
    head = fp32_head(model)
    print(f"    loaded in {load_s:.1f}s  (fp32 head: "
          f"{head[0].numel() * 4 / 1e9:.2f} GB)", flush=True)

    # PMI baselines depend only on (question, option), so cache them.
    baseline: dict[tuple[str, str], float] = {}
    rows = []
    t0 = time.perf_counter()

    for n, r in enumerate(prompts.itertuples(index=False), start=1):
        options = [o for o in str(r.answer_options).split("|") if o]
        if not options:
            continue
        context = PROMPT_FMT.format(prompt_text=r.prompt_text, question=r.question)
        neutral = NEUTRAL_CONTEXT.format(question=r.question)

        scored = []
        for opt in options:
            total, n_tok = option_logprob(model, tok, context, opt, device, head)
            bkey = (str(r.question), opt)
            if bkey not in baseline:
                baseline[bkey], _ = option_logprob(model, tok, neutral, opt,
                                                   device, head)
            scored.append({
                "option": opt,
                "sum_logprob": total,
                "mean_logprob": total / n_tok if n_tok else float("nan"),
                "pmi": total - baseline[bkey],
                "n_option_tokens": n_tok,
            })

        vals = np.array([s[score_key] for s in scored], dtype=float)
        probs = np.exp(vals - vals.max())
        probs = probs / probs.sum()
        for s, pr in zip(scored, probs):
            rows.append({
                "prompt_id": r.prompt_id, "vignette_id": r.vignette_id,
                "group": r.group, "condition": r.condition,
                "paraphrase": r.paraphrase, "spcu": r.spcu,
                "gender_identity": r.gender_identity,
                "reference_answer": r.reference_answer, "tier": r.tier,
                "model_id": spec.model_id, "revision": spec.revision,
                "dtype": spec.dtype, "role": spec.role,
                "corpus_index": spec.corpus_index,
                "score_key": score_key, "norm_prob": float(pr), **s,
            })

        if n % 50 == 0:
            el = time.perf_counter() - t0
            print(f"    {n}/{len(prompts)} prompts  ({el/n*1000:.0f} ms/prompt)",
                  flush=True)

    del model, head
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    out = pd.DataFrame(rows)
    _assert_not_degenerate(out, spec)
    return out


def _assert_not_degenerate(df: pd.DataFrame, spec: ModelSpec) -> None:
    """Abort if options tie across the board.

    A numerical-precision fault makes every option score identically, which
    yields a uniform distribution over the option set and therefore zero
    measured gap everywhere -- a null result that looks like a finding. It is
    cheaper to fail loudly here than to discover it after the write-up.
    """
    if df.empty:
        raise RuntimeError(f"{spec.key}: no rows scored")
    spread = df.groupby("prompt_id")["sum_logprob"].agg(lambda s: s.max() - s.min())
    tied = float((spread < 1e-9).mean())
    if tied > 0.5:
        raise RuntimeError(
            f"{spec.key}: {tied:.0%} of prompts have all answer options tied to "
            f"within 1e-9. This is a precision fault, not a finding -- see "
            f"fp32_head() and docs/decisions.md D015. Refusing to emit results."
        )
    if tied:
        print(f"    note: {tied:.1%} of prompts have tied options")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def build_specs(cfg: dict, smoke: bool, checkpoints: bool) -> list[ModelSpec]:
    default_dtype = cfg["runtime"].get("dtype", "float32")
    if smoke:
        return [ModelSpec(m, dtype=default_dtype)
                for m in cfg["smoke"]["audit_models"]]

    specs: list[ModelSpec] = []
    audit = cfg["audit"]
    if checkpoints:
        ck = audit["pythia_checkpoints"]
        return [ModelSpec(ck["model"], revision=rev, dtype=default_dtype,
                          corpus_index=audit["pythia_ladder"]["corpus_index"])
                for rev in ck["revisions"]]

    ladder = audit["pythia_ladder"]
    for s in ladder["sizes"]:
        if s.get("optional"):
            continue  # pythia-12b: run explicitly, last
        specs.append(ModelSpec(s["id"], revision=ladder.get("revision", "main"),
                               dtype=s.get("dtype", default_dtype),
                               corpus_index=ladder["corpus_index"]))
    olmo = audit["olmo2"]
    for m in olmo["models"]:
        specs.append(ModelSpec(m["id"], role=m.get("role", "audit"),
                               dtype=m.get("dtype", default_dtype),
                               corpus_index=olmo["corpus_index"]))
    for m in cfg.get("contrast", []):
        specs.append(ModelSpec(m["id"], dtype=m.get("dtype", default_dtype),
                               role="contrast", corpus_index=None))
    return specs


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"completed": {}, "runs": []}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/models.yaml")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--checkpoints", action="store_true")
    ap.add_argument("--score-key", default="pmi",
                    choices=["pmi", "mean_logprob", "sum_logprob"])
    ap.add_argument("--allow-unready", action="store_true",
                    help="score prompts whose clinical findings / reference "
                         "answers are not yet written (pipeline testing only)")
    ap.add_argument("--force", action="store_true", help="rescore completed models")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / args.config).read_text())
    seed = cfg.get("seed", 0)
    set_seeds(seed)
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    prompts = pd.read_csv(VIGNETTES)
    ready = prompts[prompts["analysis_ready"] == True]  # noqa: E712
    if len(ready) < len(prompts):
        msg = (f"{len(prompts) - len(ready)}/{len(prompts)} prompts are not "
               f"analysis-ready (clinical findings and/or reference answer "
               f"unwritten; see docs/vignette_sources.md).")
        if not args.allow_unready:
            print(f"REFUSING TO SCORE: {msg}\n"
                  f"Fill them, or pass --allow-unready to test the pipeline on "
                  f"placeholder text. Results from placeholder text are not "
                  f"valid and are tagged as such.")
            raise SystemExit(2)
        print(f"WARNING: {msg}\n"
              f"         Scoring anyway (--allow-unready). Output is tagged "
              f"placeholder_text=True and must not enter any result table.")
    else:
        prompts = ready

    if args.smoke:
        keep = prompts["vignette_id"].drop_duplicates().head(
            cfg["smoke"]["n_vignettes"])
        prompts = prompts[prompts["vignette_id"].isin(keep)]

    specs = build_specs(cfg, args.smoke, args.checkpoints)
    purge = cfg["audit"]["pythia_checkpoints"].get("purge_after_scoring", False) \
        if args.checkpoints else cfg["runtime"].get("purge_after_scoring", False)

    prompt_hash = hashlib.sha256(
        pd.util.hash_pandas_object(prompts["prompt_text"], index=False).values.tobytes()
    ).hexdigest()[:16]

    print(f"device={device}  prompts={len(prompts)}  models={len(specs)}  "
          f"score_key={args.score_key}  prompt_hash={prompt_hash}")
    print(f"purge_after_scoring={purge}  seed={seed}\n")

    manifest = load_manifest()
    RAW.mkdir(parents=True, exist_ok=True)

    for i, spec in enumerate(specs, start=1):
        if spec.key in manifest["completed"] and not args.force:
            print(f"[{i}/{len(specs)}] {spec.key}  SKIP (in manifest)")
            continue
        print(f"[{i}/{len(specs)}] {spec.key}", flush=True)
        try:
            df = score_model(spec, prompts, device, args.score_key)
        except Exception as exc:  # noqa: BLE001 — report and continue
            print(f"    FAILED: {type(exc).__name__}: {exc}")
            continue

        df["placeholder_text"] = args.allow_unready
        df["prompt_hash"] = prompt_hash
        out = RAW / f"{spec.slug}.parquet"
        df.to_parquet(out, index=False)
        manifest["completed"][spec.key] = {
            "file": out.name, "rows": len(df), "n_prompts": len(prompts),
            "prompt_hash": prompt_hash, "placeholder_text": args.allow_unready,
            "score_key": args.score_key, "device": device,
            "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
            **asdict(spec),
        }
        MANIFEST.write_text(json.dumps(manifest, indent=2))
        print(f"    wrote {out.name}  ({len(df)} rows)")

        if purge:
            from huggingface_hub import scan_cache_dir
            for repo in scan_cache_dir().repos:
                if repo.repo_id == spec.model_id:
                    for rev in repo.revisions:
                        scan_cache_dir().delete_revisions(rev.commit_hash).execute()
                    print(f"    purged weights for {spec.model_id}")

    manifest["runs"].append({
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "env": env_record(seed), "prompt_hash": prompt_hash,
        "placeholder_text": args.allow_unready, "score_key": args.score_key,
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"\ndone. manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
