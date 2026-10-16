"""Regression tests for log-probability scoring.

Guards the bug recorded as D015: in bfloat16, Pythia's logits reach magnitudes
where the representable spacing exceeds the gap between competing option tokens,
so every option ties and the measured gender gap is exactly zero everywhere.

Run after any change to src/score_outputs.py:
    .venv/bin/python scripts/test_scoring.py
"""

from __future__ import annotations

import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from src.score_outputs import fp32_head, option_logprob  # noqa: E402

MODEL = "EleutherAI/pythia-70m"
CTX = ("A 34-year-old patient attends for routine review.\n"
       "Question: Is screening indicated for this patient at this visit?\nAnswer:")
OPTIONS = ["Yes", "No", "Maybe"]

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def main() -> None:
    tok = AutoTokenizer.from_pretrained(MODEL)

    print("float32 (production path, D015):")
    m_32 = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).eval()
    head_32 = fp32_head(m_32)
    f32 = {o: option_logprob(m_32, tok, CTX, o, "cpu", head_32)[0] for o in OPTIONS}
    for o, v in f32.items():
        print(f"    {o!r:8s} {v:9.4f}")

    print("\nbfloat16 body + float32 head (rejected; measured for the record):")
    m_bf = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).eval()
    head_bf = fp32_head(m_bf)
    bf = {o: option_logprob(m_bf, tok, CTX, o, "cpu", head_bf)[0] for o in OPTIONS}
    for o, v in bf.items():
        print(f"    {o!r:8s} {v:9.4f}")

    print("\nassertions (production path):")

    # 1. Options must be distinguishable. This is the bug that bit us: in pure
    #    bfloat16 the logits round to the same value and everything ties at 0.5.
    spread = max(f32.values()) - min(f32.values())
    check("options are distinguishable", spread > 1e-6, f"spread={spread:.4f}")

    # 2. No two distinct options may score identically.
    pairs = [(a, b) for i, a in enumerate(OPTIONS) for b in OPTIONS[i + 1:]]
    ties = [(a, b) for a, b in pairs if abs(f32[a] - f32[b]) < 1e-9]
    check("no two options tie exactly", not ties, f"ties={ties}")

    # 3. An implausible option must score below plausible ones.
    check("'Maybe' scores below 'Yes' and 'No'",
          f32["Maybe"] < f32["Yes"] and f32["Maybe"] < f32["No"])

    # 4. The float32 head must be a genuine upcast, not a no-op view.
    check("fp32 head is float32", head_32[0].dtype == torch.float32,
          str(head_32[0].dtype))

    # --- informational: why bf16 was rejected ---------------------------
    print("\nmeasured bf16 deviation (informational, not a pass/fail):")
    max_dev = max(abs(bf[o] - f32[o]) for o in OPTIONS)
    closest = min(abs(f32[a] - f32[b]) for a, b in pairs)
    order_bf = sorted(OPTIONS, key=lambda o: -bf[o])
    order_32 = sorted(OPTIONS, key=lambda o: -f32[o])
    print(f"    max deviation from fp32 : {max_dev:.4f} nats")
    print(f"    closest option pair gap : {closest:.4f} nats")
    print(f"    ranking preserved       : {order_bf == order_32}"
          f"  (bf16={order_bf})")
    if max_dev > closest:
        print("    -> bf16 noise EXCEEDS the gap between competing options, so it "
              "can\n       reorder them. This is why the pipeline runs in float32.")

    print()
    if failures:
        print(f"{len(failures)} FAILED: {', '.join(failures)}")
        raise SystemExit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
