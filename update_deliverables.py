# -*- coding: utf-8 -*-
import zipfile
import shutil
from pathlib import Path
from kdp_epub_exporter import construire_epub, livre_depuis_manuscrit

workspace = Path(r"c:\Users\acer\OneDrive\Desktop\mon-espace-ia")

# 1. Mise à jour EPUB
print("📚 Compilation de l'EPUB...")
md_text = (workspace / "manuscrit_complet.md").read_text(encoding="utf-8")
livre = livre_depuis_manuscrit(md_text, titre="L'ARCHITECTE FINANCIER", auteur="MarkEddy")
construire_epub(livre, chemin_sortie=workspace / "livre_ebook_kdp.epub")
print("✅ livre_ebook_kdp.epub généré.")

# 2. Mise à jour du dossier pack
pack_dir = workspace / "PACK_TELECHARGEMENT_L_ARCHITECTE_FINANCIER"
pack_dir.mkdir(exist_ok=True)

files_to_pack = [
    ("livre_kdp_interieur.pdf", "01_LIVRE_PAPIER_BROCHE_6X9_KDP.pdf"),
    ("livre_ebook_kdp.epub", "02_LIVRE_EBOOK_KINDLE.epub"),
    ("livre_numerique_interactif.pdf", "03_LIVRE_NUMERIQUE_ECRAN_A4.pdf"),
    ("couverture_kdp_complete.pdf", "04_COUVERTURE_IMPRESSION_300DPI_KDP.pdf"),
    ("couverture_ebook.jpg", "05_COUVERTURE_EBOOK_KINDLE_HD.jpg"),
    ("couverture_kdp_complete.jpg", "06_COUVERTURE_COMPLETE_APERCU_HD.jpg"),
    ("LIVRE_AUDIO_SPECIFICATIONS_ACX_AUDIBLE.md", "07_SPECIFICATIONS_PRODUCTION_LIVRE_AUDIO.md"),
    ("kdp_marketing_pack.html", "08_PACK_MARKETING_DESCRIPTION_AMAZON.html"),
    ("book_blueprint.json", "09_BLUEPRINT_EDITORIAL_ET_SEO.json"),
    ("manuscrit_complet.md", "10_MANUSCRIT_INTEGRAL_SOURCE.md"),
]

for src_name, dst_name in files_to_pack:
    src_file = workspace / src_name
    if src_file.exists():
        shutil.copy2(src_file, pack_dir / dst_name)
        print(f"  • {dst_name} copié.")

# 3. Création du ZIP
zip_path = workspace / "PACK_TELECHARGEMENT_L_ARCHITECTE_FINANCIER.zip"
print(f"📦 Création de l'archive {zip_path.name}...")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for item in pack_dir.iterdir():
        zipf.write(item, arcname=f"PACK_L_ARCHITECTE_FINANCIER/{item.name}")

print(f"🎉 Archive ZIP prête ({zip_path.stat().st_size / (1024*1024):.2f} Mo) !")
