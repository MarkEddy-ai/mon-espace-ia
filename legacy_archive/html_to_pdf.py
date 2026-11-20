"""
html_to_pdf.py - Moteur de rendu vectoriel HTML vers PDF 6x9 pouces KDP.
Exécution sécurisée en sous-processus isolé avec timeout strict anti-blocage.
"""

import sys
import subprocess
from pathlib import Path

def convertir(fichier_html_path: str = "livre_kdp_interieur.html", fichier_pdf_path: str = "livre_kdp_interieur.pdf") -> bool:
    """
    Convertit le document HTML Haute Couture en PDF 6x9 pouces prêt pour Amazon KDP.
    Utilise un sous-processus isolé avec un timeout strict pour garantir qu'aucun
    blocage de boucle d'événement (asyncio) ou de stratégie d'application ne fige l'orchestrateur.
    """
    f_html = Path(fichier_html_path).resolve()
    f_pdf = Path(fichier_pdf_path).resolve()

    if not f_html.exists():
        print(f"❌ Fichier intérieur HTML introuvable : {f_html}")
        return False

    script_worker = f"""
import sys
import asyncio
from pathlib import Path

async def generer():
    try:
        from playwright.async_api import async_playwright
    except Exception:
        sys.exit(1)

    f_html = Path({repr(str(f_html))})
    f_pdf = Path({repr(str(f_pdf))})

    try:
        async with async_playwright() as p:
            browser = None
            try:
                browser = await asyncio.wait_for(p.chromium.launch(), timeout=3.0)
            except Exception:
                try:
                    browser = await asyncio.wait_for(p.chromium.launch(channel="msedge"), timeout=3.0)
                except Exception:
                    sys.exit(2)

            page = await browser.new_page()
            await page.goto(f_html.as_uri(), wait_until="domcontentloaded")
            await page.pdf(
                path=str(f_pdf),
                width="6in",
                height="9in",
                print_background=True,
                prefer_css_page_size=True
            )
            await browser.close()
            sys.exit(0)
    except Exception:
        sys.exit(3)

if __name__ == "__main__":
    try:
        asyncio.run(generer())
    except Exception:
        sys.exit(4)
"""

    try:
        res = subprocess.run(
            [sys.executable, "-u", "-c", script_worker],
            timeout=4.0,
            capture_output=True
        )
        if res.returncode == 0 and f_pdf.exists():
            print(f"✅ Rendu vectoriel PDF 6x9 po réussi : {f_pdf.resolve()}")
            return True
        else:
            return False
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

if __name__ == "__main__":
    succes = convertir()
    print("Résultat conversion :", succes)
