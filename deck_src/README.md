# Deck source

Four decks are generated from these files. Do not hand-edit any .pptx: edit the
source and rebuild, or the next rebuild silently discards the edit.

| Deck | Built by | Slides | Use |
|---|---|---|---|
| `Datasheet_to_Diagnosis_Presentation.pptx` | `build.js` | 56 | The living reference. Every decision, every validity check, every table. For a reader working through the project, not for standing up and talking. |
| `Datasheet_to_Diagnosis_Talk.pptx` | `talk/build.js` | 19 | Fifteen to twenty minutes, ten beats, one argument carried through. |
| `Datasheet_to_Diagnosis_7min.pptx` | `short/build.js` | 12 | The seven-minute content on seven dense slides. The better handout: each slide carries a whole section, so it reads on its own. Slide 8 is references, 9 to 12 are backup. |
| `Datasheet_to_Diagnosis_5min_Pitch.pptx` | `pitch/build.js` | 31 | **The pitch.** Five minutes, thirteen messages, one idea per slide, and a build sequence wherever a message has more than one part, so advancing it reads as an animation. 23 slides are spoken, 24 is references, 25 to 28 are the chart backups, 29 and 30 are the corpus argument and 31 the limits. The spoken budget is summed at build time and the build **fails** if it exceeds 300 seconds. |
| `Datasheet_to_Diagnosis_7min_Stepped.pptx` | `stepped/build.js` | 21 | **The better talk.** The same seven minutes and the same figures, split one message to a slide, because the dense version asks a listener to hold two or three ideas at once. Slides 1 to 16 are spoken, 17 is references, 18 to 21 are backup. |

All four read the same accessors in `figures.js`, so a figure cannot differ
between them. Only the selection and the ordering differ. The two seven-minute
decks share `short/acm.js`, which numbers `docs/references.json` alphabetically
for ACM-style bracketed citations; that is presentation only and changes no
figure. The stepped deck reuses the short deck's reference and backup slides
verbatim, so there is exactly one copy of each.

Both seven-minute decks budget their spoken slides to 420 seconds in total, with
each slide's allowance written into its speaker notes as a `[NNs]` prefix.

Build the seven-minute decks with:

```bash
cd short   && NODE_PATH="$(cd .. && pwd)/node_modules" node build.js
cd stepped && NODE_PATH="$(cd .. && pwd)/node_modules" node build.js
cd pitch   && NODE_PATH="$(cd .. && pwd)/node_modules" node build.js
```

### Checking the spoken length

The two seven-minute decks are the only ones with a time budget, so check them
after any change to the notes. At 135 words per minute, 7:00 is about 945 words:

```bash
qa_venv/bin/python - <<'EOF'
from pptx import Presentation
import re
p = Presentation("Datasheet_to_Diagnosis_7min_Stepped.pptx")
tot = 0
for i, s in enumerate(p.slides, 1):
    t = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    w = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\u2019-]*", t))
    m = re.match(r"\s*\[(\d+)s\]", t)
    if m:
        tot += w
        print(f"slide {i}: {w} words = {w/135*60:.0f}s, budget {m.group(1)}s")
print(f"TOTAL {tot} words = {tot/135:.2f} min")
EOF
```

The first draft of these notes came to 1,594 words, which is 11.8 minutes. They
were coaching notes rather than a script, and nothing on the slide said so.
Measure before rehearsing.

## Build

```bash
sh ../scripts/run_full_pipeline.sh   # FIRST: figures.js refuses a stale/unscored set
npm install                          # pptxgenjs only
NODE_PATH="$PWD/node_modules" node build.js
```

`NODE_PATH` is required: `build.js` calls `applyTheme` from a script outside this
folder, and that script resolves `pptxgenjs` and its bundled `jszip` from
`NODE_PATH`. Without it the deck is still written but **the theme colours are not
applied**, and every scheme colour falls back to Office's stock palette.

## Layout

| File | Contents |
|---|---|
| `part1.js` | The kernel: theme, four slide masters (TITLE_DARK, SECTION, CONTENT, CONTENT_DARK) and the `S` / `card` / `stat` / `badge` / `box` / `arrow` / `note` helpers. Everything else requires it. |
| `figures.js` | **D090: every number on a results slide is read from `results/tables/*.csv` at build time.** The build ABORTS if a table carries a non-current prompt-set hash, or if `results/tables/_provenance.json` says the current set has never been scored. Run the pipeline before building. Numbers were hand-typed before this existed, which is how the deck came to be showing a 576-prompt set while the repository was on 648. |
| `part3b.js` | The story spine: the whole argument in six moves, each with the paper that forced it. |
| `part6b.js` | Methodology visuals: the SPCU × identity arm grid, the nine-stage process with its four refusal points, and the vignette ledger. |
| `part13b.js` | Fix rounds 3–7, and the two-tier reporting rule (D091). |
| `part13c.js` | Limitations and conclusions. **Split out of `part13.js`** on 2026-11-09 so the "Fix rounds 3-7" section lands before Limitations rather than after it. |
| `part2.js` … `part15.js` | Slides, in order. **Slide order is `require` order in `build.js`**, so a slide must be added in the part that sits at the right point in the narrative, not appended at the end. |
| `qa_geom.py` | Geometry and overflow QA. Needs `python-pptx`. It is **not** a substitute for the render pass: it compares text against text, so it cannot see a line drawn through a label or a chart data label printed over an axis label. Both of those reached the short deck and only the render caught them. |
| `qa_tokens.py` | Scans every slide for `undefined`, `NaN`, `[object Object]`, `Infinity` and unexpanded `${...}`. |
| `short/` | The dense seven-minute deck: `s1.js` to `s12.js`, `acm.js`, `build.js`. |
| `stepped/` | The stepped seven-minute deck: `s01.js` to `s21.js`, `build.js`. Slides 17 to 21 are copies of the short deck's reference and backup slides. |
| `pitch/` | The five-minute pitch deck: `kit.js`, `a1_problem.js`, `a2_method.js`, `a3_results.js`, `a4_close.js`, `a5_charts.js`, `a6_backup.js`, `build.js`. One file per act rather than per slide, because a build-sequence message is one block of code that emits several slides. The last two hold the backup slides, in the order a presenter flips through them: the four result charts, then the corpus argument and the limits. |
| `talk/` | The fifteen-to-twenty-minute deck: `t1.js` to `t7.js`, `build.js`. |
| `text.md` | The long-form speaker text the slides were condensed from. |

## Sections

Declared with `pres.addSection` and passed to every `addSlide` as `sectionTitle`.
A slide without one lands in a stray "Default-N" section. Current order:
Opening, Problem and objective, Related work, Methodology, Results, Fix round 1,
Fix round 2, **Fix rounds 3-7**, Limitations and conclusions.

## QA

Four checks, in this order. The first three all passed on a deck that had six
visible defects, so none of them substitutes for the fourth.

1. `validate.py` from the pptx skill, run under a venv built from
   `/opt/homebrew/bin/python3.12`. The project `.venv` cannot run it: no pip, no
   `defusedxml`, and system python3 is 3.9.
2. `qa_geom.py`: shapes outside a 0.45in margin, text that cannot fit its box at
   the stated font size, and overlapping text frames. The fit model is
   deliberately conservative, so a few flags are normal on the long decks, which
   sat at 19 overflows and 6 overlaps. A slide you just added should report 0.
   The short deck reports 0 on all three counts.
3. `qa_tokens.py`, for placeholders that never got substituted.
4. `soffice --convert-to pdf`, then `pdftoppm -jpeg -r 85`, then **look at the
   images**. Both tools are installed. This is the only check that sees a rule
   drawn through its own label, a chart label printed over an axis label, or
   text set in a colour that matches its own background. All three of those
   reached the short deck and all three were invisible to checks 1 to 3.

## How the pitch deck "animates"

PowerPoint animations live in a `<p:timing>` tree, and pptxgenjs writes no such
thing. Hand-patching that tree into the packed XML would put a fragile,
invisible structure into a file nobody can diff, and it would be the first
thing to break the next time the deck is rebuilt.

So `pitch/` uses a **build sequence** instead, which is what professional decks
use. A message with three parts is emitted as three slides, each showing one
more part. Advancing the slide looks exactly like an entrance animation, and it
behaves the same in PowerPoint, Keynote, Google Slides and a PDF export.

The detail that makes it read as animation rather than as three separate slides
is **ghosting**. A part that has not arrived yet is still drawn, in a tint
barely off the background, so nothing moves when it lights up. Without that the
eye sees a new layout on every click and the illusion is gone. `kit.js` holds
the ghost palette and the `message({ steps, draw })` helper; `draw` is called
once per step with the step number, and only the last step of a message carries
the speaker notes, so the presenter view does not repeat the same paragraph
three times.

`kit.js` also sums each message's `secs` and `build.js` fails the build if the
total passes 300 seconds. A talk that runs long is a defect, and it should stop
the build the same way a stale table does.

## The pitch deck's backup charts

The spoken five minutes carry no chart, because in five minutes a chart costs
more attention than the sentence it replaces. The minute after is different, so
`pitch/a5_charts.js` holds four, one per result, and they sit at the front of
the backup section because that is where a spare minute is spent.

Each one carries a single claim, states it in the slide title, plots the one
quantity that supports it, and puts the sentence a presenter would say in a
card beside the plot. Two rules came out of building them and are worth keeping:

- **Do not reuse the paper's figures.** They are drawn at 3.3in column width
  for print. On a 13.3in slide they are either unreadable or an image that goes
  stale against the tables. These are native `addChart` charts read through
  `figures.js`, like every other chart in this repository.
- **Keep a chart title under about 60 characters.** At 30pt in the 12.2in title
  placeholder it wraps to two lines above that, and the second line lands on
  the chart. One title had to be cut after the render showed it.

There were two per-model tables behind these charts and they are gone (D126).
They restated the charts' own numbers, which is not a backup but a choice to
make under a question. The charts' data labels went to four decimals when the
tables went, so nothing they carried was lost. The fifth chart, after the
corpus slide, plots the per-concept skew in both corpora: the Spearman rho the
slide before quotes is a summary, and this is the pattern it summarises.

The size-trend chart is bars for the gap with the floor as a reference line on
the same axis, never a second axis. It was lines over equal-spaced categories
first, and read as noise: a line claims the points lie on a trajectory when the
claim is a rank correlation, and equal spacing hides that 70M to 6.9B is a
hundredfold. See D125.
