"""
kdp_extensions - Extensions isolées du pipeline MarkEddy KDP Studio.

Ce package est un SUR-ENSEMBLE 100 % compatible : aucun fichier existant à la
racine n'est déplacé, renommé ni supprimé. Toute nouvelle fonctionnalité est
ajoutée ici uniquement, conformément à la règle de non-régression du dépôt.

Modules :
- kdp_dimensions   : Référentiel des 16 formats officiels Amazon KDP + calculs 300 DPI.
- media_connectors : Connecteurs Unsplash, Pixabay & Canva Connect API (httpx + Pillow).
- coloring_book_engine : Moteur de livres de coloriage KDP (SVG, line-art, Playwright).

Exécution obligatoire via : .\\.venv\\Scripts\\python.exe
"""

__all__ = [
    "kdp_dimensions",
    "media_connectors",
    "coloring_book_engine",
]
