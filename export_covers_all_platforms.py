"""
Générateur et convertisseur de couvertures multi-plateformes
(Amazon KDP eBook, Gumroad, Etsy, Payhip).
Auteur : MarkEddy
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DOSSIER_SORTIE = Path("couvertures_export")
DOSSIER_SORTIE.mkdir(exist_ok=True)


def creer_face_avant_base():
    """Génère la face avant en très haute définition (2560 x 1600 px)."""
    largeur, hauteur = 1600, 2560
    img = Image.new("RGB", (largeur, hauteur), color="#0F172A")
    draw = ImageDraw.Draw(img)

    # Cadre ornemental doré
    draw.rectangle([50, 50, largeur - 50, hauteur - 50], outline="#D97706", width=6)
    draw.rectangle([70, 70, largeur - 70, hauteur - 70], outline="#EAB308", width=2)

    # Textes principaux
    # (Pillow basique utilise les polices système par défaut)
    try:
        font_titre = ImageFont.truetype("times.ttf", 90)
        font_sub = ImageFont.truetype("arial.ttf", 42)
        font_auteur = ImageFont.truetype("times.ttf", 65)
    except IOError:
        font_titre = ImageFont.load_default()
        font_sub = font_titre
        font_auteur = font_titre

    # Titre & Sous-titre
    draw.text((largeur // 2, 450), "MAÎTRISER SES", fill="#F8FAFC", font=font_titre, anchor="mm")
    draw.text((largeur // 2, 570), "FINANCES PERSONNELLES", fill="#EAB308", font=font_titre, anchor="mm")
    
    draw.text((largeur // 2, 750), "De l'endettement à l'indépendance financière :", fill="#94A3B8", font=font_sub, anchor="mm")
    draw.text((largeur // 2, 820), "la méthode pas-à-pas pour budgétiser et investir", fill="#94A3B8", font=font_sub, anchor="mm")

    # Ligne dorée de séparation
    draw.line([(largeur // 4, 1100), (3 * largeur // 4, 1100)], fill="#D97706", width=4)

    # Nom d'auteur officiel
    draw.text((largeur // 2, 2200), "MarkEddy", fill="#F8FAFC", font=font_auteur, anchor="mm")
    draw.text((largeur // 2, 2300), "ÉDITION ACADÉMIQUE INDÉPENDANTE", fill="#64748B", font=font_sub, anchor="mm")

    return img


def generer_mockup_3d(img_face):
    """Génère un rendu 3D du livre avec tranche et ombre pour Etsy et Gumroad."""
    largeur_canvas, hauteur_canvas = 2400, 2400
    mockup = Image.new("RGBA", (largeur_canvas, hauteur_canvas), (245, 247, 250, 255))
    
    # Redimensionnement de la face avant
    livre_face = img_face.resize((1000, 1600), Image.Resampling.LANCZOS)
    
    # Dessin de l'ombre portée
    draw = ImageDraw.Draw(mockup)
    draw.polygon([(780, 480), (1850, 460), (1890, 2120), (740, 2150)], fill=(0, 0, 0, 70))
    draw.polygon([(800, 490), (1830, 470), (1870, 2100), (760, 2130)], fill=(0, 0, 0, 90))

    # Dessin de la fausse tranche 3D (spine)
    draw.polygon([(700, 520), (800, 480), (800, 2080), (700, 2120)], fill="#060C18")
    draw.line([(700, 520), (700, 2120)], fill="#D97706", width=3)

    # Collage de la face avant
    mockup.paste(livre_face, (800, 480))

    # Badge de qualité "Format eBook & Imprimable"
    draw.rectangle([1450, 350, 2100, 450], fill="#0F172A")
    draw.rectangle([1450, 350, 2100, 450], outline="#EAB308", width=3)
    try:
        font_badge = ImageFont.truetype("arial.ttf", 36)
        draw.text((1775, 400), "PACK OFFICIEL MarkEddy", fill="#FFFFFF", font=font_badge, anchor="mm")
    except IOError:
        pass

    return mockup.convert("RGB")


def exporter_toutes_les_plateformes():
    print("=" * 65)
    print("🎨 GÉNÉRATION DES COUVERTURES MULTI-PLATEFORMES (MarkEddy)")
    print("=" * 65)

    base = creer_face_avant_base()

    # 1. AMAZON KDP EBOOK (Format 1:1.6 - Haute Résolution)
    kdp_ebook = base.resize((1600, 2560), Image.Resampling.LANCZOS)
    kdp_path = DOSSIER_SORTIE / "01_amazon_kdp_ebook_cover.jpg"
    kdp_ebook.save(kdp_path, quality=95)
    print(f"✅ Amazon KDP eBook (1600x2560)    : {kdp_path.name}")

    # 2. PAYHIP & STORE NUMÉRIQUE (Format Portrait Standard)
    payhip = base.resize((1200, 1600), Image.Resampling.LANCZOS)
    payhip_path = DOSSIER_SORTIE / "02_payhip_product_cover.png"
    payhip.save(payhip_path)
    print(f"✅ Payhip Produit (1200x1600)        : {payhip_path.name}")

    # Génération du Mockup 3D
    mockup_3d = generer_mockup_3d(base)

    # 3. ETSY (Format Carré 1:1 Haute Définition)
    etsy = mockup_3d.resize((2000, 2000), Image.Resampling.LANCZOS)
    etsy_path = DOSSIER_SORTIE / "03_etsy_listing_mockup_carre.jpg"
    etsy.save(etsy_path, quality=95)
    print(f"✅ Etsy Listing Mockup (2000x2000)   : {etsy_path.name}")

    # 4. GUMROAD (Format Bannière 16:9)
    gumroad = mockup_3d.resize((1920, 1080), Image.Resampling.LANCZOS)
    gumroad_path = DOSSIER_SORTIE / "04_gumroad_cover_16x9.png"
    gumroad.save(gumroad_path)
    print(f"✅ Gumroad Cover (1920x1080)         : {gumroad_path.name}")

    print("\n🎯 Toutes les couvertures prêtes dans :", DOSSIER_SORTIE.resolve())


if __name__ == "__main__":
    exporter_toutes_les_plateformes()