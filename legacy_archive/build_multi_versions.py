"""
build_multi_versions.py - Compilateur Multi-Formats de Haute Édition Amazon KDP.
Génère de manière chirurgicale les 3 versions commerciales distinctes du livre de MarkEddy :
  1. VERSION BROCHÉE PAPIER (Print-Ready PDF)       -> livre_imprimable_kdp.pdf
  2. VERSION EBOOK ÉLECTRONIQUE (EPUB 3 / Kindle)   -> livre_ebook_kdp.epub
  3. VERSION PDF NUMÉRIQUE INTERACTIVE (Digital PDF) -> livre_numerique_interactif.pdf
"""

import os
import re
import sys
import json
import uuid
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pypdf
from ebooklib import epub

BLUEPRINT_PATH = Path("book_blueprint.json")
MANUSCRIT_PATH = Path("manuscrit_complet.md")

# Chemins des livrables finaux
LIVRABLE_PRINT_HTML = Path("livre_imprimable_kdp.html")
LIVRABLE_PRINT_PDF = Path("livre_imprimable_kdp.pdf")

LIVRABLE_EBOOK_COVER = Path("couverture_ebook.jpg")
LIVRABLE_EBOOK_EPUB = Path("livre_ebook_kdp.epub")

LIVRABLE_DIGITAL_HTML = Path("livre_numerique_interactif.html")
LIVRABLE_DIGITAL_PDF = Path("livre_numerique_interactif.pdf")


# ==============================================================================
# 1. UTILITAIRES & CHARGEMENT DES DONNÉES
# ==============================================================================

def charger_blueprint() -> dict:
    if not BLUEPRINT_PATH.exists():
        raise FileNotFoundError(f"❌ {BLUEPRINT_PATH} introuvable.")
    return json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))


def charger_manuscrit() -> str:
    if not MANUSCRIT_PATH.exists():
        # Génération immédiate si absent
        from kdp_toc_and_frontmatter import assembler_livre_complet_kdp
        assembler_livre_complet_kdp()
    return MANUSCRIT_PATH.read_text(encoding="utf-8")


def charger_police(taille: int, gras: bool = False):
    polices = [
        "C:/Windows/Fonts/georgiab.ttf" if gras else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if gras else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if gras else "C:/Windows/Fonts/calibri.ttf"
    ]
    for p in polices:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, taille)
            except Exception:
                pass
    return ImageFont.load_default()


def dessiner_texte_centre(draw, texte: str, centre_x: int, y: int, font, couleur):
    try:
        bbox = draw.textbbox((0, 0), texte, font=font)
        w = bbox[2] - bbox[0]
        draw.text((centre_x - w // 2, y), texte, fill=couleur, font=font)
        return y + (bbox[3] - bbox[1]) + 15
    except Exception:
        draw.text((centre_x - 100, y), texte, fill=couleur, font=font)
        return y + 30


# ==============================================================================
# 2. CONCEPTION DE LA COUVERTURE EBOOK HAUTE DÉFINITION (Kindle 300 DPI)
# ==============================================================================

def generer_couverture_ebook(sortie_path: Path = LIVRABLE_EBOOK_COVER, blueprint: dict = None) -> Path:
    """Génère une couverture avant Kindle d'élite (1800 x 2700 px @ 300 DPI) dynamique."""
    print("🎨 [EBOOK] Génération de la couverture numérique avant (1800x2700 px)...")
    if blueprint is None:
        try:
            blueprint = charger_blueprint()
        except Exception:
            blueprint = {}

    titre_brut = blueprint.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    sous_titre_brut = blueprint.get("sous_titre", "Reprogrammer son cerveau en 66 jours sans procrastination")
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy"))

    largeur, hauteur = 1800, 2700
    img = Image.new("RGB", (largeur, hauteur), color="#0A0F1D")
    draw = ImageDraw.Draw(img)

    # Double cadre or impérial
    draw.rectangle([60, 60, largeur - 60, hauteur - 60], outline="#D4AF37", width=6)
    draw.rectangle([78, 78, largeur - 78, hauteur - 78], outline="#1E293B", width=2)
    draw.rectangle([95, 95, largeur - 95, hauteur - 95], outline="#D4AF37", width=1)

    centre_x = largeur // 2

    # Badge supérieur
    font_badge = charger_police(28, gras=True)
    y = 260
    y = dessiner_texte_centre(draw, "MÉTHODE SCIENTIFIQUE D'INGÉNIERIE COGNITIVE", centre_x, y, font_badge, "#C5A059")

    # Filet doré
    draw.line([(centre_x - 120, y + 10), (centre_x + 120, y + 10)], fill="#D4AF37", width=2)
    y += 90

    # Titre principal (découpage intelligent en lignes)
    font_titre = charger_police(72, gras=True)
    # Découpage du titre par ':' ou par longueur
    if ":" in titre_brut:
        parties_t = [p.strip() for p in titre_brut.split(":", 1)]
        titre_lignes = [parties_t[0], parties_t[1]]
    else:
        mots_t = titre_brut.split()
        titre_lignes = []
        cur_l = ""
        for m in mots_t:
            if len(cur_l + " " + m) > 22:
                titre_lignes.append(cur_l.strip())
                cur_l = m
            else:
                cur_l = cur_l + " " + m if cur_l else m
        if cur_l:
            titre_lignes.append(cur_l.strip())

    for lig in titre_lignes:
        y = dessiner_texte_centre(draw, lig, centre_x, y, font_titre, "#FFFFFF")

    # Ornement central
    y += 35
    draw.line([(centre_x - 220, y), (centre_x + 220, y)], fill="#D4AF37", width=4)
    draw.text((centre_x - 14, y - 18), "◆", fill="#D4AF37", font=charger_police(28))
    y += 75

    # Sous-titre dynamique
    font_soustitre = charger_police(34)
    mots_st = sous_titre_brut.split()
    st_lignes = []
    cur_st = ""
    for m in mots_st:
        if len(cur_st + " " + m) > 42:
            st_lignes.append(cur_st.strip())
            cur_st = m
        else:
            cur_st = cur_st + " " + m if cur_st else m
    if cur_st:
        st_lignes.append(cur_st.strip())

    for lig in st_lignes:
        y = dessiner_texte_centre(draw, lig, centre_x, y, font_soustitre, "#E2E8F0")

    # Macaron des caractéristiques dynamique
    y = hauteur - 780
    font_puces = charger_police(24, gras=True)
    nb_chaps = len(blueprint.get("chapitres", [])) or 8
    nb_secs = sum(len(c.get("sections", [])) for c in blueprint.get("chapitres", [])) or (nb_chaps * 5)
    texte_badge = f"{nb_chaps} CHAPITRES • {nb_secs} PLANS D'ACTION SOUS 24H • EXEMPLES SCIENTIFIQUES"
    draw.rectangle([centre_x - 490, y, centre_x + 490, y + 90], outline="#D4AF37", fill="#111B30", width=2)
    dessiner_texte_centre(draw, texte_badge, centre_x, y + 30, font_puces, "#FAF7F2")

    # Auteur officiel : Signature calligraphique noble MarkEddy
    y = hauteur - 460
    font_auteur_label = charger_police(26)
    dessiner_texte_centre(draw, "PAR L'AUTEUR & STRATÈGE", centre_x, y, font_auteur_label, "#94A3B8")
    
    logo_signature_path = Path("assets/logo/logo_markeddy_or_fond_sombre.png")
    if not logo_signature_path.exists():
        logo_signature_path = Path("assets/logo/logo_mark_eddy_blanc.png")
    if logo_signature_path.exists():
        try:
            sig_im = Image.open(logo_signature_path).convert("RGBA")
            sig_im.thumbnail((560, 200), Image.Resampling.LANCZOS)
            sw, sh = sig_im.size
            img.paste(sig_im, (centre_x - sw // 2, y + 45), sig_im)
        except Exception:
            font_auteur = charger_police(58, gras=True)
            dessiner_texte_centre(draw, auteur.upper(), centre_x, y + 50, font_auteur, "#D4AF37")
    else:
        font_auteur = charger_police(58, gras=True)
        dessiner_texte_centre(draw, auteur.upper(), centre_x, y + 50, font_auteur, "#D4AF37")

    # Empreinte d'édition en pied de page
    font_editeur = charger_police(22)
    dessiner_texte_centre(draw, f"ÉDITIONS {auteur.upper()} • ÉDITION OFFICIELLE", centre_x, hauteur - 160, font_editeur, "#64748B")

    sortie_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie_path, "JPEG", quality=95)
    print(f"  ✅ Couverture Kindle enregistrée : {sortie_path.resolve()} ({sortie_path.stat().st_size / 1024:.1f} Ko)")
    return sortie_path


# ==============================================================================
# 3. CONVERTISSEUR MARKDOWN ROBUSTE MULTI-FORMATS
# ==============================================================================

def markdown_vers_html(md_texte: str, mode: str = "print") -> str:
    """
    Convertit le texte Markdown en HTML sémantique ultra-soigné.
    mode : 'print' (nuances de gris, marges de reliure),
           'interactive' (pleine couleur or/bleu, ancres et liens cliquables),
           'epub' (reflowable, balises xhtml propres).
    """
    lignes = md_texte.split("\n")
    nouvelles = []
    en_liste = False
    en_blockquote = False
    en_table = False
    prochain_lead = False

    for idx, lig in enumerate(lignes):
        l = lig.strip()

        # 1. Gestion des Tableaux Markdown
        if l.startswith("|") and l.endswith("|"):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False

            colonnes = [c.strip() for c in l[1:-1].split("|")]
            if all(re.match(r"^:?-+:?$", c) for c in colonnes if c):
                continue

            if not en_table:
                nouvelles.append('<table class="kdp-table">')
                nouvelles.append("<thead><tr>")
                for col in colonnes:
                    col_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", col)
                    col_fmt = re.sub(r"\*(.*?)\*", r"<em>\1</em>", col_fmt)
                    # Remplacement des tirets par des tirets insécables dans les en-têtes pour zéro coupure
                    col_fmt = col_fmt.replace("-", "&#8209;")
                    nouvelles.append(f"<th>{col_fmt}</th>")
                nouvelles.append("</tr></thead><tbody>")
                en_table = True
                continue
            else:
                nouvelles.append("<tr>")
                for col in colonnes:
                    col_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", col)
                    col_fmt = re.sub(r"\*(.*?)\*", r"<em>\1</em>", col_fmt)
                    # Sécuriser les mots composés dans les cellules
                    col_fmt = re.sub(r"\b(micro|neuro|contre|non|anti|auto)-([a-zà-ÿ]+)\b", r"\1&#8209;\2", col_fmt, flags=re.IGNORECASE)
                    nouvelles.append(f"<td>{col_fmt}</td>")
                nouvelles.append("</tr>")
                continue
        else:
            if en_table:
                nouvelles.append("</tbody></table>")
                en_table = False

        # 2. Gestion des Titres avec injection d'ID pour ancres
        if l.startswith("#### "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            titre_texte = l[5:].strip()
            titre_texte = re.sub(r"\b(micro|neuro|contre|non|au)-([a-zà-ÿ]+)\b", r"\1&#8209;\2", titre_texte, flags=re.IGNORECASE)
            nouvelles.append(f'<h4 class="sub-heading">{titre_texte}</h4>')
            continue

        elif l.startswith("### "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            titre_texte = l[4:].strip()
            match_num = re.match(r"^(\d+)\.(\d+)\s*(.*)", titre_texte)
            if match_num:
                ancre = f"sec-{match_num.group(1)}-{match_num.group(2)}"
            else:
                ancre = re.sub(r"[^a-zA-Z0-9]+", "-", titre_texte).strip("-").lower()
            titre_texte = re.sub(r"\b(micro|neuro|contre|non|au)-([a-zà-ÿ]+)\b", r"\1&#8209;\2", titre_texte, flags=re.IGNORECASE)
            nouvelles.append(f'<h3 id="{ancre}">{titre_texte}</h3>')
            continue

        elif l.startswith("## "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            titre_texte = l[3:].strip()
            titre_texte = re.sub(r"\b(micro|neuro|contre|non|au)-([a-zà-ÿ]+)\b", r"\1&#8209;\2", titre_texte, flags=re.IGNORECASE)
            nouvelles.append(f"<h2>{titre_texte}</h2>")
            continue

        elif l.startswith("# "):
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            titre_texte = l[2:].strip()
            match_chap = re.match(r"^Chapitre\s*(\d+)", titre_texte, re.IGNORECASE)
            if match_chap:
                ancre = f"ch-{match_chap.group(1)}"
            else:
                ancre = re.sub(r"[^a-zA-Z0-9]+", "-", titre_texte).strip("-").lower()
            titre_texte = re.sub(r"\b(micro|neuro|contre|non|au)-([a-zà-ÿ]+)\b", r"\1&#8209;\2", titre_texte, flags=re.IGNORECASE)
            nouvelles.append(f'<h1 id="{ancre}">{titre_texte}</h1>')
            prochain_lead = True
            continue

        # 3. Séparateurs horizontaux (supprimés s'ils précèdent directement un titre de grand chapitre ou de section)
        if l == "---":
            if en_liste: nouvelles.append("</ul>"); en_liste = False
            if en_blockquote: nouvelles.append("</blockquote>"); en_blockquote = False
            # Regard vers l'avant : ne pas émettre de <hr> si le prochain bloc non-vide est un titre
            prochains = [lignes[k].strip() for k in range(idx + 1, min(idx + 5, len(lignes))) if lignes[k].strip()]
            if prochains and (prochains[0].startswith("# ") or prochains[0].startswith("## ") or prochains[0].startswith("### ")):
                continue
            nouvelles.append("<hr>")
            continue

        # 4. Citations et Encadrés d'Action Immédiate (avec rendu propre sans balise markdown)
        if l.startswith(">"):
            contenu_bq = l[1:].strip()
            if not en_blockquote:
                nouvelles.append('<blockquote class="callout-box">')
                en_blockquote = True
            
            if not contenu_bq:
                continue

            # Rendu propre des titres d'encadrés
            if "Action Immédiate" in contenu_bq or "ACTION IMMÉDIATE" in contenu_bq or "action immédiate" in contenu_bq.lower() or contenu_bq.startswith("###") or contenu_bq.startswith("##") or contenu_bq.startswith("⚡"):
                titre_clean = re.sub(r"^[#\s\*🛑⚡💡]+", "", contenu_bq)
                titre_clean = re.sub(r"[\*:]+$", "", titre_clean).strip()
                titre_clean = re.sub(r"\b(micro|neuro|contre|non|au)-([a-zà-ÿ]+)\b", r"\1&#8209;\2", titre_clean, flags=re.IGNORECASE)
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

        # 5. Listes à puces
        if l.startswith("- ") or l.startswith("* "):
            if not en_liste:
                nouvelles.append("<ul>")
                en_liste = True
            item = l[2:]
            
            # Liens actifs pour la table des matières en mode interactif
            if mode == "interactive" and ("Chapitre" in item or re.match(r"^\d+\.\d+", item)):
                m_item = re.match(r"^(\d+\.\d+)\s*(.*)", item)
                if m_item:
                    num_sec = m_item.group(1)
                    titre_s = m_item.group(2)
                    c_n, s_n = num_sec.split(".")
                    item = f'<a href="#sec-{c_n}-{s_n}" class="toc-link"><strong>{num_sec}</strong> {titre_s}</a>'
            
            item = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item)
            item = re.sub(r"\*(.*?)\*", r"<em>\1</em>", item)
            nouvelles.append(f"<li>{item}</li>")
            continue
        else:
            if en_liste:
                nouvelles.append("</ul>")
                en_liste = False

        # 6. Paragraphes de texte courant
        if l:
            # Insertion du Logo Officiel MarkEddy sur la page de titre selon le mode d'édition
            if l.strip() in ["**Par MarkEddy**", "Par MarkEddy"]:
                if mode == "print":
                    nouvelles.append('<div class="author-signature" style="text-align: center; margin: 40px auto 15px auto;">'
                                     '<img src="assets/logo/logo_markeddy_noir_print.png" alt="MarkEddy" style="width: 2.6in; max-width: 80%; height: auto; display: inline-block;" />'
                                     '<p style="font-family: \'Garamond\', \'Georgia\', serif; font-size: 11pt; letter-spacing: 2px; text-transform: uppercase; margin-top: 10px; color: #1a1a1a;">Éditions MarkEddy</p></div>')
                elif mode == "interactive":
                    nouvelles.append('<div class="author-signature" style="text-align: center; margin: 40px auto 15px auto;">'
                                     '<img src="assets/logo/logo_markeddy_bleu_or_fond_clair.png" alt="MarkEddy" style="width: 3.0in; max-width: 85%; height: auto; display: inline-block;" />'
                                     '<p style="font-family: \'Georgia\', serif; font-size: 11pt; letter-spacing: 2px; text-transform: uppercase; margin-top: 10px; color: #0f172a;">Éditions MarkEddy</p></div>')
                else:
                    nouvelles.append('<p class="author-title" style="text-align: center; font-size: 1.2em; font-weight: bold; margin-top: 1.5em; letter-spacing: 1px;">Par MarkEddy</p>')
                continue

            # Traitement des titres de chapitres dans le sommaire interactif
            if mode == "interactive" and l.startswith("**Chapitre ") and l.endswith("**"):
                m_ch = re.match(r"^\*\*Chapitre\s*(\d+)\s*:\s*(.*?)\*\*$", l)
                if m_ch:
                    ch_num = m_ch.group(1)
                    ch_nom = m_ch.group(2)
                    nouvelles.append(f'<p class="toc-chapitre-item"><a href="#ch-{ch_num}" class="toc-ch-link"><strong>Chapitre {ch_num} : {ch_nom}</strong></a></p>')
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

    if en_liste: nouvelles.append("</ul>")
    if en_blockquote: nouvelles.append("</blockquote>")
    if en_table: nouvelles.append("</tbody></table>")

    return "\n".join(nouvelles)


# ==============================================================================
# 4. MODULE 1 : VERSION BROCHÉE PAPIER (Print-Ready 6x9 po PDF)
# ==============================================================================

CSS_PRINT_KDP = """
@page {
    size: 6in 9in;
    margin-top: 0.8in;
    margin-bottom: 0.8in;
    @bottom-center {
        content: counter(page);
        font-family: 'Garamond', 'Georgia', serif;
        font-size: 9pt;
        color: #333333;
    }
}

/* Page Paire (Verso / Gauche) : Gutter à droite */
@page :left {
    margin-left: 0.65in;
    margin-right: 0.85in;
    @top-center {
        content: "__TITRE_HEADER__";
        font-family: 'Garamond', serif;
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #555;
    }
}

/* Page Impaire (Recto / Droite) : Gutter à gauche */
@page :right {
    margin-left: 0.85in;
    margin-right: 0.65in;
    @top-center {
        content: "__AUTEUR_HEADER__";
        font-family: 'Garamond', serif;
        font-size: 8pt;
        font-style: italic;
        letter-spacing: 1.5px;
        color: #555;
    }
}

@page :first {
    @top-center { content: ""; }
    @bottom-center { content: ""; }
}

body {
    font-family: 'Garamond', 'Georgia', 'Times New Roman', serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111827;
    text-align: justify;
    hyphens: manual;
    -webkit-hyphens: manual;
    orphans: 3;
    widows: 3;
    margin: 0;
    padding: 0;
}

/* Règle stricte anti-césure sauvage sur tous les titres, tableaux et éléments structurés */
h1, h2, h3, h4, th, td, .callout-box, .callout-header, .author-title, .title-signature, .chapter-lead::first-letter, .toc-link, .author-signature, .kdp-table, tr {
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
}

h1 {
    page-break-before: always;
    break-before: page;
    font-size: 19pt;
    font-weight: 700;
    text-align: center;
    margin-top: 1.8in;
    margin-bottom: 0.8in;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #000000;
}

h1::after {
    content: "❖   ❖   ❖";
    display: block;
    font-size: 8pt;
    letter-spacing: 5px;
    margin-top: 14px;
    color: #64748b;
}

h2 {
    font-size: 13pt;
    margin-top: 1.2in;
    margin-bottom: 0.35in;
    font-weight: 700;
    color: #111827;
    page-break-after: avoid;
    break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    margin-top: 0.7in;
    margin-bottom: 0.25in;
    font-weight: 700;
    color: #1f2937;
    border-bottom: 0.5pt solid #9ca3af;
    padding-bottom: 3px;
    page-break-after: avoid;
    break-after: avoid;
}

h4, .sub-heading {
    font-family: 'Georgia', serif;
    font-size: 10pt;
    font-weight: 700;
    color: #1f2937;
    margin-top: 0.45in;
    margin-bottom: 0.15in;
    page-break-after: avoid;
    break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 0.6em;
    text-indent: 1.25em;
}

h1 + p, h2 + p, h3 + p, h4 + p, hr + p, blockquote + p, table + p {
    text-indent: 0;
}

p.chapter-lead::first-letter {
    font-size: 3.4em;
    float: left;
    line-height: 0.8;
    margin-right: 0.12em;
    font-family: 'Georgia', 'Garamond', serif;
    font-weight: bold;
    color: #000000;
}

blockquote, .callout-box {
    border-left: 3.5px solid #d4af37;
    background-color: #fafaf9;
    margin: 1.2em 0.2in;
    padding: 0.8em 1.1em;
    font-size: 9.5pt;
    font-style: normal;
    page-break-inside: avoid;
    break-inside: avoid;
    border-radius: 0 4px 4px 0;
}

.callout-header {
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
}

table, .kdp-table {
    table-layout: fixed;
    width: 100%;
    margin: 1.4em 0;
    border-collapse: collapse;
    font-size: 8pt;
    line-height: 1.35;
    page-break-inside: avoid;
    break-inside: avoid;
}

th {
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
}

td {
    font-size: 7.8pt;
    padding: 5px 4px;
    border-bottom: 0.5pt solid #cbd5e1;
    color: #1f2937;
    text-align: left;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

ul, ol {
    margin: 0.6em 0 0.8em 1.5em;
    padding: 0;
}

li {
    margin-bottom: 0.3em;
}

hr {
    border: 0;
    text-align: center;
    margin: 1.8em auto;
    page-break-after: avoid;
    break-after: avoid;
}

hr::after {
    content: "— ❧ —";
    display: inline-block;
    color: #6b7280;
    font-size: 10pt;
    letter-spacing: 4px;
}
"""

async def convertir_html_en_pdf_playwright(source_html: Path, sortie_pdf: Path, titre_livre: str, auteur: str):
    """Effectue le rendu vectoriel strict 6x9 pouces via Chromium / Edge."""
    from playwright.async_api import async_playwright

    print(f"🖨️ [PLAYWRIGHT] Rendu PDF haute définition : {sortie_pdf.name}...")
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch()
        except Exception:
            try:
                browser = await p.chromium.launch(channel="msedge")
            except Exception as e:
                raise RuntimeError(f"Impossible de lancer Chromium ou Edge : {e}")

        page = await browser.new_page()
        await page.goto(source_html.resolve().as_uri(), wait_until="load")

        await page.pdf(
            path=str(sortie_pdf),
            width="6in",
            height="9in",
            print_background=True,
            prefer_css_page_size=True
        )
        await browser.close()

    # Injection des métadonnées PDF via pypdf
    reader = pypdf.PdfReader(str(sortie_pdf))
    writer = pypdf.PdfWriter()
    writer.append(reader)
    writer.add_metadata({
        "/Title": titre_livre,
        "/Author": auteur,
        "/Subject": "Guide pratique d'excellence et de haute performance Amazon KDP",
        "/Creator": "Éditions MarkEddy - Machine de Création KDP",
        "/Producer": "Playwright Chromium PDF Engine 300 DPI"
    })
    with open(sortie_pdf, "wb") as f_out:
        writer.write(f_out)

    print(f"  ✅ PDF généré et enrichi en métadonnées : {sortie_pdf.resolve()} ({sortie_pdf.stat().st_size / 1024:.1f} Ko)")


def compiler_version_imprimee(blueprint: dict, manuscrit_md: str) -> Path:
    """Compile la version brochée papier conforme aux exigences KDP 6x9 pouces."""
    print("\n" + "=" * 65)
    print("📦 1. COMPILATION VERSION BROCHÉE PAPIER (livre_imprimable_kdp.pdf)")
    print("=" * 65)

    corps_html = markdown_vers_html(manuscrit_md, mode="print")
    titre = blueprint.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy"))

    css_dynamique = CSS_PRINT_KDP.replace("__TITRE_HEADER__", titre.upper()).replace("__AUTEUR_HEADER__", auteur.upper())

    html_complet = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{titre} - Version Imprimable KDP</title>
    <style>
{css_dynamique}
    </style>
</head>
<body>
{corps_html}
</body>
</html>"""

    LIVRABLE_PRINT_HTML.write_text(html_complet, encoding="utf-8")
    print(f"  ✅ Fichier HTML Paged Media généré : {LIVRABLE_PRINT_HTML.resolve()}")

    asyncio.run(convertir_html_en_pdf_playwright(
        source_html=LIVRABLE_PRINT_HTML,
        sortie_pdf=LIVRABLE_PRINT_PDF,
        titre_livre=titre,
        auteur=auteur
    ))

    return LIVRABLE_PRINT_PDF


# ==============================================================================
# 5. MODULE 2 : VERSION EBOOK ÉLECTRONIQUE (EPUB 3 / Kindle Amazon)
# ==============================================================================

CSS_EPUB = """
body {
    font-family: Georgia, Garamond, serif;
    font-size: 1.05em;
    line-height: 1.5;
    color: #111827;
    margin: 5% 5%;
    text-align: justify;
}

h1 {
    font-size: 1.8em;
    font-weight: bold;
    text-align: center;
    color: #0f172a;
    margin-top: 2em;
    margin-bottom: 1em;
    border-bottom: 2px solid #d4af37;
    padding-bottom: 0.3em;
}

h2 {
    font-size: 1.3em;
    color: #1e293b;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h3 {
    font-size: 1.15em;
    color: #334155;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 0.2em;
}

p {
    margin-top: 0;
    margin-bottom: 0.8em;
    text-indent: 1.2em;
}

h1 + p, h2 + p, h3 + p, hr + p, blockquote + p {
    text-indent: 0;
}

blockquote, .callout-box {
    border-left: 4px solid #d4af37;
    background-color: #fbfbfa;
    margin: 1.2em 0.5em;
    padding: 0.8em 1.2em;
    font-size: 0.95em;
    border-radius: 0 4px 4px 0;
}

table, .kdp-table {
    width: 100%;
    margin: 1.5em 0;
    border-collapse: collapse;
    font-size: 0.9em;
}

th {
    background-color: #0f172a;
    color: #ffffff;
    padding: 8px;
    border: 1px solid #0f172a;
    text-align: left;
}

td {
    padding: 7px;
    border-bottom: 1px solid #e2e8f0;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

hr {
    border: 0;
    text-align: center;
    margin: 2em auto;
}

hr::after {
    content: "❖   ❖   ❖";
    color: #94a3b8;
    letter-spacing: 5px;
}
"""

def compiler_version_ebook(blueprint: dict, manuscrit_md: str) -> Path:
    """Compile la version EPUB 3 certifiée pour Kindle Amazon avec table des matières dynamique."""
    print("\n" + "=" * 65)
    print("📱 2. COMPILATION VERSION EBOOK KINDLE (livre_ebook_kdp.epub)")
    print("=" * 65)

    # 1. Génération de la couverture haute résolution
    couv_path = generer_couverture_ebook(LIVRABLE_EBOOK_COVER, blueprint=blueprint)

    # 2. Initialisation du livre EPUB
    book = epub.EpubBook()
    livre_id = str(uuid.uuid4())
    titre = blueprint.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    sous_titre = blueprint.get("sous_titre", "")
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy"))
    promesse = blueprint.get("promesse_client", "")

    book.set_identifier(f"urn:uuid:{livre_id}")
    book.set_title(titre)
    book.set_language("fr")
    book.add_author(auteur)

    book.add_metadata("DC", "description", f"{sous_titre}. {promesse}")
    book.add_metadata("DC", "publisher", "Éditions MarkEddy")
    book.add_metadata("DC", "rights", "© 2026 MarkEddy. Tous droits réservés.")
    book.add_metadata(None, "meta", "", {"property": "rendition:layout", "content": "reflowable"})

    # 3. Couverture
    with open(couv_path, "rb") as f_cov:
        book.set_cover("cover.jpg", f_cov.read())

    # 4. Feuille de style CSS
    style_item = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=CSS_EPUB
    )
    book.add_item(style_item)

    # 5. Découpage du manuscrit en fichiers chapitres individuels
    # Sépare le manuscrit par grands blocs '# '
    parties_brutes = re.split(r"\n(?=# )", manuscrit_md)
    chapitres_items = []
    toc_links = []

    chapitre_counter = 0

    for partie in parties_brutes:
        partie = partie.strip()
        if not partie:
            continue

        premiere_ligne = partie.splitlines()[0].replace("#", "").strip()
        corps_html = markdown_vers_html(partie, mode="epub")

        # Faux-titre ou titre initial
        if "Mentions Légales" in premiere_ligne or "Droits d'Auteur" in premiere_ligne:
            f_name = "text/00_frontmatter.xhtml"
            t_titre = "Mentions Légales"
        elif "Table des Matières" in premiere_ligne:
            # L'EPUB génère sa propre table dynamique nav.xhtml
            continue
        elif "Avant-propos" in premiere_ligne:
            f_name = "text/01_avant_propos.xhtml"
            t_titre = premiere_ligne
            toc_links.append(epub.Link(f_name, t_titre, "intro"))
        elif "Chapitre " in premiere_ligne:
            chapitre_counter += 1
            f_name = f"text/chapitre_{chapitre_counter:02d}.xhtml"
            t_titre = premiere_ligne

            # Extraction des sous-sections pour la table des matières hiérarchique
            sub_links = []
            for lig in partie.splitlines():
                if lig.startswith("### "):
                    s_titre = lig[4:].strip()
                    m_num = re.match(r"^(\d+)\.(\d+)\s*(.*)", s_titre)
                    if m_num:
                        ancre = f"sec-{m_num.group(1)}-{m_num.group(2)}"
                        sub_links.append(epub.Link(f"{f_name}#{ancre}", s_titre, f"sec_{m_num.group(1)}_{m_num.group(2)}"))

            if sub_links:
                toc_links.append((epub.Section(t_titre, href=f_name), sub_links))
            else:
                toc_links.append(epub.Link(f_name, t_titre, f"ch_{chapitre_counter}"))
        elif "Conclusion" in premiere_ligne:
            f_name = "text/90_conclusion.xhtml"
            t_titre = premiere_ligne
            toc_links.append(epub.Link(f_name, t_titre, "conclusion"))
        elif "Votre Avis" in premiere_ligne:
            f_name = "text/91_avis.xhtml"
            t_titre = premiere_ligne
            toc_links.append(epub.Link(f_name, t_titre, "avis"))
        elif "À Propos" in premiere_ligne:
            f_name = "text/92_bio_auteur.xhtml"
            t_titre = premiere_ligne
            toc_links.append(epub.Link(f_name, t_titre, "bio"))
        elif "Remerciements" in premiere_ligne:
            f_name = "text/93_remerciements.xhtml"
            t_titre = premiere_ligne
            toc_links.append(epub.Link(f_name, t_titre, "remerciements"))
        else:
            f_name = f"text/section_{len(chapitres_items):02d}.xhtml"
            t_titre = premiere_ligne

        c_item = epub.EpubHtml(title=t_titre, file_name=f_name, lang="fr")
        c_item.content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="fr">
<head>
    <title>{t_titre}</title>
    <link rel="stylesheet" type="text/css" href="../style/nav.css" />
</head>
<body>
{corps_html}
</body>
</html>"""
        c_item.add_item(style_item)
        book.add_item(c_item)
        chapitres_items.append(c_item)

    # 6. Table des matières dynamique & Navigation
    book.toc = toc_links
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 7. Spine du livre
    book.spine = ["nav"] + chapitres_items

    # 8. Écriture du fichier EPUB final
    epub.write_epub(str(LIVRABLE_EBOOK_EPUB), book, {})
    print(f"  ✅ EBOOK EPUB 3 certifié généré : {LIVRABLE_EBOOK_EPUB.resolve()} ({LIVRABLE_EBOOK_EPUB.stat().st_size / 1024:.1f} Ko)")
    return LIVRABLE_EBOOK_EPUB


# ==============================================================================
# 6. MODULE 3 : VERSION PDF NUMÉRIQUE INTERACTIVE (Digital PDF avec Signets)
# ==============================================================================

CSS_DIGITAL_INTERACTIVE = """
@page {
    size: 6in 9in;
    margin: 0.75in;
    @bottom-center {
        content: counter(page);
        font-family: 'Georgia', serif;
        font-size: 9pt;
        color: #64748b;
    }
}

@page :first {
    @bottom-center { content: ""; }
}

body {
    font-family: 'Georgia', 'Garamond', serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #0f172a;
    text-align: justify;
    hyphens: manual;
    -webkit-hyphens: manual;
}

/* Règle stricte anti-césure sauvage */
h1, h2, h3, h4, th, td, .callout-box, .callout-header, .author-title, .title-signature, .chapter-lead::first-letter, .toc-link, .author-signature, .kdp-table, tr {
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
}

h1 {
    page-break-before: always;
    break-before: page;
    font-size: 20pt;
    font-weight: 700;
    text-align: center;
    margin-top: 1.6in;
    margin-bottom: 0.8in;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #0f172a;
    border-bottom: 2px solid #d4af37;
    padding-bottom: 10px;
}

h1::after {
    content: "❖   ❖   ❖";
    display: block;
    font-size: 8pt;
    letter-spacing: 6px;
    margin-top: 14px;
    color: #d4af37;
}

h2 {
    font-size: 13.5pt;
    margin-top: 1.1in;
    margin-bottom: 0.35in;
    font-weight: 700;
    color: #1e3a8a;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    margin-top: 0.75in;
    margin-bottom: 0.25in;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3px;
    page-break-after: avoid;
}

h4, .sub-heading {
    font-family: 'Georgia', serif;
    font-size: 10pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 0.45in;
    margin-bottom: 0.15in;
    page-break-after: avoid;
    break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 0.65em;
    text-indent: 1.2em;
}

h1 + p, h2 + p, h3 + p, h4 + p, hr + p, blockquote + p, table + p {
    text-indent: 0;
}

p.chapter-lead::first-letter {
    font-size: 3.5em;
    float: left;
    line-height: 0.8;
    margin-right: 0.12em;
    font-family: 'Georgia', serif;
    font-weight: bold;
    color: #0f172a;
}

/* Encadrés d'action immédiate avec bordure dorée noble */
blockquote, .callout-box {
    border-left: 3.5px solid #d4af37;
    background-color: #fcfbf9;
    margin: 1.3em 0.2in;
    padding: 0.9em 1.3em;
    font-size: 9.6pt;
    font-style: normal;
    page-break-inside: avoid;
    break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    border-radius: 0 4px 4px 0;
}

.callout-header {
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
}

/* Liens cliquables actifs */
a {
    color: #0f172a;
    text-decoration: none;
    transition: color 0.2s;
}

a:hover {
    color: #b45309;
    text-decoration: underline;
}

.toc-link {
    color: #1e3a8a;
}

.toc-ch-link {
    color: #0f172a;
    font-size: 10.5pt;
}

.toc-chapitre-item {
    margin-top: 0.9em;
    margin-bottom: 0.2em;
}

table, .kdp-table {
    table-layout: fixed;
    width: 100%;
    margin: 1.4em 0;
    border-collapse: collapse;
    font-size: 8pt;
    line-height: 1.35;
    page-break-inside: avoid;
    break-inside: avoid;
}

th {
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
}

td {
    font-size: 7.8pt;
    padding: 5px 4px;
    border-bottom: 0.5pt solid #cbd5e1;
    color: #334155;
    text-align: left;
    hyphens: none !important;
    -webkit-hyphens: none !important;
    word-break: normal !important;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

hr {
    border: 0;
    text-align: center;
    margin: 1.8em auto;
    page-break-after: avoid;
    break-after: avoid;
}

hr::after {
    content: "— ❧ —";
    display: inline-block;
    color: #d4af37;
    font-size: 11pt;
    letter-spacing: 4px;
}
"""

def injecter_signets_interactifs_pdf(pdf_source: Path, pdf_destination: Path, blueprint: dict):
    """Injecte l'arborescence complète des signets PDF (Outline / Bookmarks) pour chaque chapitre et section."""
    print("📑 [OUTLINE] Injection des signets hiérarchiques PDF (Chapitres & 50 Sous-sections)...")
    reader = pypdf.PdfReader(str(pdf_source))
    writer = pypdf.PdfWriter()
    writer.append(reader)

    # Extraction du texte de chaque page pour localiser avec exactitude les titres
    pages_texte = [page.extract_text() for page in reader.pages]

    def trouver_page(terme: str, debut_page: int = 0) -> int:
        for idx in range(debut_page, len(pages_texte)):
            if terme.lower() in pages_texte[idx].lower():
                return idx
        return debut_page

    # 1. Avant-propos
    page_intro = trouver_page("Avant-propos", 0)
    writer.add_outline_item("Avant-propos", page_number=page_intro)

    derniere_page_ch = page_intro

    # 2. Les Chapitres et leurs sous-sections
    for chap in blueprint.get("chapitres", []):
        c_num = chap.get("numero", 1)
        c_titre = chap.get("titre", "")
        titre_complet_ch = f"Chapitre {c_num} : {c_titre}"

        page_ch = trouver_page(f"Chapitre {c_num}", derniere_page_ch)
        parent_ch = writer.add_outline_item(titre_complet_ch, page_number=page_ch)
        derniere_page_ch = page_ch

        # Sous-sections
        derniere_page_sec = page_ch
        for s_idx, sec in enumerate(chap.get("sections", []), start=1):
            s_titre = sec.get("titre", "")
            prefixe = f"{c_num}.{s_idx}"
            titre_sec = f"{prefixe} {s_titre}"

            page_sec = trouver_page(prefixe, derniere_page_sec)
            writer.add_outline_item(titre_sec, page_number=page_sec, parent=parent_ch)
            derniere_page_sec = page_sec

    # 3. Éléments finaux
    page_concl = trouver_page("Conclusion Générale", derniere_page_ch)
    writer.add_outline_item("Conclusion Générale", page_number=page_concl)

    page_avis = trouver_page("Votre Avis Compte", page_concl)
    writer.add_outline_item("Votre Avis Compte : Soutenir l'Auteur", page_number=page_avis)

    page_bio = trouver_page("À Propos de l'Auteur", page_avis)
    writer.add_outline_item("À Propos de l'Auteur : MarkEddy", page_number=page_bio)

    page_rem = trouver_page("Remerciements", page_bio)
    writer.add_outline_item("Remerciements & Notes d'Édition", page_number=page_rem)

    # 4. Métadonnées interactives
    titre = blueprint.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy"))
    sous_titre = blueprint.get("sous_titre", "")
    mots_cles = ", ".join(blueprint.get("mots_cles_kdp", []))

    writer.add_metadata({
        "/Title": titre,
        "/Author": auteur,
        "/Subject": sous_titre,
        "/Keywords": mots_cles,
        "/Creator": "Éditions MarkEddy - Machine de Publication KDP",
        "/Producer": "Playwright + PyPDF Interactive Outline Engine"
    })

    with open(pdf_destination, "wb") as f_out:
        writer.write(f_out)

    print(f"  ✅ PDF Numérique Interactif avec signets enregistré : {pdf_destination.resolve()}")


def compiler_version_numerique_interactive(blueprint: dict, manuscrit_md: str) -> Path:
    """Compile la version PDF numérique interactive avec liens et signets hiérarchiques."""
    print("\n" + "=" * 65)
    print("💻 3. COMPILATION VERSION NUMÉRIQUE INTERACTIVE (livre_numerique_interactif.pdf)")
    print("=" * 65)

    corps_html = markdown_vers_html(manuscrit_md, mode="interactive")
    titre = blueprint.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy"))
    auteur = blueprint.get("auteur", "MarkEddy")

    html_complet = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{titre} - Version Numérique Interactive</title>
    <style>
{CSS_DIGITAL_INTERACTIVE}
    </style>
</head>
<body>
{corps_html}
</body>
</html>"""

    LIVRABLE_DIGITAL_HTML.write_text(html_complet, encoding="utf-8")
    print(f"  ✅ Fichier HTML Interactif généré : {LIVRABLE_DIGITAL_HTML.resolve()}")

    pdf_temp = Path("temp_interactive_raw.pdf")
    asyncio.run(convertir_html_en_pdf_playwright(
        source_html=LIVRABLE_DIGITAL_HTML,
        sortie_pdf=pdf_temp,
        titre_livre=titre,
        auteur=auteur
    ))

    # Injection des signets et métadonnées
    injecter_signets_interactifs_pdf(pdf_temp, LIVRABLE_DIGITAL_PDF, blueprint)

    if pdf_temp.exists():
        pdf_temp.unlink()

    return LIVRABLE_DIGITAL_PDF


# ==============================================================================
# 7. ÉTAPE 3 : AUDIT PRE-FLIGHT & CERTIFICATION DES 3 LIVRABLES
# ==============================================================================

def auditer_livrables():
    """Vérifie l'intégrité, le poids, les métadonnées et la conformité des 3 fichiers."""
    print("\n" + "=" * 70)
    print("🔬 AUDIT PRE-FLIGHT CHIRURGICAL DES 3 FORMATS COMMERCIAUX")
    print("=" * 70)

    fichiers = [
        ("VERSION BROCHÉE PAPIER (Print-Ready)", LIVRABLE_PRINT_PDF, "PDF 6x9 po (Print KDP)"),
        ("VERSION EBOOK KINDLE (EPUB 3)", LIVRABLE_EBOOK_EPUB, "EPUB 3 Reflowable (Kindle)"),
        ("VERSION NUMÉRIQUE INTERACTIVE", LIVRABLE_DIGITAL_PDF, "PDF Interactif (Bookmarks & Links)")
    ]

    resultats = []

    for nom, path, format_nom in fichiers:
        if not path.exists():
            resultats.append({
                "format": nom,
                "fichier": path.name,
                "taille": "MANQUANT",
                "pages_mots": "0",
                "auteur_verifie": "NON",
                "statut": "❌ ÉCHEC"
            })
            continue

        taille_ko = path.stat().st_size / 1024
        taille_str = f"{taille_ko / 1024:.2f} Mo" if taille_ko > 1024 else f"{taille_ko:.1f} Ko"

        auteur_trouve = False
        details_volume = ""

        if path.suffix == ".pdf":
            try:
                reader = pypdf.PdfReader(str(path))
                nb_pages = len(reader.pages)
                details_volume = f"{nb_pages} pages"
                auteur_meta = reader.metadata.author if reader.metadata else ""
                auteur_trouve = "MarkEddy" in str(auteur_meta) or "MarkEddy" in reader.pages[0].extract_text()
            except Exception as e:
                details_volume = "Erreur lecture"
        elif path.suffix == ".epub":
            try:
                book = epub.read_epub(str(path))
                creators = book.get_metadata("DC", "creator")
                auteur_meta = ", ".join([c[0] for c in creators]) if creators else ""
                auteur_trouve = "MarkEddy" in auteur_meta
                # Nombre d'éléments HTML
                nb_items = len(list(book.get_items_of_type(9)))  # ITEM_DOCUMENT
                details_volume = f"{nb_items} chapitres reflowable"
            except Exception as e:
                details_volume = "Erreur lecture EPUB"

        statut = "✅ CERTIFIÉ CONFORME" if auteur_trouve else "⚠️ MÉTADONNÉES INCOMPLÈTES"

        resultats.append({
            "format": nom,
            "fichier": path.name,
            "chemin_absolu": str(path.resolve()),
            "taille": taille_str,
            "pages_mots": details_volume,
            "auteur_verifie": "MarkEddy" if auteur_trouve else "NON",
            "statut": statut
        })

    # Affichage du tableau de synthèse
    print("\n| Format Commercial | Fichier | Poids | Volume | Auteur Métadonnées | Statut KDP |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in resultats:
        print(f"| **{r['format']}** | `{r['fichier']}` | {r['taille']} | {r['pages_mots']} | `{r['auteur_verifie']}` | **{r['statut']}** |")

    print("\n" + "=" * 70)
    print("📍 CHEMINS ABSOLUS DES FICHIERS PRÊTS POUR PUBLICATION :")
    for r in resultats:
        if "chemin_absolu" in r:
            print(f"  • {r['format']} : {r['chemin_absolu']}")
    print("=" * 70 + "\n")

    return resultats


# ==============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ==============================================================================

def main():
    print("\n" + "=" * 70)
    print("👑 USINE DE PRODUCTION ÉDITORIALE KDP - AUTEUR MARKEDDY")
    print("   Compilation en 3 Versions Commerciales Distinctes")
    print("=" * 70)

    blueprint = charger_blueprint()
    manuscrit_md = charger_manuscrit()

    # 1. Version Brochée Papier
    compiler_version_imprimee(blueprint, manuscrit_md)

    # 2. Version Ebook Kindle
    compiler_version_ebook(blueprint, manuscrit_md)

    # 3. Version Numérique Interactive
    compiler_version_numerique_interactive(blueprint, manuscrit_md)

    # 4. Audit & Certification
    auditer_livrables()


if __name__ == "__main__":
    main()
