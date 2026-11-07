import asyncio
from pathlib import Path

async def html_vers_pdf(fichier_html_path: str = "livre_kdp_interieur.html", fichier_pdf_path: str = "livre_kdp_interieur.pdf"):
    """
    Convertit le document HTML Haute Couture en PDF 6x9 pouces prêt pour Amazon KDP
    en utilisant Playwright (moteur Chromium ou Edge local).
    """
    fichier_html = Path(fichier_html_path).resolve()
    fichier_pdf = Path(fichier_pdf_path).resolve()

    if not fichier_html.exists():
        print(f"❌ Fichier {fichier_html_path} introuvable.")
        print("Générez-le d'abord avec 'python kdp_formatter.py'.")
        return False

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright n'est pas encore installé.")
        print("Pour l'installer dans votre environnement :")
        print("   pip install playwright")
        print("   playwright install chromium")
        return False

    print("🚀 Lancement du moteur Chromium/Edge pour le rendu vectoriel KDP 6x9...", flush=True)
    
    async with async_playwright() as p:
        navigateur = None
        # 1. Essai avec Chromium Playwright (timeout de 8s pour éviter tout blocage en environnement restreint)
        try:
            navigateur = await asyncio.wait_for(p.chromium.launch(), timeout=8.0)
        except Exception:
            # 2. Repli immédiat sur Microsoft Edge local
            try:
                print("ℹ️  Utilisation du canal Microsoft Edge local...", flush=True)
                navigateur = await asyncio.wait_for(p.chromium.launch(channel="msedge"), timeout=8.0)
            except Exception as e:
                print(f"ℹ️  Navigateur Playwright non disponible immédiatement : {e}", flush=True)
                return False

        page = await navigateur.new_page()
        uri_fichier = fichier_html.as_uri()
        await page.goto(uri_fichier, wait_until="domcontentloaded")

        # Format 6x9 pouces strict KDP : 6in = 152.4mm, 9in = 228.6mm
        await page.pdf(
            path=str(fichier_pdf),
            width="6in",
            height="9in",
            print_background=True,
            prefer_css_page_size=True
        )
        await navigateur.close()

    print(f"✅ PDF KDP 6x9 généré avec succès : {fichier_pdf}", flush=True)
    return True

def convertir():
    """Point d'entrée synchrone."""
    return asyncio.run(html_vers_pdf())

if __name__ == "__main__":
    convertir()
