import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

def generer_couverture_kdp(
    nb_pages=130,
    largeur_page=6.0,
    hauteur_page=9.0,
    titre="L'INTELLIGENCE FINANCIÈRE PRATIQUE",
    sous_titre="Comprendre ses biais émotionnels, automatiser son épargne...",
    auteur="MarkEddy",
    bg_image_path=None,
    sortie_pdf_path=None,
    sortie_jpg_path=None
):
    dpi = 300
    bleed_in = 0.125
    trim_w_in = float(largeur_page)
    trim_h_in = float(hauteur_page)
    spine_in = round(nb_pages * 0.002252, 4)

    total_w_in = bleed_in + trim_w_in + spine_in + trim_w_in + bleed_in
    total_h_in = bleed_in + trim_h_in + bleed_in

    width_px = int(round(total_w_in * dpi))
    height_px = int(round(total_h_in * dpi))

    print(f"📐 Gabarit KDP 300 DPI : {width_px} x {height_px} px ({total_w_in:.4f} x {total_h_in:.4f} po)")
    print(f"   Tranche (dos) calculée pour {nb_pages} pages : {spine_in:.4f} po ({spine_in * 25.4:.2f} mm)")

    # Création du canvas fond Obsidienne velouté (#0A0F1D)
    img = Image.new("RGB", (width_px, height_px), color="#0A0F1D")
    draw = ImageDraw.Draw(img)

    # Coordonnées des zones en pixels
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

    # Arrière-plan personnalisé si fourni (stock photo Pexels/Unsplash)
    if bg_image_path and Path(bg_image_path).exists():
        try:
            bg_raw = Image.open(bg_image_path).convert("RGB")
            # Recadrer pour Plat 1
            bg_plat1 = ImageOps.fit(bg_raw, (trim_w_px, height_px), method=Image.Resampling.LANCZOS)
            # Assombrir légèrement pour garantir le contraste du texte
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(bg_plat1)
            bg_plat1_dark = enhancer.enhance(0.40)
            img.paste(bg_plat1_dark, (plat1_left, 0))
        except Exception as e_bg:
            print(f"⚠️ Note intégration image fond : {e_bg}")

    # Teinte contrastée sur le dos (Ardoise dense #111827)
    draw.rectangle([spine_left, 0, spine_right, height_px], fill="#111827")

    # Filets dorés subtils séparant le dos des plats
    draw.line([(spine_left, 0), (spine_left, height_px)], fill="#D4AF37", width=3)
    draw.line([(spine_right, 0), (spine_right, height_px)], fill="#D4AF37", width=3)

    # Chargement des polices système Windows
    try:
        font_titre = ImageFont.truetype("timesbd.ttf", 95)
        font_titre_sub = ImageFont.truetype("timesbd.ttf", 75)
        font_sub = ImageFont.truetype("georgia.ttf", 36)
        font_badge = ImageFont.truetype("arialbd.ttf", 28)
        font_auteur = ImageFont.truetype("timesbd.ttf", 60)
        font_dos = ImageFont.truetype("arialbd.ttf", 26)
        font_back_titre = ImageFont.truetype("timesbd.ttf", 52)
        font_back_texte = ImageFont.truetype("georgia.ttf", 32)
        font_back_points = ImageFont.truetype("georgia.ttf", 30)
    except Exception:
        font_titre = ImageFont.load_default()
        font_titre_sub = font_titre
        font_sub = font_titre
        font_badge = font_titre
        font_auteur = font_titre
        font_dos = font_titre
        font_back_titre = font_titre
        font_back_texte = font_titre
        font_back_points = font_titre

    # =========================================================================
    # 1. PLAT 1 (FACE AVANT) - Règle du tiers supérieur & lisibilité thumbnail
    # =========================================================================
    plat1_center_x = (plat1_left + plat1_right) // 2

    # Cadre ornemental doré subtil
    cadre_marge = bleed_px + int(0.3 * dpi)
    draw.rectangle(
        [plat1_left + cadre_marge - bleed_px, bleed_px + int(0.3 * dpi), plat1_right - int(0.3 * dpi), height_px - bleed_px - int(0.3 * dpi)],
        outline="#D4AF37",
        width=2
    )

    # Badge d'Excellence supérieur
    badge_y = bleed_px + int(0.8 * dpi)
    draw.text((plat1_center_x, badge_y), "— ÉDITION MASTERCLASS 2026 —", fill="#D4AF37", font=font_badge, anchor="mm")

    # Titre Principal dynamique
    titre_y1 = badge_y + 140
    titre_y2 = titre_y1 + 105

    if ":" in titre:
        morceaux = titre.split(":", 1)
        titre_p1 = morceaux[0].strip()
        titre_p2 = morceaux[1].strip()
    else:
        mots = titre.split()
        if len(mots) > 3:
            mid = len(mots) // 2
            titre_p1 = " ".join(mots[:mid])
            titre_p2 = " ".join(mots[mid:])
        else:
            titre_p1 = titre
            titre_p2 = ""

    draw.text((plat1_center_x, titre_y1), titre_p1, fill="#F8FAFC", font=font_titre, anchor="mm")
    if titre_p2:
        draw.text((plat1_center_x, titre_y2), titre_p2, fill="#D4AF37", font=font_titre_sub, anchor="mm")
    else:
        titre_y2 = titre_y1

    # Filet doré décoratif
    draw.line([(plat1_center_x - 280, titre_y2 + 70), (plat1_center_x + 280, titre_y2 + 70)], fill="#D4AF37", width=4)

    # Sous-titre à fort CTR
    sub_y = titre_y2 + 150
    st_texte = sous_titre or "La méthode pas-à-pas pour transformer vos résultats en 30 jours sans stress"
    draw.text((plat1_center_x, sub_y), st_texte[:60], fill="#E2E8F0", font=font_sub, anchor="mm")
    if len(st_texte) > 60:
        draw.text((plat1_center_x, sub_y + 55), st_texte[60:120], fill="#D4AF37", font=font_sub, anchor="mm")

    # Auteur officiel en bas
    auteur_y = height_px - bleed_px - int(1.1 * dpi)
    draw.text((plat1_center_x, auteur_y), auteur, fill="#F8FAFC", font=font_auteur, anchor="mm")
    draw.text((plat1_center_x, auteur_y + 65), "PUBLICATION INDÉPENDANTE D'AUTORITÉ", fill="#64748B", font=font_badge, anchor="mm")

    # =========================================================================
    # 2. TRANCHE (DOS / SPINE)
    # =========================================================================
    spine_center_x = (spine_left + spine_right) // 2
    spine_img = Image.new("RGBA", (height_px - 400, max(20, spine_px)), (0, 0, 0, 0))
    spine_draw = ImageDraw.Draw(spine_img)
    titre_tranche = titre.replace("\n", " ").strip()[:50]
    spine_draw.text(((height_px - 400) // 2, max(20, spine_px) // 2), f"{auteur}   —   {titre_tranche}   —   ÉDITION 2026", fill="#F8FAFC", font=font_dos, anchor="mm")
    rotated_spine = spine_img.rotate(270, expand=True)
    img.paste(rotated_spine, (spine_center_x - rotated_spine.width // 2, 200), rotated_spine)

    # =========================================================================
    # 3. PLAT 4 (QUATRIÈME DE COUVERTURE)
    # =========================================================================
    plat4_center_x = (plat4_left + plat4_right) // 2
    plat4_margin_x = plat4_left + int(0.6 * dpi)
    plat4_text_w = trim_w_px - int(1.2 * dpi)

    # Accroche forte
    back_y = bleed_px + int(0.9 * dpi)
    draw.text((plat4_center_x, back_y), "POURQUOI 90 % DES PERSONNES", fill="#D4AF37", font=font_back_titre, anchor="mm")
    draw.text((plat4_center_x, back_y + 65), "ÉCHOUENT À BÂTIR UN PATRIMOINE ?", fill="#F8FAFC", font=font_back_titre, anchor="mm")

    # Ligne dorée
    draw.line([(plat4_center_x - 200, back_y + 115), (plat4_center_x + 200, back_y + 115)], fill="#D4AF37", width=3)

    # Texte de 4ème de couverture
    p_lines = [
        "La majorité des livres de finances personnelles vous noient sous des calculs",
        "arides ou vous demandent de vivre dans une privation permanente stérile.",
        f"« {titre} » prend le contre-pied absolu de cette approche.",
        "",
        "Inspiré des plus grands travaux sur la psychologie comportementale et",
        "l'ingénierie budgétaire moderne, cet ouvrage vous offre une méthode chirurgicale",
        "sans jargon pour reprendre le contrôle total de votre argent en moins de 30 jours."
    ]
    cur_y = back_y + 160
    for l in p_lines:
        draw.text((plat4_center_x, cur_y), l, fill="#CBD5E1", font=font_back_texte, anchor="mm")
        cur_y += 44

    # Points clés à puces
    cur_y += 30
    points_cles = [
        "• Désamorcer vos biais émotionnels et neutraliser la comparaison sociale",
        "• L'Architecture des 3 Comptes : automatiser votre épargne dès le jour J+1",
        "• Éradiquer vos crédits toxiques avec les méthodes Avalanche et Boule de Neige",
        "• Bâtir votre matelas de sécurité inviolable sur livrets réglementés",
        "• L'investissement passif indiciel (ETF & PEA) en 1 clic par mois sans stress",
        "• La règle des 4% pour sécuriser une rente perpétuelle à terme"
    ]
    for pt in points_cles:
        draw.text((plat4_margin_x + 40, cur_y), pt, fill="#FAF5FF", font=font_back_points, anchor="lm")
        cur_y += 58

    # Citation d'autorité
    cur_y += 40
    draw.text((plat4_center_x, cur_y), "« La richesse ne se mesure pas à ce qui se voit,", fill="#D4AF37", font=font_back_texte, anchor="mm")
    draw.text((plat4_center_x, cur_y + 44), "mais à la pleine souveraineté de vos journées. »", fill="#D4AF37", font=font_back_texte, anchor="mm")
    draw.text((plat4_center_x, cur_y + 90), "— MarkEddy", fill="#94A3B8", font=font_badge, anchor="mm")

    # RÉSERVE CODE-BARRES ISBN OBLIGATOIRE AMAZON KDP (600 x 360 px)
    isbn_w = 600
    isbn_h = 360
    isbn_x = plat4_right - isbn_w - int(0.3 * dpi)
    isbn_y = height_px - bleed_px - isbn_h - int(0.3 * dpi)
    draw.rectangle([isbn_x, isbn_y, isbn_x + isbn_w, isbn_y + isbn_h], fill="#FFFFFF")
    draw.text((isbn_x + isbn_w // 2, isbn_y + isbn_h // 2), "RÉSERVE CODE-BARRES ISBN KDP", fill="#64748B", font=font_badge, anchor="mm")
    draw.rectangle([isbn_x, isbn_y, isbn_x + isbn_w, isbn_y + isbn_h], outline="#CBD5E1", width=1)

    # =========================================================================
    # 4. EXPORT COUVERTURE COMPLÈTE PDF 300 DPI
    # =========================================================================
    dossier_couv = Path("couvertures_finales")
    dossier_couv.mkdir(exist_ok=True)
    sortie_pdf = dossier_couv / "Couverture_OFFICIELLE_KDP.pdf"
    img.save(str(sortie_pdf), "PDF", resolution=300.0)
    
    # Copie à la racine pour compatibilité directe
    img.save("couverture_kdp_complete.pdf", "PDF", resolution=300.0)
    img.save("couverture_kdp_complete.jpg", "JPEG", quality=95)
    if sortie_pdf_path:
        p_out = Path(sortie_pdf_path)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(p_out), "PDF", resolution=300.0)
    print(f"✅ Couverture complète KDP 300 DPI générée : {sortie_pdf.resolve()}")

    # =========================================================================
    # 5. EXPORT COUVERTURE EBOOK KINDLE (FACE AVANT SEULE - 1600 x 2560 px)
    # =========================================================================
    face_avant = img.crop((plat1_left, bleed_px, plat1_right, height_px - bleed_px))
    face_avant_hd = face_avant.resize((1600, 2560), Image.Resampling.LANCZOS)
    
    dossier_export = Path("couvertures_export")
    dossier_export.mkdir(exist_ok=True)
    sortie_ebook = dossier_export / "01_amazon_kdp_ebook_cover.jpg"
    face_avant_hd.save(str(sortie_ebook), "JPEG", quality=95)
    face_avant_hd.save("couverture_ebook.jpg", "JPEG", quality=95)
    if sortie_jpg_path:
        p_jpg = Path(sortie_jpg_path)
        p_jpg.parent.mkdir(parents=True, exist_ok=True)
        face_avant_hd.save(str(p_jpg), "JPEG", quality=95)
    print(f"✅ Couverture eBook Kindle HD générée : {sortie_ebook.resolve()}")

    return sortie_pdf

if __name__ == "__main__":
    generer_couverture_kdp(130)
