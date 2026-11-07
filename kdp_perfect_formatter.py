"""
MOTEUR DE CORRECTION DÉFINITIVE & D'OPTIMISATION PRÉ-PRESSE (MarkEddy)
"""

import re
from pathlib import Path
import markdown

SOURCE_MD = Path("manuscrit_enrichi.md") if Path("manuscrit_enrichi.md").exists() else Path("manuscrit_complet.md")
SORTIE_HTML = Path("livre_parfait_kdp.html")

CSS_PERFAIT = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400;1,600&display=swap');

@page {
    size: 6in 9in;
    margin-top: 0.85in;
    margin-bottom: 0.85in;
    @bottom-center {
        content: counter(page);
        font-family: 'EB Garamond', serif;
        font-size: 9.5pt;
        color: #1e293b;
    }
}

@page :left {
    margin-left: 0.65in;
    margin-right: 0.85in;
    @top-center {
        content: "MarkEddy";
        font-family: 'Cinzel', serif;
        font-size: 8pt;
        letter-spacing: 1.5px;
        color: #64748b;
        border-bottom: 0.5pt solid #cbd5e1;
        padding-bottom: 4px;
    }
}

@page :right {
    margin-left: 0.85in;
    margin-right: 0.65in;
    @top-center {
        content: string(titre-chapitre);
        font-family: 'EB Garamond', serif;
        font-style: italic;
        font-size: 8.5pt;
        color: #64748b;
        border-bottom: 0.5pt solid #cbd5e1;
        padding-bottom: 4px;
    }
}

@page :blank {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

html, body {
    font-family: 'EB Garamond', 'Garamond', serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #0f172a;
    text-align: justify;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: keep-all !important;
    orphans: 3 !important;
    widows: 3 !important;
}

h1 {
    page-break-before: always;
    string-set: titre-chapitre content();
    font-family: 'Cinzel', serif;
    font-size: 18pt;
    text-align: center;
    text-transform: uppercase;
    margin-top: 1.8in;
    margin-bottom: 1.2in;
    page-break-after: avoid;
}

h2, h3 {
    font-family: 'Cinzel', serif;
    color: #1e293b;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

p {
    margin: 0;
    text-indent: 1.4em;
}

h1 + p, h2 + p, h3 + p, blockquote + p, tr + p {
    text-indent: 0;
}

p.lettrine::first-letter {
    font-family: 'Cinzel', serif;
    float: left;
    font-size: 3.2em;
    line-height: 0.8;
    margin-top: 0.1em;
    margin-right: 0.12em;
    font-weight: bold;
    color: #0F172A;
}

table {
    width: 100% !important;
    max-width: 100% !important;
    border-collapse: collapse;
    margin: 1.5em 0;
    font-size: 9pt;
    line-height: 1.3;
    page-break-inside: avoid;
}

th {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: bold;
    padding: 6px 8px;
    border: 1px solid #0f172a;
    text-align: left;
}

td {
    padding: 6px 8px;
    border: 1px solid #e2e8f0;
}

tr:nth-child(even) {
    background-color: #f8fafc;
}

blockquote {
    page-break-inside: avoid;
    background: #f8fafc;
    border-left: 3pt solid #D97706;
    padding: 1.1em 1.3em;
    margin: 1.5em 0;
    border-radius: 0 4px 4px 0;
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
    background: #cbd5e1;
    margin: 2em auto;
    width: 50%;
}
"""

def nettoyer_texte_markdown(texte: str) -> str:
    texte = re.sub(r'(?<!^)(?<!\n)#+\s*', '', texte)
    texte = re.sub(r'\s+([:;!?%€»])', r'&nbsp;\1', texte)
    texte = re.sub(r'([«])\s+', r'\1&nbsp;', texte)
    texte = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', texte)
    texte = re.sub(r'\\\*', '*', texte)
    return texte

def appliquer_lettrines(texte: str) -> str:
    lignes = texte.splitlines()
    lignes_traitees = []
    apres_h1 = False
    
    for l in lignes:
        l_strip = l.strip()
        if l_strip.startswith("# Chapitre") or (l_strip.startswith("# ") and not lignes_traitees):
            apres_h1 = True
            lignes_traitees.append(l)
            continue
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

    print("🛠️  Nettoyage des erreurs et application des règles anti-bug...")
    brut = SOURCE_MD.read_text(encoding="utf-8")
    nettoye = nettoyer_texte_markdown(brut)
    avec_lettrines = appliquer_lettrines(nettoye)

    print("⚙️  Compilation du document...")
    html_corps = markdown.markdown(avec_lettrines, extensions=["extra", "tables", "smarty"])

    document = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Livre KDP Corrigé - MarkEddy</title>
    <style>
{CSS_PERFAIT}
    </style>
</head>
<body>
    <div class="meta-titre">MAÎTRISER SES FINANCES PERSONNELLES</div>
    {html_corps}
</body>
</html>"""

    SORTIE_HTML.write_text(document, encoding="utf-8")
    print(f"🎉 MAQUETTE SANS ERREUR GÉNÉRÉE : {SORTIE_HTML.resolve()}")

if __name__ == "__main__":
    executer_correction_et_maquettage()
