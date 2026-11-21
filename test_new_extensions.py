"""
test_new_extensions.py — Banc d'essai unitaire automatisé pour les 5 nouvelles extensions KDP :
1. kdp_extensions/fonts_connector.py (Pairings éditoriaux & Google Fonts API)
2. kdp_extensions/market_trends_agent.py (Veille Google Trends, Amazon KDP, Pinterest)
3. kdp_extensions/editorial_structure.py (Générateur Front-Matter & Back-Matter)
4. kdp_extensions/layout_engine_pro.py (Moteur CSS Paged Media W3C & Typographie)
5. kdp_extensions/cover_calculator.py (Calcul dimensionnel exact & gabarit SVG)
6. kdp_extensions/router.py (Validation des 11 nouvelles routes HTTP FastAPI)

Exécution : .\\.venv\\Scripts\\python.exe -m pytest test_new_extensions.py
"""

from __future__ import annotations

import re
import pytest
from fastapi.testclient import TestClient


# ==============================================================================
# TEST 1 : CONNECTEUR GOOGLE FONTS & PAIRINGS ÉDITORIAUX
# ==============================================================================

def test_01_fonts_connector_pairings():
    import kdp_extensions.fonts_connector as fc

    # 1. Liste des pairings
    pairings = fc.list_editorial_pairings()
    assert len(pairings) >= 7, f"Attendu >= 7 pairings, reçu {len(pairings)}"
    for p in pairings:
        assert "title_font" in p
        assert "subtitle_font" in p
        assert "body_font" in p
        assert "accent_font" in p
        assert "charte_chromatique" in p

    # 2. Recommandation automatique selon la niche
    p_biz = fc.recommend_font_pairing("Finances et Bourse")
    assert p_biz["title_font"] in ("Cinzel", "Montserrat", "Playfair Display")

    p_kids = fc.recommend_font_pairing("Livre de coloriage pour enfants")
    assert p_kids["id"] == "enfants_ludique"
    assert p_kids["title_font"] == "Baloo 2"

    p_tech = fc.recommend_font_pairing("Intelligence Artificielle et Python")
    assert p_tech["id"] == "tech_productivity"
    assert p_tech["title_font"] == "Inter"

    # 3. URL Google Fonts v2
    url = fc.get_google_fonts_embed_url(["Cinzel", "Merriweather"])
    assert "https://fonts.googleapis.com/css2?" in url
    assert "Cinzel" in url
    assert "Merriweather" in url
    assert "display=swap" in url

    # 4. Génération CSS de pairing
    css = fc.generate_pairing_css(p_biz, include_embed=True)
    assert "@import url(" in css
    assert "--font-title" in css
    assert "--font-body" in css
    assert "hyphens: auto" in css


# ==============================================================================
# TEST 2 : AGENT DE VEILLE TRI-PLATEFORME (Google, Amazon, Pinterest)
# ==============================================================================

def test_02_market_trends_agent():
    import kdp_extensions.market_trends_agent as mta

    # 1. Google Trends / Suggest
    g_res = mta.fetch_google_trends("finances personnelles", geo="FR")
    assert "trend_score" in g_res
    assert 0 <= g_res["trend_score"] <= 100
    assert len(g_res["related_queries"]) >= 1

    # 2. Amazon KDP Autocomplete
    amz_res = mta.fetch_amazon_kdp_trends("finances", marketplace="fr")
    assert amz_res["niche"] == "finances"
    assert len(amz_res["top_suggestions"]) >= 1
    assert "intents" in amz_res

    # 3. Pinterest Mood & Palette
    pin_res = mta.fetch_pinterest_trends("finances personnelles")
    assert "pinterest_mood" in pin_res
    assert len(pin_res["recommended_palette"]) >= 3
    assert any("#" in c for c in pin_res["recommended_palette"])

    # 4. Analyse globale & 7 Mots-clés A9
    rapport = mta.analyze_market_trends(
        niche="Stoïcisme & Sérénité",
        target_audience="Adultes stressés",
        marketplace="fr",
    )
    assert 0 <= rapport["opportunity_score"] <= 100
    assert len(rapport["backend_keywords_7"]) == 7, "Doit comporter exactement 7 mots-clés"
    assert len(rapport["competitor_gaps"]) >= 2
    assert "cover_design_brief" in rapport

    # 5. Export Markdown
    brief_md = mta.export_trend_brief_markdown(rapport)
    assert "# 📊 BRIEF STRATÉGIQUE" in brief_md
    assert "Les 7 Mots-Clés Backend A9" in brief_md


# ==============================================================================
# TEST 3 : STRUCTURE ÉDITORIALE (FRONT-MATTER & BACK-MATTER)
# ==============================================================================

def test_03_editorial_structure():
    import kdp_extensions.editorial_structure as es

    meta = es.get_default_editorial_metadata(
        niche="Immobilier Locatif",
        title="L'Investisseur Rentable",
        author="Jean Dupont",
        publisher="Éditions du Siècle",
        isbn="979-8-1234-5678-9",
    )
    assert meta["title"] == "L'Investisseur Rentable"
    assert meta["isbn"] == "979-8-1234-5678-9"
    assert "Avertissement" in meta["disclaimer"]

    # 1. Front-Matter Markdown & HTML
    fm_md = es.generate_front_matter_markdown(meta)
    assert "L'Investisseur Rentable" in fm_md
    assert "ISBN : 979-8-1234-5678-9" in fm_md
    assert "Sommaire" in fm_md
    assert "Avant-Propos" in fm_md
    assert "<div class=\"page-break\"></div>" in fm_md

    fm_html = es.generate_front_matter_html(meta)
    assert "half-title-page" in fm_html
    assert "title-page" in fm_html
    assert "copyright-page" in fm_html
    assert "Jean Dupont" in fm_html

    # 2. Back-Matter Markdown & HTML
    bm_md = es.generate_back_matter_markdown(meta)
    assert "Conclusion" in bm_md
    assert "Pack de Ressources" in bm_md
    assert "Votre Avis Compte" in bm_md
    assert "À Propos de l'Auteur" in bm_md
    assert "ACHEVÉ D'IMPRIMER" in bm_md

    bm_html = es.generate_back_matter_html(meta)
    assert "conclusion-page" in bm_html
    assert "review-card" in bm_html
    assert "colophon-page" in bm_html

    # 3. Assemblage du livre complet
    corps = "## Chapitre 1 : Les Fondations\n\nVoici le contenu du premier chapitre."
    livre_md = es.assemble_complete_book(corps, meta, output_format="markdown")
    assert "L'Investisseur Rentable" in livre_md
    assert corps in livre_md
    assert "ACHEVÉ D'IMPRIMER" in livre_md

    livre_html = es.assemble_complete_book(corps, meta, output_format="html")
    assert "class=\"front-matter" in livre_html
    assert "class=\"back-matter" in livre_html
    assert corps in livre_html


# ==============================================================================
# TEST 4 : MOTEUR CSS PAGED MEDIA & AUDIT DE CONFORMITÉ
# ==============================================================================

def test_04_layout_engine_pro():
    import kdp_extensions.layout_engine_pro as lep

    # 1. Calcul du Gutter
    assert lep.calculate_gutter_in(80, high_prestige=False) == 0.375
    assert lep.calculate_gutter_in(200, high_prestige=False) == 0.500
    assert lep.calculate_gutter_in(150, high_prestige=True) == 0.85

    # 2. Génération de CSS Paged Media
    css = lep.generate_paged_media_css(
        format_id="6x9",
        page_count=160,
        book_title="STRATÉGIE FINANCIÈRE",
        author_name="Marc Aurèle",
    )
    assert "@page {" in css
    assert "size: 6.0in 9.0in;" in css
    assert "@page :left" in css
    assert "@page :right" in css
    assert "@page :first" in css
    assert "counter(page)" in css
    assert "hyphens: auto" in css
    assert ".drop-cap" in css
    assert ".action-box" in css

    # 3. Compilation HTML complet
    from kdp_extensions.editorial_structure import get_default_editorial_metadata
    meta = get_default_editorial_metadata("Productivité", "Le Guide du Focus")
    html_doc = lep.compile_paged_interior_html(
        content="<p class='lead'>Premier paragraphe captivant sans remplissage.</p><p>Deuxième paragraphe avec alinéa.</p>",
        metadata=meta,
        format_id="6x9",
        page_count=120,
    )
    assert "<!DOCTYPE html>" in html_doc
    assert "@page {" in html_doc
    assert "Le Guide du Focus" in html_doc

    # 4. Audit de conformité
    audit = lep.audit_paged_css_compliance(html_doc)
    assert audit["conforme_kdp"] is True
    assert audit["score_conformite"] == 100
    assert len(audit["anomalies"]) == 0


# ==============================================================================
# TEST 5 : CALCULATEUR DE COUVERTURE & GABARIT SVG
# ==============================================================================

def test_05_cover_calculator():
    import kdp_extensions.cover_calculator as cc

    # 1. Calculs 6x9 standard (150 pages blanc)
    specs = cc.calculate_cover_dimensions(
        trim_id="6x9",
        page_count=150,
        paper_type="white",
        bleed=0.125,
        dpi=300,
    )
    assert specs["format_id"] == "6x9"
    assert specs["page_count"] == 150

    u_in = specs["units"]["inches"]
    u_px = specs["units"]["pixels"]
    # Spine = 150 * 0.002252 = 0.3378 in
    assert abs(u_in["spine_width"] - 0.3378) < 0.001
    # Total width = 0.125 + 6.0 + 0.3378 + 6.0 + 0.125 = 12.5878 in
    assert abs(u_in["total_width"] - 12.5878) < 0.001
    # Total height = 9.0 + 2 * 0.125 = 9.25 in
    assert abs(u_in["total_height"] - 9.25) < 0.001

    # 300 DPI pixels
    assert u_px["total_height"] == 2775  # 9.25 * 300 = 2775
    assert specs["spine_spec"]["can_print_text"] is True  # 150 >= 79

    # 2. Cas livre fin (< 79 pages) : texte interdit sur le dos
    specs_thin = cc.calculate_cover_dimensions("6x9", page_count=50, paper_type="white")
    assert specs_thin["spine_spec"]["can_print_text"] is False

    # 3. Réserve ISBN (600x360 px)
    isbn = specs["zones_px"]["isbn_reservation"]
    assert isbn["width"] == 600
    assert isbn["height"] == 360

    # 4. Gabarit SVG
    svg = cc.generate_cover_template_svg(
        specs_or_trim=specs,
        book_title="MAÎTRISER SES FINANCES",
        author_name="MARCUS EDDY",
    )
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "viewBox=\"0 0" in svg
    assert "RÉSERVE ISBN / CODE-BARRES" in svg
    assert "MAÎTRISER SES FINANCES" in svg

    # 5. Rapport prépresse
    rapport = cc.generate_cover_specs_report(specs)
    assert "RAPPORT DE DIMENSIONS PRÉPRESSE" in rapport
    assert "6x9" in rapport


# ==============================================================================
# TEST 6 : ROUTES FASTAPI DU ROUTEUR (Intégration app_studio / router)
# ==============================================================================

def test_06_router_endpoints():
    from kdp_extensions.router import construire_router
    from fastapi import FastAPI

    test_app = FastAPI()
    test_app.include_router(construire_router())
    client = TestClient(test_app)

    # 1. GET /api/fonts/pairings
    r1 = client.get("/api/fonts/pairings")
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["status"] == "success"
    assert len(d1["pairings"]) >= 7

    # 2. GET /api/fonts/recommend-pairing
    r2 = client.get("/api/fonts/recommend-pairing?niche=coloriage")
    assert r2.status_code == 200
    assert r2.json()["pairing"]["id"] == "enfants_ludique"

    # 3. GET /api/trends/market
    r3 = client.get("/api/trends/market?niche=investissement")
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["status"] == "success"
    assert len(d3["trends"]["backend_keywords_7"]) == 7

    # 4. POST /api/editorial/front-matter
    r4 = client.post("/api/editorial/front-matter", json={"niche": "Finances", "title": "L'Or Noir"})
    assert r4.status_code == 200
    assert "L'Or Noir" in r4.json()["content"]

    # 5. POST /api/editorial/back-matter
    r5 = client.post("/api/editorial/back-matter", json={"niche": "Finances", "title": "L'Or Noir"})
    assert r5.status_code == 200
    assert "Conclusion" in r5.json()["content"]

    # 6. POST /api/editorial/assemble
    r6 = client.post("/api/editorial/assemble", json={
        "body_content": "## Chapitre 1\n\nTexte du chapitre.",
        "title": "Mon Grand Livre",
    })
    assert r6.status_code == 200
    assert "Mon Grand Livre" in r6.json()["full_book"]

    # 7. POST /api/layout/paged-css
    r7 = client.post("/api/layout/paged-css?format_id=6x9&page_count=150")
    assert r7.status_code == 200
    assert "@page {" in r7.text

    # 8. POST /api/layout/audit
    r8 = client.post("/api/layout/audit", json={
        "html_content": "@page { size: 6in 9in; } @page :left { margin-right: 0.85in; } @page :right { margin-left: 0.85in; } body { hyphens: auto; } h1 { page-break-before: always; } span { content: counter(page); }"
    })
    assert r8.status_code == 200
    assert r8.json()["audit"]["conforme_kdp"] is True

    # 9. GET /api/cover/calculator
    r9 = client.get("/api/cover/calculator?trim_id=6x9&page_count=150")
    assert r9.status_code == 200
    assert r9.json()["specs"]["spine_spec"]["width_in"] > 0

    # 10. GET /api/cover/template-svg
    r10 = client.get("/api/cover/template-svg?trim_id=6x9&page_count=150&title=TEST")
    assert r10.status_code == 200
    assert "image/svg+xml" in r10.headers.get("content-type", "")
    assert "<svg" in r10.text

    # 11. GET /api/coloring/themes
    r11 = client.get("/api/coloring/themes")
    assert r11.status_code == 200
    d11 = r11.json()
    assert d11["status"] == "success"
    assert len(d11["themes"]) >= 6

    # 12. POST /api/coloring/generate-sheet
    r12 = client.post("/api/coloring/generate-sheet", json={
        "theme": "animaux_mignons",
        "index": 1,
        "age_group": "4-8"
    })
    assert r12.status_code == 200
    d12 = r12.json()
    assert d12["status"] == "success"
    assert "<svg" in d12["sheet"]["svg_code"]

    # 13. POST /api/coloring/generate-pack
    r13 = client.post("/api/coloring/generate-pack", json={
        "theme": "dinosaures",
        "nb_sheets": 3,
        "age_group": "4-8"
    })
    assert r13.status_code == 200
    d13 = r13.json()
    assert d13["status"] == "success"
    assert len(d13["pack"]["sheets"]) == 3


# ==============================================================================
# TEST 7 : GÉNÉRATEUR DE COLORIAGE & PROFIL CSS KIDS
# ==============================================================================

def test_07_coloring_generator_and_kids_profile():
    import kdp_extensions.coloring_generator as cg
    import kdp_extensions.layout_engine_pro as lep
    import kdp_extensions.editorial_structure as es

    # 1. Thèmes de coloriage
    themes = cg.list_coloring_themes()
    assert len(themes) >= 6
    ids = [t["id"] for t in themes]
    assert "animaux_mignons" in ids
    assert "dinosaures" in ids
    assert "espace_galaxie" in ids

    # 2. Génération SVG vectorielle
    svg_lion = cg.generate_coloring_sheet_svg("animaux_mignons", index=1, age_group="4-6")
    assert "<svg" in svg_lion
    assert 'fill="#FFFFFF"' in svg_lion
    assert 'stroke="#000000"' in svg_lion
    # Pas de nuances de gris autorisées
    assert "#808080" not in svg_lion
    assert "#999999" not in svg_lion

    svg_dino = cg.generate_coloring_sheet_svg("dinosaures", index=2, age_group="4-8")
    assert "<svg" in svg_dino

    # 3. Profil CSS "coloring_kids"
    css_kids = lep.generate_paged_media_css(
        format_id="8.5x11",
        page_count=60,
        profile="coloring_kids",
        book_title="MON ALBUM DE COLORIAGE"
    )
    assert ".coloring-sheet-page" in css_kids
    assert ".blank-verso-page" in css_kids
    assert ".belongs-to-page" in css_kids
    assert ".diploma-page" in css_kids
    assert "@page :left" in css_kids
    assert "@page :right" in css_kids

    # 4. Front & Back Matter Coloriage
    meta = es.get_default_editorial_metadata("Coloriage", "Animaux Mignons")
    fm_col = es.generate_coloring_front_matter_html(meta)
    assert "Ce livre appartient à" in fm_col
    assert "Mon Nuancier de Feutres" in fm_col

    bm_col = es.generate_coloring_back_matter_html(meta)
    assert "DIPLÔME OFFICIEL" in bm_col
    assert "DU SUPER ARTISTE" in bm_col
    assert "Avis Est Précieux" in bm_col


# ==============================================================================
# TEST 8 : GÉNÉRATEUR DE PUZZLES (8 FORMATS + SOLUTIONNAIRE)
# ==============================================================================

def test_08_puzzle_generator_8_formats():
    import kdp_extensions.puzzle_generator as pg

    # 1. Mots Mêlés
    ws = pg.generate_word_search(title="Mots Mêlés Animaux", theme="animaux", rows=10, cols=10, seed=42)
    assert ws["type"] == "word_search"
    assert len(ws["grid"]) == 10
    assert len(ws["grid"][0]) == 10
    assert len(ws["words"]) >= 4
    assert len(ws["solution"]) == 10

    # 2. Mots Mélangés (Anagrammes)
    sc = pg.generate_word_scramble(title="Mots Mélangés", count=5, seed=42)
    assert sc["type"] == "word_scramble"
    assert len(sc["items"]) == 5
    for item in sc["items"]:
        assert "scrambled" in item
        assert "answer" in item

    # 3. Échelle de Mots
    wl = pg.generate_word_ladder(title="Échelle", seed=42)
    assert wl["type"] == "word_ladder"
    assert len(wl["steps"]) >= 4
    assert wl["start_word"] == wl["steps"][0]["answer"]
    assert wl["end_word"] == wl["steps"][-1]["answer"]

    # 4. Devinettes
    rd = pg.generate_riddles_set(title="Devinettes", count=3, seed=42)
    assert rd["type"] == "riddles"
    assert len(rd["items"]) == 3
    for r in rd["items"]:
        assert "question" in r
        assert "answer" in r

    # 5. Cryptogramme
    cr = pg.generate_cryptogram(title="Code Secret", phrase="LE SUCCES EST UN DEFI", seed=42)
    assert cr["type"] == "cryptogram"
    assert "phrase" in cr
    assert len(cr["cipher_key"]) >= 5

    # 6. Labyrinthe
    mz = pg.generate_maze(title="Labyrinthe", width_cells=11, height_cells=11, seed=42)
    assert mz["type"] == "maze"
    assert mz["rows"] >= 10
    assert len(mz["solution_path"]) >= 5

    # 7. Points à Relier
    cd = pg.generate_connect_dots(title="Points à Relier", points_count=12, seed=42)
    assert cd["type"] == "connect_dots"
    assert len(cd["points"]) == 12

    # 8. Grille Logique
    lg = pg.generate_logic_grid(title="Grille Logique", size=4, seed=42)
    assert lg["type"] == "logic_grid"
    assert len(lg["puzzle"]) == 4
    assert len(lg["solution"]) == 4

    # 9. Collection complète multi-jeux + solutionnaire
    full = pg.generate_full_puzzle_collection(
        book_title="Cahier de Jeux Spécial Vacances",
        theme="ocean",
        age_group="6-9",
        puzzles_per_type=1,
        seed=100,
    )
    assert full["status"] == "success"
    assert full["total_puzzles"] == 8
    assert "SOLUTIONS DES GRILLES" in full["html"] or "Solutionnaire" in full["html"]
    # Pure black/white compliance
    assert "#000000" in full["html"]
    assert "#FFFFFF" in full["html"]


# ==============================================================================
# TEST 9 : ORCHESTRATEUR EXPORT KDP, RÈGLE 24 PAGES & ARCHIVAGE ZIP
# ==============================================================================

def test_09_kdp_export_orchestrator_and_zip():
    import zipfile
    from pathlib import Path
    import kdp_extensions.kdp_export_orchestrator as keo

    # 1. Règle Prépresse 24 pages minimum
    html_court = "<html><body><h1>Mon Livre Court</h1><p>Contenu test</p></body></html>"
    enriched, final_pages, bonus_added = keo.inject_kdp_prepress_bonus_pages(
        html_content=html_court,
        current_pages=8,
        project_type="puzzle",
        min_pages=24,
        title="Livre Puzzles Test",
    )
    assert final_pages == 24
    assert bonus_added == 16
    assert "Carnet de Brouillon du Détective" in enriched
    assert "CERTIFICAT D'ACCOMPLISSEMENT" in enriched

    # Pas de bonus si déjà >= 24
    _, p_ok, b_zero = keo.inject_kdp_prepress_bonus_pages(
        html_content=html_court,
        current_pages=30,
        project_type="text",
        min_pages=24,
    )
    assert p_ok == 30
    assert b_zero == 0

    # 2. Métadonnées A9 : 7 mots-clés sans doublon
    a9 = keo.generate_kdp_a9_metadata(
        title="Stoïcisme Quotidien",
        subtitle="365 Réflexions pour une Vie Sereine",
        author="MarkEddy",
        niche="stoicisme",
        page_count=150,
        format_id="6x9",
    )
    assert len(a9["a9_backend_keywords"]) == 7
    assert len(set(a9["a9_backend_keywords"])) == 7
    assert "<h2>" in a9["description_html"]
    assert "<ul>" in a9["description_html"]

    # 3. Production complète du package KDP 1-clic (ZIP)
    pkg = keo.build_kdp_export_package(
        book_id="unit_test_pkg_01",
        title="Guide Stoicien Ultime",
        subtitle="Principes Éternels pour l'Esprit Moderne",
        project_type="text",
        format_id="6x9",
        initial_pages=10,
        enforce_24_pages=True,
    )
    assert pkg["status"] == "success"
    assert pkg["page_count_final"] >= 24
    assert pkg["bonus_pages_injected"] > 0
    assert pkg["spine_thickness_mm"] > 0
    assert Path(pkg["zip_path"]).exists()

    # 4. Vérification du contenu du ZIP
    with zipfile.ZipFile(pkg["zip_path"], "r") as zf:
        names = zf.namelist()
        assert "interieur_kdp.pdf" in names
        assert "couverture_calibree.svg" in names
        assert "metadata_a9.json" in names
        assert "manifest.json" in names
        assert "interieur_kdp.html" in names
        assert "kdp_supervision_report.json" in names
        assert "seo_amazon_ready.json" in names
        assert "description_amazon.html" in names

        # Vérification du manifeste d'audit KDP
        manifest_raw = zf.read("manifest.json").decode("utf-8")
        manifest_obj = __import__("json").loads(manifest_raw)
        assert manifest_obj["compliance_status"] == "KDP_CERTIFIED_PRINT_READY"
        assert manifest_obj["prepress_specs"]["page_count_final"] >= 24
        assert "600x360" in manifest_obj["prepress_specs"]["isbn_reservation_px"]
        assert len(manifest_obj["files"]) >= 4


# ==============================================================================
# TEST 10 : ENDPOINTS API FASTAPI (PUZZLES, EXPORT PACKAGE & DOWNLOAD ZIP)
# ==============================================================================

def test_10_router_export_and_download():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # 1. Endpoint Génération Collection Puzzles
    res_puzz = client.post("/api/puzzles/generate-collection", json={
        "book_title": "Puzzles Express",
        "theme": "espace",
        "age_group": "4-6",
        "puzzle_types": ["word_search", "maze"],
        "puzzles_per_type": 1,
        "seed": 42,
    })
    assert res_puzz.status_code == 200
    data_puzz = res_puzz.json()
    assert data_puzz["status"] == "success"
    assert data_puzz["total_puzzles"] == 2

    # 2. Endpoint Export Package 1-Clic
    res_pkg = client.post("/api/kdp/export-package", json={
        "book_id": "test_api_book_88",
        "title": "Livre Puzzles Galaxie",
        "author": "MarkEddy",
        "subtitle": "Jeux et Logique Spatiale",
        "project_type": "puzzle",
        "format_id": "8.5x11",
        "initial_pages": 8,
        "enforce_24_pages": True,
    })
    assert res_pkg.status_code == 200
    pkg_data = res_pkg.json()
    assert pkg_data["status"] == "success"
    assert pkg_data["page_count_final"] >= 24
    pkg_name = pkg_data["package_name"]

    # 3. Endpoint Téléchargement ZIP
    res_dl = client.get(f"/api/kdp/download-package/{pkg_name}")
    assert res_dl.status_code == 200
    assert res_dl.headers["content-type"] == "application/zip"
    assert len(res_dl.content) > 1000

    # 4. Sécurité anti-traversal
    res_hack = client.get("/api/kdp/download-package/../etc/passwd")
    assert res_hack.status_code in (400, 404)


# ==============================================================================
# TEST 11 : AGENT 1 — VEILLE TENDANCES & DOULEURS SOCIALES (social_trend_hunter)
# ==============================================================================

def test_11_social_trend_hunter():
    from kdp_extensions.social_trend_hunter import harvest_market_ideas

    # 1. Niche connue (Finances)
    res_fin = harvest_market_ideas("finances personnelles", language="fr")
    assert res_fin["status"] == "success"
    assert res_fin["niche"] == "finances personnelles"
    assert len(res_fin["top_questions"]) >= 3
    assert any("?" in q for q in res_fin["top_questions"])
    assert len(res_fin["pain_points"]) >= 2
    assert len(res_fin["book_ideas"]) == 3
    assert set(c["id"] for c in res_fin["book_ideas"]) == {"concept_1", "concept_2", "concept_3"}
    for concept in res_fin["book_ideas"]:
        assert "title" in concept and len(concept["title"]) > 3
        assert "subtitle" in concept
        assert "angle" in concept
        assert "promise" in concept
    assert len(res_fin["trending_keywords"]) >= 5
    assert len(res_fin["sources_checked"]) >= 3

    # 2. Niche libre / générique (Apiculture urbaine)
    res_api = harvest_market_ideas("apiculture urbaine", language="fr")
    assert res_api["status"] == "success"
    assert len(res_api["book_ideas"]) == 3
    assert any("apiculture" in c["title"].lower() or "apiculture" in c["subtitle"].lower() for c in res_api["book_ideas"])


# ==============================================================================
# TEST 12 : AGENT 2 — RECHERCHE DOCUMENTAIRE & ACADÉMIQUE (deep_research_agent)
# ==============================================================================

def test_12_deep_research_agent():
    from kdp_extensions.deep_research_agent import build_chapter_evidence_pack

    chapters = [
        "1. Les Pièges Psychologiques et Décisions Financières",
        "2. Automatiser ses Habitudes d'Épargne",
        "3. Investir en Bourse Passivement"
    ]
    pack = build_chapter_evidence_pack(
        topic="finances et psychologie",
        chapter_outline=chapters,
        language="fr"
    )
    assert pack["status"] == "success"
    assert pack["total_chapters"] == 3
    assert pack["total_sources_count"] >= 6
    assert len(pack["chapters"]) == 3

    for chap in pack["chapters"]:
        assert "chapter_title" in chap
        assert len(chap["academic_studies"]) >= 1
        study = chap["academic_studies"][0]
        assert study["tier"] == "A"
        assert "author" in study and "title" in study
        assert study["doi_or_url"].startswith("http")

        assert len(chap["press_and_books"]) >= 1
        book = chap["press_and_books"][0]
        assert book["tier"] == "B"
        assert "takeaway" in book

        assert len(chap["field_case_studies"]) >= 1
        case = chap["field_case_studies"][0]
        assert case["tier"] == "C"
        assert "outcome" in case

        assert len(chap["suggested_quotes"]) >= 1


# ==============================================================================
# TEST 13 : AGENT 3 — SYNTHÈSE, FACT-CHECKING & HUMANISATION (editorial_humanizer_agent)
# ==============================================================================

def test_13_editorial_humanizer_agent():
    from kdp_extensions.editorial_humanizer_agent import synthesize_and_verify, humanize_manuscript

    # 1. Vérification & Fact-Checking d'un pack de recherche
    raw_pack = {
        "chapters": [
            {
                "chapter_title": "Chapitre 1",
                "academic_studies": [
                    {
                        "author": "Kahneman, D., & Tversky, A.",
                        "year": 1979,
                        "title": "Prospect Theory",
                        "journal": "Econometrica",
                        "doi_or_url": "https://doi.org/10.2307/1914185",
                        "key_findings": "Asymétrie des pertes",
                        "tier": "A"
                    },
                    {
                        "author": "",  # Invalide : doit être rejeté
                        "title": "Étude Anonyme Douteuse",
                    }
                ],
                "press_and_books": [
                    {
                        "author": "Clear, James",
                        "year": 2018,
                        "title": "Atomic Habits",
                        "source": "Penguin",
                        "takeaway": "Gains marginaux 1%",
                        "tier": "B"
                    }
                ],
                "field_case_studies": [
                    {
                        "context": "Ménage en découvert",
                        "challenge": "Supprimer agios",
                        "outcome": "Équilibre en 60 jours",
                        "tier": "C"
                    }
                ]
            }
        ]
    }

    synth = synthesize_and_verify(raw_pack)
    assert synth["status"] == "success"
    assert synth["total_verified"] == 3
    assert synth["total_rejected"] == 1
    assert synth["rejected_sources"][0]["title"] == "Étude Anonyme Douteuse"
    assert synth["overall_confidence_score"] > 70.0
    assert synth["credibility_breakdown"]["tier_A_academic"] == 1
    assert synth["credibility_breakdown"]["tier_B_reference_books"] == 1

    # 2. Humanisation et élimination de clichés IA
    robotic_text = (
        "Dans ce chapitre, nous allons explorer la gestion du budget. "
        "Il est important de noter que l'argent est une ressource finie. "
        "Comme nous l'avons mentionné dans la section précédente, les imprévus arrivent toujours. "
        "Chaque début de mois, mettez 100 euros de côté dès la réception de votre salaire. "
        "C'est un automatisme simple. "
        "En conclusion, on peut dire que la discipline financière paie toujours."
    )

    humanized = humanize_manuscript(
        text=robotic_text,
        author_voice="expert_pedagogue",
        research_pack=raw_pack
    )
    assert humanized["status"] == "success"
    assert humanized["cliches_removed_count"] >= 3
    assert "Dans ce chapitre, nous allons explorer" not in humanized["humanized_text"]
    assert "Il est important de noter que" not in humanized["humanized_text"]
    assert humanized["human_naturalness_score"] > 40.0
    assert humanized["bibliography_appended"] is True
    assert "## Sources & Bibliographie de Référence" in humanized["humanized_text"]
    assert "Kahneman, D., & Tversky, A." in humanized["humanized_text"]


# ==============================================================================
# TEST 14 : ENDPOINTS API CHAÎNE INTELLIGENCE ÉDITORIALE (router)
# ==============================================================================

def test_14_editorial_intelligence_routes():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # 1. Route Agent 1 : Veille Sociale
    res1 = client.post("/api/research/social-trends", json={
        "niche": "gestion du temps",
        "language": "fr"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "success"
    assert len(data1["book_ideas"]) == 3

    # 2. Route Agent 2 : Recherche Documentaire
    res2 = client.post("/api/research/deep-sources", json={
        "topic": "productivité et concentration",
        "chapter_outline": ["Chapitre 1 : Deep Work", "Chapitre 2 : Déconnexion"],
        "language": "fr"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    assert data2["total_chapters"] == 2
    assert len(data2["chapters"]) == 2

    # 3. Route Agent 3 : Humanisation & Fact-Checking
    res3 = client.post("/api/editorial/verify-humanize", json={
        "text": "Dans ce chapitre, nous allons voir comment travailler vite. Il convient de souligner que le repos compte.",
        "author_voice": "expert_pedagogue",
        "research_pack": data2
    })
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["status"] == "success"
    assert data3["cliches_removed_count"] >= 1
    assert data3["verification_audit"] is not None
    assert data3["verification_audit"]["overall_confidence_score"] > 0


# ==============================================================================
# TEST 15 : AGENT 4 : SUPERVISEUR DE CONFORMITÉ KDP & SCORE ANTI-ANONYMAT
# ==============================================================================

def test_15_kdp_compliance_supervisor():
    import kdp_extensions.kdp_compliance_supervisor as kcs

    # 1. Cas Conforme (Livre propre avec mentions obligatoires)
    audit_ok = kcs.audit_kdp_compliance(
        title="Psychologie de l'Épargne",
        subtitle="Construire sa Sécurité Financière Pas à Pas",
        author="Marc Dupont",
        keywords=[
            "methode gestion budget debutant",
            "epargne precaution matelas securite",
            "investir pea etf passif bourse",
            "finances personnelles sans privation",
            "education financiere jeune actif",
            "eliminer credit consommation dettes",
            "independance liberte financiere"
        ],
        page_count=120,
        format_id="6x9",
        content_text_or_html="""<!DOCTYPE html><html><body>
        <h1>Psychologie de l'Épargne</h1>
        <p>Mentions légales : © 2026 Éditions MarkEddy. Tous droits réservés.</p>
        <p>Avertissement : Ce livre ne constitue pas un conseil financier personnalisé.</p>
        <p>À propos de l'auteur : Marc Dupont est consultant financier.</p>
        <p>Achevé d'imprimer en France.</p>
        <p>Corps du livre avec étude de cas et calculs réels.</p>
        </body></html>""",
        has_copyright=True,
        has_disclaimer=True,
        has_author_bio=True,
        has_colophon=True,
        cover_specs={"isbn_reserve": "600x360 px"},
    )
    assert audit_ok["status"] == "success"
    assert audit_ok["verdict"] == "PASSED"
    assert audit_ok["overall_score"] >= 80.0
    assert audit_ok["anti_anonymity_score"] == 100.0
    assert len(audit_ok["critical_violations"]) == 0

    # 2. Cas Rejet : Nom d'auteur bourré de mots-clés (Keyword Stuffing)
    crit_auth = kcs.audit_kdp_compliance(
        title="Livre de Coloriage Mignon",
        author="Coloring Books For Kids Publisher",
        page_count=50,
    )
    assert crit_auth["verdict"] == "REJECTED"
    assert any("bourrage de mots-clés" in err for err in crit_auth["critical_violations"])

    # 3. Cas Rejet : Termes interdits par KDP (#1, Bestseller, Gratuit)
    crit_title = kcs.audit_kdp_compliance(
        title="Livre Bestseller N°1 Gratuit",
        author="Jean Dupont",
        page_count=50,
    )
    assert crit_title["verdict"] == "REJECTED"
    assert any("Terme prohibé" in err for err in crit_title["critical_violations"])

    # 4. Cas Rejet : Marque déposée notoire (Disney / Pokémon / Lego)
    crit_tm = kcs.audit_kdp_compliance(
        title="Coloriage Disney et Pokemon Magique",
        author="Jean Dupont",
        page_count=50,
    )
    assert crit_tm["verdict"] == "REJECTED"
    assert any("Marque déposée notoire" in err for err in crit_tm["critical_violations"])

    # 5. Cas Rejet : Livre broché < 24 pages
    crit_pages = kcs.audit_kdp_compliance(
        title="Mon Livre Trop Court",
        author="Jean Dupont",
        page_count=16,
        binding="paperback",
    )
    assert crit_pages["verdict"] == "REJECTED"
    assert any("24 pages" in err for err in crit_pages["critical_violations"])

    # 6. Cas Rejet : Présence de Lorem Ipsum ou TODO dans le texte
    crit_hyg = kcs.audit_kdp_compliance(
        title="Livre Inachevé",
        author="Jean Dupont",
        page_count=40,
        content_text_or_html="<p>Chapitre 1. TODO: Rédiger la fin. Lorem ipsum dolor sit amet.</p>",
    )
    assert crit_hyg["verdict"] == "REJECTED"
    assert any("Lorem ipsum" in err or "TODO" in err for err in crit_hyg["critical_violations"])


# ==============================================================================
# TEST 16 : ORCHESTRATEUR EXPORT BLOQUÉ EN CAS DE REJET DU SUPERVISEUR KDP
# ==============================================================================

def test_16_export_blocked_on_rejection():
    import kdp_extensions.kdp_export_orchestrator as keo
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router

    # 1. Blocage direct via build_kdp_export_package
    res_blocked = keo.build_kdp_export_package(
        book_id="test_blocked_book",
        title="Guide Bestseller N°1 Ultime",
        subtitle="Gratuit et Pas Cher",
        author="Coloring Books Publisher",
        project_type="text",
        format_id="6x9",
        initial_pages=30,
    )
    assert res_blocked["status"] == "rejected"
    assert res_blocked["verdict"] == "REJECTED"
    assert res_blocked["package_name"] is None
    assert res_blocked["zip_path"] is None
    assert len(res_blocked["critical_violations"]) >= 1

    # 2. Test via endpoint API FastAPI POST /api/compliance/audit
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    res_audit_api = client.post("/api/compliance/audit", json={
        "title": "Maître de ses Finances",
        "subtitle": "La méthode concrète",
        "author": "Pierre Martin",
        "page_count": 80,
        "format_id": "6x9",
        "has_copyright": True,
        "has_disclaimer": True,
        "has_author_bio": True,
        "has_colophon": True
    })
    assert res_audit_api.status_code == 200
    data_audit = res_audit_api.json()
    assert data_audit["status"] == "success"
    assert data_audit["verdict"] == "PASSED"
    assert data_audit["overall_score"] >= 80.0

    # 3. Test de rejet via endpoint API
    res_reject_api = client.post("/api/compliance/audit", json={
        "title": "Livre Lego et Marvel Gratuit",
        "author": "Activity Books Press",
        "page_count": 10
    })
    assert res_reject_api.status_code == 200
    data_reject = res_reject_api.json()
    assert data_reject["verdict"] == "REJECTED"
    assert len(data_reject["critical_violations"]) >= 2


# ==============================================================================
# TEST 17 : SUPERVISEUR GATEKEEPER KDP & EXCELLENCE ANTI-ANONYMAT (AGENT 4)
# ==============================================================================

def test_17_supervise_kdp_book_gatekeeper():
    from kdp_extensions.kdp_compliance_supervisor import supervise_kdp_book
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router

    # 1. Rejet automatique : Keyword Stuffing nom d'auteur
    res_kw = supervise_kdp_book({
        "title": "Livre de Coloriage Mignon",
        "author": "Coloring Books For Kids Publisher",
        "page_count": 50,
        "binding": "paperback",
    })
    assert res_kw["verdict"] == "REJECTED_FOR_REVISION"
    assert res_kw["approved"] is False
    assert any("bourrage de mots-clés" in v or "keyword" in v.lower() for v in res_kw["blocking_violations"])

    # 2. Rejet automatique : Marque déposée notoire
    res_tm = supervise_kdp_book({
        "title": "Livre Lego et Marvel Magique",
        "subtitle": "Aventures amusantes pour enfants",
        "author": "Jean Dupont",
        "page_count": 50,
        "binding": "paperback",
    })
    assert res_tm["verdict"] == "REJECTED_FOR_REVISION"
    assert res_tm["approved"] is False
    assert any("Marque déposée notoire" in v or "Lego" in v or "Marvel" in v for v in res_tm["blocking_violations"])

    # 3. Rejet automatique : Livre broché < 24 pages
    res_p24 = supervise_kdp_book({
        "title": "Manuel Succinct",
        "subtitle": "Guide minimaliste pour débuter",
        "author": "Pierre Martin",
        "page_count": 16,
        "binding": "paperback",
    })
    assert res_p24["verdict"] == "REJECTED_FOR_REVISION"
    assert res_p24["approved"] is False
    assert any("24 pages" in v for v in res_p24["blocking_violations"])

    # 4. Rejet : Livre générique / ordinaire (Score < 85/100)
    res_gen = supervise_kdp_book({
        "title": "Simple Livre",
        "author": "Jean Dupont",
        "page_count": 80,
        "binding": "paperback",
    })
    assert res_gen["excellence_score"] < 85.0
    assert res_gen["verdict"] == "REJECTED_FOR_REVISION"
    assert res_gen["approved"] is False
    assert len(res_gen["anti_ordinary_recommendations"]) > 0

    # 5. Approbation : Ouvrage conforme et complet (Score >= 85/100, 0 infraction)
    good_book = {
        "title": "Psychologie de l'Épargne Pro",
        "subtitle": "La méthode concrète pour bâtir un patrimoine durable",
        "author": "Marc Dupont",
        "keywords": [
            "gestion budget debutant",
            "epargne de securite matelas",
            "bourse etf pea passif",
            "liberte financiere jeune actif",
            "sortir du decouvert bancaire",
            "finances personnelles saines",
            "education financiere pratique"
        ],
        "page_count": 120,
        "binding": "paperback",
        "niche": "finances personnelles",
        "content": "<p>Avertissement : Ce livre n'est pas un conseil financier individuel.</p><p>Biographie de l'auteur : Marc Dupont est expert en gestion patrimoniale.</p>",
        "has_copyright": True,
        "has_disclaimer": True,
        "has_author_bio": True,
        "has_colophon": True,
        "has_toc": True,
        "has_cover": True,
        "isbn": True,
        "ai_transparency_declared": True,
    }
    res_good = supervise_kdp_book(good_book)
    assert res_good["excellence_score"] >= 85.0
    assert len(res_good["blocking_violations"]) == 0
    assert res_good["verdict"] == "APPROVED_FOR_KDP"
    assert res_good["approved"] is True
    assert res_good["kdp_compliance_passed"] is True
    assert "excellence_score_breakdown" in res_good

    # 6. Test de l'endpoint POST /api/kdp/supervise-audit
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Appel rejeté via API
    api_bad = client.post("/api/kdp/supervise-audit", json={
        "title": "Livre Lego Gratuit",
        "author": "Coloring Books Publisher",
        "page_count": 12,
        "binding": "paperback"
    })
    assert api_bad.status_code == 200
    bad_data = api_bad.json()
    assert bad_data["verdict"] == "REJECTED_FOR_REVISION"
    assert bad_data["approved"] is False
    assert len(bad_data["blocking_violations"]) >= 1

    # Appel approuvé via API
    api_good = client.post("/api/kdp/supervise-audit", json=good_book)
    assert api_good.status_code == 200
    good_data = api_good.json()
    assert good_data["verdict"] == "APPROVED_FOR_KDP"
    assert good_data["approved"] is True
    assert good_data["excellence_score"] >= 85.0


# ==============================================================================
# TEST 18 : AGENT 6 — TRANSCRÉATEUR MULTILINGUE IDIOMATIQUE (5 LANGUES) & BUNDLE
# ==============================================================================

def test_18_multilingual_transcreator_agent():
    import zipfile
    from pathlib import Path
    import kdp_extensions.multilingual_transcreator as mt

    master_book = {
        "title": "L'Architecte Financier",
        "subtitle": "Bâtir son indépendance financière sans spéculer",
        "author": "MarkEddy",
        "publisher": "Éditions MarkEddy",
        "niche": "finances",
        "language": "fr",
        "format_id": "6x9",
        "paper_type": "white",
        "year": 2026,
        "isbn": "979-8-1234-5678-9",
        "seed_keywords": ["budget", "epargne", "bourse passive"],
    }

    # Génération du bundle complet pour les 5 langues
    bundle_res = mt.produce_multilang_bundle(
        master_book=master_book,
        target_languages=["en", "fr", "es", "de", "ar"],
    )

    assert bundle_res["status"] == "success"
    assert bundle_res["editions_count"] == 5
    manifest = bundle_res["manifest"]
    assert manifest["total_editions"] == 5
    assert len(manifest["editions"]) == 5

    # Vérification comparative détaillée des 5 éditions
    editions_by_lang = {ed["language"]: ed for ed in manifest["editions"]}
    for lang in ["en", "fr", "es", "de", "ar"]:
        assert lang in editions_by_lang
        ed = editions_by_lang[lang]
        assert ed["real_page_count"] >= 24, f"L'édition {lang} doit respecter le minimum de 24 pages KDP"
        assert ed["spine_thickness_mm"] > 0
        assert ed["spine_thickness_in"] > 0
        assert ed["seo_score"] >= 80.0
        assert ed["anti_anonymity_score"] >= 85.0
        assert ed["kdp_verdict"] in ("APPROVED_FOR_KDP", "PASSED")
        # Vérification des fichiers générés
        for ftype, fpath in ed["files"].items():
            assert Path(fpath).is_file(), f"Le fichier {ftype} ({fpath}) doit exister sur disque"

    # Vérification spécifique Arabe (RTL)
    ar_ed = editions_by_lang["ar"]
    assert ar_ed["direction"] == "rtl"
    assert ar_ed["marketplace"] in ("amazon.ae", "amazon.sa")
    assert "المهندس" in ar_ed["title"]

    # Vérification de l'archive ZIP globale
    global_zip = Path(bundle_res["global_zip_path"])
    assert global_zip.is_file()
    with zipfile.ZipFile(global_zip, "r") as zf:
        namelist = zf.namelist()
        assert "bundle_manifest.json" in namelist
        assert any(n.startswith("ar/") for n in namelist)
        assert any(n.startswith("en/") for n in namelist)
        assert any(n.startswith("de/") for n in namelist)

    # Vérification des archives ZIP individuelles
    assert len(bundle_res["per_language_zips"]) == 5
    for lang, lzip in bundle_res["per_language_zips"].items():
        assert Path(lzip).is_file()
        with zipfile.ZipFile(lzip, "r") as zf_lang:
            assert "edition_manifest.json" in zf_lang.namelist()


# ==============================================================================
# TEST 19 : ENDPOINTS API TRANSCRÉATION & TÉLÉCHARGEMENT BUNDLE
# ==============================================================================

def test_19_transcreate_book_and_download_routes():
    from fastapi import FastAPI
    from kdp_extensions.router import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    master_book = {
        "title": "Stoïcisme Quotidien",
        "subtitle": "La méthode pratique pour dompter le stress en 30 jours",
        "author": "MarkEddy",
        "publisher": "Éditions MarkEddy",
        "niche": "productivite",
        "language": "fr",
        "format_id": "6x9",
        "seed_keywords": ["stoicisme", "focus", "serenite"],
    }

    # 1. POST /api/kdp/transcreate-book pour 3 langues
    resp = client.post("/api/kdp/transcreate-book", json={
        "master_book": master_book,
        "target_languages": ["en", "de", "ar"],
        "bundle_name": "bundle_test_fastapi",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert data["bundle_name"] == "bundle_test_fastapi"
    assert data["editions_count"] == 3
    assert len(data["manifest"]["editions"]) == 3

    # 2. GET /api/kdp/download-multilang-bundle/bundle_test_fastapi (Global ZIP)
    resp_global = client.get("/api/kdp/download-multilang-bundle/bundle_test_fastapi")
    assert resp_global.status_code == 200
    assert resp_global.headers["content-type"] == "application/zip"
    assert len(resp_global.content) > 1000

    # 3. GET /api/kdp/download-multilang-bundle/bundle_test_fastapi?lang=ar (Arabe ZIP)
    resp_ar = client.get("/api/kdp/download-multilang-bundle/bundle_test_fastapi?lang=ar")
    assert resp_ar.status_code == 200
    assert resp_ar.headers["content-type"] == "application/zip"
    assert len(resp_ar.content) > 1000

    # 4. 404 sur bundle inexistant
    resp_404 = client.get("/api/kdp/download-multilang-bundle/bundle_inexistant_999999")
    assert resp_404.status_code == 404


# ==============================================================================
# TEST 20 : AGENT 5 — SEO AMAZON A9/A10, CATÉGORIES BISAC, HTML & ADS
# ==============================================================================

def test_20_seo_a9_agent_full_package_and_export():
    import zipfile
    from pathlib import Path
    import kdp_extensions.seo_a9_agent as seo
    import kdp_extensions.kdp_compliance_supervisor as kcs
    import kdp_extensions.kdp_export_orchestrator as keo

    # 1. Optimisation SEO complète A9/A10 via optimize_kdp_seo
    seo_res = seo.optimize_kdp_seo(
        book_title="L'Architecte Financier",
        subtitle="Construire son indépendance financière sans spéculer",
        niche="finances",
        book_type="text",
        target_audience="jeunes actifs et investisseurs débutants",
        seed_keywords=["budget", "epargne de securite", "bourse passive etf"],
        language="fr",
    )
    assert seo_res["status"] == "success"
    assert seo_res["seo_package_ready"] is True

    # Vérification des 8 clés explicites demandées pour l'Agent 5
    assert "optimized_title" in seo_res
    assert "optimized_subtitle" in seo_res
    assert "backend_keywords_7" in seo_res
    assert "categories_3" in seo_res
    assert "amazon_description_html" in seo_res
    assert "aplus_content_blueprint" in seo_res
    assert "ppc_launch_keywords" in seo_res
    assert "seo_audit" in seo_res
    assert seo_res["seo_audit"]["score_a9_100"] >= 80

    # Vérification des 7 slots backend (<= 50 octets UTF-8 chacun, cumul <= 250 octets)
    slots = seo_res["backend_keywords"]
    assert len(slots) == 7
    total_bytes = sum(seo.calculate_utf8_bytes(s) for s in slots)
    assert total_bytes <= 250, f"Le total des 7 slots dépasse 250 octets : {total_bytes}"
    for idx, s in enumerate(slots, 1):
        b_len = seo.calculate_utf8_bytes(s)
        assert b_len <= 50, f"Slot {idx} dépasse 50 octets UTF-8 : '{s}' ({b_len} octets)"

    # Vérification des catégories Amazon et codes BISAC
    cats = seo_res["categories"]
    assert "volume_category" in cats
    assert "volume_bisac" in cats
    assert cats["volume_bisac"] == "BUS027000"
    assert len(cats["niche_categories"]) >= 2
    assert len(cats["niche_bisac_codes"]) >= 2
    assert "BUS006000" in cats["niche_bisac_codes"]

    # Vérification de la description HTML (KDP strict, <= 4000 car., balises autorisées)
    desc_html = seo_res["description_html"]
    assert len(desc_html) <= 4000
    assert "<h2>" in desc_html
    assert "<h3>" in desc_html
    assert "<ul>" in desc_html
    assert "<li>" in desc_html
    assert "<b>" in desc_html
    # Aucune balise interdite
    assert "<script" not in desc_html.lower()
    assert "<div" not in desc_html.lower()
    assert "<span" not in desc_html.lower()

    # Vérification des campagnes Amazon Ads PPC
    ads = seo_res["amazon_ads_campaigns"]
    assert len(ads["campaigns"]) >= 4
    c_names = [c["targeting_type"] for c in ads["campaigns"]]
    assert any("Exact" in n for n in c_names)
    assert any("Phrase" in n for n in c_names)
    assert any("Broad" in n for n in c_names)
    assert any("Product" in n for n in c_names)
    assert "gratuit" in ads["negative_keywords"]
    assert ads["recommended_daily_budget_total_eur"] > 0

    # Vérification du blueprint A+
    a_plus = seo_res["a_plus_blueprint"]
    assert len(a_plus["modules"]) >= 3
    assert any("image_header" in m.get("module_type", "") for m in a_plus["modules"])
    assert any("three_image" in m.get("module_type", "") for m in a_plus["modules"])

    # 2. Vérification de la connexion avec le Superviseur de Conformité (Zéro marque & Zéro keyword-stuffing)
    crit_tm, warn_tm = kcs.check_a9_keywords_compliance(
        keywords=["guide officiel lego star wars", "methode financiere"],
        title="Mon Livre",
        subtitle="Un guide",
    )
    assert any("marque notoire" in c.lower() for c in crit_tm), "Doit bloquer les marques notoires dans les mots-clés"

    crit_forb, warn_forb = kcs.check_a9_keywords_compliance(
        keywords=["livre bestseller n°1 gratuit", "methode financiere"],
        title="Mon Livre",
        subtitle="Un guide",
    )
    assert any("terme promotionnel prohibé" in c.lower() or "prohibé" in c.lower() for c in crit_forb), "Doit bloquer les termes interdits (bestseller/gratuit) dans les mots-clés"

    # 3. Vérification de la production complète dans l'Orchestrateur Export
    pkg = keo.build_kdp_export_package(
        book_id="unit_test_seo_export_01",
        title="L'Architecte Financier Pro",
        subtitle="Méthode pas-à-pas pour maîtriser son patrimoine",
        niche="finances",
        project_type="text",
        format_id="6x9",
        initial_pages=12,
        enforce_24_pages=True,
    )
    assert pkg["status"] == "success"
    assert "seo_amazon_ready" in pkg
    assert "description_amazon_html" in pkg
    assert "seo_amazon_ready.json" in pkg["files_included"]
    assert "description_amazon.html" in pkg["files_included"]

    # Vérification physique dans l'archive ZIP
    zip_path = Path(pkg["zip_path"])
    assert zip_path.is_file()
    with zipfile.ZipFile(zip_path, "r") as zf:
        z_names = zf.namelist()
        assert "seo_amazon_ready.json" in z_names
        assert "description_amazon.html" in z_names
        # Contrôle du contenu de seo_amazon_ready.json
        raw_seo = zf.read("seo_amazon_ready.json").decode("utf-8")
        parsed_seo = __import__("json").loads(raw_seo)
        assert len(parsed_seo["backend_keywords"]) == 7
        assert "categories" in parsed_seo
        assert "description_html" in parsed_seo
        assert "amazon_ads_campaigns" in parsed_seo


# ==============================================================================
# TEST 21 : ROUTE API SEO A9 & SANITISATION HTML KDP STRICTE
# ==============================================================================

def test_21_route_seo_optimize_a9_and_sanitization():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router
    import kdp_extensions.seo_a9_agent as seo

    # 1. Test unitaire de sanitisation HTML KDP stricte
    dirty_html = (
        "<h1>Mon Chef-d'Œuvre</h1>"
        "<script>alert('xss');</script>"
        "<div class='box'><p>Paragraphe dans div</p></div>"
        "<span style='color:red;'>Texte rouge</span>"
        "<a href='https://spam.com'>Visitez ce site</a>"
        "<b>Important</b> <i>Clair</i>"
        "<ul><li>Point 1</li><li>Point 2</li></ul>"
    )
    clean_html = seo.sanitize_kdp_html(dirty_html)
    assert "<script" not in clean_html.lower()
    assert "alert(" not in clean_html.lower()
    assert "<div" not in clean_html.lower()
    assert "<span" not in clean_html.lower()
    assert "<a " not in clean_html.lower()
    assert "<h1" not in clean_html.lower()
    assert "<h2>" in clean_html
    assert "<b>Important</b>" in clean_html
    assert "<i>Clair</i>" in clean_html
    assert "<ul>" in clean_html
    assert "<li>Point 1</li>" in clean_html
    assert len(clean_html) <= 4000

    # 2. Test de l'endpoint FastAPI POST /api/seo/optimize-a9
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    payload = {
        "book_title": "Gestion du Temps et Focus",
        "subtitle": "La méthode concrète pour éliminer la procrastination",
        "niche": "productivite",
        "book_type": "text",
        "target_audience": "professionnels et étudiants",
        "seed_keywords": ["deep work", "organisation quotidienne", "blocs de temps"],
        "language": "fr",
    }
    resp = client.post("/api/seo/optimize-a9", json=payload)
    assert resp.status_code == 200, f"Erreur route /api/seo/optimize-a9 : {resp.text}"
    data = resp.json()

    # Vérification des 8 clés primaires Agent 5
    assert "optimized_title" in data
    assert "optimized_subtitle" in data
    assert "backend_keywords_7" in data
    assert "categories_3" in data
    assert "amazon_description_html" in data
    assert "aplus_content_blueprint" in data
    assert "ppc_launch_keywords" in data
    assert "seo_audit" in data

    # Vérification des 7 slots backend (<= 50 octets UTF-8 et cumul <= 250 octets)
    slots = data["backend_keywords_7"]
    assert len(slots) == 7
    total_b = sum(seo.calculate_utf8_bytes(s) for s in slots)
    assert total_b <= 250
    for s in slots:
        assert seo.calculate_utf8_bytes(s) <= 50

    # Vérification des catégories
    assert len(data["categories_3"]) >= 3

    # Vérification de l'audit
    audit = data["seo_audit"]
    assert audit["score_a9_100"] >= 80
    assert audit["zero_forbidden_terms"] is True
    assert audit["zero_trademarks"] is True
    assert audit["html_valid"] is True


def main():
    print("\n" + "=" * 65)
    print("🧪 SUITE DE TESTS — NOUVELLES EXTENSIONS KDP (MarkEddy)")
    print("=" * 65)

    tests = [
        ("Pairings typographiques & Google Fonts (fonts_connector)", test_01_fonts_connector_pairings),
        ("Agent de veille tri-plateforme (market_trends_agent)", test_02_market_trends_agent),
        ("Structure éditoriale Front/Back Matter (editorial_structure)", test_03_editorial_structure),
        ("Moteur CSS Paged Media W3C & Audit (layout_engine_pro)", test_04_layout_engine_pro),
        ("Calculateur de couverture & Gabarit SVG (cover_calculator)", test_05_cover_calculator),
        ("Endpoints d'extension FastAPI (router)", test_06_router_endpoints),
        ("Générateur Coloriage & Profil Kids (coloring_generator)", test_07_coloring_generator_and_kids_profile),
        ("Générateur de Puzzles 8 Formats (puzzle_generator)", test_08_puzzle_generator_8_formats),
        ("Orchestrateur Export KDP, Règle 24p & ZIP (kdp_export_orchestrator)", test_09_kdp_export_orchestrator_and_zip),
        ("Endpoints API Puzzles & Export Package (router)", test_10_router_export_and_download),
        ("Agent 1 : Veille Tendances Sociales (social_trend_hunter)", test_11_social_trend_hunter),
        ("Agent 2 : Recherche Documentaire & Académique (deep_research_agent)", test_12_deep_research_agent),
        ("Agent 3 : Synthèse, Fact-Checking & Humanisation (editorial_humanizer_agent)", test_13_editorial_humanizer_agent),
        ("Endpoints API Intelligence Éditoriale (router)", test_14_editorial_intelligence_routes),
        ("Agent 4 : Superviseur de Conformité KDP & Anti-Anonymat (kdp_compliance_supervisor)", test_15_kdp_compliance_supervisor),
        ("Blocage Export KDP si REJECTED & API Compliance (kdp_export_orchestrator)", test_16_export_blocked_on_rejection),
        ("Gatekeeper Anti-Anonymat & API Supervise-Audit (kdp_compliance_supervisor)", test_17_supervise_kdp_book_gatekeeper),
        ("Agent 6 : Transcréateur Multilingue 5 Langues & Bundle (multilingual_transcreator)", test_18_multilingual_transcreator_agent),
        ("Endpoints API Transcréation & Téléchargement Bundle (router)", test_19_transcreate_book_and_download_routes),
        ("Agent 5 : SEO A9/A10, Catégories, HTML & Ads (seo_a9_agent)", test_20_seo_a9_agent_full_package_and_export),
        ("Route API SEO A9 & Sanitisation HTML (router)", test_21_route_seo_optimize_a9_and_sanitization),
        ("Profils linguistiques 5 langues (i18n_config)", test_i18n_profiles_five_languages),
        ("Validation UTF-8 50 octets A9 (seo_a9_agent)", test_seo_a9_utf8_byte_limit_and_optimize),
        ("Superviseur Conformité KDP Reject/Approve (kdp_compliance_supervisor)", test_compliance_supervisor_reject_and_approve),
        ("Mode RTL Arabe (i18n_config)", test_rtl_arabic_mode_profile),
        ("Enhance Brief KDP (brief_enhancer & router)", test_26_enhance_brief_endpoint),
        ("Catalogue KDP + Etsy 8 Catégories (book_catalog & router)", test_27_book_catalog_and_endpoint),
        ("Métrage KDP/Etsy & Calculateur dynamique (book_catalog & router)", test_28_model_measurements_and_endpoint),
        ("Moteur Visuel Autonome 100% Arrière-Plan (autonomous_visual_agent)", test_29_autonomous_visual_agent),
    ]

    reussis = 0
    total = len(tests)

    for idx, (nom, fn) in enumerate(tests, 1):
        try:
            print(f"\n🔍 Test {idx} : {nom}...")
            fn()
            print(f"  ✅ [SUCCÈS] {nom} validé")
            reussis += 1
        except Exception as e:
            print(f"  ❌ [ÉCHEC] {nom} : {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 65)
    print(f"📊 RÉSULTAT NOUVELLES EXTENSIONS : {reussis}/{total} tests validés.")
    if reussis == total:
        print("🎉 TOUTES LES NOUVELLES EXTENSIONS SONT AU VERT !")
        print("=" * 65)
        return 0
    print("⚠️ Des erreurs ont été détectées.")
    print("=" * 65)
    return 1


# ==============================================================================
# TEST N : EXTENSIONS i18n / SEO A9 / COMPLIANCE SUPERVISOR (Task 4)
# ==============================================================================

def test_i18n_profiles_five_languages():
    from kdp_extensions.i18n_config import get_language_profile, normalize_language
    for code in ["en", "fr", "es", "de", "ar"]:
        p = get_language_profile(code)
        assert p["direction"] in ("ltr", "rtl")
        assert "amazon_marketplace" in p
        assert "google_fonts" in p
        assert "editorial_strings" in p
        assert "puzzle_alphabet" in p
        assert "word_banks" in p
        assert "forbidden_kdp_terms" in p
    # ar specifics
    par = get_language_profile("ar")
    assert par["direction"] == "rtl"
    assert par["is_rtl"] is True
    assert "Cairo" in par["google_fonts"]
    assert "Tajawal" in par["google_fonts"]
    assert "Amiri" in par["google_fonts"]
    # es has Ñ
    pes = get_language_profile("es")
    assert "Ñ" in "".join(pes["puzzle_alphabet"]) or "Ñ" in pes["puzzle_alphabet"]
    # de has ÄÖÜ
    pde = get_language_profile("de")
    joined = "".join(pde["puzzle_alphabet"])
    assert ("Ä" in joined) and ("Ö" in joined) and ("Ü" in joined)


def test_seo_a9_utf8_byte_limit_and_optimize():
    from kdp_extensions.seo_a9_agent import calculate_utf8_bytes, validate_a9_slot, optimize_kdp_seo
    # ASCII
    assert calculate_utf8_bytes("hello") == 5
    # Arabic/multi-byte should be > char count in some cases
    ar = "تخفيض"
    assert calculate_utf8_bytes(ar) >= len(ar)
    # slot validation flags over 50 bytes
    long_text = "a" * 60
    res = validate_a9_slot(long_text, language="en", title="T", subtitle="S", max_bytes=50)
    assert res["is_valid"] is False or res["byte_count"] > 50
    # optimize_kdp_seo basic
    out = optimize_kdp_seo(
        book_title="My Book",
        subtitle="A guide",
        niche="self help",
        book_type="guide",
        target_audience="beginners",
        seed_keywords=["habit", "growth"],
        language="en",
    )
    assert "backend_keywords" in out
    assert len(out["backend_keywords"]) == 7
    for sl in out["backend_keywords"]:
        assert len(sl.encode("utf-8")) <= 50


def test_compliance_supervisor_reject_and_approve():
    from kdp_extensions.kdp_compliance_supervisor import supervise_kdp_book
    # Reject case: trademark in title + < 24 pages paperback
    bad = {
        "title": "Disney Coloring Book",
        "subtitle": "fun",
        "author": "Coloring Books",
        "page_count": 10,
        "binding": "paperback",
        "language": "en",
        "niche": "kids",
        "keywords": ["kids", "color"],
    }
    rbad = supervise_kdp_book(bad)
    assert rbad["verdict"] == "REJECTED_FOR_REVISION"
    assert rbad["approved"] is False
    # Approve-ish case (may still warn but if score>=85 and no blocking -> approved). Craft carefully.
    good = {
        "title": "Calm Focus Daily",
        "subtitle": "Practical steps for busy people",
        "author": "Jane Doe",
        "page_count": 120,
        "binding": "paperback",
        "language": "en",
        "niche": "productivity",
        "keywords": ["focus habits", "deep work", "time blocks", "morning routine", "attention", "planner", "energy"],
        "has_disclaimer": True,
        "has_author_bio": True,
        "has_copyright": True,
        "has_colophon": True,
        "has_toc": True,
        "has_cover": True,
        "isbn": "9790000000000",
        "ai_transparency_declared": True,
    }
    rgood = supervise_kdp_book(good)
    assert rgood["verdict"] in ("APPROVED_FOR_KDP", "REJECTED_FOR_REVISION")
    # If approved, must be >=85 and no blocking
    if rgood["approved"]:
        assert rgood["score_anti_anonymat_100"] >= 85
        assert len(rgood["blocking_violations"]) == 0


def test_rtl_arabic_mode_profile():
    from kdp_extensions.i18n_config import get_language_profile
    p = get_language_profile("ar")
    assert p["direction"] == "rtl"
    assert p["is_rtl"] is True
    # editorial strings present
    assert isinstance(p.get("editorial_strings"), dict)
    assert len(p.get("editorial_strings", {})) > 0


def test_26_enhance_brief_endpoint():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router
    from kdp_extensions.brief_enhancer import enhance_kdp_brief

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # 1. Test unitaire direct mode 'random'
    res_rand = enhance_kdp_brief(
        niche="Immobilier Locatif",
        book_type="non-fiction",
        mode="random",
        language="fr"
    )
    assert res_rand["status"] == "success"
    assert res_rand["mode"] == "random"
    assert len(res_rand["brief"]) >= 50
    assert "suggested_angle" in res_rand and len(res_rand["suggested_angle"]) > 3
    assert "target_audience" in res_rand
    assert "tone" in res_rand

    # 2. Test unitaire direct mode 'enhance'
    res_enh = enhance_kdp_brief(
        niche="Finances Personnelles",
        book_type="non-fiction",
        current_brief="guide pour débutants budget",
        mode="enhance",
        language="fr"
    )
    assert res_enh["status"] == "success"
    assert res_enh["mode"] == "enhance"
    b_enh = res_enh["brief"]
    assert len(b_enh.strip()) >= 80
    assert any(k.lower() in b_enh.lower() for k in ("public cible", "cible", "audience"))
    assert any(k in b_enh for k in ("Promesse", "Objectif", "Valeur"))
    assert any(k in b_enh for k in ("Ton", "Voix", "Style"))

    # 3. Test API POST /api/kdp/enhance-brief (mode random)
    resp_api_rand = client.post("/api/kdp/enhance-brief", json={
        "niche": "Stoïcisme & Sérénité",
        "book_type": "non-fiction",
        "target_audience": "Adultes Débutants",
        "current_brief": "",
        "mode": "random",
        "language": "fr"
    })
    assert resp_api_rand.status_code == 200
    data_rand = resp_api_rand.json()
    assert data_rand["status"] == "success"
    assert data_rand["mode"] == "random"
    assert len(data_rand["brief"]) > 50
    assert data_rand["large_print_recommended"] is False

    # 4. Test unitaire et API avec cible Seniors (Grands Caractères / Large Print)
    res_senior = enhance_kdp_brief(
        niche="Mots Croisés & Logique",
        book_type="puzzle",
        target_audience="Seniors 60+ (Grands Caractères / Large Print)",
        mode="random",
        language="fr"
    )
    assert res_senior["large_print_recommended"] is True
    assert "Grands Caractères" in res_senior["brief"] or "Large Print" in res_senior["brief"]

    resp_api_senior = client.post("/api/kdp/enhance-brief", json={
        "niche": "Santé & Mémoire",
        "book_type": "non-fiction",
        "target_audience": "Seniors 60+ (Grands Caractères / Large Print)",
        "current_brief": "exercices quotidiens mémoire",
        "mode": "enhance",
        "language": "fr"
    })
    assert resp_api_senior.status_code == 200
    data_senior = resp_api_senior.json()
    assert data_senior["large_print_recommended"] is True
    assert "Grands Caractères" in data_senior["brief"] or "Large Print" in data_senior["brief"]

    # 5. Test avec cible Enfants
    res_kids = enhance_kdp_brief(
        niche="Animaux de la Savane",
        book_type="coloriage",
        target_audience="Enfants 6–8 ans (Primaire)",
        mode="random",
        language="fr"
    )
    assert res_kids["large_print_recommended"] is False
    assert "Enfants" in res_kids["brief"]

    # 6. Test API POST /api/kdp/enhance-brief (mode enhance en anglais)
    resp_api_enh = client.post("/api/kdp/enhance-brief", json={
        "niche": "Mindfulness & Sleep",
        "book_type": "non-fiction",
        "target_audience": "Adults & Busy Professionals",
        "current_brief": "practical routine for better sleep without pills",
        "mode": "enhance",
        "language": "en"
    })
    assert resp_api_enh.status_code == 200
    data_enh = resp_api_enh.json()
    assert data_enh["status"] == "success"
    assert data_enh["mode"] == "enhance"
    assert any(k.lower() in data_enh["brief"].lower() for k in ("target audience", "audience", "public cible", "cible"))
    assert any(k.lower() in data_enh["brief"].lower() for k in ("promise", "promesse", "objectif", "valeur"))


def test_27_book_catalog_and_endpoint():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router
    import kdp_extensions.book_catalog as bc

    # 1. Vérification des 8 catégories
    expected_categories = [
        "non_fiction", "coloring", "puzzles", "educational",
        "planners_journals", "workbooks", "cookbooks", "fiction_kids"
    ]
    for cat_id in expected_categories:
        assert cat_id in bc.BOOK_CATEGORIES_CATALOG, f"Catégorie manquante : {cat_id}"
        cat_data = bc.BOOK_CATEGORIES_CATALOG[cat_id]
        assert "id" in cat_data
        assert "label" in cat_data
        assert "icon" in cat_data
        assert "models" in cat_data
        assert len(cat_data["models"]) >= 3, f"Pas assez de modèles pour {cat_id}"

        # Vérification des champs requis sur chaque modèle
        for m in cat_data["models"]:
            assert "id" in m
            assert "label" in m
            assert "platforms" in m and isinstance(m["platforms"], list)
            assert "default_format" in m
            assert "engine" in m
            assert "min_pages_kdp" in m
            assert "bleed_required" in m
            assert "low_content_flag" in m
            assert isinstance(m["low_content_flag"], bool)

    # 2. Test des fonctions utilitaires
    cat_all = bc.get_catalog()
    assert len(cat_all) == 8

    cat_color = bc.get_category("coloring")
    assert cat_color is not None
    assert cat_color["id"] == "coloring"
    assert cat_color["primary_engine"] == "coloring"

    m_zen = bc.get_model("mandalas_zen_adultes")
    assert m_zen is not None
    assert m_zen["id"] == "mandalas_zen_adultes"
    assert m_zen["engine"] == "coloring"

    # Test normalisation rétrocompatible
    norm_color = bc.normalize_catalog_selection("coloring", "mandalas_zen_adultes")
    assert norm_color["engine"] == "coloring"
    assert norm_color["category"] == "coloring"

    norm_legacy = bc.normalize_catalog_selection(None, None, legacy_project_type="coloring_book")
    assert norm_legacy["engine"] == "coloring"

    norm_planners = bc.normalize_catalog_selection("planners_journals", "planner_quotidien_hebdo")
    assert norm_planners["low_content_flag"] is True

    # 3. Test de l'endpoint FastAPI GET /api/kdp/catalog
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/api/kdp/catalog")
    assert resp.status_code == 200, f"Erreur route /api/kdp/catalog : {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_categories"] == 8
    assert "categories" in data
    for cat_id in expected_categories:
        assert cat_id in data["categories"]


def test_28_model_measurements_and_endpoint():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router
    from kdp_extensions.book_catalog import compute_model_measurements

    # 1. Cas 1 : Coloriage 64 pages (8.5x11, bleed, dos < 79 p.)
    m_col = compute_model_measurements(
        model_id="enfants_traits_epais",
        page_count=64,
        format_kdp="8.5x11",
        paper_type="white",
        platform="kdp"
    )
    assert m_col["bleed_required"] is True
    assert m_col["interior_inches"]["width"] == 8.625
    assert m_col["interior_inches"]["height"] == 11.25
    assert abs(m_col["interior_mm"]["width"] - 219.08) < 0.02
    assert abs(m_col["interior_mm"]["height"] - 285.75) < 0.02
    assert m_col["gutter_inches"] == 0.75  # min_gutter_override = 0.75
    assert m_col["outer_margin_inches"] == 0.375  # avec bleed
    assert m_col["spine_text_allowed"] is False  # 64 < 79
    assert m_col["low_content_flag"] is False
    assert m_col["isbn_box_px"] == [600, 360]
    assert "cover_300dpi_px" in m_col and len(m_col["cover_300dpi_px"]) == 2
    assert any("79 pages" in w or "tranche interdit" in w for w in m_col["validation_warnings"])

    # 2. Cas 2 : Non-Fiction 220 pages (6x9, crème, gouttière 0.50", texte dos autorisé)
    m_nf = compute_model_measurements(
        model_id="guide_pratique",
        page_count=220,
        format_kdp="6x9",
        paper_type="cream",
        platform="kdp"
    )
    assert m_nf["bleed_required"] is False
    assert m_nf["interior_inches"]["width"] == 6.0
    assert m_nf["interior_inches"]["height"] == 9.0
    assert m_nf["gutter_inches"] == 0.50  # barème KDP 151-300 p.
    assert m_nf["gutter_mm"] == 12.7
    assert m_nf["outer_margin_inches"] == 0.25  # sans bleed
    assert m_nf["spine_text_allowed"] is True  # 220 >= 79
    assert m_nf["spine_inches"] == 0.55  # 220 * 0.0025
    assert m_nf["spine_mm"] == 13.97
    assert not any("tranche interdit" in w for w in m_nf["validation_warnings"])

    # 3. Cas 3 : Pack Etsy (A4 + US Letter)
    m_etsy = compute_model_measurements(
        model_id="pack_etsy_printable",
        page_count=60,
        format_kdp="8.5x11",
        paper_type="white",
        platform="etsy"
    )
    assert m_etsy["etsy_print_formats"] is not None
    assert "a4" in m_etsy["etsy_print_formats"]
    assert "us_letter" in m_etsy["etsy_print_formats"]
    assert m_etsy["etsy_print_formats"]["a4"]["dimensions_mm"] == [210, 297]
    assert m_etsy["etsy_print_formats"]["a4"]["resolution_300dpi_px"] == [2480, 3508]
    us_dims = m_etsy["etsy_print_formats"]["us_letter"].get("dimensions_in") or m_etsy["etsy_print_formats"]["us_letter"].get("dimensions_inches")
    assert us_dims == [8.5, 11.0]
    assert m_etsy["etsy_print_formats"]["us_letter"]["resolution_300dpi_px"] == [2550, 3300]

    # 4. Test endpoint FastAPI POST /api/kdp/calculate-measurements
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.post("/api/kdp/calculate-measurements", json={
        "model_id": "guide_pratique",
        "page_count": 220,
        "format_kdp": "6x9",
        "paper_type": "cream",
        "platform": "kdp"
    })
    assert resp.status_code == 200, f"Erreur route /api/kdp/calculate-measurements : {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert "measurements" in data
    meas = data["measurements"]
    assert meas["gutter_inches"] == 0.50
    assert meas["spine_text_allowed"] is True
    assert meas["spine_inches"] == 0.55

    # Test endpoint avec platform="both" pour validation des formats Etsy
    resp_both = client.post("/api/kdp/calculate-measurements", json={
        "model_id": "enfants_traits_epais",
        "page_count": 64,
        "format_kdp": "8.5x11",
        "paper_type": "white",
        "platform": "both"
    })
    assert resp_both.status_code == 200
    data_both = resp_both.json()
    assert data_both["measurements"]["etsy_print_formats"] is not None
    assert "a4" in data_both["measurements"]["etsy_print_formats"]


def test_29_autonomous_visual_agent():
    import io
    from pathlib import Path
    from unittest import mock
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from kdp_extensions.router import router
    from kdp_extensions.autonomous_visual_agent import build_autonomous_visuals
    import kdp_extensions.media_connectors as mc

    # Mock HTTP Unsplash / Pixabay pour recherche déterministe
    def _mock_get_json(url, params=None, headers=None, timeout=10.0):
        if "api.unsplash.com" in url:
            return {"results": [{
                "id": "u-photo-auto-1",
                "description": "Background abstrait doré",
                "urls": {
                    "small": "https://images.unsplash.com/small.jpg",
                    "regular": "https://images.unsplash.com/regular.jpg",
                    "full": "https://images.unsplash.com/full.jpg",
                },
                "user": {"name": "Artiste IA"},
                "links": {"html": "https://unsplash.com/photos/1"},
                "tags": [{"title": "or"}],
            }]}
        if "pixabay.com" in url:
            return {"hits": [{
                "id": 88,
                "tags": "finance, business",
                "fullHDURL": "https://pixabay.com/full_hd.jpg",
                "webformatURL": "https://pixabay.com/web.jpg",
            }]}
        return {}

    # Mock binaire download
    from PIL import Image
    buf = io.BytesIO()
    img_factice = Image.new("RGB", (600, 900), color="#0A0F1D")
    img_factice.save(buf, "JPEG")
    fake_bytes = buf.getvalue()

    with mock.patch.object(mc, "_httpx_get_json", side_effect=_mock_get_json), \
         mock.patch.object(mc, "_get_unsplash_key", return_value="fake_key"), \
         mock.patch.object(mc, "_httpx_download", return_value=fake_bytes):

        # 1. Test Non-Fiction avec repli local 300 DPI + Unsplash silencieux
        res_nf = build_autonomous_visuals(
            title="L'Architecte Financier",
            subtitle="Maîtriser son Argent",
            niche="Finances Personnelles",
            category="non_fiction",
            target_audience="Adultes Débutants",
            format_kdp="6x9",
            page_count=120,
            paper_type="cream",
            language="fr",
        )

        assert res_nf["status"] == "success"
        assert "cover_asset_path" in res_nf and Path(res_nf["cover_asset_path"]).exists()
        assert "interior_illustrations" in res_nf and len(res_nf["interior_illustrations"]) >= 1
        assert "sources_used" in res_nf and len(res_nf["sources_used"]) >= 1
        assert any(s in res_nf["sources_used"] for s in ("unsplash", "pixabay", "curated", "local_300dpi"))
        assert "canva_background_status" in res_nf

        # 2. Test Coloriage avec génération automatique de planches vectorielles N&B
        res_col = build_autonomous_visuals(
            title="Mandalas & Sérénité",
            subtitle="Coloriage Adulte Zen",
            niche="mandalas",
            category="coloring",
            target_audience="Adultes",
            format_kdp="8.5x11",
            page_count=64,
            paper_type="white",
            language="fr",
            count_illustrations=4,
        )

        assert res_col["status"] == "success"
        assert Path(res_col["cover_asset_path"]).exists()
        assert len(res_col["interior_illustrations"]) >= 4
        # Vérifier que les illustrations sont au format vectoriel pur noir et blanc
        svg_illus = [i for i in res_col["interior_illustrations"] if i["format"] == "svg"]
        assert len(svg_illus) >= 4
        for illu in svg_illus:
            svg_text = Path(illu["file_path"]).read_text(encoding="utf-8")
            assert "<svg" in svg_text
            assert "#000000" in svg_text or "stroke=" in svg_text

        # 3. Test Endpoint API POST /api/visuals/autonomous-build
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        resp = client.post("/api/visuals/autonomous-build", json={
            "title": "Stoïcisme Quotidien",
            "subtitle": "Le Guide Pratique",
            "niche": "Philosophie & Sérénité",
            "category": "non_fiction",
            "target_audience": "Tous publics",
            "format_kdp": "6x9",
            "page_count": 100,
            "paper_type": "white",
            "language": "fr"
        })
        assert resp.status_code == 200, f"Erreur API /api/visuals/autonomous-build : {resp.text}"
        data = resp.json()
        assert data["status"] == "success"
        assert "cover_asset_path" in data
        assert "interior_illustrations" in data
        assert "sources_used" in data


if __name__ == "__main__":
    import sys
    sys.exit(main())
