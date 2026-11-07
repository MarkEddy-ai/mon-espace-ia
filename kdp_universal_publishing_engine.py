"""
Moteur Typographique et Éditorial Universel KDP (MarkEddy Publishing Engine).
Formats supportés : 6x9, 5.5x8.5, 5x8, 8.5x8.5, 8.5x11, 7x10.
Thèmes supportés   : NON_FICTION, ROMAN, SCIENTIFIQUE, ENFANT_EDUCATIF, COLORIAGE_WORKBOOK.
"""

import sys
import argparse
from pathlib import Path
import markdown

# ==============================================================================
# 1. BIBLIOTHÈQUE DES FORMATS STANDARDS (KDP & INGRAMSPARK)
# ==============================================================================
FORMATS_LIVRES = {
    "6x9": {
        "nom": "Standard Broché (6 x 9 po)",
        "largeur_in": 6.0,
        "hauteur_in": 9.0,
        "marge_interieure_in": 0.85,
        "marge_exterieure_in": 0.65,
        "marge_haut_in": 0.80,
        "marge_bas_in": 0.80,
    },
    "5.5x8.5": {
        "nom": "Roman / Digest (5.5 x 8.5 po)",
        "largeur_in": 5.5,
        "hauteur_in": 8.5,
        "marge_interieure_in": 0.75,
        "marge_exterieure_in": 0.55,
        "marge_haut_in": 0.70,
        "marge_bas_in": 0.70,
    },
    "5x8": {
        "nom": "Poche / Pocket (5 x 8 po)",
        "largeur_in": 5.0,
        "hauteur_in": 8.0,
        "marge_interieure_in": 0.70,
        "marge_exterieure_in": 0.50,
        "marge_haut_in": 0.65,
        "marge_bas_in": 0.65,
    },
    "8.5x8.5": {
        "nom": "Carré Illustré / Enfants (8.5 x 8.5 po)",
        "largeur_in": 8.5,
        "hauteur_in": 8.5,
        "marge_interieure_in": 0.60,
        "marge_exterieure_in": 0.60,
        "marge_haut_in": 0.60,
        "marge_bas_in": 0.60,
    },
    "8.5x11": {
        "nom": "Grand Format / Coloriage / Workbook (8.5 x 11 po)",
        "largeur_in": 8.5,
        "hauteur_in": 11.0,
        "marge_interieure_in": 0.75,
        "marge_exterieure_in": 0.50,
        "marge_haut_in": 0.60,
        "marge_bas_in": 0.60,
    },
    "7x10": {
        "nom": "Manuel Académique (7 x 10 po)",
        "largeur_in": 7.0,
        "hauteur_in": 10.0,
        "marge_interieure_in": 0.85,
        "marge_exterieure_in": 0.65,
        "marge_haut_in": 0.75,
        "marge_bas_in": 0.75,
    }
}

# ==============================================================================
# 2. BIBLIOTHÈQUE DES THÉMATIQUES & CHARTES GRAPHIQUES
# ==============================================================================
THEMATIQUES_STYLES = {
    "NON_FICTION": {
        "description": "Business, finances, développement personnel, productivité",
        "font_titre": "'Cinzel', 'Trajan Pro', serif",
        "font_corps": "'EB Garamond', 'Garamond', serif",
        "couleur_primaire": "#0F172A",
        "couleur_accent": "#D97706",
        "taille_corps": "10.5pt",
        "interligne": "1.5",
        "lettrine": True,
        "encadres": "cadre_noble"
    },
    "ROMAN": {
        "description": "Littérature, fiction générale, thriller, romance, fantasy",
        "font_titre": "'Baskerville', 'Playfair Display', serif",
        "font_corps": "'Baskerville', 'Georgia', serif",
        "couleur_primaire": "#1A1A1A",
        "couleur_accent": "#4A5568",
        "taille_corps": "11pt",
        "interligne": "1.45",
        "lettrine": True,
        "encadres": "sobre"
    },
    "SCIENTIFIQUE": {
        "description": "Physique, informatique, biologie, manuels techniques",
        "font_titre": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "font_corps": "'Times New Roman', 'Liberation Serif', serif",
        "couleur_primaire": "#1E293B",
        "couleur_accent": "#0284C7",
        "taille_corps": "10pt",
        "interligne": "1.4",
        "lettrine": False,
        "encadres": "technique"
    },
    "ENFANT_EDUCATIF": {
        "description": "Contes, histoires illustrées, apprentissage jeunesse",
        "font_titre": "'Quicksand', 'Nunito', 'Comic Sans MS', sans-serif",
        "font_corps": "'Quicksand', 'Arial', sans-serif",
        "couleur_primaire": "#1E1B4B",
        "couleur_accent": "#E11D48",
        "taille_corps": "14pt",
        "interligne": "1.65",
        "lettrine": False,
        "encadres": "ludique"
    },
    "COLORIAGE_WORKBOOK": {
        "description": "Coloring books, carnets de notes, livres d'activités",
        "font_titre": "'Montserrat', sans-serif",
        "font_corps": "'Arial', sans-serif",
        "couleur_primaire": "#000000",
        "couleur_accent": "#666666",
        "taille_corps": "12pt",
        "interligne": "1.8",
        "lettrine": False,
        "encadres": "contours_blancs"
    }
}


def construire_css(format_cle: str, thematique_cle: str) -> str:
    fmt = FORMATS_LIVRES.get(format_cle, FORMATS_LIVRES["6x9"])
    sty = THEMATIQUES_STYLES.get(thematique_cle, THEMATIQUES_STYLES["NON_FICTION"])

    css = f"""
    @page {{
        size: {fmt['largeur_in']}in {fmt['hauteur_in']}in;
        margin-top: {fmt['marge_haut_in']}in;
        margin-bottom: {fmt['marge_bas_in']}in;
        @bottom-center {{
            content: counter(page);
            font-family: {sty['font_corps']};
            font-size: 9pt;
            color: #64748B;
        }}
    }}

    @page :left {{
        margin-left: {fmt['marge_exterieure_in']}in;
        margin-right: {fmt['marge_interieure_in']}in;
        @top-center {{
            content: string(titre-livre);
            font-family: {sty['font_titre']};
            font-size: 8pt;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: #64748B;
            border-bottom: 0.5pt solid #CBD5E1;
            padding-bottom: 3px;
        }}
    }}

    @page :right {{
        margin-left: {fmt['marge_interieure_in']}in;
        margin-right: {fmt['marge_exterieure_in']}in;
        @top-center {{
            content: string(titre-chapitre);
            font-family: {sty['font_titre']};
            font-size: 8pt;
            font-style: italic;
            color: #64748B;
            border-bottom: 0.5pt solid #CBD5E1;
            padding-bottom: 3px;
        }}
    }}

    body {{
        font-family: {sty['font_corps']};
        font-size: {sty['taille_corps']};
        line-height: {sty['interligne']};
        color: {sty['couleur_primaire']};
        text-align: justify;
        hyphens: auto;
        orphans: 3;
        widows: 3;
    }}

    .meta-titre {{
        string-set: titre-livre content();
        display: none;
    }}

    h1 {{
        page-break-before: always;
        string-set: titre-chapitre content();
        font-family: {sty['font_titre']};
        text-align: center;
        color: {sty['couleur_primaire']};
        margin-top: 1.8in;
        margin-bottom: 1.2in;
    }}

    h2 {{
        font-family: {sty['font_titre']};
        color: {sty['couleur_primaire']};
        margin-top: 1.6em;
        margin-bottom: 0.6em;
        page-break-after: avoid;
    }}

    p {{
        margin: 0;
        text-indent: 1.4em;
    }}

    h1 + p, h2 + p, hr + p, blockquote + p {{
        text-indent: 0;
    }}
    """

    if sty["lettrine"]:
        css += f"""
        p.lettrine::first-letter {{
            font-family: {sty['font_titre']};
            float: left;
            font-size: 3.4em;
            line-height: 0.8;
            margin-top: 0.1em;
            margin-right: 0.15em;
            color: {sty['couleur_primaire']};
            font-weight: bold;
        }}
        """

    if sty["encadres"] == "cadre_noble":
        css += f"""
        blockquote {{
            page-break-inside: avoid;
            margin: 1.6em 0.8em;
            padding: 1.2em 1.4em;
            background: #F8FAFC;
            border-left: 3pt solid {sty['couleur_accent']};
            font-size: 9.8pt;
        }}
        """
    elif sty["encadres"] == "technique":
        css += """
        blockquote {{
            page-break-inside: avoid;
            margin: 1.5em 0;
            padding: 10px 15px;
            background: #F1F5F9;
            border: 1px solid #CBD5E1;
            font-family: monospace;
            font-size: 9pt;
        }}
        """
    elif sty["encadres"] == "ludique":
        css += f"""
        blockquote {{
            page-break-inside: avoid;
            margin: 1.5em 0;
            padding: 15px;
            background: #FEF2F2;
            border: 2px dashed {sty['couleur_accent']};
            border-radius: 12px;
        }}
        """

    return css


def compiler_livre_sur_mesure(chemin_manuscrit: str, chemin_sortie_html: str, format_choisi: str, thematique_choisie: str, titre_livre: str):
    source = Path(chemin_manuscrit)
    sortie = Path(chemin_sortie_html)

    if not source.exists():
        print(f"❌ Erreur : Fichier source introuvable -> {source.resolve()}")
        return

    print("=" * 70)
    print("📚 MOTEUR TYPOGRAPHIQUE UNIVERSEL KDP (MarkEddy)")
    print("=" * 70)
    print(f"📖 Format retenu       : {FORMATS_LIVRES.get(format_choisi, {}).get('nom', format_choisi)}")
    print(f"🎨 Charte éditoriale   : {thematique_choisie}")
    print(f"📄 Manuscrit source    : {source.name}")

    texte_source = source.read_text(encoding="utf-8")

    if THEMATIQUES_STYLES.get(thematique_choisie, {}).get("lettrine", False):
        lignes = texte_source.splitlines()
        lignes_traitees = []
        flag_h1 = False
        for l in lignes:
            l_strip = l.strip()
            if l_strip.startswith("# Chapitre") or (l_strip.startswith("# ") and not lignes_traitees):
                flag_h1 = True
                lignes_traitees.append(l)
                continue
            if flag_h1 and l_strip and not l_strip.startswith("#") and not l_strip.startswith(">"):
                lignes_traitees.append(f'<p class="lettrine">{l_strip}</p>')
                flag_h1 = False
                continue
            lignes_traitees.append(l)
        texte_source = "\n".join(lignes_traitees)

    html_corps = markdown.markdown(texte_source, extensions=["extra", "tables", "smarty"])
    css_genere = construire_css(format_choisi, thematique_choisie)

    document = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{titre_livre}</title>
    <style>{css_genere}</style>
</head>
<body>
    <div class="meta-titre">{titre_livre}</div>
    {html_corps}
</body>
</html>"""

    sortie.write_text(document, encoding="utf-8")
    print(f"✅ Maquette HTML générée : {sortie.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moteur Typographique Universel KDP")
    parser.add_argument("--format", default="6x9", help="6x9, 5.5x8.5, 5x8, 8.5x8.5, 8.5x11, 7x10")
    parser.add_argument("--theme", default="NON_FICTION", help="NON_FICTION, ROMAN, SCIENTIFIQUE, ENFANT_EDUCATIF, COLORIAGE_WORKBOOK")
    parser.add_argument("--src", default="", help="Fichier Markdown source")
    parser.add_argument("--out", default="", help="Fichier HTML de sortie")
    parser.add_argument("--titre", default="MAÎTRISER SES FINANCES PERSONNELLES - MarkEddy", help="Titre de l'ouvrage")

    args = parser.parse_args()

    if args.src and Path(args.src).exists():
        fichier_source = args.src
    elif Path("manuscrit_enrichi.md").exists():
        fichier_source = "manuscrit_enrichi.md"
    elif Path("manuscrit_ameliore.md").exists():
        fichier_source = "manuscrit_ameliore.md"
    elif Path("manuscrit_avec_preface.md").exists():
        fichier_source = "manuscrit_avec_preface.md"
    else:
        fichier_source = "manuscrit_complet.md"

    fichier_sortie = args.out if args.out else f"livre_{args.theme.lower()}_{args.format}.html"

    compiler_livre_sur_mesure(
        chemin_manuscrit=fichier_source,
        chemin_sortie_html=fichier_sortie,
        format_choisi=args.format,
        thematique_choisie=args.theme,
        titre_livre=args.titre
    )