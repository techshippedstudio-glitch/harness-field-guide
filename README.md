# Harness Field Guide

Diagrams and dated notes for building AI agents on Microsoft Foundry, from the Techshipped Studio video
series. Each page goes with an episode and can be read on its own.

Live site: GitHub Pages, served from `docs/`.

## What's here

| Path | What it is |
|---|---|
| `docs/index.html` | Home page |
| `docs/foundry-resource-project.html` | Episode 1: resource and project in Microsoft Foundry |
| `docs/copilot-harness.html` | Episode 2: the Copilot harness, drawn out |
| `docs/assets/site.css` | All styles, including the diagram classes |
| `docs/diagrams/` | Each diagram as a standalone SVG, light and dark (generated) |
| `tools/build_diagrams.py` | Regenerates `docs/diagrams/`; `--png` also renders 1920 px PNGs into `exports/` |
| `tools/fonts/` | Brand fonts (SIL Open Font License) embedded in the exported diagrams |

## Editing a diagram

Diagrams are inline SVG in the pages, styled by the "svg drawing classes" in `site.css`. Edit the page,
then run:

```
python3 tools/build_diagrams.py --png
```

## Accuracy

Every statement links to a Microsoft source with the date it was checked. Things we observed in our own
Azure subscription are labelled "We saw this". Preview features, prices and regions are re-checked before
each episode is published.

This is an independent guide, not affiliated with Microsoft.

## Licence

Text and diagrams: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code (`tools/`, CSS): MIT,
see `LICENSE`. Fonts: SIL Open Font License 1.1, see `tools/fonts/`.
