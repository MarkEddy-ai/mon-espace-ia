"""
GÉNÉRATEUR DE COUVERTURES ULTRA-MODERNES KDP (MarkEddy)
Connecté à la bibliothèque locale de gabarits.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------
# CONFIGURATION DE LA BIBLIOTHÈQUE
# ---------------------------------------------------------
DOSSIER_GABARITS = Path("assets/gabarits_kdp")
DOSSIER_SORTIE = Path("couvertures_finales")
DOSSIER_SORTIE.mkdir(exist_ok=True)

# Charte Graphique MarkEddy
COULEUR_FOND = "#0F172A"      # Obsidienne
COULEUR_OR = "#D4AF37"        # Or Impérial
COULEUR_BLANC = "#FFFFFF"
TEXTE_AUTEUR = "MarkEddy"

def trouver_gabarit(type_livre, format_coupe):
    """Cherche automatiquement le bon gabarit dans la bibliothèque."""
    if not DOSSIER_GABARITS.exists():
        print(f"❌ Erreur : Le dossier {DOSSIER_GABARITS} n'existe pas.")
        return None
        
    # Recherche un fichier PNG qui contient le type (ex: PAPERBACK) et le format (ex: 8.500x11.000)
    recherche = f"*{type_livre}*{format_coupe}*.png"
    fichiers_trouves = list(DOSSIER_GABARITS.glob(recherche))
    
    if fichiers_trouves:
        return fichiers_trouves[0]
    else:
        print(f"❌ Gabarit introuvable pour {type_livre} en {format_coupe}.")
        print(f"Vérifiez que le PNG est bien dans {DOSSIER_GABARITS.resolve()}")
        return None

def generer_couverture(type_livre, format_coupe, titre, sous_titre):
    print("=" * 65)
    print(f"🎨 GÉNÉRATION COUVERTURE : {type_livre} - {format_coupe}")
    print("=" * 65)

    path_template = trouver_gabarit(type_livre, format_coupe)
    if not path_template:
        return

    print(f"📐 Gabarit trouvé : {path_template.name}")
    gabarit = Image.open(path_template).convert("RGBA")
    largeur, hauteur = gabarit.size

    couverture = Image.new("RGBA", (largeur, hauteur), COULEUR_FOND)
    draw = ImageDraw.Draw(couverture)

    try:
        font_titre = ImageFont.truetype("arial.ttf", int(hauteur * 0.045))
        font_sub = ImageFont.truetype("arial.ttf", int(hauteur * 0.022))
        font_auteur = ImageFont.truetype("arial.ttf", int(hauteur * 0.03))
        font_dos = ImageFont.truetype("arial.ttf", int(hauteur * 0.018))
    except IOError:
        font_titre = font_sub = font_auteur = font_dos = ImageFont.load_default()

    centre_x_dos = largeur // 2
    centre_x_premiere = int(largeur * 0.75)
    centre_x_quatrieme = int(largeur * 0.25)

    # 1ÈRE DE COUVERTURE
    draw.text((centre_x_premiere, int(hauteur * 0.25)), titre.upper(), fill=COULEUR_OR, font=font_titre, anchor="mm", align="center")
    draw.text((centre_x_premiere, int(hauteur * 0.32)), sous_titre, fill=COULEUR_BLANC, font=font_sub, anchor="mm", align="center")
    draw.line([(centre_x_premiere - 300, int(hauteur * 0.36)), (centre_x_premiere + 300, int(hauteur * 0.36))], fill=COULEUR_OR, width=6)
    draw.text((centre_x_premiere, int(hauteur * 0.85)), TEXTE_AUTEUR.upper(), fill=COULEUR_BLANC, font=font_auteur, anchor="mm")

    # TRANCHE (DOS)
    txt_dos_img = Image.new('RGBA', (hauteur, int(largeur * 0.05)), (255,255,255,0))
    draw_dos = ImageDraw.Draw(txt_dos_img)
    draw_dos.text((hauteur // 2, int(largeur * 0.025)), f"{titre.upper()}      •      {TEXTE_AUTEUR.upper()}", fill=COULEUR_BLANC, font=font_dos, anchor="mm")
    txt_dos_rot = txt_dos_img.rotate(270, expand=1)
    couverture.paste(txt_dos_rot, (centre_x_dos - txt_dos_rot.width // 2, 0), txt_dos_rot)

    # 4ÈME DE COUVERTURE (Logo)
    logo_path = Path("assets/logo/logo_markeddy_blanc.png")
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        new_h = int(hauteur * 0.08)
        new_w = int(new_h * (logo.width / logo.height))
        logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)
        couverture.paste(logo, (centre_x_quatrieme - new_w//2, int(hauteur * 0.80)), logo)

    # EXPORTATION
    nom_fichier_final = f"Couverture_{type_livre}_{format_coupe}.pdf"
    fichier_sortie = DOSSIER_SORTIE / nom_fichier_final
    couverture.convert("RGB").save(fichier_sortie, "PDF", resolution=300.0)
    
    print(f"✅ SUCCÈS ! Couverture enregistrée ici : {fichier_sortie.resolve()}")

if __name__ == "__main__":
    TITRE = "MAÎTRISER SES\nFINANCES PERSONNELLES"
    SOUS_TITRE = "Méthode académique, stratégies d'investissement\net tableau de bord complet"
    
    TYPE_EDITION = "PAPERBACK"
    FORMAT = "8.500x11.000"
    
    generer_couverture(TYPE_EDITION, FORMAT, TITRE, SOUS_TITRE)