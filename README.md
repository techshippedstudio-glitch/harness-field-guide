# Harness Field Guide

The complete learning collection for the Techshipped Studio series on harness engineering and Microsoft
Foundry: concepts, diagrams, episode tutorials and code. The site is its readable front door; the videos
explain and demonstrate the same material.

Live site: https://techshippedstudio-glitch.github.io/harness-field-guide/ (GitHub Pages, from `docs/`).

## What's here

| Path | What it is |
|---|---|
| `src/pages/` | The content of every site page (edit these) |
| `docs/` | The built site, served by GitHub Pages (generated; don't edit by hand) |
| `docs/assets/site.css` | All styles, including the diagram classes |
| `docs/diagrams/` | Each diagram as a standalone SVG, light and dark (generated) |
| `episodes/` | Material for each episode: outline, diagrams used, resources created |
| `code/` | Runnable samples, one folder per episode |
| `tools/build_site.py` | Builds `docs/` from `src/pages/` (shared header, navigation, footer) |
| `tools/build_diagrams.py` | Exports diagrams; `--png` also renders 1920 px PNGs and staged frames into `exports/` |
| `tools/fonts/` | Brand fonts (SIL Open Font License) embedded in the exported diagrams |

## Site areas

- **Concepts**: harness engineering and the ideas behind it
- **Microsoft**: the Copilot harness, Foundry's capabilities, resources and projects, roles and identities
- **Episodes**: a tutorial for each video
- **Code**: samples for each episode

## Editing a diagram

Diagrams are inline SVG in the pages under `src/pages/`, styled by the "svg drawing classes" in `site.css`.
Groups marked `data-stage="n"` are revealed one by one in the videos. After an edit, run:

```
python3 tools/build_site.py
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
