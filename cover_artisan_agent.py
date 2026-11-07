"""
MOTEUR COUVERTURE KDP - MULTI-THÉMATIQUES STABLE (MarkEddy Production)
"""

from pathlib import Path
from pypdf import PdfReader
from playwright.sync_api import sync_playwright

FOND_PERDU = 0.125
COEFF_PAPIER = 0.002252

DOSSIER_SORTIE = Path("couvertures_finales")
DOSSIER_SORTIE.mkdir(exist_ok=True)

# LES 6 THÉMATIQUES AVEC LEURS PALETTES STABLES
PALETTES = {
    "FINANCE": {
        "base": "#1a0f0a",
        "accent": "#e5b869",
        "degrade": "radial-gradient(circle at 75% 32%, rgba(229, 184, 105, 0.22) 0%, transparent 48%), radial-gradient(circle at 25% 65%, rgba(180, 83, 9, 0.15) 0%, transparent 45%), radial-gradient(circle at 50% 50%, #291811 0%, #0f0704 100%)",
        "badge": "Édition Masterclass"
    },
    "TECH_IA": {
        "base": "#020617",
        "accent": "#38bdf8",
        "degrade": "radial-gradient(circle at 75% 32%, rgba(56, 189, 248, 0.22) 0%, transparent 50%), radial-gradient(circle at 25% 65%, rgba(99, 102, 241, 0.16) 0%, transparent 45%), radial-gradient(circle at 50% 50%, #0b1329 0%, #020617 100%)",
        "badge": "Protocole Technologique"
    },
    "MINDSET": {
        "base": "#09090b",
        "accent": "#f59e0b",
        "degrade": "radial-gradient(circle at 75% 32%, rgba(245, 158, 11, 0.20) 0%, transparent 48%), radial-gradient(circle at 25% 65%, rgba(217, 119, 6, 0.12) 0%, transparent 45%), radial-gradient(circle at 50% 50%, #1c1917 0%, #09090b 100%)",
        "badge": "Guide d'Excellence"
    },
    "SANTE": {
        "base": "#04150f",
        "accent": "#10b981",
        "degrade": "radial-gradient(circle at 75% 32%, rgba(16, 185, 129, 0.20) 0%, transparent 48%), radial-gradient(circle at 25% 65%, rgba(5, 150, 105, 0.14) 0%, transparent 45%), radial-gradient(circle at 50% 50%, #062e22 0%, #020b08 100%)",
        "badge": "Science & Santé"
    },
    "IMMOBILIER": {
        "base": "#0c1524",
        "accent": "#38bdf8",
        "degrade": "radial-gradient(circle at 75% 32%, rgba(56, 189, 248, 0.18) 0%, transparent 48%), radial-gradient(circle at 25% 65%, rgba(229, 184, 105, 0.14) 0%, transparent 45%), radial-gradient(circle at 50% 50%, #152238 0%, #070d18 100%)",
        "badge": "Stratégie Immobilière"
    },
    "PHILOSOPHIE": {
        "base": "#140e1b",
        "accent": "#c084fc",
        "degrade": "radial-gradient(circle at 75% 32%, rgba(192, 132, 252, 0.20) 0%, transparent 48%), radial-gradient(circle at 25% 65%, rgba(147, 51, 234, 0.15) 0%, transparent 45%), radial-gradient(circle at 50% 50%, #20152c 0%, #0a060f 100%)",
        "badge": "Traité de Réflexion"
    }
}


def fabriquer(
    pdf_interieur="livre_ultra_moderne.pdf",
    thematique="FINANCE",
    titre="MAÎTRISER SES\nFINANCES\nPERSONNELLES",
    sous_titre="Méthode académique, stratégies d'investissement\net tableau de bord complet",
    titre_arriere="BÂTIR UNE AUTONOMIE<br>FINANCIÈRE DURABLE",
    pitch_arriere="Une approche méthodique, structurée et chiffrée pour maîtriser, allouer et valoriser votre capital. Conçu pour éliminer l'incertitude et appliquer des protocoles d'investissement rigoureux."
):
    pdf_path = Path(pdf_interieur)
    if not pdf_path.exists():
        print(f"❌ Intérieur introuvable : {pdf_interieur}")
        return

    # 1. Analyse automatique du PDF
    reader = PdfReader(pdf_path)
    nb_pages = len(reader.pages)
    box = reader.pages[0].mediabox
    largeur_po = round(float(box.width) / 72.0, 2)
    hauteur_po = round(float(box.height) / 72.0, 2)

    largeur_tranche_po = nb_pages * COEFF_PAPIER
    largeur_totale_po = (FOND_PERDU * 2) + (largeur_po * 2) + largeur_tranche_po
    hauteur_totale_po = (FOND_PERDU * 2) + hauteur_po
    largeur_panel_po = largeur_po + FOND_PERDU
    tranche_font_in = max(0.12, round(largeur_tranche_po * 0.35, 3))

    palette = PALETTES.get(thematique.upper(), PALETTES["FINANCE"])

    with open("template_cover.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remplacement des dimensions
    html = html.replace("{{LARGEUR_TOTALE_IN}}", f"{largeur_totale_po:.4f}")
    html = html.replace("{{HAUTEUR_TOTALE_IN}}", f"{hauteur_totale_po:.4f}")
    html = html.replace("{{LARGEUR_PANEL_IN}}", f"{largeur_panel_po:.4f}")
    html = html.replace("{{LARGEUR_TRANCHE_IN}}", f"{largeur_tranche_po:.4f}")
    html = html.replace("{{TRANCHE_FONT_IN}}", f"{tranche_font_in:.3f}")

    # Remplacement des textes
    html = html.replace("{{TITRE}}", titre.replace("\n", "<br>"))
    html = html.replace("{{TITRE_TRANCHE}}", titre.replace("\n", " "))
    html = html.replace("{{SOUS_TITRE}}", sous_titre.replace("\n", "<br>"))
    html = html.replace("{{TITRE_ARRIERE}}", titre_arriere)
    html = html.replace("{{SOUS_TITRE_ARRIERE}}", palette["badge"])
    html = html.replace("{{PITCH_ARRIERE}}", pitch_arriere)

    # Remplacement des couleurs
    html = html.replace("{{COULEUR_FOND_BASE}}", palette["base"])
    html = html.replace("{{COULEUR_ACCENT}}", palette["accent"])
    html = html.replace("{{DEGRADE_AMBIANCE}}", palette["degrade"])

    temp_file = Path("temp_rendered_cover.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(html)

    sortie_pdf = DOSSIER_SORTIE / f"Couverture_{thematique.upper()}_{largeur_po}x{hauteur_po}_{nb_pages}p.pdf"

    vw = int(round(largeur_totale_po * 120))
    vh = int(round(hauteur_totale_po * 120))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": vw, "height": vh})
        page.goto(temp_file.resolve().as_uri(), wait_until="load")
        page.wait_for_selector(".hero-title-3d")
        page.wait_for_timeout(500)

        page.pdf(
            path=str(sortie_pdf),
            width=f"{largeur_totale_po:.4f}in",
            height=f"{hauteur_totale_po:.4f}in",
            print_background=True,
            page_ranges="1",
            margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"}
        )
        browser.close()

    print(f"✅ Couverture {thematique.upper()} générée : {sortie_pdf.resolve()}")


if __name__ == "__main__":
    # Changez simplement la thématique ici pour tester :
    # "FINANCE", "TECH_IA", "MINDSET", "SANTE", "IMMOBILIER", "PHILOSOPHIE"
    fabriquer(
        pdf_interieur="livre_ultra_moderne.pdf",
        thematique="FINANCE"
    )