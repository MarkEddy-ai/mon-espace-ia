# -*- coding: utf-8 -*-
from pathlib import Path
from playwright.sync_api import sync_playwright

html_file = Path("livre_kdp_interieur.html").resolve()
pdf_interactif = Path("livre_numerique_interactif.pdf").resolve()

print(f"📱 Compilation du PDF Numérique Interactif depuis {html_file.name}...")

with sync_playwright() as p:
    try:
        browser = p.chromium.launch()
    except Exception:
        browser = p.chromium.launch(channel="msedge")
    page = browser.new_page()
    page.goto(html_file.as_uri(), wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_function("document.fonts.status === 'loaded'", timeout=5000)
    except Exception:
        pass
    page.wait_for_timeout(500)
    page.pdf(
        path=str(pdf_interactif),
        format="A4",
        print_background=True,
        prefer_css_page_size=False,
        margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
    )
    browser.close()

print(f"✅ PDF Numérique Interactif généré : {pdf_interactif} ({pdf_interactif.stat().st_size / 1024:.1f} Ko)")
