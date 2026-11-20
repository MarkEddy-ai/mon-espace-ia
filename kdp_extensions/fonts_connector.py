"""
Connecteur Google Fonts API — MarkEddy KDP Studio (Sur-Ensemble Zéro-Casse)
Recherche des familles de polices Google Fonts + téléchargement local dans assets/fonts/
avec repli curé hors-ligne pour l'édition KDP (couvertures, intérieurs, coloriage).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
FONTS_CACHE_DIR = BASE_DIR / "assets" / "fonts"
GOOGLE_FONTS_ENDPOINT = "https://www.googleapis.com/webfonts/v1/webfonts"

CURATED_KDP_FONTS: List[Dict[str, Any]] = [
    {
        "family": "Fredoka",
        "category": "sans-serif",
        "usage": "Titres & Labels Enfants (4-8 ans)",
        "variants": ["regular", "500", "600", "700"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Nunito",
        "category": "sans-serif",
        "usage": "Texte & Consignes Enfants (4-8 ans)",
        "variants": ["regular", "600", "700", "800"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Baloo 2",
        "category": "display",
        "usage": "Titres Ludiques Enfants / Coloriage",
        "variants": ["regular", "600", "700", "800"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Cormorant Garamond",
        "category": "serif",
        "usage": "Titres Éditoriaux Raffinés",
        "variants": ["regular", "600", "700", "italic"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Lato",
        "category": "sans-serif",
        "usage": "Corps de Texte Clair & Lisible",
        "variants": ["regular", "700", "italic"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Libre Baskerville",
        "category": "serif",
        "usage": "Corps de Livre Classique KDP",
        "variants": ["regular", "700", "italic"],
        "subsets": ["latin"],
        "source": "curated_kdp",
    },
    {
        "family": "Playfair Display",
        "category": "serif",
        "usage": "Titre / Couverture Haute Couture",
        "variants": ["regular", "600", "700", "italic"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Merriweather",
        "category": "serif",
        "usage": "Corps de livre Non-Fiction (6x9)",
        "variants": ["300", "regular", "700", "italic"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Lora",
        "category": "serif",
        "usage": "Chapitres & Citations éditoriales",
        "variants": ["regular", "500", "700", "italic"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Inter",
        "category": "sans-serif",
        "usage": "Tableaux, Encadrés & UI Studio",
        "variants": ["regular", "500", "600", "700"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Montserrat",
        "category": "sans-serif",
        "usage": "Badges, Sous-titres & Couvertures",
        "variants": ["regular", "600", "700", "800"],
        "subsets": ["latin", "latin-ext"],
        "source": "curated_kdp",
    },
    {
        "family": "Cinzel",
        "category": "display",
        "usage": "Titres Prestige / Mythologie / Stoïcisme",
        "variants": ["regular", "600", "700"],
        "subsets": ["latin"],
        "source": "curated_kdp",
    },
]


def _get_fonts_api_key() -> str:
    return (
        os.getenv("GOOGLE_FONTS_API_KEY", "").strip()
        or os.getenv("GOOGLE_API_KEY", "").strip()
    )


def search_google_fonts(
    query: str = "",
    category: Optional[str] = None,
    sort: str = "popularity",
    limit: int = 12,
) -> Dict[str, Any]:
    """
    Interroge Google Fonts Developer API (v1/webfonts) si une clé est configurée,
    sinon retourne les polices KDP curées filtrées proprement.
    """
    api_key = _get_fonts_api_key()
    q_norm = (query or "").strip().lower()
    cat_norm = (category or "").strip().lower()

    if api_key and httpx is not None:
        try:
            params: Dict[str, Any] = {"key": api_key, "sort": sort}
            if cat_norm in ("serif", "sans-serif", "display", "handwriting", "monospace"):
                params["category"] = cat_norm
            with httpx.Client(timeout=8.0) as client:
                r = client.get(GOOGLE_FONTS_ENDPOINT, params=params)
            if r.status_code == 200:
                items = r.json().get("items", [])
                filtered: List[Dict[str, Any]] = []
                for it in items:
                    fam = it.get("family", "")
                    cat = it.get("category", "")
                    if q_norm and q_norm not in fam.lower() and q_norm not in cat.lower():
                        continue
                    filtered.append({
                        "family": fam,
                        "category": cat,
                        "variants": it.get("variants", []),
                        "subsets": it.get("subsets", []),
                        "files": it.get("files", {}),
                        "source": "google_fonts_api",
                    })
                    if len(filtered) >= max(1, min(limit, 50)):
                        break
                return {
                    "status": "success",
                    "mode": "live",
                    "count": len(filtered),
                    "fonts": filtered,
                }
        except Exception:
            pass

    fallback: List[Dict[str, Any]] = []
    for item in CURATED_KDP_FONTS:
        if cat_norm and item["category"].lower() != cat_norm:
            continue
        if q_norm and q_norm not in item["family"].lower() and q_norm not in item["usage"].lower():
            continue
        fallback.append(dict(item))
        if len(fallback) >= max(1, min(limit, 50)):
            break

    if not fallback:
        fallback = [dict(x) for x in CURATED_KDP_FONTS[:limit]]

    return {
        "status": "success",
        "mode": "curated_fallback",
        "count": len(fallback),
        "fonts": fallback,
    }


def download_font_file(
    font_url: str,
    family: str,
    variant: str = "regular",
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Télécharge un fichier de police (TTF/WOFF2) dans assets/fonts/ pour usage local."""
    if not font_url or not str(font_url).startswith(("http://", "https://")):
        raise ValueError("URL de police invalide.")
    if httpx is None:
        raise RuntimeError("httpx n'est pas installé.")

    target_dir = Path(output_dir) if output_dir else FONTS_CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", f"{family}_{variant}").strip("_").lower()
    ext = ".ttf"
    if ".woff2" in font_url.lower():
        ext = ".woff2"
    dest = target_dir / f"{safe_name}{ext}"

    with httpx.Client(timeout=12.0, follow_redirects=True) as client:
        r = client.get(font_url)
        r.raise_for_status()
        dest.write_bytes(r.content)

    return {
        "status": "downloaded",
        "family": family,
        "variant": variant,
        "file_path": str(dest),
        "size_bytes": dest.stat().st_size,
    }


def build_font_face_css(family: str, font_file_path: Optional[str] = None, fallback: str = "sans-serif") -> str:
    """Génère une règle @font-face locale si un fichier est présent, avec repli Google Fonts / système."""
    safe_fam = (family or "Nunito").replace("'", "")
    if font_file_path:
        uri = Path(font_file_path).resolve().as_uri()
        fmt = "truetype" if uri.lower().endswith(".ttf") else "woff2"
        return (
            f"@font-face {{\n"
            f"  font-family: '{safe_fam}';\n"
            f"  src: url('{uri}') format('{fmt}');\n"
            f"  font-display: swap;\n"
            f"}}\n"
            f"body {{ font-family: '{safe_fam}', {fallback}; }}"
        )
    return f"body {{ font-family: '{safe_fam}', {fallback}; }}"
