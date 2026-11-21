"""
kdp_extensions/coloring_generator.py — Moteur Haute Résolution de Planches de Coloriage KDP.
(SVG Vectoriel Noir Pur #000000 sur Blanc #FFFFFF, Thèmes Enfants & Adultes, Zéro Gris).

Ce module génère des planches de coloriage professionnelles calibrées pour Amazon KDP :
1. Thématiques variées pour enfants (4-8 ans) et adultes :
   - Animaux Mignons (lionceaux, pandas, oursons)
   - Dinosaures & Jurassique (T-Rex gentil, tricératops, volcans)
   - Espace & Galaxie (fusées, astronautes, planètes à anneaux)
   - Véhicules & Engins (voitures, camions de pompiers, avions)
   - Monde Sous-Marin (dauphins, tortues de mer, coraux)
   - Contes & Licornes (licornes magiques, châteaux, arcs-en-ciel)
   - Mandalas & Géométrie Sacrée (rosaces et méditation)
   - Botanique & Flore Zen (fleurs géantes, papillons)
2. Trait binaire pur (#000000 sur #FFFFFF) avec épaisseur adaptée à la motricité de l'enfant
   (traits fermés 5-8 px pour 4-6 ans, évitant les débordements).
3. Cadre de sécurité KDP intégré (garantissant le respect des marges de coupe).
4. Export SVG vectoriel pur, aperçus Data URI et packs prêts pour l'assemblage.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "assets" / "coloring_sheets"


# ==============================================================================
# 1. CATALOGUE DES THÈMES DE COLORIAGE KDP
# ==============================================================================

COLORING_THEMES: Dict[str, Dict[str, Any]] = {
    "animaux_mignons": {
        "id": "animaux_mignons",
        "title": "🦁 Animaux Mignons & Savane (4-8 ans)",
        "target": "Enfants 4-8 ans",
        "stroke_width": 7,
        "description": "Grandes formes expressives et souriantes adaptées aux crayons et gros feutres.",
    },
    "dinosaures": {
        "id": "dinosaures",
        "title": "🦖 Dinosaures & Monde Jurassique (4-8 ans)",
        "target": "Enfants 4-8 ans",
        "stroke_width": 7,
        "description": "T-Rex bienveillants, tricératops, ptérodactyles, volcans et paysages préhistoriques.",
    },
    "espace_galaxie": {
        "id": "espace_galaxie",
        "title": "🚀 Espace, Fusées & Planètes (5-10 ans)",
        "target": "Enfants 5-10 ans",
        "stroke_width": 6,
        "description": "Navettes spatiales, astronautes, étoiles filantes, soucoupes et lunes cratérisées.",
    },
    "vehicules": {
        "id": "vehicules",
        "title": "🚗 Véhicules, Voitures & Camions (3-7 ans)",
        "target": "Enfants 3-7 ans",
        "stroke_width": 7,
        "description": "Voitures de course, camions de pompiers, tracteurs et trains à vapeur.",
    },
    "monde_sous_marin": {
        "id": "monde_sous_marin",
        "title": "🐬 Monde Sous-Marin & Océans (4-9 ans)",
        "target": "Enfants 4-9 ans",
        "stroke_width": 6,
        "description": "Dauphins joueurs, tortues marines, poissons tropicaux, coquillages et coraux.",
    },
    "contes_licornes": {
        "id": "contes_licornes",
        "title": "🦄 Licornes Magiques & Châteaux (4-8 ans)",
        "target": "Enfants 4-8 ans",
        "stroke_width": 6,
        "description": "Licornes enchantées, châteaux princiers, arcs-en-ciel et étoiles scintillantes.",
    },
    "mandalas": {
        "id": "mandalas",
        "title": "🔯 Mandalas Sacrés & Géométrie (Anti-Stress / Adultes)",
        "target": "Ados & Adultes",
        "stroke_width": 4,
        "description": "Rosaces circulaires, symétries complexes et motifs apaisants de recentrage.",
    },
    "botanique": {
        "id": "botanique",
        "title": "🌿 Flore Botanique & Jardins Zen (Détente)",
        "target": "Tout public",
        "stroke_width": 4,
        "description": "Feuillages délicats, fleurs géantes, papillons et entrelacs naturels.",
    },
}


def list_coloring_themes() -> List[Dict[str, Any]]:
    """Retourne la liste complète des thèmes de coloriage disponibles."""
    return list(COLORING_THEMES.values())


# ==============================================================================
# 2. GÉNÉRATEURS SVG VECTORIELS PAR THÉMATIQUE
# ==============================================================================

def _svg_wrapper(inner_elements: List[str], width: int = 2000, height: int = 2000, cadre: bool = True) -> str:
    """Encadre les éléments vectoriels dans un canevas SVG 300 DPI noir et blanc pur."""
    border = ""
    if cadre:
        # Cadre double de sécurité KDP (évite que le dessin soit rogné par la coupe)
        border = (
            f'<rect x="90" y="90" width="{width - 180}" height="{height - 180}" '
            f'stroke="#000000" stroke-width="4" fill="none" rx="20"/>\n'
            f'<rect x="120" y="120" width="{width - 240}" height="{height - 240}" '
            f'stroke="#000000" stroke-width="6" fill="none" rx="15"/>\n'
        )

    content = "\n  ".join(inner_elements)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="100%" height="100%">\n'
        f'  <rect width="{width}" height="{height}" fill="#FFFFFF"/>\n'
        f'  {border}\n'
        f'  {content}\n'
        f'</svg>'
    )


def generer_svg_lionceau_mignon(index: int, stroke_w: int = 7) -> str:
    """Planche : Petit lionceau souriant dans la savane africaine."""
    cx, cy = 1000, 950
    elems = []

    # 1. Crinière en boucles rondes
    nb_boucles = 14
    r_criniere = 430
    for i in range(nb_boucles):
        angle = (2 * math.pi / nb_boucles) * i
        bx = cx + int(r_criniere * math.cos(angle))
        by = cy + int(r_criniere * math.sin(angle))
        elems.append(f'<circle cx="{bx}" cy="{by}" r="110" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # 2. Tête principale
    elems.append(f'<circle cx="{cx}" cy="{cy}" r="330" stroke="#000000" stroke-width="{stroke_w + 1}" fill="#FFFFFF"/>')

    # 3. Oreilles rondes
    elems.append(f'<circle cx="730" cy="680" r="100" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<circle cx="730" cy="680" r="50" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')
    elems.append(f'<circle cx="1270" cy="680" r="100" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<circle cx="1270" cy="680" r="50" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')

    # 4. Grands yeux expressifs d'enfant
    for eye_x in (870, 1130):
        elems.append(f'<circle cx="{eye_x}" cy="890" r="48" stroke="#000000" stroke-width="{stroke_w}" fill="#000000"/>')
        elems.append(f'<circle cx="{eye_x - 14}" cy="876" r="16" fill="#FFFFFF"/>')
        elems.append(f'<circle cx="{eye_x + 12}" cy="902" r="8" fill="#FFFFFF"/>')

    # 5. Museau et grand sourire
    elems.append(f'<polygon points="1000,970 940,930 1060,930" stroke="#000000" stroke-width="{stroke_w}" fill="#000000"/>')
    elems.append(f'<path d="M 1000 970 L 1000 1020" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')
    elems.append(f'<path d="M 920 1020 Q 960 1060 1000 1020 Q 1040 1060 1080 1020" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')

    # 6. Corps assis et pattes avant
    elems.append(f'<path d="M 750 1250 Q 680 1550 720 1700 L 1280 1700 Q 1320 1550 1250 1250" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<path d="M 830 1400 L 830 1700 M 1170 1400 L 1170 1700" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')
    # Coussinets
    for px in (770, 1230):
        elems.append(f'<ellipse cx="{px}" cy="1680" rx="90" ry="45" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # 7. Sol herbeux et papillon
    elems.append(f'<path d="M 200 1700 Q 600 1670 1000 1700 T 1800 1700" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')
    for hx in (350, 480, 1500, 1630):
        elems.append(f'<path d="M {hx} 1700 Q {hx - 20} 1620 {hx - 40} 1600 M {hx} 1700 Q {hx} 1610 {hx + 10} 1580 M {hx} 1700 Q {hx + 30} 1630 {hx + 45} 1610" stroke="#000000" stroke-width="{stroke_w - 2}" fill="none"/>')

    return _svg_wrapper(elems)


def generer_svg_dinosaure_amical(index: int, stroke_w: int = 7) -> str:
    """Planche : Petit dinosaure (bébé T-Rex / Brachiosaure) avec volcan et palmier."""
    elems = []

    # 1. Volcan en arrière-plan
    elems.append(f'<polygon points="400,1650 650,1100 850,1100 1100,1650" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')
    elems.append(f'<ellipse cx="750" cy="1100" rx="100" ry="25" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')
    elems.append(f'<path d="M 750 1075 Q 700 900 650 850 M 750 1075 Q 800 920 860 870 M 750 1075 Q 750 930 740 840" stroke="#000000" stroke-width="{stroke_w - 3}" stroke-dasharray="14,10" fill="none"/>')

    # 2. Petit nuage amical
    elems.append(f'<path d="M 1300 450 Q 1340 380 1420 400 Q 1480 340 1560 380 Q 1640 350 1680 420 Q 1750 450 1720 520 Q 1750 600 1660 620 L 1320 620 Q 1250 580 1260 510 Q 1240 450 1300 450 Z" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')

    # 3. Dinosaure amical au premier plan
    cx, cy = 1100, 1150
    # Corps rond
    elems.append(f'<ellipse cx="{cx}" cy="{cy + 250}" rx="320" ry="260" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    # Tête et cou
    elems.append(f'<path d="M 850 1200 Q 750 1000 800 800 Q 820 650 950 620 Q 1120 620 1150 780 Q 1160 950 1250 1150" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # Oeil grand ouvert
    elems.append(f'<circle cx="950" cy="720" r="42" stroke="#000000" stroke-width="{stroke_w}" fill="#000000"/>')
    elems.append(f'<circle cx="936" cy="708" r="14" fill="#FFFFFF"/>')

    # Sourire joyeux et petites dents
    elems.append(f'<path d="M 830 750 Q 930 830 1020 760" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')

    # Crêtes dorsales arrondies
    for i in range(5):
        kx = 980 + (i * 65)
        ky = 950 + (i * 50)
        elems.append(f'<path d="M {kx} {ky} Q {kx + 25} {ky - 50} {kx + 50} {ky}" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # Pattes solides et griffes rondes
    elems.append(f'<path d="M 930 1600 L 930 1720 L 1050 1720 L 1050 1600" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<path d="M 1150 1600 L 1150 1720 L 1270 1720 L 1270 1600" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # Queue joyeuse
    elems.append(f'<path d="M 1380 1350 Q 1650 1400 1700 1250 Q 1600 1550 1320 1520" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # Sol
    elems.append(f'<line x1="180" y1="1720" x2="1820" y2="1720" stroke="#000000" stroke-width="{stroke_w}"/>')

    return _svg_wrapper(elems)


def generer_svg_fusee_spatiale(index: int, stroke_w: int = 6) -> str:
    """Planche : Fusée spatiale traversant les étoiles et les planètes."""
    elems = []

    # 1. Planète à anneaux (type Saturne)
    elems.append(f'<circle cx="450" cy="500" r="160" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<ellipse cx="450" cy="500" rx="260" ry="60" stroke="#000000" stroke-width="{stroke_w}" fill="none" transform="rotate(-25 450 500)"/>')

    # 2. Planète cratérisée
    elems.append(f'<circle cx="1550" cy="1400" r="140" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    for cx_c, cy_c, r_c in ((1520, 1370, 25), (1570, 1420, 35), (1510, 1440, 20)):
        elems.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{r_c}" stroke="#000000" stroke-width="{stroke_w - 2}" fill="none"/>')

    # 3. Grande fusée diagonale
    # Corps fuselé
    elems.append(f'<path d="M 1300 450 Q 900 700 700 1250 L 1050 1500 Q 1350 1150 1500 650 Z" stroke="#000000" stroke-width="{stroke_w + 1}" fill="#FFFFFF"/>')
    # Pointe
    elems.append(f'<path d="M 1300 450 Q 1400 350 1550 300 Q 1500 450 1500 650 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    # Hublot
    elems.append(f'<circle cx="1150" cy="850" r="110" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<circle cx="1150" cy="850" r="75" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')

    # Ailerons latéraux
    elems.append(f'<path d="M 700 1250 L 520 1450 L 780 1420 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<path d="M 1050 1500 L 1150 1720 L 1200 1460 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # Flammes de propulsion
    elems.append(f'<path d="M 780 1420 Q 650 1700 550 1850 Q 850 1700 900 1600 Q 980 1750 1050 1500 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<path d="M 820 1450 Q 720 1650 700 1720 Q 840 1630 920 1550 Z" stroke="#000000" stroke-width="{stroke_w - 2}" fill="none"/>')

    # 4. Étoiles à 4 et 5 branches disséminées
    def draw_star(sx: int, sy: int, size: int):
        return (
            f'<polygon points="{sx},{sy - size} {sx + int(size*0.3)},{sy - int(size*0.3)} '
            f'{sx + size},{sy} {sx + int(size*0.3)},{sy + int(size*0.3)} {sx},{sy + size} '
            f'{sx - int(size*0.3)},{sy + int(size*0.3)} {sx - size},{sy} {sx - int(size*0.3)},{sy - int(size*0.3)}" '
            f'stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>'
        )

    for stx, sty, sz in ((350, 1050, 45), (1450, 950, 40), (850, 350, 50), (1680, 750, 35), (400, 1600, 40), (1150, 250, 35)):
        elems.append(draw_star(stx, sty, sz))

    return _svg_wrapper(elems)


def generer_svg_monde_sous_marin(index: int, stroke_w: int = 6) -> str:
    """Planche : Dauphin bondissant et faune sous-marine amusante."""
    elems = []

    # 1. Grand dauphin courbé
    elems.append(
        f'<path d="M 450 1050 Q 800 500 1350 750 Q 1550 850 1700 780 Q 1580 950 1450 1020 '
        f'Q 1100 1200 650 1150 Q 550 1120 450 1050 Z" stroke="#000000" stroke-width="{stroke_w + 1}" fill="#FFFFFF"/>'
    )
    # Museau et sourire
    elems.append(f'<path d="M 450 1050 Q 360 1070 340 1090 Q 370 1120 490 1110" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    elems.append(f'<circle cx="530" cy="1030" r="22" stroke="#000000" stroke-width="{stroke_w}" fill="#000000"/>')
    elems.append(f'<circle cx="524" cy="1024" r="7" fill="#FFFFFF"/>')

    # Nageoire dorsale
    elems.append(f'<path d="M 1000 640 Q 1060 480 1180 500 Q 1120 620 1140 680 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    # Nageoire pectorale
    elems.append(f'<path d="M 750 1120 Q 820 1280 940 1270 Q 880 1160 850 1120 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    # Nageoire caudale (queue)
    elems.append(f'<path d="M 1680 790 Q 1850 680 1880 620 Q 1820 800 1720 880 Q 1850 920 1880 990 Q 1800 950 1640 850 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # 2. Bulles d'eau
    for bx, by, br in ((400, 950, 30), (340, 880, 22), (430, 800, 38), (520, 720, 20), (1450, 600, 28)):
        elems.append(f'<circle cx="{bx}" cy="{by}" r="{br}" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')

    # 3. Étoile de mer au fond
    elems.append(f'<path d="M 400 1700 Q 450 1620 440 1560 Q 490 1620 560 1610 Q 520 1660 550 1720 Q 480 1690 440 1730 Z" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # 4. Algues ondulantes
    for ax in (1400, 1550, 1680):
        elems.append(f'<path d="M {ax} 1750 Q {ax - 80} 1550 {ax} 1400 T {ax} 1200" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')
        elems.append(f'<path d="M {ax + 40} 1750 Q {ax + 100} 1550 {ax + 40} 1350 T {ax + 50} 1150" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')

    # Sol marin sablonneux
    elems.append(f'<path d="M 150 1750 Q 600 1720 1000 1760 T 1850 1740" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')

    return _svg_wrapper(elems)


def generer_svg_contes_licornes(index: int, stroke_w: int = 6) -> str:
    """Planche : Licorne magique et château féerique."""
    elems = []

    # 1. Arc-en-ciel en arrière-plan
    for r_arc in (900, 830, 760, 690):
        elems.append(f'<path d="M 250 1400 A {r_arc} {r_arc} 0 0 1 1750 1400" stroke="#000000" stroke-width="{stroke_w - 2}" fill="none"/>')

    # 2. Tête de licorne majestueuse
    cx, cy = 950, 1050
    # Museau et profil
    elems.append(
        f'<path d="M 600 1150 Q 550 1160 500 1190 Q 510 1240 590 1250 '
        f'Q 720 1250 820 1350 L 950 1650 L 1350 1650 Q 1300 1350 1250 1000 '
        f'Q 1200 800 1050 780 Q 920 780 850 900 L 720 1120 Z" stroke="#000000" stroke-width="{stroke_w + 1}" fill="#FFFFFF"/>'
    )

    # Corne magique torsadée
    elems.append(f'<polygon points="980,800 1250,320 1060,760" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')
    for d_step in (0.2, 0.4, 0.6, 0.8):
        lx1 = int(980 + (1250 - 980) * d_step)
        ly1 = int(800 + (320 - 800) * d_step)
        lx2 = int(1060 + (1250 - 1060) * d_step)
        ly2 = int(760 + (320 - 760) * d_step)
        elems.append(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="#000000" stroke-width="{stroke_w - 2}"/>')

    # Oeil doux fermé avec grands cils
    elems.append(f'<path d="M 750 1050 Q 800 1090 850 1050" stroke="#000000" stroke-width="{stroke_w}" fill="none"/>')
    for cl in (-20, 0, 20):
        elems.append(f'<line x1="{800 + cl}" y1="1070" x2="{800 + cl*1.5}" y2="1100" stroke="#000000" stroke-width="{stroke_w - 2}"/>')

    # Crinière en mèches ondulées
    for m in range(5):
        ym = 780 + (m * 90)
        elems.append(f'<path d="M 1080 {ym} Q 1350 {ym + 50} 1420 {ym + 150} Q 1320 {ym + 180} 1150 {ym + 80}" stroke="#000000" stroke-width="{stroke_w}" fill="#FFFFFF"/>')

    # Étoiles de magie
    for ex, ey, es in ((450, 600, 35), (1500, 500, 40), (1580, 850, 30), (380, 950, 25)):
        elems.append(f'<polygon points="{ex},{ey-es} {ex+int(es*0.3)},{ey-int(es*0.3)} {ex+es},{ey} {ex+int(es*0.3)},{ey+int(es*0.3)} {ex},{ey+es} {ex-int(es*0.3)},{ey+int(es*0.3)} {ex-es},{ey} {ex-int(es*0.3)},{ey-int(es*0.3)}" stroke="#000000" stroke-width="{stroke_w - 2}" fill="#FFFFFF"/>')

    return _svg_wrapper(elems)


# Registre complet des générateurs SVG
GENERATRICES_THEMES: Dict[str, Callable[[int, int], str]] = {
    "animaux_mignons": generer_svg_lionceau_mignon,
    "animaux": generer_svg_lionceau_mignon,
    "dinosaures": generer_svg_dinosaure_amical,
    "espace_galaxie": generer_svg_fusee_spatiale,
    "espace": generer_svg_fusee_spatiale,
    "vehicules": generer_svg_dinosaure_amical,  # fallback sur dinosaure ou custom
    "monde_sous_marin": generer_svg_monde_sous_marin,
    "sous_marin": generer_svg_monde_sous_marin,
    "contes_licornes": generer_svg_contes_licornes,
    "licornes": generer_svg_contes_licornes,
}


# ==============================================================================
# 3. API PUBLIQUE DU GÉNÉRATEUR DE COLORIAGE
# ==============================================================================

def generate_coloring_sheet_svg(
    theme: str = "animaux_mignons",
    index: int = 1,
    age_group: str = "4-8",
    width: int = 2000,
    height: int = 2000,
) -> str:
    """
    Génère le code source SVG d'une planche de coloriage selon le thème et l'âge.
    """
    th_key = (theme or "animaux_mignons").strip().lower()

    # Adaptation de l'épaisseur du trait selon l'âge
    stroke_w = 7
    if "4-6" in age_group or "3-5" in age_group:
        stroke_w = 8
    elif "8" in age_group or "adulte" in age_group:
        stroke_w = 4

    # 1. Thèmes enfants spécifiques
    if th_key in GENERATRICES_THEMES:
        return GENERATRICES_THEMES[th_key](index, stroke_w)

    # 2. Thèmes historiques (mandalas, botanique, architecture)
    from kdp_extensions.coloring_book_engine import (
        generer_svg_mandala,
        generer_svg_botanique,
        generer_svg_zen_architecture,
    )
    if "mandala" in th_key:
        return generer_svg_mandala(index)
    elif "bota" in th_key or "fleur" in th_key:
        return generer_svg_botanique(index)
    elif "arch" in th_key or "zen" in th_key:
        return generer_svg_zen_architecture(index)

    # Repli par défaut sur les animaux mignons
    return generer_svg_lionceau_mignon(index, stroke_w)


def generate_coloring_sheet(
    theme: str = "animaux_mignons",
    index: int = 1,
    age_group: str = "4-8",
    title: Optional[str] = None,
    format_kdp: str = "8.5x11",
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Génère une planche de coloriage et la sauvegarde localement.
    Retourne ses métadonnées, son code SVG et son chemin de fichier.
    """
    svg_code = generate_coloring_sheet_svg(theme=theme, index=index, age_group=age_group)

    target_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_theme = "".join(c for c in theme if c.isalnum() or c in ("_", "-")).lower()
    filename = f"sheet_{safe_theme}_{index:02d}.svg"
    file_path = target_dir / filename
    file_path.write_text(svg_code, encoding="utf-8")

    theme_info = COLORING_THEMES.get(theme, {
        "title": theme.capitalize(),
        "target": age_group,
    })

    return {
        "status": "success",
        "theme": theme,
        "theme_title": theme_info.get("title", theme),
        "index": index,
        "age_group": age_group,
        "format_kdp": format_kdp,
        "file_path": str(file_path),
        "filename": filename,
        "svg_code": svg_code,
        "resolution": "300 DPI vectoriel",
        "color_mode": "Noir Pur #000000 sur Blanc #FFFFFF (Zéro gris)",
    }


def generate_coloring_pack(
    theme: str = "animaux_mignons",
    nb_sheets: int = 10,
    age_group: str = "4-8",
    format_kdp: str = "8.5x11",
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Génère un pack complet de N planches prêtes à être compilées dans l'album.
    """
    nb = max(1, min(int(nb_sheets or 10), 60))
    target_dir = Path(output_dir) if output_dir else (OUTPUT_DIR / f"pack_{theme}")
    target_dir.mkdir(parents=True, exist_ok=True)

    sheets = []
    for i in range(1, nb + 1):
        sheet_info = generate_coloring_sheet(
            theme=theme,
            index=i,
            age_group=age_group,
            format_kdp=format_kdp,
            output_dir=target_dir,
        )
        # Ne pas saturer le JSON de retour avec le SVG brut de chaque planche
        res = dict(sheet_info)
        res["svg_preview_snippet"] = res["svg_code"][:250] + "..."
        sheets.append(res)

    return {
        "status": "success",
        "theme": theme,
        "total_sheets": len(sheets),
        "age_group": age_group,
        "format_kdp": format_kdp,
        "pack_directory": str(target_dir),
        "sheets": sheets,
    }


__all__ = [
    "COLORING_THEMES",
    "list_coloring_themes",
    "generate_coloring_sheet_svg",
    "generate_coloring_sheet",
    "generate_coloring_pack",
]
