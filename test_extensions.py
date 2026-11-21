"""
test_extensions.py - Suite de tests automatisés des extensions `kdp_extensions/` :
  * Référentiel des 16 formats KDP officiels + calculate_kdp_specs() (300 DPI)
  * Connecteurs Unsplash / Pixabay / Canva Connect API
  * Moteur de livres de coloriage (SVG noir pur, verso anti-bavure, PDF)

Exécution obligatoire (Windows 11, virtualenv du projet) :
    .\\.venv\\Scripts\\python.exe -m pytest test_suite.py test_extensions.py

Aucun appel réseau réel : les accès HTTP (Unsplash, Pixabay), l'API Canva et le
moteur de coloriage (Playwright / cover_artisan_agent) sont MOCKÉS.
"""

import inspect
import io
import json
import re
import shutil
from pathlib import Path
from unittest import mock

from PIL import Image, ImageDraw

# Compteurs de tests (mêmes conventions que test_suite.py)
tests_reussis = 0
tests_total = 0

BOOK_TEST_ID = 987654
DOSSIER_TEST_COLO = Path("books") / f"livre_coloriage_{BOOK_TEST_ID}"


def afficher_succes(message: str):
    global tests_reussis, tests_total
    tests_reussis += 1
    tests_total += 1
    print(f"  ✅ [SUCCÈS] {message}")


def afficher_erreur(message: str):
    global tests_total
    tests_total += 1
    print(f"  ❌ [ÉCHEC] {message}")


# ==============================================================================
# 1. RÉFÉRENTIEL DES 16 FORMATS KDP
# ==============================================================================

def test_1_formats_kdp_16():
    print("\n🔍 Test 1 : Référentiel des 16 formats KDP officiels...")
    from kdp_extensions.kdp_dimensions import (
        KDP_FORMAT_IDS, KDP_FORMATS, list_kdp_formats, normalize_format,
    )

    attendus = {
        "5x8", "5.06x7.81", "5.25x8", "5.5x8.5", "6x9", "6.14x9.21",
        "6.69x9.61", "7x10", "7.44x9.69", "7.5x9.25", "8.25x6",
        "8.25x8.25", "8.5x8.5", "8x10", "8.5x11", "8.27x11.69",
    }
    assert len(KDP_FORMAT_IDS) == 16, f"16 formats attendus, {len(KDP_FORMAT_IDS)} trouvés"
    assert set(KDP_FORMAT_IDS) == attendus, f"IDs incorrects : {set(KDP_FORMAT_IDS) ^ attendus}"
    assert len(KDP_FORMATS) == 16

    liste = list_kdp_formats()
    assert len(liste) == 16 and all("label" in f and "width_in" in f for f in liste)

    # Normalisation des alias (tolérance '6.0x9.0', '8.5×11', espaces)
    assert normalize_format("6.0x9.0") == "6x9"
    assert normalize_format("8.5×11") == "8.5x11"
    assert normalize_format("  6x9  ") == "6x9"
    try:
        normalize_format("12x12")
        raise AssertionError("Un format invalide aurait dû lever ValueError")
    except ValueError:
        pass

    afficher_succes("16 formats KDP, labels, alias et ValueError validés")


def test_2_calculate_kdp_specs():
    print("\n🔍 Test 2 : calculate_kdp_specs() — dos, gutter, 300 DPI, ISBN...")
    from kdp_extensions.kdp_dimensions import (
        BLEED_IN, ISBN_ZONE_PX, PAPER_SPINE_COEFFS, calculate_kdp_specs,
    )

    assert BLEED_IN == 0.125
    assert ISBN_ZONE_PX == (600, 360)
    assert PAPER_SPINE_COEFFS["white"] == 0.002252

    s = calculate_kdp_specs("6x9", page_count=100, paper_type="white", bleed=True)
    assert s["spine"]["width_in"] == round(100 * 0.002252, 6)
    assert s["interior"]["width_px"] == 1875 and s["interior"]["height_px"] == 2775
    # Couverture = (2 x trim) + dos + 2 x bleed -> 12 + 0.2252 + 0.25 = 12.4752 po
    assert s["cover"]["width_in"] == 12.4752
    assert s["cover"]["width_px"] == int(round(12.4752 * 300))
    assert s["cover"]["height_px"] == 2775
    # Gutter <=150 p. : 0.375 + bleed 0.125 = 0.5
    assert s["margins"]["gutter_in"] == 0.5
    assert s["isbn_reserve_px"] == {"width": 600, "height": 360}

    # Gutter dynamique : >400 pages -> 0.75 (+ bleed)
    s2 = calculate_kdp_specs("8.5x11", page_count=500, paper_type="cream", bleed=True)
    assert s2["spine"]["width_in"] == round(500 * 0.0025, 6)
    assert s2["margins"]["gutter_in"] == 0.875
    assert s2["interior"]["width_px"] == 2625 and s2["interior"]["height_px"] == 3375

    # Sans bleed : marges brutes, intérieur = trim exact
    s3 = calculate_kdp_specs("6x9", page_count=100, bleed=False)
    assert s3["margins"]["gutter_in"] == 0.375
    assert s3["interior"]["width_px"] == 1800 and s3["interior"]["height_px"] == 2700

    for mauvais, valeurs in (("12x12", dict(page_count=10)),
                             ("6x9", dict(page_count=0)),
                             ("6x9", dict(page_count=10, paper_type="inconnu"))):
        try:
            calculate_kdp_specs(mauvais, **valeurs)
            raise AssertionError(f"Valeurs invalides non détectées : {mauvais} {valeurs}")
        except ValueError:
            pass

    afficher_succes("Dos, gutter dynamique, bleed, 300 DPI, ISBN et erreurs validés")


# ==============================================================================
# 2. CONNECTEURS MÉDIA — HTTP MOCKÉ (UNSPLASH / PIXABAY)
# ==============================================================================

def _fake_get_json(url, params=None, headers=None, timeout=10.0):
    """Réponses factices d'Unsplash et Pixabay (aucun appel réseau)."""
    if "api.unsplash.com" in url:
        assert headers and headers.get("Authorization", "").startswith("Client-ID "), \
            "En-tête Authorization: Client-ID attendu pour Unsplash"
        assert params and params.get("orientation") == "portrait"
        return {"results": [{
            "id": "u-photo-1",
            "description": "Mandala doré sacré",
            "alt_description": None,
            "urls": {
                "small": "https://images.unsplash.com/small.jpg",
                "regular": "https://images.unsplash.com/regular.jpg",
                "full": "https://images.unsplash.com/full.jpg",
            },
            "user": {"name": "Artiste Test"},
            "links": {"html": "https://unsplash.com/photos/u-photo-1"},
            "tags": [{"title": "mandala"}],
        }]}
    if "pixabay.com/api" in url:
        assert params and params.get("orientation") == "vertical", \
            "orientation='vertical' attendue pour un portrait Pixabay"
        return {"hits": [
            {"id": 11, "tags": "mandala, zen, or", "user": "Pix Test",
             "fullHDURL": "https://pixabay.com/full_hd.jpg",
             "webformatURL": "https://pixabay.com/web.jpg",
             "pageURL": "https://pixabay.com/photos/11"},
            # Pas de fullHDURL -> repli obligatoire sur largeImageURL
            {"id": 12, "tags": "botanique", "user": "Pix Test 2",
             "largeImageURL": "https://pixabay.com/large.jpg",
             "webformatURL": "https://pixabay.com/web2.jpg",
             "pageURL": "https://pixabay.com/photos/12"},
        ]}
    raise AssertionError(f"URL inattendue (appel réseau non mocké ?) : {url}")


def test_3_recherche_stock_http_mockee():
    print("\n🔍 Test 3 : search_stock_images() avec HTTP Unsplash/Pixabay mocké...")
    import kdp_extensions.media_connectors as mc

    with mock.patch.object(mc, "_httpx_get_json", side_effect=_fake_get_json), \
         mock.patch.object(mc, "_get_unsplash_key", return_value="fake_unsplash_key"), \
         mock.patch.object(mc, "_get_pixabay_key", return_value="fake_pixabay_key"):

        res_all = mc.search_stock_images("mandala", source="all", per_page=6)
        res_un = mc.search_stock_images("mandala", source="unsplash", per_page=6)
        res_pb = mc.search_stock_images("mandala", source="pixabay", per_page=6)
        # Rétrocompatibilité UI : 'pexels' redirigé vers Pixabay
        res_legacy = mc.search_stock_images("mandala", source="pexels", per_page=6)

    assert len(res_all) == 3, f"3 images attendues (1 Unsplash + 2 Pixabay), {len(res_all)} trouvées"
    assert {r["source"] for r in res_all} == {"unsplash", "pixabay"}

    unsplash = next(r for r in res_all if r["source"] == "unsplash")
    assert unsplash["hd_url"] == "https://images.unsplash.com/full.jpg"
    assert unsplash["thumb_url"] == "https://images.unsplash.com/small.jpg"
    assert unsplash["photographer"] == "Artiste Test"

    pix_hd = next(r for r in res_all if r["id"] == "pixabay-11")
    assert pix_hd["hd_url"] == "https://pixabay.com/full_hd.jpg"
    assert pix_hd["thumb_url"] == "https://pixabay.com/web.jpg"

    pix_legacy = next(r for r in res_all if r["id"] == "pixabay-12")
    assert pix_legacy["hd_url"] == "https://pixabay.com/large.jpg", \
        "Repli largeImageURL obligatoire quand fullHDURL est absent"

    assert len(res_un) == 1 and res_un[0]["source"] == "unsplash"
    assert len(res_pb) == 2 and all(r["source"] == "pixabay" for r in res_pb)
    assert len(res_legacy) == 2

    afficher_succes("Unsplash (Client-ID), Pixabay (fullHDURL/largeImageURL) et 'pexels' mockés")


def test_4_repli_catalogue_sans_reseau():
    print("\n🔍 Test 4 : Repli sur le catalogue curé (sans clé API / sans réseau)...")
    import kdp_extensions.media_connectors as mc

    def reseau_indisponible(*args, **kwargs):
        raise ConnectionError("réseau coupé (simulé)")

    with mock.patch.object(mc, "_httpx_get_json", side_effect=reseau_indisponible), \
         mock.patch.object(mc, "_get_unsplash_key", return_value=""), \
         mock.patch.object(mc, "_get_pixabay_key", return_value=""):
        res = mc.search_stock_images("mandala", source="all", per_page=5)

    assert len(res) > 0, "Le catalogue curé doit garantir une liste non vide"
    assert all(r.get("hd_url") for r in res), "Chaque image doit exposer une URL HD"
    assert all(r.get("thumb_url") for r in res)
    assert any(r["source"] == "curated" for r in res)

    afficher_succes("Jamais de liste vide : repli curé avec URL HD + vignettes")


def test_5_download_and_prepare_300dpi_mockee():
    print("\n🔍 Test 5 : download_and_prepare_cover_bg() — anti-hotlinking + 300 DPI...")
    import kdp_extensions.media_connectors as mc

    # Payload PNG factice (aucun téléchargement réel)
    buf = io.BytesIO()
    Image.new("RGB", (640, 480), "#334455").save(buf, format="PNG")
    octets_png = buf.getvalue()

    dest = None
    try:
        with mock.patch.object(mc, "_httpx_download", return_value=octets_png) as dl:
            dest = mc.download_and_prepare_cover_bg(
                "https://images.unsplash.com/photo-test?w=2400",
                target_width_px=900,
                target_height_px=1350,
            )
            assert dl.call_count == 1, "Le téléchargement doit passer par _httpx_download (mockable)"
            # En-têtes anti-hotlinking obligatoires (UA + Referer)
            kwargs = dl.call_args.kwargs
            assert "User-Agent" in kwargs.get("headers", {})
            assert "Referer" in kwargs.get("headers", {})

        assert dest is not None and dest.exists(), "Fichier local attendu dans assets/media_cache/"
        assert mc.MEDIA_CACHE_DIR in dest.parents, f"{dest} hors de assets/media_cache/"

        with Image.open(dest) as img:
            assert img.size == (900, 1350), f"Recadrage ImageOps.fit attendu, taille {img.size} obtenue"
            dpi = img.info.get("dpi", (0, 0))
            assert abs(dpi[0] - 300) < 1 and abs(dpi[1] - 300) < 1, f"DPI 300 attendu, {dpi} obtenu"
            assert img.mode == "RGB"
    finally:
        if dest and Path(dest).exists():
            Path(dest).unlink()

    afficher_succes("Téléchargement mocké, recadrage sans déformation et JPEG 300 DPI validés")


# ==============================================================================
# 3. CANVA CONNECT API — MOCKÉ (OAUTH, JETONS, UPLOAD, EXPORT, GABARIT)
# ==============================================================================

def test_6_canva_connect_mocke():
    print("\n🔍 Test 6 : Canva Connect API — OAuth 2.0, jetons, upload et export...")
    import kdp_extensions.media_connectors as mc

    # 1. URL d'autorisation (aucun réseau)
    auth = mc.get_canva_auth_url(redirect_uri="http://127.0.0.1:8000/api/canva/callback")
    assert isinstance(auth, dict), "get_canva_auth_url doit retourner un dict {auth_url, state}"
    assert "canva.com" in auth["auth_url"], "URL d'autorisation Canva attendue"
    assert "state" in auth and auth["state"], "state CSRF obligatoire"
    assert "client_id=" in auth["auth_url"] and "redirect_uri=" in auth["auth_url"]

    tmp_dir = Path(tempfile_dir())
    fichiers_sauves = []
    try:
        tokens_file = tmp_dir / "canva_tokens.json"

        with mock.patch.object(mc, "CANVA_TOKENS_FILE", tokens_file), \
             mock.patch.object(mc, "_get_canva_client_secret", return_value=""):
            # 2. Échange du code -> jeton persisté (mode simulé, sans secret client)
            tokens = mc.exchange_canva_code_for_token(
                code="fake_code", redirect_uri="http://127.0.0.1:8000/api/canva/callback",
                state=auth["state"],
            )
            assert tokens["access_token"].startswith("canva_simulated_token_")
            assert tokens_file.exists(), "Jeton persisté dans canva_tokens.json"
            assert json.loads(tokens_file.read_text(encoding="utf-8"))["access_token"]

            # 3. Lecture du jeton
            lus = mc.get_canva_tokens()
            assert lus and lus["access_token"] == tokens["access_token"]

            # 4. Upload d'actif -> repli local sans jeton live
            actif = tmp_dir / "couverture_test.png"
            Image.new("RGB", (300, 450), "#0A0F1D").save(actif, "PNG")
            up = mc.upload_canva_asset(str(actif), name="Couverture Test")
            assert up["status"] == "local_fallback" and up["mode"] == "local"
            assert Path(up["file_path"]).exists()

            # 5. Export design -> repli sur le gabarit local 300 DPI
            exp = mc.export_canva_design(design_id=None, template_path=str(actif))
            assert exp["status"] == "fallback_template" and exp["mode"] == "local"

            # 6. Actif inexistant -> FileNotFoundError explicite
            try:
                mc.upload_canva_asset(str(tmp_dir / "absent.png"))
                raise AssertionError("Fichier introuvable non détecté")
            except FileNotFoundError:
                pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    afficher_succes("OAuth (dict auth_url + state), jeton, upload et export fallback mockés")


def tempfile_dir() -> str:
    import tempfile
    return tempfile.mkdtemp(prefix="kdp_ext_test_")


def test_7_gabarit_canva_300dpi_isbn():
    print("\n🔍 Test 7 : Gabarit Canva 300 DPI — 16 formats + réserve ISBN 600x360...")
    import kdp_extensions.media_connectors as mc
    from kdp_extensions.kdp_dimensions import calculate_kdp_specs

    dest = None
    try:
        dest = mc.generate_canva_cover_template(
            book_id=BOOK_TEST_ID, format_kdp="6x9", nb_pages=100,
            titre="TEST ISBN", author="MarkEddy",
        )
        assert dest.exists() and dest.suffix == ".png"
        assert mc.MEDIA_CACHE_DIR in dest.parents

        specs = calculate_kdp_specs("6x9", page_count=100, bleed=True)
        img = Image.open(dest)
        assert img.size == (specs["cover"]["width_px"], specs["cover"]["height_px"]), \
            f"Taille couverture incorrecte : {img.size}"
        dpi = img.info.get("dpi", (0, 0))
        assert abs(dpi[0] - 300) < 1, f"DPI 300 attendu, {dpi} obtenu"

        # Réserve ISBN : zone blanche 600 x 360 px sur le Plat 4 (4ème de couverture)
        bleed_px = int(round(0.125 * 300))
        page_w_px = int(round(6.0 * 300))
        dos_w_px = int(round(specs["spine"]["width_in"] * 300))
        plat4_droite = bleed_px + page_w_px
        isbn_x1 = plat4_droite - 600 - int(0.25 * 300)
        isbn_y1 = img.size[1] - bleed_px - 360 - int(0.25 * 300)
        zone = img.crop((isbn_x1, isbn_y1, isbn_x1 + 600, isbn_y1 + 360)).convert("RGB")
        blancs = sum(1 for px in zone.getdata() if px == (255, 255, 255))
        assert blancs > 150000, f"Réserve ISBN blanche attendue, {blancs} px blancs seulement"

        # Variante PDF imprimable générée à côté du PNG
        pdf = dest.with_suffix(".pdf")
        assert pdf.exists(), "PDF 300 DPI attendu en complément du PNG"
    finally:
        if dest and dest.exists():
            dest.unlink()
        if dest:
            pdf = dest.with_suffix(".pdf")
            if pdf.exists():
                pdf.unlink()

    afficher_succes("Gabarit PNG + PDF 300 DPI, dimensions exactes et réserve ISBN 600x360")


# ==============================================================================
# 4. MOTEUR DE COLORIAGE — NOIR PUR, ANTI-BAVURE, PDF (MOCKÉ)
# ==============================================================================

def test_8_svg_noir_blanc_pur():
    print("\n🔍 Test 8 : Générateurs SVG — noir #000000 sur blanc #FFFFFF, zéro gris...")
    from kdp_extensions.coloring_book_engine import GENERATEURS_SVG

    assert len(GENERATEURS_SVG) == 4, "4 thèmes attendus (mandalas, botanique, animaux, architecture)"
    autorises = {"000000", "FFFFFF"}

    for nom, gen in GENERATEURS_SVG.items():
        svg = gen(1)
        assert svg and "<svg" in svg, f"SVG invalide pour '{nom}'"
        couleurs = set(re.findall(r"#([0-9a-fA-F]{6})", svg))
        assert couleurs <= autorises, f"Teinte non autorisée dans '{nom}' : {couleurs - autorises}"
        assert "rgb(" not in svg.lower() and "gray" not in svg.lower() \
            and "grey" not in svg.lower(), f"Dégradé/gray détecté dans '{nom}'"
        # Deux index doivent produire deux planches distinctes
        assert gen(2) != gen(1), f"Les planches '{nom}' doivent varier selon l'index"

    afficher_succes("4 thèmes SVG en noir/blanc pur, sans gris ni dégradé")


def test_9_line_art_binaire():
    print("\n🔍 Test 9 : convertir_en_line_art() — binarisation stricte 0/255...")
    from kdp_extensions.coloring_book_engine import convertir_en_line_art

    tmp_dir = Path(tempfile_dir())
    try:
        src = tmp_dir / "source.png"
        img = Image.new("L", (400, 400), 255)
        d = ImageDraw.Draw(img)
        d.rectangle([40, 40, 360, 360], outline=0, width=6)
        d.ellipse([110, 110, 290, 290], outline=0, width=6)
        img.save(src, "PNG")

        out = convertir_en_line_art(src, tmp_dir / "line_art.png")
        assert out.exists()

        binarise = Image.open(out).convert("L")
        valeurs = set(binarise.getdata())
        assert valeurs <= {0, 255}, f"Niveaux de gris détectés : {sorted(valeurs)[:10]}"
        assert valeurs == {0, 255}, "Les deux tons (trait noir + fond blanc) doivent coexister"
        assert Image.open(out).info.get("dpi", (0, 0))[0] >= 299, "Sortie 300 DPI attendue"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    afficher_succes("Line-art binaire 0/255 uniquement, aucune teinte intermédiaire")


def _fake_compiler_pdf(html_path, pdf_path, largeur_in, hauteur_in):
    """Mock de compiler_pdf_playwright : compte les pages réelles du HTML assemblé."""
    html = Path(html_path).read_text(encoding="utf-8")
    nb_pages = html.count('<div class="p">')
    from pypdf import PdfWriter
    writer = PdfWriter()
    for _ in range(max(1, nb_pages)):
        writer.add_blank_page(width=largeur_in * 72.0, height=hauteur_in * 72.0)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return Path(pdf_path)


def _fake_fabriquer(**kwargs):
    """Mock de cover_artisan_agent.fabriquer : écrit une couverture PDF factice."""
    sortie = Path(kwargs["fichier_sortie"])
    sortie.parent.mkdir(parents=True, exist_ok=True)
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=432, height=648)
    with open(sortie, "wb") as f:
        writer.write(f)
    return str(sortie)


def test_10_production_coloriage_mockee():
    print("\n🔍 Test 10 : produire_livre_coloriage() mocké (Playwright + couverture)...")
    import kdp_extensions.coloring_book_engine as ce
    import cover_artisan_agent

    if DOSSIER_TEST_COLO.exists():
        shutil.rmtree(DOSSIER_TEST_COLO, ignore_errors=True)

    try:
        with mock.patch.object(ce, "compiler_pdf_playwright", side_effect=_fake_compiler_pdf), \
             mock.patch.object(ce, "_html_cover_vers_jpg", return_value=None), \
             mock.patch.object(cover_artisan_agent, "fabriquer", side_effect=_fake_fabriquer):
            res = ce.produire_livre_coloriage(
                book_id=BOOK_TEST_ID,
                titre="MANDALAS DE TEST",
                sous_titre="Sous-titre de test",
                theme="mandalas",
                nb_illustrations=2,
                recto_uniquement=True,
                format_kdp="6x9",
            )

        assert res["status"] == "success"
        assert res["format_kdp"] == "6x9"
        # 3 pages de garde + 1 anti-bavure + 2 x (planche + verso) + félicitations
        assert res["nb_pages"] == 9, f"9 pages attendues (recto seul), {res['nb_pages']} obtenues"
        assert res["nb_illustrations"] == 2

        # Specs 300 DPI du format 6x9 avec bleed
        specs = res["specs"]
        assert specs["interior"]["width_px"] == 1875 and specs["interior"]["height_px"] == 2775
        assert res["epaisseur_dos_po"] == round(9 * 0.002252, 6)

        # Fichiers produits
        pdf_int = Path(res["chemin_pdf_interieur"])
        assert pdf_int.exists() and pdf_int.stat().st_size > 0
        assert Path(res["chemin_pdf_couverture"]).exists(), "Couverture PDF attendue"
        assert res["chemin_couverture_jpg"] is None, "Aperçu JPG désactivé (mock _html_cover_vers_jpg)"

        html = Path(res["chemin_interieur_html"])
        assert html.exists()
        contenu = html.read_text(encoding="utf-8")
        # Recto uniquement : 1 verso blanc anti-bavure APRÈS chaque planche
        assert contenu.count('<div class="page verso"></div>') == 2, \
            "Un verso anti-bavure est exigé après chacune des 2 planches"

        # Planches exportées : 2 SVG + 2 PNG
        dossier_planches = Path(res["dossier_planches"])
        assert len(list(dossier_planches.glob("*.svg"))) == 2
        assert len(list(dossier_planches.glob("*.png"))) == 2

        assert Path(res["chemin_marketing_html"]).exists()
        assert not (DOSSIER_TEST_COLO / "_assembly_tmp.html").exists(), \
            "Le HTML temporaire d'assemblage doit être nettoyé"

        # --- Variante recto/verso standard (sans verso anti-bavure) ------------
        with mock.patch.object(ce, "compiler_pdf_playwright", side_effect=_fake_compiler_pdf), \
             mock.patch.object(ce, "_html_cover_vers_jpg", return_value=None), \
             mock.patch.object(cover_artisan_agent, "fabriquer", side_effect=_fake_fabriquer):
            res2 = ce.produire_livre_coloriage(
                book_id=BOOK_TEST_ID,
                titre="MANDALAS DE TEST",
                sous_titre="Sous-titre de test",
                theme="mandalas",
                nb_illustrations=2,
                recto_uniquement=False,
                format_kdp="6x9",
            )
        # 3 pages de garde + 2 planches + félicitations = 6 pages
        assert res2["nb_pages"] == 6, f"6 pages attendues (recto/verso), {res2['nb_pages']} obtenues"
        contenu2 = Path(res2["chemin_interieur_html"]).read_text(encoding="utf-8")
        assert '<div class="page verso"></div>' not in contenu2, \
            "Aucun verso anti-bavure en mode recto/verso standard"
    finally:
        shutil.rmtree(DOSSIER_TEST_COLO, ignore_errors=True)

    afficher_succes("9 p. recto seul (verso anti-bavure) / 6 p. standard, dos et specs 6x9 validés")


# ==============================================================================
# 5. INTÉGRATION APP_STUDIO (ROUTES, SCHÉMA, MIGRATIONS) — SANS SERVEUR
# ==============================================================================

def test_11_app_studio_extensions():
    print("\n🔍 Test 11 : Routes et schéma d'extension dans app_studio / studio_db...")
    import app_studio
    import studio_db

    # 1. Routes d'extension enregistrées
    routes = [r.path for r in app_studio.app.routes if hasattr(r, "path")]
    for attendue in ("/api/kdp/formats", "/api/canva/export/{book_id}",
                     "/api/media/search", "/api/canva/template/{book_id}"):
        assert attendue in routes, f"Route manquante : {attendue}"

    # 2. GET /api/kdp/formats -> 16 formats
    body = json.loads(app_studio.api_kdp_formats().body.decode("utf-8"))
    assert body["status"] == "success" and body["total"] == 16, body
    assert len(body["formats"]) == 16

    # 3. Recherche médias via le connecteur d'extension (HTTP mocké / sans clé)
    def reseau_indisponible(*args, **kwargs):
        raise ConnectionError("réseau coupé (simulé)")

    import kdp_extensions.media_connectors as mc
    with mock.patch.object(mc, "_httpx_get_json", side_effect=reseau_indisponible), \
         mock.patch.object(mc, "_get_unsplash_key", return_value=""), \
         mock.patch.object(mc, "_get_pixabay_key", return_value=""):
        res = app_studio.api_media_search(query="mandala", source="all",
                                          per_page=4, current_user={"id": 1})
    body = json.loads(res.body.decode("utf-8"))
    assert body["status"] == "success" and len(body["images"]) > 0, body

    # 4. URL Canva : dict {auth_url, state} correctement normalisé par la route
    class _Req:
        base_url = "http://127.0.0.1:8000"

    res_auth = app_studio.api_canva_auth_url(request=_Req(), current_user={"id": 1})
    body_auth = json.loads(res_auth.body.decode("utf-8"))
    assert body_auth["status"] == "success"
    assert "canva.com" in body_auth["auth_url"], body_auth

    # 5. CreateBookRequest : nouveaux champs optionnels, défauts préservés
    req = app_studio.CreateBookRequest(niche="test")
    assert req.project_type == "non_fiction"
    assert req.cover_image_url is None and req.single_sided is None
    assert req.format_kdp is None, "format_kdp doit rester optionnel (None par défaut)"

    # 6. studio_db : colonnes migrées + paramètres optionnels ajoutés
    conn = studio_db.get_connection()
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(books)").fetchall()]
    finally:
        conn.close()
    assert "project_type" in cols and "cover_image_url" in cols, \
        f"Colonnes d'extension manquantes : {set(['project_type', 'cover_image_url']) - set(cols)}"

    sig = inspect.signature(studio_db.creer_livre)
    assert sig.parameters["project_type"].default == "non_fiction"
    assert sig.parameters["cover_image_url"].default is None

    afficher_succes("Routes /api/kdp/formats + /api/canva/export, schéma et migrations validés")


# ==============================================================================
# 6. AUDIT / CORRECTIFS SUPPLÉMENTAIRES (Agent 0, polices, intérieur, QC)
# ==============================================================================

def test_12_routes_agent0_fonts_webhooks_montees():
    print("\n🔍 Test 12 : Routeur d'extensions monté (Agent 0 / polices / webhooks)...")
    import tempfile
    from fastapi.testclient import TestClient
    import app_studio
    import kdp_extensions.pipeline_bridge as pont

    client = TestClient(app_studio.app)

    # /api/kdp/formats reste servi (historique + routeur)
    r_formats = client.get("/api/kdp/formats")
    assert r_formats.status_code == 200 and r_formats.json()["total"] == 16

    # /api/fonts/search : catalogue curé avec polices enfants + éditoriales
    r_fonts = client.get("/api/fonts/search?query=Fredoka")
    assert r_fonts.status_code == 200, r_fonts.text
    corps = r_fonts.json()
    assert corps["count"] >= 1 and any(f["family"] == "Fredoka" for f in corps["fonts"])

    # /api/research/analyze-bestsellers : HTTP/IA mockés (aucun réel)
    faux_ctx = {
        "report": {"superior_angle": "Angle test", "trend_score": 71},
        "report_path": "competitor_gap_report.json",
        "recommended_title": "TITRE TEST",
        "recommended_subtitle_seo": "Sous-titre test",
        "backend_keywords_7": [f"mot-{i}" for i in range(7)],
        "design_directives": {"palette": "or"},
        "editorial_directive_block": "DIRECTIVE TEST",
    }
    with mock.patch.object(pont, "prepare_competitive_context", return_value=faux_ctx) as prep:
        r_agent0 = client.post(
            "/api/research/analyze-bestsellers",
            json={"niche": "Stoicisme Moderne", "use_ai": False},
        )
    assert r_agent0.status_code == 200, r_agent0.text
    assert r_agent0.json()["report"]["superior_angle"] == "Angle test"
    assert prep.call_args.kwargs["use_ai"] is False

    # /api/webhooks/logs : 401 sans JWT, 200 avec le compte admin
    assert client.get("/api/webhooks/logs").status_code == 401
    r_login = client.post("/api/auth/login", json={"email": "admin@markeddy.com", "password": "Admin123!"})
    assert r_login.status_code == 200, r_login.text
    jeton = r_login.json()["token"]
    r_logs = client.get("/api/webhooks/logs", headers={"Authorization": f"Bearer {jeton}"})
    assert r_logs.status_code == 200 and r_logs.json()["status"] == "success"

    # Injection dans blueprint : clé réellement consommée + directive
    with tempfile.TemporaryDirectory() as tmp:
        bp = Path(tmp) / "book_blueprint.json"
        bp.write_text(json.dumps({"titre": "TITRE TEST"}), encoding="utf-8")
        rapport = dict(faux_ctx["report"])
        rapport["backend_keywords_7"] = faux_ctx["backend_keywords_7"]
        ok = pont.apply_gap_report_to_blueprint(bp, pont.context_from_report_dict(rapport))
        donnees = json.loads(bp.read_text(encoding="utf-8"))
    assert ok is True
    assert len(donnees["mots_cles_kdp"]) == 7
    assert "directive_editoriale_agent0" in donnees

    afficher_succes("Routes Agent 0 / polices / webhooks montées + injection blueprint validée")


def test_13_agent0_ia_et_sept_mots_cles():
    print("\n🔍 Test 13 : Agent 0 appelle Gemini et garantit 7 mots-clés...")
    import tempfile
    import kdp_extensions.market_intelligence as mi

    assert len(mi._sept_mots_cles(["a", "b"], "Stoicisme", [], [])) == 7

    faux_json = json.dumps({
        "superior_angle": "Angle IA",
        "recommended_title": "TITRE IA",
        "recommended_subtitle_seo": "Sous-titre IA",
        "backend_keywords_7": ["k1", "k2", "k3", "k4"],
        "must_have_assets": ["checklist"],
        "design_directives": {"palette": "noir et or"},
        "bestseller_weaknesses": [{
            "categorie": "Fond", "faiblesse_concurrents": "Théorie", "contre_attaque_markeddy": "Cas pratiques"
        }],
    })
    with tempfile.TemporaryDirectory() as tmp:
        sortie = Path(tmp) / "rapport.json"
        with mock.patch.object(mi, "fetch_google_signals", return_value={
            "niche": "Stoicisme", "trend_score": 68, "google_signals": ["stoicisme livre", "stoicisme méthode"]
        }), mock.patch.object(mi, "fetch_amazon_kdp_suggestions", return_value=["stoicisme guide"]), \
             mock.patch("kdp_extensions.webhooks.emit_webhook", return_value={"mode": "local_audit_only"}), \
             mock.patch("call_ai.generer_texte_gemini", return_value=faux_json) as gemini:
            rapport = mi.analyze_bestsellers_and_gaps(
                niche="Stoicisme", cible="Débutants", marketplace="fr",
                output_path=sortie, use_ai=True,
            )
        assert gemini.called, "Agent 0 doit utiliser call_ai.generer_texte_gemini"
    assert rapport.superior_angle == "Angle IA"
    assert len(rapport.backend_keywords_7) == 7

    afficher_succes("Agent 0 IA actif + exactement 7 mots-clés backend")


def test_14_connecteur_polices_filtres_et_live():
    print("\n🔍 Test 14 : Connecteur Google Fonts (accents, filtres, mode live)...")
    import kdp_extensions.fonts_connector as fc

    editorial = fc.search_google_fonts(query="editoria")
    assert editorial["count"] >= 1, editorial
    assert any(f["family"] in ("Playfair Display", "Cormorant Garamond", "Libre Baskerville")
               for f in editorial["fonts"])
    introuvable = fc.search_google_fonts(query="zzz_introuvable_zzz")
    assert introuvable["count"] == 0, "Un filtre sans résultat ne doit pas renvoyer tout le catalogue"
    try:
        fc.search_google_fonts(category="invalide")
        raise AssertionError("Une catégorie invalide doit lever ValueError")
    except ValueError:
        pass

    faux_payload = {"items": [{"family": "Nunito", "category": "sans-serif",
                               "variants": ["regular"], "subsets": ["latin"], "files": {}}]}
    with mock.patch.object(fc, "_get_fonts_api_key", return_value="cle_test"), \
         mock.patch.object(fc, "_httpx_get_json", return_value=faux_payload):
        live = fc.search_google_fonts(query="nunito")
    assert live["mode"] == "live" and live["fonts"][0]["family"] == "Nunito"

    afficher_succes("Polices curées/live filtrées sans faux positif")


def test_15_interior_layout_master_et_formateur():
    print("\n🔍 Test 15 : kdp-interior-layout-master + formateur 6x9 réparé...")
    import tempfile
    import kdp_formatter
    from kdp_extensions.interior_layout_master import composer_interieur, choisir_thematique

    assert choisir_thematique(public_cible="Enfants 4-8 ans") == "ENFANT_EDUCATIF"
    assert choisir_thematique(public_cible="Adultes") == "NON_FICTION"

    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "manuscrit.md"
        md.write_text("# Mon Livre\n\n## Section Une\n\nTexte de test.\n", encoding="utf-8")
        html = Path(tmp) / "interieur.html"
        rapport = composer_interieur(
            chemin_manuscrit=str(md), chemin_sortie_html=str(html),
            format_kdp="6x9", titre_livre="MON LIVRE",
            public_cible="Enfants 4-8 ans", appliquer_correctifs=True,
        )
        assert html.exists() and html.stat().st_size > 100
        assert rapport["thematique"] == "ENFANT_EDUCATIF"
        contenu = html.read_text(encoding="utf-8")
        assert "<h1" in contenu and "<h2" in contenu

    # Le formateur historique transmet bien titre_livre (signature obligatoire)
    with mock.patch("kdp_formatter.compiler_livre_sur_mesure") as comp:
        kdp_formatter.convertir_manuscrit_en_pdf(
            chemin_md="manuscrit_test_qa.md",
            sortie_html="interieur_test_qa.html",
        )
        assert comp.call_args.kwargs["titre_livre"] == "LIVRE KDP"
        assert comp.call_args.kwargs["format_choisi"] == "6x9"

    afficher_succes("Intérieur composer + correctifs pré-presse + formateur non cassé")


def test_16_coloriage_noir_blanc_pur_et_bornes():
    print("\n🔍 Test 16 : Coloriage — zéro gris et mandalas dans le cadre...")
    from kdp_extensions.coloring_book_engine import (
        dessiner_planche_pil,
        GENERATEURS_SVG,
    )

    # Aucun générateur SVG n'émet de gris (uniquement #000000 / #FFFFFF)
    couleurs = set()
    for generateur in GENERATEURS_SVG.values():
        couleurs.update(re.findall(r"#[0-9a-fA-F]{6}", generateur(0)))
    assert couleurs <= {"#000000", "#FFFFFF"}, couleurs

    # Aucun tuple gris résiduel dans le moteur racine historique
    source_racine = Path("coloring_book_engine.py").read_text(encoding="utf-8")
    for gris in ("(50, 50, 50)", "(100, 100, 100)", "(252, 252, 252)"):
        assert gris not in source_racine, f"Gris interdit résiduel : {gris}"

    # Mandala 8.5x11 : le noir ne touche jamais le bord de la page
    image = dessiner_planche_pil("mandalas", 1, "TEST", 2550, 3300)
    boite = image.convert("L").point(lambda p: 255 if p < 128 else 0).getbbox()
    assert boite is not None
    x0, y0, x1, y1 = boite
    assert x0 > 0 and y0 > 0 and x1 < 2550 - 1 and y1 < 3300 - 1, boite

    afficher_succes("Traits noirs bornés dans le cadre, zéro niveau de gris")


# ==============================================================================
# EXÉCUTION
# ==============================================================================

def main() -> int:
    global tests_reussis, tests_total
    tests_reussis, tests_total = 0, 0

    print("=" * 65)
    print("🧪 SUITE DE TESTS — EXTENSIONS kdp_extensions/ (MOCKÉ)")
    print("=" * 65)

    tests = [
        ("16 formats KDP officiels + normalisation", test_1_formats_kdp_16),
        ("calculate_kdp_specs : dos, gutter, 300 DPI, ISBN", test_2_calculate_kdp_specs),
        ("Recherche stock Unsplash/Pixabay (HTTP mocké)", test_3_recherche_stock_http_mockee),
        ("Repli catalogue curé sans réseau", test_4_repli_catalogue_sans_reseau),
        ("Téléchargement couverture 300 DPI (mocké)", test_5_download_and_prepare_300dpi_mockee),
        ("Canva Connect API (OAuth, jetons, upload, export)", test_6_canva_connect_mocke),
        ("Gabarit Canva 300 DPI + réserve ISBN 600x360", test_7_gabarit_canva_300dpi_isbn),
        ("Générateurs SVG noir/blanc pur (4 thèmes)", test_8_svg_noir_blanc_pur),
        ("Line-art binaire zéro gris", test_9_line_art_binaire),
        ("Production livre de coloriage (moteur mocké)", test_10_production_coloriage_mockee),
        ("Intégration app_studio : routes + schéma", test_11_app_studio_extensions),
        ("Routes Agent 0 / polices / webhooks + blueprint", test_12_routes_agent0_fonts_webhooks_montees),
        ("Agent 0 IA + 7 mots-clés", test_13_agent0_ia_et_sept_mots_cles),
        ("Connecteur Google Fonts (filtres/live)", test_14_connecteur_polices_filtres_et_live),
        ("kdp-interior-layout-master + formateur", test_15_interior_layout_master_et_formateur),
        ("Coloriage noir/blanc pur + bornes mandala", test_16_coloriage_noir_blanc_pur_et_bornes),
    ]

    for nom, func in tests:
        try:
            func()
        except Exception as e:
            afficher_erreur(f"{nom} : {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 65)
    print(f"📊 RÉSULTAT EXTENSIONS : {tests_reussis}/{tests_total} tests validés.")
    if tests_reussis == tests_total and tests_total > 0:
        print("🎉 TOUTES LES EXTENSIONS SONT AU VERT !")
        print("=" * 65)
        return 0
    print("⚠️ Certains points nécessitent votre attention (voir détails ci-dessus).")
    print("=" * 65)
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
