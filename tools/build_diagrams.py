#!/usr/bin/env python3
"""Export the site's diagrams as standalone files for the videos and for download.

Every diagram lives once, inline in a page under docs/, as <svg id="dg-...">. Its look comes from the
"svg drawing classes" block in docs/assets/site.css. This script:

  1. finds every <svg id="dg-..."> in docs/*.html,
  2. writes docs/diagrams/<id>-light.svg and <id>-dark.svg: colours resolved from the site's light and dark
     tokens, a background, and the brand fonts embedded, so the files look right anywhere,
  3. with --png, renders exports/<id>-<theme>.png at 1920 px wide for the video pipeline, plus
     exports/stages/<id>-<theme>-s<k>.png for diagrams whose groups carry data-stage="k": frame k shows
     stages 1..k, for staged reveals in the video (exports/ is not published).

Usage:  python3 tools/build_diagrams.py [--png]
"""
from __future__ import annotations

import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FONTS = ROOT / "tools" / "fonts"
OUT_SVG = DOCS / "diagrams"
OUT_PNG = ROOT / "exports"

FONT_FACES = [  # family, file, weight range
    ("Archivo", "archivo-latin-wght-normal.woff2", "100 900"),
    ("Source Serif 4", "source-serif-4-latin-wght-normal.woff2", "200 900"),
    ("IBM Plex Mono", "ibm-plex-mono-latin-400-normal.woff2", "400"),
    ("IBM Plex Mono", "ibm-plex-mono-latin-500-normal.woff2", "500"),
]


def block(css: str, selector: str) -> str:
    """Body of the first rule whose selector is exactly `selector` (top level or inside a media query)."""
    m = re.search(re.escape(selector) + r"\s*\{([^{}]*)\}", css)
    if not m:
        sys.exit(f"selector not found in site.css: {selector}")
    return m.group(1)


def tokens(body: str) -> dict[str, str]:
    return {k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body)}


def font_css() -> str:
    out = []
    for family, file, weight in FONT_FACES:
        path = FONTS / file
        if not path.exists():
            print(f"warning: {path.name} missing; exported SVGs will fall back to system fonts")
            continue
        data = base64.b64encode(path.read_bytes()).decode()
        out.append(f'@font-face{{font-family:"{family}";font-weight:{weight};font-style:normal;'
                   f'src:url(data:font/woff2;base64,{data}) format("woff2")}}')
    return "\n".join(out)


def main() -> None:
    css = (DOCS / "assets" / "site.css").read_text(encoding="utf-8")
    themes = {
        "light": tokens(block(css, ":root")),
        "dark": {**tokens(block(css, ":root")), **tokens(block(css, ':root[data-theme="dark"]'))},
    }
    start = css.index("/* svg drawing classes")
    end = css.index("/* level matrix")
    rules = css[start:end]
    rules = rules[rules.index("*/") + 2:]
    fonts = font_css()

    OUT_SVG.mkdir(exist_ok=True)
    written: list[pathlib.Path] = []
    for page in sorted(DOCS.glob("**/*.html")):
        html = page.read_text(encoding="utf-8")
        for m in re.finditer(r'<svg id="(dg-[\w-]+)"(.*?)</svg>', html, re.S):
            dg_id, inner = m.group(1), m.group(2)
            vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', inner)
            w, h = vb.groups()
            for theme, toks in themes.items():
                def var(mm: re.Match) -> str:
                    return toks[mm.group(1)]
                resolved = re.sub(r"var\((--[\w-]+)\)", var, rules)
                bg = toks["--paper"]
                svg = (f'<svg xmlns="http://www.w3.org/2000/svg" id="{dg_id}"{inner.split(">", 1)[0]}>'
                       f"<style>\n{fonts}\n{resolved}</style>"
                       f'<rect width="{w}" height="{h}" fill="{bg}"/>'
                       f"{inner.split('>', 1)[1]}</svg>\n")
                out = OUT_SVG / f"{dg_id}-{theme}.svg"
                out.write_text(svg, encoding="utf-8")
                written.append(out)
                print(f"wrote {out.relative_to(ROOT)} ({len(svg) // 1024} KB)")

    if "--png" in sys.argv:
        from playwright.sync_api import sync_playwright
        OUT_PNG.mkdir(exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            stage_dir = OUT_PNG / "stages"
            stage_dir.mkdir(exist_ok=True)
            for svg_path in written:
                text = svg_path.read_text(encoding="utf-8")
                vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', text)
                w, h = (int(x) for x in vb.groups())
                page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1920 / w)
                page.goto(svg_path.as_uri())
                page.wait_for_timeout(300)
                png = OUT_PNG / (svg_path.stem + ".png")
                page.screenshot(path=str(png))
                print(f"wrote {png.relative_to(ROOT)}")
                stages = sorted({int(n) for n in re.findall(r'data-stage="(\d+)"', text)})
                for k in stages:
                    page.evaluate(
                        "k => document.querySelectorAll('[data-stage]').forEach("
                        "g => g.style.visibility = (+g.dataset.stage <= k) ? 'visible' : 'hidden')", k)
                    page.screenshot(path=str(stage_dir / f"{svg_path.stem}-s{k}.png"))
                if stages:
                    print(f"  + {len(stages)} stage frames")
                page.close()
            browser.close()


if __name__ == "__main__":
    main()
