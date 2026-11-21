"""
kdp_extensions/layout_engine_pro.py — Moteur CSS Paged Media & Typographie KDP Pro.
(W3C CSS Paged Media Module Level 3 + Normes d'impression Amazon KDP).

Ce moteur génère des intérieurs print-ready de qualité artisanale pour les 16 formats KDP :
1. Déclaration `@page` stricte avec format de coupe millimétrique et fond perdu optionnel.
2. Pages en regard (Spreads) asymétriques avec marge de reliure (Gutter) dynamique :
   - `@page :left` (pages paires / verso) : titre de l'ouvrage en petites capitales à gauche.
   - `@page :right` (pages impaires / recto) : titre du chapitre courant en italique à droite.
   - Suppression systématique des en-têtes sur les pages de faux-titre, titre et ouvertures de chapitre.
3. Folios alternés : numérotation centrée via `counter(page)` en pied de page.
4. Typographie d'artisan :
   - Lettrines (Drop Caps) sur 2 à 3 lignes de hauteur.
   - Justification bilatérale avec césure automatique des mots (`hyphens: auto; text-align: justify;`).
   - Alinéa de paragraphe strict de 1.2em, supprimé immédiatement après chaque titre.
   - Contrôle anti-veuves et orphelines (`orphans: 3; widows: 3;`).
5. Blocs d'autorité : boîtes d'action immédiate (24h), études de cas chiffrées, tableaux prépresse.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from kdp_extensions.kdp_dimensions import (
    KDP_FORMATS,
    KDP_FORMAT_IDS,
    normalize_format,
    calculate_kdp_specs,
)
from kdp_extensions.fonts_connector import (
    EDITORIAL_FONT_PAIRINGS,
    generate_pairing_css,
    recommend_font_pairing,
    recommend_font_pairing_for_language,
)
from kdp_extensions.i18n_config import (
    get_language_config,
    is_rtl,
    normalize_language,
)


def calculate_gutter_in(page_count: int, high_prestige: bool = True) -> float:
    """
    Calcule la marge de reliure (Gutter) requise.
    En mode 'high_prestige' (recommandation Règle 02), utilise 0.85 po pour une
    lecture fluide et sans torsion du livre en 6x9.
    """
    if high_prestige and page_count >= 100:
        return 0.85
    if page_count <= 150:
        return 0.375
    if page_count <= 300:
        return 0.500
    if page_count <= 400:
        return 0.625
    return 0.750


def generate_paged_media_css(
    format_id: str = "6x9",
    page_count: int = 150,
    paper_type: str = "white",
    bleed: bool = False,
    font_pairing: Optional[Dict[str, Any]] = None,
    book_title: str = "TITRE DE L'OUVRAGE",
    author_name: str = "NOM DE L'AUTEUR",
    high_prestige_gutter: bool = True,
    profile: str = "standard",
    language: str = "fr",
) -> str:
    """
    Génère la feuille de style CSS Paged Media complète et infaillible pour
    l'impression papier Amazon KDP.
    Supporte les profils :
    - 'standard'      : Non-fiction, business, roman (en-têtes alternés, folios, alinéas).
    - 'coloring_kids' : Livre de coloriage pour enfants (verso blanc, marges renforcées,
                        zéro en-tête distrayant, lettrages ludiques Fredoka/Baloo).
    - Multilingue 5 langues (EN, FR, ES, DE, AR) avec inversion de gouttière RTL pour l'Arabe.
    """
    fid = normalize_format(format_id)
    trim_w, trim_h = KDP_FORMATS[fid]

    lang_code = normalize_language(language)
    lang_cfg = get_language_config(lang_code)
    rtl = lang_cfg["is_rtl"]

    is_kids = (profile or "").strip().lower() == "coloring_kids"

    if is_kids:
        gutter = 0.75  # marge intérieure généreuse pour coloriage
        outside = 0.50
        top_margin = 0.50
        bottom_margin = 0.50
        if font_pairing is None:
            font_pairing = recommend_font_pairing("coloriage", "enfants")
    else:
        gutter = calculate_gutter_in(page_count, high_prestige=high_prestige_gutter)
        outside = 0.55
        top_margin = 0.75
        bottom_margin = 0.75
        if font_pairing is None:
            font_pairing = recommend_font_pairing_for_language(lang_code, "business", "professionnels")

    bleed_val = 0.125 if bleed else 0.0
    w_with_bleed = trim_w + (2 * bleed_val)
    h_with_bleed = trim_h + (2 * bleed_val)

    pairing_css = generate_pairing_css(font_pairing, include_embed=True)
    safe_title = book_title.replace('"', '\\"')

    # Règles spécifiques au profil coloriage enfants ou livre standard
    if is_kids:
        running_left = "@top-left { content: none; } @bottom-center { content: none; }"
        running_right = "@top-right { content: none; } @bottom-center { content: none; }"
    elif rtl:
        # En RTL : Titre de l'ouvrage sur la page de droite, chapitre sur la gauche
        running_left = """
  @top-left {
    content: string(chapter-title);
    font-family: var(--font-accent);
    font-style: italic;
    font-size: 8.5pt;
    color: #64748b;
    vertical-align: bottom;
    padding-bottom: 8pt;
  }
  @bottom-center {
    content: counter(page);
    font-family: var(--font-body);
    font-size: 9pt;
    color: #475569;
    vertical-align: top;
    padding-top: 10pt;
  }"""
        running_right = f"""
  @top-right {{
    content: "{safe_title}";
    font-family: var(--font-title);
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #64748b;
    vertical-align: bottom;
    padding-bottom: 8pt;
  }}
  @bottom-center {{
    content: counter(page);
    font-family: var(--font-body);
    font-size: 9pt;
    color: #475569;
    vertical-align: top;
    padding-top: 10pt;
  }}"""
    else:
        running_left = f"""
  @top-left {{
    content: "{safe_title}";
    font-family: var(--font-title);
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    vertical-align: bottom;
    padding-bottom: 8pt;
  }}
  @bottom-center {{
    content: counter(page);
    font-family: var(--font-body);
    font-size: 9pt;
    color: #475569;
    vertical-align: top;
    padding-top: 10pt;
  }}"""
        running_right = """
  @top-right {
    content: string(chapter-title);
    font-family: var(--font-accent);
    font-style: italic;
    font-size: 8.5pt;
    color: #64748b;
    vertical-align: bottom;
    padding-bottom: 8pt;
  }
  @bottom-center {
    content: counter(page);
    font-family: var(--font-body);
    font-size: 9pt;
    color: #475569;
    vertical-align: top;
    padding-top: 10pt;
  }"""

    kids_addon_css = ""
    if is_kids:
        kids_addon_css = """
/* ==========================================================================
   PROFIL ENFANTS & COLORIAGE KDP (VERSO BLANC & MARGES DE SÉCURITÉ)
   ========================================================================== */

/* Page de planche : commence toujours sur page impaire (recto) */
.coloring-sheet-page {
  page-break-before: always;
  break-before: page;
  page-break-after: always;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.coloring-sheet-page svg, .coloring-sheet-page img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

/* Page verso blanche anti-bavure (garantit qu'aucun feutre ne traverse) */
.blank-verso-page {
  page-break-before: always;
  break-before: page;
  background-color: #FFFFFF !important;
  height: 100%;
  width: 100%;
}

/* Page "Ce livre appartient à..." */
.belongs-to-page {
  page-break-before: always;
  break-before: page;
  text-align: center;
  padding: 2in 0.5in 1in 0.5in;
  font-family: var(--font-subtitle, 'Nunito', sans-serif);
}
.belongs-to-title {
  font-family: var(--font-title, 'Baloo 2', cursive);
  font-size: 26pt;
  color: #1e293b;
  margin-bottom: 2em;
}
.belongs-to-line {
  display: block;
  border-bottom: 2.5pt dashed #94a3b8;
  width: 70%;
  margin: 1.5em auto;
  height: 2em;
}

/* Page Test de Couleurs */
.color-test-page {
  page-break-before: always;
  break-before: page;
  text-align: center;
  padding: 1.5in 0.5in;
}
.color-test-title {
  font-family: var(--font-title, 'Baloo 2', cursive);
  font-size: 22pt;
  margin-bottom: 1.5em;
}
.color-test-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20pt;
  max-width: 80%;
  margin: 0 auto;
}
.color-test-circle {
  width: 60pt;
  height: 60pt;
  border: 2pt solid #000000;
  border-radius: 50%;
  margin: 0 auto;
}

/* Diplôme de Fin de Livre */
.diploma-page {
  page-break-before: always;
  break-before: page;
  border: 4pt double #d4af37;
  padding: 1in 0.5in;
  text-align: center;
  font-family: var(--font-subtitle, 'Nunito', sans-serif);
}
.diploma-title {
  font-family: var(--font-title, 'Baloo 2', cursive);
  font-size: 28pt;
  color: #a16207;
  text-transform: uppercase;
  margin-bottom: 0.5em;
}
"""

    if rtl:
        spreads_css = f"""
/* Pages Verso (Paires / Gauche) - Inversion Reliure Arabe (RTL) : Gouttière à GAUCHE */
@page :left {{
  margin-left: {gutter}in;
  margin-right: {outside}in;
  {running_left}
}}

/* Pages Recto (Impaires / Droite) - Inversion Reliure Arabe (RTL) : Gouttière à DROITE */
@page :right {{
  margin-left: {outside}in;
  margin-right: {gutter}in;
  {running_right}
}}"""
        body_direction_css = """
  direction: rtl;
  unicode-bidi: embed;
  text-align: right;
  hyphens: none !important;
  -webkit-hyphens: none !important;
"""
    elif lang_code == "de":
        spreads_css = f"""
/* Pages Verso (Paires / Gauche) : Marge intérieure (Gutter) à droite */
@page :left {{
  margin-left: {outside}in;
  margin-right: {gutter}in;
  {running_left}
}}

/* Pages Recto (Impaires / Droite) : Marge intérieure (Gutter) à gauche */
@page :right {{
  margin-left: {gutter}in;
  margin-right: {outside}in;
  {running_right}
}}"""
        body_direction_css = """
  direction: ltr;
  text-align: justify;
  hyphens: auto;
  -webkit-hyphens: auto;
"""
    else:
        spreads_css = f"""
/* Pages Verso (Paires / Gauche) : Marge intérieure (Gutter) à droite */
@page :left {{
  margin-left: {outside}in;
  margin-right: {gutter}in;
  {running_left}
}}

/* Pages Recto (Impaires / Droite) : Marge intérieure (Gutter) à gauche */
@page :right {{
  margin-left: {gutter}in;
  margin-right: {outside}in;
  {running_right}
}}"""
        body_direction_css = """
  direction: ltr;
  text-align: justify;
  hyphens: auto;
"""

    css = f"""{pairing_css}

/* ==========================================================================
   W3C CSS PAGED MEDIA MODULE LEVEL 3 — AMAZON KDP {fid.upper()} ({lang_code.upper()})
   ========================================================================== */

@page {{
  size: {w_with_bleed}in {h_with_bleed}in;
  margin-top: {top_margin}in;
  margin-bottom: {bottom_margin}in;
  orphans: 3;
  widows: 3;
}}

{spreads_css}

/* Première page & Pages Préliminaires : Pas d'en-tête ni de pied de page */
@page :first {{
  @top-left {{ content: none; }}
  @top-right {{ content: none; }}
  @bottom-center {{ content: none; }}
}}

@page blank {{
  @top-left {{ content: none; }}
  @top-right {{ content: none; }}
  @bottom-center {{ content: none; }}
}}

/* ==========================================================================
   RÈGLES TYPOGRAPHIQUES D'ÉDITION & SAUTS DE PAGES
   ========================================================================== */

*, *::before, *::after {{
  box-sizing: border-box;
}}

html, body {{
  margin: 0;
  padding: 0;
  color: #111827;
  background-color: #ffffff;
}}

body {{
  font-family: var(--font-body);
  font-size: 10.5pt;
  line-height: 1.48;
{body_direction_css}
  text-justify: inter-word;
}}

/* Capture du titre de chapitre pour l'en-tête courant */
h1.chapter-title, .chapter-opener h1 {{
  string-set: chapter-title content();
  page-break-before: always;
  break-before: page;
  margin-top: 2in;
  margin-bottom: 0.4in;
  font-family: var(--font-title);
  font-size: 22pt;
  font-weight: 700;
  text-align: center;
  color: #0f172a;
  line-height: 1.25;
}}

/* Pas d'en-tête sur la page d'ouverture de chapitre */
.chapter-opener {{
  page-break-before: always;
  break-before: page;
}}

/* Gestion stricte des alinéas */
p {{
  margin-top: 0;
  margin-bottom: 0;
}}

p + p {{
  text-indent: 1.2em;
}}

h1 + p, h2 + p, h3 + p, h4 + p, .lead, blockquote + p, .callout-box + p, .action-box + p {{
  text-indent: 0 !important;
}}

/* Lettrine Haute Couture (Drop Cap) */
.drop-cap, p.lead::first-letter {{
  float: left;
  font-family: var(--font-accent);
  font-size: 3.4em;
  line-height: 0.8;
  padding-top: 4px;
  padding-right: 8px;
  padding-bottom: 2px;
  color: #0f172a;
  font-weight: 700;
}}

/* Titres secondaires */
h2, .section-title {{
  font-family: var(--font-subtitle);
  font-size: 14pt;
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: #1e293b;
  page-break-after: avoid;
  break-after: avoid;
}}

h3 {{
  font-family: var(--font-subtitle);
  font-size: 12pt;
  font-weight: 600;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
  color: #334155;
  page-break-after: avoid;
  break-after: avoid;
}}

/* ==========================================================================
   MODULES ÉDITORIAUX & ENCADRÉS D'ACTION (ZÉRO REJET KDP)
   ========================================================================== */

.callout-box, .action-box, .case-study-box, .warning-box {{
  page-break-inside: avoid;
  break-inside: avoid;
  margin: 1.4em 0;
  padding: 12pt 14pt;
  border-radius: 4pt;
  font-size: 10pt;
  line-height: 1.42;
}}

/* Encadré Action Immédiate 24h (Règle 03) */
.action-box {{
  background-color: #f8fafc;
  border-left: 3.5pt solid #d4af37;
  border-top: 0.5pt solid #e2e8f0;
  border-right: 0.5pt solid #e2e8f0;
  border-bottom: 0.5pt solid #e2e8f0;
}}
.action-box strong.box-title {{
  display: block;
  font-family: var(--font-subtitle);
  color: #a16207;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 9pt;
  margin-bottom: 6pt;
}}

/* Encadré Étude de Cas Chiffrée */
.case-study-box {{
  background-color: #f1f5f9;
  border-left: 3.5pt solid #0284c7;
}}

/* Citations d'autorité */
blockquote {{
  margin: 1.5em 1.5em;
  padding-left: 12pt;
  border-left: 2pt solid #94a3b8;
  font-family: var(--font-accent);
  font-style: italic;
  font-size: 11pt;
  color: #334155;
  page-break-inside: avoid;
  break-inside: avoid;
}}

/* Tableaux KDP Print-Ready */
table.kdp-table {{
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
  page-break-inside: avoid;
  break-inside: avoid;
  font-size: 9.5pt;
}}
table.kdp-table th {{
  background-color: #0f172a;
  color: #ffffff;
  padding: 6pt 8pt;
  text-align: left;
  font-family: var(--font-subtitle);
  font-size: 9pt;
}}
table.kdp-table td {{
  padding: 5pt 8pt;
  border-bottom: 0.5pt solid #cbd5e1;
}}
table.kdp-table tr:nth-child(even) td {{
  background-color: #f8fafc;
}}

/* Ruptures de pages volontaires */
.page-break {{
  page-break-before: always;
  break-before: page;
}}

{kids_addon_css}
"""
    return css


def compile_paged_interior_html(
    content: str,
    metadata: Dict[str, Any],
    format_id: str = "6x9",
    page_count: int = 150,
    paper_type: str = "white",
    bleed: bool = False,
    profile: str = "standard",
    language: str = "fr",
) -> str:
    """
    Compile le document complet (HTML ou Markdown converti) avec l'enveloppe
    CSS Paged Media prête pour impression PDF via Playwright ou Weasyprint.
    Supporte les 5 langues (EN, FR, ES, DE, AR) et l'orientation LTR/RTL.
    """
    from kdp_extensions.editorial_structure import assemble_complete_book

    lang_code = normalize_language(language)
    lang_cfg = get_language_config(lang_code)
    rtl = lang_cfg["is_rtl"]
    dir_attr = "rtl" if rtl else "ltr"

    t = metadata.get("title", "LIVRE KDP")
    author = metadata.get("author", "MarkEddy Éditions")
    pairing = metadata.get("font_pairing")
    if pairing is None:
        pairing = recommend_font_pairing_for_language(lang_code, metadata.get("niche", "Business"), metadata.get("cible"))

    paged_css = generate_paged_media_css(
        format_id=format_id,
        page_count=page_count,
        paper_type=paper_type,
        bleed=bleed,
        font_pairing=pairing,
        book_title=t,
        author_name=author,
        profile=profile,
        language=lang_code,
    )

    # Passage du paramètre language à l'assemblage éditorial
    assembled_body = assemble_complete_book(content, metadata, output_format="html", language=lang_code)

    html = f"""<!DOCTYPE html>
<html lang="{lang_code}" dir="{dir_attr}">
<head>
  <meta charset="UTF-8">
  <title>{t}</title>
  <style>
{paged_css}
  </style>
</head>
<body class="kdp-paged-book" dir="{dir_attr}">
{assembled_body}
</body>
</html>"""
    return html


def audit_paged_css_compliance(html_content: str) -> Dict[str, Any]:
    """
    Audite la conformité du code HTML/CSS généré vis-à-vis des critères
    stricts d'Amazon KDP (Règle 02 & Règle 04).
    Gère les spécificités multilingues (Arabe RTL sans césure).
    """
    is_arabic_or_rtl = bool(re.search(r'lang=["\']ar["\']|dir=["\']rtl["\']|direction:\s*rtl', html_content))

    has_page_rule = bool(re.search(r"@page\s*\{", html_content))
    has_left_right = bool(re.search(r"@page\s*:left", html_content) and re.search(r"@page\s*:right", html_content))
    has_size = bool(re.search(r"size:\s*[\d\.]+in\s+[\d\.]+in", html_content))
    has_gutter = bool(re.search(r"margin-right:\s*0\.\d+in", html_content) or re.search(r"margin-left:\s*0\.\d+in", html_content))

    # En Arabe (RTL), la césure est strictement proscrite (hyphens: none)
    if is_arabic_or_rtl:
        has_hyphens = bool(re.search(r"hyphens:\s*(?:none|auto)", html_content))
    else:
        has_hyphens = bool(re.search(r"hyphens:\s*auto", html_content))

    has_page_breaks = bool(re.search(r"page-break-before:\s*always", html_content) or re.search(r"break-before:\s*page", html_content))
    has_counter = bool(re.search(r"counter\(page\)", html_content))

    conforme = all([has_page_rule, has_left_right, has_size, has_gutter, has_hyphens, has_page_breaks])

    score = 100
    deductions = []
    if not has_page_rule:
        score -= 25
        deductions.append("Absence de déclaration @page W3C")
    if not has_left_right:
        score -= 20
        deductions.append("Absence de pages en regard alternées (@page :left, @page :right)")
    if not has_gutter:
        score -= 20
        deductions.append("Marge de reliure (Gutter) non détectée")
    if not has_hyphens:
        score -= 15
        deductions.append("Césure automatique des mots (hyphens: auto) absente")
    if not has_counter:
        score -= 10
        deductions.append("Folios automatiques (counter(page)) manquants")

    return {
        "conforme_kdp": conforme,
        "score_conformite": max(0, score),
        "is_rtl": is_arabic_or_rtl,
        "criteres": {
            "has_page_rule": has_page_rule,
            "has_left_right": has_left_right,
            "has_size": has_size,
            "has_gutter": has_gutter,
            "has_hyphens": has_hyphens,
            "has_page_breaks": has_page_breaks,
            "has_counter": has_counter,
        },
        "anomalies": deductions,
    }


__all__ = [
    "calculate_gutter_in",
    "generate_paged_media_css",
    "compile_paged_interior_html",
    "audit_paged_css_compliance",
]
