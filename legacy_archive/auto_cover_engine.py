"""
MOTEUR DE COUVERTURE ULTRA-MODERNE KDP (MarkEddy Executive Edition)
Génération directe 300 DPI - 1 seule page paysage stricte, fond texturé, typo monumentale.
"""

from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

DPI = 300
FOND_PERDU = 0.125
COEFF_PAPIER = 0.002252

# Nuancier Prestige
FOND_NUIT       = (5, 9, 19)          # Bleu Nuit Profond
FOND_CENTRE     = (14, 23, 42)        # Halo central
OR_ECLATANT     = (254, 240, 138)     # Or clair lumineux
OR_IMPERIAL     = (212, 175, 55)      # Or standard
OR_FONCE        = (161, 122, 17)      # Or sombre de contraste
BLANC_PUR       = (255, 255, 255)
GRIS_TEXTE      = (203, 213, 225)
LIGNES_TRAME    = (212, 175, 55, 18)

DOSSIER_SORTIE = Path("couvertures_finales")
DOSSIER_SORTIE.mkdir(exist_ok=True)


def charger_police(nom, taille):
    try:
        return ImageFont.truetype(nom, int(taille))
    except IOError:
        try:
            return ImageFont.truetype("arialbd.ttf", int(taille))
        except IOError:
            return ImageFont.load_default()


def creer_fond_atmospherique(largeur, hauteur):
    """Crée un fond avec halo lumineux doré sous la première de couverture."""
    fond = Image.new("RGBA", (largeur, hauteur), FOND_NUIT)
    draw = ImageDraw.Draw(fond)

    # Trame géométrique moderne
    pas = 90
    for x in range(0, largeur + pas, pas):
        draw.line([(x, 0), (x, hauteur)], fill=LIGNES_TRAME, width=1)
    for y in range(0, hauteur + pas, pas):
        draw.line([(0, y), (largeur, y)], fill=LIGNES_TRAME, width=1)

    # Halo lumineux sous la 1ère de couverture (vers 75% de la largeur)
    halo = Image.new("RGBA", (largeur, hauteur), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    cx, cy = int(largeur * 0.75), int(hauteur * 0.40)
    rayon = int(hauteur * 0.35)
    halo_draw.ellipse([cx - rayon, cy - rayon, cx + rayon, cy + rayon], fill=(212, 175, 55, 32))
    halo = halo.filter(ImageFilter.GaussianBlur(80))

    fond = Image.alpha_composite(fond, halo)
    return fond


def generer_couverture(
    pdf_interieur="livre_ultra_moderne.pdf",
    largeur_po=6.0,
    hauteur_po=9.0,
    titre="MAÎTRISER SES\nFINANCES PERSONNELLES",
    sous_titre="Méthode académique, stratégies d'investissement\net tableau de bord complet",
    logo_path="assets/logo/blason_me_transparent.png"
):
    pdf_path = Path(pdf_interieur)
    if not pdf_path.exists():
        print(f"❌ Intérieur introuvable : {pdf_interieur}")
        return

    nb_pages = len(PdfReader(pdf_path).pages)
    largeur_tranche_po = nb_pages * COEFF_PAPIER
    largeur_totale_po = (FOND_PERDU * 2) + (largeur_po * 2) + largeur_tranche_po
    hauteur_totale_po = (FOND_PERDU * 2) + hauteur_po

    px_w = int(round(largeur_totale_po * DPI))
    px_h = int(round(hauteur_totale_po * DPI))
    px_tranche = int(round(largeur_tranche_po * DPI))

    print("=" * 70)
    print("🎨 GÉNÉRATION COUVERTURE ULTRA-MODERNE KDP")
    print("=" * 70)
    print(f"📖 Pages        : {nb_pages} pages")
    print(f"📐 Tranche      : {largeur_tranche_po:.4f} po ({px_tranche} px)")
    print(f"🖼️ Dimensions   : {px_w} x {px_h} px (Paysage 300 DPI)")

    couverture = creer_fond_atmospherique(px_w, px_h)
    draw = ImageDraw.Draw(couverture)

    # Repères KDP stricts
    centre_dos_x = px_w // 2
    panneau_avant_x_debut = centre_dos_x + (px_tranche // 2)
    centre_avant_x = panneau_avant_x_debut + ((px_w - panneau_avant_x_debut) // 2)

    panneau_arriere_x_fin = centre_dos_x - (px_tranche // 2)
    centre_arriere_x = panneau_arriere_x_fin // 2

    marge_secu = int(0.35 * DPI)  # 105 px de marge

    # Polices
    font_badge = charger_police("arialbd.ttf", px_h * 0.015)
    font_titre = charger_police("arialbd.ttf", px_h * 0.048)
    font_sub = charger_police("arial.ttf", px_h * 0.020)
    font_auteur = charger_police("arialbd.ttf", px_h * 0.026)
    font_dos = charger_police("arialbd.ttf", max(18, int(px_tranche * 0.38)))

    # -------------------------------------------------------------
    # 1. PREMIÈRE DE COUVERTURE (DROITE)
    # -------------------------------------------------------------
    # Badge
    y_badge = int(px_h * 0.12)
    draw.text((centre_avant_x, y_badge), "ÉDITION MASTERCLASS", fill=OR_IMPERIAL, font=font_badge, anchor="mm")
    draw.line([(centre_avant_x - 140, y_badge + 22), (centre_avant_x + 140, y_badge + 22)], fill=OR_ECLATANT, width=2)

    # Titre Monumental en Or Lumineux
    y_titre = int(px_h * 0.26)
    lignes_titre = titre.upper().split("\n")
    espacement = int(px_h * 0.055)
    for i, ligne in enumerate(lignes_titre):
        draw.text((centre_avant_x, y_titre + (i * espacement)), ligne, fill=OR_ECLATANT, font=font_titre, anchor="mm")

    # Sous-titre
    y_sub = y_titre + (len(lignes_titre) * espacement) + 40
    for i, ligne in enumerate(sous_titre.split("\n")):
        draw.text((centre_avant_x, y_sub + (i * 32)), ligne, fill=GRIS_TEXTE, font=font_sub, anchor="mm")

    # Logo Transparent Central
    logo_file = Path(logo_path)
    if not logo_file.exists():
        logo_file = Path("assets/logo/logo_markeddy_transparent.png")

    if logo_file.exists():
        logo_img = Image.open(logo_file).convert("RGBA")
        cible_h = int(px_h * 0.20)
        cible_w = int(cible_h * (logo_img.width / logo_img.height))
        logo_img = logo_img.resize((cible_w, cible_h), Image.Resampling.LANCZOS)
        
        pos_logo_x = centre_avant_x - (cible_w // 2)
        pos_logo_y = int(px_h * 0.58)
        couverture.paste(logo_img, (pos_logo_x, pos_logo_y), logo_img)

    # Auteur & Signature
    y_auteur = int(px_h * 0.88)
    draw.line([(centre_avant_x - 220, y_auteur - 35), (centre_avant_x + 220, y_auteur - 35)], fill=OR_IMPERIAL, width=2)
    draw.text((centre_avant_x, y_auteur), "MARKEDDY", fill=BLANC_PUR, font=font_auteur, anchor="mm")

    # -------------------------------------------------------------
    # 2. DOS (TRANCHE DYNAMIQUE)
    # -------------------------------------------------------------
    draw.line([(panneau_arriere_x_fin, 0), (panneau_arriere_x_fin, px_h)], fill=(212, 175, 55, 60), width=2)
    draw.line([(panneau_avant_x_debut, 0), (panneau_avant_x_debut, px_h)], fill=(212, 175, 55, 60), width=2)

    if nb_pages >= 80:
        img_spine = Image.new("RGBA", (px_h, px_tranche), (0, 0, 0, 0))
        d_spine = ImageDraw.Draw(img_spine)
        txt_spine = f"{titre.replace(chr(10), ' ')}    ◆    MARKEDDY"
        d_spine.text((px_h // 2, px_tranche // 2), txt_spine, fill=OR_ECLATANT, font=font_dos, anchor="mm")
        
        spine_rot = img_spine.rotate(270, expand=True)
        pos_x = centre_dos_x - (spine_rot.width // 2)
        couverture.paste(spine_rot, (pos_x, 0), spine_rot)

    # -------------------------------------------------------------
    # 3. QUATRIÈME DE COUVERTURE (GAUCHE) & CODE-BARRES KDP
    # -------------------------------------------------------------
    font_back_h2 = charger_police("arialbd.ttf", px_h * 0.026)
    font_back_txt = charger_police("arial.ttf", px_h * 0.018)

    y_back = int(px_h * 0.16)
    draw.text((marge_secu + 40, y_back), "MANUEL STRATÉGIQUE", fill=OR_IMPERIAL, font=font_badge)
    draw.text((marge_secu + 40, y_back + 45), "BÂTIR UNE AUTONOMIE FINANCIÈRE", fill=BLANC_PUR, font=font_back_h2)

    pitch = [
        "Une approche méthodique et chiffrée pour structurer,",
        "gérer et valoriser votre capital avec rigueur.",
        "Conçu pour éliminer l'incertitude grâce à des protocoles",
        "d'investissement validés et directement applicables."
    ]
    for i, ligne in enumerate(pitch):
        draw.text((marge_secu + 40, y_back + 120 + (i * 35)), ligne, fill=GRIS_TEXTE, font=font_back_txt)

    # Zone blanche réglementaire KDP pour code-barres (2" x 1.2" en bas à droite de la 4ème)
    w_bc = int(2.0 * DPI)
    h_bc = int(1.2 * DPI)
    bc_x2 = panneau_arriere_x_fin - marge_secu
    bc_x1 = bc_x2 - w_bc
    bc_y2 = px_h - marge_secu
    bc_y1 = bc_y2 - h_bc

    draw.rectangle([bc_x1, bc_y1, bc_x2, bc_y2], fill=(255, 255, 255), outline=OR_IMPERIAL, width=2)
    font_bc = charger_police("arialbd.ttf", 20)
    draw.text(((bc_x1 + bc_x2) // 2, (bc_y1 + bc_y2) // 2 - 14), "ZONE CODE-BARRES", fill=(71, 85, 105), font=font_bc, anchor="mm")
    draw.text(((bc_x1 + bc_x2) // 2, (bc_y1 + bc_y2) // 2 + 14), "KDP SAFE ZONE (2\" x 1.2\")", fill=(148, 163, 184), font=charger_police("arial.ttf", 16), anchor="mm")

    # 4. Exportation PDF 1 page stricte 300 DPI
    sortie_pdf = DOSSIER_SORTIE / f"Couverture_ULTRA_MODERNE_{largeur_po}x{hauteur_po}_{nb_pages}p.pdf"
    couverture.convert("RGB").save(sortie_pdf, "PDF", resolution=float(DPI))
    print(f"✅ COUVERTURE 100% VALIDE GÉNÉRÉE : {sortie_pdf.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    generer_couverture()