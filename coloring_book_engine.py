"""
coloring_book_engine.py - Moteur de Création de Livres de Coloriage Amazon KDP.
Normes industrielles :
- Format 8.5" x 11" avec fond perdu (8.625" x 11.25" / 2588 x 3375 px à 300 DPI).
- Illustrations noir et blanc pur (#000000 sur #FFFFFF) sans bruit de gris.
- Générateur d'illustrations vectorielles SVG (Mandalas, Botanique, Animaux, Zen).
- Convertisseur Raster vers Line-Art haute netteté via Pillow.
- Option "Recto uniquement" (Single-Sided) anti-bavure pour feutres.
- Compilation HTML/PDF 300 DPI via Playwright et calcul dynamique du dos.
"""

import os
import math
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent

# Dimensions KDP Standard pour Livre de Coloriage (8.5 x 11 po)
POUCE_LARGEUR = 8.5
POUCE_HAUTEUR = 11.0
FOND_PERDU = 0.125
POUCE_LARGEUR_BLEED = POUCE_LARGEUR + (FOND_PERDU * 2)  # 8.625 po
POUCE_HAUTEUR_BLEED = POUCE_HAUTEUR + (FOND_PERDU * 2)  # 11.25 po

DPI = 300
LARGEUR_PX_BLEED = int(round(POUCE_LARGEUR_BLEED * DPI))  # 2588 px
HAUTEUR_PX_BLEED = int(round(POUCE_HAUTEUR_BLEED * DPI))  # 3375 px

COEFF_PAPIER_KDP = 0.002252  # Papier blanc standard KDP (pouce par page)


# ==============================================================================
# 1. GÉNÉRATEURS VECTORIELS SVG HAUTE PRÉCISION (NOIR ET BLANC PUR)
# ==============================================================================

def generer_svg_mandala(index: int, complexite: int = 8) -> str:
    """Génère un mandala géométrique sacré vectoriel détaillé."""
    cx, cy = 1000, 1000
    r_max = 850
    elements = []

    # Cercles directeurs
    for r in range(100, r_max + 1, 90):
        elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="#000000" stroke-width="3" fill="none"/>')

    # Rayons et étoiles géométriques
    nb_petales = 12 + ((index % 5) * 4)
    for i in range(nb_petales):
        angle = (2 * math.pi / nb_petales) * i
        x1 = cx + int(120 * math.cos(angle))
        y1 = cy + int(120 * math.sin(angle))
        x2 = cx + int(r_max * math.cos(angle))
        y2 = cy + int(r_max * math.sin(angle))
        elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="2"/>')

        # Rosaces intermédiaires
        cx_sub = cx + int(450 * math.cos(angle))
        cy_sub = cy + int(450 * math.sin(angle))
        elements.append(f'<circle cx="{cx_sub}" cy="{cy_sub}" r="140" stroke="#000000" stroke-width="2.5" fill="none"/>')
        elements.append(f'<circle cx="{cx_sub}" cy="{cy_sub}" r="80" stroke="#000000" stroke-width="2" fill="none"/>')

    # Motif central sacré
    for r_in in [30, 60, 90]:
        elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in}" stroke="#000000" stroke-width="4" fill="none"/>')

    # Bordure dentelée extérieure
    nb_pointes = nb_petales * 2
    pts_dentelle = []
    for k in range(nb_pointes):
        a = (2 * math.pi / nb_pointes) * k
        rayon = r_max if k % 2 == 0 else r_max - 50
        px = cx + int(rayon * math.cos(a))
        py = cy + int(rayon * math.sin(a))
        pts_dentelle.append(f"{px},{py}")
    elements.append(f'<polygon points="{" ".join(pts_dentelle)}" stroke="#000000" stroke-width="3.5" fill="none"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">
    <rect width="2000" height="2000" fill="#FFFFFF"/>
    {''.join(elements)}
    </svg>"""
    return svg


def generer_svg_botanique(index: int) -> str:
    """Génère un motif floral et botanique complexe prêt à colorier."""
    cx, cy = 1000, 1000
    elements = []

    # Tige centrale ondulante
    elements.append(f'<path d="M {cx} 1900 Q 800 1200 {cx} 600 T {cx} 150" stroke="#000000" stroke-width="5" fill="none"/>')

    # Fleurs et feuilles réparties
    nb_feuilles = 16
    for i in range(nb_feuilles):
        y_pos = 250 + (i * 95)
        cote = 1 if i % 2 == 0 else -1
        ctrl_x = cx + (cote * 450)
        end_x = cx + (cote * 650)
        end_y = y_pos - 80

        # Feuille en amande avec nervures
        elements.append(f'<path d="M {cx} {y_pos} Q {ctrl_x} {y_pos - 150} {end_x} {end_y} Q {ctrl_x} {y_pos + 120} {cx} {y_pos}" stroke="#000000" stroke-width="3" fill="none"/>')
        elements.append(f'<line x1="{cx}" y1="{y_pos}" x2="{end_x}" y2="{end_y}" stroke="#000000" stroke-width="2"/>')

        # Nervures secondaires
        for nv in [0.3, 0.6]:
            nx = cx + int((end_x - cx) * nv)
            ny = y_pos + int((end_y - y_pos) * nv)
            elements.append(f'<line x1="{nx}" y1="{ny}" x2="{nx + (cote * 80)}" y2="{ny - 40}" stroke="#000000" stroke-width="1.8"/>')

    # Grande fleur sommitale
    for pet in range(12):
        ang = (2 * math.pi / 12) * pet
        px = cx + int(180 * math.cos(ang))
        py = 220 + int(180 * math.sin(ang))
        elements.append(f'<circle cx="{px}" cy="{py}" r="65" stroke="#000000" stroke-width="2.5" fill="none"/>')
    elements.append(f'<circle cx="{cx}" cy="220" r="85" stroke="#000000" stroke-width="4" fill="none"/>')

    # Cadre extérieur élégant
    elements.append('<rect x="80" y="80" width="1840" height="1840" stroke="#000000" stroke-width="4" fill="none" rx="20"/>')
    elements.append('<rect x="110" y="110" width="1780" height="1780" stroke="#000000" stroke-width="1.5" fill="none" rx="15"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">
    <rect width="2000" height="2000" fill="#FFFFFF"/>
    {''.join(elements)}
    </svg>"""
    return svg


def generer_svg_animal_mystique(index: int) -> str:
    """Génère un portrait géométrique d'animal totem (Chouette sacrée / Lion / Scarabée)."""
    elements = []
    cx, cy = 1000, 1000

    # Silhouette géométrique d'une Chouette de Sagesse
    # Yeux géométriques concentriques
    for eye_cx in [720, 1280]:
        for r in [260, 210, 160, 110, 60]:
            elements.append(f'<circle cx="{eye_cx}" cy="800" r="{r}" stroke="#000000" stroke-width="3" fill="none"/>')
        for ray in range(16):
            a = (2 * math.pi / 16) * ray
            x1 = eye_cx + int(60 * math.cos(a))
            y1 = 800 + int(60 * math.sin(a))
            x2 = eye_cx + int(210 * math.cos(a))
            y2 = 800 + int(210 * math.sin(a))
            elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="2"/>')

    # Bec triangulaire
    elements.append('<polygon points="1000,850 930,1100 1070,1100" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<line x1="1000" y1="850" x2="1000" y2="1100" stroke="#000000" stroke-width="2"/>')

    # Plumes du torse en écailles superposées
    for row in range(5):
        y_ecaille = 1150 + (row * 120)
        nb_col = 5 - (row % 2)
        for col in range(nb_col):
            x_ecaille = 600 + (col * 180) + (40 if row % 2 else 0)
            elements.append(f'<path d="M {x_ecaille} {y_ecaille} Q {x_ecaille + 90} {y_ecaille + 110} {x_ecaille + 180} {y_ecaille}" stroke="#000000" stroke-width="3" fill="none"/>')
            elements.append(f'<circle cx="{x_ecaille + 90}" cy="{y_ecaille + 50}" r="25" stroke="#000000" stroke-width="2" fill="none"/>')

    # Oreilles aigrettes pointues
    elements.append('<polygon points="550,600 400,250 750,450" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<polygon points="1450,600 1600,250 1250,450" stroke="#000000" stroke-width="4" fill="none"/>')

    # Ailes latérales en arabesques
    elements.append('<path d="M 450 650 C 150 900 250 1600 650 1800" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<path d="M 1550 650 C 1850 900 1750 1600 1350 1800" stroke="#000000" stroke-width="4" fill="none"/>')

    # Cadre mandala
    elements.append('<rect x="80" y="80" width="1840" height="1840" stroke="#000000" stroke-width="5" fill="none" rx="20"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">
    <rect width="2000" height="2000" fill="#FFFFFF"/>
    {''.join(elements)}
    </svg>"""
    return svg


def generer_svg_zen_architecture(index: int) -> str:
    """Génère un temple japonais / torii géométrique et ses vagues zen."""
    elements = []
    # Soleil géométrique en arrière-plan
    elements.append('<circle cx="1000" cy="650" r="380" stroke="#000000" stroke-width="4" fill="none"/>')
    for ray in range(24):
        a = (2 * math.pi / 24) * ray
        elements.append(f'<line x1="{1000 + int(380*math.cos(a))}" y1="{650 + int(380*math.sin(a))}" x2="{1000 + int(480*math.cos(a))}" y2="{650 + int(480*math.sin(a))}" stroke="#000000" stroke-width="2"/>')

    # Grand Torii central
    # Poteaux verticaux
    elements.append('<rect x="650" y="550" width="70" height="1100" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<rect x="1280" y="550" width="70" height="1100" stroke="#000000" stroke-width="4" fill="none"/>')

    # Poutre haute courbée (Kasagi)
    elements.append('<path d="M 450 540 Q 1000 490 1550 540 L 1570 470 Q 1000 420 430 470 Z" stroke="#000000" stroke-width="4" fill="none"/>')

    # Poutre intermédiaire (Nuki)
    elements.append('<rect x="550" y="660" width="900" height="60" stroke="#000000" stroke-width="3" fill="none"/>')

    # Vagues de sable zen (Karesansui) au sol
    for v in range(8):
        y_vague = 1350 + (v * 70)
        elements.append(f'<path d="M 100 {y_vague} Q 500 {y_vague - 45} 1000 {y_vague} T 1900 {y_vague}" stroke="#000000" stroke-width="2.5" fill="none"/>')

    elements.append('<rect x="80" y="80" width="1840" height="1840" stroke="#000000" stroke-width="4" fill="none"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">
    <rect width="2000" height="2000" fill="#FFFFFF"/>
    {''.join(elements)}
    </svg>"""
    return svg


# ==============================================================================
# 2. CONVERTISSEUR RASTER VERS LINE-ART HAUTE NETTETÉ (PILLOW)
# ==============================================================================

def convertir_en_line_art(image_source_path: Path, output_path: Path, seuil_binaire: int = 145) -> Path:
    """
    Transforme une image matricielle (photo ou dessin couleur) en un line-art
    noir et blanc pur (#000000 sur #FFFFFF) sans aucun niveau de gris dégradé.
    """
    img = Image.open(image_source_path).convert("L")

    # Amélioration des contours par filtre d'arête
    img_contour = img.filter(ImageFilter.FIND_EDGES)
    img_contour = ImageOps.invert(img_contour)

    # Rehaussement du contraste
    img_contraste = ImageOps.autocontrast(img_contour, cutoff=2)

    # Binarisation stricte (0 ou 255)
    img_binaire = img_contraste.point(lambda p: 0 if p < seuil_binaire else 255, mode="1")

    # Enregistrement en 300 DPI
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_binaire.save(output_path, "PNG", dpi=(300, 300))
    print(f"✒️ Line-Art binarisé 300 DPI généré : {output_path.name}")
    return output_path


# ==============================================================================
# 3. MOTEUR DE DESSIN HAUTE RÉSOLUTION 300 DPI PILLOW (INDÉPENDANT & RAPIDE)
# ==============================================================================

def _charger_police(nom_prefere: str, taille: int, gras: bool = False) -> ImageFont.ImageFont:
    candidats = [
        f"C:/Windows/Fonts/{nom_prefere}",
        f"C:/Windows/Fonts/timesbd.ttf" if gras else "C:/Windows/Fonts/times.ttf",
        f"C:/Windows/Fonts/georgiab.ttf" if gras else "C:/Windows/Fonts/georgia.ttf",
        f"C:/Windows/Fonts/arialbd.ttf" if gras else "C:/Windows/Fonts/arial.ttf",
        nom_prefere
    ]
    for c in candidats:
        try:
            return ImageFont.truetype(c, taille)
        except Exception:
            pass
    return ImageFont.load_default()


def dessiner_page_titre_pil(titre: str, sous_titre: str, auteur: str = "MarkEddy") -> Image.Image:
    """Génère la page de faux-titre et d'attribution 300 DPI."""
    img = Image.new("RGB", (LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    w, h = LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED

    # Double cadre ornemental
    draw.rectangle([(180, 180), (w - 180, h - 180)], outline=(0, 0, 0), width=6)
    draw.rectangle([(210, 210), (w - 210, h - 210)], outline=(0, 0, 0), width=2)

    # Titre principal
    f_titre = _charger_police("timesbd.ttf", 85, gras=True)
    f_sub = _charger_police("georgia.ttf", 38)
    f_aut = _charger_police("timesbd.ttf", 36, gras=True)
    f_own = _charger_police("georgia.ttf", 32)

    # Titre centré (découpage si trop long)
    mots = titre.split()
    lignes_titre = []
    curr = []
    for m in mots:
        curr.append(m)
        if len(" ".join(curr)) > 24:
            lignes_titre.append(" ".join(curr))
            curr = []
    if curr:
        lignes_titre.append(" ".join(curr))

    y_pos = 850
    for lig in lignes_titre:
        draw.text((w // 2, y_pos), lig.upper(), fill=(0, 0, 0), font=f_titre, anchor="mm")
        y_pos += 110

    # Sous-titre
    y_pos += 40
    mots_sub = sous_titre.split()
    lignes_sub = []
    curr_s = []
    for ms in mots_sub:
        curr_s.append(ms)
        if len(" ".join(curr_s)) > 45:
            lignes_sub.append(" ".join(curr_s))
            curr_s = []
    if curr_s:
        lignes_sub.append(" ".join(curr_s))

    for lig_s in lignes_sub:
        draw.text((w // 2, y_pos), lig_s, fill=(50, 50, 50), font=f_sub, anchor="mm")
        y_pos += 60

    # Filet ornemental
    y_pos += 60
    draw.line([(w // 2 - 350, y_pos), (w // 2 + 350, y_pos)], fill=(0, 0, 0), width=3)
    draw.text((w // 2, y_pos + 40), "✦  ✦  ✦", fill=(0, 0, 0), font=f_sub, anchor="mm")
    y_pos += 120

    # Auteur & Édition
    draw.text((w // 2, y_pos), f"ÉDITION DE PRESTIGE • PAR {auteur.upper()}", fill=(0, 0, 0), font=f_aut, anchor="mm")

    # Boîte de propriétaire
    y_owner = h - 650
    draw.text((w // 2, y_owner), "Ce livre de coloriage d'art appartient à :", fill=(60, 60, 60), font=f_own, anchor="mm")
    draw.line([(w // 2 - 450, y_owner + 90), (w // 2 + 450, y_owner + 90)], fill=(0, 0, 0), width=3)

    return img


def dessiner_page_copyright_pil(titre: str, auteur: str = "MarkEddy") -> Image.Image:
    """Génère la page légale et de conformité KDP 300 DPI."""
    img = Image.new("RGB", (LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    w, h = LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED

    f_bold = _charger_police("timesbd.ttf", 36, gras=True)
    f_txt = _charger_police("georgia.ttf", 30)

    lignes = [
        (titre.upper(), f_bold),
        ("", f_txt),
        (f"Conception artistique & Direction d'édition : {auteur}", f_txt),
        ("© 2026 MarkEddy Publishing House. Tous droits réservés.", f_txt),
        ("", f_txt),
        ("Format d'impression officiel : Broché Amazon KDP 8.5\" × 11\" (21,59 × 27,94 cm)", f_txt),
        ("Papier blanc standard KDP 55 lb (90 g/m²) haute densité d'encrage.", f_txt),
        ("Encre noir profond 100% sans bavure.", f_txt),
        ("", f_txt),
        ("Toute reproduction totale ou partielle sans accord préalable de l'auteur est interdite.", f_txt),
        ("Première Édition Mondiale — Imprimé à la demande par Amazon.", f_txt)
    ]

    y_pos = h // 2 - 300
    for text, font in lignes:
        if text:
            draw.text((w // 2, y_pos), text, fill=(50, 50, 50), font=font, anchor="mm")
        y_pos += 55

    return img


def dessiner_page_nuancier_pil() -> Image.Image:
    """Génère la page de test des couleurs et nuancier 300 DPI."""
    img = Image.new("RGB", (LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    w, h = LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED

    # Cadre extérieur
    draw.rectangle([(180, 180), (w - 180, h - 180)], outline=(0, 0, 0), width=4)

    f_titre = _charger_police("timesbd.ttf", 60, gras=True)
    f_sub = _charger_police("georgia.ttf", 32)
    f_label = _charger_police("arial.ttf", 24)

    draw.text((w // 2, 380), "TEST DE COULEURS & NUANCIER", fill=(0, 0, 0), font=f_titre, anchor="mm")
    draw.text((w // 2, 460), "Testez vos feutres, crayons et encres ici pour apprécier leur intensité.", fill=(70, 70, 70), font=f_sub, anchor="mm")

    # Grille de 24 cases (4 colonnes x 6 lignes)
    nb_cols = 4
    nb_lignes = 6
    margin_x = 350
    spacing_x = (w - (2 * margin_x)) // (nb_cols - 1)
    start_y = 650
    spacing_y = 380

    compteur = 1
    for r in range(nb_lignes):
        for c in range(nb_cols):
            cx = margin_x + (c * spacing_x)
            cy = start_y + (r * spacing_y)

            # Rectangle conteneur
            draw.rectangle([(cx - 170, cy - 130), (cx + 170, cy + 130)], outline=(180, 180, 180), width=2)
            # Cercle de test
            draw.ellipse([(cx - 65, cy - 80), (cx + 65, cy + 50)], outline=(0, 0, 0), width=3)
            # Libellé
            draw.text((cx, cy + 90), f"Nuance #{compteur:02d}", fill=(80, 80, 80), font=f_label, anchor="mm")
            compteur += 1

    return img


def dessiner_page_anti_bavure_pil(type_page: str = "guard") -> Image.Image:
    """Génère la page verso de protection anti-bavure pour préserver les illustrations."""
    img = Image.new("RGB", (LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED), (252, 252, 252))
    draw = ImageDraw.Draw(img)
    w, h = LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED

    # Boîte centrale en pointillés
    box_w, box_h = 1600, 1100
    bx1 = (w - box_w) // 2
    by1 = (h - box_h) // 2
    bx2 = bx1 + box_w
    by2 = by1 + box_h

    # Contour en tirets
    dash_len = 25
    for x in range(bx1, bx2, dash_len * 2):
        draw.line([(x, by1), (min(x + dash_len, bx2), by1)], fill=(160, 160, 160), width=3)
        draw.line([(x, by2), (min(x + dash_len, bx2), by2)], fill=(160, 160, 160), width=3)
    for y in range(by1, by2, dash_len * 2):
        draw.line([(bx1, y), (bx1, min(y + dash_len, by2))], fill=(160, 160, 160), width=3)
        draw.line([(bx2, y), (bx2, min(y + dash_len, by2))], fill=(160, 160, 160), width=3)

    f_titre = _charger_police("timesbd.ttf", 44, gras=True)
    f_sub = _charger_police("georgia.ttf", 32)
    f_tip = _charger_police("georgia.ttf", 28)

    draw.text((w // 2, by1 + 250), "🛡️", fill=(0, 0, 0), font=_charger_police("segoeui.ttf", 70), anchor="mm")
    draw.text((w // 2, by1 + 400), "PAGE DE PROTECTION ANTI-BAVURE", fill=(40, 40, 40), font=f_titre, anchor="mm")

    lignes = [
        "Cette page a été délibérément laissée vierge pour empêcher l'encre",
        "de vos feutres, marqueurs à alcool ou aquarelles de traverser le papier",
        "et d'endommager la planche suivante.",
        "",
        "Astuce d'Artiste : Vous pouvez glisser une feuille cartonnée souple",
        "sous votre coloriage pour une liberté d'encrage totale."
    ]

    y_t = by1 + 520
    for l in lignes:
        font = f_tip if "Astuce" in l else f_sub
        color = (100, 100, 100) if "Astuce" in l else (70, 70, 70)
        draw.text((w // 2, y_t), l, fill=color, font=font, anchor="mm")
        y_t += 55

    return img


def dessiner_page_felicitations_pil() -> Image.Image:
    """Génère la page finale de félicitations et d'appel aux avis 300 DPI."""
    img = Image.new("RGB", (LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    w, h = LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED

    # Double cadre ornemental
    draw.rectangle([(200, 200), (w - 200, h - 200)], outline=(0, 0, 0), width=5)

    f_t = _charger_police("timesbd.ttf", 70, gras=True)
    f_txt = _charger_police("georgia.ttf", 34)
    f_call = _charger_police("timesbd.ttf", 36, gras=True)

    cy = h // 2
    draw.text((w // 2, cy - 500), "🏆", fill=(0, 0, 0), font=_charger_police("segoeui.ttf", 90), anchor="mm")
    draw.text((w // 2, cy - 350), "FÉLICITATIONS !", fill=(0, 0, 0), font=f_t, anchor="mm")

    lignes = [
        "Vous êtes arrivé au terme de ce recueil artistique et méditatif.",
        "Le coloriage régulier active les ondes alpha cérébrales,",
        "apaise l'amygdale et restaure une concentration profonde.",
        "",
        "✦  ✦  ✦",
        "",
        "Votre créativité mérite d'être partagée !",
        "Prenez une photo de votre coloriage préféré et partagez-la",
        "dans votre avis client Amazon pour inspirer la communauté."
    ]

    y = cy - 200
    for lig in lignes:
        if "✦" in lig:
            draw.text((w // 2, y), lig, fill=(0, 0, 0), font=f_txt, anchor="mm")
        elif "avis client" in lig or "créativité" in lig:
            draw.text((w // 2, y), lig, fill=(20, 20, 20), font=f_call, anchor="mm")
        else:
            draw.text((w // 2, y), lig, fill=(60, 60, 60), font=f_txt, anchor="mm")
        y += 65

    return img


def dessiner_planche_pil(theme: str, index: int, titre: str) -> Image.Image:
    """Génère une planche de coloriage complète 300 DPI aux normes KDP 8.5x11 po."""
    img = Image.new("RGB", (LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    w, h = LARGEUR_PX_BLEED, HAUTEUR_PX_BLEED

    # Marges KDP avec Gutter intérieur renforcé (260 px à gauche, 180 px à droite)
    margin_l = 260
    margin_r = 180
    margin_t = 180
    margin_b = 240

    # Cadre de l'illustration
    draw.rectangle([(margin_l, margin_t), (w - margin_r, h - margin_b)], outline=(0, 0, 0), width=6)
    draw.rectangle([(margin_l + 30, margin_t + 30), (w - margin_r - 30, h - margin_b - 30)], outline=(0, 0, 0), width=2)

    cx = (margin_l + w - margin_r) // 2
    cy = (margin_t + h - margin_b) // 2

    th = theme.lower()
    if th == "botanique":
        # Motif floral & végétal luxuriant
        # Tige centrale ondulante
        stem_pts = []
        for step in range(30):
            ty = margin_t + 100 + (step * (h - margin_t - margin_b - 200) // 29)
            tx = cx + int(120 * math.sin(step * 0.45 + (index * 0.5)))
            stem_pts.append((tx, ty))
        for p1, p2 in zip(stem_pts[:-1], stem_pts[1:]):
            draw.line([p1, p2], fill=(0, 0, 0), width=8)

        # Feuilles alternées
        for idx_f, (tx, ty) in enumerate(stem_pts[2:-2:2]):
            cote = 1 if idx_f % 2 == 0 else -1
            end_x = tx + (cote * 420)
            end_y = ty - 120
            ctrl_x = tx + (cote * 250)

            # Contour de la feuille
            draw.arc([(min(tx, end_x), min(ty, end_y) - 60), (max(tx, end_x), max(ty, end_y) + 60)], 0, 360, fill=(0, 0, 0), width=4)
            draw.line([(tx, ty), (end_x, end_y)], fill=(0, 0, 0), width=3)
            # Nervures secondaires
            for nv in [0.35, 0.70]:
                nx = tx + int((end_x - tx) * nv)
                ny = ty + int((end_y - ty) * nv)
                draw.line([(nx, ny), (nx + (cote * 80), ny - 45)], fill=(0, 0, 0), width=2)

        # Grande fleur sommitale
        top_x, top_y = stem_pts[0]
        for pet in range(12):
            ang = (2 * math.pi / 12) * pet
            px = top_x + int(180 * math.cos(ang))
            py = top_y + int(180 * math.sin(ang))
            draw.ellipse([(px - 70, py - 70), (px + 70, py + 70)], outline=(0, 0, 0), width=4)
        draw.ellipse([(top_x - 90, top_y - 90), (top_x + 90, top_y + 90)], outline=(0, 0, 0), width=6)

    elif th == "animaux":
        # Chouette sacrée / Animal totem géométrique
        # Yeux concentriques
        for eye_x in [cx - 280, cx + 280]:
            eye_y = cy - 250
            for r in [280, 220, 160, 100, 45]:
                draw.ellipse([(eye_x - r, eye_y - r), (eye_x + r, eye_y + r)], outline=(0, 0, 0), width=4)
            for ray in range(16):
                a = (2 * math.pi / 16) * ray
                rx1 = eye_x + int(45 * math.cos(a))
                ry1 = eye_y + int(45 * math.sin(a))
                rx2 = eye_x + int(220 * math.cos(a))
                ry2 = eye_y + int(220 * math.sin(a))
                draw.line([(rx1, ry1), (rx2, ry2)], fill=(0, 0, 0), width=3)

        # Bec triangulaire
        draw.polygon([(cx, cy - 200), (cx - 80, cy + 80), (cx + 80, cy + 80)], outline=(0, 0, 0), fill=None)
        draw.line([(cx, cy - 200), (cx, cy + 80)], fill=(0, 0, 0), width=3)

        # Plumes du torse en écailles superposées
        for row in range(5):
            y_ec = cy + 120 + (row * 130)
            nb_col = 5 - (row % 2)
            for col in range(nb_col):
                x_ec = cx - 350 + (col * 175) + (35 if row % 2 else 0)
                draw.arc([(x_ec - 80, y_ec - 40), (x_ec + 80, y_ec + 80)], 0, 180, fill=(0, 0, 0), width=4)
                draw.ellipse([(x_ec - 20, y_ec + 10), (x_ec + 20, y_ec + 50)], outline=(0, 0, 0), width=2)

        # Aigrettes / Cornes géométriques
        draw.polygon([(cx - 450, cy - 450), (cx - 250, cy - 750), (cx - 100, cy - 500)], outline=(0, 0, 0))
        draw.polygon([(cx + 450, cy - 450), (cx + 250, cy - 750), (cx + 100, cy - 500)], outline=(0, 0, 0))

    elif th == "architecture":
        # Grand Torii & Vagues Zen
        # Grand soleil géométrique
        sun_y = cy - 250
        draw.ellipse([(cx - 420, sun_y - 420), (cx + 420, sun_y + 420)], outline=(0, 0, 0), width=5)
        for s_ray in range(24):
            sa = (2 * math.pi / 24) * s_ray
            sx1 = cx + int(420 * math.cos(sa))
            sy1 = sun_y + int(420 * math.sin(sa))
            sx2 = cx + int(560 * math.cos(sa))
            sy2 = sun_y + int(560 * math.sin(sa))
            draw.line([(sx1, sy1), (sx2, sy2)], fill=(0, 0, 0), width=3)

        # Piliers Torii
        draw.rectangle([(cx - 360, cy - 350), (cx - 280, cy + 550)], outline=(0, 0, 0), width=5)
        draw.rectangle([(cx + 280, cy - 350), (cx + 360, cy + 550)], outline=(0, 0, 0), width=5)
        # Poutre haute
        draw.polygon([(cx - 480, cy - 360), (cx + 480, cy - 360), (cx + 450, cy - 430), (cx - 450, cy - 430)], outline=(0, 0, 0))
        # Poutre basse
        draw.rectangle([(cx - 400, cy - 260), (cx + 400, cy - 210)], outline=(0, 0, 0), width=4)

        # Vagues de sable Zen (Karesansui)
        for wave_idx in range(9):
            wy = cy + 420 + (wave_idx * 75)
            wave_pts = []
            for wx in range(margin_l + 40, w - margin_r - 40, 20):
                wave_y = wy + int(25 * math.sin((wx * 0.015) + (wave_idx * 0.4)))
                wave_pts.append((wx, wave_y))
            for p1, p2 in zip(wave_pts[:-1], wave_pts[1:]):
                draw.line([p1, p2], fill=(0, 0, 0), width=3)

    else:
        # Mandalas géométriques sacrés par défaut
        r_max = 920
        # Cercles directeurs
        for r in range(120, r_max + 1, 100):
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(0, 0, 0), width=4)

        nb_petales = 12 + ((index % 5) * 4)
        for i in range(nb_petales):
            angle = (2 * math.pi / nb_petales) * i
            x1 = cx + int(120 * math.cos(angle))
            y1 = cy + int(120 * math.sin(angle))
            x2 = cx + int(r_max * math.cos(angle))
            y2 = cy + int(r_max * math.sin(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0), width=3)

            # Rosettes secondaires
            cx_sub = cx + int(520 * math.cos(angle))
            cy_sub = cy + int(520 * math.sin(angle))
            draw.ellipse([(cx_sub - 120, cy_sub - 120), (cx_sub + 120, cy_sub + 120)], outline=(0, 0, 0), width=3)
            draw.ellipse([(cx_sub - 60, cy_sub - 60), (cx_sub + 60, cy_sub + 60)], outline=(0, 0, 0), width=2)

        # Motif sacré central
        for r_in in [40, 80, 120]:
            draw.ellipse([(cx - r_in, cy - r_in), (cx + r_in, cy + r_in)], outline=(0, 0, 0), width=5)

        # Étoiles de liaison
        for k in range(nb_petales * 2):
            a_star = (2 * math.pi / (nb_petales * 2)) * k
            r_s = r_max - 50 if k % 2 == 0 else r_max - 150
            sx = cx + int(r_s * math.cos(a_star))
            sy = cy + int(r_s * math.sin(a_star))
            draw.ellipse([(sx - 20, sy - 20), (sx + 20, sy + 20)], outline=(0, 0, 0), width=3)

    # Bas de page : libellé de la planche
    f_footer = _charger_police("arial.ttf", 26)
    draw.text((cx, h - margin_b + 55), f"PLANCHE {index:02d} • {titre.upper()}", fill=(100, 100, 100), font=f_footer, anchor="mm")

    return img


# ==============================================================================
# 4. COMPILATION DU LIVRE DE COLORIAGE KDP 8.5" x 11"
# ==============================================================================

def produire_livre_coloriage(
    book_id: int,
    titre: str,
    sous_titre: str,
    theme: str = "mandalas",
    nb_illustrations: int = 30,
    recto_uniquement: bool = True,
    cover_bg_image: Optional[str] = None
) -> Dict[str, Any]:
    """
    Génère l'intégralité d'un livre de coloriage professionnel conforme aux normes Amazon KDP :
    - Format 8.5" x 11" avec fond perdu (8.625" x 11.25" / 2588 x 3375 px à 300 DPI).
    - Planches vectorielles noir et blanc pur (#000000 sur #FFFFFF).
    - Pages verso anti-bavure pour feutres si recto_uniquement=True.
    - Compilation PDF 300 DPI ultra-rapide et garantie sans échec via Pillow.
    - Couverture complète 300 DPI (Plat 1 + Dos calculé + Plat 4) via generate_luxury_cover.
    - Export des SVGs individuels et maquette HTML pour prévisualisation web.
    """
    dossier_livre = BASE_DIR / "books" / f"livre_coloriage_{book_id}"
    dossier_livre.mkdir(parents=True, exist_ok=True)
    dossier_planches = dossier_livre / "planches"
    dossier_planches.mkdir(exist_ok=True)

    # 1. Sélection du générateur SVG
    generateurs_svg = {
        "mandalas": generer_svg_mandala,
        "botanique": generer_svg_botanique,
        "animaux": generer_svg_animal_mystique,
        "architecture": generer_svg_zen_architecture
    }
    gen_svg_func = generateurs_svg.get(theme.lower(), generer_svg_mandala)

    print(f"\n🎨 [COLORIAGE] Génération de {nb_illustrations} planches thématiques '{theme}'...")

    # 2. Sauvegarde des SVGs pour les exports / Canva / Web
    planches_html = []
    for idx in range(1, nb_illustrations + 1):
        svg_code = gen_svg_func(idx)
        fichier_svg = dossier_planches / f"planche_{idx:02d}.svg"
        fichier_svg.write_text(svg_code, encoding="utf-8")

        page_recto = f"""
        <div class="page page-illustration">
          <div class="illustration-frame">
            {svg_code}
          </div>
          <div class="page-footer">Planche {idx} • {titre}</div>
        </div>
        """
        planches_html.append(page_recto)

        if recto_uniquement:
            page_verso = f"""
            <div class="page page-verso-anti-bleed">
              <div class="bleed-guard-box">
                <div class="bleed-guard-icon">🛡️</div>
                <div class="bleed-guard-title">PAGE DE PROTECTION ANTI-BAVURE</div>
                <div class="bleed-guard-text">
                  Cette page a été délibérément laissée vierge pour empêcher l'encre de vos feutres,
                  marqueurs à alcool ou aquarelles de traverser le papier et d'endommager la planche suivante.
                </div>
              </div>
            </div>
            """
            planches_html.append(page_verso)

    # Écriture de la maquette HTML complète
    fichier_html_interieur = dossier_livre / "interieur_coloriage_8.5x11.html"
    fichier_html_interieur.write_text(f"""<!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="UTF-8"><title>{titre}</title>
    <style>
      @page {{ size: {POUCE_LARGEUR_BLEED}in {POUCE_HAUTEUR_BLEED}in; margin: 0; }}
      body {{ font-family: sans-serif; margin: 0; padding: 0; }}
      .page {{ width: {POUCE_LARGEUR_BLEED}in; height: {POUCE_HAUTEUR_BLEED}in; page-break-after: always; display: flex; align-items: center; justify-content: center; }}
    </style>
    </head>
    <body>{''.join(planches_html)}</body></html>""", encoding="utf-8")

    # 3. Rendu haute définition 300 DPI de toutes les pages avec Pillow
    print("📖 Rendu des pages intérieures 300 DPI haute résolution...")
    pages_images: List[Image.Image] = []

    # Page 1: Faux-titre
    pages_images.append(dessiner_page_titre_pil(titre, sous_titre, "MarkEddy"))

    # Page 2: Copyright & Mentions KDP
    pages_images.append(dessiner_page_copyright_pil(titre, "MarkEddy"))

    # Page 3: Nuancier & Test de couleurs
    pages_images.append(dessiner_page_nuancier_pil())

    if recto_uniquement:
        # Verso du nuancier
        pages_images.append(dessiner_page_anti_bavure_pil("tip"))

    # Planches de coloriage
    for idx in range(1, nb_illustrations + 1):
        # Recto (illustration)
        img_planche = dessiner_planche_pil(theme, idx, titre)
        pages_images.append(img_planche)

        # Verso anti-bavure si recto_uniquement
        if recto_uniquement:
            pages_images.append(dessiner_page_anti_bavure_pil("guard"))

    # Page de félicitations
    pages_images.append(dessiner_page_felicitations_pil())

    # 4. Assemblage en PDF multi-page 300 DPI
    fichier_pdf_interieur = dossier_livre / "Interieur_Coloriage_8.5x11.pdf"
    print(f"📚 Assemblage du PDF multi-pages 300 DPI ({len(pages_images)} pages)...")
    pages_images[0].save(
        fichier_pdf_interieur,
        "PDF",
        resolution=300.0,
        save_all=True,
        append_images=pages_images[1:]
    )

    from pypdf import PdfReader
    reader = PdfReader(str(fichier_pdf_interieur))
    nb_pages_total = len(reader.pages)

    # 5. Calcul précis du dos KDP (8.5 x 11 po)
    epaisseur_dos = nb_pages_total * COEFF_PAPIER_KDP
    largeur_totale_couv_in = (FOND_PERDU * 2) + (POUCE_LARGEUR * 2) + epaisseur_dos
    hauteur_totale_couv_in = (FOND_PERDU * 2) + POUCE_HAUTEUR

    print(f"📐 Nombre total de pages : {nb_pages_total} pages.")
    print(f"📐 Largeur du dos calculée : {epaisseur_dos:.4f} po ({epaisseur_dos * 25.4:.2f} mm).")

    # 6. Génération de la couverture complète 300 DPI
    fichier_pdf_couv = dossier_livre / "couverture_coloriage_complete.pdf"
    fichier_jpg_couv = dossier_livre / "couverture_ebook.jpg"

    from generate_luxury_cover import generer_couverture_kdp
    try:
        generer_couverture_kdp(
            nb_pages=nb_pages_total,
            largeur_page=POUCE_LARGEUR,
            hauteur_page=POUCE_HAUTEUR,
            titre=titre,
            sous_titre=sous_titre,
            auteur="MarkEddy",
            bg_image_path=cover_bg_image
        )
        if Path("couverture_kdp_complete.pdf").exists():
            shutil.copy2("couverture_kdp_complete.pdf", fichier_pdf_couv)
        elif Path("couvertures_finales/Couverture_OFFICIELLE_KDP.pdf").exists():
            shutil.copy2("couvertures_finales/Couverture_OFFICIELLE_KDP.pdf", fichier_pdf_couv)

        if Path("couverture_ebook.jpg").exists():
            shutil.copy2("couverture_ebook.jpg", fichier_jpg_couv)
        elif Path("couvertures_export/01_amazon_kdp_ebook_cover.jpg").exists():
            shutil.copy2("couvertures_export/01_amazon_kdp_ebook_cover.jpg", fichier_jpg_couv)
    except Exception as e_cov:
        print(f"⚠️ Note génération couverture coloriage : {e_cov}")

    # 7. Pack Marketing KDP spécifique Coloriage
    fichier_marketing = dossier_livre / "kdp_marketing_pack.html"
    marketing_content = f"""
    <h2>{titre} — Grand Format Broché 8.5" × 11"</h2>
    <p><b>Plongez dans un univers d'apaisement absolu et libérez votre potentiel créatif !</b></p>
    <h3>Pourquoi choisir ce livre de coloriage d'art :</h3>
    <ul>
      <li><b>{nb_illustrations} Illustrations Uniques :</b> Tracés noir et blanc pur ultra-nets conçus pour une relaxation profonde.</li>
      <li><b>Pages Recto Uniquement :</b> Feuilles blanches anti-bavure au verso pour protéger vos créations des feutres et marqueurs.</li>
      <li><b>Grand Format Confort 8.5" × 11" :</b> Dimensions idéales pour un espace de coloriage ample et immersif.</li>
      <li><b>Page Test Nuancier :</b> Testez vos dégradés et crayons avant de vous lancer.</li>
    </ul>
    """
    fichier_marketing.write_text(marketing_content, encoding="utf-8")

    return {
        "status": "success",
        "nb_pages": nb_pages_total,
        "nb_illustrations": nb_illustrations,
        "epaisseur_dos_po": epaisseur_dos,
        "chemin_pdf_interieur": str(fichier_pdf_interieur.relative_to(BASE_DIR)),
        "chemin_pdf_couverture": str(fichier_pdf_couv.relative_to(BASE_DIR)) if fichier_pdf_couv.exists() else None,
        "chemin_couverture_jpg": str(fichier_jpg_couv.relative_to(BASE_DIR)) if fichier_jpg_couv.exists() else None,
        "chemin_interieur_html": str(fichier_html_interieur.relative_to(BASE_DIR)),
        "chemin_marketing_html": str(fichier_marketing.relative_to(BASE_DIR))
    }


if __name__ == "__main__":
    print("Test coloring_book_engine...")
    res = produire_livre_coloriage(
        book_id=888,
        titre="MANDALAS SACRÉS & SÉRÉNITÉ",
        sous_titre="50 motifs géométriques pour apaiser l'esprit",
        theme="mandalas",
        nb_illustrations=6,
        recto_uniquement=True
    )
    print("Résultat Coloriage:", res)
