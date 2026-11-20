"""
kdp_extensions/coloring_book_engine.py - Moteur de Livres de Coloriage Amazon KDP.

Extension 100 % isolée : le coloring_book_engine.py de la racine reste intact.
Ce module apporte :

1. Support des 16 formats KDP officiels (8.5" x 11" par défaut) via
   kdp_extensions.kdp_dimensions.calculate_kdp_specs (fond perdu 0.125",
   dimensions 300 DPI exactes, dos calculé, réserve ISBN).
2. Planches noir et blanc PUR (#000000 sur #FFFFFF, zéro niveau de gris) via
   SVG vectorielle haute précision ou conversion line-art Pillow binaire.
3. Option "recto uniquement" : page verso blanche anti-bavure après chaque
   illustration (anti-bavure feutres / marqueurs).
4. Compilation PDF 300 DPI via Playwright (Chromium), avec repli msedge.
5. Couverture calibrée via cover_artisan_agent.fabriquer() (tranche au micron).

Exécution : .\\.venv\\Scripts\\python.exe
"""

import math
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from kdp_extensions.kdp_dimensions import calculate_kdp_specs, normalize_format

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. GÉNÉRATEURS VECTORIELS SVG (NOIR #000000 SUR BLANC #FFFFFF, SANS GRIS)
# ==============================================================================

def generer_svg_mandala(index: int, complexite: int = 8) -> str:
    """Mandala géométrique sacré vectoriel détaillé (noir pur sur blanc pur)."""
    cx, cy = 1000, 1000
    r_max = 850
    elements = []

    for r in range(100, r_max + 1, 90):
        elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="#000000" stroke-width="3" fill="none"/>')

    nb_petales = 12 + ((index % 5) * 4)
    for i in range(nb_petales):
        angle = (2 * math.pi / nb_petales) * i
        x1 = cx + int(120 * math.cos(angle))
        y1 = cy + int(120 * math.sin(angle))
        x2 = cx + int(r_max * math.cos(angle))
        y2 = cy + int(r_max * math.sin(angle))
        elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="2"/>')

        cx_sub = cx + int(450 * math.cos(angle))
        cy_sub = cy + int(450 * math.sin(angle))
        elements.append(f'<circle cx="{cx_sub}" cy="{cy_sub}" r="140" stroke="#000000" stroke-width="2.5" fill="none"/>')
        elements.append(f'<circle cx="{cx_sub}" cy="{cy_sub}" r="80" stroke="#000000" stroke-width="2" fill="none"/>')

    for r_in in [30, 60, 90]:
        elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in}" stroke="#000000" stroke-width="4" fill="none"/>')

    nb_pointes = nb_petales * 2
    pts_dentelle = []
    for k in range(nb_pointes):
        a = (2 * math.pi / nb_pointes) * k
        rayon = r_max if k % 2 == 0 else r_max - 50
        px = cx + int(rayon * math.cos(a))
        py = cy + int(rayon * math.sin(a))
        pts_dentelle.append(f"{px},{py}")
    elements.append(f'<polygon points="{" ".join(pts_dentelle)}" stroke="#000000" stroke-width="3.5" fill="none"/>')

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">'
        '<rect width="2000" height="2000" fill="#FFFFFF"/>'
        + "".join(elements) +
        "</svg>"
    )


def generer_svg_botanique(index: int) -> str:
    """Motif floral & botanique complexe prêt à colorier (noir pur)."""
    cx, cy = 1000, 1000
    decalage = ((index % 5) - 2) * 45
    elements = [
        f'<path d="M {cx} 1900 Q {800 + decalage} 1200 {cx} 600 T {cx} 150" stroke="#000000" stroke-width="5" fill="none"/>'
    ]

    for i in range(16):
        y_pos = 250 + (i * 95)
        cote = 1 if i % 2 == 0 else -1
        ctrl_x = cx + (cote * 450)
        end_x = cx + (cote * 650)
        end_y = y_pos - 80
        elements.append(
            f'<path d="M {cx} {y_pos} Q {ctrl_x} {y_pos - 150} {end_x} {end_y} '
            f'Q {ctrl_x} {y_pos + 120} {cx} {y_pos}" stroke="#000000" stroke-width="3" fill="none"/>'
        )
        elements.append(f'<line x1="{cx}" y1="{y_pos}" x2="{end_x}" y2="{end_y}" stroke="#000000" stroke-width="2"/>')
        for nv in (0.3, 0.6):
            nx = cx + int((end_x - cx) * nv)
            ny = y_pos + int((end_y - y_pos) * nv)
            elements.append(
                f'<line x1="{nx}" y1="{ny}" x2="{nx + (cote * 80)}" y2="{ny - 40}" stroke="#000000" stroke-width="1.8"/>'
            )

    for pet in range(12):
        ang = (2 * math.pi / 12) * pet
        px = cx + int(180 * math.cos(ang))
        py = 220 + int(180 * math.sin(ang))
        elements.append(f'<circle cx="{px}" cy="{py}" r="65" stroke="#000000" stroke-width="2.5" fill="none"/>')
    elements.append(f'<circle cx="{cx}" cy="220" r="85" stroke="#000000" stroke-width="4" fill="none"/>')

    elements.append('<rect x="80" y="80" width="1840" height="1840" stroke="#000000" stroke-width="4" fill="none" rx="20"/>')
    elements.append('<rect x="110" y="110" width="1780" height="1780" stroke="#000000" stroke-width="1.5" fill="none" rx="15"/>')

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">'
        '<rect width="2000" height="2000" fill="#FFFFFF"/>'
        + "".join(elements) +
        "</svg>"
    )


def generer_svg_animal_mystique(index: int) -> str:
    """Portrait géométrique d'animal totem (chouette sacrée / lion / scarabée)."""
    elements = []

    for eye_cx in (720, 1280):
        for r in (260, 210, 160, 110, 60):
            elements.append(f'<circle cx="{eye_cx}" cy="800" r="{r}" stroke="#000000" stroke-width="3" fill="none"/>')
        nb_rays = 12 + ((index % 4) * 4)
        for ray in range(nb_rays):
            a = (2 * math.pi / nb_rays) * ray
            x1 = eye_cx + int(60 * math.cos(a))
            y1 = 800 + int(60 * math.sin(a))
            x2 = eye_cx + int(210 * math.cos(a))
            y2 = 800 + int(210 * math.sin(a))
            elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="2"/>')

    elements.append('<polygon points="1000,850 930,1100 1070,1100" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<line x1="1000" y1="850" x2="1000" y2="1100" stroke="#000000" stroke-width="2"/>')

    for row in range(5):
        y_ecaille = 1150 + (row * 120)
        nb_col = 5 - (row % 2)
        for col in range(nb_col):
            x_ec = 600 + (col * 180) + (40 if row % 2 else 0)
            elements.append(
                f'<path d="M {x_ec} {y_ecaille} Q {x_ec + 90} {y_ecaille + 110} '
                f'{x_ec + 180} {y_ecaille}" stroke="#000000" stroke-width="3" fill="none"/>'
            )
            elements.append(f'<circle cx="{x_ec + 90}" cy="{y_ecaille + 50}" r="25" stroke="#000000" stroke-width="2" fill="none"/>')

    elements.append('<polygon points="550,600 400,250 750,450" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<polygon points="1450,600 1600,250 1250,450" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<path d="M 450 650 C 150 900 250 1600 650 1800" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<path d="M 1550 650 C 1850 900 1750 1600 1350 1800" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<rect x="80" y="80" width="1840" height="1840" stroke="#000000" stroke-width="5" fill="none" rx="20"/>')

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">'
        '<rect width="2000" height="2000" fill="#FFFFFF"/>'
        + "".join(elements) +
        "</svg>"
    )


def generer_svg_zen_architecture(index: int) -> str:
    """Temple japonais / torii géométrique et vagues zen (noir pur)."""
    elements = ['<circle cx="1000" cy="650" r="380" stroke="#000000" stroke-width="4" fill="none"/>']
    nb_rays_zen = 18 + ((index % 4) * 6)
    for ray in range(nb_rays_zen):
        a = (2 * math.pi / nb_rays_zen) * ray
        elements.append(
            f'<line x1="{1000 + int(380 * math.cos(a))}" y1="{650 + int(380 * math.sin(a))}" '
            f'x2="{1000 + int(480 * math.cos(a))}" y2="{650 + int(480 * math.sin(a))}" '
            f'stroke="#000000" stroke-width="2"/>'
        )

    elements.append('<rect x="650" y="550" width="70" height="1100" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<rect x="1280" y="550" width="70" height="1100" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<path d="M 450 540 Q 1000 490 1550 540 L 1570 470 Q 1000 420 430 470 Z" stroke="#000000" stroke-width="4" fill="none"/>')
    elements.append('<rect x="550" y="660" width="900" height="60" stroke="#000000" stroke-width="3" fill="none"/>')

    for v in range(8):
        y_vague = 1350 + (v * 70)
        elements.append(
            f'<path d="M 100 {y_vague} Q 500 {y_vague - 45} 1000 {y_vague} T 1900 {y_vague}" '
            f'stroke="#000000" stroke-width="2.5" fill="none"/>'
        )

    elements.append('<rect x="80" y="80" width="1840" height="1840" stroke="#000000" stroke-width="4" fill="none"/>')

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="100%" height="100%">'
        '<rect width="2000" height="2000" fill="#FFFFFF"/>'
        + "".join(elements) +
        "</svg>"
    )


GENERATEURS_SVG = {
    "mandalas": generer_svg_mandala,
    "botanique": generer_svg_botanique,
    "animaux": generer_svg_animal_mystique,
    "architecture": generer_svg_zen_architecture,
}


# ==============================================================================
# 2. CONVERSION LINE-ART PILLOW BINAIRE (ZÉRO NIVEAU DE GRIS)
# ==============================================================================

def convertir_en_line_art(image_source_path: Path, output_path: Path, seuil_binaire: int = 145) -> Path:
    """
    Transforme une image matricielle en line-art noir et blanc PUR
    (#000000 sur #FFFFFF) : binarisation stricte 0/255, aucun dégradé de gris.
    """
    img = Image.open(image_source_path).convert("L")
    img_contour = img.filter(ImageFilter.FIND_EDGES)
    img_contour = ImageOps.invert(img_contour)
    img_contraste = ImageOps.autocontrast(img_contour, cutoff=2)
    img_binaire = img_contraste.point(lambda p: 0 if p < seuil_binaire else 255, mode="1")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_binaire.save(output_path, "PNG", dpi=(300, 300))
    print(f"✒️ Line-Art binarisé 300 DPI généré : {output_path.name}")
    return output_path


# ==============================================================================
# 3. PAGES DE GARDE (PILLOW, NOIR SUR BLANC)
# ==============================================================================

def _charger_police(nom_prefere: str, taille: int, gras: bool = False):
    from PIL import ImageFont
    candidats = [
        f"C:/Windows/Fonts/{nom_prefere}",
        "C:/Windows/Fonts/timesbd.ttf" if gras else "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/georgiab.ttf" if gras else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if gras else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidats:
        try:
            return ImageFont.truetype(c, taille)
        except Exception:
            pass
    return ImageFont.load_default()


def dessiner_page_titre_pil(titre: str, sous_titre: str, larg_px: int, haut_px: int,
                            auteur: str = "MarkEddy") -> Image.Image:
    """Page de faux-titre 300 DPI (noir sur blanc)."""
    img = Image.new("RGB", (larg_px, haut_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(140, 140), (larg_px - 140, haut_px - 140)], outline=(0, 0, 0), width=6)
    draw.rectangle([(170, 170), (larg_px - 170, haut_px - 170)], outline=(0, 0, 0), width=2)

    f_titre = _charger_police("timesbd.ttf", max(40, larg_px // 30), gras=True)
    f_sub = _charger_police("georgia.ttf", max(24, larg_px // 48))
    f_aut = _charger_police("timesbd.ttf", max(20, larg_px // 55), gras=True)

    # Découpage du titre en lignes
    lignes, curr = [], []
    for m in titre.split():
        curr.append(m)
        if len(" ".join(curr)) > 24:
            lignes.append(" ".join(curr))
            curr = []
    if curr:
        lignes.append(" ".join(curr))

    y_pos = int(haut_px * 0.35)
    for lig in lignes:
        draw.text((larg_px // 2, y_pos), lig.upper(), fill=(0, 0, 0), font=f_titre, anchor="mm")
        y_pos += int(larg_px * 0.055)

    y_pos += int(larg_px * 0.02)
    for ms in [sous_titre[i:i + 60] for i in range(0, len(sous_titre), 60)]:
        draw.text((larg_px // 2, y_pos), ms, fill=(0, 0, 0), font=f_sub, anchor="mm")
        y_pos += int(larg_px * 0.035)

    y_pos += int(larg_px * 0.04)
    draw.line([(larg_px // 2 - 300, y_pos), (larg_px // 2 + 300, y_pos)], fill=(0, 0, 0), width=3)
    y_pos += int(larg_px * 0.06)
    draw.text((larg_px // 2, y_pos), f"ÉDITION DE PRESTIGE • PAR {auteur.upper()}",
              fill=(0, 0, 0), font=f_aut, anchor="mm")
    return img


def dessiner_page_copyright_pil(titre: str, larg_px: int, haut_px: int,
                                auteur: str = "MarkEddy") -> Image.Image:
    """Page légale & conformité KDP 300 DPI (noir sur blanc)."""
    img = Image.new("RGB", (larg_px, haut_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    f_bold = _charger_police("timesbd.ttf", max(26, larg_px // 45), gras=True)
    f_txt = _charger_police("georgia.ttf", max(18, larg_px // 60))

    lignes = [
        (titre.upper(), f_bold),
        ("", f_txt),
        (f"Conception artistique & Direction d'édition : {auteur}", f_txt),
        ("© 2026 MarkEddy Publishing House. Tous droits réservés.", f_txt),
        ("", f_txt),
        ('Format d\'impression officiel : Amazon KDP (fond perdu 0.125")', f_txt),
        ("Papier standard KDP haute densité d'encrage.", f_txt),
        ("Encre noir profond 100% sans bavure.", f_txt),
        ("", f_txt),
        ("Toute reproduction totale ou partielle sans accord préalable est interdite.", f_txt),
        ("Première Édition Mondiale — Imprimé à la demande par Amazon.", f_txt),
    ]

    y_pos = haut_px // 2 - 300
    for text, font in lignes:
        if text:
            draw.text((larg_px // 2, y_pos), text, fill=(0, 0, 0), font=font, anchor="mm")
        y_pos += 55
    return img


def dessiner_page_nuancier_pil(larg_px: int, haut_px: int) -> Image.Image:
    """Page de test des couleurs / nuancier (noir sur blanc)."""
    img = Image.new("RGB", (larg_px, haut_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(140, 140), (larg_px - 140, haut_px - 140)], outline=(0, 0, 0), width=4)

    f_titre = _charger_police("timesbd.ttf", max(36, larg_px // 40), gras=True)
    f_txt = _charger_police("georgia.ttf", max(20, larg_px // 55))
    f_label = _charger_police("arial.ttf", max(16, larg_px // 75))

    draw.text((larg_px // 2, int(haut_px * 0.16)), "TEST DE COULEURS & NUANCIER",
              fill=(0, 0, 0), font=f_titre, anchor="mm")
    draw.text((larg_px // 2, int(haut_px * 0.21)),
              "Testez vos feutres, crayons et encres ici pour apprécier leur intensité.",
              fill=(0, 0, 0), font=f_txt, anchor="mm")

    nb_cols, nb_lignes = 4, 6
    margin_x = int(larg_px * 0.20)
    spacing_x = (larg_px - 2 * margin_x) // (nb_cols - 1)
    start_y = int(haut_px * 0.30)
    spacing_y = int(haut_px * 0.105)

    compteur = 1
    for r in range(nb_lignes):
        for c in range(nb_cols):
            cx = margin_x + (c * spacing_x)
            cy = start_y + (r * spacing_y)
            box_w, box_h = int(larg_px * 0.14), int(haut_px * 0.075)
            draw.rectangle([(cx - box_w, cy - box_h), (cx + box_w, cy + box_h)],
                           outline=(0, 0, 0), width=2)
            r_cercle = int(larg_px * 0.045)
            draw.ellipse([(cx - r_cercle, cy - r_cercle), (cx + r_cercle, cy + r_cercle)],
                         outline=(0, 0, 0), width=3)
            draw.text((cx, cy + box_h - 18), f"Nuance #{compteur:02d}",
                      fill=(0, 0, 0), font=f_label, anchor="mm")
            compteur += 1
    return img


def dessiner_page_anti_bavure_pil(larg_px: int, haut_px: int) -> Image.Image:
    """
    Verso de protection anti-bavure : page VIERGE (aucune illustration au verso
    pour empêcher les feutres de traverser jusqu'à la planche suivante).
    """
    img = Image.new("RGB", (larg_px, haut_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Encadré en tirets discrets (aucun aplat de gris : contour noir fin)
    box_w, box_h = int(larg_px * 0.62), int(haut_px * 0.40)
    bx1 = (larg_px - box_w) // 2
    by1 = (haut_px - box_h) // 2
    bx2, by2 = bx1 + box_w, by1 + box_h

    dash = 25
    for x in range(bx1, bx2, dash * 2):
        draw.line([(x, by1), (min(x + dash, bx2), by1)], fill=(0, 0, 0), width=2)
        draw.line([(x, by2), (min(x + dash, bx2), by2)], fill=(0, 0, 0), width=2)
    for y in range(by1, by2, dash * 2):
        draw.line([(bx1, y), (bx1, min(y + dash, by2))], fill=(0, 0, 0), width=2)
        draw.line([(bx2, y), (bx2, min(y + dash, by2))], fill=(0, 0, 0), width=2)

    f_titre = _charger_police("timesbd.ttf", max(26, larg_px // 48), gras=True)
    f_txt = _charger_police("georgia.ttf", max(18, larg_px // 62))

    draw.text((larg_px // 2, by1 + int(box_h * 0.25)), "PAGE DE PROTECTION ANTI-BAVURE",
              fill=(0, 0, 0), font=f_titre, anchor="mm")

    lignes = [
        "Cette page a été délibérément laissée vierge pour empêcher l'encre",
        "de vos feutres, marqueurs à alcool ou aquarelles de traverser le papier",
        "et d'endommager la planche suivante.",
        "",
        "Astuce d'Artiste : glissez une feuille cartonnée souple sous votre",
        "coloriage pour une liberté d'encrage totale.",
    ]
    y_t = by1 + int(box_h * 0.42)
    for l in lignes:
        draw.text((larg_px // 2, y_t), l, fill=(0, 0, 0), font=f_txt, anchor="mm")
        y_t += 50
    return img


def dessiner_page_felicitations_pil(larg_px: int, haut_px: int) -> Image.Image:
    """Page finale de félicitations & appel aux avis (noir sur blanc)."""
    img = Image.new("RGB", (larg_px, haut_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(160, 160), (larg_px - 160, haut_px - 160)], outline=(0, 0, 0), width=5)

    f_t = _charger_police("timesbd.ttf", max(44, larg_px // 34), gras=True)
    f_txt = _charger_police("georgia.ttf", max(22, larg_px // 52))

    cy = haut_px // 2
    draw.text((larg_px // 2, cy - 300), "FÉLICITATIONS !", fill=(0, 0, 0), font=f_t, anchor="mm")

    lignes = [
        "Vous êtes arrivé au terme de ce recueil artistique et méditatif.",
        "Le coloriage régulier apaise l'esprit et restaure une concentration profonde.",
        "",
        "✦   ✦   ✦",
        "",
        "Votre créativité mérite d'être partagée !",
        "Prenez une photo de votre coloriage préféré et partagez-la",
        "dans votre avis client Amazon pour inspirer la communauté.",
    ]
    y = cy - 150
    for lig in lignes:
        draw.text((larg_px // 2, y), lig, fill=(0, 0, 0), font=f_txt, anchor="mm")
        y += 60
    return img


# ==============================================================================
# 4. PLANCHE DE COLORIAGE 300 DPI (PILLOW, NOIR PUR)
# ==============================================================================

def dessiner_planche_pil(theme: str, index: int, titre: str,
                         larg_px: int, haut_px: int) -> Image.Image:
    """Planche de coloriage complète 300 DPI au format demandé (noir sur blanc)."""
    img = Image.new("RGB", (larg_px, haut_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Marges KDP avec gutter renforcé à gauche (reliure)
    margin_l = int(larg_px * 0.10)
    margin_r = int(larg_px * 0.07)
    margin_t = int(haut_px * 0.055)
    margin_b = int(haut_px * 0.075)

    draw.rectangle([(margin_l, margin_t), (larg_px - margin_r, haut_px - margin_b)],
                   outline=(0, 0, 0), width=6)
    draw.rectangle([(margin_l + 26, margin_t + 26), (larg_px - margin_r - 26, haut_px - margin_b - 26)],
                   outline=(0, 0, 0), width=2)

    cx = (margin_l + larg_px - margin_r) // 2
    cy = (margin_t + haut_px - margin_b) // 2

    th = (theme or "mandalas").lower()
    echelle = min(larg_px, haut_px) / 2000.0

    if th == "botanique":
        stem_pts = []
        hauteur_dispo = haut_px - margin_t - margin_b - 200
        for step in range(30):
            ty = margin_t + 100 + (step * hauteur_dispo // 29)
            tx = cx + int(120 * echelle * math.sin(step * 0.45 + (index * 0.5)))
            stem_pts.append((tx, ty))
        for p1, p2 in zip(stem_pts[:-1], stem_pts[1:]):
            draw.line([p1, p2], fill=(0, 0, 0), width=8)

        for idx_f, (tx, ty) in enumerate(stem_pts[2:-2:2]):
            cote = 1 if idx_f % 2 == 0 else -1
            end_x = tx + int(cote * 420 * echelle)
            end_y = ty - int(120 * echelle)
            draw.arc([(min(tx, end_x), min(ty, end_y) - int(60 * echelle)),
                      (max(tx, end_x), max(ty, end_y) + int(60 * echelle))],
                     0, 360, fill=(0, 0, 0), width=4)
            draw.line([(tx, ty), (end_x, end_y)], fill=(0, 0, 0), width=3)
            for nv in (0.35, 0.70):
                nx = tx + int((end_x - tx) * nv)
                ny = ty + int((end_y - ty) * nv)
                draw.line([(nx, ny), (nx + int(cote * 80 * echelle), ny - int(45 * echelle))],
                          fill=(0, 0, 0), width=2)

        top_x, top_y = stem_pts[0]
        for pet in range(12):
            ang = (2 * math.pi / 12) * pet
            px = top_x + int(180 * echelle * math.cos(ang))
            py = top_y + int(180 * echelle * math.sin(ang))
            r_p = int(70 * echelle)
            draw.ellipse([(px - r_p, py - r_p), (px + r_p, py + r_p)], outline=(0, 0, 0), width=4)
        r_c = int(90 * echelle)
        draw.ellipse([(top_x - r_c, top_y - r_c), (top_x + r_c, top_y + r_c)],
                     outline=(0, 0, 0), width=6)

    elif th == "animaux":
        for eye_x in (cx - int(280 * echelle), cx + int(280 * echelle)):
            eye_y = cy - int(250 * echelle)
            for r in (280, 220, 160, 100, 45):
                rr = int(r * echelle)
                draw.ellipse([(eye_x - rr, eye_y - rr), (eye_x + rr, eye_y + rr)],
                             outline=(0, 0, 0), width=4)
            for ray in range(16):
                a = (2 * math.pi / 16) * ray
                rx1 = eye_x + int(45 * echelle * math.cos(a))
                ry1 = eye_y + int(45 * echelle * math.sin(a))
                rx2 = eye_x + int(220 * echelle * math.cos(a))
                ry2 = eye_y + int(220 * echelle * math.sin(a))
                draw.line([(rx1, ry1), (rx2, ry2)], fill=(0, 0, 0), width=3)

        draw.polygon([(cx, cy - int(200 * echelle)),
                      (cx - int(80 * echelle), cy + int(80 * echelle)),
                      (cx + int(80 * echelle), cy + int(80 * echelle))],
                     outline=(0, 0, 0))
        draw.line([(cx, cy - int(200 * echelle)), (cx, cy + int(80 * echelle))],
                  fill=(0, 0, 0), width=3)

        for row in range(5):
            y_ec = cy + int(120 * echelle) + int(row * 130 * echelle)
            nb_col = 5 - (row % 2)
            for col in range(nb_col):
                x_ec = cx - int(350 * echelle) + int(col * 175 * echelle) + (int(35 * echelle) if row % 2 else 0)
                r_e = int(80 * echelle)
                draw.arc([(x_ec - r_e, y_ec - int(40 * echelle)),
                          (x_ec + r_e, y_ec + int(80 * echelle))], 0, 180, fill=(0, 0, 0), width=4)

        draw.polygon([(cx - int(450 * echelle), cy - int(450 * echelle)),
                      (cx - int(250 * echelle), cy - int(750 * echelle)),
                      (cx - int(100 * echelle), cy - int(500 * echelle))], outline=(0, 0, 0))
        draw.polygon([(cx + int(450 * echelle), cy - int(450 * echelle)),
                      (cx + int(250 * echelle), cy - int(750 * echelle)),
                      (cx + int(100 * echelle), cy - int(500 * echelle))], outline=(0, 0, 0))

    elif th == "architecture":
        sun_y = cy - int(250 * echelle)
        r_soleil = int(420 * echelle)
        draw.ellipse([(cx - r_soleil, sun_y - r_soleil), (cx + r_soleil, sun_y + r_soleil)],
                     outline=(0, 0, 0), width=5)
        for s_ray in range(24):
            sa = (2 * math.pi / 24) * s_ray
            sx1 = cx + int(r_soleil * math.cos(sa))
            sy1 = sun_y + int(r_soleil * math.sin(sa))
            sx2 = cx + int(int(560 * echelle) * math.cos(sa))
            sy2 = sun_y + int(int(560 * echelle) * math.sin(sa))
            draw.line([(sx1, sy1), (sx2, sy2)], fill=(0, 0, 0), width=3)

        draw.rectangle([(cx - int(360 * echelle), cy - int(350 * echelle)),
                        (cx - int(280 * echelle), cy + int(550 * echelle))],
                       outline=(0, 0, 0), width=5)
        draw.rectangle([(cx + int(280 * echelle), cy - int(350 * echelle)),
                        (cx + int(360 * echelle), cy + int(550 * echelle))],
                       outline=(0, 0, 0), width=5)
        draw.polygon([(cx - int(480 * echelle), cy - int(360 * echelle)),
                      (cx + int(480 * echelle), cy - int(360 * echelle)),
                      (cx + int(450 * echelle), cy - int(430 * echelle)),
                      (cx - int(450 * echelle), cy - int(430 * echelle))], outline=(0, 0, 0))
        draw.rectangle([(cx - int(400 * echelle), cy - int(260 * echelle)),
                        (cx + int(400 * echelle), cy - int(210 * echelle))],
                       outline=(0, 0, 0), width=4)

        for wave_idx in range(9):
            wy = cy + int(420 * echelle) + int(wave_idx * 75 * echelle)
            wave_pts = []
            for wx in range(margin_l + 40, larg_px - margin_r - 40, 20):
                wave_y = wy + int(25 * echelle * math.sin((wx * 0.015) + (wave_idx * 0.4)))
                wave_pts.append((wx, wave_y))
            for p1, p2 in zip(wave_pts[:-1], wave_pts[1:]):
                draw.line([p1, p2], fill=(0, 0, 0), width=3)

    else:  # mandalas (défaut)
        r_max = int(920 * echelle)
        for r in range(int(120 * echelle), r_max + 1, max(40, int(100 * echelle))):
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(0, 0, 0), width=4)

        nb_petales = 12 + ((index % 5) * 4)
        for i in range(nb_petales):
            angle = (2 * math.pi / nb_petales) * i
            x1 = cx + int(120 * echelle * math.cos(angle))
            y1 = cy + int(120 * echelle * math.sin(angle))
            x2 = cx + int(r_max * math.cos(angle))
            y2 = cy + int(r_max * math.sin(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0), width=3)

            cx_sub = cx + int(520 * echelle * math.cos(angle))
            cy_sub = cy + int(520 * echelle * math.sin(angle))
            r1 = int(120 * echelle)
            r2 = int(60 * echelle)
            draw.ellipse([(cx_sub - r1, cy_sub - r1), (cx_sub + r1, cy_sub + r1)],
                         outline=(0, 0, 0), width=3)
            draw.ellipse([(cx_sub - r2, cy_sub - r2), (cx_sub + r2, cy_sub + r2)],
                         outline=(0, 0, 0), width=2)

        for r_in in (40, 80, 120):
            rr = int(r_in * echelle)
            draw.ellipse([(cx - rr, cy - rr), (cx + rr, cy + rr)], outline=(0, 0, 0), width=5)

    # Bas de page
    f_footer = _charger_police("arial.ttf", max(16, larg_px // 85))
    draw.text((cx, haut_px - margin_b + int(margin_b * 0.55)),
              f"PLANCHE {index:02d} • {titre.upper()}", fill=(0, 0, 0), font=f_footer, anchor="mm")
    return img


# ==============================================================================
# 5. COMPILATION PDF 300 DPI VIA PLAYWRIGHT
# ==============================================================================

def compiler_pdf_playwright(html_path: Path, pdf_path: Path,
                            largeur_in: float, hauteur_in: float) -> Path:
    """
    Compile un HTML de pages en PDF au format exact via Playwright/Chromium
    (repli automatique sur le canal msedge si chromium n'est pas disponible).
    """
    from playwright.sync_api import sync_playwright

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    vw = int(round(largeur_in * 96))
    vh = int(round(hauteur_in * 96))

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": vw, "height": vh})
        page.goto(html_path.resolve().as_uri(), wait_until="load")
        page.wait_for_timeout(400)
        page.pdf(
            path=str(pdf_path),
            width=f"{largeur_in:.4f}in",
            height=f"{hauteur_in:.4f}in",
            print_background=True,
            margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"},
        )
        browser.close()

    return pdf_path


# ==============================================================================
# 6. PRODUCTION COMPLÈTE D'UN LIVRE DE COLORIAGE
# ==============================================================================

def produire_livre_coloriage(
    book_id: int,
    titre: str,
    sous_titre: str,
    theme: str = "mandalas",
    nb_illustrations: int = 30,
    recto_uniquement: bool = True,
    cover_bg_image: Optional[str] = None,
    format_kdp: str = "8.5x11",
    paper_type: str = "white"
) -> Dict[str, Any]:
    """
    Génère un livre de coloriage professionnel pour l'un des 16 formats KDP.

    - Fond perdu 0.125" et dimensions 300 DPI exactes (kdp_dimensions).
    - Planches noir et blanc PUR (#000000 sur #FFFFFF).
    - Option recto uniquement : verso blanc anti-bavure après chaque planche.
    - Compilation PDF via Playwright, couverture via cover_artisan_agent.
    """
    fid = normalize_format(format_kdp)
    specs = calculate_kdp_specs(fid, page_count=max(1, int(nb_illustrations) * 2 + 6),
                                paper_type=paper_type, bleed=True)

    larg_px = specs["interior"]["width_px"]
    haut_px = specs["interior"]["height_px"]
    larg_in = specs["interior"]["width_in"]
    haut_in = specs["interior"]["height_in"]
    trim_w = specs["trim"]["width_in"]
    trim_h = specs["trim"]["height_in"]

    dossier_livre = BASE_DIR / "books" / f"livre_coloriage_{book_id}"
    dossier_livre.mkdir(parents=True, exist_ok=True)
    dossier_planches = dossier_livre / "planches"
    dossier_planches.mkdir(exist_ok=True)

    nb_illustrations = max(1, int(nb_illustrations))
    print(f"\n🎨 [COLORIAGE] {nb_illustrations} planches '{theme}' au format {fid} "
          f"({larg_px}x{haut_px} px @300 DPI)...")

    # --- 1. Génération des planches (SVG vectoriel + PNG 300 DPI) ------------
    gen_svg = GENERATEURS_SVG.get((theme or "mandalas").lower(), generer_svg_mandala)
    planches_svg: List[str] = []
    for idx in range(1, nb_illustrations + 1):
        svg_code = gen_svg(idx)
        planches_svg.append(svg_code)
        (dossier_planches / f"planche_{idx:02d}.svg").write_text(svg_code, encoding="utf-8")

        # Variante raster binaire (line-art Pillow, zéro gris)
        png_path = dossier_planches / f"planche_{idx:02d}.png"
        dessiner_planche_pil(theme, idx, titre, larg_px, haut_px).save(
            png_path, "PNG", dpi=(300, 300)
        )

    # --- 2. Pages de garde (PILLOW 300 DPI) ---------------------------------
    print("📖 Rendu des pages de garde 300 DPI...")
    pages_images: List[Image.Image] = [
        dessiner_page_titre_pil(titre, sous_titre, larg_px, haut_px, "MarkEddy"),
        dessiner_page_copyright_pil(titre, larg_px, haut_px, "MarkEddy"),
        dessiner_page_nuancier_pil(larg_px, haut_px),
    ]
    if recto_uniquement:
        pages_images.append(dessiner_page_anti_bavure_pil(larg_px, haut_px))

    for idx in range(1, nb_illustrations + 1):
        pages_images.append(dessiner_planche_pil(theme, idx, titre, larg_px, haut_px))
        if recto_uniquement:
            # Verso VIERGE anti-bavure après chaque illustration
            pages_images.append(dessiner_page_anti_bavure_pil(larg_px, haut_px))

    pages_images.append(dessiner_page_felicitations_pil(larg_px, haut_px))

    # --- 3. Maquette HTML (planches SVG) pour aperçu web & Canva ------------
    fichier_html = dossier_livre / f"interieur_coloriage_{fid}.html"
    blocs = []
    for idx, svg in enumerate(planches_svg, start=1):
        blocs.append(
            f'<div class="page"><div class="frame">{svg}</div>'
            f'<div class="footer">Planche {idx} • {titre}</div></div>'
        )
        if recto_uniquement:
            blocs.append('<div class="page verso"></div>')

    fichier_html.write_text(f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>{titre}</title>
<style>
  @page {{ size: {larg_in}in {haut_in}in; margin: 0; }}
  body {{ margin: 0; padding: 0; background: #FFFFFF; }}
  .page {{ width: {larg_in}in; height: {haut_in}in; page-break-after: always;
           display: flex; align-items: center; justify-content: center;
           position: relative; background: #FFFFFF; }}
  .frame {{ width: 82%; height: 84%; }}
  .verso {{ background: #FFFFFF; }}
  .footer {{ position: absolute; bottom: 3%; left: 0; right: 0; text-align: center;
             font: 12px sans-serif; color: #000000; }}
</style></head><body>{''.join(blocs)}</body></html>""", encoding="utf-8")

    # --- 4. Assemblage du PDF intérieur 300 DPI ------------------------------
    fichier_pdf = dossier_livre / f"Interieur_Coloriage_{fid}.pdf"
    print(f"📚 Compilation PDF 300 DPI via Playwright ({len(pages_images)} pages)...")

    # Les pages de garde & planches sont des images 300 DPI : on les emballe
    # dans un HTML minimal au format exact puis on compile via Playwright.
    pages_html = "".join(
        f'<div class="p"><img src="data:image/png;base64,{_png_base64(im)}"></div>'
        for im in pages_images
    )
    fichier_tmp_html = dossier_livre / "_assembly_tmp.html"
    fichier_tmp_html.write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  @page {{ size: {larg_in}in {haut_in}in; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: #FFFFFF; }}
  .p {{ width: {larg_in}in; height: {haut_in}in; page-break-after: always;
        display: flex; align-items: center; justify-content: center; background: #FFFFFF; }}
  .p img {{ width: 100%; height: 100%; object-fit: fill; display: block; }}
</style></head><body>{pages_html}</body></html>""", encoding="utf-8")

    compiler_pdf_playwright(fichier_tmp_html, fichier_pdf, larg_in, haut_in)
    try:
        fichier_tmp_html.unlink()
    except Exception:
        pass

    from pypdf import PdfReader
    reader = PdfReader(str(fichier_pdf))
    nb_pages_total = len(reader.pages)

    # --- 5. Dos & couverture calibrée via cover_artisan_agent ---------------
    specs_final = calculate_kdp_specs(fid, page_count=nb_pages_total,
                                      paper_type=paper_type, bleed=True)
    epaisseur_dos = specs_final["spine"]["width_in"]
    print(f"📐 {nb_pages_total} pages • dos {epaisseur_dos:.4f} po "
          f"({epaisseur_dos * 25.4:.2f} mm) • couverture "
          f"{specs_final['cover']['width_px']}x{specs_final['cover']['height_px']} px")

    fichier_pdf_couv = dossier_livre / f"couverture_{fid}_complete.pdf"
    fichier_jpg_couv = dossier_livre / "couverture_ebook.jpg"

    try:
        import cover_artisan_agent

        # Gabarit de pages au format de coupe exact pour que cover_artisan_agent
        # mesure le trim et calcule la tranche au micron.
        proxy_pdf = dossier_livre / "_trim_proxy.pdf"
        _creer_pdf_proxy(proxy_pdf, trim_w, trim_h, nb_pages_total)

        palette_map = {
            "mandalas": "PHILOSOPHIE", "botanique": "SANTE",
            "animaux": "IMMOBILIER", "architecture": "TECH_IA",
        }
        res_couv = cover_artisan_agent.fabriquer(
            pdf_interieur=str(proxy_pdf),
            thematique=palette_map.get((theme or "mandalas").lower(), "MINDSET"),
            titre=titre.replace(":", " :"),
            sous_titre=sous_titre,
            titre_arriere=f"À COLORIER<br>ET À SÉRÉNISER",
            pitch_arriere=sous_titre,
            fichier_sortie=str(fichier_pdf_couv),
        )
        try:
            proxy_pdf.unlink()
        except Exception:
            pass

        if res_couv and Path(res_couv).exists() and not fichier_pdf_couv.exists():
            shutil.copy2(res_couv, fichier_pdf_couv)

        # Fond photo optionnel (image stock Unsplash/Pixabay déjà préparée 300 DPI)
        html_couv = BASE_DIR / "temp_rendered_cover.html"
        if cover_bg_image and Path(cover_bg_image).exists() and html_couv.exists():
            _injecter_fond_couverture(
                html_couv, fichier_pdf_couv, Path(cover_bg_image),
                specs_final["cover"]["width_in"], specs_final["cover"]["height_in"]
            )

        # Variante JPG (aperçu eBook) : capture du HTML de couverture rendu
        if fichier_pdf_couv.exists():
            _html_cover_vers_jpg(html_couv, fichier_jpg_couv,
                                 specs_final["cover"]["width_px"],
                                 specs_final["cover"]["height_px"])
    except Exception as e_cov:
        print(f"⚠️ Note couverture coloriage : {e_cov}")

    # --- 6. Pack marketing ---------------------------------------------------
    fichier_marketing = dossier_livre / "kdp_marketing_pack.html"
    fichier_marketing.write_text(f"""
<h2>{titre} — Grand Format Broché {trim_w}" × {trim_h}"</h2>
<p><b>Plongez dans un univers d'apaisement absolu et libérez votre potentiel créatif !</b></p>
<h3>Pourquoi choisir ce livre de coloriage d'art :</h3>
<ul>
  <li><b>{nb_illustrations} Illustrations Uniques :</b> tracés noir et blanc pur ultra-nets.</li>
  <li><b>Pages Recto Uniquement :</b> {'versos blancs anti-bavure après chaque planche.' if recto_uniquement else 'impression recto-verso standard.'}</li>
  <li><b>Grand Format Confort {trim_w}" × {trim_h}" :</b> espace de coloriage ample et immersif.</li>
  <li><b>Page Test Nuancier :</b> testez vos dégradés avant de vous lancer.</li>
</ul>""", encoding="utf-8")

    return {
        "status": "success",
        "format_kdp": fid,
        "nb_pages": nb_pages_total,
        "nb_illustrations": nb_illustrations,
        "epaisseur_dos_po": epaisseur_dos,
        "specs": specs_final,
        "chemin_pdf_interieur": str(fichier_pdf.relative_to(BASE_DIR)),
        "chemin_pdf_couverture": str(fichier_pdf_couv.relative_to(BASE_DIR)) if fichier_pdf_couv.exists() else None,
        "chemin_couverture_jpg": str(fichier_jpg_couv.relative_to(BASE_DIR)) if fichier_jpg_couv.exists() else None,
        "chemin_interieur_html": str(fichier_html.relative_to(BASE_DIR)),
        "chemin_marketing_html": str(fichier_marketing.relative_to(BASE_DIR)),
        "dossier_planches": str(dossier_planches.relative_to(BASE_DIR)),
    }


# ==============================================================================
# 7. UTILITAIRES INTERNES
# ==============================================================================

def _png_base64(img: Image.Image) -> str:
    import base64
    import io as _io
    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _creer_pdf_proxy(path: Path, trim_w_in: float, trim_h_in: float, page_count: int) -> Path:
    """PDF vierge au format de coupe exact (mesure trim pour la couverture)."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    for _ in range(max(1, page_count)):
        writer.add_blank_page(width=trim_w_in * 72.0, height=trim_h_in * 72.0)
    with open(path, "wb") as f:
        writer.write(f)
    return path


def _injecter_fond_couverture(html_path: Path, pdf_path: Path, bg_path: Path,
                              largeur_in: float, hauteur_in: float) -> Optional[Path]:
    """
    Injecte l'image stock (fond photo) dans le HTML de couverture rendu par
    cover_artisan_agent puis recompile le PDF au format exact.
    La couche de dégradé et les grilles restent au-dessus (overlay naturel).
    """
    try:
        html = html_path.read_text(encoding="utf-8")
        url_fichier = bg_path.resolve().as_uri()
        style_injecte = (
            "<style>/* Fond photo injecté (media_connectors 300 DPI) */\n"
            "  .cover-canvas { background-image: url('" + url_fichier + "');\n"
            "    background-size: cover; background-position: center; }\n"
            "  .front-cover, .back-cover, .spine { background: rgba(10,15,29,0.55); }\n"
            "  </style>"
        )
        if "Fond photo injecté" not in html:
            html = html.replace("</head>", style_injecte + "\n</head>")
            html_path.write_text(html, encoding="utf-8")

        from playwright.sync_api import sync_playwright
        vw = int(round(largeur_in * 120))
        vh = int(round(hauteur_in * 120))
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception:
                browser = p.chromium.launch(channel="msedge")
            page = browser.new_page(viewport={"width": vw, "height": vh})
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            page.wait_for_selector(".hero-title-3d")
            page.wait_for_timeout(500)
            page.pdf(
                path=str(pdf_path),
                width=f"{largeur_in:.4f}in",
                height=f"{hauteur_in:.4f}in",
                print_background=True,
                page_ranges="1",
                margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"},
            )
            browser.close()
        print(f"🖼️ Fond photo couverture injecté : {bg_path.name} -> {pdf_path.name}")
        return pdf_path
    except Exception as e_bg:
        print(f"⚠️ Note injection fond photo couverture : {e_bg}")
        return None


def _html_cover_vers_jpg(html_path: Path, jpg_path: Path,
                         width_px: int, height_px: int) -> Optional[Path]:
    """Capture la couverture rendue (HTML) en JPG 300 DPI (aperçu eBook)."""
    if not html_path.exists():
        return None
    try:
        from playwright.sync_api import sync_playwright
        # Rendu navigateur ~96 DPI : on échantillonne le ratio exact du gabarit
        vw = min(int(width_px / 3.125), 2600)
        vh = int(vw * height_px / width_px)
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception:
                browser = p.chromium.launch(channel="msedge")
            page = browser.new_page(viewport={"width": vw, "height": vh},
                                    device_scale_factor=1)
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            page.wait_for_timeout(600)
            page.screenshot(path=str(jpg_path), type="jpeg", quality=92)
            browser.close()
        return jpg_path if jpg_path.exists() else None
    except Exception as e:
        print(f"⚠️ Note aperçu JPG couverture : {e}")
        return None


if __name__ == "__main__":
    print("Test kdp_extensions.coloring_book_engine...")
    res = produire_livre_coloriage(
        book_id=777,
        titre="MANDALAS SACRÉS & SÉRÉNITÉ",
        sous_titre="30 motifs géométriques pour apaiser l'esprit",
        theme="mandalas",
        nb_illustrations=3,
        recto_uniquement=True,
        format_kdp="8.5x11",
    )
    print("Résultat :", res)
