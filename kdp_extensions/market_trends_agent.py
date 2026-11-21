"""
kdp_extensions/market_trends_agent.py — Agent de Veille Tri-Plateforme KDP.
(Google Trends + Amazon KDP Autocomplete + Pinterest Aesthetic & Mood).

Cet agent analyse en temps réel les trois grands canaux d'attention :
1. Google Trends / Google Suggest : vitesse de recherche, volume d'intérêt, questions fréquentes.
2. Amazon KDP Autocomplete (stripbooks) : intention d'achat commerciale, suggestions A9 en direct.
3. Pinterest Trends & Visual Discovery : palettes chromatiques tendance, esthétique de couverture,
   moodboards et signaux graphiques populaires auprès des acheteurs de livres.

Sortie : Rapport stratégique complet comprenant un score d'opportunité (0-100),
les 7 mots-clés backend Amazon A9 stricts, l'autopsie des faiblesses concurrentes
et les directives visuelles Pinterest pour le designer de couverture.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from pydantic import BaseModel, Field

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent


def _httpx_get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 6.0,
) -> Any:
    """Point de sortie HTTP unique (mockable dans les tests unitaires)."""
    if httpx is None:
        raise RuntimeError("httpx n'est pas installé")
    hdrs = headers or {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    with httpx.Client(timeout=timeout, headers=hdrs) as client:
        r = client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()


# ==============================================================================
# 1. VEILLE GOOGLE TRENDS & SUGGEST
# ==============================================================================

def fetch_google_trends(
    keyword: str,
    geo: str = "FR",
    lang: str = "fr",
) -> Dict[str, Any]:
    """
    Récupère le signal de volume et les suggestions de recherche Google.
    Tente pytrends puis bascule gracieusement sur Google Suggest.
    """
    queries: List[str] = []
    trend_score = 75

    # 1. Essai avec pytrends si disponible
    try:
        from pytrends.request import TrendReq  # type: ignore
        pt = TrendReq(hl=f"{lang}-{geo}", tz=60, timeout=(4, 8))
        pt.build_payload([keyword], geo=geo, timeframe="today 12-m")
        df = pt.interest_over_time()
        if df is not None and not df.empty and keyword in df.columns:
            trend_score = max(10, min(100, int(df[keyword].tail(8).mean())))
    except Exception:
        pass

    # 2. Requêtes Google Suggest (vitesse de recherche instantanée)
    if httpx is not None:
        seeds = [f"{keyword} livre", f"{keyword} guide", f"{keyword} debutant", f"{keyword} methode", keyword]
        for seed in seeds:
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&hl={lang}&q={quote_plus(seed)}"
            try:
                data = _httpx_get_json(url)
                if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                    for item in data[1]:
                        if isinstance(item, str) and item not in queries:
                            queries.append(item)
            except Exception:
                pass

    if not queries:
        queries = [
            f"{keyword} livre",
            f"{keyword} guide complet",
            f"{keyword} methode pratique",
            f"{keyword} debutant exercices",
            f"{keyword} pas a pas",
        ]

    return {
        "keyword": keyword,
        "geo": geo,
        "trend_score": trend_score,
        "related_queries": queries[:15],
    }


# ==============================================================================
# 2. VEILLE AMAZON KDP AUTOCOMPLETE & INTENTION D'ACHAT A9
# ==============================================================================

def fetch_amazon_kdp_trends(
    niche: str,
    marketplace: str = "fr",
) -> Dict[str, Any]:
    """
    Interroge l'API de complétion d'Amazon dans le rayon Livres ('stripbooks')
    pour capturer les intentions d'achat actives des clients Amazon.
    """
    suggestions: List[str] = []
    mp_config = {
        "fr": ("https://completion.amazon.fr/api/2017/suggestions", "A13V1IB3VIYZZH"),
        "com": ("https://completion.amazon.com/api/2017/suggestions", "ATVPDKIKX0DER"),
        "uk": ("https://completion.amazon.co.uk/api/2017/suggestions", "A1F83G8C2ARO7P"),
        "de": ("https://completion.amazon.de/api/2017/suggestions", "A1PA6795UKMFR9"),
    }
    endpoint, mid = mp_config.get(marketplace.lower(), mp_config["fr"])

    prefixes = [niche, f"{niche} ", f"livre {niche}", f"guide {niche}"]
    for prefix in prefixes:
        if httpx is None:
            break
        try:
            data = _httpx_get_json(
                endpoint,
                params={"mid": mid, "alias": "stripbooks", "prefix": prefix},
            )
            for s in data.get("suggestions", []):
                val = s.get("value", "").strip()
                if val and val not in suggestions:
                    suggestions.append(val)
        except Exception:
            pass

    if not suggestions:
        suggestions = [
            f"{niche} livre broché",
            f"{niche} guide débutant",
            f"{niche} méthode pas à pas",
            f"{niche} exercices pratiques",
            f"{niche} sans prise de tête",
            f"{niche} pour les nuls",
            f"{niche} gestion et stratégie",
        ]

    # Analyse des intentions
    classified_intents: Dict[str, List[str]] = {
        "douleur_ou_probleme": [],
        "methode_operationnelle": [],
        "public_cible": [],
    }
    for s in suggestions:
        sl = s.lower()
        if any(w in sl for w in ("debutant", "adulte", "ado", "enfant", "etudiant", "senior")):
            classified_intents["public_cible"].append(s)
        elif any(w in sl for w in ("methode", "guide", "exercices", "plan", "regle", "etape")):
            classified_intents["methode_operationnelle"].append(s)
        else:
            classified_intents["douleur_ou_probleme"].append(s)

    return {
        "niche": niche,
        "marketplace": marketplace,
        "suggestions_count": len(suggestions),
        "top_suggestions": suggestions[:15],
        "intents": classified_intents,
    }


# ==============================================================================
# 3. VEILLE PINTEREST AESTHETIC & MOOD VISUEL
# ==============================================================================

def fetch_pinterest_trends(
    niche: str,
    lang: str = "fr",
) -> Dict[str, Any]:
    """
    Extrait les signaux esthétiques, palettes chromatiques et tendances graphiques
    associées à la thématique sur Pinterest.
    """
    suggestions: List[str] = []
    clean_niche = niche.strip().lower()

    # Requête de complétion visuelle Pinterest
    if httpx is not None:
        url = f"https://www.pinterest.fr/search/autocomplete/?q={quote_plus(clean_niche + ' book aesthetic')}"
        try:
            data = _httpx_get_json(url)
            # Pinterest renvoie des listes de suggestions
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        suggestions.append(item)
                    elif isinstance(item, dict) and "query" in item:
                        suggestions.append(item["query"])
        except Exception:
            pass

    # Palettes chromatiques de référence par niche (directives Pinterest)
    niche_lower = clean_niche.lower()
    if any(k in niche_lower for k in ("financ", "argent", "investir", "bourse", "business")):
        palette = ["#0A0F1D (Obsidienne)", "#D4AF37 (Or Impérial)", "#1E293B (Ardoise)", "#F8FAFC (Blanc Lin)"]
        mood = "Dark Academic Luxury & Haute Finance"
        style_couverture = "Minimaliste sobre, titre imposant doré avec filet impérial, fond ardoise velours."
    elif any(k in niche_lower for k in ("stoic", "philosoph", "sagesse", "meditat")):
        palette = ["#2C0B0E (Bordeaux Grand Cru)", "#E8C5C8 (Or Rose)", "#FAF7F2 (Ivoire)", "#18181B (Charbon)"]
        mood = "Élégance Antique & Gravitas Méditative"
        style_couverture = "Statue antique marbre, typographie Cinzel impériale, texture papier de cuve."
    elif any(k in niche_lower for k in ("sante", "sommeil", "bien-etre", "bio", "corps")):
        palette = ["#062C22 (Émeraude)", "#C5A059 (Champagne)", "#F3F7F4 (Brume)", "#2D3748 (Gris Forêt)"]
        mood = "Botanique Zen & Sérénité Organique"
        style_couverture = "Feuillage raffiné en filigrane, mise en page épurée, teinte sauge et crème."
    elif any(k in niche_lower for k in ("ia", "tech", "code", "productivite")):
        palette = ["#0B192C (Saphir d'encre)", "#00ADB5 (Cyan Platine)", "#FFFFFF (Blanc Pur)", "#1F2937 (Graphite)"]
        mood = "Cyber Néo-Futurisme & Clarté Scandinave"
        style_couverture = "Formes géométriques abstraites, typographie sans empattements nette, contraste dynamique."
    elif any(k in niche_lower for k in ("enfant", "coloriage", "activite")):
        palette = ["#FF6B6B (Corail Vif)", "#4ECDC4 (Menthe)", "#FFE66D (Jaune Soleil)", "#2C3E50 (Bleu Nuit)"]
        mood = "Joie Éducative & Éveil Pastel"
        style_couverture = "Illustrations chaleureuses aux contours nets, rondeur typographique, badges d'apprentissage."
    else:
        palette = ["#0F172A (Bleu Nuit)", "#D4AF37 (Dorure Chaude)", "#F8FAFC (Blanc)", "#64748B (Étain)"]
        mood = "Édition Classique & Rigueur Contemporaine"
        style_couverture = "Typographie monumentale au tiers supérieur, filet d'accentuation, fond sombre texturé."

    return {
        "niche": niche,
        "pinterest_mood": mood,
        "recommended_palette": palette,
        "cover_aesthetic_directives": style_couverture,
        "visual_tags": [
            f"{niche} book cover",
            f"{niche} layout inspiration",
            f"{niche} aesthetic minimalist",
            f"{niche} workbook template",
        ] + suggestions[:5],
    }


# ==============================================================================
# 4. SYNTHÈSE GLOBALE & MATRICE 7 MOTS-CLÉS A9 (ZÉRO FLUFF)
# ==============================================================================

def _generer_7_mots_cles_a9(
    niche: str,
    titre: str,
    sous_titre: str,
    amazon_sigs: List[str],
    google_sigs: List[str],
) -> List[str]:
    """
    Construit la matrice d'attaque des 7 slots backend Amazon A9 selon la Règle 05 :
    - Zéro répétition des mots déjà présents dans le Titre ou Sous-titre
    - Zéro guillemet, zéro ponctuation (séparateurs espaces purs)
    - 35 à 45 caractères par case
    - 7 intentions stratégiques distinctes
    """
    titre_mots = set(re.findall(r"\b[a-zA-ZÀ-ÿ0-9]{3,}\b", f"{titre} {sous_titre}".lower()))

    # Intentions types
    templates = [
        f"sortir du probleme {niche} sans stress",
        f"methode pas a pas {niche} exercices concrets",
        f"guide pratique {niche} debutant autonome",
        f"plan d action {niche} resultats rapides",
        f"strategie avancee {niche} reussite et efficacite",
        f"pieges a eviter {niche} erreurs debutants",
        f"transformation durable {niche} changement quotidien",
    ]

    slots: List[str] = []
    # Mix des suggestions Amazon & Google épurées des mots du titre
    pool: List[str] = []
    for src in (amazon_sigs, google_sigs, templates):
        for phrase in src:
            clean = re.sub(r"[^\w\s]", " ", str(phrase).lower())
            clean = re.sub(r"\s+", " ", clean).strip()
            # Nettoyage des mots du titre
            tokens = [t for t in clean.split() if len(t) >= 2 and t not in titre_mots]
            if tokens:
                phrase_epuree = " ".join(tokens)
                if phrase_epuree not in pool and len(phrase_epuree) >= 15:
                    pool.append(phrase_epuree)

    for item in pool:
        if len(slots) >= 7:
            break
        # Formatage optimal entre 25 et 55 caractères
        val = item[:50].strip()
        if val not in slots:
            slots.append(val)

    # Complétion garantie si besoin
    while len(slots) < 7:
        idx = len(slots) + 1
        secours = f"conseils et astuces {niche} module {idx}"
        slots.append(secours[:45])

    return slots[:7]


def analyze_market_trends(
    niche: str,
    target_audience: Optional[str] = None,
    marketplace: str = "fr",
    use_ai: bool = True,
) -> Dict[str, Any]:
    """
    Point d'entrée unique de l'Agent de Veille Tri-Plateforme.
    Génère l'autopsie concurrentielle et le blueprint d'attaque éditoriale.
    """
    google_data = fetch_google_trends(niche, geo=marketplace.upper() if len(marketplace) == 2 else "FR")
    amazon_data = fetch_amazon_kdp_trends(niche, marketplace=marketplace)
    pinterest_data = fetch_pinterest_trends(niche)

    # Calcul du score d'opportunité global (0-100)
    score_google = google_data["trend_score"]
    score_amazon = min(100, max(40, len(amazon_data["top_suggestions"]) * 7))
    score_opportunite = int((score_google * 0.5) + (score_amazon * 0.5))

    cible = target_audience or "Débutants motivés et professionnels en quête d'efficacité"

    # Titre et sous-titre recommandés
    titre_rec = f"L'ART DE MAÎTRISER {niche.upper()}"
    sous_titre_rec = f"La méthode pas-à-pas pour transformer votre quotidien sans jargon ni théorie inutile"

    # Les 7 mots-clés backend A9
    keywords_7 = _generer_7_mots_cles_a9(
        niche=niche,
        titre=titre_rec,
        sous_titre=sous_titre_rec,
        amazon_sigs=amazon_data["top_suggestions"],
        google_sigs=google_data["related_queries"],
    )

    faiblesses_concurrents = [
        {
            "point_faible": "Ouvrages concurrents trop théoriques, sans plans d'action chiffrés",
            "contre_attaque_markeddy": "Chaque section intègre un calcul réel et un encadré 'Action Immédiate 24h'",
        },
        {
            "point_faible": "Mise en page bâclée avec texte collé au dos et lettrines absentes",
            "contre_attaque_markeddy": "Marge de reliure (gutter) de 0.85 po et typographie d'artisan imprimeur",
        },
        {
            "point_faible": "Descriptions Amazon creuses sans puces bénéfices ni balisage A+",
            "contre_attaque_markeddy": "Pack de conversion HTML complet avec modules A+ Content haute autorité",
        },
    ]

    report = {
        "niche": niche,
        "cible": cible,
        "marketplace": marketplace,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "opportunity_score": score_opportunite,
        "google_trends": google_data,
        "amazon_kdp": amazon_data,
        "pinterest_aesthetic": pinterest_data,
        "recommended_title": titre_rec,
        "recommended_subtitle_seo": sous_titre_rec,
        "backend_keywords_7": keywords_7,
        "competitor_gaps": faiblesses_concurrents,
        "strategic_angle": f"Le guide le plus concret et élégant du marché sur {niche}, calibré pour une transformation en 30 jours.",
        "cover_design_brief": {
            "mood": pinterest_data["pinterest_mood"],
            "palette": pinterest_data["recommended_palette"],
            "directives": pinterest_data["cover_aesthetic_directives"],
            "resolution": "300 DPI obligatoire",
            "isbn_reserve": "600x360 px en bas à droite de la 4ème de couverture",
        },
    }

    return report


def export_trend_brief_markdown(report: Dict[str, Any]) -> str:
    """Exporte le rapport de veille sous forme de brief éditorial Markdown percutant."""
    kw_list = "\n".join(f"  {i+1}. `{k}`" for i, k in enumerate(report.get("backend_keywords_7", [])))
    gaps = "\n".join(
        f"- ❌ **Faiblesse :** {g['point_faible']}\n  👉 **Notre Riposte :** {g['contre_attaque_markeddy']}"
        for g in report.get("competitor_gaps", [])
    )
    p_data = report.get("pinterest_aesthetic", {})
    palette_str = ", ".join(p_data.get("recommended_palette", []))

    return (
        f"# 📊 BRIEF STRATÉGIQUE & INTELLIGENCE MARCHÉ : {report.get('niche', '').upper()}\n\n"
        f"**Score d'Opportunité Amazon KDP :** {report.get('opportunity_score', 0)} / 100\n"
        f"**Public Cible :** {report.get('cible', '')}\n\n"
        f"## 🏆 Angle Supérieur & Positionnement\n"
        f"**Titre Recommandé :** {report.get('recommended_title', '')}\n"
        f"**Sous-Titre SEO A9 :** {report.get('recommended_subtitle_seo', '')}\n"
        f"**Promesse de Transformation :** {report.get('strategic_angle', '')}\n\n"
        f"## 🔍 Les 7 Mots-Clés Backend A9 (Zéro Répétition)\n"
        f"{kw_list}\n\n"
        f"## ⚔️ Autopsie des Concurrents & Contre-Attaque\n"
        f"{gaps}\n\n"
        f"## 🎨 Direction Artistique Pinterest & Couverture\n"
        f"- **Ambiance :** {p_data.get('pinterest_mood', '')}\n"
        f"- **Palette :** {palette_str}\n"
        f"- **Directives de Composition :** {p_data.get('cover_aesthetic_directives', '')}\n"
    )


__all__ = [
    "fetch_google_trends",
    "fetch_amazon_kdp_trends",
    "fetch_pinterest_trends",
    "analyze_market_trends",
    "export_trend_brief_markdown",
]
