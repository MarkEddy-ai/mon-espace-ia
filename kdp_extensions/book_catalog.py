# -*- coding: utf-8 -*-
"""
kdp_extensions/book_catalog.py — Référentiel Central des Catégories & Modèles Amazon KDP + Etsy.

Ce module définit la matrice complète des 8 catégories d'ouvrages et de leurs modèles
spécialisés pour la publication Amazon KDP (Broché / Relié) et Etsy Printables (A4 / US Letter).

Chaque modèle intègre ses spécifications techniques d'impression :
- allowed_formats : Formats de coupe officiels acceptés
- default_format : Format de coupe officiel recommandé (6x9, 8.5x11, etc.)
- default_paper_type : Type de papier ('white' | 'cream' | 'color_standard' | 'color_premium')
- engine : Moteur de génération associé ('text' | 'coloring' | 'puzzles' | 'workbook')
- platforms : Canaux compatibles ('kdp', 'etsy', 'both')
- min_pages_kdp : Nombre de pages minimum officiel Amazon KDP (24 pages broché)
- max_pages_kdp : Nombre de pages maximal autorisé selon le papier
- default_pages : Pagination recommandée
- bleed_required : Débord de fond perdu nécessaire (+0.125" W / +0.25" H)
- low_content_flag : Déclaration Low-Content requise par la politique Amazon KDP
- min_gutter_override : Marge intérieure minimale forcée (ex. 0.75" coloriage/éducatif)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

try:
    from kdp_extensions.kdp_dimensions import (
        KDP_FORMATS,
        KDP_FORMAT_IDS,
        PAPER_SPINE_COEFFS,
        normalize_format,
    )
except ImportError:
    from kdp_dimensions import (
        KDP_FORMATS,
        KDP_FORMAT_IDS,
        PAPER_SPINE_COEFFS,
        normalize_format,
    )


BOOK_CATEGORIES_CATALOG: Dict[str, Dict[str, Any]] = {
    "non_fiction": {
        "id": "non_fiction",
        "label": "Non-Fiction & Savoir",
        "description": "Livres de transmission, méthodes, guides et ouvrages d'autorité",
        "icon": "📖",
        "primary_engine": "text",
        "default_format": "6x9",
        "models": [
            {
                "id": "guide_pratique",
                "label": "Guide pratique & Méthode terrain",
                "description": "Manuel opérationnel étape par étape avec études de cas et plans d'action 24h.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["6x9", "5.5x8.5", "5x8", "7x10"],
                "default_format": "6x9",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 120,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "developpement_personnel",
                "label": "Développement personnel & Neuro-habitudes",
                "description": "Psychologie comportementale, micro-habitudes durables et passage à l'action.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["6x9", "5.5x8.5", "5x8", "7x10"],
                "default_format": "6x9",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 120,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "business_finances",
                "label": "Business, Stratégie & Finances",
                "description": "Investissement, gestion de trésorerie, création d'entreprise et productivité 80/20.",
                "platforms": ["kdp"],
                "allowed_formats": ["6x9", "5.5x8.5", "7x10"],
                "default_format": "6x9",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 150,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Confirmés / Professionnels",
            },
            {
                "id": "tech_ia",
                "label": "Intelligence Artificielle & Technologies",
                "description": "Guides d'adoption de l'IA, prompt engineering, automatisation et outils modernes.",
                "platforms": ["kdp"],
                "allowed_formats": ["6x9", "7x10", "8x10"],
                "default_format": "6x9",
                "default_paper_type": "white",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 140,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Confirmés / Professionnels",
            },
            {
                "id": "sante_bien_etre",
                "label": "Santé, Sommeil & Bien-être",
                "description": "Protocoles de longévité, nutrition raisonnée, sommeil réparateur et gestion du stress.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["6x9", "5.5x8.5", "7x10"],
                "default_format": "6x9",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 120,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Tous publics",
            },
        ],
    },
    "coloring": {
        "id": "coloring",
        "label": "Livres de Coloriage",
        "description": "Planches immersives vectorielles en noir pur #000000 sur blanc pur #FFFFFF",
        "icon": "🎨",
        "primary_engine": "coloring",
        "default_format": "8.5x11",
        "models": [
            {
                "id": "enfants_traits_epais",
                "label": "Enfants 3-8 ans (Traits Épais Anti-débordement)",
                "description": "Silhouettes douces aux contours 3-4 pt conçues pour les feutres sans déborder.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.5x8.5", "8.25x8.25"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "coloring",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 64,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Enfants 3–5 ans (Éveil / Maternelle)",
            },
            {
                "id": "bold_easy_cozy",
                "label": "Bold & Easy / Cozy (Tendance TikTok/KDP)",
                "description": "Dessins épurés, scènes de vie réconfortantes et grands aplats anti-stress.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.5x8.5", "8.25x8.25"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "coloring",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 64,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Tous publics",
            },
            {
                "id": "mandalas_zen_adultes",
                "label": "Mandalas & Art-Thérapie Zen Adultes",
                "description": "Motifs géométriques sacrés et rosaces complexes pour une relaxation méditative profonde.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.5x8.5", "8.25x8.25"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "coloring",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 64,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "botanique_architecture",
                "label": "Botanique & Architecture d'Artisan",
                "description": "Gravures végétales délicates, serres florales et façades pittoresques d'Europe.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.5x8.5", "8.25x8.25"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "coloring",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 64,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "pack_etsy_printable",
                "label": "Pack PDF Coloriage Etsy Printable",
                "description": "Planches haute résolution prêtes à imprimer en formats universels A4 & US Letter.",
                "platforms": ["etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "coloring",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 60,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Tous publics",
            },
        ],
    },
    "puzzles": {
        "id": "puzzles",
        "label": "Puzzles & Casse-têtes",
        "description": "Jeux de réflexion, logique, stimulation cognitive et solutionnaire complet",
        "icon": "🧩",
        "primary_engine": "puzzles",
        "default_format": "8.5x11",
        "models": [
            {
                "id": "mots_meles",
                "label": "Mots Mêlés Thématiques (Word Search)",
                "description": "Grilles vectorielles denses avec liste de vocabulaire et solutions en fin d'ouvrage.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.25x11.69", "8x10", "6x9"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Tous publics",
            },
            {
                "id": "mots_croises_melanges",
                "label": "Mots Croisés & Mots Mélangés",
                "description": "Définitions aiguisées, grilles croisées et anagrammes progressifs.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.25x11.69", "8x10", "6x9"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Confirmés / Professionnels",
            },
            {
                "id": "labyrinthes_immersifs",
                "label": "Labyrinthes Vectoriels Multi-niveaux",
                "description": "Chemins labyrinthiques orthogonaux et circulaires avec progression en difficulté.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.5x8.5", "8.25x8.25"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 80,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Enfants 6–8 ans (Primaire)",
            },
            {
                "id": "sudoku_logique",
                "label": "Sudoku & Grilles de Déduction Logique",
                "description": "Grilles symétriques pures 9x9 (Facile, Moyen, Difficile) vérifiées sans ambiguïté.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "6x9", "8x10"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "cryptogrammes_enigmes",
                "label": "Cryptogrammes & Énigmes à Clés",
                "description": "Citations historiques chiffrées par substitution avec indices progressifs.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "6x9", "7x10"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 90,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Confirmés / Professionnels",
            },
            {
                "id": "points_a_relier",
                "label": "Points à Relier & Chiffres Cachés",
                "description": "Dessins vectoriels révélés point par point (numérotation 1 à 100+).",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.5x8.5"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 80,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Enfants 6–8 ans (Primaire)",
            },
            {
                "id": "cahier_multi_jeux",
                "label": "Cahier Multi-Jeux (8 Formats Réunis)",
                "description": "L'anthologie complète MarkEddy combinant les 8 familles de jeux de réflexion.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 120,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Tous publics",
            },
            {
                "id": "seniors_grands_caracteres",
                "label": "Grands Caractères Seniors (Large Print Puzzles)",
                "description": "Polices haute lisibilité 18+ pt, contrastes forts et grilles aérées adaptées aux seniors.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "puzzles",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Seniors 60+ (Grands Caractères / Large Print)",
            },
        ],
    },
    "educational": {
        "id": "educational",
        "label": "Cahiers Éducatifs & Activités",
        "description": "Supports d'apprentissage, d'éveil et de consolidation scolaire",
        "icon": "🎓",
        "primary_engine": "workbook",
        "default_format": "8.5x11",
        "models": [
            {
                "id": "trace_lettres_chiffres",
                "label": "Cahier de Tracé Lettres & Chiffres (Handwriting)",
                "description": "Lignes d'écriture guidées avec flèches de direction, repères visuels et animaux à colorier.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69", "8.5x8.5"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 80,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Enfants 3–5 ans (Éveil / Maternelle)",
            },
            {
                "id": "exercices_maths_sciences",
                "label": "Cahier d'Exercices Maths & Sciences",
                "description": "Additions, soustractions, fractions visuelles, énigmes spatiales et découvertes scientifiques.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 80,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Enfants 6–8 ans (Primaire)",
            },
            {
                "id": "cahier_de_vacances",
                "label": "Cahier de Vacances Ludo-éducatif",
                "description": "Révisions complètes mêlant jeux de lecture, logique et énigmes de culture générale.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 90,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Enfants 6–8 ans (Primaire)",
            },
            {
                "id": "fiches_montessori_flashcards_etsy",
                "label": "Fiches d'Activités Montessori & Flashcards (Etsy)",
                "description": "Cartes de nomenclature et fiches d'autonomie prêtes au découpage pour l'éveil sensoriel.",
                "platforms": ["etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 60,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Parents & Éducateurs",
            },
            {
                "id": "cahier_bilingue",
                "label": "Cahier d'Apprentissage Bilingue (Langues)",
                "description": "Immersion bilingue progressive (Anglais-Français ou Arabe-Français) avec illustrations.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 80,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": 0.75,
                "suggested_audience": "Enfants 9–12 ans (Collège)",
            },
        ],
    },
    "planners_journals": {
        "id": "planners_journals",
        "label": "Planners, Agendas & Carnets",
        "description": "Outils d'organisation personnelle, productivité et journaling guidé",
        "icon": "📅",
        "primary_engine": "workbook",
        "default_format": "8.5x11",
        "models": [
            {
                "id": "planner_quotidien_hebdo",
                "label": "Planner Quotidien & Hebdomadaire Non-Daté",
                "description": "Planches de gestion du temps, priorités de la journée, plages horaires et bilans hebdo.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "6x9", "7x10"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 120,
                "bleed_required": True,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "journal_guide_gratitude",
                "label": "Journal Guidé de Gratitude & Réflexion",
                "description": "Invitations d'écriture quotidienne pour cultiver la pleine conscience et la sérénité.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["6x9", "5.5x8.5"],
                "default_format": "6x9",
                "default_paper_type": "cream",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "tracker_budget_habitudes",
                "label": "Tracker de Budget, Épargne & Habitudes",
                "description": "Grilles de suivi des dépenses, méthode 50/30/20 et suivi visuel des routines sur 12 mois.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "6x9", "7x10"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "carnet_de_bord_thematique",
                "label": "Carnet de Bord & Logbook Spécialisé",
                "description": "Cahier de suivi spécialisé (Fitness, Pêche, Randonnée, Entretien automobile, Jardin).",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["6x9", "5.5x8.5", "7x10"],
                "default_format": "6x9",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Tous publics",
            },
            {
                "id": "planner_digital_etsy",
                "label": "Planner Digital GoodNotes & Notability (Etsy)",
                "description": "Fichier PDF interactif avec onglets cliquables pour tablette iPad / Android.",
                "platforms": ["etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 150,
                "bleed_required": False,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
        ],
    },
    "workbooks": {
        "id": "workbooks",
        "label": "Workbooks & Bilans Guidés",
        "description": "Cahiers d'exercices d'accompagnement, coaching et bilans opérationnels",
        "icon": "📋",
        "primary_engine": "workbook",
        "default_format": "8.5x11",
        "models": [
            {
                "id": "workbook_coaching",
                "label": "Workbook de Coaching & Passage à l'Action",
                "description": "Cahier d'exercices structuré pour ateliers de formation, bilans de compétences et coaching.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "6x9", "7x10"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Confirmés / Professionnels",
            },
            {
                "id": "cahier_exercices_bilans",
                "label": "Cahier d'Exercices, Audits & Bilans Guidés",
                "description": "Questionnaires d'introspection, grilles d'audit personnel et synthèses de progression.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x11", "6x9", "7x10"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 90,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
            {
                "id": "kit_printable_organisation_etsy",
                "label": "Kit Printable d'Organisation Personnelle (Etsy)",
                "description": "Collection de feuilles de travail prêtes à imprimer pour la gestion du foyer et de projets.",
                "platforms": ["etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 60,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Parents & Éducateurs",
            },
        ],
    },
    "cookbooks": {
        "id": "cookbooks",
        "label": "Livres de Recettes & Cuisine",
        "description": "Ouvrages culinaires, meal planners et carnets de cuisine gourmands",
        "icon": "🍳",
        "primary_engine": "text",
        "default_format": "7x10",
        "models": [
            {
                "id": "livre_recettes_thematique",
                "label": "Livre de Recettes Thématique Illustré",
                "description": "50 recettes saines et gourmandes (Air Fryer, Batch Cooking, Végétarien, Desserts).",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["7x10", "8.5x11", "8x10", "6x9"],
                "default_format": "7x10",
                "default_paper_type": "color_standard",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 600,
                "default_pages": 80,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Tous publics",
            },
            {
                "id": "carnet_recettes_a_remplir",
                "label": "Carnet de Recettes Vierge à Remplir",
                "description": "Gabarits structurés pour consigner 100 recettes de famille avec temps de cuisson et notes.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["7x10", "8.5x11", "6x9"],
                "default_format": "7x10",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 100,
                "bleed_required": False,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Tous publics",
            },
            {
                "id": "meal_planner_courses_etsy",
                "label": "Meal Planner Hebdo & Listes de Courses (Etsy)",
                "description": "Planches de planification des menus de la semaine et fiches de courses détachables.",
                "platforms": ["etsy"],
                "allowed_formats": ["8.5x11", "8.27x11.69"],
                "default_format": "8.5x11",
                "default_paper_type": "white",
                "engine": "workbook",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 60,
                "bleed_required": False,
                "low_content_flag": True,
                "min_gutter_override": None,
                "suggested_audience": "Adultes Débutants",
            },
        ],
    },
    "fiction_kids": {
        "id": "fiction_kids",
        "label": "Fiction Jeunesse & Histoires",
        "description": "Récits illustrés, contes du soir et aventures interactives",
        "icon": "🧚",
        "primary_engine": "text",
        "default_format": "8.5x8.5",
        "models": [
            {
                "id": "contes_illustres_enfants",
                "label": "Contes Illustrés pour Enfants (3-7 ans)",
                "description": "Aventures tendres aux illustrations pleines pages et vocabulaire doux d'éveil.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["8.5x8.5", "8.25x8.25", "7x10"],
                "default_format": "8.5x8.5",
                "default_paper_type": "color_premium",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 828,
                "default_pages": 36,
                "bleed_required": True,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Enfants 3–5 ans (Éveil / Maternelle)",
            },
            {
                "id": "histoires_du_soir",
                "label": "Histoires Courtes d'Endormissement & Sérénité",
                "description": "Récits apaisants de 5 minutes pour ritualiser le coucher et inviter au calme.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["6x9", "5.5x8.5", "5x8"],
                "default_format": "6x9",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 90,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Enfants 6–8 ans (Primaire)",
            },
            {
                "id": "roman_court_recueil",
                "label": "Roman Court ou Recueil de Nouvelles",
                "description": "Récit d'aventure ou policier rythmé avec chapitrage immersif et tension narrative.",
                "platforms": ["kdp"],
                "allowed_formats": ["5x8", "5.25x8", "5.5x8.5", "6x9"],
                "default_format": "5x8",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 110,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Adolescents 12–17 ans",
            },
            {
                "id": "livre_jeu_interactif",
                "label": "Livre-Jeu Interactif (Un livre dont vous êtes le héros)",
                "description": "Parcours à choix multiples avec paragraphes numérotés et embranchements décisionnels.",
                "platforms": ["kdp", "etsy"],
                "allowed_formats": ["5.5x8.5", "6x9"],
                "default_format": "5.5x8.5",
                "default_paper_type": "cream",
                "engine": "text",
                "min_pages_kdp": 24,
                "max_pages_kdp": 746,
                "default_pages": 120,
                "bleed_required": False,
                "low_content_flag": False,
                "min_gutter_override": None,
                "suggested_audience": "Enfants 9–12 ans (Collège)",
            },
        ],
    },
}


CATALOG_PAPER_SPINE_COEFFS: Dict[str, float] = {
    "white": 0.002252,
    "cream": 0.0025,
    "color_standard": 0.002252,
    "color_premium": 0.002347,
}


def get_catalog() -> Dict[str, Dict[str, Any]]:
    """Retourne l'intégralité du catalogue des catégories et modèles de livres."""
    return BOOK_CATEGORIES_CATALOG


def get_category(category_id: str) -> Optional[Dict[str, Any]]:
    """Récupère une catégorie par son identifiant ou alias (tolérance casse et pluriels)."""
    if not category_id:
        return None
    clean = category_id.strip().lower()
    if clean in BOOK_CATEGORIES_CATALOG:
        return BOOK_CATEGORIES_CATALOG[clean]
    # Alias usuels
    if clean in ("coloriage", "coloriages", "coloring_book", "coloring_books"):
        clean = "coloring"
    elif clean in ("puzzle", "puzzles", "jeux", "jeu"):
        clean = "puzzles"
    return BOOK_CATEGORIES_CATALOG.get(clean)


def get_model(model_id: str) -> Optional[Dict[str, Any]]:
    """Recherche un modèle précis par son identifiant unique à travers tout le catalogue."""
    if not model_id:
        return None
    m_clean = model_id.strip().lower()
    for cat in BOOK_CATEGORIES_CATALOG.values():
        for mod in cat.get("models", []):
            if mod.get("id") == m_clean:
                return mod
    return None


def normalize_catalog_selection(
    category: Optional[str] = None,
    model_id: Optional[str] = None,
    legacy_project_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Harmonise la sélection utilisateur (catégorie + modèle) avec les valeurs historiques.
    Garantit 100% de rétrocompatibilité : si un ancien paramètre legacy est fourni,
    il est résolu vers le modèle et le format correspondant sans aucune rupture.
    """
    # 1. Résolution du modèle direct si fourni
    if model_id:
        mod = get_model(model_id)
        if mod:
            # Recherche de la catégorie parente
            parent_cat = None
            for cid, cdata in BOOK_CATEGORIES_CATALOG.items():
                if any(m.get("id") == mod["id"] for m in cdata.get("models", [])):
                    parent_cat = cdata
                    break
            return {
                "category_id": parent_cat["id"] if parent_cat else "non_fiction",
                "category": parent_cat["id"] if parent_cat else "non_fiction",
                "category_label": parent_cat["label"] if parent_cat else "Non-Fiction",
                "model": mod,
                "engine": mod.get("engine", "text"),
                "default_format": mod.get("default_format", "6x9"),
                "low_content_flag": mod.get("low_content_flag", False),
                "bleed_required": mod.get("bleed_required", False),
            }

    # 2. Résolution par catégorie
    cat_key = category or legacy_project_type or "non_fiction"
    cat = get_category(cat_key)
    if not cat:
        cat = BOOK_CATEGORIES_CATALOG["non_fiction"]

    first_model = cat["models"][0] if cat.get("models") else {
        "id": "standard",
        "label": cat["label"],
        "engine": cat.get("primary_engine", "text"),
        "default_format": cat.get("default_format", "6x9"),
        "low_content_flag": False,
        "bleed_required": False
    }

    return {
        "category_id": cat["id"],
        "category": cat["id"],
        "category_label": cat["label"],
        "model": first_model,
        "engine": first_model.get("engine", cat.get("primary_engine", "text")),
        "default_format": first_model.get("default_format", cat.get("default_format", "6x9")),
        "low_content_flag": first_model.get("low_content_flag", False),
        "bleed_required": first_model.get("bleed_required", False),
    }


def compute_model_measurements(
    model_id: str,
    page_count: int,
    format_kdp: Optional[str] = None,
    paper_type: Optional[str] = None,
    platform: str = "kdp"
) -> Dict[str, Any]:
    """
    Calcule dynamiquement en temps réel le métrage exact d'un livre KDP / Etsy :
    - Épaisseur du dos (spine) au micron
    - Marge de reliure (gutter) selon le barème officiel KDP (et min_gutter_override)
    - Marges extérieures
    - Dimensions intérieures (avec débord fond perdu +0.125" W / +0.25" H si bleed_required)
    - Dimensions totales de la couverture (300 DPI, pouces, mm, pixels)
    - Réserve normalisée ISBN (600x360 px)
    - Formats d'impression Etsy (A4 + US Letter @ 300 DPI) si platform in ('etsy', 'both')
    - Alertes de validation (seuil 24p broché, texte dos < 79p, dépassement pagination max).
    """
    mod = get_model(model_id)
    if not mod:
        # Repli propre sur guide_pratique sans lever d'exception bloquante
        mod = get_model("guide_pratique") or {
            "id": model_id or "guide_pratique",
            "label": "Guide pratique & Méthode terrain",
            "default_format": "6x9",
            "allowed_formats": ["6x9", "5.5x8.5", "5x8", "7x10"],
            "default_paper_type": "white",
            "engine": "text",
            "min_pages_kdp": 24,
            "max_pages_kdp": 828,
            "default_pages": 120,
            "bleed_required": False,
            "low_content_flag": False,
            "min_gutter_override": None,
        }

    # Recherche catégorie parente
    parent_cat_id = "non_fiction"
    for cid, cdata in BOOK_CATEGORIES_CATALOG.items():
        if any(m.get("id") == mod["id"] for m in cdata.get("models", [])):
            parent_cat_id = cid
            break

    # 1. Validation de la pagination
    try:
        pages = int(page_count)
    except (TypeError, ValueError):
        pages = mod.get("default_pages", 120)
    if pages < 1:
        pages = 1

    # 2. Format KDP & validation
    fmt_raw = format_kdp or mod.get("default_format", "6x9")
    try:
        fid = normalize_format(fmt_raw)
    except Exception:
        fid = mod.get("default_format", "6x9")
        if fid not in KDP_FORMATS:
            fid = "6x9"

    trim_w_in, trim_h_in = KDP_FORMATS.get(fid, (6.0, 9.0))

    # 3. Type de papier & coefficient de tranche
    paper_key = (paper_type or mod.get("default_paper_type", "white")).strip().lower()
    if paper_key not in CATALOG_PAPER_SPINE_COEFFS and paper_key not in PAPER_SPINE_COEFFS:
        paper_key = mod.get("default_paper_type", "white")
        if paper_key not in CATALOG_PAPER_SPINE_COEFFS and paper_key not in PAPER_SPINE_COEFFS:
            paper_key = "white"

    spine_coeff = CATALOG_PAPER_SPINE_COEFFS.get(paper_key, PAPER_SPINE_COEFFS.get(paper_key, 0.002252))

    # 4. Fond perdu (Bleed)
    bleed_required = bool(mod.get("bleed_required", False))

    # 5. Dimensions intérieures
    # Règle KDP : avec fond perdu, la largeur page augmente de +0.125" (côté extérieur)
    # et la hauteur augmente de +0.25" (+0.125" haut + 0.125" bas).
    if bleed_required:
        interior_w_in = round(trim_w_in + 0.125, 4)
        interior_h_in = round(trim_h_in + 0.25, 4)
    else:
        interior_w_in = round(trim_w_in, 4)
        interior_h_in = round(trim_h_in, 4)

    interior_w_mm = round(interior_w_in * 25.4, 2)
    interior_h_mm = round(interior_h_in * 25.4, 2)

    # 6. Marge de reliure (Gutter) selon le barème officiel KDP
    # 24 à 150 pages  : 0.375"
    # 151 à 300 pages : 0.500"
    # 301 à 500 pages : 0.625"
    # 501 à 700 pages : 0.750"
    # 701+ pages      : 0.875"
    if pages <= 150:
        scale_gutter = 0.375
    elif pages <= 300:
        scale_gutter = 0.500
    elif pages <= 500:
        scale_gutter = 0.625
    elif pages <= 700:
        scale_gutter = 0.750
    else:
        scale_gutter = 0.875

    min_gutter_ov = mod.get("min_gutter_override")
    if min_gutter_ov is not None:
        gutter_in = max(scale_gutter, float(min_gutter_ov))
    else:
        gutter_in = scale_gutter

    gutter_inches = round(gutter_in, 4)
    gutter_mm = round(gutter_inches * 25.4, 2)

    # 7. Marge extérieure
    outer_margin_inches = 0.375 if bleed_required else 0.25
    outer_margin_mm = round(outer_margin_inches * 25.4, 2)

    # 8. Épaisseur du dos (Spine)
    spine_inches = round(pages * spine_coeff, 4)
    spine_mm = round(spine_inches * 25.4, 2)
    spine_text_allowed = bool(pages >= 79)

    # 9. Dimensions totales de la couverture complète (Plat 4 + Dos + Plat 1 + Bleed 0.125" sur les 4 côtés)
    cover_bleed = 0.125
    cover_w_in = round((trim_w_in * 2.0) + spine_inches + (cover_bleed * 2.0), 4)
    cover_h_in = round(trim_h_in + (cover_bleed * 2.0), 4)
    cover_w_mm = round(cover_w_in * 25.4, 2)
    cover_h_mm = round(cover_h_in * 25.4, 2)
    cover_w_px = int(round(cover_w_in * 300))
    cover_h_px = int(round(cover_h_in * 300))

    # 10. Formats d'impression Etsy (si platform in 'etsy' ou 'both')
    plat_clean = (platform or "kdp").strip().lower()
    if plat_clean in ("etsy", "both"):
        etsy_print_formats = {
            "a4": {
                "label": "Format A4 Universel",
                "dimensions_mm": [210, 297],
                "dimensions_inches": [8.27, 11.69],
                "resolution_300dpi_px": [2480, 3508],
            },
            "us_letter": {
                "label": "Format US Letter Amérique du Nord",
                "dimensions_mm": [215.9, 279.4],
                "dimensions_inches": [8.5, 11.0],
                "resolution_300dpi_px": [2550, 3300],
            },
        }
    else:
        etsy_print_formats = None

    # 11. Alertes de validation
    validation_warnings: List[str] = []
    min_pages = mod.get("min_pages_kdp", 24)
    if pages < min_pages:
        validation_warnings.append(
            f"Seuil minimal KDP non atteint : {pages} pages (minimum {min_pages} pages pour livre broché)."
        )
    if not spine_text_allowed:
        validation_warnings.append(
            f"Texte sur la tranche interdit : Amazon KDP requiert au moins 79 pages pour imprimer du texte sur le dos ({pages} pages, dos de {spine_mm} mm)."
        )
    max_pages = mod.get("max_pages_kdp") or (746 if paper_key == "cream" else 828)
    if pages > max_pages:
        validation_warnings.append(
            f"Dépassement du nombre maximal de pages KDP : {pages} pages (limite {max_pages} pages pour papier {paper_key})."
        )
    allowed_fmts = mod.get("allowed_formats", [])
    if allowed_fmts and fid not in allowed_fmts:
        validation_warnings.append(
            f"Le format '{fid}' n'est pas dans la liste des formats recommandés ({', '.join(allowed_fmts)})."
        )

    return {
        "model_id": mod["id"],
        "model_label": mod["label"],
        "category_id": parent_cat_id,
        "platform": plat_clean,
        "format_id": fid,
        "page_count": pages,
        "paper_type": paper_key,
        "bleed_required": bleed_required,
        "interior_inches": {"width": interior_w_in, "height": interior_h_in},
        "interior_mm": {"width": interior_w_mm, "height": interior_h_mm},
        "gutter_inches": gutter_inches,
        "gutter_mm": gutter_mm,
        "outer_margin_inches": outer_margin_inches,
        "outer_margin_mm": outer_margin_mm,
        "spine_inches": spine_inches,
        "spine_mm": spine_mm,
        "spine_text_allowed": spine_text_allowed,
        "cover_total_inches": {"width": cover_w_in, "height": cover_h_in},
        "cover_total_mm": {"width": cover_w_mm, "height": cover_h_mm},
        "cover_300dpi_px": [cover_w_px, cover_h_px],
        "isbn_box_px": [600, 360],
        "etsy_print_formats": etsy_print_formats,
        "low_content_flag": bool(mod.get("low_content_flag", False)),
        "validation_warnings": validation_warnings,
    }
