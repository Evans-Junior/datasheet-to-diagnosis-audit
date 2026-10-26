"""RQ1: gender skew around health concepts in the Pile and OLMo-mix-1124.

Queries the infini-gram API (https://api.infini-gram.io/) for co-occurrence of
gender terms with health concepts, and computes a **base-rate-normalised** skew
score per concept.

Why normalisation is the whole method, not a refinement
-------------------------------------------------------
In the Pile, "he" occurs 506,515,052 times and "she" 209,229,612 — a ratio of
2.42. Two probes:

    chest pain : she 2,510   he 6,078    raw ratio 2.422
    anxious    : she 8,723   he 21,073   raw ratio 2.416

Both raw ratios match the pronoun base rate almost exactly, so normalised skew
is -0.0004 and +0.0030 — no skew at all. Reporting raw counts would have
produced the confident false claim that chest pain is 2.4x more male-associated
in the Pile. Skew is therefore always:

    rate(group)  = cooccur(group, concept) / base(group)
    skew_log2    = log2( rate(female) / rate(male) )

Two API traps this module guards against
----------------------------------------
1. `find_cnf` returns **cnt = 0** when `max_diff_tokens` is omitted — silently.
   The window is always sent explicitly, and a run aborts if the whole sweep
   comes back zero.
2. `count` does not support CNF: "she AND chest pain" returns 0. Co-occurrence
   must use `find_cnf`; `count` is only for single-term base rates.

Every response is cached to disk by a hash of its request, so no query is ever
repeated and results are reproducible without network access.

Usage:
    .venv/bin/python -m src.corpus_counts --probe      # ~20 queries, variance check
    .venv/bin/python -m src.corpus_counts --run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import pandas as pd
import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
TERMS = ROOT / "configs/terms.yaml"
CACHE = ROOT / "data/cache/infinigram"
MANIFEST = ROOT / "data/cache/manifest.json"
OUT = ROOT / "results/tables/rq1_corpus_skew.csv"

API = "https://api.infini-gram.io/"
PAUSE = 1.0           # politeness between uncached calls; the API rate-limits
RETRIES = 5
BACKOFF = 8.0         # seconds, multiplied by attempt, on a 403/429


# --------------------------------------------------------------------------- #
# Cached API access
# --------------------------------------------------------------------------- #

def _key(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()[:24]


def api(payload: dict, cache: bool = True) -> dict:
    """POST to infini-gram, caching every response by request hash."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{_key(payload)}.json"
    if cache and path.exists():
        return json.loads(path.read_text())

    last = None
    for attempt in range(RETRIES):
        try:
            r = requests.post(API, json=payload, timeout=90)

            # Rate limiting returns HTTP 403 with body {"message": "Forbidden"},
            # which has no "error" key. Checking only for "error" treated it as
            # success and CACHED IT, so every blocked query read back as 0
            # forever. Status is checked first, and nothing without a count
            # field is ever written to cache. See D022.
            if r.status_code in (403, 429, 503):
                last = f"HTTP {r.status_code} (rate limited)"
                time.sleep(BACKOFF * (attempt + 1))
                continue
            if r.status_code != 200:
                last = f"HTTP {r.status_code}"
                time.sleep(BACKOFF * (attempt + 1))
                continue

            j = r.json()
            if "error" in j:
                last = str(j["error"])
                if "not found" in last.lower() or "invalid" in last.lower():
                    break   # malformed query will not improve on retry
                time.sleep(BACKOFF * (attempt + 1))
                continue

            # A valid response MUST carry a count field. Anything else is an
            # error in disguise and must not be cached.
            if not ({"cnt", "count"} & set(j)):
                last = f"response lacks a count field: {list(j)[:4]}"
                time.sleep(BACKOFF * (attempt + 1))
                continue

            path.write_text(json.dumps(j))
            time.sleep(PAUSE)
            return j
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(BACKOFF * (attempt + 1))
    return {"error": last or "unknown"}


def base_count(index: str, term: str) -> tuple[int, bool]:
    """Single-term frequency. `count` is exact (approx=False) for these."""
    j = api({"index": index, "query_type": "count", "query": term})
    if "error" in j:
        return -1, False
    return int(j.get("count", 0)), bool(j.get("approx", False))


def cooccur(index: str, a: str, b: str, window: int, max_clause_freq: int
            ) -> tuple[int, bool]:
    """Co-occurrence of two terms within `window` tokens, via CNF.

    `max_diff_tokens` is always sent: omitting it returns 0 without an error.
    """
    j = api({"index": index, "query_type": "find_cnf", "query": f"{a} AND {b}",
             "max_diff_tokens": window, "max_clause_freq": max_clause_freq})
    if "error" in j:
        return -1, False
    return int(j.get("cnt", 0)), bool(j.get("approx", False))


# --------------------------------------------------------------------------- #
# Skew
# --------------------------------------------------------------------------- #

def skew(co_f: int, co_m: int, base_f: int, base_m: int) -> dict:
    """Base-rate-normalised female-vs-male skew for one concept."""
    out = {"raw_ratio_m_over_f": None, "rate_female": None, "rate_male": None,
           "skew_log2": None, "note": ""}
    if min(co_f, co_m, base_f, base_m) < 0:
        out["note"] = "query failed"
        return out
    if co_f == 0 or co_m == 0:
        out["note"] = "zero co-occurrence in one arm; skew undefined"
        return out
    rf, rm = co_f / base_f, co_m / base_m
    out.update(raw_ratio_m_over_f=co_m / co_f, rate_female=rf, rate_male=rm,
               skew_log2=math.log2(rf / rm))
    return out


def concept_pairs(cfg: dict) -> list[tuple[str, str]]:
    """(group, term) pairs across every concept block in the config."""
    pairs: list[tuple[str, str]] = []
    for vid, terms in (cfg.get("health_concepts") or {}).items():
        pairs += [(vid, t) for t in terms]
    for name, terms in (cfg.get("psychologizing_concepts") or {}).items():
        pairs += [(f"psych:{name}", t) for t in terms]
    for name, terms in (cfg.get("decision_concepts") or {}).items():
        pairs += [(f"decision:{name}", t) for t in terms]
    return pairs


# --------------------------------------------------------------------------- #
# Runs
# --------------------------------------------------------------------------- #

def sweep(cfg: dict, pairs: list[tuple[str, str]], indexes: list[str]) -> pd.DataFrame:
    window = cfg["window_tokens"]
    mcf = cfg["max_clause_freq"]
    gt = cfg["gender_terms"]
    rows = []

    for index in indexes:
        # Base rates for the two compared groups. Summed over each group's terms:
        # a group's rate must be normalised by the same terms used to measure it.
        base: dict[str, int] = {}
        for grp in ("female", "male"):
            tot = 0
            for term in gt[grp]:
                c, _ = base_count(index, term)
                if c > 0:
                    tot += c
            base[grp] = tot
        print(f"  {index}: base female={base['female']:,}  male={base['male']:,}  "
              f"ratio m/f={base['male']/max(base['female'],1):.3f}", flush=True)

        for grp_label, term in pairs:
            co, fails = {}, 0
            approx = False
            for grp in ("female", "male"):
                tot = 0
                for g in gt[grp]:
                    c, ap = cooccur(index, g, term, window, mcf)
                    approx |= ap
                    if c < 0:
                        fails += 1          # counted, never silently zeroed
                    else:
                        tot += c
                co[grp] = tot
            s = skew(co["female"], co["male"], base["female"], base["male"])
            if fails:
                # A partial sum makes the ratio meaningless, so the row is
                # marked unusable rather than reported.
                s["skew_log2"] = None
                s["note"] = f"{fails} failed queries; sums partial, row unusable"
            rows.append({"index": index, "concept_group": grp_label, "concept": term,
                         "failed_queries": fails,
                         "cooccur_female": co["female"], "cooccur_male": co["male"],
                         "base_female": base["female"], "base_male": base["male"],
                         "window_tokens": window, "approx": approx, **s})
            sk = s["skew_log2"]
            shown = "n/a" if sk is None else f"{sk:+.3f}"
            flag = f"  [{fails} FAILED]" if fails else ""
            print(f"    {term:28s} F={co['female']:>9,} M={co['male']:>9,}  "
                  f"skew_log2={shown}{flag}", flush=True)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true",
                    help="small sweep to check whether ANY concept shows skew")
    ap.add_argument("--run", action="store_true", help="full sweep")
    ap.add_argument("--index", action="append", help="override index targets")
    ap.add_argument("--max-terms", type=int, default=0,
                    help="use only the first N terms per gender group (keeps the "
                         "query count low enough to avoid rate limiting)")
    args = ap.parse_args()
    if not (args.probe or args.run):
        ap.print_help()
        return

    cfg = yaml.safe_load(TERMS.read_text())
    if args.max_terms:
        for grp in cfg["gender_terms"]:
            cfg["gender_terms"][grp] = cfg["gender_terms"][grp][:args.max_terms]
    indexes = args.index or cfg["index_targets"]
    pairs = concept_pairs(cfg)

    if args.probe:
        # One concept per vignette group plus the psychologizing terms, on one
        # index. The question this answers: is there ANY variance in normalised
        # skew to correlate against in RQ4?
        seen, probe = set(), []
        for g, t in pairs:
            head = g.split(":")[0]
            if head.startswith("psych") or head not in seen:
                probe.append((g, t))
                seen.add(head)
        pairs = probe[:20]
        indexes = indexes[:1]
        print(f"PROBE: {len(pairs)} concepts on {indexes[0]}\n")

    df = sweep(cfg, pairs, indexes)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tag = "_probe" if args.probe else ""
    dest = OUT.with_name(OUT.stem + tag + OUT.suffix)
    df.to_csv(dest, index=False)

    ok = df[df["skew_log2"].notna()]
    nfail = int(df["failed_queries"].sum())
    print(f"\n{len(ok)}/{len(df)} concepts scored. {nfail} failed queries. "
          f"wrote {dest.relative_to(ROOT)}")
    if nfail:
        raise SystemExit(
            f"ABORT: {nfail} queries failed, so gender sums are partial and every "
            f"affected ratio is meaningless. Re-run with --max-terms to reduce "
            f"query volume, or wait for the rate limit to clear. Do NOT interpret "
            f"these numbers (D022)."
        )
    if len(ok) == 0:
        raise SystemExit(
            "ABORT: no concept produced a skew score. Check that max_diff_tokens "
            "is being sent — find_cnf returns 0 silently without it (D022)."
        )
    print(f"skew_log2  min={ok['skew_log2'].min():+.3f}  "
          f"max={ok['skew_log2'].max():+.3f}  sd={ok['skew_log2'].std():.3f}")
    if ok["skew_log2"].abs().max() < 0.1:
        print("\nWARNING: every concept has |skew| < 0.1, i.e. no measurable gender\n"
              "skew after normalisation. RQ4 correlates data skew against output\n"
              "gaps — with no variance in the predictor there is nothing to\n"
              "correlate. Widen the window, use more specific concept phrases, or\n"
              "reconsider RQ4's feasibility BEFORE investing in it.")

    # Cache manifest keeps counts reproducible without re-querying.
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({
        "cached_responses": len(list(CACHE.glob("*.json"))),
        "indexes": indexes, "window_tokens": cfg["window_tokens"],
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, indent=2))


if __name__ == "__main__":
    main()
