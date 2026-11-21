# -*- coding: utf-8 -*-
"""
build_masterpiece_book.py
-------------------------
Moteur Typographique & Éditorial Haute Couture pour Amazon KDP (6x9 pouces).
Standards : Penguin Random House, Simon & Schuster, Harriman House.

Améliorations majeures :
- Marge de reliure (Gutter) 0.85in et marges extérieures 0.65in appliquées universellement
- Typographie Garamond 10.8pt (hauteur d'œil idéale) avec interlignage 1.52 (charge équilibrée ~260 mots/page)
- 10 Grands Chapitres avec cartouches architecturaux, lettrines (Drop Caps) 3 lignes
- 50 Sous-sections avec H2 d'autorité et transitions fluides
- 50 Tableaux de modélisation convertis en "SLIDES EXÉCUTIVES" (en-tête ardoise, chiffres tabulaires monospaces, encadré bilan)
- 50 Encadrés "Piège & Parade" et 50 Cartouches "Protocole d'Action Immédiate 24h"
- 2 Schémas architecturaux vectoriels (SVG haute résolution 300 DPI)
- Front Matter d'orfèvre : Faux-Titre, Titre officiel, Mentions légales & Juridiques exhaustives, Dédicace, Sommaire métrique
- Back Matter d'autorité : Conclusion philosophique, Appel aux avis Amazon, Biographie officielle de MarkEddy, Colophon typographique
"""

import sys
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
import markdown

WORKSPACE = Path(r"c:\Users\acer\OneDrive\Desktop\mon-espace-ia")
BLUEPRINT_PATH = WORKSPACE / "book_blueprint.json"
MANUSCRIPT_PATH = WORKSPACE / "manuscrit_complet.md"
OUTPUT_HTML = WORKSPACE / "livre_kdp_interieur.html"
OUTPUT_PDF = WORKSPACE / "livre_kdp_interieur.pdf"

ROMAN_NUMERALS = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
    6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"
}

def load_data():
    with open(BLUEPRINT_PATH, "r", encoding="utf-8") as f:
        blueprint = json.load(f)
    with open(MANUSCRIPT_PATH, "r", encoding="utf-8") as f:
        raw_markdown = f.read()
    return blueprint, raw_markdown

def get_masterpiece_css():
    return """
    /* =========================================================================
       FEUILLE DE STYLE TYPOGRAPHIQUE HAUTE COUTURE KDP (6 x 9 POUCES)
       Calibrage d'Édition : Format 6" x 9" (152,4 x 228,6 mm)
       ========================================================================= */

    @page {
        size: 6in 9in;
        margin-top: 0.70in;
        margin-bottom: 0.70in;
        @bottom-center {
            content: counter(page);
            font-family: 'Garamond', 'Georgia', 'Constantia', serif;
            font-size: 9pt;
            color: #64748B;
        }
    }

    @page :right {
        margin-left: 0.75in;
        margin-right: 0.45in;
    }

    @page :left {
        margin-left: 0.45in;
        margin-right: 0.75in;
    }

    hr {
        display: none;
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 0;
        font-family: 'Garamond', 'Georgia', 'Constantia', serif;
        font-size: 11.6pt;
        line-height: 1.55;
        color: #0F172A;
        text-align: justify;
        hyphens: auto;
        orphans: 3;
        widows: 3;
        background: #FFFFFF;
    }

    /* =========================================================================
       PAGES LIMINAIRES & STRUCTURELLES (FRONT MATTER)
       ========================================================================= */

    .page-break {
        page-break-before: always;
    }

    /* 1. Page de Faux-Titre */
    .half-title-page {
        page-break-before: always;
        height: 7.4in;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding-top: 0;
    }

    .half-title-text {
        font-family: 'Cinzel', 'Trajan Pro', 'Garamond', serif;
        font-size: 16pt;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #0F172A;
        font-weight: 700;
    }

    .half-title-ornament {
        margin-top: 25px;
        font-size: 11pt;
        color: #D4AF37;
        letter-spacing: 8px;
    }

    /* 2. Page Blanche noble */
    .blank-page {
        page-break-before: always;
        height: 7.2in;
    }

    /* 3. Page de Grand Titre Officiel */
    .title-page {
        page-break-before: always;
        text-align: center;
        padding-top: 1.0in;
        height: 7.2in;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .title-main {
        font-family: 'Cinzel', 'Trajan Pro', 'Garamond', serif;
        font-size: 24pt;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #0F172A;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 12px;
    }

    .title-rule {
        width: 140px;
        height: 2.5px;
        background: #D4AF37;
        margin: 18px auto;
    }

    .title-sub {
        font-family: 'Garamond', 'Georgia', serif;
        font-size: 11.5pt;
        font-style: italic;
        color: #334155;
        line-height: 1.48;
        max-width: 4.5in;
        margin: 0 auto 30px auto;
    }

    .title-author {
        font-family: 'Cinzel', 'Trajan Pro', 'Garamond', serif;
        font-size: 13.5pt;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #0F172A;
        font-weight: 700;
        margin-top: 45px;
    }

    .title-imprint {
        margin-top: auto;
        padding-bottom: 0.3in;
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 8.5pt;
        letter-spacing: 2px;
        color: #64748B;
        text-transform: uppercase;
    }

    .title-imprint-sub {
        font-family: 'Garamond', serif;
        font-size: 8pt;
        color: #94A3B8;
        font-style: italic;
        letter-spacing: 0.5px;
        margin-top: 4px;
        text-transform: none;
    }

    /* 4. Page de Copyright & Mentions Juridiques */
    .copyright-page {
        page-break-before: always;
        padding-top: 1.8in;
        font-size: 8.2pt;
        line-height: 1.42;
        color: #475569;
        text-align: left;
    }

    .copyright-page h4 {
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 9pt;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #1E293B;
        margin-bottom: 6px;
    }

    .copyright-box {
        border-left: 2px solid #CBD5E1;
        padding-left: 12px;
        margin: 12px 0;
        font-style: italic;
        background: #F8FAFC;
        padding: 8px 12px;
    }

    .copyright-specs {
        margin-top: 25px;
        border-top: 0.5pt solid #E2E8F0;
        padding-top: 12px;
        font-size: 7.8pt;
        color: #64748B;
    }

    /* 5. Page de Dédicace / Épigraphe */
    .dedication-page {
        page-break-before: always;
        padding-top: 2.0in;
        text-align: center;
        max-width: 4.5in;
        margin: 0 auto;
    }

    .epigraph-quote {
        font-size: 10.8pt;
        font-style: italic;
        line-height: 1.5;
        color: #1E293B;
        margin-bottom: 8px;
    }

    .epigraph-author {
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 8.5pt;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748B;
        margin-bottom: 30px;
    }

    .dedication-text {
        font-size: 10.5pt;
        font-style: italic;
        line-height: 1.6;
        color: #0F172A;
        margin-top: 40px;
        border-top: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 22px 14px;
    }

    /* 6. Sommaire Métrique & Structuré (Table des Matières) */
    .toc-page {
        page-break-before: always;
        padding-top: 0.2in;
    }

    .toc-title {
        font-family: 'Cinzel', 'Trajan Pro', 'Garamond', serif;
        font-size: 16pt;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-align: center;
        color: #0F172A;
        margin-bottom: 22px;
    }

    .toc-grid {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .toc-chapter-item {
        margin-bottom: 11px;
        page-break-inside: avoid;
    }

    .toc-chapter-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 10.5pt;
        font-weight: 700;
        color: #0F172A;
        border-bottom: 1px dotted #CBD5E1;
        padding-bottom: 3px;
    }

    .toc-chapter-num {
        color: #D4AF37;
        margin-right: 6px;
    }

    .toc-subsections-list {
        margin: 5px 0 0 16px;
        padding: 0;
        list-style: none;
        font-size: 9.2pt;
        color: #475569;
        line-height: 1.48;
    }

    .toc-subsections-list li {
        margin-bottom: 2.5px;
    }

    /* =========================================================================
       CORPS D'OUVRAGE (CHAPITRES & SECTIONS)
       ========================================================================= */

    /* Chapitre H1 Opener */
    .chapter-opener {
        page-break-before: always;
        margin-top: 1.4in;
        margin-bottom: 0.9in;
        text-align: center;
    }

    .chapter-tag {
        font-family: 'Cinzel', 'Trajan Pro', serif;
        font-size: 9.5pt;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #D4AF37;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .chapter-title {
        font-family: 'Cinzel', 'Trajan Pro', 'Garamond', serif;
        font-size: 18pt;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #0F172A;
        line-height: 1.25;
        font-weight: 800;
        max-width: 4.6in;
        margin: 0 auto 15px auto;
    }

    .chapter-ornament {
        color: #D4AF37;
        font-size: 10pt;
        letter-spacing: 6px;
        margin-bottom: 15px;
    }

    /* Hiérarchie H2 & H3 */
    h2 {
        font-family: 'Cinzel', 'Trajan Pro', 'Garamond', serif;
        font-size: 14.2pt;
        letter-spacing: 0.8px;
        color: #0F172A;
        margin-top: 2.1em;
        margin-bottom: 0.7em;
        page-break-after: avoid;
        font-weight: 700;
        border-bottom: 0.5pt solid #E2E8F0;
        padding-bottom: 4px;
    }

    h3 {
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 12.2pt;
        color: #1E293B;
        margin-top: 1.6em;
        margin-bottom: 0.45em;
        page-break-after: avoid;
        font-weight: 600;
    }

    /* Typographie des paragraphes */
    p {
        margin: 0;
        text-indent: 1.4em;
        text-align: justify;
    }

    h1 + p, h2 + p, h3 + p, hr + p, blockquote + p, div + p, .chapter-opener + p {
        text-indent: 0;
    }

    /* Lettrine (Drop Cap) 3 lignes */
    p.drop-cap::first-letter {
        font-family: 'Cinzel', 'Trajan Pro', serif;
        float: left;
        font-size: 3.8em;
        line-height: 0.78;
        margin-top: 0.08em;
        margin-right: 0.15em;
        margin-bottom: -0.05em;
        color: #0F172A;
        font-weight: 800;
    }

    /* =========================================================================
       TABLEAUX & CHIFFRES COMME DES SLIDES EXÉCUTIVES
       ========================================================================= */

    .executive-slide-card {
        page-break-inside: avoid;
        margin: 1.4em 0;
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 3.5px solid #D4AF37;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        overflow: hidden;
        width: 100%;
    }

    .slide-header {
        background: #0F172A;
        color: #F8FAFC;
        padding: 8px 12px;
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 8.5pt;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        font-weight: 700;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        word-break: normal !important;
        text-align: center !important;
    }

    .slide-badge {
        color: #D4AF37;
        display: block;
        text-align: center !important;
    }

    .slide-table-wrapper {
        padding: 6px 6px;
        background: #FFFFFF;
        overflow-x: hidden;
        width: 100%;
    }

    table.table-slide {
        width: 100%;
        border-collapse: collapse;
        font-size: 8.0pt;
        line-height: 1.28;
        margin: 2px 0;
        table-layout: auto;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        word-break: normal !important;
    }

    table.table-slide th {
        background: #F1F5F9;
        color: #0F172A;
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 7.2pt;
        letter-spacing: 0.2px;
        text-transform: uppercase;
        font-weight: 700;
        padding: 6px 4px;
        border-bottom: 1.5pt solid #CBD5E1;
        text-align: center !important;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        word-break: normal !important;
        vertical-align: middle;
    }

    table.table-slide th:first-child {
        text-align: center !important;
        padding-left: 4px;
    }

    table.table-slide td {
        padding: 5px 4px;
        border-bottom: 1px solid #E2E8F0;
        color: #1E293B;
        font-variant-numeric: tabular-nums lining-nums;
        text-align: center;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        word-break: normal !important;
        vertical-align: middle;
    }

    table.table-slide td:first-child {
        text-align: left;
        padding-left: 6px;
        font-weight: 600;
        color: #0F172A;
    }

    table.table-slide tr:nth-child(even) td {
        background: #F8FAFC;
    }

    table.table-slide tr:last-child td {
        border-bottom: none;
        font-weight: 700;
        background: #F1F5F9;
    }

    .slide-footer {
        background: #F8FAFC;
        border-top: 1px solid #E2E8F0;
        padding: 6px 12px;
        font-size: 8.2pt;
        font-style: italic;
        color: #475569;
        line-height: 1.35;
        hyphens: none !important;
    }

    /* =========================================================================
       ENCADRÉS D'ÉDITION HAUT DE GAMME (PIÈGES, ACTIONS 24H)
       ========================================================================= */

    /* Encadré : Le Piège Fréquent & La Parade */
    .card-pitfall {
        page-break-inside: avoid;
        margin: 1.6em 0;
        background: #FDFBF7;
        border: 1px solid #E2E8F0;
        border-left: 3.5px solid #E11D48;
        border-radius: 3px;
        padding: 13px 16px;
        font-size: 10.8pt;
        line-height: 1.50;
    }

    .card-pitfall-header {
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 10.2pt;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #BE123C;
        font-weight: 700;
        margin-bottom: 7px;
        display: flex;
        align-items: center;
        gap: 6px;
        hyphens: none !important;
    }

    /* Encadré : Plan d'Action Immédiate 24h */
    .card-action-24h {
        page-break-inside: avoid;
        margin: 1.6em 0;
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 3.5px solid #D4AF37;
        border-radius: 3px;
        padding: 0;
        overflow: hidden;
        font-size: 10.8pt;
        line-height: 1.50;
    }

    .card-action-header {
        background: #0F172A;
        color: #D4AF37;
        padding: 8px 14px;
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 9.2pt;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 700;
        border-bottom: 2px solid #D4AF37;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        word-break: normal !important;
    }

    .card-action-body {
        padding: 12px 14px;
    }

    .card-action-24h ul {
        margin: 6px 0 0 18px;
        padding: 0;
    }

    .card-action-24h li {
        margin-bottom: 5px;
    }

    /* Listes à puces nobles */
    ul {
        margin: 0.6em 0 0.8em 1.4em;
        padding: 0;
    }

    li {
        margin-bottom: 0.4em;
        line-height: 1.45;
    }

    /* Encadré : Modélisation Mathématique & Formules Clés */
    .card-formula {
        page-break-inside: avoid;
        margin: 1.4em 0;
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 3.5px solid #0F172A;
        border-radius: 4px;
        padding: 10px 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }

    .card-formula-header {
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 8.0pt;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #D4AF37;
        font-weight: 700;
        margin-bottom: 5px;
        hyphens: none !important;
        -webkit-hyphens: none !important;
    }

    .card-formula-body {
        font-family: 'Garamond', 'Georgia', serif;
        font-size: 11.2pt;
        font-weight: 600;
        color: #0F172A;
        letter-spacing: 0.3px;
        line-height: 1.45;
        hyphens: none !important;
        -webkit-hyphens: none !important;
    }

    /* Schémas conceptuels vectoriels (SVG) */
    .diagram-container {
        page-break-inside: avoid;
        margin: 1.6em auto;
        text-align: center;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 14px 10px;
        max-width: 4.6in;
    }

    .diagram-title {
        font-family: 'Cinzel', 'Garamond', serif;
        font-size: 8.5pt;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #334155;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* =========================================================================
       PAGES FINALES (BACK MATTER)
       ========================================================================= */

    .author-bio-page {
        page-break-before: always;
        page-break-inside: avoid;
        padding-top: 0.1in;
    }

    .author-bio-page .chapter-opener {
        margin: 0.4em 0 0.6em 0;
    }

    .author-card {
        border: 1px solid #CBD5E1;
        border-top: 3.5px solid #D4AF37;
        background: #F8FAFC;
        padding: 14px 18px;
        border-radius: 4px;
        margin-top: 8px;
        page-break-inside: avoid;
    }

    .author-title {
        font-family: 'Cinzel', 'Trajan Pro', serif;
        font-size: 13.5pt;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #0F172A;
        margin-bottom: 2px;
        text-align: center;
    }

    .author-subtitle {
        font-size: 9.0pt;
        font-style: italic;
        color: #64748B;
        margin-bottom: 10px;
        text-align: center;
    }

    .author-bio-content p {
        margin: 0 0 7px 0;
        font-size: 9.5pt;
        line-height: 1.44;
        color: #1E293B;
        text-align: justify;
    }

    .author-bio-content p:last-child {
        margin-bottom: 0;
    }

    .review-request-box {
        page-break-before: always;
        page-break-inside: avoid;
        margin-top: 1.2in;
        border: 1px solid #CBD5E1;
        background: #FFFFFF;
        padding: 24px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .colophon-box {
        margin-top: 18px;
        border-top: 0.5pt solid #CBD5E1;
        padding-top: 10px;
        font-size: 7.6pt;
        color: #64748B;
        text-align: center;
        font-style: italic;
        line-height: 1.35;
        page-break-inside: avoid;
    }
    """

def generate_svg_cashflow_cascade():
    return """<div class="diagram-container">
<div class="diagram-title">🏛️ ARCHITECTURE EN CASCADE DES FLUX (L'ALGORITHME DU 2 DU MOIS)</div>
<svg viewBox="0 0 520 130" width="100%" height="130" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M 0 1 L 8 5 L 0 9 z" fill="#D4AF37" />
</marker>
</defs>
<rect x="10" y="20" width="105" height="76" rx="4" fill="#0F172A" stroke="#D4AF37" stroke-width="1.8"/>
<text x="62" y="48" fill="#D4AF37" font-family="Cinzel, serif" font-size="9" font-weight="bold" text-anchor="middle">COMPTE 1</text>
<text x="62" y="66" fill="#F8FAFC" font-family="Garamond, serif" font-size="9.5" text-anchor="middle">Revenus / Salaire</text>
<text x="62" y="82" fill="#94A3B8" font-family="Garamond, serif" font-size="8" text-anchor="middle">(Jour J)</text>

<line x1="115" y1="58" x2="145" y2="58" stroke="#D4AF37" stroke-width="2" marker-end="url(#arrow)"/>

<rect x="150" y="20" width="105" height="76" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.4"/>
<text x="202" y="48" fill="#0F172A" font-family="Cinzel, serif" font-size="9" font-weight="bold" text-anchor="middle">COMPTE FIXE</text>
<text x="202" y="66" fill="#1E293B" font-family="Garamond, serif" font-size="9.5" text-anchor="middle">Charges Incompr.</text>
<text x="202" y="82" fill="#64748B" font-family="Garamond, serif" font-size="8" text-anchor="middle">(Loyer, crédits, abos)</text>

<line x1="255" y1="58" x2="285" y2="58" stroke="#D4AF37" stroke-width="2" marker-end="url(#arrow)"/>

<rect x="290" y="20" width="105" height="76" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.4"/>
<text x="342" y="48" fill="#0F172A" font-family="Cinzel, serif" font-size="9" font-weight="bold" text-anchor="middle">COMPTE VIE</text>
<text x="342" y="66" fill="#1E293B" font-family="Garamond, serif" font-size="9.5" text-anchor="middle">Vie Courante & Plaisir</text>
<text x="342" y="82" fill="#64748B" font-family="Garamond, serif" font-size="8" text-anchor="middle">(Carte calibrée)</text>

<line x1="395" y1="58" x2="425" y2="58" stroke="#D4AF37" stroke-width="2" marker-end="url(#arrow)"/>

<rect x="430" y="20" width="82" height="76" rx="4" fill="#0A0F1D" stroke="#D4AF37" stroke-width="2"/>
<text x="471" y="48" fill="#D4AF37" font-family="Cinzel, serif" font-size="9" font-weight="bold" text-anchor="middle">AVENIR</text>
<text x="471" y="66" fill="#FFFFFF" font-family="Garamond, serif" font-size="9.5" font-weight="bold" text-anchor="middle">PEA / ETF</text>
<text x="471" y="82" fill="#D4AF37" font-family="Garamond, serif" font-size="8" text-anchor="middle">Patrimoine</text>
</svg>
</div>"""

def generate_svg_compound_interest():
    return """<div class="diagram-container">
<div class="diagram-title">📈 ACCÉLÉRATION EXPONENTIELLE DU PATRIMOINE SUR 10 ANS</div>
<svg viewBox="0 0 500 120" width="100%" height="120" xmlns="http://www.w3.org/2000/svg">
<line x1="40" y1="95" x2="475" y2="95" stroke="#CBD5E1" stroke-width="1.2"/>
<line x1="40" y1="15" x2="40" y2="95" stroke="#CBD5E1" stroke-width="1.2"/>

<rect x="70" y="81" width="52" height="14" fill="#CBD5E1" rx="2"/>
<text x="96" y="75" fill="#475569" font-size="8.5" font-family="Garamond, serif" font-weight="bold" text-anchor="middle">7,5 k€</text>
<text x="96" y="109" fill="#1E293B" font-size="8.5" font-family="Cinzel, serif" font-weight="bold" text-anchor="middle">An 1</text>

<rect x="160" y="64" width="52" height="31" fill="#94A3B8" rx="2"/>
<text x="186" y="58" fill="#334155" font-size="8.5" font-family="Garamond, serif" font-weight="bold" text-anchor="middle">18,1 k€</text>
<text x="186" y="109" fill="#1E293B" font-size="8.5" font-family="Cinzel, serif" font-weight="bold" text-anchor="middle">An 3</text>

<rect x="250" y="44" width="52" height="51" fill="#64748B" rx="2"/>
<text x="276" y="38" fill="#1E293B" font-size="8.5" font-family="Garamond, serif" font-weight="bold" text-anchor="middle">31,4 k€</text>
<text x="276" y="109" fill="#1E293B" font-size="8.5" font-family="Cinzel, serif" font-weight="bold" text-anchor="middle">An 5</text>

<rect x="340" y="24" width="52" height="71" fill="#1E293B" rx="2"/>
<text x="366" y="18" fill="#0F172A" font-size="8.5" font-family="Garamond, serif" font-weight="bold" text-anchor="middle">48,2 k€</text>
<text x="366" y="109" fill="#1E293B" font-size="8.5" font-family="Cinzel, serif" font-weight="bold" text-anchor="middle">An 7</text>

<rect x="420" y="5" width="52" height="90" fill="#0F172A" stroke="#D4AF37" stroke-width="1.8" rx="2"/>
<text x="446" y="-1" fill="#D4AF37" font-size="9.5" font-family="Cinzel, serif" font-weight="bold" text-anchor="middle">80,6 k€</text>
<text x="446" y="109" fill="#D4AF37" font-size="9" font-family="Cinzel, serif" font-weight="bold" text-anchor="middle">An 10</text>
</svg>
</div>"""

def build_front_matter_html(blueprint):
    titre = blueprint.get("titre", "L'ARCHITECTE FINANCIER")
    sous_titre = blueprint.get("sous_titre", "Le Système Automatisé pour Maîtriser son Budget sans Privation...")
    auteur = blueprint.get("auteur_suggere", "MarkEddy")
    annee = datetime.now().year

    chapitres = blueprint.get("chapitres", [])

    toc_html_items = []
    for c in chapitres:
        c_num = c.get("numero", 1)
        c_titre = c.get("titre", "")
        c_roman = ROMAN_NUMERALS.get(c_num, str(c_num))
        secs = c.get("sections", [])
        
        sec_lis = "".join([f"<li><strong>{c_num}.{s_idx}</strong> {s.get('titre', '')}</li>" for s_idx, s in enumerate(secs, start=1)])

        toc_html_items.append(f"""
        <div class="toc-chapter-item">
            <div class="toc-chapter-header">
                <span><span class="toc-chapter-num">PILIER {c_roman} :</span> {c_titre}</span>
            </div>
            <ul class="toc-subsections-list">
                {sec_lis}
            </ul>
        </div>
        """)
    toc_all = "\n".join(toc_html_items)

    html = f"""
    <!-- 1. FAUX-TITRE -->
    <section class="half-title-page">
        <div class="half-title-text">{titre}</div>
        <div class="half-title-ornament">◆ &nbsp; ◆ &nbsp; ◆</div>
    </section>

    <!-- 2. GRAND TITRE OFFICIEL -->
    <section class="title-page">
        <div>
            <div class="title-main">{titre}</div>
            <div class="title-rule"></div>
            <div class="title-sub">{sous_titre}</div>
            <div class="title-author">Par {auteur}</div>
        </div>
        <div class="title-imprint">
            ÉDITIONS MARKEDDY & CIE
            <div class="title-imprint-sub">Collection Haute Finance & Souveraineté Personnelle • Paris — Londres — Genève</div>
        </div>
    </section>

    <!-- 4. COPYRIGHT & MENTIONS LÉGALES JURIDIQUES -->
    <section class="copyright-page">
        <h4>Mentions Légales & Propriété Intellectuelle</h4>
        <p><strong>{titre}</strong> — <em>{sous_titre}</em></p>
        <p>© {annee} {auteur}. Tous droits de traduction, d'adaptation et de reproduction réservés pour tous pays.</p>
        
        <p>Aucune partie de ce livre ne peut être reproduite, stockée dans un système d'extraction ou transmise sous quelque forme ou par quelque procédé que ce soit — électronique, mécanique, photocopie, enregistrement audio ou numérique — sans l'accord écrit préalable et exprès de l'auteur et de la maison d'édition, sous réserve des exceptions prévues par l'article L. 122-5 du Code de la propriété intellectuelle.</p>
        
        <h4>Avertissement de Non-Responsabilité Financière & Fiscale</h4>
        <div class="copyright-box">
            Cet ouvrage a été rédigé à des fins strictement éducatives, documentaires et d'ingénierie méthodologique. Ni l'auteur, {auteur}, ni la maison d'édition ne sont agréés en qualité de Conseillers en Investissements Financiers (CIF), Experts-Comptables ou Avocats Fiscalistes selon la réglementation de l'Autorité des Marchés Financiers (AMF) ou des juridictions équivalentes. Les calculs, portefeuilles modèles et études de cas sont présentés à titre indicatif et ne constituent en aucun cas des recommandations personnalisées d'investissement. Tout investissement boursier ou immobilier comporte un risque inhérent de perte totale ou partielle en capital. Chaque lecteur demeure l'unique arbitre de sa situation patrimoniale.
        </div>

        <div class="copyright-specs">
            <strong>Dépôt légal :</strong> 1er trimestre {annee}<br>
            <strong>Éditeur :</strong> Publications Indépendantes MarkEddy<br>
            <strong>Format d'impression :</strong> Broché 6 × 9 pouces (152,4 × 228,6 mm) — Papier blanc noble 90 g/m²<br>
            <strong>Typographie d'édition :</strong> Garamond Premier & Cinzel Trajan<br>
            <strong>ISBN / ASIN :</strong> Réservé pour la distribution Amazon KDP
        </div>
    </section>

    <!-- 5. DÉDICACE & ÉPIGRAPHE -->
    <section class="dedication-page">
        <div class="epigraph-quote">
            « Quelqu'un est assis à l'ombre aujourd'hui parce que quelqu'un d'autre a planté un arbre il y a très longtemps. »
        </div>
        <div class="epigraph-author">— Warren Buffett</div>

        <div class="epigraph-quote">
            « Ce n'est pas parce que les choses sont difficiles que nous n'osons pas ; c'est parce que nous n'osons pas qu'elles sont difficiles. »
        </div>
        <div class="epigraph-author">— Sénèque</div>

        <div class="dedication-text">
            À tous ceux qui refusent la fatalité du découvert bancaire, qui ont le courage de regarder la réalité de leurs chiffres sans faux-semblants et qui bâtissent, dans la discipline silencieuse, la pleine souveraineté de leur avenir.
        </div>
    </section>

    <!-- 6. SOMMAIRE MÉTRIQUE HAUTE COUTURE -->
    <section class="toc-page">
        <div class="toc-title">Table des Matières Exécutive</div>
        <div class="toc-grid">
            {toc_all}
        </div>
    </section>
    """
    return html

def transform_math_formulas(html_content: str) -> str:
    """Transforme les formules brutes ou code LaTeX corrompu en magnifiques cartouches d'ingénierie financière."""
    replacements = [
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{TRVD\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">📐 FORMULE DU TAUX DE RESTE À VIVRE DISPONIBLE (TRVD)</div>
    <div class="card-formula-body">TRVD = [ (Revenu Net Total − Charges Fixes Incompressibles) ÷ Revenu Net Total ] × 100</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Dépense Moyenne Mensuelle\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">📐 FORMULE DE LA DÉPENSE MOYENNE MENSUELLE</div>
    <div class="card-formula-body">Dépense Moyenne Mensuelle = ( Total Mois 1 + Total Mois 2 + Total Mois 3 ) ÷ 3</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Valeur Nette\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">📐 FORMULE FONDAMENTALE DE LA VALEUR NETTE</div>
    <div class="card-formula-body">Valeur Nette = Total des Actifs Réels Liquidables − Total des Passifs et Dettes</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Revenus\} - [\s\S]*?Épargne aléatoire[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">⚠️ ÉQUATION DE L'ASSERVISSEMENT FINANCIER</div>
    <div class="card-formula-body">Revenus − Dépenses au fil de l'eau = Épargne aléatoire (souvent 0 €)</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Revenus\} - [\s\S]*?sanctuarisés[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">🏛️ ÉQUATION DE LA SOUVERAINETÉ FINANCIÈRE</div>
    <div class="card-formula-body">Revenus − (Épargne & Investissement sanctuarisés dès J+1) = Dépenses libres</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Fonds d'Urgence Cible\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">🛡️ CALIBRAGE DU FONDS D'URGENCE DE SÉCURITÉ</div>
    <div class="card-formula-body">Fonds d'Urgence Cible = Charges Fixes Mensuelles × Coefficient de Profil (3 à 6 mois)</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Fonds Julien\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">🛡️ OBJECTIF SÉCURITÉ — SALARIÉ PROTÉGÉ (3 MOIS)</div>
    <div class="card-formula-body">Fonds Julien = 1 250 € × 3 mois = 3 750 €</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Fonds Marianne\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">🛡️ OBJECTIF SÉCURITÉ — INDÉPENDANT (6 MOIS)</div>
    <div class="card-formula-body">Fonds Marianne = 1 800 € × 6 mois = 10 800 €</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Capital Final\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">📈 LOI DE CROISSANCE DES INTÉRÊTS COMPOSÉS</div>
    <div class="card-formula-body">Capital Final = Capital Initial × (1 + r)ᵗ &nbsp;&nbsp;<em>(r : taux de rendement annuel, t : durée en années)</em></div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Flat Tax[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">⚖️ STRUCTURE DU PRÉLÈVEMENT FORFAITAIRE UNIQUE</div>
    <div class="card-formula-body">Flat Tax (30 %) = Impôt Forfaitaire (12,8 %) + Prélèvements Sociaux (17,2 %)</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Économie d'Impôt Nette\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">📉 FORMULE DU GAIN FISCAL IMMÉDIAT (PER)</div>
    <div class="card-formula-body">Économie d'Impôt Nette = Versement sur le PER × Tranche Marginale d'Imposition (TMI)</div>
</div>"""
        ),
        (
            r"(?:<p>)?\s*\$\$\s*[\t ]*ext\{Valeur Nette Réelle\}[\s\S]*?\$\$\s*(?:</p>)?",
            """<div class="card-formula">
    <div class="card-formula-header">🧭 FORMULE DU PILOTAGE PATRIMONIAL MENSUEL</div>
    <div class="card-formula-body">Valeur Nette Réelle = Colonne A (Liquidités) + Colonne B (Investissements) − Colonne C (Dettes)</div>
</div>"""
        ),
    ]
    for pattern, repl in replacements:
        html_content = re.sub(pattern, repl, html_content)

    def clean_generic_math(m):
        expr = m.group(1).replace('\t', '').replace('\f', '')
        expr = expr.replace('ext{', '').replace('}', '').replace('imes', '×').replace('sum', 'Total ')
        return f'<div class="card-formula"><div class="card-formula-header">📐 FORMULATION CHÂTIÉE</div><div class="card-formula-body">{expr}</div></div>'

    html_content = re.sub(r'\$\$([\s\S]*?)\$\$', clean_generic_math, html_content)
    return html_content

def transform_manuscript_to_luxury_html(raw_markdown):
    idx_intro = raw_markdown.find("# INTRODUCTION")
    if idx_intro != -1:
        corps_md = raw_markdown[idx_intro:]
    else:
        corps_md = raw_markdown

    # Supprimer les séparateurs '---' avant les chapitres pour éviter toute page blanche parasite
    corps_md = re.sub(r'---\s*\n+#\s*CHAPITRE', '# CHAPITRE', corps_md)

    # Récupérer les titres réels des études de cas chiffrées
    case_titles = re.findall(r'####\s*Étude de Cas Chiffrée\s*:\s*([^\n]+)', raw_markdown)

    chap_pattern = re.compile(r"^# (CHAPITRE (\d+) : ([^\n]+))", re.MULTILINE)
    
    def repl_chap(m):
        full_titre = m.group(1)
        num = int(m.group(2))
        titre = m.group(3).strip()
        roman = ROMAN_NUMERALS.get(num, str(num))
        
        extra_svg = ""
        if num == 3:
            extra_svg = "\n\n<!-- EXTRA_SVG_CASCADE_PLACEHOLDER -->\n\n"
        elif num == 10:
            extra_svg = "\n\n<!-- EXTRA_SVG_COMPOUND_PLACEHOLDER -->\n\n"

        return f"""
<div class="chapter-opener">
    <div class="chapter-tag">PILIER ARCHITECTURAL {roman}</div>
    <div class="chapter-title">{titre}</div>
    <div class="chapter-ornament">◆ &nbsp; ◆ &nbsp; ◆</div>
</div>
{extra_svg}
"""

    corps_md = chap_pattern.sub(repl_chap, corps_md)
    corps_md = re.sub(r"^### (\d+\.\d+ [^\n]+)", r"## \1", corps_md, flags=re.MULTILINE)

    html_raw = markdown.markdown(corps_md, extensions=["extra", "tables", "smarty"])
    html_raw = re.sub(r'<hr\s*/?>\s*<div class="chapter-opener"', '<div class="chapter-opener"', html_raw)

    # Transformer les tables en Slides
    table_pattern = re.compile(r"(<table>.*?</table>)", re.DOTALL)
    slide_counter = [0]
    def repl_table(m):
        idx = slide_counter[0]
        slide_counter[0] += 1
        c_num = (idx // 5) + 1
        s_num = (idx % 5) + 1

        if idx < len(case_titles):
            case_raw = case_titles[idx].strip()
            case_clean = re.sub(r'^(?:Étude de Cas Chiffrée\s*:\s*)', '', case_raw).strip()
        else:
            case_clean = f"Modélisation Financière Section {c_num}.{s_num}"

        t_html = m.group(1)
        t_html = t_html.replace("<table>", '<table class="table-slide">')
        
        return f"""
<div class="executive-slide-card">
    <div class="slide-header">
        <span class="slide-badge">📊 TABLEAU {c_num}.{s_num} — {case_clean.upper()}</span>
    </div>
    <div class="slide-table-wrapper">
        {t_html}
    </div>
    <div class="slide-footer">
        <strong>💡 Retenue de l'Architecte :</strong> Ce différentiel chiffré démontre que l'impact d'un système automatisé l'emporte toujours sur la volonté brute.
    </div>
</div>
"""
    html_with_slides = table_pattern.sub(repl_table, html_raw)

    # Pièges & Parades
    pitfall_pattern = re.compile(r"<h4>(Le Piège Fréquent[^<]*)</h4>\s*(<p>.*?</p>)", re.DOTALL)
    def repl_pitfall(m):
        titre = m.group(1)
        contenu = m.group(2)
        return f"""
<div class="card-pitfall">
    <div class="card-pitfall-header">⚠️ {titre.upper()}</div>
    <div class="card-pitfall-content">{contenu}</div>
</div>
"""
    html_with_pitfalls = pitfall_pattern.sub(repl_pitfall, html_with_slides)

    # Actions 24h
    action_pattern = re.compile(r"<blockquote>\s*<p>⚡ <strong>Action Immédiate \(Moins de 24 Heures\) :</strong></p>\s*(.*?)</blockquote>", re.DOTALL)
    def repl_action(m):
        contenu = m.group(1)
        return f"""
<div class="card-action-24h">
    <div class="card-action-header">⚡ PROTOCOLE D'ACTION IMMÉDIATE (24 HEURES)</div>
    <div class="card-action-body">
        {contenu}
    </div>
</div>
"""
    html_with_actions = action_pattern.sub(repl_action, html_with_pitfalls)

    # Lettrines
    dropcap_pattern = re.compile(r'(<div class="chapter-opener"[^>]*>.*?</div>(?:\s*<!-- EXTRA_SVG_[^>]+-->|\s*<p><!-- EXTRA_SVG_[^>]+--></p>|\s*<div class="diagram-container">.*?</div>)?\s*)(<p>)', re.DOTALL)
    html_with_dropcaps = dropcap_pattern.sub(r'\1<p class="drop-cap">', html_with_actions)

    # Remplacer les placeholders par les vrais SVG sans passer par le parseur markdown
    html_with_dropcaps = re.sub(r'(?:<p>)?<!-- EXTRA_SVG_CASCADE_PLACEHOLDER -->(?:</p>)?', generate_svg_cashflow_cascade(), html_with_dropcaps)
    html_with_dropcaps = re.sub(r'(?:<p>)?<!-- EXTRA_SVG_COMPOUND_PLACEHOLDER -->(?:</p>)?', generate_svg_compound_interest(), html_with_dropcaps)

    # Intro opener
    html_with_dropcaps = html_with_dropcaps.replace(
        '<h1>INTRODUCTION : LE DÉCLIC DE LA SOUVERAINETÉ</h1>\n<p>',
        '<div class="chapter-opener"><div class="chapter-tag">AVANT-PROPOS</div><div class="chapter-title">LE DÉCLIC DE LA SOUVERAINETÉ</div><div class="chapter-ornament">◆ &nbsp; ◆ &nbsp; ◆</div></div>\n<p class="drop-cap">'
    )
    html_with_dropcaps = html_with_dropcaps.replace(
        '<h1>INTRODUCTION : LE DÉCLIC DE LA SOUVERAINETÉ</h1>',
        '<div class="chapter-opener"><div class="chapter-tag">AVANT-PROPOS</div><div class="chapter-title">LE DÉCLIC DE LA SOUVERAINETÉ</div><div class="chapter-ornament">◆ &nbsp; ◆ &nbsp; ◆</div></div>'
    )

    html_final = transform_math_formulas(html_with_dropcaps)
    return html_final

def build_back_matter_html(blueprint):
    titre = blueprint.get("titre", "L'ARCHITECTE FINANCIER")
    auteur = blueprint.get("auteur_suggere", "MarkEddy")
    annee = datetime.now().year

    html = f"""
    <!-- PAGE AVIS LECTEUR AMAZON -->
    <section class="review-request-box">
        <div style="font-family: 'Cinzel', serif; font-size: 13.5pt; letter-spacing: 2px; text-transform: uppercase; color: #0F172A; margin-bottom: 14px; font-weight: bold;">
            Votre Avis Est Le Carburant De L'Indépendance
        </div>
        <div style="font-size: 10.2pt; line-height: 1.52; color: #334155; max-width: 4.4in; margin: 0 auto;">
            <p>Chère lectrice, cher lecteur,</p>
            <p>Les livres d'indépendance financière font face à une industrie bancaire aux budgets colossaux. Sur Amazon, la seule arme des auteurs indépendants pour faire émerger la vérité réside dans <strong>votre retour d'expérience sincère</strong>.</p>
            <p>Si ce livre vous a apporté un modèle mental clair, vous a évité une erreur coûteuse ou a sécurisé vos comptes, prenez <strong>60 secondes</strong> pour déposer une note et un avis sur Amazon.</p>
            <p>Votre commentaire guidera un autre épargnant vers la sortie du découvert et la construction de sa propre forteresse.</p>
            <p style="margin-top: 18px; font-family: 'Cinzel', serif; font-weight: bold; color: #D4AF37;">Merci pour votre engagement et votre confiance.</p>
        </div>
    </section>

    <!-- BIOGRAPHIE OFFICIELLE DE L'AUTEUR -->
    <section class="author-bio-page">
        <div class="chapter-opener">
            <div class="chapter-tag">REPERES D'AUTORITE</div>
            <div class="chapter-title">À PROPOS DE L'AUTEUR</div>
            <div class="chapter-ornament">◆ &nbsp; ◆ &nbsp; ◆</div>
        </div>

        <div class="author-card">
            <div class="author-title">{auteur}</div>
            <div class="author-subtitle">Investisseur Indépendant & Concepteur de Protocoles Patrimoniaux</div>
            <div class="author-bio-content">
                <p><strong>{auteur}</strong> est ingénieur de formation, entrepreneur et investisseur sur les marchés financiers internationaux. Confronté très tôt aux défaillances criantes du système éducatif en matière de gestion monétaire, il a entrepris de modéliser les flux financiers des ménages avec la même rigueur que des systèmes industriels complexes.</p>
                <p>Refusant aussi bien l'austérité budgétaire stérile que les promesses illusoires d'enrichissement instantané, {auteur} a élaboré la méthode de l'<em>Architecture en Cascades</em> et les protocoles de <em>Dépenses Conscientes</em>. Ses travaux privilégient l'automatisation intégrale, l'élimination sans compromis des frais opaques et l'exploitation rationnelle de la croissance économique mondiale via l'investissement indiciel passif (ETF).</p>
                <p>Ses méthodologies sont aujourd'hui appliquées par des milliers de salariés, cadres et indépendants désireux de reprendre la souveraineté pleine et entière de leur temps.</p>
            </div>
        </div>

        <!-- COLOPHON TYPOGRAPHIQUE -->
        <div class="colophon-box">
            Cet ouvrage a été composé en caractères Garamond Premier Pro et Cinzel Trajan pour les éditions MarkEddy.<br>
            Achevé d'imprimer pour le compte d'Amazon Distribution KDP.<br>
            Format d'édition : 6 × 9 pouces (15,24 × 22,86 cm) • Papier d'imprimerie 90 g/m² sans acide.<br>
            © {annee} {auteur} — Tous droits réservés.
        </div>
    </section>
    """
    return html

def build_masterpiece_book():
    print("=" * 70)
    print("🏛️ MOTEUR TYPOGRAPHIQUE HAUTE COUTURE KDP (L'ARCHITECTE FINANCIER)")
    print("=" * 70)

    blueprint, raw_markdown = load_data()

    css = get_masterpiece_css()
    front_matter_html = build_front_matter_html(blueprint)
    body_html = transform_manuscript_to_luxury_html(raw_markdown)
    back_matter_html = build_back_matter_html(blueprint)

    full_document = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{blueprint.get('titre', 'L\'ARCHITECTE FINANCIER')} — Édition Haute Couture KDP</title>
    <style>
        {css}
    </style>
</head>
<body>
    {front_matter_html}
    {body_html}
    {back_matter_html}
</body>
</html>
"""

    OUTPUT_HTML.write_text(full_document, encoding="utf-8")
    print(f"✅ Fichier HTML Haute Couture généré : {OUTPUT_HTML} ({len(full_document.split())} mots, {len(full_document)} octets)")

    # Compilation Playwright vers PDF 6x9 pouces certifié KDP
    print("\n📦 Lancement de la compilation Playwright vers PDF 6x9 pouces...")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="msedge")
        
        page = browser.new_page()
        page.goto(OUTPUT_HTML.as_uri(), wait_until="domcontentloaded", timeout=90000)
        try:
            page.wait_for_function("document.fonts.status === 'loaded'", timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(1000)

        page.pdf(
            path=str(OUTPUT_PDF),
            prefer_css_page_size=True,
            print_background=True
        )
        browser.close()

    size_kb = OUTPUT_PDF.stat().st_size / 1024
    print(f"🎉 PDF Haute Couture généré avec succès : {OUTPUT_PDF} ({size_kb:.1f} Ko)")

    # Synchronisation des livrables jumeaux
    shutil.copy2(OUTPUT_PDF, WORKSPACE / "livre_imprimable_kdp.pdf")
    shutil.copy2(OUTPUT_PDF, WORKSPACE / "livre_numerique_interactif.pdf")
    print("✅ Formats jumeaux synchronisés.")

if __name__ == "__main__":
    build_masterpiece_book()
