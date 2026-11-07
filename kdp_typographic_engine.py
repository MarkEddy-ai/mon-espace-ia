"""
Moteur Typographique & Directeur Artistique Print KDP (Format 6x9 pouces).
Génère une mise en page Haute Couture : lettrines, en-têtes courants alternés,
justification parfaite, césures douces et ornementation éditoriale.
"""

import re
from pathlib import Path
try:
    import markdown
except ImportError:
    markdown = None


FICHIER_SOURCE = Path("manuscrit_enrichi.md") if Path("manuscrit_enrichi.md").exists() else Path("manuscrit_complet.md")
FICHIER_HTML_SORTIE = Path("livre_haute_couture.html")

CSS_HAUTE_COUTURE = """
/* ==========================================================================
   CONFIGURATIONS FONDAMENTALES DU FORMAT BROCHÉ 6x9 POUCES (152.4 x 228.6 mm)
   ========================================================================== */
@page {
    size: 6in 9in;
    margin-top: 0.85in;
    margin-bottom: 0.8in;
    @bottom-center {
        content: counter(page);
        font-family: 'EB Garamond', 'Garamond', 'Baskerville', 'Georgia', serif;
        font-size: 9pt;
        color: #475569;
        font-feature-settings: "onum" 1; /* Chiffres elzéviriens */
    }
}

/* Page Paire (Verso / Page de gauche) : En-tête avec Titre du Livre */
@page :left {
    margin-left: 0.6in;
    margin-right: 0.9in; /* Marge de reliure (dos) */
    @top-center {
        content: string(livre-titre);
        font-family: 'EB Garamond', 'Garamond', serif;
        font-size: 8pt;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b;
        border-bottom: 0.5pt solid #cbd5e1;
        padding-bottom: 4px;
        width: 100%;
    }
}

/* Page Impaire (Recto / Page de droite) : En-tête avec Titre du Chapitre */
@page :right {
    margin-left: 0.9in; /* Marge de reliure (dos) */
    margin-right: 0.6in;
    @top-center {
        content: string(chapitre-titre);
        font-family: 'EB Garamond', 'Garamond', serif;
        font-size: 8pt;
        font-style: italic;
        letter-spacing: 1px;
        color: #64748b;
        border-bottom: 0.5pt solid #cbd5e1;
        padding-bottom: 4px;
        width: 100%;
    }
}

/* Page blanche ou départ de chapitre sans en-tête polluant */
@page :blank {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

/* ==========================================================================
   TYPOGRAPHIE & RYTHME DE LECTURE (Gris Typographique)
   ========================================================================== */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400;1,600&display=swap');

html, body {
    font-family: 'EB Garamond', 'Garamond', 'Georgia', serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #0f172a;
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
    hyphenate-limit-chars: 6 3 3;
    orphans: 3;
    widows: 3;
}

/* Mémorisation des variables d'en-tête */
.titre-livre-source {
    string-set: livre-titre content();
    display: none;
}

/* ==========================================================================
   DÉPARTS DE CHAPITRES (H1) & HIÉRARCHIE VISUELLE (H2, H3)
   ========================================================================== */
h1 {
    page-break-before: always;
    string-set: chapitre-titre content();
    font-family: 'Cinzel', 'Trajan Pro', 'Georgia', serif;
    font-size: 19pt;
    font-weight: 700;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-top: 2.2in;
    margin-bottom: 1.4in;
    color: #0f172a;
    position: relative;
}

/* Ornement sous le titre de chapitre */
h1::after {
    content: "❖   ❖   ❖";
    display: block;
    font-size: 8pt;
    letter-spacing: 6px;
    margin-top: 18px;
    color: #94a3b8;
    font-family: sans-serif;
}

/* Sous-sections (H2) */
h2 {
    font-family: 'Cinzel', 'Georgia', serif;
    font-size: 13pt;
    font-weight: 600;
    letter-spacing: 1px;
    margin-top: 1.8em;
    margin-bottom: 0.6em;
    color: #1e293b;
    page-break-after: avoid;
    border-bottom: 0.5pt solid #e2e8f0;
    padding-bottom: 4px;
}

/* Points clés & focus (H3) */
h3 {
    font-family: 'EB Garamond', 'Garamond', serif;
    font-size: 11.5pt;
    font-style: italic;
    font-weight: 600;
    margin-top: 1.4em;
    margin-bottom: 0.4em;
    color: #334155;
    page-break-after: avoid;
}

/* ==========================================================================
   PARAGRAPHES, LETTRINES & CITATIONS
   ========================================================================== */
p {
    margin-top: 0;
    margin-bottom: 0;
    text-indent: 1.4em; /* Retrait de première ligne noble */
}

/* Premier paragraphe sans alinéa après titre ou saut */
h1 + p, h2 + p, h3 + p, hr + p, blockquote + p {
    text-indent: 0;
}

/* Lettrine magistrale sur le premier paragraphe du chapitre */
p.lettrine::first-letter {
    font-family: 'Cinzel', serif;
    float: left;
    font-size: 3.6em;
    line-height: 0.78;
    margin-top: 0.1em;
    margin-right: 0.15em;
    margin-bottom: -0.05em;
    color: #0f172a;
    font-weight: bold;
}

/* Encadrés d'action & Études de cas immersives */
blockquote {
    page-break-inside: avoid;
    margin: 1.6em 0.8em;
    padding: 1.2em 1.4em;
    background: #f8fafc;
    border-left: 2.5pt solid #0f172a;
    border-radius: 0 4px 4px 0;
    font-size: 9.8pt;
    line-height: 1.45;
    color: #1e293b;
}

blockquote p {
    text-indent: 0;
    margin-bottom: 0.5em;
}

blockquote p:last-child {
    margin-bottom: 0;
}

/* Tableaux professionnels imprimables */
table {
    width: 100%;
    margin: 1.8em 0;
    border-collapse: collapse;
    font-size: 9pt;
    page-break-inside: avoid;
}

th {
    font-family: 'Cinzel', serif;
    font-size: 8pt;
    letter-spacing: 1px;
    text-transform: uppercase;
    background-color: #0f172a;
    color: #ffffff;
    padding: 8px 10px;
    border: 1px solid #0f172a;
}

td {
    padding: 7px 10px;
    border-bottom: 0.5pt solid #cbd5e1;
    color: #334155;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

/* Séparateurs poétiques */
hr {
    border: 0;
    text-align: center;
    margin: 2em 0;
    height: auto;
}

hr::before {
    content: "— ❧ —";
    font-size: 11pt;
    color: #64748b;
}
"""


def injecter_lettrines_et_ornements(texte_markdown: str) -> str:
    """Recherche le premier paragraphe suivant chaque H1 pour lui assigner la classe .lettrine."""
    lignes = texte_markdown.split("\n")
    lignes_transformees = []
    apres_h1 = False

    for ligne in lignes:
        ligne_strip = ligne.strip()

        if ligne_strip.startswith("# Chapitre") or (ligne_strip.startswith("# ") and not lignes_transformees):
            apres_h1 = True
            lignes_transformees.append(ligne)
            continue

        if apres_h1 and ligne_strip and not ligne_strip.startswith("#") and not ligne_strip.startswith(">") and not ligne_strip.startswith("---"):
            # Enrobage avec balise HTML pour la lettrine
            lignes_transformees.append(f'<p class="lettrine">{ligne_strip}</p>')
            apres_h1 = False
            continue

        lignes_transformees.append(ligne)

    return "\n".join(lignes_transformees)


def fabriquer_edition_haute_couture():
    if not FICHIER_SOURCE.exists():
        print(f"❌ {FICHIER_SOURCE} introuvable.")
        return

    print("🖋️ Lecture du manuscrit brut...")
    texte_brut = FICHIER_SOURCE.read_text(encoding="utf-8")

    print("✨ Ornementation typographique & injection des lettrines...")
    texte_orne = injecter_lettrines_et_ornements(texte_brut)

    print("⚙️ Compilation Markdown structurée...")
    if markdown:
        html_corps = markdown.markdown(
            texte_orne,
            extensions=["extra", "smarty", "tables", "sane_lists"]
        )
    else:
        from kdp_formatter import markdown_vers_html_haute_couture
        html_corps = markdown_vers_html_haute_couture(texte_orne)

    # Récupération du titre du livre pour l'en-tête
    lignes = texte_brut.splitlines()
    titre_livre = "GUIDE PRATIQUE HAUTE DÉFINITION"
    for l in lignes:
        if l.startswith("# ") and "Chapitre" not in l and "Table" not in l:
            titre_livre = l.replace("#", "").strip()
            break

    document_complet = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{titre_livre}</title>
    <style>
{CSS_HAUTE_COUTURE}
    </style>
</head>
<body>
    <div class="titre-livre-source">{titre_livre}</div>
    {html_corps}
</body>
</html>"""

    FICHIER_HTML_SORTIE.write_text(document_complet, encoding="utf-8")
    print(f"\n💎 MAQUETTE HAUTE COUTURE TERMINÉE : {FICHIER_HTML_SORTIE.resolve()}")
    print("👉 Vous pouvez l'imprimer directement via Playwright ou dans votre navigateur (Ctrl + P) !")


if __name__ == "__main__":
    fabriquer_edition_haute_couture()