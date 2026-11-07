"""
cover_generator.py - Générateur de Couverture Complète KDP Haute Définition (300 DPI).
Intègre les palettes de prestige (Or, Émeraude, Saphir, Bordeaux) et la géométrie de reliure KDP.
"""

import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from kdp_design_system import PALETTES_PRESTIGE, KDP_METRICS_6X9, get_palette_par_defaut

DPI = KDP_METRICS_6X9["dpi"]
PAGE_WIDTH_INCHES = KDP_METRICS_6X9["trim_width_in"]
PAGE_HEIGHT_INCHES = KDP_METRICS_6X9["trim_height_in"]
BLEED_INCHES = KDP_METRICS_6X9["bleed_in"]

BLUEPRINT_PATH = Path("book_blueprint.json")
MANUSCRIT_PATH = Path("manuscrit_complet.md")
SORTIE_COUVERTURE = Path("couverture_kdp_complete.pdf")

def estimer_nombre_pages() -> int:
    # 1. Vérifier en priorité le PDF imprimable compilé réel
    pdf_print = Path("livre_imprimable_kdp.pdf")
    if not pdf_print.exists():
        pdf_print = Path("livre_kdp_interieur.pdf")
    if pdf_print.exists():
        try:
            import pypdf
            reader = pypdf.PdfReader(str(pdf_print))
            nb = len(reader.pages)
            if nb > 0:
                return nb
        except Exception:
            pass

    # 2. Estimation d'après le manuscrit
    if MANUSCRIT_PATH.exists():
        texte = MANUSCRIT_PATH.read_text(encoding="utf-8")
        mots = len(texte.split())
        return max(150, mots // 250)
    return 160

def calculer_dimensions_kdp(nb_pages: int, papier: str = "white"):
    epaisseur_page = KDP_METRICS_6X9["epaisseur_page_creme"] if papier == "cream" else KDP_METRICS_6X9["epaisseur_page_blanc"]
    dos_largeur_in = nb_pages * epaisseur_page
    
    largeur_totale_in = (BLEED_INCHES * 2) + (PAGE_WIDTH_INCHES * 2) + dos_largeur_in
    hauteur_totale_in = (BLEED_INCHES * 2) + PAGE_HEIGHT_INCHES
    
    return {
        "largeur_px": int(round(largeur_totale_in * DPI)),
        "hauteur_px": int(round(hauteur_totale_in * DPI)),
        "dos_px": int(round(dos_largeur_in * DPI)),
        "page_px": int(round(PAGE_WIDTH_INCHES * DPI)),
        "bleed_px": int(round(BLEED_INCHES * DPI)),
        "dos_in": dos_largeur_in
    }

def charger_donnees_livre() -> dict:
    if BLUEPRINT_PATH.exists():
        with open(BLUEPRINT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "titre": "MAÎTRISER SES FINANCES PERSONNELLES",
        "sous_titre": "De l'endettement à l'indépendance financière sans jargon",
        "auteur_suggere": "MarkEddy"
    }

def charger_police(taille: int, gras: bool = False):
    polices_test = [
        "C:/Windows/Fonts/georgiab.ttf" if gras else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if gras else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if gras else "C:/Windows/Fonts/calibri.ttf"
    ]
    for p in polices_test:
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

def generer_couverture(palette_name: str = "obsidian_gold"):
    palette = get_palette_par_defaut(palette_name)
    nb_pages = estimer_nombre_pages()
    dims = calculer_dimensions_kdp(nb_pages)
    blueprint = charger_donnees_livre()

    print(f"🎨 Palette appliquée : {palette['nom']}")
    print(f"📐 Nombre de pages estimé : {nb_pages}")
    print(f"📏 Largeur de la tranche (dos) : {dims['dos_in']:.4f} po ({dims['dos_px']} px)")
    print(f"🖼️ Résolution totale : {dims['largeur_px']} x {dims['hauteur_px']} px @ 300 DPI")

    # Fond de base
    img = Image.new("RGB", (dims["largeur_px"], dims["hauteur_px"]), color=palette["primaire"])
    draw = ImageDraw.Draw(img)

    # Coordonnées des zones
    x_dos_debut = dims["bleed_px"] + dims["page_px"]
    x_dos_fin = x_dos_debut + dims["dos_px"]
    centre_dos = (x_dos_debut + x_dos_fin) // 2
    centre_face = x_dos_fin + (dims["page_px"] // 2)
    centre_dos_arriere = dims["bleed_px"] + (dims["page_px"] // 2)

    # Zone du dos (Spine)
    draw.rectangle([x_dos_debut, 0, x_dos_fin, dims["hauteur_px"]], fill=palette["secondaire"])
    draw.line([(x_dos_debut, 0), (x_dos_debut, dims["hauteur_px"])], fill=palette["accent"], width=2)
    draw.line([(x_dos_fin, 0), (x_dos_fin, dims["hauteur_px"])], fill=palette["accent"], width=2)

    # 1ÈRE DE COUVERTURE (FRONT COVER)
    titre = blueprint.get("titre", "TITRE DU LIVRE").upper()
    sous_titre = blueprint.get("sous_titre", "Le guide pratique étape par étape")
    auteur = blueprint.get("auteur_suggere", "Édition Indépendante").upper()

    font_titre = charger_police(70, gras=True)
    font_soustitre = charger_police(32)
    font_auteur = charger_police(36, gras=True)

    y_courant = dims["bleed_px"] + 420
    
    # Découpage intelligent du titre
    mots = titre.split()
    lignes_titre = []
    ligne_temp = ""
    for m in mots:
        if len(ligne_temp + " " + m) < 22:
            ligne_temp = (ligne_temp + " " + m).strip()
        else:
            lignes_titre.append(ligne_temp)
            ligne_temp = m
    if ligne_temp:
        lignes_titre.append(ligne_temp)

    for lig in lignes_titre:
        y_courant = dessiner_texte_centre(draw, lig, centre_face, y_courant, font_titre, palette["texte_clair"])

    # Filet d'or décoratif
    y_courant += 30
    draw.line([(centre_face - 160, y_courant), (centre_face + 160, y_courant)], fill=palette["accent"], width=4)
    y_courant += 60

    # Sous-titre
    mots_st = sous_titre.split()
    lignes_st = []
    l_temp = ""
    for m in mots_st:
        if len(l_temp + " " + m) < 32:
            l_temp = (l_temp + " " + m).strip()
        else:
            lignes_st.append(l_temp)
            l_temp = m
    if l_temp:
        lignes_st.append(l_temp)

    for lig in lignes_st:
        y_courant = dessiner_texte_centre(draw, lig, centre_face, y_courant, font_soustitre, palette["texte_sourd"])

    # 1ère de couverture : Signature calligraphique officielle MarkEddy (Or & Champagne)
    logo_signature_path = Path("assets/logo/logo_markeddy_or_fond_sombre.png")
    if not logo_signature_path.exists():
        logo_signature_path = Path("assets/logo/logo_mark_eddy_blanc.png")
    if logo_signature_path.exists():
        try:
            sig_im = Image.open(logo_signature_path).convert("RGBA")
            sig_im.thumbnail((560, 180), Image.Resampling.LANCZOS)
            sw, sh = sig_im.size
            y_sig = dims["hauteur_px"] - dims["bleed_px"] - 360
            img.paste(sig_im, (centre_face - sw // 2, y_sig), sig_im)
        except Exception as e:
            dessiner_texte_centre(draw, auteur, centre_face, dims["hauteur_px"] - dims["bleed_px"] - 320, font_auteur, palette["texte_clair"])
    else:
        dessiner_texte_centre(draw, auteur, centre_face, dims["hauteur_px"] - dims["bleed_px"] - 320, font_auteur, palette["texte_clair"])

    # Dos de couverture (Spine) : Monogramme 'M' doré à la base
    logo_blason_path = Path("assets/logo/monogramme_m_dore.png")
    if not logo_blason_path.exists():
        logo_blason_path = Path("assets/logo/blason_me_transparent.png")
    if logo_blason_path.exists() and dims["dos_px"] >= 60:
        try:
            blason_dos = Image.open(logo_blason_path).convert("RGBA")
            dos_w = min(int(dims["dos_px"] * 0.70), 75)
            blason_dos.thumbnail((dos_w, dos_w), Image.Resampling.LANCZOS)
            bd_w, bd_h = blason_dos.size
            img.paste(blason_dos, (centre_dos - bd_w // 2, dims["hauteur_px"] - dims["bleed_px"] - 180), blason_dos)
        except Exception:
            pass

    # 4ÈME DE COUVERTURE (BACK COVER)
    font_back_h1 = charger_police(44, gras=True)
    font_back_txt = charger_police(26)
    
    y_back = dims["bleed_px"] + 420
    y_back = dessiner_texte_centre(draw, "CE QUE CE LIVRE VA CHANGER", centre_dos_arriere, y_back, font_back_h1, palette["accent"])
    y_back += 30

    lignes_promesse = [
        "Reprenez le contrôle complet de vos finances sans jargon abstrait.",
        "Ce guide complet condense des stratégies éprouvées et applicables",
        "dès aujourd'hui pour construire un patrimoine solide et durable.",
        "",
        "Au sommaire de ce guide :",
        "• La cartographie chirurgicale de vos flux de trésorerie",
        "• Le budget automatique des 3 comptes sans sacrifice",
        "• Le plan de désendettement accéléré mathématique",
        "• La constitution de votre forteresse d'épargne de sécurité",
        "• Vos premiers investissements indiciels passifs en bourse"
    ]
    for lp in lignes_promesse:
        y_back = dessiner_texte_centre(draw, lp, centre_dos_arriere, y_back, font_back_txt, palette["texte_sourd"])

    # Zone réservée pour le code-barres ISBN Amazon (600 x 360 px)
    isbn_x1 = dims["bleed_px"] + dims["page_px"] - 650
    isbn_y1 = dims["hauteur_px"] - dims["bleed_px"] - 420
    draw.rectangle([isbn_x1, isbn_y1, isbn_x1 + 600, isbn_y1 + 360], fill="#FFFFFF")
    draw.text((isbn_x1 + 100, isbn_y1 + 160), "Emplacement réservé Code-Barres ISBN KDP", fill="#64748B", font=charger_police(18))

    # Logo officiel Éditions MarkEddy à gauche du code-barres (Modèle Or pour fond sombre)
    logo_officiel_path = Path("assets/logo/logo_markeddy_or_fond_sombre.png")
    if not logo_officiel_path.exists():
        logo_officiel_path = Path("assets/logo/logo_mark_eddy_blanc.png")
    if logo_officiel_path.exists():
        try:
            logo_back = Image.open(logo_officiel_path).convert("RGBA")
            logo_back.thumbnail((460, 160), Image.Resampling.LANCZOS)
            lb_w, lb_h = logo_back.size
            img.paste(logo_back, (dims["bleed_px"] + 120, isbn_y1 + (360 - lb_h) // 2), logo_back)
        except Exception as e:
            print(f"Note logo 4ème : {e}")

    # Exportation PDF 300 DPI
    img.save(SORTIE_COUVERTURE, "PDF", resolution=300.0)
    print(f"✅ COUVERTURE KDP 300 DPI GÉNÉRÉE : {SORTIE_COUVERTURE.resolve()}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--palette", choices=list(PALETTES_PRESTIGE.keys()), default="obsidian_gold")
    args = parser.parse_args()
    generer_couverture(args.palette)
