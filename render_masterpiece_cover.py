# -*- coding: utf-8 -*-
"""
render_masterpiece_cover.py - Moteur de Couverture Haute Couture KDP 300 DPI
Intègre :
1. Revêtement écaillé cuir de crocodile de luxe en bleu nuit mat profond
2. Illustration centrale 100% symétrique avec partage de lumière positive et architecture sacrée
3. Typographie d'élite à brillance or impérial et platine/argent éclatant
4. Repositionnement aéré du sous-titre de description (dégagé du filet doré)
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

def generate_crocodile_leather(width: int, height: int) -> Image.Image:
    """Génère un cuir de crocodile de haute maroquinerie en bleu nuit mat profond."""
    base = Image.new("RGB", (width, height), "#080E1C")
    draw = ImageDraw.Draw(base)

    tile_w = 130
    tile_h = 90

    y = 0
    row = 0
    while y < height + tile_h:
        rh = tile_h + ((row * 7) % 16)
        row_shift = (row % 2) * (tile_w // 2)
        x = -row_shift
        col = 0
        while x < width + tile_w:
            cw = tile_w + ((col * 11) % 20)
            pad = 5
            x0, y0 = x + pad, y + pad
            x1, y1 = x + cw - pad, y + rh - pad

            # Base de couleur des dômes d'écailles : nuances bleu nuit mat
            v = 11 + ((row * 4 + col * 7) % 9)
            scale_fill = (v, v + 7, v + 24)
            seam_color = (3, 5, 11)

            # Écaille galbée aux angles adoucis
            draw.rounded_rectangle([x0, y0, x1, y1], radius=15, fill=scale_fill, outline=seam_color, width=4)

            # Liseré de relief spéculaire (biseau supérieur gauche)
            hl = (v + 14, v + 22, v + 44)
            draw.arc([x0 + 3, y0 + 3, x1 - 3, y1 - 3], start=180, end=270, fill=hl, width=2)

            x += cw
            col += 1
        y += rh
        row += 1

    # Très léger adoucissement pour un velouté de cuir mat naturel
    base = base.filter(ImageFilter.GaussianBlur(radius=0.6))
    return base

def render_metallic_text(text: str, font: ImageFont.FreeTypeFont, mode: str = "gold"):
    """Génère un texte aux reflets métalliques or ou argent avec biseau et ombre portée."""
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), text, font=font)
    w = max(10, bbox[2] - bbox[0] + 30)
    h = max(10, bbox[3] - bbox[1] + 30)
    ox, oy = -bbox[0] + 15, -bbox[1] + 15

    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    dm.text((ox, oy), text, fill=255, font=font)

    grad = Image.new("RGBA", (w, h))
    for y in range(h):
        ratio = y / max(1, h)
        if mode == "gold":
            # Dégradé Or Impérial brillant : champagne éclatant -> or chaud -> bronze riche
            if ratio < 0.30:
                r = int(255 - ratio * 30)
                g = int(248 - ratio * 50)
                b = int(195 - ratio * 160)
            elif ratio < 0.70:
                r = int(246 - (ratio - 0.30) * 60)
                g = int(200 - (ratio - 0.30) * 110)
                b = int(75 - (ratio - 0.30) * 80)
            else:
                r = int(222 - (ratio - 0.70) * 80)
                g = int(156 - (ratio - 0.70) * 90)
                b = int(43 - (ratio - 0.70) * 35)
        else:
            # Dégradé Platine / Argent étincelant : blanc pur -> argent vif -> platine satiné
            if ratio < 0.35:
                v = int(255 - ratio * 20)
                r, g, b = v, v, v
            elif ratio < 0.75:
                v = int(248 - (ratio - 0.35) * 55)
                r, g, b = v, v + 2, v + 8
            else:
                v = int(226 - (ratio - 0.75) * 90)
                r, g, b = v, v + 4, v + 14

        for x in range(w):
            grad.putpixel((x, y), (r, g, b, 255))

    # Application du masque sur le dégradé
    res = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    res.paste(grad, (0, 0), mask)

    # Ombre portée douce pour l'effet de relief 3D
    shadow = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    s_mask = Image.new("L", (w + 14, h + 14), 0)
    s_mask.paste(mask, (7, 8))
    s_mask = s_mask.filter(ImageFilter.GaussianBlur(radius=4))
    s_fill = Image.new("RGBA", (w + 14, h + 14), (2, 4, 8, 220))
    shadow.paste(s_fill, (0, 0), s_mask)

    final = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    final.paste(shadow, (0, 0), shadow)
    final.paste(res, (7, 6), res)
    return final, (w, h)

def paste_centered(canvas: Image.Image, text_img: Image.Image, center_x: int, center_y: int):
    """Colle une image de texte centrée sur les coordonnées spécifiées."""
    x = center_x - text_img.width // 2
    y = center_y - text_img.height // 2
    canvas.paste(text_img, (x, y), text_img)

def creer_couverture_chef_d_oeuvre(
    nb_pages: int = None,
    largeur_page: float = 6.0,
    hauteur_page: float = 9.0,
    titre: str = "L'ARCHITECTE FINANCIER",
    sous_titre: str = "Le Système Automatisé pour Maîtriser son Budget sans Privation, Éliminer ses Dettes et Bâtir un Patrimoine Passif avec un Salaire Ordinaire",
    auteur: str = "MarkEddy",
    bg_image_path: str = "assets/larchitecte_financier_cover_bg.jpg"
):
    if nb_pages is None:
        try:
            import pypdf
            reader = pypdf.PdfReader("livre_kdp_interieur.pdf")
            nb_pages = len(reader.pages)
        except Exception:
            nb_pages = 190

    dpi = 300
    bleed_in = 0.125
    trim_w_in = float(largeur_page)
    trim_h_in = float(hauteur_page)
    spine_in = round(nb_pages * 0.002252, 4)

    total_w_in = bleed_in + trim_w_in + spine_in + trim_w_in + bleed_in
    total_h_in = bleed_in + trim_h_in + bleed_in

    width_px = int(round(total_w_in * dpi))
    height_px = int(round(total_h_in * dpi))

    bleed_px = int(round(bleed_in * dpi))
    trim_w_px = int(round(trim_w_in * dpi))
    trim_h_px = int(round(trim_h_in * dpi))
    spine_px = int(round(spine_in * dpi))

    plat4_left = bleed_px
    plat4_right = plat4_left + trim_w_px

    spine_left = plat4_right
    spine_right = spine_left + spine_px

    plat1_left = spine_right
    plat1_right = plat1_left + trim_w_px

    print(f"📐 Dimensions globales 300 DPI : {width_px} x {height_px} px")
    print(f"   Tranche (dos) calculée pour {nb_pages} pages : {spine_in:.4f} po ({spine_in * 25.4:.2f} mm)")

    # 1. Canvas intégral en cuir de crocodile de luxe bleu nuit mat
    print("🐊 Génération du revêtement écaillé cuir de crocodile bleu nuit mat...")
    img = generate_crocodile_leather(width_px, height_px)
    draw = ImageDraw.Draw(img)

    # 2. Intégration de l'illustration centrale 100% symétrique avec partage de lumière positive
    if bg_image_path and Path(bg_image_path).exists():
        try:
            bg_art = Image.open(bg_image_path).convert("RGBA")
            w_art = trim_w_px + bleed_px
            bg_art_fit = ImageOps.fit(bg_art, (w_art, height_px), method=Image.Resampling.LANCZOS)

            # Masque de fondu vertical d'orfèvrerie :
            # - Dégage le haut (y < 720) pour le titre en or/argent pur
            # - Révèle pleinement le cœur lumineux, les piliers symétriques et l'auréole dorée (y = 720 à 2050)
            # - Assombrit en douceur le bas (y > 2050) pour le nom d'auteur
            mask = Image.new("L", (w_art, height_px), color=0)
            mask_draw = ImageDraw.Draw(mask)

            for y in range(height_px):
                if y < 720:
                    alpha = int(25 + (y / 720) * 165)
                elif y < 2050:
                    alpha = 240
                else:
                    factor = (height_px - y) / (height_px - 2050)
                    alpha = int(45 + factor * 195)
                mask_draw.line([(0, y), (w_art, y)], fill=max(0, min(255, alpha)))

            img_rgba = img.convert("RGBA")
            img_rgba.paste(bg_art_fit, (plat1_left, 0), mask)

            # Ajout d'un halo de lumière radiale dorée au cœur de l'illustration (charge positive rayonnante)
            halo = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))
            halo_draw = ImageDraw.Draw(halo)
            plat1_center_x = (plat1_left + plat1_right) // 2
            halo_center_y = 1380
            halo_r = 450
            for r in range(halo_r, 0, -15):
                alpha_h = int(35 * (1.0 - r / halo_r))
                halo_draw.ellipse(
                    [plat1_center_x - r, halo_center_y - r, plat1_center_x + r, halo_center_y + r],
                    fill=(255, 215, 0, alpha_h)
                )
            halo = halo.filter(ImageFilter.GaussianBlur(radius=30))
            img_rgba = Image.alpha_composite(img_rgba, halo)

            img = img_rgba.convert("RGB")
            draw = ImageDraw.Draw(img)
            print("✔ Illustration 3D symétrique et halo de lumière dorée intégrés.")
        except Exception as e_art:
            print(f"⚠️ Erreur intégration artwork : {e_art}")

    # 3. Tranche / Dos (Ardoise dense surmontée de filets dorés)
    draw.rectangle([spine_left, 0, spine_right, height_px], fill="#0A1122")
    draw.line([(spine_left, 0), (spine_left, height_px)], fill="#D4AF37", width=3)
    draw.line([(spine_right, 0), (spine_right, height_px)], fill="#D4AF37", width=3)

    # Chargement des polices d'édition
    try:
        font_titre = ImageFont.truetype("timesbd.ttf", 94)
        font_sub = ImageFont.truetype("georgia.ttf", 34)
        font_badge = ImageFont.truetype("arialbd.ttf", 26)
        font_auteur = ImageFont.truetype("timesbd.ttf", 62)
        font_dos = ImageFont.truetype("arialbd.ttf", 24)

        font_back_h1 = ImageFont.truetype("timesbd.ttf", 46)
        font_back_corps = ImageFont.truetype("georgia.ttf", 29)
        font_back_bullet = ImageFont.truetype("georgia.ttf", 28)
        font_back_citation = ImageFont.truetype("georgiab.ttf", 29)
    except Exception:
        font_titre = ImageFont.load_default()
        font_sub = font_titre
        font_badge = font_titre
        font_auteur = font_titre
        font_dos = font_titre
        font_back_h1 = font_titre
        font_back_corps = font_titre
        font_back_bullet = font_titre
        font_back_citation = font_titre

    # =========================================================================
    # FACE AVANT (PLAT 1)
    # =========================================================================
    plat1_center_x = (plat1_left + plat1_right) // 2
    img_rgba = img.convert("RGBA")

    # Double cadre ornemental d'orfèvrerie
    marge_cadre_ext = int(0.35 * dpi)
    marge_cadre_int = int(0.40 * dpi)
    draw_rgba = ImageDraw.Draw(img_rgba)
    draw_rgba.rectangle(
        [plat1_left + marge_cadre_ext, bleed_px + marge_cadre_ext, plat1_right - marge_cadre_ext, height_px - bleed_px - marge_cadre_ext],
        outline="#D4AF37",
        width=2
    )
    draw_rgba.rectangle(
        [plat1_left + marge_cadre_int, bleed_px + marge_cadre_int, plat1_right - marge_cadre_int, height_px - bleed_px - marge_cadre_int],
        outline="#64748B",
        width=1
    )

    # 1. Badge de tête : Or impérial étincelant
    badge_y = bleed_px + int(0.75 * dpi)
    badge_img, _ = render_metallic_text("— ÉDITION MASTERCLASS 2026 —", font_badge, mode="gold")
    paste_centered(img_rgba, badge_img, plat1_center_x, badge_y)

    # 2. Titre Principal à haute brillance financière :
    # "L'ARCHITECTE" (Argent pur / Platine) + "FINANCIER" (Or Impérial éclatant)
    titre_y1 = badge_y + 130
    titre_y2 = titre_y1 + 105
    t1_img, _ = render_metallic_text("L'ARCHITECTE", font_titre, mode="silver")
    t2_img, _ = render_metallic_text("FINANCIER", font_titre, mode="gold")
    paste_centered(img_rgba, t1_img, plat1_center_x, titre_y1)
    paste_centered(img_rgba, t2_img, plat1_center_x, titre_y2)

    # 3. Filet doré avec losange central d'orfèvre
    sep_y = titre_y2 + 80
    draw_rgba.line([(plat1_center_x - 280, sep_y), (plat1_center_x - 25, sep_y)], fill="#D4AF37", width=3)
    draw_rgba.line([(plat1_center_x + 25, sep_y), (plat1_center_x + 280, sep_y)], fill="#D4AF37", width=3)
    draw_rgba.polygon([
        (plat1_center_x, sep_y - 9),
        (plat1_center_x + 9, sep_y),
        (plat1_center_x, sep_y + 9),
        (plat1_center_x - 9, sep_y)
    ], fill="#FFD700")

    # 4. Sous-titre de description : DESCENDU EN TOUTE AÉRATION (dégagé du filet)
    # Ligne 1 : sep_y + 90 px (ample respiration de 90 px sous le trait !)
    sub_y1 = sep_y + 90
    s1_img, _ = render_metallic_text("Le Système Automatisé pour Maîtriser son Budget sans Privation,", font_sub, mode="silver")
    s2_img, _ = render_metallic_text("Éliminer ses Dettes et Bâtir un Patrimoine Passif", font_sub, mode="silver")
    s3_img, _ = render_metallic_text("avec un Salaire Ordinaire", font_sub, mode="gold")
    paste_centered(img_rgba, s1_img, plat1_center_x, sub_y1)
    paste_centered(img_rgba, s2_img, plat1_center_x, sub_y1 + 52)
    paste_centered(img_rgba, s3_img, plat1_center_x, sub_y1 + 104)

    # 5. Nom d'Auteur en bas : Platine & Or noble
    auteur_y = height_px - bleed_px - int(1.15 * dpi)
    aut_img, _ = render_metallic_text(auteur, font_auteur, mode="silver")
    paste_centered(img_rgba, aut_img, plat1_center_x, auteur_y)
    draw_rgba.text((plat1_center_x, auteur_y + 68), "INGÉNIERIE BUDGÉTAIRE & PATRIMOINE RÉSILIENT", fill="#D4AF37", font=font_badge, anchor="mm")

    # =========================================================================
    # TRANCHE (DOS / SPINE)
    # =========================================================================
    spine_center_x = (spine_left + spine_right) // 2
    spine_h = height_px - 450
    spine_w = max(24, spine_px)

    spine_surf = Image.new("RGBA", (spine_h, spine_w), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(spine_surf)
    texte_tranche = f"{auteur.upper()}   ◆   L'ARCHITECTE FINANCIER   ◆   ÉDITION 2026"
    s_draw.text((spine_h // 2, spine_w // 2), texte_tranche, fill="#F8FAFC", font=font_dos, anchor="mm")

    spine_rot = spine_surf.rotate(270, expand=True)
    img_rgba.paste(spine_rot, (spine_center_x - spine_rot.width // 2, 225), spine_rot)

    # =========================================================================
    # QUATRIÈME DE COUVERTURE (PLAT 4)
    # =========================================================================
    marge_securite_x = int(0.70 * dpi)
    col_left = plat4_left + marge_securite_x
    col_right = plat4_right - marge_securite_x
    plat4_center_x = (plat4_left + plat4_right) // 2

    # En-tête accrocheuse
    header_y = bleed_px + int(0.75 * dpi)
    b_back_img, _ = render_metallic_text("— ANALYSE & MÉTHODE D'ÉLITE —", font_badge, mode="gold")
    paste_centered(img_rgba, b_back_img, plat4_center_x, header_y)

    h1_img, _ = render_metallic_text("POURQUOI 90 % DES PERSONNES", font_back_h1, mode="silver")
    h2_img, _ = render_metallic_text("ÉCHOUENT À BÂTIR UN PATRIMOINE ?", font_back_h1, mode="gold")
    paste_centered(img_rgba, h1_img, plat4_center_x, header_y + 62)
    paste_centered(img_rgba, h2_img, plat4_center_x, header_y + 118)

    draw_rgba.line([(plat4_center_x - 180, header_y + 168), (plat4_center_x + 180, header_y + 168)], fill="#D4AF37", width=2)

    # Texte de 4ème de couverture
    paragraphes = [
        "La majorité des livres de finances personnelles vous noient sous des calculs",
        "arides ou vous imposent une privation permanente stérile et culpabilisante.",
        "« L'ARCHITECTE FINANCIER » prend le contre-pied absolu de cette approche.",
        "",
        "Inspiré des plus grands travaux sur l'ingénierie des flux et la psychologie",
        "comportementale, cet ouvrage vous livre une méthode d'acier, sans jargon,",
        "pour bâtir votre forteresse patrimoniale en moins de 30 jours :"
    ]

    cur_y = header_y + 208
    line_spacing = 38
    for line in paragraphes:
        if line:
            draw_rgba.text((col_left, cur_y), line, fill="#CBD5E1", font=font_back_corps, anchor="lt")
        cur_y += line_spacing

    # Les 5 Piliers Stratégiques
    cur_y += 15
    bullet_indent = 45
    piliers = [
        ("◆", "L'Architecture des 3 Comptes : automatiser votre trésorerie dès le 2 du mois."),
        ("◆", "La Dépense Consciente : supprimer la privation et sanctuariser son plaisir."),
        ("◆", "L'Éradication des Dettes : détruire les crédits toxiques avec la méthode Boule de Neige."),
        ("◆", "La Forteresse de Sécurité : calibrer son fonds d'urgence sans sur-stocker de cash."),
        ("◆", "L'Investissement Passif : bâtir un portefeuille indiciel mondial résilient en 1 clic/mois.")
    ]

    for bullet, texte_p in piliers:
        draw_rgba.text((col_left, cur_y), bullet, fill="#D4AF37", font=font_back_bullet, anchor="lt")
        draw_rgba.text((col_left + bullet_indent, cur_y), texte_p, fill="#F8FAFC", font=font_back_bullet, anchor="lt")
        cur_y += 48

    # Bloc Encadré de Citation
    cur_y += 35
    box_padding = 25
    box_h = 135
    box_top = cur_y
    box_bottom = box_top + box_h

    draw_rgba.rectangle([col_left, box_top, col_right, box_bottom], fill=(15, 23, 42, 235), outline="#1E293B", width=1)
    draw_rgba.line([(col_left, box_top), (col_left, box_bottom)], fill="#D4AF37", width=5)

    draw_rgba.text((col_left + box_padding + 10, box_top + 22), "« La véritable richesse ne se mesure pas à ce qui se voit,", fill="#D4AF37", font=font_back_citation, anchor="lt")
    draw_rgba.text((col_left + box_padding + 10, box_top + 58), "mais à la pleine souveraineté de votre temps. »", fill="#D4AF37", font=font_back_citation, anchor="lt")
    draw_rgba.text((col_right - box_padding, box_top + 95), "— MarkEddy", fill="#94A3B8", font=font_badge, anchor="rt")

    # Réserve Code-Barres ISBN KDP (600 x 360 px en bas à droite)
    isbn_w = 600
    isbn_h = 360
    isbn_x = plat4_right - isbn_w - int(0.35 * dpi)
    isbn_y = height_px - bleed_px - isbn_h - int(0.35 * dpi)

    draw_rgba.rectangle([isbn_x, isbn_y, isbn_x + isbn_w, isbn_y + isbn_h], fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw_rgba.text((isbn_x + isbn_w // 2, isbn_y + isbn_h // 2 - 20), "RÉSERVE CODE-BARRES ISBN", fill="#64748B", font=font_badge, anchor="mm")
    draw_rgba.text((isbn_x + isbn_w // 2, isbn_y + isbn_h // 2 + 20), "Format normalisé KDP (600 x 360 px)", fill="#94A3B8", font=font_dos, anchor="mm")

    draw_rgba.text((col_left, isbn_y + 140), "COLLECTION HAUTE INGÉNIERIE", fill="#D4AF37", font=font_badge, anchor="lt")
    draw_rgba.text((col_left, isbn_y + 180), "Édition reliée & numérique 2026", fill="#94A3B8", font=font_dos, anchor="lt")
    draw_rgba.text((col_left, isbn_y + 215), "Catégorie : Économie & Finances Personnelles", fill="#94A3B8", font=font_dos, anchor="lt")

    # Conversion finale
    img = img_rgba.convert("RGB")

    # =========================================================================
    # SAUVEGARDE MULTI-FORMATS
    # =========================================================================
    sortie_pdf = Path("couverture_kdp_complete.pdf")
    sortie_jpg = Path("couverture_kdp_complete.jpg")
    sortie_ebook = Path("couverture_ebook.jpg")

    # 1. Couverture intégrale PDF 300 DPI
    img.save(str(sortie_pdf), "PDF", resolution=300.0)
    print(f"✅ PDF Couverture intégrale KDP 300 DPI : {sortie_pdf.resolve()}")

    # 2. Couverture intégrale JPG HD
    img.save(str(sortie_jpg), "JPEG", quality=95)
    print(f"✅ JPG Couverture intégrale 300 DPI : {sortie_jpg.resolve()}")

    # 3. Face avant seule pour eBook Kindle HD (1600 x 2560 px)
    face_avant = img.crop((plat1_left, bleed_px, plat1_right, height_px - bleed_px))
    face_avant_hd = face_avant.resize((1600, 2560), Image.Resampling.LANCZOS)
    face_avant_hd.save(str(sortie_ebook), "JPEG", quality=95)
    print(f"✅ JPG Face avant eBook Kindle HD : {sortie_ebook.resolve()}")

    return sortie_pdf

if __name__ == "__main__":
    creer_couverture_chef_d_oeuvre()
