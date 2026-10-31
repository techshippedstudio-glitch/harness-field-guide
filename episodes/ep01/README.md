# Episode 1: Harness Engineering on Microsoft Foundry: Start Here

Playlist: Microsoft Foundry: Build Real AI Agents · Status: recorded, script in review · Video: not yet published

This is the index for everything that belongs to Episode 1.

| Material | Where | Status |
|---|---|---|
| Tutorial (learning goals, prerequisites, walkthrough, troubleshooting) | [`docs/episodes/ep01.html`](../../docs/episodes/ep01.html) · [live](https://techshippedstudio-glitch.github.io/harness-field-guide/episodes/ep01.html) | Published |
| Concept pages used in the episode | [Harness engineering](../../docs/concepts/harness-engineering.html), [Copilot harness](../../docs/microsoft/copilot-harness.html), [Foundry](../../docs/microsoft/foundry.html), [Resources and projects](../../docs/microsoft/resources-projects.html), [Roles and identities](../../docs/microsoft/roles-identities.html) | Published |
| Diagrams (sources) | Inline SVG in [`src/pages/`](../../src/pages/); standalone SVGs in [`docs/diagrams/`](../../docs/diagrams/) | Published |
| Diagram frames for the video | `exports/stages/` and `exports/video/` (1920x1080), made by `tools/build_diagrams.py --png` | Generated locally, not committed |
| Runnable example | None: this episode is done entirely in the Azure portal and the Foundry portal | n/a |
| Narration script | Added here once it's signed off | In review |
| Screen recording | Kept offline (raw footage contains account details); edited scenes are blurred before encoding | Recorded 31 Oct 2026 |
| Published video, Short, posts | Linked here after publishing | Not yet |

## Scene map

Which diagram (and reveal stage) or recording passage each chapter uses.

| # | Chapter | Visual |
|---|---|---|
| 0 | What does a model need to become a useful agent? | Motion intro, then `dg-harness-layers` s1 |
| 1 | Harness engineering explained | `dg-harness-layers` s1 → s8; the site's task table; skills strip |
| 2 | Microsoft Copilot harness | `dg-harness-ownership` s1 → s8; the three-way comparison from the Copilot harness page |
| 3 | What is Microsoft Foundry? | `dg-foundry-map` s1 → s8, then zooms on individual areas |
| 4 | Resource vs project, and who can build | `dg-foundry-resource-project` s1 → s5; `dg-roles-identities` s1 → s4 |
| 5 | Create the resource and project | Recording: create form, region choice, default project, deployment details |
| 6 | Check what was created | Recording: resource overview, resource endpoint, projects list, resource group |
| 7 | Portal tour and access check | Recording: Foundry home (project endpoint), model catalog, access check, harness checkbox |
| 8 | What we built, and what's next | `dg-foundry-resource-project` with our names; `dg-harness-ownership` with Episode 2 tags |

## Verification checklist (from the recording)

- [x] One deployment created two items: the Foundry resource and its default project
- [x] The resource is kind AIServices, in Canada Central
- [x] The resource endpoint (Keys and Endpoint) and the project endpoint (Foundry home) are both visible; keys stay masked
- [x] The default project is listed under Projects
- [x] Building works: Build › Agents shows "Create your first agent" (after the Foundry User role was assigned)
- [x] The Copilot harness option is visible in "Create an agent"; no agent was created and no model was deployed

## Resources created in the demo (kept for Episode 2)

- Resource group `rg-techshipped-foundry`, region Canada Central
- Foundry resource `techshipped-foundry-01`
- Default project `techshipped-agents`

## Next episode

Episode 2 deploys a compatible model and builds the first Copilot harness agent on this project, defined in code
in `code/`.
