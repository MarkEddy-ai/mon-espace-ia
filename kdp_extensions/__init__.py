"""
kdp_extensions - Extensions isolées du pipeline MarkEddy KDP Studio.

Ce package est un SUR-ENSEMBLE 100 % compatible : aucun fichier existant à la
racine n'est déplacé, renommé ni supprimé. Toute nouvelle fonctionnalité est
ajoutée ici uniquement, conformément à la règle de non-régression du dépôt.

Modules :
- kdp_dimensions         : Référentiel des 16 formats officiels Amazon KDP + calculs 300 DPI.
- media_connectors       : Connecteurs Unsplash, Pixabay & Canva Connect API (httpx + Pillow).
- coloring_book_engine   : Moteur de livres de coloriage KDP (SVG, line-art, Playwright).
- fonts_connector        : Connexion API Google Fonts + Pairings typographiques d'édition KDP.
- market_trends_agent    : Veille tri-plateforme (Google Trends, Amazon KDP A9, Pinterest).
- editorial_structure    : Générateur complet de Front-Matter & Back-Matter KDP.
- layout_engine_pro      : Moteur CSS Paged Media (W3C), marges dynamiques & typographie d'artisan.
- cover_calculator       : Calcul dimensionnel exact au micron (Trim + Bleed + Spine) et gabarits SVG.
- coloring_generator     : Générateur de planches vectorielles de coloriage (thèmes enfants & adultes).
- puzzle_generator       : Générateur de 8 types de jeux et casse-têtes vectoriels + solutionnaire.
- kdp_export_orchestrator: Orchestrateur d'export ZIP 1-clic & règle prépresse des 24 pages KDP.
- social_trend_hunter    : Agent 1 - Veille tendances sociales (Reddit, Trends, A9, TikTok).
- deep_research_agent    : Agent 2 - Recherche académique, documentaire et presse (OpenAlex, CrossRef).
- editorial_humanizer_agent : Agent 3 - Synthèse, fact-checking, élimination des tics IA & humanisation.
- multilingual_transcreator : Agent 6 - Transcréateur multilingue idiomatique 5 langues (EN, FR, ES, DE, AR).

Exécution obligatoire via : .\\.venv\\Scripts\\python.exe
"""

from . import kdp_dimensions
from . import media_connectors
from . import coloring_book_engine
from . import fonts_connector
from . import market_trends_agent
from . import editorial_structure
from . import layout_engine_pro
from . import cover_calculator
from . import coloring_generator
from . import puzzle_generator
from . import kdp_export_orchestrator
from . import social_trend_hunter
from . import deep_research_agent
from . import editorial_humanizer_agent
from . import multilingual_transcreator
from . import brief_enhancer
from . import book_catalog
from . import autonomous_visual_agent

__all__ = [
    "kdp_dimensions",
    "media_connectors",
    "coloring_book_engine",
    "fonts_connector",
    "market_trends_agent",
    "editorial_structure",
    "layout_engine_pro",
    "cover_calculator",
    "coloring_generator",
    "puzzle_generator",
    "kdp_export_orchestrator",
    "social_trend_hunter",
    "deep_research_agent",
    "editorial_humanizer_agent",
    "multilingual_transcreator",
    "brief_enhancer",
    "book_catalog",
    "autonomous_visual_agent",
]
