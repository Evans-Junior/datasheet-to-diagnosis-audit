#!/bin/sh
# Rebuild "Ethics In AI Final Presentation.pptx" from the pristine base.
#
# The order below is NOT interchangeable. The first three steps address slides by
# index, so they must run while the deck still has its original 24 slides; every
# later step finds its slide by title or by a named shape and so tolerates the
# insertions above it.
#
# build_slide_provenance.py is deliberately NOT in this list. Its slide was cut
# on 2026-11-18 (D112): slide 6 already names what was taken from each of the
# five papers, so the provenance table was the same claim a second time. The
# table itself survives in the paper's appendix.
set -e
cd "$(dirname "$0")/.."

BASE="${BASE:-/private/tmp/claude-501/-Users-evanskumi-Documents-Masters-Ethics-in-Artificial-Intelligence-Team-Project/cc2372fa-6b34-4e7a-8ac8-096625da5abc/scratchpad/deck_BEFORE_slide6_diagram.pptx}"
DECK="Ethics In AI Final Presentation.pptx"
PY="${PY:-qa_venv/bin/python}"

test -f "$BASE" || { echo "no pristine base at $BASE" >&2; exit 1; }

# A rebuild restores the pristine base over the deck, which DESTROYS any
# PowerPoint comments added to it. (The build scripts themselves are safe:
# python-pptx round-trips comment parts untouched. It is this cp that loses
# them.) So save them first and say so loudly, rather than discovering it later.
SAVED="deck_comments_saved.json"
if $PY -c "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); sys.exit(0 if any(n.startswith('ppt/comments/') for n in z.namelist()) else 1)"         "$DECK" 2>/dev/null; then
    echo "!! $DECK carries PowerPoint comments, which this rebuild will destroy."
    $PY scripts/read_deck_comments.py "$DECK" --json "$SAVED"
    echo "!! saved to $SAVED before overwriting. Re-add them by hand afterwards."
fi

cp "$BASE" "$DECK"
echo "base restored: $($PY -c "from pptx import Presentation; print(len(Presentation('$DECK').slides)), 'slides'")"

for step in \
    build_slide6_diagram.py \
    cascade_placebo_citations.py \
    build_slide_reference_standard.py \
    build_slide_arms_output.py \
    split_slide_scoring.py \
    split_slide_worked_example.py \
    build_slide_placebo_result.py \
    build_slide_prior_architectures.py \
    update_slide_figures.py
do
    echo ""
    echo "================ $step"
    $PY "scripts/$step"
done

echo ""
echo "================ done"
$PY - <<'PYEOF'
from pptx import Presentation
p = Presentation("Ethics In AI Final Presentation.pptx")
print(len(p.slides), "slides")
for i, s in enumerate(p.slides, 1):
    t = ""
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            t = sh.text_frame.text.strip().split("\n")[0][:66]
            break
    print(f"  {i:2d}  {t}")
PYEOF
