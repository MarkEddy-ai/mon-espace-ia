# -*- coding: utf-8 -*-
"""
kdp_extensions/autonomous_visual_agent.py — Agent Visuel Autonome 100% Arrière-Plan.

Cet agent gère l'intégralité du pipeline visuel et graphique sans aucune intervention
manuelle de l'utilisateur sur le dashboard :
1. Recherche silencieuse d'images stock haute résolution (Unsplash, Pixabay, catalogue curé)
   avec des requêtes adaptées à la niche, au genre et à l'audience cible.
2. Téléchargement et calibrage prépresse 300 DPI sans hotlinking (ImageOps.fit).
   Génération et conversion automatique des illustrations intérieures en noir et blanc pur
   (SVG vectoriel 300 DPI et binarisation 0/255 via convertir_en_line_art).
3. Synchronisation Canva Connect en arrière-plan : si des jetons valides et un Brand Template
   sont configurés, exécution silencieuse upload asset -> autofill -> export PNG/PDF
   sans jamais rediriger l'utilisateur vers Canva.
4. Repli local haute définition garanti (Zero Failure) : production d'une couverture complète
   calibrée au micron (Plat 1 + Dos + Plat 4 + Réserve ISBN 600x360 px) et d'actifs prêts
   pour l'impression industrielle Amazon KDP.
"""

from __future__ import annotations

import io
import json
import os
import re
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageOps, ImageDraw
except ImportError:
    Image = None  # pragma: no cover

try:
    import httpx
except ImportError:
    httpx = None

from kdp_extensions.kdp_dimensions import (
    KDP_FORMATS,
    calculate_kdp_specs,
    normalize_format,
)
from kdp_extensions.media_connectors import (
    MEDIA_CACHE_DIR,
    CANVA_TOKENS_FILE,
    CANVA_API_BASE,
    search_stock_images,
    download_and_prepare_cover_bg,
    get_canva_tokens,
    upload_canva_asset,
    export_canva_design,
    generate_canva_cover_template,
)
from kdp_extensions.cover_calculator import (
    calculate_cover_dimensions,
    generate_cover_template_svg,
)
from kdp_extensions.coloring_book_engine import (
    convertir_en_line_art,
    generer_svg_mandala,
    generer_svg_botanique,
    generer_svg_animal_mystique,
    generer_svg_zen_architecture,
)

BASE_DIR = Path(__file__).resolve().parent.parent
AUTONOMOUS_VISUALS_DIR = BASE_DIR / "assets" / "autonomous_visuals"
AUTONOMOUS_VISUALS_DIR.mkdir(parents=True, exist_ok=True)


def _build_enriched_search_queries(
    niche: str,
    category: str,
    target_audience: str,
    title: str = ""
) -> List[str]:
    """Construit une séquence ordonnée de requêtes visuelles précises."""
    cat_clean = (category or "non_fiction").strip().lower()
    niche_clean = (niche or "general").strip()
    aud_clean = (target_audience or "").strip().lower()

    queries: List[str] = []

    if cat_clean in ("coloring", "coloriage"):
        queries.append(f"{niche_clean} line art pattern")
        queries.append(f"{niche_clean} coloring mandala")
        queries.append(f"{niche_clean} black and white drawing")
    elif cat_clean in ("puzzles", "puzzle"):
        queries.append(f"{niche_clean} geometric minimalist background")
        queries.append(f"{niche_clean} abstract puzzle")
    elif cat_clean in ("educational", "workbook", "workbooks"):
        queries.append(f"{niche_clean} learning education book")
        queries.append(f"{niche_clean} minimalist background")
    else:  # non_fiction, cookbooks, etc.
        if "senior" in aud_clean or "60+" in aud_clean:
            queries.append(f"{niche_clean} calm elegant background")
        elif "enfant" in aud_clean or "kid" in aud_clean:
            queries.append(f"{niche_clean} colorful cute illustration")
        else:
            queries.append(f"{niche_clean} obsidian gold background")
            queries.append(f"{niche_clean} executive finance leadership")

    # Requêtes de secours universelles
    queries.append(niche_clean)
    queries.append("minimalist abstract dark gold")
    return queries


def _try_canva_background_autofill(
    cover_bg_path: Path,
    title: str,
    subtitle: str,
    brand_template_id: Optional[str] = None
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Tente d'exécuter un autofill Canva Connect API 100% silencieux en arrière-plan.
    Retourne (statut, données_autofill).
    """
    tokens = get_canva_tokens()
    if not tokens or not tokens.get("access_token"):
        return "offline_or_unconnected", None

    access_token = tokens.get("access_token")
    mode = tokens.get("mode", "simulated")

    # 1. Upload de l'actif visuel en arrière-plan
    try:
        asset_res = upload_canva_asset(str(cover_bg_path), name=f"Cover {title[:30]}")
    except Exception as exc:
        print(f"⚠️ Note upload arrière-plan Canva : {exc}")
        asset_res = {"status": "error"}

    # 2. Vérification d'un Brand Template ID configuré pour autofill
    template_id = brand_template_id or os.getenv("CANVA_BRAND_TEMPLATE_ID") or tokens.get("brand_template_id")
    if not template_id or mode != "live" or httpx is None:
        if asset_res.get("status") == "uploaded":
            return "asset_uploaded_live", asset_res
        return "canva_simulated_ready", asset_res

    # 3. Appel de l'API Autofill de Canva Connect
    try:
        with httpx.Client(timeout=25.0) as client:
            resp = client.post(
                f"{CANVA_API_BASE}/autofills",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "brand_template_id": template_id,
                    "title": f"Cover_{title[:40]}",
                    "data": {
                        "book_title": {"type": "text", "text": title},
                        "book_subtitle": {"type": "text", "text": subtitle},
                    },
                },
            )
            if resp.status_code < 400:
                autofill_data = resp.json()
                return "autofill_completed", autofill_data
            else:
                print(f"⚠️ Canva Autofill HTTP {resp.status_code} : {resp.text}")
                return "autofill_template_unavailable", None
    except Exception as exc:
        print(f"⚠️ Exception Canva Autofill en arrière-plan : {exc}")
        return "autofill_error_fallback", None


def _generate_autonomous_interior_illustrations(
    category: str,
    niche: str,
    output_dir: Path,
    count: int = 4,
    source_bg_image: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Génère ou convertit automatiquement les illustrations intérieures requises
    sans intervention utilisateur (SVG vectoriel ou line-art 0/255 binarisé).
    """
    illustrations: List[Dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    cat_clean = (category or "").strip().lower()

    if cat_clean in ("coloring", "coloriage"):
        generators = [
            ("mandala", generer_svg_mandala),
            ("botanique", generer_svg_botanique),
            ("animal", generer_svg_animal_mystique),
            ("architecture", generer_svg_zen_architecture),
        ]
        for idx in range(1, count + 1):
            name, gen_func = generators[(idx - 1) % len(generators)]
            try:
                svg_content = gen_func(idx)
                svg_path = output_dir / f"interior_illustration_{idx:02d}_{name}.svg"
                svg_path.write_text(svg_content, encoding="utf-8")
                illustrations.append({
                    "index": idx,
                    "title": f"Planche {idx} - {name.capitalize()}",
                    "file_path": str(svg_path),
                    "filename": svg_path.name,
                    "format": "svg",
                    "mode": "vector_pure_black",
                })
            except Exception as e:
                print(f"⚠️ Erreur génération SVG illustration {idx} : {e}")

    # Si une image matricielle de fond est disponible, binarisation line-art 0/255
    if source_bg_image and source_bg_image.exists():
        try:
            line_art_path = output_dir / f"interior_frontispiece_lineart_{source_bg_image.stem}.png"
            convertir_en_line_art(source_bg_image, line_art_path, seuil_binaire=145)
            illustrations.append({
                "index": len(illustrations) + 1,
                "title": f"Frontispice Binarisé ({niche})",
                "file_path": str(line_art_path),
                "filename": line_art_path.name,
                "format": "png",
                "mode": "line_art_0_255",
            })
        except Exception as exc:
            print(f"⚠️ Note conversion line-art frontispice : {exc}")

    # Pour les guides pratiques et autres catégories : génération d'un schéma vectoriel sobre
    if not illustrations:
        try:
            sample_svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">'
                f'<rect width="1200" height="800" fill="#FFFFFF"/>'
                f'<circle cx="600" cy="400" r="280" fill="none" stroke="#000000" stroke-width="4"/>'
                f'<line x1="320" y1="400" x2="880" y2="400" stroke="#000000" stroke-width="2"/>'
                f'<line x1="600" y1="120" x2="600" y2="680" stroke="#000000" stroke-width="2"/>'
                f'<text x="600" y="420" font-family="Arial, sans-serif" font-size="28" font-weight="bold" '
                f'text-anchor="middle" fill="#000000">{niche.upper()} - ARCHITECTURE STRATÉGIQUE</text>'
                f'</svg>'
            )
            svg_path = output_dir / "interior_illustration_01_schema.svg"
            svg_path.write_text(sample_svg, encoding="utf-8")
            illustrations.append({
                "index": 1,
                "title": f"Schéma d'Autorité ({niche})",
                "file_path": str(svg_path),
                "filename": svg_path.name,
                "format": "svg",
                "mode": "vector_pure_black",
            })
        except Exception as e:
            pass

    return illustrations


def build_autonomous_visuals(
    title: str,
    subtitle: str = "",
    niche: str = "general",
    category: str = "non_fiction",
    target_audience: str = "Tous publics",
    format_kdp: str = "6x9",
    page_count: int = 100,
    paper_type: str = "white",
    language: str = "fr",
    output_dir: Optional[Path] = None,
    count_illustrations: int = 4
) -> Dict[str, Any]:
    """
    Point d'entrée unique de l'Agent Visuel Autonome 100% Arrière-Plan.

    Exécute sans aucune interaction utilisateur :
    1. Sélection d'une image stock optimale (Unsplash / Pixabay / catalogue curé).
    2. Recadrage et préparation 300 DPI sans hotlinking.
    3. Production des planches et illustrations intérieures N&B (SVG vectoriel & line-art).
    4. Tentative d'autofill Canva Connect en arrière-plan (si jeton + brand template).
    5. Repli local garanti sur le gabarit haute définition 300 DPI (Plat 1 + Dos + Plat 4 + ISBN 600x360).

    Retourne un descripteur complet prêt à être consommé par l'orchestrateur d'export KDP.
    """
    fid = normalize_format(format_kdp)
    pages = max(1, int(page_count))
    work_dir = output_dir or (AUTONOMOUS_VISUALS_DIR / f"vis_{int(time.time())}_{fid}")
    work_dir.mkdir(parents=True, exist_ok=True)

    sources_used: List[str] = []

    # 1. Spécifications KDP
    specs = calculate_kdp_specs(trim_id=fid, page_count=pages, paper_type=paper_type)
    trim_w_in, trim_h_in = KDP_FORMATS.get(fid, (6.0, 9.0))
    front_w_px = int(round(float(trim_w_in) * 300))
    front_h_px = int(round(float(trim_h_in) * 300))

    # --- ÉTAPE 1 : Recherche Stock en arrière-plan ---
    queries = _build_enriched_search_queries(
        niche=niche,
        category=category,
        target_audience=target_audience,
        title=title
    )
    selected_image: Optional[Dict[str, Any]] = None

    for q in queries:
        try:
            hits = search_stock_images(query=q, source="all", orientation="portrait", per_page=4)
            if hits:
                selected_image = hits[0]
                break
        except Exception as exc:
            print(f"⚠️ Note recherche stock pour '{q}' : {exc}")

    # --- ÉTAPE 2 : Téléchargement et préparation 300 DPI ---
    cover_bg_path: Optional[Path] = None
    if selected_image:
        img_source_type = selected_image.get("source", "curated")
        if img_source_type in ("unsplash", "pixabay"):
            sources_used.append(img_source_type)
        else:
            sources_used.append("curated")

        img_url = (
            selected_image.get("hd_url")
            or selected_image.get("regular_url")
            or selected_image.get("thumb_url")
        )
        if img_url:
            try:
                dest_name = f"cover_bg_{fid}_{pages}p_{selected_image.get('id', 'asset')}.jpg"
                cover_bg_path = download_and_prepare_cover_bg(
                    image_url=img_url,
                    target_width_px=front_w_px,
                    target_height_px=front_h_px,
                    output_filename=dest_name
                )
            except Exception as e:
                print(f"⚠️ Téléchargement fond de couverture échoué : {e}")

    # Si aucun fond stock n'a pu être téléchargé, création synthétique haute définition locale
    if not cover_bg_path or not cover_bg_path.exists():
        fallback_bg_name = f"cover_bg_local_{fid}_{pages}p.jpg"
        cover_bg_path = MEDIA_CACHE_DIR / fallback_bg_name
        if Image:
            img_syn = Image.new("RGB", (front_w_px, front_h_px), color="#0A0F1D")
            draw = ImageDraw.Draw(img_syn)
            for r in range(150, max(front_w_px, front_h_px), 75):
                draw.ellipse(
                    (front_w_px // 2 - r, front_h_px // 2 - r,
                     front_w_px // 2 + r, front_h_px // 2 + r),
                    outline="#D4AF37", width=3
                )
            img_syn.save(cover_bg_path, "JPEG", quality=95, dpi=(300, 300))
        sources_used.append("local_300dpi")

    # Génération des illustrations intérieures
    interior_illustrations = _generate_autonomous_interior_illustrations(
        category=category,
        niche=niche,
        output_dir=work_dir / "interior_illustrations",
        count=count_illustrations,
        source_bg_image=cover_bg_path
    )

    # --- ÉTAPE 3 : Synchronisation Canva Connect en arrière-plan ---
    canva_status, canva_data = _try_canva_background_autofill(
        cover_bg_path=cover_bg_path,
        title=title,
        subtitle=subtitle
    )
    if canva_status.startswith("autofill") or canva_status == "asset_uploaded_live":
        sources_used.append("canva_bg")

    # --- ÉTAPE 4 : Repli Local Haute Définition Garanti ---
    is_ar_rtl = language.strip().lower() in ("ar", "arabic", "العربية")
    cover_specs = calculate_cover_dimensions(
        trim_id=fid,
        page_count=pages,
        paper_type=paper_type,
        language=language,
        is_rtl=is_ar_rtl
    )

    svg_cover_content = generate_cover_template_svg(
        specs_or_trim=cover_specs,
        page_count=pages,
        paper_type=paper_type,
        book_title=title,
        author_name="MarkEddy",
        subtitle=subtitle,
        language=language,
        is_rtl=is_ar_rtl
    )
    cover_svg_path = work_dir / "couverture_calibree.svg"
    cover_svg_path.write_text(svg_cover_content, encoding="utf-8")

    if "local_300dpi" not in sources_used:
        sources_used.append("local_300dpi")

    # Nettoyage des doublons de sources en préservant l'ordre
    unique_sources = []
    for s in sources_used:
        if s not in unique_sources:
            unique_sources.append(s)

    return {
        "status": "success",
        "cover_asset_path": str(cover_svg_path),
        "cover_bg_path": str(cover_bg_path) if cover_bg_path else None,
        "interior_illustrations": interior_illustrations,
        "sources_used": unique_sources,
        "canva_background_status": canva_status,
        "selected_stock_image": selected_image,
        "cover_specs": cover_specs,
        "timestamp": int(time.time()),
    }
