"""
AGENT INTÉRIEUR DE LIVRE ACADÉMIQUE (MarkEddy Interior Engine)
Compile le texte, les tableaux et les têtes de chapitres au standard 6x9 KDP.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

DOSSIER_SORTIE = Path("interieurs_finaux")
DOSSIER_SORTIE.mkdir(exist_ok=True)

def fabriquer_interieur(
    fichier_html="template_interior.html",
    titre_livre="Maîtriser ses Finances Personnelles",
    largeur_po=6.0,
    hauteur_po=9.0
):
    html_path = Path(fichier_html)
    if not html_path.exists():
        print(f"❌ Gabarit introuvable : {fichier_html}")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        code_html = f.read()

    code_html = code_html.replace("{{TITRE_LIVRE}}", titre_livre)

    temp_html = Path("temp_rendered_interior.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(code_html)

    sortie_pdf = DOSSIER_SORTIE / f"Interieur_{largeur_po}x{hauteur_po}.pdf"

    print("=" * 70)
    print("📖 COMPILATION TYPOGRAPHIQUE DU MANUSCRIT INTÉRIEUR")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(temp_html.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(800)

        page.pdf(
            path=str(sortie_pdf),
            width=f"{largeur_po}in",
            height=f"{hauteur_po}in",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"}
        )
        browser.close()

    print(f"✅ Manuscrit intérieur prêt pour KDP : {sortie_pdf.resolve()}")
    print("=" * 70)

if __name__ == "__main__":
    fabriquer_interieur()
