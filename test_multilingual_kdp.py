"""
test_multilingual_kdp.py — Banc d'essai automatisé d'extension multilingue (5 langues KDP).
Couvre : i18n_config, fonts_connector, layout_engine_pro, editorial_structure,
puzzle_generator, seo_a9_agent, kdp_compliance_supervisor, router.
"""

import pytest
from fastapi.testclient import TestClient

from kdp_extensions.i18n_config import (
    SUPPORTED_LANGUAGES,
    get_alphabet,
    get_editorial_labels,
    get_forbidden_keywords,
    get_language_config,
    get_paperback_warning,
    get_puzzle_word_banks,
    get_supported_languages,
    is_rtl,
    normalize_language,
)
from kdp_extensions.fonts_connector import (
    EDITORIAL_FONT_PAIRINGS,
    recommend_font_pairing_for_language,
)
from kdp_extensions.layout_engine_pro import (
    audit_paged_css_compliance,
    compile_paged_interior_html,
    generate_paged_media_css,
)
from kdp_extensions.editorial_structure import (
    assemble_complete_book,
    generate_back_matter_html,
    generate_front_matter_html,
)
from kdp_extensions.puzzle_generator import (
    generate_word_search,
    generate_full_puzzle_collection,
)
from kdp_extensions.seo_a9_agent import (
    audit_7_slots_a9,
    calculate_utf8_bytes,
    optimize_7_slots_a9,
    validate_a9_slot,
)
from kdp_extensions.kdp_compliance_supervisor import (
    audit_font_script_compatibility,
    audit_hyphenation_rules,
    audit_multilingual_kdp_project,
    audit_rtl_gutter_compliance,
    audit_utf8_integrity,
)
from kdp_extensions.router import router


# -----------------------------------------------------------------------------
# 1. Tests Registre i18n_config
# -----------------------------------------------------------------------------

def test_i18n_config_supported_languages():
    raw_langs = get_supported_languages()
    codes = [item["code"] if isinstance(item, dict) else item for item in raw_langs]
    assert set(codes) == {"fr", "en", "es", "de", "ar"}
    assert normalize_language("FR") == "fr"
    assert normalize_language("french") == "fr"
    assert normalize_language("arabic") == "ar"
    assert normalize_language("spanish") == "es"
    assert normalize_language("german") == "de"
    assert normalize_language("unknown") == "fr"  # Repli sécurisé


def test_i18n_config_details_and_rtl():
    for code in ["fr", "en", "es", "de"]:
        cfg = get_language_config(code)
        assert cfg["is_rtl"] is False
        assert is_rtl(code) is False
        assert len(get_alphabet(code)) >= 26
        assert len(get_forbidden_keywords(code)) >= 5

    ar_cfg = get_language_config("ar")
    assert ar_cfg["is_rtl"] is True
    assert is_rtl("ar") is True
    assert ar_cfg["paperback_warning"] is not None
    assert get_paperback_warning("ar") is not None
    assert get_paperback_warning("fr") is None


def test_i18n_config_editorial_labels():
    for code in ["fr", "en", "es", "de", "ar"]:
        labels = get_editorial_labels(code)
        assert "half_title" in labels
        assert "title_page" in labels
        assert "copyright_notice" in labels
        assert "legal_deposit" in labels
        assert "toc_title" in labels
        assert "colophon" in labels


# -----------------------------------------------------------------------------
# 2. Tests fonts_connector Multilingue
# -----------------------------------------------------------------------------

def test_fonts_connector_multilingual_pairings():
    # Arabe : pairing dédié avec Amiri / Cairo
    p_ar = recommend_font_pairing_for_language("ar")
    assert p_ar["id"] == "arabic_majestic"
    assert "Amiri" in p_ar["body_font"]
    assert "Cairo" in p_ar["title_font"]

    # Allemand : germanic_precision
    p_de = recommend_font_pairing_for_language("de")
    assert p_de["id"] == "germanic_precision"

    # Espagnol : spanish_modern
    p_es = recommend_font_pairing_for_language("es")
    assert p_es["id"] == "spanish_modern"

    # Français & Anglais
    p_fr = recommend_font_pairing_for_language("fr")
    assert p_fr is not None and "title_font" in p_fr
    p_en = recommend_font_pairing_for_language("en")
    assert p_en is not None and "title_font" in p_en


# -----------------------------------------------------------------------------
# 3. Tests layout_engine_pro : Inversion RTL & Césures
# -----------------------------------------------------------------------------

def test_layout_engine_rtl_gutter_inversion():
    css_ar = generate_paged_media_css(format_id="6x9", language="ar", page_count=150)
    assert "direction: rtl" in css_ar
    assert "hyphens: none !important" in css_ar
    # En RTL : la gouttière (0.85in) doit être à droite sur :right et à gauche sur :left
    assert "margin-right: 0.85in" in css_ar
    assert "margin-left: 0.85in" in css_ar

    css_fr = generate_paged_media_css(format_id="6x9", language="fr", page_count=150)
    assert "direction: ltr" in css_fr
    assert "hyphens: auto" in css_fr

    # Compilation HTML complète avec attributs lang et dir
    html_ar = compile_paged_interior_html(
        content="<p>محتوى تجريبي</p>",
        metadata={"title": "كتاب تجريبي", "author": "مؤلف"},
        language="ar"
    )
    assert 'lang="ar"' in html_ar
    assert 'dir="rtl"' in html_ar

    # Audit CSS
    audit_ar = audit_paged_css_compliance(html_ar)
    assert audit_ar["conforme_kdp"] is True
    assert audit_ar["score_conformite"] >= 80


# -----------------------------------------------------------------------------
# 4. Tests editorial_structure Multilingue
# -----------------------------------------------------------------------------

def test_editorial_structure_multilingual():
    meta = {
        "title": "EL ARTE DE LAS FINANZAS",
        "subtitle": "Guía Práctica",
        "author": "MarkEddy",
        "publisher": "Ediciones MarkEddy",
        "year": 2026,
    }
    fm_es = generate_front_matter_html(meta, language="es")
    assert "EL ARTE DE LAS FINANZAS" in fm_es
    assert "Todos los derechos reservados" in fm_es or "derechos reservados" in fm_es.lower()

    bm_ar = generate_back_matter_html({"title": "كتاب", "author": "كاتب"}, language="ar")
    assert 'dir="rtl"' in bm_ar
    assert "خاتمة" in bm_ar or "تقييم" in bm_ar

    # Assemblage complet
    book_de = assemble_complete_book("<p>Inhalt</p>", {"title": "BUCH", "language": "de"}, output_format="html")
    assert "Schmutztitel" in book_de or "BUCH" in book_de


# -----------------------------------------------------------------------------
# 5. Tests puzzle_generator Multilingue
# -----------------------------------------------------------------------------

def test_puzzle_generator_multilingual():
    # Mots mêlés en Allemand
    ws_de = generate_word_search(theme="animaux", language="de", seed=42)
    assert ws_de["type"] == "word_search"
    assert len(ws_de["words"]) > 0

    # Mots mêlés en Arabe
    ws_ar = generate_word_search(theme="espace", language="ar", seed=42)
    assert ws_ar["type"] == "word_search"
    assert ws_ar["is_rtl"] is True
    assert len(ws_ar["words"]) > 0

    # Collection complète
    coll_es = generate_full_puzzle_collection(
        book_title="Libro de Pasatiempos",
        theme="general",
        puzzles_per_type=1,
        language="es"
    )
    assert coll_es["status"] == "success"
    assert "lang='es'" in coll_es["html"]


# -----------------------------------------------------------------------------
# 6. Tests seo_a9_agent : 50 octets UTF-8 & Mots Interdits
# -----------------------------------------------------------------------------

def test_seo_a9_utf8_byte_calculation():
    assert calculate_utf8_bytes("finances") == 8
    # En français : "indépendance" (12 caractères, 'é' prend 2 octets en UTF-8 -> 13 octets)
    assert calculate_utf8_bytes("indépendance") == 13
    # En arabe : chaque lettre = 2 octets
    assert calculate_utf8_bytes("كتاب") == 8  # 4 lettres * 2 = 8 octets

    # Slot valide <= 50 octets
    v_ok = validate_a9_slot("methode budget enveloppes 50 30 20", language="fr")
    assert v_ok["is_valid"] is True
    assert v_ok["byte_count"] <= 50

    # Slot dépassant 50 octets
    long_slot = "un texte extremement long concu specifiquement pour depasser la limite stricte de cinquante octets imposee par l algorithme amazon kdp"
    v_fail = validate_a9_slot(long_slot, language="fr")
    assert v_fail["is_valid"] is False
    assert any("Dépassement" in e for e in v_fail["errors"])

    # Mot interdit détecté
    v_forb = validate_a9_slot("le meilleur livre pour investir", language="fr")
    assert v_forb["is_valid"] is False
    assert any("meilleur" in e for e in v_forb["errors"])


def test_seo_a9_audit_and_optimize():
    res_opt = optimize_7_slots_a9(
        title="L'Architecte Financier",
        subtitle="Le Système Automatisé",
        niche="Finances",
        language="fr"
    )
    assert res_opt["status"] == "success"
    assert len(res_opt["optimized_slots"]) == 7
    audit = res_opt["audit"]
    assert audit["is_conforme"] is True
    assert audit["score_a9"] >= 80
    assert audit["total_bytes"] <= 250


# -----------------------------------------------------------------------------
# 7. Tests kdp_compliance_supervisor
# -----------------------------------------------------------------------------

def test_compliance_supervisor_checks():
    # UTF-8
    u_ok = audit_utf8_integrity("Texte propre avec accents éàç.")
    assert u_ok["valid"] is True
    u_bad = audit_utf8_integrity("Texte avec mojibake Ã© et TODO restant.")
    assert u_bad["valid"] is False

    # Font Arabe
    f_ok = audit_font_script_compatibility("font-family: 'Amiri', serif;", language="ar")
    assert f_ok["is_compatible"] is True
    f_bad = audit_font_script_compatibility("font-family: 'Garamond', serif;", language="ar")
    assert f_bad["is_compatible"] is False

    # Rapport complet avec alerte Arabe
    rep_ar = audit_multilingual_kdp_project(
        html_content="<style>@page :left { margin-left: 0.85in; } @page :right { margin-right: 0.85in; } body { font-family: 'Amiri'; hyphens: none !important; }</style>",
        metadata={"title": "كتاب"},
        language="ar",
        cover_type="paperback"
    )
    assert rep_ar["status"] == "success"
    assert rep_ar["paperback_warning"] is not None
    assert "Kindle eBook" in rep_ar["recommendations"][0]


# -----------------------------------------------------------------------------
# 8. Tests Routes API Router Multilingues
# -----------------------------------------------------------------------------

def test_router_i18n_endpoints():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # 1. GET /api/i18n/languages
    r_langs = client.get("/api/i18n/languages")
    assert r_langs.status_code == 200
    data_langs = r_langs.json()
    raw_codes = data_langs["supported_codes"]
    codes = [c["code"] if isinstance(c, dict) else c for c in raw_codes]
    assert set(codes) == {"fr", "en", "es", "de", "ar"}

    # 2. GET /api/i18n/language/ar
    r_ar = client.get("/api/i18n/language/ar")
    assert r_ar.status_code == 200
    assert r_ar.json()["language"]["is_rtl"] is True

    # 3. POST /api/seo/audit-keywords
    r_audit = client.post("/api/seo/audit-keywords", json={
        "slots": [
            "sortir du decouvert bancaire",
            "methode enveloppes virtuelles",
            "investir en bourse petit budget",
            "epargne de precaution matelas",
            "jeune actif debutant finances",
            "rembourser credit consommation",
            "independance financiere liberte"
        ],
        "language": "fr",
        "title": "Guide du Budget"
    })
    assert r_audit.status_code == 200
    assert r_audit.json()["is_conforme"] is True

    # 4. POST /api/seo/optimize-keywords
    r_opt = client.post("/api/seo/optimize-keywords", json={
        "title": "Mastering Personal Finance",
        "subtitle": "Step by step system",
        "niche": "Finance",
        "language": "en"
    })
    assert r_opt.status_code == 200
    assert len(r_opt.json()["optimized_slots"]) == 7

    # 5. POST /api/compliance/audit-multilingual
    r_comp = client.post("/api/compliance/audit-multilingual", json={
        "html_content": "<style>@page { size: 6in 9in; } @page :left { margin-right: 0.85in; } @page :right { margin-left: 0.85in; } body { hyphens: auto; }</style>",
        "metadata": {"title": "Test Book"},
        "language": "fr"
    })
    assert r_comp.status_code == 200
    assert r_comp.json()["status"] == "success"


def main() -> int:
    print("\n" + "=" * 65)
    print("🧪 SUITE DE TESTS — EXTENSION MULTILINGUE KDP (5 LANGUES)")
    print("=" * 65)

    tests = [
        ("Codes et normalisation des 5 langues (i18n_config)", test_i18n_config_supported_languages),
        ("Marchés, alphabets, mots interdits & RTL (i18n_config)", test_i18n_config_details_and_rtl),
        ("Front/Back Matter labels localisés (i18n_config)", test_i18n_config_editorial_labels),
        ("Recommandation & pairing polices par langue (fonts_connector)", test_fonts_connector_multilingual_pairings),
        ("Inversion reliure RTL Arabe & Césures (layout_engine_pro)", test_layout_engine_rtl_gutter_inversion),
        ("Front/Back Matter multilingue (editorial_structure)", test_editorial_structure_multilingual),
        ("Jeux & Puzzles multilingues (puzzle_generator)", test_puzzle_generator_multilingual),
        ("Calcul octets UTF-8 & Mots interdits A9 (seo_a9_agent)", test_seo_a9_utf8_byte_calculation),
        ("Audit & Optimisation 7 slots A9 (seo_a9_agent)", test_seo_a9_audit_and_optimize),
        ("Audit UTF-8, script & alerte Arabe (kdp_compliance_supervisor)", test_compliance_supervisor_checks),
        ("Endpoints API Multilingues FastAPI (router)", test_router_i18n_endpoints),
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
    print(f"📊 RÉSULTAT EXTENSION MULTILINGUE : {reussis}/{total} tests validés.")
    if reussis == total:
        print("🎉 TOUS LES TESTS MULTILINGUES KDP SONT AU VERT !")
        print("=" * 65)
        return 0
    print("⚠️ Des erreurs ont été détectées.")
    print("=" * 65)
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
