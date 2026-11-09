# Deck source

`Datasheet_to_Diagnosis_Presentation.pptx` in the repo root is generated from these
files. Do not hand-edit the .pptx: edit the part files and rebuild, or the next
rebuild silently discards the edit.

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
| `qa_geom.py` | Geometry and overflow QA. Substitute for a visual pass, because this machine has neither LibreOffice nor Poppler. Needs `python-pptx`. |
| `text.md` | The long-form speaker text the slides were condensed from. |

## Sections

Declared with `pres.addSection` and passed to every `addSlide` as `sectionTitle`.
A slide without one lands in a stray "Default-N" section. Current order:
Opening, Problem and objective, Related work, Methodology, Results, Fix round 1,
Fix round 2, **Fix rounds 3-7**, Limitations and conclusions.

## QA without a renderer

`qa_geom.py` flags shapes outside a 0.45in margin, text that cannot fit its box at
the stated font size, and overlapping text frames. The fit model is deliberately
conservative, so a small number of flags is normal, the deck sat at 18 before
round 4 and 13 after. What matters is that a slide you just added reports **0**,
which the round-4 slides (38 to 40) do. If `python-pptx` is unavailable, the same
checks can be run straight off the slide XML with the standard library.
