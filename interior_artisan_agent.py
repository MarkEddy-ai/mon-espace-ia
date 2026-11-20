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
    titre_livre="NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES",
    sous_titre="Reprogrammer son cerveau en 66 jours : la méthode pas-à-pas pour éliminer la procrastination et libérer 3 heures par jour",
    auteur="MarkEddy",
    contenu_html="",
    largeur_po=6.0,
    hauteur_po=9.0,
    fichier_sortie=None
):
    html_path = Path(fichier_html)
    if not html_path.exists():
        print(f"❌ Gabarit introuvable : {fichier_html}")
        return None

    with open(html_path, "r", encoding="utf-8") as f:
        code_html = f.read()

    # Remplacement des balises de template
    code_html = code_html.replace("{{TITRE_LIVRE}}", titre_livre)
    code_html = code_html.replace("{{SOUS_TITRE}}", sous_titre)
    code_html = code_html.replace("{{AUTEUR}}", auteur)
    code_html = code_html.replace("{{CONTENU_LIVRE}}", contenu_html)

    temp_html = Path("temp_rendered_interior.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(code_html)

    if fichier_sortie:
        sortie_pdf = Path(fichier_sortie)
        sortie_pdf.parent.mkdir(parents=True, exist_ok=True)
    else:
        sortie_pdf = DOSSIER_SORTIE / f"Interieur_{largeur_po}x{hauteur_po}.pdf"

    print("=" * 70)
    print("📖 COMPILATION TYPOGRAPHIQUE DU MANUSCRIT INTÉRIEUR")
    print(f"Format : {largeur_po} x {hauteur_po} po | Cible : {sortie_pdf}")
    print("=" * 70)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="msedge")
        page = browser.new_page()
        page.goto(temp_html.resolve().as_uri(), wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_function("document.fonts.status === 'loaded'", timeout=2000)
        except Exception:
            pass
        page.wait_for_timeout(300)

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
    return sortie_pdf


if __name__ == "__main__":
    fabriquer_interieur()
