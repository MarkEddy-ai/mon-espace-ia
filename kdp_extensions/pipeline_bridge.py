"""
Pont d'Orchestration Sprint 3 — MarkEddy KDP Studio (Sur-Ensemble Zéro-Casse)
Relie l'Agent 0 (market_intelligence) au pipeline de production (app_studio / orchestrator)
et émet les webhooks de cycle de vie (manuscript, design, pack_ready, failed).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from kdp_extensions.market_intelligence import CompetitorGapReport, analyze_bestsellers_and_gaps
from kdp_extensions.webhooks import emit_webhook

STAGE_EVENT_MAP = {
    "manuscript": "book.manuscript.ready",
    "design": "book.design.ready",
    "pack_ready": "book.published.pack_ready",
    "failed": "job.failed",
}


def build_editorial_directive_block(report: CompetitorGapReport) -> str:
    """Construit un bloc d'instructions concis à injecter dans les prompts Architecte / Rédacteur / SEO."""
    lignes = [
        f"ANGLE SUPÉRIEUR MARKEDDY : {report.superior_angle}",
        "FAIBLESSES DES BEST-SELLERS À CORRIGER IMPÉRATIVEMENT :",
    ]
    for idx, w in enumerate(report.bestseller_weaknesses[:5], 1):
        lignes.append(
            f"  {idx}. [{w.categorie}] Défaut concurrent : {w.faiblesse_concurrents} "
            f"-> Notre réponse : {w.contre_attaque_markeddy}"
        )
    if report.must_have_assets:
        lignes.append("ACTIFS PRATIQUES OBLIGATOIRES : " + " | ".join(report.must_have_assets[:4]))
    if report.backend_keywords_7:
        lignes.append("MOTS-CLÉS AMAZON LIVE : " + ", ".join(report.backend_keywords_7[:7]))
    if report.design_directives:
        dd = ", ".join(f"{k}: {v}" for k, v in report.design_directives.items())
        lignes.append(f"DIRECTIVES DESIGN : {dd}")
    return "\n".join(lignes)


def prepare_competitive_context(
    niche: str,
    cible: str = "Lecteurs exigeants cherchant des résultats concrets",
    marketplace: str = "fr",
    output_dir: Optional[Path] = None,
    use_ai: bool = True,
) -> Dict[str, Any]:
    """
    Exécute l'Agent 0 pour une production de livre, sauvegarde competitor_gap_report.json
    (dans le dossier du livre si fourni) et retourne le contexte prêt à injecter.
    """
    dest = (Path(output_dir) / "competitor_gap_report.json") if output_dir else None
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)

    report = analyze_bestsellers_and_gaps(
        niche=niche,
        cible=cible,
        marketplace=marketplace,
        output_path=dest,
        use_ai=use_ai,
    )

    return {
        "report": report.model_dump(),
        "report_path": str(dest) if dest else "competitor_gap_report.json",
        "recommended_title": report.recommended_title,
        "recommended_subtitle_seo": report.recommended_subtitle_seo,
        "backend_keywords_7": report.backend_keywords_7,
        "design_directives": report.design_directives,
        "editorial_directive_block": build_editorial_directive_block(report),
    }


def apply_gap_report_to_blueprint(blueprint_path: Path, context: Dict[str, Any]) -> bool:
    """
    Enrichit book_blueprint.json avec les métadonnées SEO et directives anti-faiblesses
    de l'Agent 0 sans casser la structure attendue par book_writer.py / kdp_marketing.py.
    """
    if not blueprint_path.exists():
        return False
    try:
        bp = json.loads(blueprint_path.read_text(encoding="utf-8"))
        bp["competitor_gap_intelligence"] = {
            "superior_angle": context.get("report", {}).get("superior_angle", ""),
            "bestseller_weaknesses": context.get("report", {}).get("bestseller_weaknesses", []),
            "must_have_assets": context.get("report", {}).get("must_have_assets", []),
            "design_directives": context.get("design_directives", {}),
        }
        kws = context.get("backend_keywords_7") or []
        if kws and not bp.get("mots_cles_backend"):
            bp["mots_cles_backend"] = kws[:7]
        blueprint_path.write_text(json.dumps(bp, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def notify_pipeline_stage(stage: str, book_id: Any, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Émet le webhook correspondant à l'étape du pipeline (manuscript, design, pack_ready, failed)."""
    event = STAGE_EVENT_MAP.get(stage, f"book.{stage}")
    data = {"book_id": book_id, **(payload or {})}
    return emit_webhook(event=event, payload=data)
