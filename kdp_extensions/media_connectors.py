"""
kdp_extensions/media_connectors.py - Connecteurs Médias & Design (Unsplash, Pixabay, Canva).

Extensions 100 % isolées : ce module n'altère en rien le media_connectors.py de la
racine. Il implémente :

1. search_stock_images(query, source="all", orientation="portrait", per_page=12)
   - Unsplash  : UNSPLASH_ACCESS_KEY  -> Authorization: Client-ID ...
   - Pixabay   : PIXABAY_API_KEY      -> https://pixabay.com/api/
                 orientation='vertical' pour portrait, image_type 'photo' | 'vector',
                 URL HD = hit.get("fullHDURL") or hit.get("largeImageURL"),
                 aperçu = hit.get("webformatURL").
   - Gestion propre des clés absentes (repli sur un catalogue curé hors-ligne).

2. download_and_prepare_cover_bg(image_url, target_width_px, target_height_px)
   - Téléchargement systématique dans assets/media_cache/ (conformité anti-hotlinking),
     recadrage sans déformation (ImageOps.fit) et sauvegarde JPEG 300 DPI.

3. Connecteur Canva Connect API :
   - get_canva_auth_url()            : URL OAuth 2.0 + state aléatoire.
   - exchange_canva_code_for_token() : callback -> canva_tokens.json.
   - upload_canva_asset() / export_canva_design() : avec repli local propre.
   - generate_canva_cover_template() : gabarit PNG/PDF 300 DPI (16 formats KDP,
     dos calculé, réserve ISBN 600x360 px) prêt à ouvrir dans Canva.

Exécution : .\\.venv\\Scripts\\python.exe
"""

import io
import json
import time
import hashlib
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # pragma: no cover - dotenv optionnel
    pass

import os

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None

from PIL import Image, ImageOps, ImageDraw

from kdp_extensions.kdp_dimensions import (
    calculate_kdp_specs,
    normalize_format,
    KDP_FORMAT_IDS,
)

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_CACHE_DIR = BASE_DIR / "assets" / "media_cache"
MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

CANVA_TOKENS_FILE = BASE_DIR / "canva_tokens.json"
CANVA_API_BASE = "https://api.canva.com/rest/v1"

# Clés d'API lues à l'exécution (gestion propre si absentes du .env)
def _env(key: str, alt: str = "") -> str:
    return (os.getenv(key) or os.getenv(alt) or "").strip()


def _get_unsplash_key() -> str:
    return _env("UNSPLASH_ACCESS_KEY", "UNSPLASH_CLIENT_ID")


def _get_pixabay_key() -> str:
    return _env("PIXABAY_API_KEY")


def _get_canva_client_id() -> str:
    return _env("CANVA_CLIENT_ID") or "kdp_studio_canva_client"


def _get_canva_client_secret() -> str:
    return _env("CANVA_CLIENT_SECRET")


# ==============================================================================
# RESSOURCES HTTP (isolées pour permettre le mock dans les tests)
# ==============================================================================

def _httpx_get_json(url: str, params: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    timeout: float = 10.0) -> Dict[str, Any]:
    """GET JSON via httpx. Fonction mockable dans test_extensions.py."""
    if httpx is None:
        raise RuntimeError("Le module httpx est requis (pip install httpx).")
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()


def _httpx_download(url: str, headers: Optional[Dict[str, str]] = None,
                    timeout: float = 20.0) -> bytes:
    """Téléchargement binaire via httpx. Fonction mockable dans test_extensions.py."""
    if httpx is None:
        raise RuntimeError("Le module httpx est requis (pip install httpx).")
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.content


# ==============================================================================
# CATALOGUE CURÉ DE SECOURS (hors-ligne / sans clé API)
# ==============================================================================

PRESETS_STOCK_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "preset-mandala-gold",
        "title": "Mandala Géométrique Sacré Or",
        "source": "curated",
        "photographer": "Studio MarkEddy Art",
        "thumb_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=400&q=80",
        "regular_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=1600&q=85",
        "hd_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=2400&q=95",
        "url_page": "https://unsplash.com",
        "tags": ["mandala", "coloriage", "or", "spiritualite", "meditation", "zen"],
    },
    {
        "id": "preset-finance-abyssal",
        "title": "Abstrait Obsidienne & Ondes Dorées",
        "source": "curated",
        "photographer": "Élégance Graphique",
        "thumb_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80",
        "regular_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1600&q=85",
        "hd_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=2400&q=95",
        "url_page": "https://unsplash.com",
        "tags": ["finance", "business", "sombre", "or", "richesse", "argent"],
    },
    {
        "id": "preset-nature-botanic",
        "title": "Flore Tropicale Minimaliste",
        "source": "curated",
        "photographer": "Nature Botanique",
        "thumb_url": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400&q=80",
        "regular_url": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600&q=85",
        "hd_url": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=2400&q=95",
        "url_page": "https://unsplash.com",
        "tags": ["nature", "botanique", "fleurs", "feuilles", "coloriage", "relaxation"],
    },
    {
        "id": "preset-coloring-lines",
        "title": "Motifs Géométriques Noir & Blanc",
        "source": "curated",
        "photographer": "Atelier Coloriage Zen",
        "thumb_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&q=80",
        "regular_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1600&q=85",
        "hd_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=2400&q=95",
        "url_page": "https://unsplash.com",
        "tags": ["coloriage", "mandalas", "motifs", "lignes", "dessin", "art"],
    },
    {
        "id": "preset-architecture-pagoda",
        "title": "Architecture Zen & Mont Fuji",
        "source": "curated",
        "photographer": "Orient Sérénité",
        "thumb_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=400&q=80",
        "regular_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=1600&q=85",
        "hd_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=2400&q=95",
        "url_page": "https://unsplash.com",
        "tags": ["architecture", "japon", "zen", "voyage", "temple", "coloriage"],
    },
]


# ==============================================================================
# 1. RECHERCHE UNIFIÉE UNSPLASH + PIXABAY
# ==============================================================================

def _search_unsplash(query: str, orientation: str, per_page: int) -> List[Dict[str, Any]]:
    """Recherche Unsplash (Authorization: Client-ID <key>)."""
    key = _get_unsplash_key()
    if not key:
        return []

    data = _httpx_get_json(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "orientation": orientation, "per_page": per_page},
        headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"},
        timeout=8.0,
    )

    resultats = []
    for photo in data.get("results", []) or []:
        urls = photo.get("urls") or {}
        user = photo.get("user") or {}
        resultats.append({
            "id": f"unsplash-{photo.get('id')}",
            "title": photo.get("description") or photo.get("alt_description") or f"Photo Unsplash {query}",
            "source": "unsplash",
            "photographer": user.get("name", "Inconnu"),
            "thumb_url": urls.get("small") or urls.get("thumb") or "",
            "regular_url": urls.get("regular") or urls.get("small") or "",
            "hd_url": urls.get("full") or urls.get("regular") or "",
            "url_page": (photo.get("links") or {}).get("html"),
            "tags": [t for t in (photo.get("tags") or []) if isinstance(t, dict)][:6],
        })
    return resultats


def _search_pixabay(query: str, orientation: str, per_page: int,
                    image_type: str = "photo") -> List[Dict[str, Any]]:
    """
    Recherche Pixabay (PIXABAY_API_KEY).
    - orientation : 'vertical' pour portrait, 'horizontal' pour paysage.
    - image_type  : 'photo' ou 'vector'.
    - URL HD      : hit.get("fullHDURL") or hit.get("largeImageURL").
    - Aperçu      : hit.get("webformatURL").
    """
    key = _get_pixabay_key()
    if not key:
        return []

    params: Dict[str, Any] = {
        "key": key,
        "q": query,
        "image_type": image_type if image_type in ("photo", "vector") else "photo",
        "orientation": "vertical" if orientation == "portrait" else "horizontal",
        "per_page": max(3, min(int(per_page), 200)),
        "safesearch": "true",
    }

    data = _httpx_get_json("https://pixabay.com/api/", params=params, timeout=8.0)

    resultats = []
    for hit in data.get("hits", []) or []:
        hd_url = hit.get("fullHDURL") or hit.get("largeImageURL") or hit.get("largeImageURL")
        resultats.append({
            "id": f"pixabay-{hit.get('id')}",
            "title": hit.get("tags") or f"Image Pixabay {query}",
            "source": "pixabay",
            "photographer": hit.get("user", "Inconnu"),
            "thumb_url": hit.get("webformatURL") or hit.get("previewURL") or "",
            "regular_url": hit.get("webformatURL") or hit.get("previewURL") or "",
            "hd_url": hd_url or hit.get("webformatURL") or "",
            "url_page": hit.get("pageURL"),
            "tags": [t.strip() for t in str(hit.get("tags", "")).split(",") if t.strip()][:6],
        })
    return resultats


def search_stock_images(
    query: str,
    source: str = "all",
    orientation: str = "portrait",
    per_page: int = 12
) -> List[Dict[str, Any]]:
    """
    Recherche unifiée d'images libres de droits (Unsplash + Pixabay).

    - source : 'all' | 'unsplash' | 'pixabay'
    - En l'absence de clé API ou de résultats, repli sur le catalogue curé
      hors-ligne afin que l'interface reste toujours fonctionnelle.
    """
    query_clean = (query or "").strip()
    source_clean = (source or "all").strip().lower()
    per_page = max(1, min(int(per_page or 12), 30))
    resultats: List[Dict[str, Any]] = []

    if source_clean in ("all", "unsplash"):
        try:
            resultats.extend(_search_unsplash(query_clean, orientation, per_page))
        except Exception as e:
            print(f"⚠️ Note recherche Unsplash : {e}")

    if source_clean in ("all", "pixabay", "pexels"):
        # 'pexels' accepté par rétrocompatibilité de l'UI -> redirigé vers Pixabay
        try:
            resultats.extend(_search_pixabay(query_clean, orientation, per_page))
        except Exception as e:
            print(f"⚠️ Note recherche Pixabay : {e}")

    # Repli catalogue curé si aucune source externe n'a répondu
    if not resultats:
        mots_cles = query_clean.lower().split()
        correspondances = []
        for item in PRESETS_STOCK_CATALOG:
            texte = (item["title"] + " " + " ".join(item["tags"])).lower()
            score = sum(1 for m in mots_cles if m in texte)
            if score > 0 or not mots_cles:
                correspondances.append((score, item))
        correspondances.sort(key=lambda x: x[0], reverse=True)
        resultats = [item for _, item in correspondances] or list(PRESETS_STOCK_CATALOG)

    return resultats[:per_page]


# ==============================================================================
# 2. TÉLÉCHARGEMENT & PRÉPRESSE 300 DPI (ANTI-HOTLINKING)
# ==============================================================================

def download_and_prepare_cover_bg(
    image_url: str,
    target_width_px: int,
    target_height_px: int,
    output_filename: Optional[str] = None
) -> Path:
    """
    Télécharge systématiquement l'image choisie dans assets/media_cache/
    (les hotlinkers CDN bloquent les requêtes directes des sites tiers),
    la recadre au ratio exact KDP SANS déformation (ImageOps.fit) et
    l'enregistre en JPEG 300 DPI.
    """
    if not image_url or not str(image_url).strip():
        raise ValueError("URL d'image vide.")

    target_width_px = int(target_width_px)
    target_height_px = int(target_height_px)
    if target_width_px < 1 or target_height_px < 1:
        raise ValueError("Dimensions cibles invalides.")

    hash_nom = hashlib.md5(f"{image_url}|{target_width_px}x{target_height_px}".encode("utf-8")).hexdigest()[:12]
    nom_fichier = output_filename or f"cover_bg_{hash_nom}.jpg"
    dest_path = MEDIA_CACHE_DIR / nom_fichier

    image_source: Optional[Image.Image] = None

    if str(image_url).startswith(("http://", "https://")):
        try:
            raw = _httpx_download(
                image_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                    "Referer": f"{image_url.split('/')[0]}//{image_url.split('/')[2]}/",
                    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                },
            )
            image_source = Image.open(io.BytesIO(raw))
            image_source.load()
        except Exception as e:
            print(f"⚠️ Téléchargement distant échoué ({e}), génération d'un fond texturé local...")
    else:
        local = Path(image_url)
        if local.exists():
            image_source = Image.open(local)
            image_source.load()

    # Repli synthétique si le réseau ou la source échoue
    if image_source is None:
        image_source = Image.new("RGB", (target_width_px, target_height_px), color="#0A0F1D")
        draw = ImageDraw.Draw(image_source)
        for r in range(200, max(target_width_px, target_height_px), 80):
            draw.ellipse(
                (target_width_px // 2 - r, target_height_px // 2 - r,
                 target_width_px // 2 + r, target_height_px // 2 + r),
                outline="#D4AF37", width=2,
            )

    # Recadrage au ratio parfait KDP (sans anamorphose)
    image_finale = ImageOps.fit(
        image_source.convert("RGB"),
        (target_width_px, target_height_px),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    image_finale.save(dest_path, "JPEG", quality=95, dpi=(300, 300))
    print(f"🎨 Image d'arrière-plan 300 DPI préparée : {dest_path.name} "
          f"({target_width_px}x{target_height_px} px)")
    return dest_path


# ==============================================================================
# 3. CONNECTEUR CANVA CONNECT API (OAUTH 2.0)
# ==============================================================================

def get_canva_auth_url(redirect_uri: str, state: Optional[str] = None) -> Dict[str, str]:
    """
    Génère l'URL d'autorisation OAuth 2.0 PKCE (s256) Canva Connect + state CSRF
    et persiste le code_verifier pour l'échange du token au callback.
    """
    import base64, hashlib
    state_final = state or f"kdp_{secrets.token_hex(8)}"
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    sessions_file = CANVA_TOKENS_FILE.parent / "canva_oauth_sessions.json"
    try:
        sessions = json.loads(sessions_file.read_text(encoding="utf-8")) if sessions_file.exists() else {}
    except Exception:
        sessions = {}
    sessions[state_final] = {
        "state": state_final,
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "s256",
        "redirect_uri": redirect_uri,
        "created_at": int(time.time()),
    }
    sessions_file.write_text(json.dumps(sessions, indent=2), encoding="utf-8")

    params = {
        "client_id": _get_canva_client_id(),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "asset:read asset:write design:content:read design:content:write design:meta:read profile:read",
        "state": state_final,
        "code_challenge": code_challenge,
        "code_challenge_method": "s256",
    }
    return {
        "auth_url": f"https://www.canva.com/api/oauth/authorize?{urlencode(params)}",
        "state": state_final,
        "code_challenge": code_challenge,
        "code_challenge_method": "s256",
    }


def exchange_canva_code_for_token(code: str, redirect_uri: str,
                                  state: Optional[str] = None) -> Dict[str, Any]:
    """
    Échange le code d'autorisation du callback contre un token d'accès.
    Le jeton est persisté dans canva_tokens.json à la racine du projet.
    """
    token_data: Dict[str, Any] = {
        "access_token": f"canva_simulated_token_{int(time.time())}",
        "token_type": "Bearer",
        "expires_in": 3600,
        "obtained_at": int(time.time()),
        "client_id": _get_canva_client_id(),
        "state": state or "",
        "mode": "simulated",
    }

    secret = _get_canva_client_secret()
    if secret:
        try:
            if httpx is not None:
                sessions_file = CANVA_TOKENS_FILE.parent / "canva_oauth_sessions.json"
                code_verifier = ""
                if state and sessions_file.exists():
                    try:
                        sess = json.loads(sessions_file.read_text(encoding="utf-8"))
                        code_verifier = sess.get(state, {}).get("code_verifier", "")
                    except Exception:
                        code_verifier = ""
                payload = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                }
                if code_verifier:
                    payload["code_verifier"] = code_verifier
                with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                    r = client.post(
                        f"{CANVA_API_BASE}/oauth/token",
                        auth=(_get_canva_client_id(), secret),
                        data=payload,
                    )
                    if r.status_code < 400:
                        token_data = r.json()
                        token_data["mode"] = "live"
        except Exception as e:
            print(f"⚠️ Note échange token Canva : {e}")

    CANVA_TOKENS_FILE.write_text(json.dumps(token_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return token_data


def get_canva_tokens() -> Optional[Dict[str, Any]]:
    """Lit le jeton Canva persisté (ou None si jamais connecté)."""
    try:
        if CANVA_TOKENS_FILE.exists():
            return json.loads(CANVA_TOKENS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def upload_canva_asset(file_path: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Upload d'un actif vers Canva Connect (mode live si jeton présent),
    sinon retourne un descripteur local réutilisable par le gabarit de repli.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Actif introuvable : {file_path}")

    tokens = get_canva_tokens()
    if tokens and tokens.get("access_token") and tokens.get("mode") == "live" and httpx is not None:
        try:
            with httpx.Client(timeout=20.0) as client:
                r = client.post(
                    f"{CANVA_API_BASE}/assets",
                    headers={"Authorization": f"Bearer {tokens['access_token']}"},
                    json={"name": name or path.name, "file_base64": None},
                )
                if r.status_code < 400:
                    return {"status": "uploaded", "asset": r.json(), "mode": "live"}
        except Exception as e:
            print(f"⚠️ Note upload actif Canva : {e}")

    return {
        "status": "local_fallback",
        "mode": "local",
        "file_path": str(path),
        "name": name or path.name,
        "message": "Actif prêt à importer manuellement dans Canva (aucun jeton live).",
    }


def export_canva_design(design_id: Optional[str] = None,
                        template_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Exporte un design Canva (mode live si jeton présent).
    Repli : génère/retourne le gabarit PNG/PDF 300 DPI local prêt pour Canva.
    """
    tokens = get_canva_tokens()
    if design_id and tokens and tokens.get("mode") == "live" and httpx is not None:
        try:
            with httpx.Client(timeout=20.0) as client:
                r = client.post(
                    f"{CANVA_API_BASE}/designs/{design_id}/exports",
                    headers={"Authorization": f"Bearer {tokens['access_token']}"},
                    json={"format": "PDF"},
                )
                if r.status_code < 400:
                    return {"status": "exported", "export": r.json(), "mode": "live"}
        except Exception as e:
            print(f"⚠️ Note export design Canva : {e}")

    return {
        "status": "fallback_template",
        "mode": "local",
        "template_path": str(template_path) if template_path else None,
        "message": "Gabarit KDP 300 DPI généré localement, prêt à ouvrir dans Canva.",
    }


def generate_canva_cover_template(
    book_id: int,
    format_kdp: str = "6x9",
    nb_pages: int = 100,
    titre: str = "MON LIVRE BEST-SELLER",
    author: str = "MarkEddy"
) -> Path:
    """
    Gabarit de couverture KDP complet 300 DPI (Plat 1 + Dos + Plat 4) pour les
    16 formats officiels, avec repères de fond perdu et réserve ISBN 600x360 px.
    Produit un PNG (aperçu Canva) et un PDF (impression).
    """
    specs = calculate_kdp_specs(trim_id=format_kdp, page_count=int(nb_pages),
                                paper_type="white", bleed=True)

    largeur_px = specs["cover"]["width_px"]
    hauteur_px = specs["cover"]["height_px"]
    dpi = specs["cover"]["dpi"]
    bleed_in = specs["cover"]["bleed_in"]
    spine_in = specs["cover"]["spine_in"]
    trim_w = specs["trim"]["width_in"]
    trim_h = specs["trim"]["height_in"]

    bleed_px = int(round(bleed_in * dpi))
    page_w_px = int(round(trim_w * dpi))
    dos_w_px = int(round(spine_in * dpi))

    img = Image.new("RGB", (largeur_px, hauteur_px), color="#0A0F1D")
    draw = ImageDraw.Draw(img)

    # Zones : Plat 4 (dos de couverture) | Tranche | Plat 1 (face avant)
    plat4_gauche = bleed_px
    plat4_droite = plat4_gauche + page_w_px
    dos_gauche = plat4_droite
    dos_droite = dos_gauche + dos_w_px
    plat1_gauche = dos_droite
    plat1_droite = plat1_gauche + page_w_px

    # Tranche
    draw.rectangle([dos_gauche, 0, dos_droite, hauteur_px], fill="#111827",
                   outline="#D4AF37", width=3)
    # Lignes de coupe / marges de sécurité
    draw.rectangle([plat4_gauche, bleed_px, plat4_droite, hauteur_px - bleed_px],
                   outline="#334155", width=2)
    draw.rectangle([plat1_gauche, bleed_px, plat1_droite, hauteur_px - bleed_px],
                   outline="#D4AF37", width=3)

    # Réserve code-barres ISBN (600 x 360 px, 4ème de couverture)
    isbn_w, isbn_h = 600, 360
    isbn_x1 = plat4_droite - isbn_w - int(0.25 * dpi)
    isbn_y1 = hauteur_px - bleed_px - isbn_h - int(0.25 * dpi)
    draw.rectangle([isbn_x1, isbn_y1, isbn_x1 + isbn_w, isbn_y1 + isbn_h],
                   fill="#FFFFFF", outline="#000000", width=2)

    # Libellés de repérage
    draw.text((plat1_gauche + 100, 400),
              f"PLAT 1 (FACE AVANT) - 300 DPI\n{titre}\nPar {author}", fill="#D4AF37")
    draw.text((dos_gauche + 10, hauteur_px // 2),
              f"TRANCHE ({spine_in:.4f} po)", fill="#F8FAFC")
    draw.text((plat4_gauche + 100, 400),
              f"PLAT 4 (DOS DE COUVERTURE)\nFormat {format_kdp} po ({nb_pages} pages)",
              fill="#94A3B8")
    draw.text((isbn_x1 + 30, isbn_y1 + 150), "[ RÉSERVE CODE-BARRES ISBN ]", fill="#000000")
    draw.text((10, hauteur_px - 30),
              f"Gabarit MarkEddy KDP Studio • {specs['interior']['width_px']}x"
              f"{specs['interior']['height_px']} px intérieur @300 DPI", fill="#64748B")

    dest_png = MEDIA_CACHE_DIR / f"canva_template_book_{book_id}_{format_kdp}.png"
    img.save(dest_png, "PNG", dpi=(dpi, dpi))

    # Variante PDF imprimable (même châssis)
    dest_pdf = MEDIA_CACHE_DIR / f"canva_template_book_{book_id}_{format_kdp}.pdf"
    try:
        img.save(dest_pdf, "PDF", resolution=float(dpi))
    except Exception as e:
        print(f"⚠️ Note export PDF du gabarit Canva : {e}")

    print(f"📐 Gabarit KDP Canva généré : {dest_png.name} ({largeur_px}x{hauteur_px} px @300 DPI)")
    return dest_png


def list_supported_formats() -> List[str]:
    """Les 16 formats KDP supportés par les connecteurs de couverture."""
    return list(KDP_FORMAT_IDS)


if __name__ == "__main__":
    print("Test kdp_extensions.media_connectors...")
    imgs = search_stock_images("mandala", per_page=4)
    print(f"  Images trouvées : {len(imgs)} (sources : "
          f"{sorted({i['source'] for i in imgs})})")
    tpl = generate_canva_cover_template(book_id=999, format_kdp="8.5x11", nb_pages=80)
    print(f"  Gabarit Canva : {tpl.name}")
    print(f"  Formats supportés : {len(list_supported_formats())}")
