"""
kdp_dimensions.py - Référentiel officiel des 16 formats Amazon KDP.

Fournit :
1. Les 16 formats de coupe (trim) officiels Amazon KDP.
2. calculate_kdp_specs(trim_id, page_count, paper_type="white", bleed=True)
   -> marges dynamiques KDP, épaisseur de dos (white / cream / color_standard /
      color_premium), dimensions 300 DPI de l'intérieur et de la couverture
      complète, et réserve ISBN (600 x 360 px).

Constantes industrielles :
- Fond perdu (bleed) standard KDP : 0.125 pouce sur tout le pourtour.
- Coefficients d'épaisseur de tranche (pouce / page, papier KDP standard) :
    white          = 0.002252
    cream          = 0.0025
    color_standard = 0.002349
    color_premium  = 0.0025
- Résolution de prépresse : 300 DPI.
- Réserve code-barres ISBN : 600 x 360 px.
"""

from typing import Dict, List, Tuple, Any

# ==============================================================================
# 1. LES 16 FORMATS OFFICIELS AMAZON KDP (largeur x hauteur, en pouces)
# ==============================================================================

KDP_FORMATS: Dict[str, Tuple[float, float]] = {
    "5x8": (5.0, 8.0),
    "5.06x7.81": (5.06, 7.81),
    "5.25x8": (5.25, 8.0),
    "5.5x8.5": (5.5, 8.5),
    "6x9": (6.0, 9.0),
    "6.14x9.21": (6.14, 9.21),
    "6.69x9.61": (6.69, 9.61),
    "7x10": (7.0, 10.0),
    "7.44x9.69": (7.44, 9.69),
    "7.5x9.25": (7.5, 9.25),
    "8.25x6": (8.25, 6.0),
    "8.25x8.25": (8.25, 8.25),
    "8.5x8.5": (8.5, 8.5),
    "8x10": (8.0, 10.0),
    "8.5x11": (8.5, 11.0),
    "8.27x11.69": (8.27, 11.69),
}

# Les 16 IDs dans l'ordre officiel de publication KDP
KDP_FORMAT_IDS: List[str] = list(KDP_FORMATS.keys())

BLEED_IN = 0.125            # Fond perdu KDP standard (pouce)
DPI = 300                   # Résolution de prépresse industrielle
ISBN_ZONE_PX = (600, 360)   # Réserve code-barres ISBN (largeur x hauteur en px)

# Épaisseur de tranche en pouces par page selon le type de papier KDP
PAPER_SPINE_COEFFS: Dict[str, float] = {
    "white": 0.002252,
    "cream": 0.0025,
    "color_standard": 0.002349,
    "color_premium": 0.0025,
}

# Marges de texte minimales KDP (pouces) mesurées depuis la ligne de coupe
MARGIN_TOP_IN = 0.25
MARGIN_BOTTOM_IN = 0.25
MARGIN_OUTSIDE_IN = 0.25


# ==============================================================================
# 2. UTILITAIRES DE FORMAT
# ==============================================================================

def normalize_format(trim_id: str) -> str:
    """
    Normalise un identifiant de format KDP ('6x9', '6.0 x 9.0', '8.5×11'...).
    Lève ValueError si le format n'appartient pas aux 16 formats officiels.
    """
    if not trim_id or not isinstance(trim_id, str):
        raise ValueError("Identifiant de format KDP vide ou invalide.")

    brut = trim_id.strip().lower().replace(" ", "").replace("×", "x").replace("*", "x")

    # Correspondance exacte sur les 16 IDs officiels
    if brut in KDP_FORMATS:
        return brut

    # Tolérance : '6.0x9.0' -> '6x9'
    if "x" in brut:
        try:
            larg_s, haut_s = brut.split("x", 1)
            larg, haut = float(larg_s), float(haut_s)
        except ValueError:
            raise ValueError(f"Format KDP non reconnu : '{trim_id}'.")
        for fid, (fw, fh) in KDP_FORMATS.items():
            if abs(fw - larg) < 0.02 and abs(fh - haut) < 0.02:
                return fid

    raise ValueError(
        f"Format KDP non reconnu : '{trim_id}'. "
        f"Formats officiels acceptés : {', '.join(KDP_FORMAT_IDS)}"
    )


def list_kdp_formats() -> List[Dict[str, Any]]:
    """Retourne la liste descriptive des 16 formats KDP (pour l'API / l'UI)."""
    return [
        {
            "id": fid,
            "width_in": dims[0],
            "height_in": dims[1],
            "label": f'{fid.replace("x", '" × "')} po',
        }
        for fid, dims in KDP_FORMATS.items()
    ]


# ==============================================================================
# 3. CALCUL DYNAMIQUE DES SPÉCIFICATIONS KDP
# ==============================================================================

def _gutter_in(page_count: int) -> float:
    """
    Marge de reliure (gutter) dynamique selon le nombre de pages (règle KDP) :
    - jusqu'à 150 pages  : 0.375"
    - 151 à 300 pages    : 0.500"
    - 301 à 400 pages    : 0.625"
    - plus de 400 pages  : 0.750"
    """
    if page_count <= 150:
        return 0.375
    if page_count <= 300:
        return 0.500
    if page_count <= 400:
        return 0.625
    return 0.750


def calculate_kdp_specs(
    trim_id: str,
    page_count: int,
    paper_type: str = "white",
    bleed: bool = True
) -> Dict[str, Any]:
    """
    Calcule l'ensemble des spécifications d'impression KDP pour un format donné.

    Paramètres
    ----------
    trim_id    : l'un des 16 identifiants de format officiels ('6x9', '8.5x11'...).
    page_count : nombre de pages de l'intérieur (>= 1).
    paper_type : 'white' | 'cream' | 'color_standard' | 'color_premium'.
    bleed      : True (défaut) pour un fond perdu de 0.125" sur tout le pourtour.

    Retourne un dictionnaire contenant :
    - trim            : dimensions de coupe en pouces.
    - spine           : épaisseur de dos en pouces (coeff x page_count).
    - margins         : marges dynamiques (gutter / outside / top / bottom).
    - interior        : dimensions intérieures avec fond perdu, en pouces et px @300 DPI.
    - cover           : dimensions de la couverture complète (Plat 1 + Dos + Plat 4),
                        en pouces et px @300 DPI.
    - isbn_reserve_px : réserve code-barres (600 x 360 px).
    """
    fid = normalize_format(trim_id)

    try:
        page_count = int(page_count)
    except (TypeError, ValueError):
        raise ValueError("page_count doit être un entier positif.")
    if page_count < 1:
        raise ValueError("page_count doit être >= 1.")

    paper_key = (paper_type or "white").strip().lower()
    if paper_key not in PAPER_SPINE_COEFFS:
        raise ValueError(
            f"Type de papier inconnu : '{paper_type}'. "
            f"Options : {', '.join(PAPER_SPINE_COEFFS.keys())}"
        )

    trim_w, trim_h = KDP_FORMATS[fid]

    # --- Dos (tranche) -------------------------------------------------------
    coeff = PAPER_SPINE_COEFFS[paper_key]
    spine_in = round(page_count * coeff, 6)

    # --- Marges dynamiques ---------------------------------------------------
    gutter_in = _gutter_in(page_count)
    margins = {
        "gutter_in": gutter_in,
        "outside_in": MARGIN_OUTSIDE_IN,
        "top_in": MARGIN_TOP_IN,
        "bottom_in": MARGIN_BOTTOM_IN,
    }

    bleed_in = BLEED_IN if bleed else 0.0
    if bleed:
        # Avec fond perdu, toutes les marges de sécurité augmentent du bleed
        # afin de rester à distance constante de la ligne de coupe.
        margins = {k: round(v + bleed_in, 4) for k, v in margins.items()}

    # --- Intérieur (avec fond perdu) ----------------------------------------
    interior_w_in = round(trim_w + (bleed_in * 2), 4)
    interior_h_in = round(trim_h + (bleed_in * 2), 4)
    interior = {
        "width_in": interior_w_in,
        "height_in": interior_h_in,
        "width_px": int(round(interior_w_in * DPI)),
        "height_px": int(round(interior_h_in * DPI)),
        "dpi": DPI,
    }

    # --- Couverture complète : Plat 4 + Dos + Plat 1 + 2 x bleed -------------
    cover_w_in = round((trim_w * 2) + spine_in + (bleed_in * 2), 4)
    cover_h_in = round(trim_h + (bleed_in * 2), 4)
    cover = {
        "width_in": cover_w_in,
        "height_in": cover_h_in,
        "width_px": int(round(cover_w_in * DPI)),
        "height_px": int(round(cover_h_in * DPI)),
        "dpi": DPI,
        "spine_in": spine_in,
        "bleed_in": bleed_in,
    }

    return {
        "trim_id": fid,
        "page_count": page_count,
        "paper_type": paper_key,
        "bleed": bool(bleed),
        "trim": {"width_in": trim_w, "height_in": trim_h},
        "spine": {
            "width_in": spine_in,
            "width_mm": round(spine_in * 25.4, 3),
            "coeff_per_page": coeff,
        },
        "margins": margins,
        "interior": interior,
        "cover": cover,
        "isbn_reserve_px": {"width": ISBN_ZONE_PX[0], "height": ISBN_ZONE_PX[1]},
    }


if __name__ == "__main__":
    print(f"Formats KDP officiels : {len(KDP_FORMAT_IDS)}")
    for fmt in KDP_FORMAT_IDS:
        print(f"  - {fmt}")
    print()
    specs = calculate_kdp_specs("8.5x11", page_count=80, paper_type="white", bleed=True)
    print("Exemple 8.5x11 / 80 pages / blanc / bleed :")
    print(f"  Dos            : {specs['spine']['width_in']:.4f} po")
    print(f"  Intérieur 300DPI: {specs['interior']['width_px']} x {specs['interior']['height_px']} px")
    print(f"  Couverture 300DPI: {specs['cover']['width_px']} x {specs['cover']['height_px']} px")
    print(f"  Gutter         : {specs['margins']['gutter_in']} po")
