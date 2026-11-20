"""
kdp_formatter.py - Moteur de Formatage & Maquettisme Haute Couture KDP 6x9 pouces.
Applique la géométrie d'édition professionnelle : marges de reliure asymétriques (gutter 0.85"),
lettrines sculptées (drop caps), ornements d'édition (fleurons) et typographie d'exception.
"""

import os
import re
import json
from datetime import date
from pathlib import Path
from kdp_design_system import KDP_METRICS_6X9, ORNEMENTS_EDITION

FICHIER_SOURCE = Path("manuscrit_complet.md")
FICHIER_HTML = Path("livre_kdp_interieur.html")
FICHIER_PDF = Path("livre_kdp_interieur.pdf")

GUTTER = KDP_METRICS_6X9["gutter_margin_in"]
OUTSIDE = KDP_METRICS_6X9["outside_margin_in"]
TOP = KDP_METRICS_6X9["top_margin_in"]
BOTTOM = KDP_METRICS_6X9["bottom_margin_in"]

CSS_HAUTE_COUTURE = f"""
@page {{
    size: 6in 9in;
    margin-top: {TOP}in;
    margin-bottom: {BOTTOM}in;
    @bottom-center {{
        content: counter(page);
        font-family: 'Georgia', 'Garamond', serif;
        font-size: 9pt;
        color: #555;
    }}
}}

/* Page impaire (droite) : marge de reliure intérieure à gauche */
@page :right {{
    margin-left: {GUTTER}in;
    margin-right: {OUTSIDE}in;
}}

/* Page paire (gauche) : marge de reliure intérieure à droite */
@page :left {{
    margin-left: {OUTSIDE}in;
    margin-right: {GUTTER}in;
}}

/* Première page sans folio */
@page :first {{
    @bottom-center {{
        content: "";
    }}
}}

body {{
    font-family: 'Garamond', 'Georgia', 'Times New Roman', serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1a1a1a;
    text-align: justify;
    hyphens: manual;
    -webkit-hyphens: manual;
    margin: 0;
    padding: 0;
}}

/* Règle stricte anti-césure sauvage sur tous les titres, tableaux et éléments structurés */
h1, h2, h3, h4, th, td, .callout-box, .callout-header, .author-title, .title-signature, .chapter-lead::first-letter, .toc-link, .author-signature, .kdp-table, tr {{
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
}}

/* Page de Grand Titre */
.title-page {{
    page-break-before: always;
    padding-top: 2.2in;
    text-align: center;
}}

.book-title {{
    font-size: 24pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.3in;
    color: #0f172a;
}}

.book-subtitle {{
    font-size: 12.5pt;
    font-style: italic;
    color: #475569;
    margin-bottom: 1.8in;
    line-height: 1.4;
}}

.author-title {{
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
    color: #1e293b;
}}

/* Page de copyright */
.copyright-page {{
    page-break-before: always;
    padding-top: 4.8in;
    font-size: 8.5pt;
    line-height: 1.4;
    color: #475569;
}}

/* Grands chapitres */
h1 {{
    page-break-before: always;
    break-before: page;
    font-size: 20pt;
    font-weight: 700;
    text-align: center;
    margin-top: 1.6in;
    margin-bottom: 0.8in;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #0f172a;
}}

h2 {{
    font-size: 13.5pt;
    margin-top: 1.1in;
    margin-bottom: 0.35in;
    font-weight: 600;
    color: #1e293b;
    page-break-after: avoid;
}}

h3 {{
    font-size: 11.5pt;
    margin-top: 0.65in;
    margin-bottom: 0.2in;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3px;
    page-break-after: avoid;
    break-after: avoid;
}}

h4, .sub-heading {{
    font-family: 'Georgia', serif;
    font-size: 10pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 0.45in;
    margin-bottom: 0.15in;
    page-break-after: avoid;
    break-after: avoid;
}}

p {{
    margin-top: 0;
    margin-bottom: 0.65em;
    text-indent: 1.25em;
}}

/* Pas d'indentation après un titre */
h1 + p, h2 + p, h3 + p, h4 + p, hr + p, blockquote + p, div + p {{
    text-indent: 0;
}}

/* Lettrine sculptée de début de chapitre (Drop Cap) */
p.chapter-lead::first-letter {{
    font-size: 3.4em;
    float: left;
    line-height: 0.8;
    margin-right: 0.12em;
    font-family: 'Georgia', 'Garamond', serif;
    font-weight: bold;
    color: #0f172a;
}}

/* Encadrés d'action immédiate et conseils d'autorité */
blockquote, .callout-box {{
    border-left: 3.5px solid #d4af37;
    background-color: #fafaf9;
    margin: 1.2em 0.2in;
    padding: 0.8em 1.1em;
    font-size: 9.5pt;
    font-style: normal;
    page-break-inside: avoid;
    break-inside: avoid;
    border-radius: 0 4px 4px 0;
}}

.callout-header {{
    font-family: 'Georgia', serif;
    font-weight: bold;
    font-size: 9.8pt;
    color: #996515;
    letter-spacing: 0.5px;
    margin-bottom: 0.4em;
    display: block;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    text-transform: uppercase;
}}

.callout-box strong {{
    color: #996515;
}}

ul, ol {{
    margin: 0.6em 0 0.8em 1.5em;
    padding: 0;
}}

li {{
    margin-bottom: 0.35em;
}}

/* Séparateur d'édition ornemental */
hr {{
    border: 0;
    text-align: center;
    margin: 1.8em auto;
    page-break-after: avoid;
    break-after: avoid;
}}

hr::after {{
    content: "{ORNEMENTS_EDITION['separateur_fin']}";
    display: inline-block;
    color: #94a3b8;
    font-size: 11pt;
    letter-spacing: 4px;
}}

/* Tableaux d'édition conformes KDP */
table {{
    table-layout: fixed;
    width: 100%;
    margin: 1.4em 0;
    border-collapse: collapse;
    font-size: 8pt;
    line-height: 1.35;
    page-break-inside: avoid;
    break-inside: avoid;
}}

th {{
    font-family: 'Georgia', serif;
    font-size: 7.5pt;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    background-color: #0f172a;
    color: #ffffff;
    padding: 6px 4px;
    border: 1px solid #0f172a;
    text-align: left;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
}}

td {{
    font-size: 7.8pt;
    padding: 5px 4px;
    border-bottom: 0.5pt solid #cbd5e1;
    color: #334155;
    text-align: left;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
}}

tr:nth-child(even) td {{
    background-color: #f8fafc;
}}

.author-bio-box {{
    border: 1.5px solid #d4af37;
    background: #fbfbfa;
    padding: 1.5em;
    margin: 1.5em 0;
    border-radius: 4px;
}}
"""

def markdown_vers_html_haute_couture(texte_md: str) -> str:
    """Convertit le Markdown en HTML riche avec lettrines, tableaux et structure d'édition."""
    lignes = texte_md.split("\n")
    nouvelles = []
    en_liste = False
    en_blockquote = False
    en_table = False
    prochain_lead = False
    
    for idx, lig in enumerate(lignes):
        l = lig.strip()
        
        # Tables Markdown
        if l.startswith("|") and l.endswith("|"):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            
            colonnes = [c.strip() for c in l[1:-1].split("|")]
            if all(re.match(r"^:?-+:?$", c) for c in colonnes if c):
                continue
                
            if not en_table:
                nouvelles.append("<table>")
                nouvelles.append("<thead><tr>")
                for col in colonnes:
                    col_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", col)
                    col_fmt = re.sub(r"\*(.*?)\*", r"<em>\1</em>", col_fmt)
                    nouvelles.append(f"<th>{col_fmt}</th>")
                nouvelles.append("</tr></thead><tbody>")
                en_table = True
                continue
            else:
                nouvelles.append("<tr>")
                for col in colonnes:
                    col_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", col)
                    col_fmt = re.sub(r"\*(.*?)\*", r"<em>\1</em>", col_fmt)
                    nouvelles.append(f"<td>{col_fmt}</td>")
                nouvelles.append("</tr>")
                continue
        else:
            if en_table:
                nouvelles.append("</tbody></table>")
                en_table = False
        
        # Titres
        if l.startswith("#### "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            nouvelles.append(f'<h4 class="sub-heading">{l[5:].strip()}</h4>')
            continue
        elif l.startswith("### "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            nouvelles.append(f"<h3>{l[4:].strip()}</h3>")
            continue
        elif l.startswith("## "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            nouvelles.append(f"<h2>{l[3:].strip()}</h2>")
            continue
        elif l.startswith("# "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            nouvelles.append(f"<h1>{l[2:].strip()}</h1>")
            prochain_lead = True
            continue
            
        # Séparateurs (supprimés s'ils précèdent directement un titre)
        if l == "---":
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            prochains = [lignes[k].strip() for k in range(idx + 1, min(idx + 5, len(lignes))) if lignes[k].strip()]
            if prochains and (prochains[0].startswith("# ") or prochains[0].startswith("## ") or prochains[0].startswith("### ")):
                continue
            nouvelles.append("<hr>")
            continue
            
        # Citations / Blockquotes et Encadrés d'Action Immédiate
        if l.startswith(">"):
            contenu_bq = l[1:].strip()
            if not en_blockquote:
                nouvelles.append('<blockquote class="callout-box">')
                en_blockquote = True
            if not contenu_bq:
                continue

            if "Action Immédiate" in contenu_bq or "ACTION IMMÉDIATE" in contenu_bq or "action immédiate" in contenu_bq.lower() or contenu_bq.startswith("###") or contenu_bq.startswith("##") or contenu_bq.startswith("⚡"):
                titre_clean = re.sub(r"^[#\s\*🛑⚡💡]+", "", contenu_bq)
                titre_clean = re.sub(r"[\*:]+$", "", titre_clean).strip()
                nouvelles.append(f'<div class="callout-header">⚡ {titre_clean}</div>')
                continue

            contenu_bq = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", contenu_bq)
            contenu_bq = re.sub(r"\*(.*?)\*", r"<em>\1</em>", contenu_bq)
            nouvelles.append(f"<p>{contenu_bq}</p>")
            continue
        else:
            if en_blockquote:
                nouvelles.append("</blockquote>")
                en_blockquote = False
                
        # Listes
        if l.startswith("- ") or l.startswith("* "):
            if not en_liste:
                nouvelles.append("<ul>")
                en_liste = True
            item = l[2:]
            item = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item)
            item = re.sub(r"\*(.*?)\*", r"<em>\1</em>", item)
            nouvelles.append(f"<li>{item}</li>")
            continue
        else:
            if en_liste:
                nouvelles.append("</ul>")
                en_liste = False
                
        # Paragraphes
        if l:
            # Insertion du Logo Officiel MarkEddy Noir d'Édition (Print KDP 6x9)
            if l.strip() in ["**Par MarkEddy**", "Par MarkEddy"]:
                nouvelles.append('<div class="author-signature" style="text-align: center; margin: 40px auto 15px auto;">'
                                 '<img src="assets/logo/logo_markeddy_noir_print.png" alt="MarkEddy" style="width: 2.6in; max-width: 80%; height: auto; display: inline-block;" />'
                                 '<p style="font-family: \'Garamond\', \'Georgia\', serif; font-size: 11pt; letter-spacing: 2px; text-transform: uppercase; margin-top: 10px; color: #1a1a1a;">Éditions MarkEddy</p></div>')
                continue

            p_texte = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", l)
            p_texte = re.sub(r"\*(.*?)\*", r"<em>\1</em>", p_texte)
            if prochain_lead and not l.startswith("<"):
                nouvelles.append(f'<p class="chapter-lead">{p_texte}</p>')
                prochain_lead = False
            else:
                nouvelles.append(f"<p>{p_texte}</p>")
        else:
            nouvelles.append("")
            
    if en_liste:
        nouvelles.append("</ul>")
    if en_blockquote:
        nouvelles.append("</blockquote>")
    if en_table:
        nouvelles.append("</tbody></table>")
        
    return "\n".join(nouvelles)

def convertir_manuscrit_en_html_kdp(source_md: Path = FICHIER_SOURCE, sortie_html: Path = FICHIER_HTML) -> Path:
    if not source_md.exists():
        raise FileNotFoundError(f"❌ {source_md} introuvable.")
        
    texte_md = source_md.read_text(encoding="utf-8")
    corps_html = markdown_vers_html_haute_couture(texte_md)
    
    html_complet = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Manuscrit KDP Haute Couture - Format 6x9 pouces</title>
    <style>
{CSS_HAUTE_COUTURE}
    </style>
</head>
<body>
{corps_html}
</body>
</html>"""

    sortie_html.write_text(html_complet, encoding="utf-8")
    print(f"📖 Livre KDP HTML 6x9 po Haute Couture généré : {sortie_html.resolve()}")
    return sortie_html

def convertir_manuscrit_en_pdf():
    f_html = convertir_manuscrit_en_html_kdp()
    
    # 1. Rendu d'élite vectoriel via Playwright (Chromium / Edge)
    try:
        from html_to_pdf import convertir
        print("🖨️ Tentative de rendu vectoriel haute fidélité via Playwright (Chromium/Edge)...")
        succes = convertir()
        if succes and FICHIER_PDF.exists():
            return FICHIER_PDF
    except Exception as e:
        print(f"ℹ️  Playwright non activé : {e}")

    # 2. Rendu alternatif via WeasyPrint
    try:
        from weasyprint import HTML, CSS
        document = HTML(filename=str(f_html))
        feuille_style = CSS(string=CSS_HAUTE_COUTURE)
        document.write_pdf(str(FICHIER_PDF), stylesheets=[feuille_style])
        print(f"✅ FICHIER PDF PRÊT POUR KDP : {FICHIER_PDF.resolve()}")
        return FICHIER_PDF
    except (ImportError, OSError):
        print(f"ℹ️  Intérieur Haute Couture prêt pour l'impression :")
        print(f"   👉 Ouvrez {f_html.name} dans Google Chrome ou Edge")
        print(f"   👉 Appuyez sur Ctrl + P (Format: 6x9 po, Marges intégrées, Graphiques d'arrière-plan)")
        print(f"   👉 Enregistrez en PDF haute définition !")
        print(f"   👉 Ou installez Playwright pour l'export automatique : pip install playwright && playwright install chromium")
        return f_html

# Compatibilité test_suite et kdp_machine
def generer_manuscrit_markdown(draft: dict, output_file: str = "manuscrit_complet.md") -> Path:
    meta = draft.get("metadata", {})
    titre = meta.get("titre", "LIVRE KDP")
    sous_titre = meta.get("sous_titre", "")
    
    lignes = [
        f"# {titre}",
        f"*{sous_titre}*\n",
        "---\n",
        draft.get("introduction", ""),
        "\n---\n"
    ]
    for ch in draft.get("chapitres_rediges", []):
        lignes.append(f"\n# Chapitre {ch.get('numero')} : {ch.get('titre')}\n")
        for s in ch.get("sections_redigees", []):
            lignes.append(f"\n### {s.get('titre')}\n\n{s.get('contenu')}\n")
            
    if draft.get("conclusion"):
        lignes.append(f"\n---\n\n# Conclusion\n\n{draft.get('conclusion')}\n")
        
    p = Path(output_file)
    p.write_text("\n".join(lignes), encoding="utf-8")
    return p

def generer_livre_html_kdp(draft: dict, output_file: str = "livre_kdp_6x9.html") -> Path:
    md_temp = generer_manuscrit_markdown(draft, "temp_render.md")
    p_out = Path(output_file)
    convertir_manuscrit_en_html_kdp(source_md=md_temp, sortie_html=p_out)
    if md_temp.exists():
        md_temp.unlink()
    return p_out

def generer_description_amazon_kdp(blueprint: dict, output_file: str = "amazon_description.html") -> Path:
    from kdp_marketing import generer_pack_marketing
    p = Path(output_file)
    f_pack = generer_pack_marketing()
    p.write_text(f_pack.read_text(encoding="utf-8"), encoding="utf-8")
    return p

def formater_projet_complet(draft_file: str = "book_draft.json", blueprint_file: str = "book_blueprint.json"):
    convertir_manuscrit_en_pdf()

if __name__ == "__main__":
    convertir_manuscrit_en_pdf()
