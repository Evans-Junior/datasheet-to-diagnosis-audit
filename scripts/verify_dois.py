"""Resolve DOIs against CrossRef so no citation enters the project unverified.

Search-engine snippets disagree about DOIs. CrossRef is the registration
authority, so it settles which DOI belongs to which article.

Usage:
    .venv/bin/python scripts/verify_dois.py                  # check the registry
    .venv/bin/python scripts/verify_dois.py 10.1093/cid/ciu296 ...
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import os

import requests

# CrossRef asks callers to identify themselves; providing a contact address puts
# requests in their "polite pool". Kept out of the source so the repository can be
# shared without carrying a personal address: set CROSSREF_MAILTO in your
# environment. Without it the script still runs, on the anonymous pool.
MAILTO = os.environ.get("CROSSREF_MAILTO", "").strip()

# Candidate DOIs for the project's guideline and methods citations.
REGISTRY = {
    "G1-01 pneumonia (ATS/IDSA)": "10.1164/rccm.201908-1581ST",
    "G1-04 cellulitis (IDSA SSTI) cand.A": "10.1093/cid/ciu296",
    "G1-04 cellulitis (IDSA SSTI) cand.B": "10.1093/cid/ciu444",
    "G3-02 chest pain (Circulation)": "10.1161/CIR.0000000000001029",
    "G3-02 chest pain (JACC copub)": "10.1016/j.jacc.2021.07.053",
    "method: HL7 Gender Harmony": "10.1093/jamia/ocab196",
    "method: anti-LGBTQIA+ audit": "10.1371/journal.pdig.0001001",
    "method: GPT-4 bias (Zack)": "10.1016/S2589-7500(23)00225-X",
    "method: sex/gender AI (Cirillo)": "10.1038/s41746-020-0288-5",
    "method: SAGER guidelines": "10.1186/s41073-016-0007-6",
}


def resolve(doi: str) -> dict:
    url = f"https://api.crossref.org/works/{doi}"
    params = {"mailto": MAILTO} if MAILTO else {}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 404:
        return {"doi": doi, "ok": False, "error": "not registered"}
    r.raise_for_status()
    m = r.json()["message"]
    return {
        "doi": doi,
        "ok": True,
        "title": (m.get("title") or ["?"])[0],
        "container": (m.get("container-title") or ["?"])[0],
        "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "page": m.get("page"),
        "type": m.get("type"),
        "first_author": next(
            (f"{a.get('family','')}" for a in m.get("author", []) if a.get("family")),
            None,
        ),
    }


def main() -> None:
    args = sys.argv[1:]
    items = [(d, d) for d in args] if args else list(REGISTRY.items())

    out = []
    for label, doi in items:
        try:
            res = resolve(doi)
        except Exception as exc:  # noqa: BLE001
            res = {"doi": doi, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
        res["label"] = label
        out.append(res)

        if res["ok"]:
            print(f"\n[OK] {label}\n     {doi}")
            print(f"     {res['first_author']} et al. ({res['year']}) "
                  f"{res['container']}")
            print(f"     vol {res['volume']} issue {res['issue']} pp {res['page']}")
            print(f"     {res['title'][:110]}")
        else:
            print(f"\n[!!] {label}\n     {doi}  ->  {res['error']}")
        time.sleep(0.3)  # be polite to the API

    dest = Path("results/tables/doi_verification.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2))
    bad = [r for r in out if not r["ok"]]
    print(f"\n{len(out) - len(bad)}/{len(out)} resolved. wrote {dest}")


if __name__ == "__main__":
    main()
