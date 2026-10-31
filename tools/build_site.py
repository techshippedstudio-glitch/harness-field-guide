#!/usr/bin/env python3
"""Build the site in docs/ from the page bodies in src/pages/.

Each source page holds only the content of <main>. This script adds the shared head, masthead, area
navigation, "next in the learning path" link and footer, so every page stays consistent.
Inside a source page, write {root} wherever a link must start from the site root (it becomes "", "../" ...).

Usage:  python3 tools/build_site.py      (then python3 tools/build_diagrams.py --png)
"""
from __future__ import annotations

import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "pages"
DOCS = ROOT / "docs"
EDITION = "0.2"

# path, nav title, page title, description, area
PAGES = [
    ("index.html", "Learning path", "Harness Field Guide",
     "Learn harness engineering and Microsoft Foundry step by step: concepts, Microsoft's implementation, "
     "episode tutorials and code, with diagrams.", "home"),
    ("concepts/harness-engineering.html", "Harness engineering", "Harness Engineering",
     "What we build around a model to make a useful agent: instructions, context, tools, execution, "
     "controls and feedback.", "concepts"),
    ("microsoft/copilot-harness.html", "Copilot harness", "The Microsoft Copilot Harness",
     "How Microsoft's managed Copilot harness in Foundry Agent Service implements the harness, and what you "
     "configure yourself.", "microsoft"),
    ("microsoft/foundry.html", "Microsoft Foundry", "Microsoft Foundry Capabilities",
     "Where models, agents, tools, knowledge, evaluation and operations fit together in Microsoft Foundry.",
     "microsoft"),
    ("microsoft/resources-projects.html", "Resources and projects", "Foundry Resources and Projects",
     "How an Azure environment for Microsoft Foundry is organised: subscription, resource group, Foundry "
     "resource and projects.", "microsoft"),
    ("microsoft/roles-identities.html", "Roles and identities", "Foundry Roles and Identities",
     "Who can manage Foundry, who can build in a project, and how an agent gets access to other services.",
     "microsoft"),
    ("episodes/ep01.html", "Episode 1", "Episode 1: Foundry from Zero",
     "Episode 1 tutorial: from harness engineering to a Microsoft Foundry resource and default project, "
     "created and checked in the Azure portal.", "episodes"),
    ("code/index.html", "Code and examples", "Code and Examples",
     "Runnable samples and setup instructions for each episode, with the versions they were tested on.",
     "code"),
]

AREAS = [  # key, label, first page
    ("concepts", "Concepts", "concepts/harness-engineering.html"),
    ("microsoft", "Microsoft", "microsoft/copilot-harness.html"),
    ("episodes", "Episodes", "episodes/ep01.html"),
    ("code", "Code", "code/index.html"),
]

# The learning path, in order. Each page links to the next one.
PATH = [
    "concepts/harness-engineering.html",
    "microsoft/copilot-harness.html",
    "microsoft/foundry.html",
    "microsoft/resources-projects.html",
    "microsoft/roles-identities.html",
    "episodes/ep01.html",
]

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wght@500..900&family=IBM+Plex+Mono:wght@400;500"
         "&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap")


def page(path: str, nav_title: str, title: str, desc: str, area: str, body: str) -> str:
    depth = path.count("/")
    root = "../" * depth
    full_title = title if path == "index.html" else f"{title} · Harness Field Guide"
    nav = []
    for key, label, first in AREAS:
        cur = ' aria-current="page"' if key == area else ""
        nav.append(f'<a href="{root}{first}"{cur}>{label}</a>')
    sub = ""
    siblings = [p for p in PAGES if p[4] == area and area != "home"]
    if len(siblings) > 1:
        items = []
        for p in siblings:
            cur = ' aria-current="page"' if p[0] == path else ""
            items.append(f'<a href="{root}{p[0]}"{cur}>{html.escape(p[1])}</a>')
        sub = f'<nav class="subnav" aria-label="In this area">{"".join(items)}</nav>'
    nxt = ""
    if path in PATH and PATH.index(path) < len(PATH) - 1:
        n = PATH[PATH.index(path) + 1]
        meta = next(p for p in PAGES if p[0] == n)
        step = PATH.index(path) + 2
        nxt = (f'<a class="next" href="{root}{n}"><span class="label">Next in the learning path · step {step} of '
               f'{len(PATH)}</span><span class="next-title">{html.escape(meta[2])} →</span></a>')
    body = body.replace("{root}", root)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
  <header class="mast">
    <a class="lockup" href="{root or './'}">
      <span class="wordmark">Techshipped<br>Studio</span>
      <span class="sitename">Harness Field Guide</span>
      <span class="stamp">ED. {EDITION}</span>
    </a>
    <nav aria-label="Site">{''.join(nav)}</nav>
  </header>
  {sub}
  <main id="main">
{body}
  {nxt}
  </main>
  <footer>
    <span class="wordmark">Techshipped Studio</span>
    <span>Explore. Understand. Build.</span>
    <span>Independent guide; not affiliated with Microsoft.</span>
  </footer>
</div>
</body>
</html>
"""


def main() -> None:
    for path, nav_title, title, desc, area in PAGES:
        src = SRC / path
        body = src.read_text(encoding="utf-8")
        out = DOCS / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(path, nav_title, title, desc, area, body), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
