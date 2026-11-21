"""
Agent 0 & Agent 0.5 — Intelligence Marché & Autopsie Best-Sellers (Sur-Ensemble Zéro-Casse)
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

from kdp_extensions.webhooks import emit_webhook

BASE_DIR = Path(__file__).resolve().parent.parent


def _httpx_get_json(url: str, params: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    timeout: float = 6.0) -> Any:
    """Unique point de sortie HTTP (mockable dans les tests, zéro appel inline)."""
    if httpx is None:
        raise RuntimeError("httpx n'est pas installé")
    with httpx.Client(timeout=timeout, headers=headers or {"User-Agent": "Mozilla/5.0"}) as client:
        r = client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()


class BestsellerWeakness(BaseModel):
    categorie: str
    faiblesse_concurrents: str
    contre_attaque_markeddy: str


class CompetitorGapReport(BaseModel):
    niche: str
    cible: str
    marketplace: str = "fr"
    generated_at: str
    trend_score: int = Field(ge=0, le=100)
    google_signals: List[str] = Field(default_factory=list)
    amazon_kdp_keywords_live: List[str] = Field(default_factory=list)
    bestseller_weaknesses: List[BestsellerWeakness] = Field(default_factory=list)
    superior_angle: str
    recommended_title: str
    recommended_subtitle_seo: str
    backend_keywords_7: List[str] = Field(default_factory=list)
    must_have_assets: List[str] = Field(default_factory=list)
    design_directives: Dict[str, str] = Field(default_factory=dict)


def fetch_google_signals(niche: str, lang: str = "fr") -> Dict[str, Any]:
    queries: List[str] = []
    trend_score = 72
    try:
        from pytrends.request import TrendReq  # type: ignore
        pt = TrendReq(hl=f"{lang}-{lang.upper()}", tz=60, timeout=(5, 10))
        pt.build_payload([niche], timeframe="today 12-m")
        df = pt.interest_over_time()
        if df is not None and not df.empty and niche in df.columns:
            trend_score = max(10, min(100, int(df[niche].tail(8).mean())))
    except Exception:
        pass

    if httpx is not None:
        seeds = [f"{niche} livre", f"{niche} guide", f"{niche} debutant", niche]
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
        queries = [f"{niche} livre", f"{niche} méthode pratique", f"{niche} guide complet"]

    return {"niche": niche, "trend_score": trend_score, "google_signals": queries[:15]}


def fetch_amazon_kdp_suggestions(niche: str, marketplace: str = "fr") -> List[str]:
    suggestions: List[str] = []
    if httpx is None:
        return [f"{niche} livre", f"{niche} guide pratique"]

    mp_config = {
        "fr": ("https://completion.amazon.fr/api/2017/suggestions", "A13V1IB3VIYZZH"),
        "com": ("https://completion.amazon.com/api/2017/suggestions", "ATVPDKIKX0DER"),
        "uk": ("https://completion.amazon.co.uk/api/2017/suggestions", "A1F83G8C2ARO7P"),
    }
    endpoint, mid = mp_config.get(marketplace.lower(), mp_config["fr"])

    for prefix in (niche, f"{niche} "):
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

    return suggestions[:15] or [f"{niche} livre", f"{niche} guide complet", f"{niche} exercices"]


def _sept_mots_cles(mots: List[str], niche: str, amazon: List[str], google: List[str]) -> List[str]:
    """Garantit exactement 7 mots-clés backend, même en mode fallback hors-ligne."""
    resultats: List[str] = []
    for source in (mots or [], amazon or [], google or [],
                   [f"{niche} livre", f"{niche} guide pratique", f"{niche} pas à pas",
                    f"{niche} débutant", f"{niche} méthode", f"{niche} exercices",
                    f"{niche} avancé"]):
        for mot in source:
            propre = str(mot).strip().lower()
            if propre and propre not in resultats:
                resultats.append(propre)
            if len(resultats) == 7:
                return resultats
    return resultats[:7]


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    raw = m.group(1) if m else text
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except Exception:
        return None


def analyze_bestsellers_and_gaps(
    niche: str,
    cible: str = "Lecteurs exigeants cherchant des résultats concrets",
    marketplace: str = "fr",
    output_path: Optional[Path] = None,
    use_ai: bool = True,
) -> CompetitorGapReport:
    lang = "en" if marketplace.lower() in ("com", "uk") else "fr"
    google_data = fetch_google_signals(niche, lang=lang)
    amazon_kw = fetch_amazon_kdp_suggestions(niche, marketplace=marketplace)

    emit_webhook("market.trends.ready", {
        "niche": niche,
        "marketplace": marketplace,
        "trend_score": google_data["trend_score"],
        "google_signals_count": len(google_data["google_signals"]),
        "amazon_keywords_count": len(amazon_kw),
    })

    ai_payload: Optional[Dict[str, Any]] = None
    if use_ai:
        try:
            import call_ai
            prompt = (
                f"Tu es un Directeur Éditorial & Analyste Amazon KDP d'élite.\n"
                f"Analyse la niche : '{niche}' pour la cible : '{cible}' (Amazon.{marketplace}).\n"
                f"Signaux Google live : {json.dumps(google_data['google_signals'], ensure_ascii=False)}\n"
                f"Requêtes Amazon KDP live : {json.dumps(amazon_kw, ensure_ascii=False)}\n"
                f"Identifie 5 faiblesses majeures des best-sellers actuels (avis 1-3 étoiles) et réponds UNIQUEMENT en JSON valide "
                f"avec les clés : superior_angle, recommended_title, recommended_subtitle_seo, backend_keywords_7 (7 items), "
                f"must_have_assets (4 items), design_directives (palette, typographie, concept_couverture, mise_en_page_interieure), "
                f"bestseller_weaknesses (liste d'objets avec categorie, faiblesse_concurrents, contre_attaque_markeddy)."
            )
            system_prompt = "Tu es un Directeur Éditorial & Analyste Amazon KDP d'élite. Réponds uniquement en JSON valide."
            if hasattr(call_ai, "ask_ai"):
                raw_resp = call_ai.ask_ai(prompt)
            elif hasattr(call_ai, "generer_texte_gemini"):
                raw_resp = call_ai.generer_texte_gemini(system_prompt, prompt)
            else:
                raw_resp = None
            if isinstance(raw_resp, str):
                ai_payload = _extract_json_block(raw_resp)
        except Exception:
            ai_payload = None

    if not ai_payload:
        ai_payload = {
            "superior_angle": f"Transformer '{niche}' en un système exécutable en 30 jours avec feuilles de route chiffrées, cas réels et checklists.",
            "recommended_title": f"LA MÉTHODE COMPLÈTE : {niche.upper()}",
            "recommended_subtitle_seo": f"Le guide pratique pas-à-pas pour maîtriser {niche} avec plans d'action et études de cas",
            "backend_keywords_7": (amazon_kw + google_data["google_signals"])[:7],
            "must_have_assets": [
                "Tableaux de diagnostic chiffrés en fin de chaque chapitre",
                "Plan d'action opérationnel sur 30 jours",
                "Études de cas détaillées avant/après",
                "Checklists anti-erreurs récapitulatives",
            ],
            "design_directives": {
                "palette": "Obsidienne profond (#0A0F1D), Or éditorial (#D4AF37) et Blanc cassé (#F8FAFC)",
                "typographie": "Titres Serif haute autorité + corps Sans-Serif aéré (interligne 1.45)",
                "concept_couverture": "Minimalisme exécutif à fort contraste lisible en vignette 120px sur Amazon",
                "mise_en_page_interieure": "Encadrés d'action, tableaux synthétiques et marges respirantes KDP",
            },
            "bestseller_weaknesses": [
                {"categorie": "Fond", "faiblesse_concurrents": "Contenu trop théorique et répétitif sans protocole concret.", "contre_attaque_markeddy": "Chaque chapitre se termine par un protocole chiffré et une checklist exécutable."},
                {"categorie": "Pratique", "faiblesse_concurrents": "Absence d'exemples récents et de modèles réutilisables.", "contre_attaque_markeddy": "Intégration d'études de cas modernes et de grilles prêtes à remplir."},
                {"categorie": "Mise en page", "faiblesse_concurrents": "Blocs de texte compacts fatigants à lire.", "contre_attaque_markeddy": "Hiérarchie visuelle haute couture : encadrés, tableaux et résumés visuels."},
                {"categorie": "Design", "faiblesse_concurrents": "Couvertures génériques illisibles en miniature Amazon.", "contre_attaque_markeddy": "Couverture 300 DPI à contraste fort optimisée pour le CTR."},
            ],
        }

    report = CompetitorGapReport(
        niche=niche,
        cible=cible,
        marketplace=marketplace,
        generated_at=datetime.now(timezone.utc).isoformat(),
        trend_score=google_data["trend_score"],
        google_signals=google_data["google_signals"],
        amazon_kdp_keywords_live=amazon_kw,
        bestseller_weaknesses=[BestsellerWeakness(**w) for w in ai_payload.get("bestseller_weaknesses", [])],
        superior_angle=ai_payload.get("superior_angle", ""),
        recommended_title=ai_payload.get("recommended_title", niche),
        recommended_subtitle_seo=ai_payload.get("recommended_subtitle_seo", ""),
        backend_keywords_7=_sept_mots_cles(
            ai_payload.get("backend_keywords_7", []), niche, amazon_kw, google_data["google_signals"]
        ),
        must_have_assets=ai_payload.get("must_have_assets", []),
        design_directives=ai_payload.get("design_directives", {}),
    )

    dest = output_path or (BASE_DIR / "competitor_gap_report.json")
    dest.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    emit_webhook("competitor.gap.ready", {
        "niche": niche,
        "report_path": str(dest),
        "recommended_title": report.recommended_title,
        "weaknesses_count": len(report.bestseller_weaknesses),
        "trend_score": report.trend_score,
    })
    return report
