"""
Compilateur Universel HTML vers PDF d'impression KDP via Playwright / Chromium.
Prend en charge tous les formats de découpe KDP (6x9, 8.5x8.5, 8.5x11, 5.5x8.5, 7x10).
"""

import sys
import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright

DIMENSIONS_PAGES = {
    "6x9": {"w": "6in", "h": "9in"},
    "5.5x8.5": {"w": "5.5in", "h": "8.5in"},
    "5x8": {"w": "5in", "h": "8in"},
    "8.5x8.5": {"w": "8.5in", "h": "8.5in"},
    "8.5x11": {"w": "8.5in", "h": "11in"},
    "7x10": {"w": "7in", "h": "10in"}
}

async def compiler(fichier_html: str, format_nom: str, fichier_pdf: str = None):
    source = Path(fichier_html)
    if not source.exists():
        print(f"❌ Fichier source introuvable : {source.resolve()}")
        return

    cible = Path(fichier_pdf) if fichier_pdf else source.with_suffix(".pdf")
    dims = DIMENSIONS_PAGES.get(format_nom, {"w": "6in", "h": "9in"})

    print("=" * 65)
    print("🖨️  COMPILATION PDF PRE-PRESSE KDP (PLAYWRIGHT)")
    print("=" * 65)
    print(f"📄 Source HTML : {source.name}")
    print(f"📐 Format KDP  : {format_nom} ({dims['w']} x {dims['h']})")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(source.resolve().as_uri(), wait_until="networkidle")

        await page.pdf(
            path=str(cible),
            width=dims["w"],
            height=dims["h"],
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=False
        )
        await browser.close()

    print(f"✅ PDF Haute Définition généré : {cible.resolve()}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertisseur HTML vers PDF KDP")
    parser.add_argument("html", nargs="?", default="livre_non_fiction_6x9.html", help="Fichier HTML à convertir")
    parser.add_argument("--format", default="6x9", help="6x9, 5.5x8.5, 5x8, 8.5x8.5, 8.5x11, 7x10")
    parser.add_argument("--out", default=None, help="Nom du fichier PDF en sortie")

    args = parser.parse_args()
    asyncio.run(compiler(args.html, args.format, args.out))