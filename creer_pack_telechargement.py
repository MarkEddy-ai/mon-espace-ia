# -*- coding: utf-8 -*-
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(".")
DOSSIER_PACK = BASE_DIR / "PACK_TELECHARGEMENT_L_ARCHITECTE_FINANCIER"
DOSSIER_PACK.mkdir(exist_ok=True)

FICHIERS_MAPPING = {
    "livre_kdp_interieur.pdf": "01_LIVRE_INTERIEUR_PRINT_6x9_173PAGES.pdf",
    "couverture_kdp_complete.pdf": "02_COUVERTURE_COMPLETE_300DPI_TRANCHE_CALCULEE.pdf",
    "couverture_ebook.jpg": "03_COUVERTURE_EBOOK_KINDLE_HD_1600x2560.jpg",
    "livre_ebook_kdp.epub": "04_LIVRE_EBOOK_KINDLE_OFFICIEL.epub",
    "kdp_marketing_pack.html": "05_PACK_MARKETING_DESCRIPTION_ET_7_MOTS_CLES_A9.html",
    "manuscrit_complet.md": "06_MANUSCRIT_SOURCE_COMPLET_42000_MOTS.md",
    "livre_kdp_interieur.html": "07_MAQUETTE_TYPOGRAPHIQUE_HTML_CSS_6x9.html",
    "book_blueprint.json": "08_BLUEPRINT_SEO_ET_ARCHITECTURE_10X5.json",
    "competitor_gap_report.json": "09_ETUDE_MARCHE_ET_ANALYSE_CONCURRENTS.json"
}

# 1. Copie des fichiers avec des noms explicites
print("📦 Copie des actifs dans le dossier de téléchargement...")
for src_name, dest_name in FICHIERS_MAPPING.items():
    src = BASE_DIR / src_name
    if src.exists():
        shutil.copy2(src, DOSSIER_PACK / dest_name)
        # Copier également dans l'archive books/
        shutil.copy2(src, BASE_DIR / "books" / "l_architecte_financier" / src_name)
        print(f"  ✔ {dest_name} ({src.stat().st_size / 1024:.1f} Ko)")
    else:
        print(f"  ⚠️ Fichier source manquant : {src_name}")

# 2. Création de l'archive ZIP complète
ZIP_PATH = BASE_DIR / "PACK_TELECHARGEMENT_L_ARCHITECTE_FINANCIER.zip"
print(f"\n🗜️ Création de l'archive ZIP globale : {ZIP_PATH.name}...")
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in DOSSIER_PACK.iterdir():
        if f.is_file():
            zf.write(f, arcname=f.name)

# Copie du zip dans books/
shutil.copy2(ZIP_PATH, BASE_DIR / "books" / "l_architecte_financier" / ZIP_PATH.name)

taille_zip_mo = ZIP_PATH.stat().st_size / (1024 * 1024)
print(f"🎉 Archive ZIP prête pour téléchargement immédiat ({taille_zip_mo:.2f} Mo) !")
