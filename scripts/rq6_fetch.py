"""Retrieve the RQ6 documentation corpus and stamp each file with its date.

Implements step 0 of `docs/codebook.md` §2: the documents are fetched, their
identity is CHECKED against an expected title fragment, and each is written with
a `# retrieved:` header so `scripts/rq6_search.py` will accept it.

The identity check is not ceremony. Three downloads in the clinical sourcing
phase turned out to be the wrong document and all three failed silently -- a
Q&A companion instead of a guideline chapter, a PSA-screening guideline instead
of the LUTS one, an OCR scan whose byline named the wrong author. That is D033,
and dataset documentation is more exposed to it, not less: model and dataset
cards are edited in place with no version notice, so a file fetched today and a
file fetched last month can differ with nothing to show it.

A card and its paper are kept as SEPARATE documents even where they describe the
same artefact, because which document carries a disclosure is part of RQ6's
answer. A risk stated in a paper's limitations section and absent from the
dataset card reaches a different audience.

Usage
    .venv/bin/python scripts/rq6_fetch.py
    .venv/bin/python scripts/rq6_search.py data/raw/rq6/
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/raw/rq6"
MANIFEST = OUT / "manifest.json"

UA = "Mozilla/5.0 (academic research; see AI_USE.md)"

# (filename stem, kind, url, expected fragment that must appear in the text)
DOCS = [
    ("01_pile_paper", "pdf", "https://arxiv.org/pdf/2101.00027",
     "The Pile: An 800GB Dataset"),
    ("02_pile_datasheet", "pdf", "https://arxiv.org/pdf/2201.07311",
     "Datasheet for the Pile"),
    ("03_pythia_model_card", "md",
     "https://huggingface.co/EleutherAI/pythia-70m/raw/main/README.md",
     "Pythia Scaling Suite"),
    ("04_pythia_paper", "pdf", "https://arxiv.org/pdf/2304.01373",
     "Pythia: A Suite for Analyzing Large Language Models"),
    ("05_dolma_paper", "pdf", "https://arxiv.org/pdf/2402.00159",
     "an Open Corpus of Three Trillion Tokens"),
    ("06_olmomix_dataset_card", "md",
     "https://huggingface.co/datasets/allenai/olmo-mix-1124/raw/main/README.md",
     "OLMo 2 Mix"),
    ("07a_olmo2_report", "pdf", "https://arxiv.org/pdf/2501.00656",
     "OLMo 2 Furious"),
    ("07b_olmo2_model_card", "md",
     "https://huggingface.co/allenai/OLMo-2-1124-7B/raw/main/README.md",
     "olmo-mix-1124"),
    ("08a_qwen3_report", "pdf", "https://arxiv.org/pdf/2505.09388",
     "Qwen3 Technical Report"),
    ("08b_qwen3_model_card", "md",
     "https://huggingface.co/Qwen/Qwen3-8B/raw/main/README.md",
     "Qwen3-8B"),
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def pdf_text(raw: bytes, tmp: Path) -> str:
    from pypdf import PdfReader
    tmp.write_bytes(raw)
    reader = PdfReader(str(tmp))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    tmp = OUT / ".fetch.pdf"
    manifest, failures = [], []

    for stem, kind, url, expect in DOCS:
        try:
            raw = fetch(url)
            text = pdf_text(raw, tmp) if kind == "pdf" else raw.decode(
                "utf-8", errors="replace")
        except Exception as e:                                  # noqa: BLE001
            failures.append(f"{stem}: {type(e).__name__}: {e}")
            continue

        # Identity check. A fetch that succeeds and returns the wrong document
        # is the dangerous case, so this is an error rather than a warning.
        flat = re.sub(r"\s+", " ", text)
        if re.sub(r"\s+", " ", expect).lower() not in flat.lower():
            failures.append(
                f"{stem}: fetched {len(text)} chars from {url} but the expected "
                f"fragment {expect!r} is not in it -- NOT the expected document, "
                f"or its text layer is unusable")
            continue

        path = OUT / f"{stem}.md"
        path.write_text(f"# retrieved: {today}\n# source: {url}\n\n{text}",
                        encoding="utf-8")
        manifest.append({"document": stem, "kind": kind, "url": url,
                         "retrieved": today, "chars": len(text),
                         "identity_fragment": expect})
        print(f"  ok   {stem:28s} {len(text):>8,d} chars")

    if tmp.exists():
        tmp.unlink()
    MANIFEST.write_text(json.dumps(manifest, indent=2))

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  {f}")
    print(f"\n{len(manifest)}/{len(DOCS)} documents retrieved, manifest: {MANIFEST}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
