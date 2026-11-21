# -*- coding: utf-8 -*-
import json
import shutil
from pathlib import Path
from kdp_epub_exporter import construire_epub, livre_depuis_manuscrit

with open("book_blueprint.json", "r", encoding="utf-8") as f:
    bp = json.load(f)

titre = bp.get("titre", "L'ARCHITECTE FINANCIER")
sous_titre = bp.get("sous_titre", "Le Système Automatisé pour Maîtriser son Budget...")
auteur = bp.get("auteur", "MarkEddy")

md_text = Path("manuscrit_complet.md").read_text(encoding="utf-8")

livre_struct = livre_depuis_manuscrit(
    texte_markdown=md_text,
    titre=titre,
    auteur=auteur,
    sous_titre=sous_titre
)

sortie = construire_epub(livre_struct, nom_fichier="livre_ebook_kdp.epub")
shutil.copy2(sortie, "livre_ebook_kdp.epub")
shutil.copy2(sortie, Path("books/l_architecte_financier/livre_ebook_kdp.epub"))
print(f"✅ EPUB officiel généré avec succès : {sortie}")
