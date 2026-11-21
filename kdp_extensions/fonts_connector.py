"""
Connecteur Google Fonts API — MarkEddy KDP Studio (Sur-Ensemble Zéro-Casse)
Recherche des familles de polices Google Fonts + téléchargement local dans assets/fonts/
avec repli curé hors-ligne pour l'édition KDP (couvertures, intérieurs, coloriage).
"""
from __future__ import annotations

import os
import re
import unicodedata
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
    {
        "family": "Amiri",
        "category": "serif",
        "usage": "Typographie d'Artisan Arabe KDP (Naskh Classique)",
        "variants": ["regular", "700", "italic"],
        "subsets": ["arabic", "latin"],
        "source": "curated_kdp",
    },
    {
        "family": "Cairo",
        "category": "sans-serif",
        "usage": "Titres & Badges Arabes Modernes KDP",
        "variants": ["regular", "600", "700", "800"],
        "subsets": ["arabic", "latin"],
        "source": "curated_kdp",
    },
    {
        "family": "Noto Naskh Arabic",
        "category": "serif",
        "usage": "Corps de Livre Arabe KDP & Lisibilité Maximale",
        "variants": ["regular", "500", "600", "700"],
        "subsets": ["arabic"],
        "source": "curated_kdp",
    },
]


def _get_fonts_api_key() -> str:
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / ".env", override=False)
    except Exception:
        pass
    return (
        os.getenv("GOOGLE_FONTS_API_KEY", "").strip()
        or os.getenv("GOOGLE_API_KEY", "").strip()
    )


def _normaliser(texte: str) -> str:
    """Recherche insensible aux accents ('Éditoriaux' == 'editoriaux')."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", (texte or "").lower())
        if not unicodedata.combining(c)
    )


def _httpx_get_json(url: str, params: Optional[Dict[str, Any]] = None,
                    timeout: float = 8.0) -> Any:
    """Point de sortie HTTP unique (mockable dans les tests)."""
    if httpx is None:
        raise RuntimeError("httpx n'est pas installé")
    with httpx.Client(timeout=timeout) as client:
        r = client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()


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
    q_norm = _normaliser(query)
    cat_norm = (category or "").strip().lower()
    categories_valides = ("serif", "sans-serif", "display", "handwriting", "monospace")
    if cat_norm and cat_norm not in categories_valides:
        raise ValueError(
            f"Catégorie inconnue '{category}'. Catégories acceptées : {', '.join(categories_valides)}."
        )

    max_resultats = max(1, min(int(limit or 12), 50))

    if api_key and httpx is not None:
        try:
            params: Dict[str, Any] = {"key": api_key, "sort": sort}
            if cat_norm:
                params["category"] = cat_norm
            data = _httpx_get_json(GOOGLE_FONTS_ENDPOINT, params=params)
            filtered: List[Dict[str, Any]] = []
            for it in data.get("items", []):
                fam = it.get("family", "")
                cat = it.get("category", "")
                if q_norm and q_norm not in _normaliser(fam) and q_norm not in _normaliser(cat):
                    continue
                filtered.append({
                    "family": fam,
                    "category": cat,
                    "variants": it.get("variants", []),
                    "subsets": it.get("subsets", []),
                    "files": it.get("files", {}),
                    "source": "google_fonts_api",
                })
                if len(filtered) >= max_resultats:
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
        if q_norm and q_norm not in _normaliser(item["family"]) and q_norm not in _normaliser(item["usage"]):
            continue
        fallback.append(dict(item))
        if len(fallback) >= max_resultats:
            break

    # Repli sur la liste complète UNIQUEMENT si aucune recherche n'a été demandée.
    if not fallback and not q_norm and not cat_norm:
        fallback = [dict(x) for x in CURATED_KDP_FONTS[:max_resultats]]

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


# ==============================================================================
# PAIRINGS ÉDITORIAUX KDP (Typographie Haute Couture & Harmonie des Titres/Corps)
# ==============================================================================

EDITORIAL_FONT_PAIRINGS: Dict[str, Dict[str, Any]] = {
    "prestige_business": {
        "id": "prestige_business",
        "name": "Obsidienne & Or (Business & Finance)",
        "genre": "Finances, Business, Stratégie, Leadership, Patrimoine",
        "title_font": "Cinzel",
        "subtitle_font": "Montserrat",
        "body_font": "Merriweather",
        "accent_font": "Cormorant Garamond",
        "fallback_serif": "Georgia, serif",
        "fallback_sans": "'Segoe UI', sans-serif",
        "charte_chromatique": "Obsidienne & Or Impérial (#0A0F1D, #D4AF37, #F8FAFC)",
        "description": "Alliance impériale entre la monumentalité romaine de Cinzel et la lisibilité éditoriale de Merriweather.",
    },
    "luxe_patrimoine": {
        "id": "luxe_patrimoine",
        "name": "Émeraude Royale & Champagne (Immobilier & Luxe)",
        "genre": "Immobilier, Architecture, Luxe, Héritage, Investissement",
        "title_font": "Playfair Display",
        "subtitle_font": "Cormorant Garamond",
        "body_font": "Libre Baskerville",
        "accent_font": "Cinzel",
        "fallback_serif": "Baskerville, Garamond, serif",
        "fallback_sans": "'Helvetica Neue', sans-serif",
        "charte_chromatique": "Émeraude Royale & Champagne (#062C22, #C5A059, #FAF7F2)",
        "description": "Typographie haute couture d'inspiration Didot et Baskerville, élégance patrimoniale absolue.",
    },
    "tech_productivity": {
        "id": "tech_productivity",
        "name": "Saphir Majestueux & Argent (Tech, IA & Méthodes)",
        "genre": "Intelligence Artificielle, Tech, Productivité, Sciences, Méthodes",
        "title_font": "Inter",
        "subtitle_font": "Montserrat",
        "body_font": "Lato",
        "accent_font": "Cinzel",
        "fallback_serif": "sans-serif",
        "fallback_sans": "'Inter', system-ui, sans-serif",
        "charte_chromatique": "Saphir d'encre & Argent Platine (#0B192C, #00ADB5, #FFFFFF)",
        "description": "Précision chirurgicale et lisibilité moderne scandinave pour ouvrages techniques et guides d'efficacité.",
    },
    "stoicisme_philosophie": {
        "id": "stoicisme_philosophie",
        "name": "Bordeaux Grand Cru & Or Rose (Philosophie & Stoïcisme)",
        "genre": "Stoïcisme, Philosophie, Psychologie, Développement Personnel Profond",
        "title_font": "Cinzel",
        "subtitle_font": "Cormorant Garamond",
        "body_font": "Libre Baskerville",
        "accent_font": "Playfair Display",
        "fallback_serif": "Georgia, serif",
        "fallback_sans": "sans-serif",
        "charte_chromatique": "Bordeaux Grand Cru & Or Rose (#2C0B0E, #E8C5C8, #FFF8F8)",
        "description": "Gravité intellectuelle, noblesse des empattements classiques et sérénité méditative.",
    },
    "sante_bien_etre": {
        "id": "sante_bien_etre",
        "name": "Harmonie Vitale & Sérénité (Santé & Équilibre)",
        "genre": "Santé, Bien-être, Méditation, Sommeil, Nutrition, Longévité",
        "title_font": "Lora",
        "subtitle_font": "Montserrat",
        "body_font": "Lato",
        "accent_font": "Cormorant Garamond",
        "fallback_serif": "Georgia, serif",
        "fallback_sans": "'Segoe UI', sans-serif",
        "charte_chromatique": "Sauge & Crème Naturelle (#1B3B2B, #7EA172, #FDFBF7)",
        "description": "Douceur organique de Lora alliée à la limpidité moderne de Lato pour une lecture fluide et apaisante.",
    },
    "enfants_ludique": {
        "id": "enfants_ludique",
        "name": "Soleil & Joie (Livres Enfants & Activités 4-8 ans)",
        "genre": "Enfants, Coloriage, Éveil, Contes, Activités pédagogiques",
        "title_font": "Baloo 2",
        "subtitle_font": "Fredoka",
        "body_font": "Nunito",
        "accent_font": "Fredoka",
        "fallback_serif": "sans-serif",
        "fallback_sans": "'Comic Sans MS', cursive, sans-serif",
        "charte_chromatique": "Pastels Lumineux & Noir Pur (#2D3748, #ED8936, #FFFFFF)",
        "description": "Formes rondes, affectueuses et parfaitement lisibles pour jeunes lecteurs et cahiers d'activités.",
    },
    "fiction_roman": {
        "id": "fiction_roman",
        "name": "Littérature & Roman d'Auteur (Fiction & Récit)",
        "genre": "Roman, Thriller, Fiction Littéraire, Mémoires, Biographies",
        "title_font": "Cormorant Garamond",
        "subtitle_font": "Playfair Display",
        "body_font": "Libre Baskerville",
        "accent_font": "Lora",
        "fallback_serif": "Garamond, Baskerville, serif",
        "fallback_sans": "sans-serif",
        "charte_chromatique": "Noir Encre & Papier Lin (#111827, #6B7280, #FDFBF7)",
        "description": "La tradition séculaire des grandes maisons d'édition (Gallimard, Grasset) transposée sur Amazon KDP.",
    },
    "arabic_majestic": {
        "id": "arabic_majestic",
        "name": "Arabe Majestueux & Souverain (Amiri & Cairo)",
        "genre": "Édition Arabe KDP, Non-Fiction, Essais, Littérature, Affaires",
        "title_font": "Cairo",
        "subtitle_font": "Cairo",
        "body_font": "Amiri",
        "accent_font": "Noto Naskh Arabic",
        "fallback_serif": "'Traditional Arabic', 'Scheherazade New', serif",
        "fallback_sans": "'Segoe UI', 'Tahoma', sans-serif",
        "charte_chromatique": "Émeraude Royale & Or Impérial (#062C22, #D4AF37, #FAF7F2)",
        "description": "Calligraphie Naskh noble (Amiri) combinée à la lisibilité géométrique moderne de Cairo pour les titres arabes.",
    },
    "germanic_precision": {
        "id": "germanic_precision",
        "name": "Précision Germanique & Rigueur (EB Garamond & Cinzel)",
        "genre": "Édition Allemande KDP (Amazon.de), Sachbuch, Finanzen, Wirtschaft",
        "title_font": "Cinzel",
        "subtitle_font": "Montserrat",
        "body_font": "EB Garamond",
        "accent_font": "Cormorant Garamond",
        "fallback_serif": "Georgia, serif",
        "fallback_sans": "sans-serif",
        "charte_chromatique": "Obsidienne & Or Platine (#0A0F1D, #D4AF37, #F8FAFC)",
        "description": "Élégance éditoriale rigoureuse optimisée pour les longues césures de mots composés de la langue allemande.",
    },
    "spanish_modern": {
        "id": "spanish_modern",
        "name": "Espagnol Littéraire & Contemporain (Lora & Playfair)",
        "genre": "Édition Espagnole KDP (Amazon.es / MX), No-Ficción, Liderazgo, Finanzas",
        "title_font": "Playfair Display",
        "subtitle_font": "Montserrat",
        "body_font": "Lora",
        "accent_font": "Cormorant Garamond",
        "fallback_serif": "Georgia, serif",
        "fallback_sans": "sans-serif",
        "charte_chromatique": "Bordeaux Noble & Or (#2C0B0E, #D4AF37, #FFF8F8)",
        "description": "Empattements chantants et clairs pour les marchés hispanophones d'Espagne et d'Amérique Latine.",
    },
}


def list_editorial_pairings() -> List[Dict[str, Any]]:
    """Retourne la collection des pairings éditoriaux curés pour Amazon KDP."""
    return list(EDITORIAL_FONT_PAIRINGS.values())


def recommend_font_pairing(
    niche_or_genre: str,
    target_audience: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sélectionne automatiquement le pairing typographique optimal en fonction
    de la niche, du thème et du public cible.
    """
    texte = f"{niche_or_genre or ''} {target_audience or ''}".lower()
    t_norm = _normaliser(texte)

    # 1. Enfants / Coloriage / Activités
    if any(m in t_norm for m in ("enfant", "coloriage", "activite", "manga", "4-8", "jeunesse", "kids")):
        return dict(EDITORIAL_FONT_PAIRINGS["enfants_ludique"])

    # 2. Tech / IA / Productivité
    if any(m in t_norm for m in ("ia", "intelligence", "tech", "code", "informatique", "productivite", "systeme", "automatisation")):
        return dict(EDITORIAL_FONT_PAIRINGS["tech_productivity"])

    # 3. Stoïcisme / Philosophie / Psychologie
    if any(m in t_norm for m in ("stoic", "philosoph", "sagesse", "meditation", "psycholog", "esprit", "epictete", "aurele")):
        return dict(EDITORIAL_FONT_PAIRINGS["stoicisme_philosophie"])

    # 4. Santé / Bien-être / Nutrition
    if any(m in t_norm for m in ("sante", "sommeil", "bien-etre", "nutrition", "regime", "guerison", "corps", "respiration")):
        return dict(EDITORIAL_FONT_PAIRINGS["sante_bien_etre"])

    # 5. Luxe / Immobilier / Patrimoine
    if any(m in t_norm for m in ("immobilier", "luxe", "patrimoine", "architecture", "prestige", "chateau", "art")):
        return dict(EDITORIAL_FONT_PAIRINGS["luxe_patrimoine"])

    # 6. Roman / Fiction
    if any(m in t_norm for m in ("roman", "fiction", "thriller", "suspense", "polar", "biograph", "memoire")):
        return dict(EDITORIAL_FONT_PAIRINGS["fiction_roman"])

    # 7. Par défaut : Business & Finances Prestige
    return dict(EDITORIAL_FONT_PAIRINGS["prestige_business"])


def recommend_font_pairing_for_language(
    language: str = "fr",
    niche_or_genre: str = "",
    target_audience: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sélectionne automatiquement le pairing Google Fonts de prestige selon la langue cible :
    - 'ar' : Amiri & Cairo (Arabe Majestueux & Calligraphie Naskh)
    - 'de' : EB Garamond & Cinzel (Précision Germanique & Césures composées)
    - 'es' : Lora & Playfair Display (Espagnol Littéraire & Contemporain)
    - 'en' / 'fr' : Pairing spécialisé selon la niche et l'audience
    """
    lang = (language or "fr").strip().lower()
    if lang == "ar":
        return dict(EDITORIAL_FONT_PAIRINGS["arabic_majestic"])
    if lang == "de":
        return dict(EDITORIAL_FONT_PAIRINGS["germanic_precision"])
    if lang == "es":
        return dict(EDITORIAL_FONT_PAIRINGS["spanish_modern"])
    return recommend_font_pairing(niche_or_genre, target_audience)


def get_google_fonts_embed_url(families: List[str], display: str = "swap") -> str:
    """
    Construit l'URL canonique Google Fonts v2 pour l'import direct dans le CSS ou HTML.
    Exemple : https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Merriweather:ital,wght@0,400;0,700;1,400&display=swap
    """
    if not families:
        return ""
    from urllib.parse import quote_plus
    parts: List[str] = []
    seen = set()
    for fam in families:
        propre = str(fam).strip()
        if not propre or propre in seen:
            continue
        seen.add(propre)
        # Weights recommandés pour KDP
        encoded = quote_plus(propre)
        parts.append(f"family={encoded}:ital,wght@0,400;0,600;0,700;1,400")

    return f"https://fonts.googleapis.com/css2?{'&'.join(parts)}&display={display}"


def generate_pairing_css(
    pairing: Dict[str, Any],
    include_embed: bool = True,
) -> str:
    """
    Génère les règles CSS complètes (règles @import + variables + classes utilitaires)
    pour le pairing typographique sélectionné.
    """
    title_font = pairing.get("title_font", "Cinzel")
    subtitle_font = pairing.get("subtitle_font", "Montserrat")
    body_font = pairing.get("body_font", "Merriweather")
    accent_font = pairing.get("accent_font", "Cormorant Garamond")
    fallback_serif = pairing.get("fallback_serif", "Georgia, serif")
    fallback_sans = pairing.get("fallback_sans", "sans-serif")

    embed_css = ""
    if include_embed:
        fonts_to_load = [title_font, subtitle_font, body_font, accent_font]
        url = get_google_fonts_embed_url(fonts_to_load)
        embed_css = f'@import url("{url}");\n\n'

    return (
        f"{embed_css}"
        f"/* === TYPOGRAPHIE ÉDITORIALE KDP ({pairing.get('name', 'Custom')}) === */\n"
        f":root {{\n"
        f"  --font-title: '{title_font}', {fallback_serif};\n"
        f"  --font-subtitle: '{subtitle_font}', {fallback_sans};\n"
        f"  --font-body: '{body_font}', {fallback_serif};\n"
        f"  --font-accent: '{accent_font}', {fallback_serif};\n"
        f"}}\n\n"
        f"body, .kdp-book-content {{\n"
        f"  font-family: var(--font-body);\n"
        f"  font-size: 10.5pt;\n"
        f"  line-height: 1.48;\n"
        f"  text-align: justify;\n"
        f"  hyphens: auto;\n"
        f"}}\n\n"
        f"h1, .book-title, .chapter-title {{\n"
        f"  font-family: var(--font-title);\n"
        f"  font-weight: 700;\n"
        f"  letter-spacing: 0.04em;\n"
        f"  line-height: 1.2;\n"
        f"}}\n\n"
        f"h2, h3, .book-subtitle, .section-title {{\n"
        f"  font-family: var(--font-subtitle);\n"
        f"  font-weight: 600;\n"
        f"  letter-spacing: 0.02em;\n"
        f"}}\n\n"
        f"blockquote, .drop-cap, .quote-box, .epigraph {{\n"
        f"  font-family: var(--font-accent);\n"
        f"  font-style: italic;\n"
        f"}}\n"
    )


__all__ = [
    "search_google_fonts",
    "download_font_file",
    "build_font_face_css",
    "CURATED_KDP_FONTS",
    "EDITORIAL_FONT_PAIRINGS",
    "list_editorial_pairings",
    "recommend_font_pairing",
    "recommend_font_pairing_for_language",
    "get_google_fonts_embed_url",
    "generate_pairing_css",
]

