"""
test_media_and_coloring.py - Suite de Tests Automatisée : Connecteurs Médias & Moteur Coloriage KDP.
Valide :
1. Connecteurs Pexels, Unsplash & Curated Stock (recherche, prépresse 300 DPI).
2. Connecteur Canva (Gabarits KDP 300 DPI, repères fond perdu & zone ISBN).
3. Moteur de Livre de Coloriage KDP 8.5" x 11" (SVG, Line-Art, anti-bavure, PDF 300 DPI, dos calculé).
4. Routes API FastAPI (/api/media/search, /api/canva/auth-url, /api/canva/template, /api/books/create mode coloriage).
"""

import os
import sys
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from fastapi import BackgroundTasks

import media_connectors
import coloring_book_engine
import app_studio
import studio_db
import auth


def test_media_connectors_stock_search():
    """Vérifie la recherche d'images stock (Pexels / Unsplash / Curated)."""
    resultats = media_connectors.search_stock_images(query="mandala", source="all", per_page=6)
    assert len(resultats) > 0, "La recherche d'images stock doit retourner au moins un résultat"
    premier = resultats[0]
    assert "thumb_url" in premier, "Chaque image doit avoir une URL miniature"
    assert "regular_url" in premier or "hd_url" in premier, "Chaque image doit avoir une URL HD"
    assert "photographer" in premier, "Chaque image doit créditer l'auteur/photographe"

    res_finance = media_connectors.search_stock_images(query="finance", source="all", per_page=4)
    assert any("finance" in img.get("tags", []) or "finance" in img.get("title", "").lower() for img in res_finance)


def test_canva_template_generation():
    """Vérifie la génération d'un gabarit de couverture KDP 300 DPI prêt pour Canva."""
    template_path = media_connectors.generate_canva_cover_template(
        book_id=777,
        format_kdp="8.5x11",
        nb_pages=60,
        titre="TEST COUVERTURE CANVA",
        author="MarkEddy"
    )
    assert template_path.exists(), "Le gabarit Canva PNG doit exister sur disque"
    
    from PIL import Image
    with Image.open(template_path) as img:
        assert img.size[1] == 3375, f"La hauteur doit être exactement 3375 px (11.25 po à 300 DPI), obtenu {img.size[1]}"
        assert img.size[0] > 5000, f"La largeur totale doit dépasser 5000 px, obtenu {img.size[0]}"


def test_coloring_book_engine_planches_svg():
    """Vérifie la conformité des générateurs vectoriels SVG noir et blanc pur."""
    svg_mandala = coloring_book_engine.generer_svg_mandala(index=1)
    assert "<svg" in svg_mandala and "</svg>" in svg_mandala
    assert 'stroke="#000000"' in svg_mandala
    assert 'fill="#FFFFFF"' in svg_mandala

    svg_botanique = coloring_book_engine.generer_svg_botanique(index=1)
    assert "<svg" in svg_botanique and "path" in svg_botanique

    svg_animal = coloring_book_engine.generer_svg_animal_mystique(index=1)
    assert "<svg" in svg_animal and "circle" in svg_animal

    svg_zen = coloring_book_engine.generer_svg_zen_architecture(index=1)
    assert "<svg" in svg_zen and ("polygon" in svg_zen or "rect" in svg_zen)


def test_coloring_book_engine_production_complete():
    """Vérifie la création complète d'un livre de coloriage 8.5x11 à 300 DPI."""
    book_id = 991
    res = coloring_book_engine.produire_livre_coloriage(
        book_id=book_id,
        titre="MANDALAS D'OR & ÉVEIL",
        sous_titre="40 chefs-d'œuvre géométriques pour calmer le mental",
        theme="mandalas",
        nb_illustrations=4,
        recto_uniquement=True
    )

    assert res["status"] == "success"
    assert res["nb_illustrations"] == 4
    assert res["nb_pages"] >= 12
    assert res["epaisseur_dos_po"] > 0

    pdf_int = Path(res["chemin_pdf_interieur"])
    assert pdf_int.exists() and pdf_int.stat().st_size > 50000, "Le PDF intérieur doit être généré et non vide"

    from pypdf import PdfReader
    reader = PdfReader(str(pdf_int))
    assert len(reader.pages) == res["nb_pages"]

    dossier_test = Path("books") / f"livre_coloriage_{book_id}"
    if dossier_test.exists():
        shutil.rmtree(dossier_test, ignore_errors=True)


def test_api_media_and_canva_routes():
    """Vérifie les endpoints FastAPI pour les médias et Canva Connect."""
    email = "test_media_user@markeddy.com"
    user = studio_db.obtenir_utilisateur_par_email(email)
    if not user:
        pwd_hash = auth.hacher_mot_de_passe("Secret123!")
        u_id = studio_db.creer_utilisateur(email, pwd_hash, credits=5)
        user = studio_db.obtenir_utilisateur_par_id(u_id)

    # 1. GET /api/media/search
    res_search = app_studio.api_media_search(query="mandala", source="all", per_page=4, current_user=user)
    body_search = json.loads(res_search.body.decode("utf-8"))
    assert body_search["status"] == "success"
    assert len(body_search["images"]) > 0

    # 2. GET /api/canva/auth-url
    dummy_req = MagicMock()
    dummy_req.base_url = "http://127.0.0.1:8000"
    res_canva = app_studio.api_canva_auth_url(request=dummy_req, current_user=user)
    body_canva = json.loads(res_canva.body.decode("utf-8"))
    assert body_canva["status"] == "success"
    assert "canva.com" in body_canva["auth_url"]

    # 3. GET /api/canva/template/{book_id}
    res_tmpl = app_studio.api_canva_template(book_id=1, current_user=user)
    assert res_tmpl.media_type == "image/png"
    assert Path(res_tmpl.path).exists()


def test_api_create_coloring_book_order():
    """Vérifie le déclenchement de la création d'un livre de coloriage via l'API."""
    email = "test_coloriage_order@markeddy.com"
    user = studio_db.obtenir_utilisateur_par_email(email)
    if not user:
        pwd_hash = auth.hacher_mot_de_passe("Secret123!")
        u_id = studio_db.creer_utilisateur(email, pwd_hash, credits=5)
        user = studio_db.obtenir_utilisateur_par_id(u_id)

    payload = app_studio.CreateBookRequest(
        type_projet="coloriage",
        theme_coloriage="botanique",
        nb_illustrations=5,
        recto_uniquement=True,
        titre="JARDINS BOTANIQUES DE SÉRÉNITÉ",
        sous_titre="Planches florales grand format 8.5x11",
        format_kdp="8.5x11"
    )

    dummy_bg = MagicMock(spec=BackgroundTasks)
    res_post = app_studio.api_creer_livre(req=payload, bg_tasks=dummy_bg, current_user=user)
    body_post = json.loads(res_post.body.decode("utf-8"))
    assert body_post["status"] == "success"
    assert "book_id" in body_post
    b_id = body_post["book_id"]

    # Vérification en base de données
    livre = studio_db.obtenir_livre(b_id, user_id=user["id"])
    assert livre is not None
    assert livre["type_projet"] == "coloriage"
    assert livre["theme_coloriage"] == "botanique"
    assert livre["format_kdp"] == "8.5x11"

    # Vérification que la tâche de fond a bien été enregistrée
    assert dummy_bg.add_task.called

    # Nettoyage
    studio_db.supprimer_livre(b_id, user_id=user["id"])


def main():
    print("\n" + "=" * 65)
    print("🧪 SUITE DE TESTS AUTOMATISÉE : CONNECTEURS MÉDIAS & LIVRE COLORIAGE")
    print("=" * 65)

    tests = [
        ("Recherche d'images Stock (Pexels, Unsplash, Curated)", test_media_connectors_stock_search),
        ("Génération de gabarit KDP 300 DPI pour Canva", test_canva_template_generation),
        ("Générateurs vectoriels SVG (Mandalas, Botanique, Animaux, Zen)", test_coloring_book_engine_planches_svg),
        ("Production complète d'un livre de coloriage 8.5x11 à 300 DPI", test_coloring_book_engine_production_complete),
        ("Endpoints API /api/media/search, /api/canva/auth-url, /api/canva/template", test_api_media_and_canva_routes),
        ("Création d'un livre de coloriage via POST /api/books/create", test_api_create_coloring_book_order)
    ]

    reussis = 0
    for nom, func in tests:
        print(f"\n🔍 Exécution : {nom}...")
        try:
            func()
            print(f"  ✅ [SUCCÈS] {nom}")
            reussis += 1
        except Exception as e:
            print(f"  ❌ [ÉCHEC] {nom} : {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 65)
    print(f"📊 RÉSULTAT : {reussis}/{len(tests)} tests validés.")
    print("=" * 65 + "\n")
    if reussis == len(tests):
        print("🎉 TOUS LES TESTS MÉDIAS & COLORIAGE SONT AU VERT !")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
