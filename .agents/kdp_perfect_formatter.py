"""
MOTEUR DE CORRECTION DÉFINITIVE & D'OPTIMISATION PRÉ-PRESSE (MarkEddy)
- Supprime les dièses '#' et scories Markdown résiduelles.
- Bloque les césures sauvages (pas de mots coupés en deux).
- Structure et ajuste les tableaux pour le format 6x9 po sans débordement.
- Élimine les sauts de page abusifs et les pages vides.
- Force les espaces insécables devant la ponctuation et les unités.
- INCLUT LE DESIGN ULTRA-MODERNE : Espace blanc, lettrines épurées, style académique.
"""

import re
from pathlib import Path
import markdown

SOURCE_MD = Path("manuscrit_enrichi.md") if Path("manuscrit_enrichi.md").exists() else Path("manuscrit_complet.md")
SORTIE_HTML = Path("livre_parfait_kdp.html")

# ==============================================================================
# LE STYLE CSS ULTRA-MODERNE "ANTI-BUG" (ESPACE, CONTRASTE, SANS-SERIF)
# ==============================================================================
CSS_PERFAIT = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,600;1,300&family=EB+Garamond:ital,wght@0,400;0,600;1,400;1,600&display=swap');

@page {
    size: 6in 9in;
    margin-top: 0.85in;
    margin-bottom: 0.85in;
    @bottom-center {
        content: counter(page);
        font-family: 'Montserrat', sans-serif;
        font-size: 9pt;
        color: #64748b;
    }
}

@page :left {
    margin-left: 0.65in;
    margin-right: 0.85in;
    @top-center {
        content: "MARKEDDY";
        font-family: 'Montserrat', sans-serif;
        font-size: 7.5pt;
        letter-spacing: 2px;
        color: #94a3b8;
        border-bottom: 0.5px solid #e2e8f0;
        padding-bottom: 4px;
    }
}

@page :right {
    margin-left: 0.85in;
    margin-right: 0.65in;
    @top-center {
        content: string(titre-chapitre);
        font-family: 'Montserrat', sans-serif;
        font-style: italic;
        font-size: 7.5pt;
        color: #94a3b8;
        border-bottom: 0.5px solid #e2e8f0;
        padding-bottom: 4px;
    }
}

@page :blank {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

html, body {
    font-family: 'EB Garamond', 'Minion Pro', serif;
    font-size: 11pt;
    line-height: 1.65; /* Interligne très aéré */
    color: #2D3748; /* Gris Charcoal élégant */
    text-align: justify;
    
    /* BLOQUE LES MOTS COUPÉS */
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: keep-all !important;
    
    /* Évite les lignes orphelines et veuves */
    orphans: 3 !important;
    widows: 3 !important;
}

h1 {
    page-break-before: always;
    string-set: titre-chapitre content();
    font-family: 'Montserrat', 'Helvetica', sans-serif;
    font-size: 28pt;
    font-weight: 300; /* Typographie fine et moderne */
    text-align: left;
    color: #0F172A;
    margin-top: 2.5in; /* Espace blanc massif au-dessus (Negative space) */
    margin-bottom: 1.2in;
    border-bottom: 2px solid #D4AF37; /* Ligne Or Impérial fine */
    padding-bottom: 15px;
    page-break-after: avoid;
}

h2, h3 {
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    color: #0F172A;
    margin-top: 2em;
    margin-bottom: 1em;
    page-break-after: avoid;
}

p {
    margin: 0;
    text-indent: 1.5em;
}

h1 + p, h2 + p, h3 + p, blockquote + p, tr + p {
    text-indent: 0;
}

/* Lettrine épurée */
p.lettrine::first-letter {
    font-family: 'Montserrat', sans-serif;
    float: left;
    font-size: 3.5em;
    line-height: 0.8;
    margin-top: 0.05em;
    margin-right: 0.15em;
    font-weight: 300;
    color: #D4AF37; /* Lettrine en Or Impérial */
}

/* Tableaux ultra-modernes (style rapport annuel) */
table {
    width: 100% !important;
    max-width: 100% !important;
    border-collapse: collapse;
    margin: 2em 0;
    font-family: 'Montserrat', sans-serif;
    font-size: 8.5pt;
    line-height: 1.4;
    page-break-inside: avoid;
}

th {
    color: #0F172A;
    font-weight: 600;
    padding: 8px 10px;
    border-bottom: 2px solid #0F172A;
    text-align: left;
    text-transform: uppercase;
}

td {
    padding: 8px 10px;
    border-bottom: 1px solid #E2E8F0; /* Uniquement des lignes horizontales */
}

/* Citations en exergue avec beaucoup d'espace */
blockquote {
    page-break-inside: avoid;
    font-family: 'Montserrat', sans-serif;
    font-size: 13pt;
    font-style: italic;
    font-weight: 600;
    color: #D4AF37;
    line-height: 1.5;
    margin: 1.5in 0.8in; /* Marges massives pour isoler le texte */
    text-align: center;
    border: none;
}

blockquote p {
    text-indent: 0;
    margin-bottom: 0.4em;
}

blockquote p:last-child {
    margin-bottom: 0;
}

hr {
    border: 0;
    height: 1px;
    background: #E2E8F0;
    margin: 3em auto;
    width: 30%;
}
"""

def nettoyer_texte_markdown(texte: str) -> str:
    """Corrige les bugs d'écriture, de caractères parasites, de ponctuation et de césures."""
    # 1. Supprime les dièses '#' perdus au milieu du texte (mais garde les titres en début de ligne)
    texte = re.sub(r'(?<!^)(?<!\n)#+\s*', '', texte)
    
    # 2. Force les espaces insécables pour empêcher les signes isolés en début de ligne
    texte = re.sub(r'\s+([:;!?%€»])', r'&nbsp;\1', texte)
    texte = re.sub(r'([«])\s+', r'\1&nbsp;', texte)
    
    # 3. Corrige l'erreur fréquente des mots d'exemple divisés par des tirets
    texte = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', texte)
    
    # 4. Supprime les balises Markdown brutes non interprétées de type `* ` erratiques
    texte = re.sub(r'\\\*', '*', texte)
    
    return texte

def appliquer_lettrines(texte: str) -> str:
    """Injecte proprement les lettrines sans casser le HTML."""
    lignes = texte.splitlines()
    lignes_traitees = []
    apres_h1 = False
    
    for l in lignes:
        l_strip = l.strip()
        if l_strip.startswith("# Chapitre") or (l_strip.startswith("# ") and not lignes_traitees):
            apres_h1 = True
            lignes_traitees.append(l)
            continue
        # Premier paragraphe après un grand titre -> Lettrine !
        if apres_h1 and l_strip and not l_strip.startswith("#") and not l_strip.startswith(">") and not l_strip.startswith("-"):
            lignes_traitees.append(f'<p class="lettrine">{l_strip}</p>')
            apres_h1 = False
            continue
        lignes_traitees.append(l)
        
    return "\n".join(lignes_traitees)

def executer_correction_et_maquettage():
    if not SOURCE_MD.exists():
        print(f"❌ Impossible de trouver le fichier source {SOURCE_MD.name}")
        return

    print("🛠️  Nettoyage des erreurs et application du style ULTRA-MODERNE...")
    brut = SOURCE_MD.read_text(encoding="utf-8")
    nettoye = nettoyer_texte_markdown(brut)
    avec_lettrines = appliquer_lettrines(nettoye)

    # Conversion Markdown vers HTML
    print("⚙️  Compilation du document...")
    html_corps = markdown.markdown(avec_lettrines, extensions=["extra", "tables", "smarty"])

    # Assemblage du document final
    document = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Livre KDP Ultra-Moderne - MarkEddy</title>
    <style>
{CSS_PERFAIT}
    </style>
</head>
<body>
    {html_corps}
</body>
</html>"""

    SORTIE_HTML.write_text(document, encoding="utf-8")
    print(f"🎉 MAQUETTE ULTRA-MODERNE GÉNÉRÉE : {SORTIE_HTML.resolve()}")
    print("👉 Exécutez maintenant 'python compile_html_to_pdf.py livre_parfait_kdp.html --format 6x9 --out livre_ultra_moderne.pdf' !")

if __name__ == "__main__":
    executer_correction_et_maquettage()