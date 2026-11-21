"""
kdp_extensions/cover_calculator.py - Calcul dimensionnel exact pour couverture Amazon KDP.
(Trim + Bleed + Spine au micron, gabarits SVG 300 DPI, réserve ISBN).

Ce module implémente les spécifications industrielles d'Amazon KDP :
1. Calcul précis de l'épaisseur du dos (Spine) selon le grammage/type de papier :
   - white          : 0.002252 in / page (50 lb papier blanc)
   - cream          : 0.002500 in / page (55 lb papier crème)
   - color_standard : 0.002349 in / page (50 lb papier couleur standard)
   - color_premium  : 0.002500 in / page (60 lb papier couleur premium)
2. Fond perdu (Bleed) normalisé KDP : 0.125 pouce (3.175 mm) sur les 4 côtés extérieurs.
3. Formats de coupe (Trim) : intégration complète des 16 formats officiels KDP.
4. Règle du texte sur le dos : impression du texte autorisée par Amazon uniquement
   à partir de 79 pages (épaisseur minimale pour repérage de pliure fiable).
5. Réserve normalisée pour le code-barres ISBN : 2.0" × 1.2" (600 × 360 px @300 DPI)
   positionnée en bas à droite de la 4ème de couverture (0.25" du bord de coupe).
6. Export SVG vectoriel haute précision avec calques de repérage (plis, coupe, marges de sécurité).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
from kdp_extensions.kdp_dimensions import (
    KDP_FORMATS,
    KDP_FORMAT_IDS,
    PAPER_SPINE_COEFFS,
    normalize_format,
)

DPI_DEFAULT = 300
BLEED_STANDARD_IN = 0.125
ISBN_WIDTH_IN = 2.0
ISBN_HEIGHT_IN = 1.2
ISBN_WIDTH_PX = 600
ISBN_HEIGHT_PX = 360
MIN_PAGES_FOR_SPINE_TEXT = 79
SPINE_TEXT_SAFETY_MARGIN_IN = 0.0625  # 1/16 pouce de chaque pli de tranche
SAFETY_MARGIN_TRIM_IN = 0.25         # Marge de sécurité texte/logos vis-à-vis de la coupe


def calculate_cover_dimensions(
    trim_id: str = "6x9",
    page_count: int = 150,
    paper_type: str = "white",
    bleed: float = BLEED_STANDARD_IN,
    dpi: int = DPI_DEFAULT,
    language: str = "fr",
    is_rtl: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Calcule au micron toutes les cotes d'une couverture complète Amazon KDP
    (Plat 4 + Dos + Plat 1 + Fond Perdu).
    Supporte l'inversion géométrique RTL pour l'Arabe (Plat 1 à gauche, Plat 4 à droite).

    Parameters
    ----------
    trim_id : identifiant du format ('6x9', '8.5x11', etc.)
    page_count : nombre exact de pages du livre (>= 1)
    paper_type : 'white' | 'cream' | 'color_standard' | 'color_premium'
    bleed : fond perdu en pouces (défaut 0.125")
    dpi : résolution de calcul (défaut 300 DPI)
    language : code langue ('fr', 'en', 'es', 'de', 'ar')
    is_rtl : orientation droite-à-gauche explicite (optionnel)
    """
    fid = normalize_format(trim_id)
    trim_w_in, trim_h_in = KDP_FORMATS[fid]

    if not isinstance(page_count, int) or page_count < 1:
        raise ValueError(f"Le nombre de pages doit être un entier >= 1 (reçu: {page_count})")

    paper_key = (paper_type or "white").strip().lower()
    if paper_key not in PAPER_SPINE_COEFFS:
        raise ValueError(
            f"Type de papier inconnu: '{paper_type}'. Valides: {', '.join(PAPER_SPINE_COEFFS.keys())}"
        )

    spine_coeff = PAPER_SPINE_COEFFS[paper_key]
    spine_w_in = round(page_count * spine_coeff, 6)
    spine_w_mm = round(spine_w_in * 25.4, 3)

    bleed_in = max(0.0, float(bleed))
    bleed_mm = round(bleed_in * 25.4, 3)

    rtl_mode = (
        is_rtl if is_rtl is not None
        else (language or "").strip().lower() in ("ar", "arabic", "العربية")
    )

    # Largeur totale = Bleed_G + Plat4 + Dos + Plat1 + Bleed_D
    total_w_in = round((trim_w_in * 2.0) + spine_w_in + (bleed_in * 2.0), 6)
    total_h_in = round(trim_h_in + (bleed_in * 2.0), 6)

    total_w_mm = round(total_w_in * 25.4, 3)
    total_h_mm = round(total_h_in * 25.4, 3)

    total_w_px = int(round(total_w_in * dpi))
    total_h_px = int(round(total_h_in * dpi))

    # Coordonnées des zones (X_start, X_end) en pouces
    if rtl_mode:
        # En RTL (Arabe) : Face avant à GAUCHE, Tranche au CENTRE, Dos à DROITE
        plat1_x_start = bleed_in
        plat1_x_end = plat1_x_start + trim_w_in

        spine_x_start = plat1_x_end
        spine_x_end = spine_x_start + spine_w_in

        plat4_x_start = spine_x_end
        plat4_x_end = plat4_x_start + trim_w_in
    else:
        # 1. Plat 4 (Quatrième de couverture / dos gauche)
        plat4_x_start = bleed_in
        plat4_x_end = plat4_x_start + trim_w_in

        # 2. Dos (Spine / tranche)
        spine_x_start = plat4_x_end
        spine_x_end = spine_x_start + spine_w_in

        # 3. Plat 1 (Première de couverture / face avant)
        plat1_x_start = spine_x_end
        plat1_x_end = plat1_x_start + trim_w_in

    y_cut_top = bleed_in
    y_cut_bottom = y_cut_top + trim_h_in

    # Possibilité de texte sur le dos
    can_have_spine_text = page_count >= MIN_PAGES_FOR_SPINE_TEXT
    spine_text_safe_w_in = max(0.0, round(spine_w_in - (2 * SPINE_TEXT_SAFETY_MARGIN_IN), 6))

    # Réserve ISBN sur le Plat 4
    isbn_margin_bottom = SAFETY_MARGIN_TRIM_IN
    isbn_margin_spine = 0.375  # distance de sécurité vis-à-vis de la rainure de tranche

    isbn_x_in = round(plat4_x_end - isbn_margin_spine - ISBN_WIDTH_IN, 4)
    if isbn_x_in < plat4_x_start + SAFETY_MARGIN_TRIM_IN:
        isbn_x_in = round(plat4_x_start + SAFETY_MARGIN_TRIM_IN, 4)

    isbn_y_in = round(y_cut_bottom - isbn_margin_bottom - ISBN_HEIGHT_IN, 4)

    # Conversion en pixels 300 DPI
    def to_px(val_in: float) -> int:
        return int(round(val_in * dpi))

    def to_rect_px(x_in: float, y_in: float, w_in: float, h_in: float) -> Dict[str, int]:
        return {
            "x": to_px(x_in),
            "y": to_px(y_in),
            "width": to_px(w_in),
            "height": to_px(h_in),
        }

    return {
        "format_id": fid,
        "page_count": page_count,
        "paper_type": paper_key,
        "dpi": dpi,
        "is_rtl": rtl_mode,
        "language": language,
        "units": {
            "inches": {
                "total_width": total_w_in,
                "total_height": total_h_in,
                "trim_width": trim_w_in,
                "trim_height": trim_h_in,
                "spine_width": spine_w_in,
                "bleed": bleed_in,
                "safety_margin": SAFETY_MARGIN_TRIM_IN,
            },
            "millimeters": {
                "total_width": total_w_mm,
                "total_height": total_h_mm,
                "trim_width": round(trim_w_in * 25.4, 2),
                "trim_height": round(trim_h_in * 25.4, 2),
                "spine_width": spine_w_mm,
                "bleed": bleed_mm,
            },
            "pixels": {
                "total_width": total_w_px,
                "total_height": total_h_px,
                "trim_width": to_px(trim_w_in),
                "trim_height": to_px(trim_h_in),
                "spine_width": to_px(spine_w_in),
                "bleed": to_px(bleed_in),
            },
        },
        "spine_spec": {
            "width_in": spine_w_in,
            "width_mm": spine_w_mm,
            "width_px": to_px(spine_w_in),
            "coeff_per_page": spine_coeff,
            "can_print_text": can_have_spine_text,
            "min_pages_required": MIN_PAGES_FOR_SPINE_TEXT,
            "text_safe_width_in": spine_text_safe_w_in,
            "text_safe_width_px": to_px(spine_text_safe_w_in),
        },
        "zones_px": {
            "full_wrap": {"x": 0, "y": 0, "width": total_w_px, "height": total_h_px},
            "plat4_back": to_rect_px(plat4_x_start, y_cut_top, trim_w_in, trim_h_in),
            "spine": to_rect_px(spine_x_start, y_cut_top, spine_w_in, trim_h_in),
            "plat1_front": to_rect_px(plat1_x_start, y_cut_top, trim_w_in, trim_h_in),
            "isbn_reservation": to_rect_px(isbn_x_in, isbn_y_in, ISBN_WIDTH_IN, ISBN_HEIGHT_IN),
        },
        "fold_lines_px": {
            "spine_left_x": to_px(spine_x_start),
            "spine_right_x": to_px(spine_x_end),
            "trim_top_y": to_px(y_cut_top),
            "trim_bottom_y": to_px(y_cut_bottom),
        },
        "safe_zones_px": {
            "front_safe": to_rect_px(
                plat1_x_start + SAFETY_MARGIN_TRIM_IN,
                y_cut_top + SAFETY_MARGIN_TRIM_IN,
                trim_w_in - (2 * SAFETY_MARGIN_TRIM_IN),
                trim_h_in - (2 * SAFETY_MARGIN_TRIM_IN),
            ),
            "back_safe": to_rect_px(
                plat4_x_start + SAFETY_MARGIN_TRIM_IN,
                y_cut_top + SAFETY_MARGIN_TRIM_IN,
                trim_w_in - (2 * SAFETY_MARGIN_TRIM_IN),
                trim_h_in - (2 * SAFETY_MARGIN_TRIM_IN),
            ),
        },
    }


def generate_cover_template_svg(
    specs_or_trim: Any,
    page_count: int = 150,
    paper_type: str = "white",
    book_title: str = "TITRE DU LIVRE",
    author_name: str = "NOM DE L'AUTEUR",
    subtitle: str = "SOUS-TITRE ÉDITORIAL",
    language: str = "fr",
    is_rtl: Optional[bool] = None,
) -> str:
    """
    Génère un gabarit SVG vectoriel interactif et print-ready respectant
    scrupuleusement les spécifications d'Amazon KDP.
    Supporte l'inversion géométrique RTL (Face avant à gauche, 4ème + ISBN à droite).
    """
    if isinstance(specs_or_trim, dict) and "units" in specs_or_trim:
        specs = specs_or_trim
    else:
        specs = calculate_cover_dimensions(
            trim_id=str(specs_or_trim),
            page_count=page_count,
            paper_type=paper_type,
            language=language,
            is_rtl=is_rtl,
        )

    w_px = specs["units"]["pixels"]["total_width"]
    h_px = specs["units"]["pixels"]["total_height"]
    spine_x = specs["fold_lines_px"]["spine_left_x"]
    spine_r = specs["fold_lines_px"]["spine_right_x"]
    trim_top = specs["fold_lines_px"]["trim_top_y"]
    trim_bottom = specs["fold_lines_px"]["trim_bottom_y"]

    p1 = specs["zones_px"]["plat1_front"]
    p4 = specs["zones_px"]["plat4_back"]
    sp = specs["zones_px"]["spine"]
    isbn = specs["zones_px"]["isbn_reservation"]
    safe_front = specs["safe_zones_px"]["front_safe"]

    can_spine = specs["spine_spec"]["can_print_text"]
    spine_label = "TEXTE SUR LE DOS AUTORISÉ" if can_spine else "DOS TROP FIN (PAS DE TEXTE < 79p)"
    is_rtl_mode = bool(specs.get("is_rtl", False))

    trim_min_x = min(p1["x"], p4["x"])
    trim_max_x = max(p1["x"] + p1["width"], p4["x"] + p4["width"])
    trim_w_span = trim_max_x - trim_min_x

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_px} {h_px}" width="100%" height="100%" style="background-color:#0a0f1d; font-family:'Inter', Arial, sans-serif;">
  <defs>
    <!-- Pattern de grille technique -->
    <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
      <path d="M 60 0 L 0 0 0 60" fill="none" stroke="#1e293b" stroke-width="1" />
    </pattern>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDE047" />
      <stop offset="50%" stop-color="#D4AF37" />
      <stop offset="100%" stop-color="#A16207" />
    </linearGradient>
  </defs>

  <!-- Fond technique -->
  <rect width="{w_px}" height="{h_px}" fill="url(#grid)" />

  <!-- Fond Perdu Externe (Zone rouge de coupe) -->
  <rect x="0" y="0" width="{w_px}" height="{h_px}" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="12,6" />

  <!-- Ligne de Coupe Réelle (Trim Line) -->
  <rect x="{trim_min_x}" y="{trim_top}" width="{trim_w_span}" height="{trim_bottom - trim_top}" fill="none" stroke="#f8fafc" stroke-width="2" />

  <!-- Plat 4 (Arrière) -->
  <rect x="{p4['x']}" y="{p4['y']}" width="{p4['width']}" height="{p4['height']}" fill="#0f172a" fill-opacity="0.6" stroke="#334155" stroke-width="1" />
  <text x="{p4['x'] + p4['width']/2}" y="{trim_top + 80}" fill="#94a3b8" font-size="28" font-weight="700" text-anchor="middle" letter-spacing="4">{('4ÈME DE COUVERTURE (RTL - DROITE)' if is_rtl_mode else '4ÈME DE COUVERTURE (DOS DU LIVRE)')}</text>

  <!-- Dos / Tranche (Spine) -->
  <rect x="{sp['x']}" y="{sp['y']}" width="{sp['width']}" height="{sp['height']}" fill="#1e293b" fill-opacity="0.8" stroke="#3b82f6" stroke-width="2" stroke-dasharray="8,4" />
  <g transform="translate({sp['x'] + sp['width']/2}, {trim_top + (trim_bottom - trim_top)/2}) rotate(-90)">
    <text x="0" y="5" fill="#fde047" font-size="{min(24, max(12, int(sp['width'] * 0.4)))}" font-weight="700" text-anchor="middle" letter-spacing="2">
      {book_title} — {author_name}
    </text>
  </g>

  <!-- Plat 1 (Face Avant) -->
  <rect x="{p1['x']}" y="{p1['y']}" width="{p1['width']}" height="{p1['height']}" fill="#0d1527" fill-opacity="0.6" stroke="#d4af37" stroke-width="1.5" />
  <text x="{p1['x'] + p1['width']/2}" y="{trim_top + 80}" fill="#d4af37" font-size="28" font-weight="700" text-anchor="middle" letter-spacing="4">{('1ÈRE DE COUVERTURE (RTL - GAUCHE)' if is_rtl_mode else '1ÈRE DE COUVERTURE (FACE AVANT)')}</text>

  <!-- Zone de sécurité Plat 1 (Marges texte) -->
  <rect x="{safe_front['x']}" y="{safe_front['y']}" width="{safe_front['width']}" height="{safe_front['height']}" fill="none" stroke="#10b981" stroke-width="1.5" stroke-dasharray="6,6" />
  <text x="{safe_front['x'] + 20}" y="{safe_front['y'] + 40}" fill="#10b981" font-size="14" font-weight="600">ZONE SÉCURISÉE TEXTE (MARGE 0.25")</text>

  <!-- Aperçu Titre & Auteur sur Plat 1 -->
  <text x="{p1['x'] + p1['width']/2}" y="{trim_top + p1['height']*0.35}" fill="url(#goldGrad)" font-size="44" font-weight="800" text-anchor="middle" font-family="'Cinzel', serif">
    {book_title}
  </text>
  <text x="{p1['x'] + p1['width']/2}" y="{trim_top + p1['height']*0.42}" fill="#cbd5e1" font-size="20" font-weight="500" text-anchor="middle">
    {subtitle}
  </text>
  <text x="{p1['x'] + p1['width']/2}" y="{trim_top + p1['height']*0.82}" fill="#f8fafc" font-size="24" font-weight="600" text-anchor="middle">
    {author_name}
  </text>

  <!-- Réserve Code-Barres ISBN (600x360 px) -->
  <rect x="{isbn['x']}" y="{isbn['y']}" width="{isbn['width']}" height="{isbn['height']}" fill="#ffffff" stroke="#94a3b8" stroke-width="2" rx="4" />
  <text x="{isbn['x'] + isbn['width']/2}" y="{isbn['y'] + isbn['height']/2 - 10}" fill="#0f172a" font-size="18" font-weight="800" text-anchor="middle">RÉSERVE ISBN / CODE-BARRES</text>
  <text x="{isbn['x'] + isbn['width']/2}" y="{isbn['y'] + isbn['height']/2 + 18}" fill="#64748b" font-size="14" font-weight="600" text-anchor="middle">600 × 360 px (2.0" × 1.2")</text>

  <!-- Bandeau d'informations techniques en bas -->
  <rect x="0" y="{h_px - 60}" width="{w_px}" height="60" fill="#030712" fill-opacity="0.9" />
  <text x="30" y="{h_px - 25}" fill="#94a3b8" font-size="16" font-family="monospace">
    GABARIT KDP 300 DPI • Format: {specs['format_id']} • Pages: {specs['page_count']} • Dos: {specs['spine_spec']['width_in']:.4f}" ({specs['spine_spec']['width_mm']} mm) • Wrap Total: {w_px} × {h_px} px • {spine_label}
  </text>
</svg>"""
    return svg


def generate_cover_specs_report(specs: Dict[str, Any]) -> str:
    """Produit un rapport textuel clair de vérification prépresse."""
    u_in = specs["units"]["inches"]
    u_px = specs["units"]["pixels"]
    sp = specs["spine_spec"]

    return (
        f"=================================================================\n"
        f"📐 RAPPORT DE DIMENSIONS PRÉPRESSE COUVERTURE KDP (MarkEddy)\n"
        f"=================================================================\n"
        f"• Format de coupe (Trim)   : {specs['format_id']} ({u_in['trim_width']}\" × {u_in['trim_height']}\")\n"
        f"• Nombre de pages          : {specs['page_count']} pages (papier {specs['paper_type']})\n"
        f"• Épaisseur du dos (Spine) : {sp['width_in']:.4f} po ({sp['width_mm']} mm) [{u_px['spine_width']} px @300 DPI]\n"
        f"• Texte sur le dos         : {'AUTORISÉ (>= 79 pages)' if sp['can_print_text'] else 'INTERDIT (< 79 pages)'}\n"
        f"• Fond perdu (Bleed)       : {u_in['bleed']}\" sur les 4 côtés extérieurs\n"
        f"• Marge de sécurité texte  : {u_in['safety_margin']}\" depuis la ligne de coupe\n"
        f"• Dimensions complètes     : {u_in['total_width']:.4f}\" × {u_in['total_height']:.4f}\"\n"
        f"• Résolution d'impression  : {u_px['total_width']} × {u_px['total_height']} px @ {specs['dpi']} DPI\n"
        f"• Réserve Code-barres ISBN : 600 × 360 px (Plat 4 bas-droite)\n"
        f"================================================================="
    )


__all__ = [
    "calculate_cover_dimensions",
    "generate_cover_template_svg",
    "generate_cover_specs_report",
    "MIN_PAGES_FOR_SPINE_TEXT",
    "BLEED_STANDARD_IN",
    "ISBN_WIDTH_PX",
    "ISBN_HEIGHT_PX",
]
