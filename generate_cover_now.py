# -*- coding: utf-8 -*-
import json
from generate_luxury_cover import generer_couverture_kdp

with open("book_blueprint.json", "r", encoding="utf-8") as f:
    bp = json.load(f)

titre = bp.get("titre", "L'ARCHITECTE FINANCIER")
sous_titre = bp.get("sous_titre", "Le Système Automatisé pour Maîtriser son Budget sans Privation...")
auteur = bp.get("auteur", "MarkEddy")

# Exact page count : 173 pages
generer_couverture_kdp(
    nb_pages=173,
    titre=titre,
    sous_titre=sous_titre,
    auteur=auteur,
    sortie_pdf_path="couverture_kdp_complete.pdf",
    sortie_jpg_path="couverture_ebook.jpg"
)
print("✅ Couverture 300 DPI recalibrée au micron pour 173 pages !")
