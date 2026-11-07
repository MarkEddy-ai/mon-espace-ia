"""
generate_book_logo.py - Générateur et Traiteur Officiel du Logo Calligraphique "MarkEddy" (300 DPI).
Traite le fichier source maître officiel (Typographie noble bleu nuit, inlays or et arabesque royale)
pour produire l'ensemble des déclinaisons professionnelles pour tous les livres :
  1. Logo Couleur Originale (Fond Blanc pur & Fond Transparent)
  2. Logo Blanc & Or Prestige (Pour couvertures sombres, jaquettes et fonds nuit)
  3. Logo Monochrome Noir d'Édition (Impression intérieure KDP, Faux-titre, Mentions légales)
  4. Monogramme 'M' Calligraphique (Pour la tranche/dos du livre et culs-de-lampe)
  5. Icône Carrée de Marque (Réseaux sociaux, Favicon)
"""

import os
from pathlib import Path
from PIL import Image

DOSSIER_SORTIE = Path("assets/logo")
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

# Sources possibles du logo maître
SOURCES_POSSIBLES = [
    DOSSIER_SORTIE / "source_logo_master.jpg",
    Path("C:/Users/acer/.gemini/antigravity/brain/54fac2a2-52b1-456e-b05b-bca556a19e4e/.user_uploaded/media_1794014366705_52a4fcbd.jpg"),
    DOSSIER_SORTIE / "source_logo_calligraphique.jpg",
    Path("media_1794014366705_52a4fcbd.jpg")
]


def charger_source_maitre() -> Image.Image:
    """Charge l'image du logo calligraphique officiel MarkEddy."""
    for p in SOURCES_POSSIBLES:
        if p.exists():
            return Image.open(p).convert("RGB")
    raise FileNotFoundError(
        "❌ Aucun fichier source de logo trouvé. Placez 'source_logo_master.jpg' dans 'assets/logo/'."
    )


def creer_fond_transparent(img_rgb: Image.Image, seuil_bas=215, seuil_haut=250) -> Image.Image:
    """
    Supprime le fond blanc avec adoucissement des contours et dé-frangeage mathématique.
    Garantit une découpe soignée sans liseré parasite.
    """
    w, h = img_rgb.size
    img_rgba = Image.new("RGBA", (w, h))

    for y in range(h):
        for x in range(w):
            r, g, b = img_rgb.getpixel((x, y))
            lum = 0.299 * r + 0.587 * g + 0.114 * b

            if lum >= seuil_haut:
                img_rgba.putpixel((x, y), (255, 255, 255, 0))
            elif lum <= seuil_bas:
                img_rgba.putpixel((x, y), (r, g, b, 255))
            else:
                alpha = int(255 * (seuil_haut - lum) / (seuil_haut - seuil_bas))
                if alpha <= 0:
                    img_rgba.putpixel((x, y), (255, 255, 255, 0))
                else:
                    a_norm = alpha / 255.0
                    r_un = max(0, min(255, int((r - 255 * (1 - a_norm)) / a_norm)))
                    g_un = max(0, min(255, int((g - 255 * (1 - a_norm)) / a_norm)))
                    b_un = max(0, min(255, int((b - 255 * (1 - a_norm)) / a_norm)))
                    img_rgba.putpixel((x, y), (r_un, g_un, b_un, alpha))

    return img_rgba


def creer_version_blanc_et_or(logo_transparent: Image.Image) -> Image.Image:
    """
    Crée la version haute visibilité pour fonds sombres :
    Lettres bleu nuit converties en blanc pur satiné (#FAFAFC),
    Dorures et arabesques sublimées en or éclatant (#D4AF37).
    """
    w, h = logo_transparent.size
    blanc_or = Image.new("RGBA", (w, h))

    for y in range(h):
        for x in range(w):
            r, g, b, a = logo_transparent.getpixel((x, y))
            if a == 0:
                blanc_or.putpixel((x, y), (0, 0, 0, 0))
            else:
                # Détection des dorures (teintes chaudes or / ocre)
                is_gold = (r > 120 and g > 95 and r > b + 15)
                if is_gold:
                    blanc_or.putpixel((x, y), (212, 175, 55, a))  # Or royal
                else:
                    blanc_or.putpixel((x, y), (250, 250, 252, a))  # Blanc pur satiné

    return blanc_or


def creer_version_monochrome_noir(logo_transparent: Image.Image) -> Image.Image:
    """Crée la version monochrome noire d'édition pour impression intérieure KDP (Faux-titre, Copyright)."""
    w, h = logo_transparent.size
    noir_rgba = Image.new("RGBA", (w, h))

    for y in range(h):
        for x in range(w):
            r, g, b, a = logo_transparent.getpixel((x, y))
            if a == 0:
                noir_rgba.putpixel((x, y), (0, 0, 0, 0))
            else:
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                val = int(lum * 0.35)
                noir_rgba.putpixel((x, y), (val, val, val, a))

    return noir_rgba


def exporter_toutes_variantes():
    """Génère l'ensemble des déclinaisons officielles du logo calligraphique MarkEddy."""
    print("=" * 70)
    print("⚜️  GÉNÉRATEUR DU LOGO OFFICIEL 'MarkEddy' (300 DPI)")
    print("   Typographie Calligraphique de Luxe avec Inlays & Arabesque d'Or")
    print("=" * 70)

    # 1. Chargement de l'image source
    src = charger_source_maitre()
    print(f"📖 Source chargée : {src.size[0]} x {src.size[1]} px")

    # Coordonnées du bloc calligraphique (xmin=122, xmax=889, ymin=411, ymax=612)
    pad_x, pad_y = 12, 10
    box_logo = (
        max(0, 122 - pad_x),
        max(0, 411 - pad_y),
        min(src.width, 889 + pad_x),
        min(src.height, 612 + pad_y)
    )

    logo_couleur_fond_blanc = src.crop(box_logo)

    # 2. Version Couleur Originale & Détourage Transparent
    print("\n🎨 1. Traitement de la version couleur et détourage transparent...")
    logo_transparent = creer_fond_transparent(logo_couleur_fond_blanc)

    # Sauvegarde des versions Couleurs (compatibilité avec toutes les nomenclatures)
    p_couleur_officiel = DOSSIER_SORTIE / "logo_mark_eddy_officiel.png"
    p_couleur_alias = DOSSIER_SORTIE / "logo_markeddy_couleur.png"
    logo_couleur_fond_blanc.save(p_couleur_officiel, dpi=(300, 300))
    logo_couleur_fond_blanc.save(p_couleur_alias, dpi=(300, 300))

    p_transp_officiel = DOSSIER_SORTIE / "logo_mark_eddy_transparent.png"
    p_transp_alias = DOSSIER_SORTIE / "logo_markeddy_transparent.png"
    logo_transparent.save(p_transp_officiel, dpi=(300, 300))
    logo_transparent.save(p_transp_alias, dpi=(300, 300))

    print(f"  ✅ Logo Couleur Fond Blanc : {p_couleur_officiel.resolve()} ({logo_couleur_fond_blanc.size})")
    print(f"  ✅ Logo Couleur Détouré    : {p_transp_officiel.resolve()} ({logo_transparent.size})")

    # 3. Version Blanc & Or (pour fonds sombres et couvertures)
    print("\n✨ 2. Génération de la version Blanc & Or (pour couvertures sombres)...")
    logo_blanc_or = creer_version_blanc_et_or(logo_transparent)
    p_blanc_officiel = DOSSIER_SORTIE / "logo_mark_eddy_blanc.png"
    p_blanc_alias = DOSSIER_SORTIE / "logo_markeddy_blanc.png"
    logo_blanc_or.save(p_blanc_officiel, dpi=(300, 300))
    logo_blanc_or.save(p_blanc_alias, dpi=(300, 300))
    print(f"  ✅ Logo Blanc & Or         : {p_blanc_officiel.resolve()} ({logo_blanc_or.size})")

    # 4. Version Monochrome Noir (Print intérieur KDP)
    print("\n🖋️ 3. Génération de la version Monochrome Noir d'édition...")
    logo_noir = creer_version_monochrome_noir(logo_transparent)
    p_noir_officiel = DOSSIER_SORTIE / "logo_mark_eddy_noir.png"
    p_noir_alias = DOSSIER_SORTIE / "logo_markeddy_noir.png"
    logo_noir.save(p_noir_officiel, dpi=(300, 300))
    logo_noir.save(p_noir_alias, dpi=(300, 300))
    print(f"  ✅ Logo Monochrome Noir   : {p_noir_officiel.resolve()} ({logo_noir.size})")

    # 5. Monogramme 'M' Calligraphique seul (pour dos/tranche et médaillon)
    print("\n🛡️ 4. Extraction du Monogramme 'M' doré pour la tranche du livre...")
    box_m = (0, 30, min(130, logo_transparent.width), min(195, logo_transparent.height))
    monogramme_m = logo_blanc_or.crop(box_m)
    p_blason = DOSSIER_SORTIE / "blason_me_transparent.png"
    p_mono = DOSSIER_SORTIE / "monogramme_m_transparent.png"
    monogramme_m.save(p_blason, dpi=(300, 300))
    monogramme_m.save(p_mono, dpi=(300, 300))
    print(f"  ✅ Monogramme 'M' Dos/Spine: {p_blason.resolve()} ({monogramme_m.size})")

    # 6. Icône haute résolution (Carrée 800x800 px sur fond nuit)
    print("\n📱 5. Génération de l'icône de marque...")
    taille_icone = 800
    icone_carree = Image.new("RGBA", (taille_icone, taille_icone), (10, 15, 29, 255))
    logo_scaled = logo_blanc_or.copy()
    logo_scaled.thumbnail((700, 300), Image.Resampling.LANCZOS)
    lw, lh = logo_scaled.size
    icone_carree.paste(logo_scaled, ((taille_icone - lw) // 2, (taille_icone - lh) // 2), logo_scaled)

    p_icone = DOSSIER_SORTIE / "icone_markeddy.png"
    icone_carree.save(p_icone, dpi=(300, 300))
    print(f"  ✅ Icône carrée de marque : {p_icone.resolve()} ({icone_carree.size})")

    print("\n" + "=" * 70)
    print("🎉 LE NOUVEAU LOGO CALLIGRAPHIQUE EST DÉPLOYÉ AVEC SUCCÈS !")
    print("   Dossier : assets/logo/")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    exporter_toutes_variantes()
