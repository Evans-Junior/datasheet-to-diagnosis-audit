"""Validation D: is the guideline text itself in the training corpus? (D063)

Queries exact n-gram counts for verbatim spans of each governing guideline
against every indexed corpus, reusing the cached infini-gram client from
src/corpus_counts.py. See configs/contamination_probes.yaml for the probe
design and for why long and short spans are read differently.

Usage:
    .venv/bin/python scripts/contamination_audit.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.corpus_counts import base_count  # noqa: E402

CFG = ROOT / "configs/contamination_probes.yaml"
TERMS = ROOT / "configs/terms.yaml"
OUT = ROOT / "results/tables/v_d_contamination.csv"


def main() -> None:
    cfg = yaml.safe_load(CFG.read_text())
    indexes = yaml.safe_load(TERMS.read_text())["index_targets"]

    jobs = []
    for p in cfg["probes"]:
        for kind in ("long", "short"):
            jobs.append((p["vignette"], p.get("guideline", ""), kind, p[kind]))
    nc = cfg["negative_control"]
    for kind in ("long", "short"):
        jobs.append(("NEGATIVE_CONTROL", "not from any guideline", kind, nc[kind]))

    rows = []
    print(f"querying {len(jobs)} spans x {len(indexes)} indexes\n")
    for index in indexes:
        print(f"{index}")
        for vig, gl, kind, span in jobs:
            n, approx = base_count(index, span)
            rows.append({"index": index, "vignette": vig, "guideline": gl,
                         "span_kind": kind, "span": span, "n_tokens_approx":
                         len(span.split()), "count": n, "approx": approx,
                         "present": n > 0 if n >= 0 else None,
                         "query_failed": n < 0})
            flag = "FAILED" if n < 0 else ("PRESENT" if n > 0 else "absent")
            print(f"  {vig:18s} {kind:5s} n={n:>9,}  {flag:8s} {span[:52]!r}")
        print()

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    nfail = int(df.query_failed.sum())
    if nfail:
        raise SystemExit(f"ABORT: {nfail} queries failed; counts are partial "
                         f"and must not be interpreted (D022).")

    print("=" * 72)
    print("SUMMARY\n")
    piv = df[df.vignette != "NEGATIVE_CONTROL"].pivot_table(
        index=["vignette", "span_kind"], columns="index", values="count",
        aggfunc="first")
    print(piv.to_string())

    print("\nNegative control (clinical register, not from any of our guidelines):")
    for _, r in df[df.vignette == "NEGATIVE_CONTROL"].iterrows():
        print(f"  {r['index']:28s} {r.span_kind:5s} n={r['count']:>9,}")

    print("\nINTERPRETATION")
    real = df[(df.vignette != "NEGATIVE_CONTROL") & (df.span_kind == "long")]
    ctrl_long = df[(df.vignette == "NEGATIVE_CONTROL") & (df.span_kind == "long")]
    n_hit = int((real["count"] > 0).sum())
    print(f"  long spans present : {n_hit}/{len(real)} corpus x guideline cells")
    if n_hit == 0:
        print("    => No governing guideline appears VERBATIM in any corpus at the\n"
              "       10+ token level. Recitation of the guideline text is ruled out\n"
              "       as an explanation for correct answers, which STRENGTHENS the\n"
              "       claim that the models are doing something clinical.")
    else:
        print("    => At least one guideline is in a corpus verbatim. Those vignettes\n"
              "       must be reported with a recitation caveat, and their gender\n"
              "       effects may reflect the guideline's own phrasing.")
    if (ctrl_long["count"] > 0).any() and n_hit == 0:
        print("  Negative control DOES occur while the real probes do not, so the\n"
              "  zero counts above are specific to these guidelines and not an\n"
              "  artefact of long spans being rare in general. The probe has power.")
    elif (ctrl_long["count"] == 0).all():
        print("  WARNING: the negative control is also absent, so a long span of ANY\n"
              "  clinical prose may simply be rare. The long-span nulls are then\n"
              "  WEAK evidence. Report the short spans as the informative measure.")

    shorts = df[(df.vignette != "NEGATIVE_CONTROL") & (df.span_kind == "short")]
    absent = shorts[shorts["count"] == 0]
    print(f"\n  short spans ABSENT : {len(absent)}/{len(shorts)} cells")
    if len(absent):
        print("    These decisions are not stated in these terms anywhere in the\n"
              "    corpus. A null result on such a vignette is a data-absence\n"
              "    finding, not a fairness finding:")
        for _, r in absent.iterrows():
            print(f"      {r['index']:28s} {r.vignette:10s} {r.span!r}")

    nb = df[(df.vignette == "G2-01b")]
    if not nb.empty:
        print("\n  The trans/non-binary scope probe (G2-01b), the key one:")
        for _, r in nb.iterrows():
            print(f"      {r['index']:28s} {r.span_kind:5s} n={r['count']:>9,}  "
                  f"{r.span[:46]!r}")

    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
