"""Export chosen slides of a built deck as PNGs, for Canva or any other tool.

WHY A SCRIPT AND NOT A COMMAND SOMEBODY REMEMBERS. D121 removed the last
hand-exported figure from this project for one reason: nothing in the repo
produced it, so nothing would notice when it went stale. A PNG of a slide has
the same problem and worse, because a slide changes every time the tables move.
This takes the deck as its input, so re-running it after a deck build is the
whole update procedure.

It renders through LibreOffice, which is the same path the deck's own render
check uses, so what lands in the PNG is what the slide actually looks like
rather than a second drawing of it.

    .venv/bin/python scripts/export_slide_png.py Datasheet_to_Diagnosis_Presentation.pptx 24:audit_vocabulary_1 25:audit_vocabulary_2

Each argument after the deck is  <slide number>:<output name>. Slide numbers
are 1-based and are the numbers printed on the slides themselves.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/figures/canva"
DPI = 200                       # 13.33 x 7.5 in gives 2667 x 1500 px
SOFFICE = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    deck = (ROOT / argv[0]).resolve() if not Path(argv[0]).is_absolute() else Path(argv[0])
    if not deck.exists():
        print(f"no such deck: {deck}")
        return 1
    wanted = []
    for spec in argv[1:]:
        n, _, name = spec.partition(":")
        if not name:
            print(f"expected <slide>:<name>, got {spec!r}")
            return 2
        wanted.append((int(n), name))

    if not SOFFICE.exists():
        print(f"LibreOffice not found at {SOFFICE}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        # A throwaway profile, because a shared one makes the headless run hang
        # if a desktop LibreOffice is already open.
        prof = Path(tmp) / "profile"
        r = subprocess.run(
            [str(SOFFICE), f"-env:UserInstallation=file://{prof}", "--headless",
             "--convert-to", "pdf", "--outdir", tmp, str(deck)],
            capture_output=True, text=True)
        pdf = Path(tmp) / (deck.stem + ".pdf")
        if not pdf.exists():
            print("conversion failed:", r.stdout.strip(), r.stderr.strip())
            return 1
        for n, name in wanted:
            stem = Path(tmp) / name
            subprocess.run(["pdftoppm", "-png", "-r", str(DPI),
                            "-f", str(n), "-l", str(n), str(pdf), str(stem)],
                           check=True)
            hits = sorted(Path(tmp).glob(f"{name}-*.png"))
            if not hits:
                print(f"slide {n} produced no page: is the deck that long?")
                return 1
            dest = OUT / f"{name}.png"
            dest.write_bytes(hits[0].read_bytes())
            print(f"  slide {n:>3}  ->  {dest.relative_to(ROOT)}")
    print(f"{DPI} dpi")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
