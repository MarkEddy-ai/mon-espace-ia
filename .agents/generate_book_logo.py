from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DOSSIER_SORTIE = Path("assets/logo")
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

def creer_logo_moderne(mode="COULEUR"):
    largeur, hauteur = 3000, 1500
    
    if mode == "COULEUR":
        fond, couleur_texte, couleur_accent = (255, 255, 255, 255), "#0F172A", "#D4AF37"
    elif mode == "BLANC":
        fond, couleur_texte, couleur_accent = (15, 23, 42, 255), "#FFFFFF", "#D4AF37"
    else: 
        fond, couleur_texte, couleur_accent = (255, 255, 255, 0), "#0F172A", "#475569"

    img = Image.new("RGBA", (largeur, hauteur), fond)
    draw = ImageDraw.Draw(img)
    
    try:
        font_titre = ImageFont.truetype("times.ttf", 350)
        font_sub = ImageFont.truetype("arial.ttf", 60) # Sans-serif pour la modernité
    except IOError:
        font_titre = ImageFont.load_default()
        font_sub = font_titre

    # 1. Cadre géométrique minimaliste
    draw.rectangle([600, 300, 2400, 1200], outline=couleur_accent, width=12)
    
    # 2. Typographie principale
    draw.text((largeur//2, 650), "MarkEddy", fill=couleur_texte, font=font_titre, anchor="mm")
    
    # 3. Ligne de séparation subtile
    draw.line([(1200, 850), (1800, 850)], fill=couleur_accent, width=4)
    
    # 4. Sous-titre avec large espacement (Tracking)
    texte_sub = "É D I T I O N S   A C A D É M I Q U E S"
    draw.text((largeur//2, 980), texte_sub, fill=couleur_texte, font=font_sub, anchor="mm")

    return img

def exporter_toutes_variantes():
    print("=" * 65)
    print("⚜️ GÉNÉRATION DU LOGO ULTRA-MODERNE 'MarkEddy'")
    print("=" * 65)
    
    for mode, nom_fichier in [("COULEUR", "logo_couleur.png"), ("BLANC", "logo_blanc.png"), ("TRANSPARENT", "logo_transparent.png")]:
        img = creer_logo_moderne(mode)
        img.save(DOSSIER_SORTIE / nom_fichier, dpi=(300, 300))
        print(f"✅ Logo {mode} généré.")

if __name__ == "__main__":
    exporter_toutes_variantes()