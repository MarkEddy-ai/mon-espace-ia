# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

html_file = Path("livre_kdp_interieur.html").resolve()
pdf_file = Path("livre_kdp_interieur.pdf").resolve()

print(f"📖 Compilation Playwright de {html_file.name} vers {pdf_file.name}...")

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
        path=str(pdf_file),
        width="6in",
        height="9in",
        print_background=True,
        prefer_css_page_size=True,
        margin={"top": "0in", "bottom": "0in", "left": "0in", "right": "0in"}
    )
    browser.close()

print(f"✅ PDF intérieur 6x9 généré : {pdf_file} ({pdf_file.stat().st_size / 1024:.1f} Ko)")
