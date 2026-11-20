"""
kdp_extensions/router.py - APIRouter des extensions KDP monté sur app_studio.

Ce module expose l'ensemble des routes d'extension du studio MarkEddy :

  GET  /api/kdp/formats          : Les 16 formats officiels Amazon KDP
  POST /api/kdp/calculate        : Calcul des specs 300 DPI (dos, marges, gabarit)
  GET  /api/media/search         : Recherche Unsplash / Pixabay (+ catalogue curé)
  GET  /api/canva/auth           : OAuth 2.0 + PKCE S256 (state + code_verifier)
  GET  /api/canva/callback       : Échange du code (Basic + code_verifier) -> canva_tokens.json
  GET  /api/canva/status         : État de la connexion Canva, profil & clés configurées
  POST /api/canva/export-cover   : Upload PNG 300 DPI / création design Canva / fallback local
  POST /api/coloring/generate    : Production d'un livre de coloriage (16 formats)

Montage dans app_studio.py (AUCUNE route existante n'est supprimée ni modifiée) :

    from kdp_extensions.router import construire_router
    app.include_router(construire_router(auth_dependency=get_current_user))

Le routeur est monté AVANT les décorateurs @app.* historiques : sur les trois
chemins strictement identiques (/api/kdp/formats, /api/media/search,
/api/canva/callback) l'implémentation du routeur prend la main avec un
comportement équivalent (mêmes clés de réponse, même exigence d'authentification
JWT sur /api/media/search, repli automatique sur le flux historique pour le
callback non-PKCE). Les fonctions historiques restent définies dans app_studio
et sont toujours appelables directement (test_media_and_coloring.py).

Modules mobilisés : kdp_dimensions, media_connectors, coloring_book_engine.

Exécution obligatoire via : .\\.venv\\Scripts\\python.exe
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import secrets
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from kdp_extensions.kdp_dimensions import (
    KDP_FORMAT_IDS,
    PAPER_SPINE_COEFFS,
    calculate_kdp_specs,
    list_kdp_formats,
)
from kdp_extensions import media_connectors as mc

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONSTANTES CANVA CONNECT API (OAuth 2.0 + PKCE S256)
# ==============================================================================

CANVA_AUTHORIZE_ENDPOINT = "https://www.canva.com/api/oauth/authorize"
CANVA_TOKEN_ENDPOINT = "https://api.canva.com/rest/v1/oauth/token"
CANVA_API_BASE = "https://api.canva.com/rest/v1"

# Redirect URI imposé par le cahier des charges du studio
CANVA_REDIRECT_URI_DEFAUT = "http://127.0.0.1:8000/api/canva/callback"
CANVA_CLIENT_ID_DEFAUT = "kdp_studio_canva_client"
CANVA_SCOPES = "asset:read asset:write design:content:read design:content:write design:meta:read design:meta:write brandtemplate:content:read brandtemplate:meta:read profile:read"

CANVA_TOKENS_FILE = BASE_DIR / "canva_tokens.json"
CANVA_SESSIONS_FILE = BASE_DIR / "canva_oauth_sessions.json"
GITIGNORE_FILE = BASE_DIR / ".gitignore"

# Secrets ne doivent JAMAIS être versionnés
ENTREES_GITIGNORE = ("canva_tokens.json", "canva_oauth_sessions.json")

# Durée de validité d'une session OAuth locale (state + code_verifier)
DUREE_SESSION_OAUTH_S = 900


# ==============================================================================
# UTILITAIRES GÉNÉRIQUES (fichiers JSON, .env, .gitignore)
# ==============================================================================

def _env(cle: str, alternative: str = "") -> str:
    """Lit une variable d'environnement (avec repli sur une clé alternative)."""
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / ".env", override=False)
    except Exception:
        pass
    return (os.getenv(cle) or os.getenv(alternative) or "").strip()


def _lire_json(chemin: Path, defaut: Any) -> Any:
    try:
        if chemin.exists():
            return json.loads(chemin.read_text(encoding="utf-8"))
    except Exception:
        pass
    return defaut


def _ecrire_json(chemin: Path, donnees: Any) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(donnees, indent=2, ensure_ascii=False), encoding="utf-8")


def _client_id_canva() -> str:
    return _env("CANVA_CLIENT_ID") or CANVA_CLIENT_ID_DEFAUT


def _client_secret_canva() -> str:
    return _env("CANVA_CLIENT_SECRET")


def _redirect_uri_canva() -> str:
    """Redirect URI : CANVA_REDIRECT_URI dans le .env, sinon l'URL officielle du studio."""
    return (_env("CANVA_REDIRECT_URI") or CANVA_REDIRECT_URI_DEFAUT).rstrip("/")


def assurer_gitignore() -> Dict[str, bool]:
    """
    Garantit que canva_tokens.json (et canva_oauth_sessions.json) figurent bien
    dans .gitignore. Ajoute les entrées manquantes puisque les jetons OAuth
    ne doivent jamais être commités.
    """
    contenu = ""
    try:
        if GITIGNORE_FILE.exists():
            contenu = GITIGNORE_FILE.read_text(encoding="utf-8")
    except Exception:
        contenu = ""

    lignes_existantes = {l.strip() for l in contenu.splitlines()}
    manquantes = [e for e in ENTREES_GITIGNORE if e not in lignes_existantes]

    if manquantes:
        try:
            prefixe = "" if (not contenu or contenu.endswith("\n")) else "\n"
            with open(GITIGNORE_FILE, "a", encoding="utf-8") as f:
                f.write(f"{prefixe}# Secrets OAuth Canva Connect (jamais versionnés)\n")
                f.write("\n".join(manquantes) + "\n")
            print(f"🔒 .gitignore complété : {', '.join(manquantes)}")
        except Exception as e:
            print(f"⚠️ Impossible de compléter .gitignore : {e}")

    lignes_finales = {l.strip() for l in GITIGNORE_FILE.read_text(encoding="utf-8").splitlines()} \
        if GITIGNORE_FILE.exists() else lignes_existantes
    return {e: e in lignes_finales for e in ENTREES_GITIGNORE}


def _chemin_local_securise(chemin_relatif: str) -> Path:
    """Contrôle anti-Path Traversal (mêmes règles que app_studio._chemin_securise)."""
    if not chemin_relatif or not str(chemin_relatif).strip():
        raise HTTPException(status_code=422, detail="Chemin de fichier vide.")

    p = Path(chemin_relatif)
    if p.is_absolute() or ".." in p.parts or ":" in p.name:
        raise HTTPException(status_code=403, detail="Chemin non autorisé (tentative de Path Traversal).")

    resolu = (BASE_DIR / p).resolve()
    try:
        if not resolu.is_relative_to(BASE_DIR):
            raise HTTPException(status_code=403, detail="Accès refusé : fichier hors du répertoire de travail.")
    except AttributeError:  # Python < 3.9
        if not str(resolu).startswith(str(BASE_DIR) + "/"):
            raise HTTPException(status_code=403, detail="Accès refusé : fichier hors du répertoire de travail.")
    return resolu


# ==============================================================================
# SESSIONS OAUTH PKCE (state + code_verifier persistés sur disque)
# ==============================================================================

def _sessions_valides() -> Dict[str, Any]:
    sessions = _lire_json(CANVA_SESSIONS_FILE, {})
    if not isinstance(sessions, dict):
        return {}
    maintenant = int(time.time())
    return {
        state: s for state, s in sessions.items()
        if isinstance(s, dict)
        and (int(s.get("created_at", 0)) + DUREE_SESSION_OAUTH_S) >= maintenant
    }


def _creer_session_oauth() -> Dict[str, str]:
    """
    Génère le state CSRF (anti-forgery) et le code_verifier PKCE,
    puis dérive le code_challenge S256 (SHA-256 base64url sans padding).
    """
    code_verifier = secrets.token_urlsafe(64)  # 86 caractères (RFC 7636 : 43 à 128)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    state = secrets.token_urlsafe(24)

    session = {
        "state": state,
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "redirect_uri": _redirect_uri_canva(),
        "created_at": int(time.time()),
    }
    sessions = _sessions_valides()
    sessions[state] = session
    _ecrire_json(CANVA_SESSIONS_FILE, sessions)
    return session


def _consommer_session_oauth(state: Optional[str]) -> Optional[Dict[str, Any]]:
    """Valide le state reçu (CSRF) et le supprime (usage unique)."""
    if not state:
        return None
    sessions = _sessions_valides()
    session = sessions.pop(state, None)
    _ecrire_json(CANVA_SESSIONS_FILE, sessions)
    return session


def _url_autorisation_canva(session: Dict[str, Any]) -> str:
    """URL https://www.canva.com/api/oauth/authorize avec PKCE S256."""
    params = {
        "client_id": _client_id_canva(),
        "redirect_uri": session.get("redirect_uri") or _redirect_uri_canva(),
        "response_type": "code",
        "scope": CANVA_SCOPES,
        "state": session["state"],
        "code_challenge": session["code_challenge"],
        "code_challenge_method": "S256",
    }
    return f"{CANVA_AUTHORIZE_ENDPOINT}?{urlencode(params)}"


# ==============================================================================
# APPELS CANVA CONNECT API (échange PKCE, profil, asset, design, export)
# ==============================================================================

def _echanger_code_pkce(code: str, code_verifier: str, redirect_uri: str) -> Dict[str, Any]:
    """
    POST https://api.canva.com/rest/v1/oauth/token
    - En-tête : Authorization: Basic base64(client_id:client_secret)
    - Corps   : grant_type=authorization_code, code, code_verifier, redirect_uri
    """
    try:
        import httpx
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("Le module httpx est requis pour l'échange OAuth Canva.") from e

    client_secret = _client_secret_canva()
    if not client_secret:
        raise RuntimeError(
            "CANVA_CLIENT_SECRET absent du .env : impossible d'échanger le code. "
            "Renseignez CANVA_CLIENT_ID et CANVA_CLIENT_SECRET puis relancez la connexion."
        )

    identifiants = base64.b64encode(
        f"{_client_id_canva()}:{client_secret}".encode("utf-8")
    ).decode("ascii")

    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        resp = client.post(
            CANVA_TOKEN_ENDPOINT,
            headers={
                "Authorization": f"Basic {identifiants}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
            },
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"Canva a refusé l'échange du code (HTTP {resp.status_code}) : {resp.text[:300]}"
            )
        return resp.json()


def _profil_canva(access_token: str) -> Optional[Dict[str, Any]]:
    """GET /rest/v1/users/me - profil du compte Canva connecté (best effort)."""
    try:
        import httpx
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(
                f"{CANVA_API_BASE}/users/me",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            )
        if resp.status_code < 400:
            data = resp.json()
            profil = data.get("user") or data
            return profil if isinstance(profil, dict) else None
        print(f"⚠️ Profil Canva indisponible (HTTP {resp.status_code}).")
    except Exception as e:
        print(f"⚠️ Profil Canva : {e}")
    return None


def _uploader_asset_canva(chemin_png: Path, nom: str, jeton: str) -> Optional[Dict[str, Any]]:
    """
    POST /rest/v1/asset-uploads (Content-Type: application/octet-stream +
    Asset-Upload-Metadata) -> identifiant d'actif Canva.
    """
    try:
        import httpx
        octets = chemin_png.read_bytes()
        metadata = json.dumps(
            {"name_base64": base64.b64encode(nom.encode("utf-8")).decode("ascii")},
            ensure_ascii=False,
        )
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(
                f"{CANVA_API_BASE}/asset-uploads",
                headers={
                    "Authorization": f"Bearer {jeton}",
                    "Content-Type": "application/octet-stream",
                    "Asset-Upload-Metadata": metadata,
                },
                content=octets,
            )
        if resp.status_code >= 400:
            print(f"⚠️ Upload actif Canva refusé (HTTP {resp.status_code}) : {resp.text[:200]}")
            return None
        data = resp.json()
        actif = data.get("asset") or data
        return actif if isinstance(actif, dict) else None
    except Exception as e:
        print(f"⚠️ Upload actif Canva : {e}")
        return None


def _creer_design_canva(asset_id: Optional[str], titre: str,
                        larg_px: int, haut_px: int, jeton: str) -> Optional[Dict[str, Any]]:
    """POST /rest/v1/designs - création de design (best effort, 3 variantes tolérantes)."""
    if not asset_id:
        return None
    try:
        import httpx
    except ImportError:  # pragma: no cover
        return None

    variantes = [
        {
            "type": "type_and_asset",
            "design_type": {"type": "custom", "width": int(larg_px), "height": int(haut_px)},
            "asset_id": asset_id,
            "title": titre,
        },
        {
            "type": "type_and_asset",
            "design_type": {"type": "preset", "name": "doc"},
            "asset_id": asset_id,
            "title": titre,
        },
        {"asset_id": asset_id, "title": titre},
    ]

    try:
        with httpx.Client(timeout=30.0) as client:
            for payload in variantes:
                resp = client.post(
                    f"{CANVA_API_BASE}/designs",
                    headers={"Authorization": f"Bearer {jeton}", "Content-Type": "application/json"},
                    json=payload,
                )
                if resp.status_code < 400:
                    data = resp.json()
                    design = data.get("design") or data
                    if isinstance(design, dict) and design.get("id"):
                        return design
                else:
                    print(f"⚠️ Création design Canva refusée (HTTP {resp.status_code}) pour {payload.get('type', 'nu')}.")
    except Exception as e:
        print(f"⚠️ Création design Canva : {e}")
    return None


def _exporter_design_canva(design_id: str, jeton: str, format_export: str = "PDF") -> Optional[Dict[str, Any]]:
    """POST /rest/v1/designs/{id}/exports - export du design (best effort)."""
    try:
        import httpx
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{CANVA_API_BASE}/designs/{design_id}/exports",
                headers={"Authorization": f"Bearer {jeton}", "Content-Type": "application/json"},
                json={"format": format_export},
            )
        if resp.status_code < 400:
            data = resp.json()
            return data.get("export") or data if isinstance(data, dict) else None
        print(f"⚠️ Export design Canva refusé (HTTP {resp.status_code}).")
    except Exception as e:
        print(f"⚠️ Export design Canva : {e}")
    return None


# ==============================================================================
# LECTURE / ÉCRITURE DES JETONS (canva_tokens.json)
# ==============================================================================

def lire_jetons_canva() -> Optional[Dict[str, Any]]:
    """Lit les jetons persistés (None si jamais connecté)."""
    try:
        if CANVA_TOKENS_FILE.exists():
            donnees = json.loads(CANVA_TOKENS_FILE.read_text(encoding="utf-8"))
            return donnees if isinstance(donnees, dict) else None
    except Exception:
        return None
    return None


def _sauver_jetons_canva(jetons: Dict[str, Any]) -> None:
    assurer_gitignore()
    _ecrire_json(CANVA_TOKENS_FILE, jetons)


def _cle_configuree(cle: str, alternative: str = "") -> bool:
    return bool(_env(cle, alternative))


# ==============================================================================
# PAGES HTML DU FLUX OAUTH (retour navigateur)
# ==============================================================================

def _page_canva_html(titre: str, lignes: List[str], succes: bool,
                     delai_s: int = 3) -> HTMLResponse:
    couleur = "#34D399" if succes else "#FB7185"
    corps = "".join(f"<li style='margin:0.45rem 0'>{html.escape(l)}</li>" for l in lignes)
    status = 200 if succes else 400
    return HTMLResponse(
        f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titre)}</title></head>
<body style="background:#0A0F1D; color:#F8FAFC; font-family:'Segoe UI',sans-serif; text-align:center; padding:4rem 1.5rem;">
  <div style="max-width:560px; margin:0 auto; background:#1E293B; border:1px solid #D4AF37; padding:2rem; border-radius:12px;">
    <div style="font-size:2.4rem;">{"🎨" if succes else "⚠️"}</div>
    <h2 style="color:{couleur}; margin:0.6rem 0 1rem;">{html.escape(titre)}</h2>
    <ul style="list-style:none; padding:0; margin:0 0 1.5rem; color:#94A3B8; font-size:14px; text-align:left;">
      {corps}
    </ul>
    <a href="/" style="display:inline-block; background:#D4AF37; color:#0A0F1D; text-decoration:none; font-weight:bold; padding:0.75rem 1.5rem; border-radius:8px;">
      Retourner au Studio
    </a>
  </div>
  <script>setTimeout(function() {{ window.location.href = '/'; }}, {int(delai_s) * 1000});</script>
</body>
</html>""",
        status_code=status,
    )


def _veut_json(request: Request, format_requete: Optional[str]) -> bool:
    if (format_requete or "").lower() == "json":
        return True
    accept = (request.headers.get("accept") or "").lower()
    return "application/json" in accept and "text/html" not in accept


# ==============================================================================
# MODÈLES DE DONNÉES PYDANTIC
# ==============================================================================

class KdpCalculateRequest(BaseModel):
    """Requête de calcul des spécifications d'impression KDP."""
    format_kdp: Optional[str] = Field("6x9", description="Format KDP (16 formats officiels)")
    trim_id: Optional[str] = Field(None, description="Alias de format_kdp (référentiel kdp_dimensions)")
    page_count: Optional[int] = Field(100, ge=1, le=8000, description="Nombre de pages de l'intérieur")
    nb_pages: Optional[int] = Field(None, ge=1, le=8000, description="Alias de page_count")
    paper_type: Optional[str] = Field("white", description="white | cream | color_standard | color_premium")
    bleed: Optional[bool] = Field(True, description="Fond perdu 0.125 pouce")


class CanvaExportCoverRequest(BaseModel):
    """Requête d'export de couverture 300 DPI vers Canva."""
    book_id: Optional[int] = Field(None, description="Identifiant du livre (0 = gabarit libre)")
    titre: Optional[str] = Field("MON LIVRE BEST-SELLER", description="Titre imprimé sur le gabarit")
    format_kdp: Optional[str] = Field("6x9", description="Format KDP de la couverture")
    nb_pages: Optional[int] = Field(100, ge=1, le=8000, description="Nombre de pages (calcule la tranche)")
    png_path: Optional[str] = Field(None, description="Chemin local d'un PNG 300 DPI déjà généré")
    design_id: Optional[str] = Field(None, description="Design Canva existant à réutiliser")


class ColoringGenerateRequest(BaseModel):
    """Requête de génération rapide d'un livre de coloriage."""
    book_id: Optional[int] = Field(None, description="Identifiant libre (généré si absent)")
    titre: Optional[str] = Field(None, description="Titre du livre (auto si vide)")
    sous_titre: Optional[str] = Field(None, description="Sous-titre (auto si vide)")
    theme: Optional[str] = Field("mandalas", description="mandalas | botanique | animaux | architecture")
    format_kdp: Optional[str] = Field("8.5x11", description="Format KDP (16 formats officiels)")
    nb_illustrations: Optional[int] = Field(6, ge=1, le=60, description="Nombre de planches")
    recto_uniquement: Optional[bool] = Field(True, description="Verso blanc anti-bavure après chaque planche")
    paper_type: Optional[str] = Field("white", description="Type de papier KDP")


# ==============================================================================
# FABRIQUE DU ROUTEUR
# ==============================================================================

def _aucune_auth() -> Optional[Dict[str, Any]]:
    """Dépendance neutre : routeur monté hors app_studio (tests / standalone)."""
    return None


def construire_router(auth_dependency: Optional[Callable[..., Dict[str, Any]]] = None) -> APIRouter:
    """
    Construit l'APIRouter des extensions KDP.

    Parameters
    ----------
    auth_dependency : la dépendance d'authentification JWT de l'hôte
                      (app_studio.get_current_user). Si elle est fournie,
                      GET /api/media/search exige un jeton valide, exactement
                      comme la route historique équivalente.

    Returns
    -------
    APIRouter prêt à être monté via app.include_router(...).
    """
    router = APIRouter(tags=["KDP Extensions"])

    # Dépendance appliquée aux endpoints sensibles (réquise si l'hôte en fournit une)
    dependance = auth_dependency or _aucune_auth

    # ------------------------------------------------------------------
    # 1. RÉFÉRENTIEL DES 16 FORMATS KDP
    # ------------------------------------------------------------------
    @router.get("/api/kdp/formats", summary="Liste des 16 formats officiels Amazon KDP")
    def api_formats_kdp():
        """GET /api/kdp/formats - kdp_extensions.kdp_dimensions.list_kdp_formats()."""
        try:
            formats = list_kdp_formats()
        except Exception:
            formats = [{"id": "6x9", "width_in": 6.0, "height_in": 9.0, "label": '6" × 9" po'}]
        return JSONResponse(content={
            "status": "success",
            "total": len(formats),
            "formats": formats,
            "paper_types": list(PAPER_SPINE_COEFFS.keys()),
            "dpi": 300,
        })

    # ------------------------------------------------------------------
    # 2. CALCUL DES SPÉCIFICATIONS 300 DPI (dos, marges, couverture)
    # ------------------------------------------------------------------
    @router.post("/api/kdp/calculate", summary="Calcule les specs KDP d'un format (dos, marges, 300 DPI)")
    def api_calculer_kdp(req: KdpCalculateRequest):
        """POST /api/kdp/calculate - kdp_extensions.kdp_dimensions.calculate_kdp_specs()."""
        trim = (req.trim_id or req.format_kdp or "6x9").strip()
        pages = int(req.nb_pages or req.page_count or 100)

        try:
            specs = calculate_kdp_specs(
                trim_id=trim,
                page_count=pages,
                paper_type=(req.paper_type or "white").strip(),
                bleed=bool(req.bleed if req.bleed is not None else True),
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        return JSONResponse(content={
            "status": "success",
            "specs": specs,
            "resume": {
                "format": specs["trim_id"],
                "pages": specs["page_count"],
                "papier": specs["paper_type"],
                "dos_po": specs["spine"]["width_in"],
                "dos_mm": specs["spine"]["width_mm"],
                "gutter_po": specs["margins"]["gutter_in"],
                "couverture_px": [specs["cover"]["width_px"], specs["cover"]["height_px"]],
                "interieur_px": [specs["interior"]["width_px"], specs["interior"]["height_px"]],
                "couverture_po": [specs["cover"]["width_in"], specs["cover"]["height_in"]],
                "bleed_po": specs["cover"]["bleed_in"],
            },
        })

    # ------------------------------------------------------------------
    # 3. RECHERCHE MÉDIA (UNSPLASH + PIXABAY + CATALOGUE CURÉ)
    # ------------------------------------------------------------------
    @router.get("/api/media/search", summary="Recherche d'images libres de droits (Unsplash / Pixabay)")
    def api_rechercher_medias(
        query: str = Query("texture", description="Termes de recherche"),
        source: str = Query("all", description="Source : unsplash, pixabay ou all"),
        orientation: str = Query("portrait", description="portrait ou landscape"),
        per_page: int = Query(12, ge=1, le=30),
        current_user: Optional[Dict[str, Any]] = Depends(dependance),
    ):
        """
        GET /api/media/search - kdp_extensions.media_connectors.search_stock_images().
        Repli automatique sur le catalogue curé hors-ligne si les clés API manquent.
        """
        resultats = mc.search_stock_images(
            query=query,
            source=source,
            orientation=orientation,
            per_page=per_page,
        )
        return JSONResponse(content={
            "status": "success",
            "query": query,
            "source": source,
            "total": len(resultats),
            "images": resultats,
        })

    # ------------------------------------------------------------------
    # 4. CONNEXION CANVA : OAUTH 2.0 + PKCE S256
    # ------------------------------------------------------------------
    @router.get("/api/canva/auth", summary="Génère state + PKCE S256 et ouvre l'autorisation Canva")
    def api_canva_auth(
        redirect: bool = Query(False, description="Rediriger immédiatement vers Canva"),
        format_requete: Optional[str] = Query(None, alias="format", description="json pour forcer le JSON"),
    ):
        """
        GET /api/canva/auth
        - Génère un state aléatoire (CSRF) et un code_verifier, dérive le
          code_challenge S256, puis construit l'URL
          https://www.canva.com/api/oauth/authorize pointant sur
          http://127.0.0.1:8000/api/canva/callback.
        - ?redirect=1 -> redirection HTTP 302 vers Canva
        - sinon       -> JSON {auth_url, state, code_challenge, ...}
        """
        session = _creer_session_oauth()
        auth_url = _url_autorisation_canva(session)

        if redirect and (format_requete or "").lower() != "json":
            return RedirectResponse(url=auth_url, status_code=302)

        return JSONResponse(content={
            "status": "success",
            "auth_url": auth_url,
            "authorize_url": auth_url,
            "state": session["state"],
            "code_challenge": session["code_challenge"],
            "code_challenge_method": "S256",
            "redirect_uri": session["redirect_uri"],
            "client_id": _client_id_canva(),
            "token_endpoint": CANVA_TOKEN_ENDPOINT,
            "scopes": CANVA_SCOPES,
        })

    # ------------------------------------------------------------------
    # 5. CALLBACK CANVA : ÉCHANGE DU CODE -> canva_tokens.json
    # ------------------------------------------------------------------
    @router.get("/api/canva/callback", summary="Échange le code Canva et enregistre les jetons")
    def api_canva_callback(
        request: Request,
        code: Optional[str] = Query(None, description="Code d'autorisation renvoyé par Canva"),
        state: Optional[str] = Query(None, description="State CSRF renvoyé par Canva"),
        error: Optional[str] = Query(None),
        error_description: Optional[str] = Query(None),
        format_requete: Optional[str] = Query(None, alias="format", description="json pour une réponse JSON"),
    ):
        """
        GET /api/canva/callback
        1. Vérifie que canva_tokens.json est bien ignoré par git (.gitignore).
        2. Valide le state puis échange le code sur
           https://api.canva.com/rest/v1/oauth/token avec
           Authorization: Basic base64(client_id:client_secret) et code_verifier.
        3. Persiste les jetons (+ profil) dans canva_tokens.json.
        4. Renvoie une page HTML de confirmation (ou du JSON).
        """
        assurer_gitignore()
        en_json = _veut_json(request, format_requete)

        # --- Refus explicite par Canva -------------------------------------
        if error:
            detail = error_description or error
            if en_json:
                return JSONResponse(status_code=400, content={
                    "status": "error", "message": "Autorisation Canva refusée.", "detail": detail,
                })
            return _page_canva_html(
                "Connexion Canva annulée",
                [f"Canva a refusé la demande : {detail}",
                 "Réessayez depuis le bouton « Connecter Canva » du studio."],
                succes=False,
            )

        # --- Code absent ---------------------------------------------------
        if not code:
            if en_json:
                return JSONResponse(status_code=400, content={
                    "status": "error",
                    "message": "Code d'autorisation manquant dans le callback Canva.",
                })
            return _page_canva_html(
                "Callback Canva incomplet",
                ["Aucun paramètre « code » n'a été renvoyé par Canva.",
                 "Relancez la connexion depuis « Connecter Canva »."],
                succes=False,
            )

        # --- Échange PKCE (si la session locale existe), sinon repli historique
        session = _consommer_session_oauth(state)
        redirect_uri = (session or {}).get("redirect_uri") or _redirect_uri_canva()
        jetons: Optional[Dict[str, Any]] = None
        mode_echange = "simulated"
        erreur_echange: Optional[str] = None

        if session:
            try:
                jetons = _echanger_code_pkce(code, session["code_verifier"], redirect_uri)
                mode_echange = "live"
            except Exception as e:
                erreur_echange = str(e)
                print(f"⚠️ Échange PKCE Canva échoué, repli sur le flux historique : {e}")

        if jetons is None:
            # Repli : flux historique de media_connectors (sans code_verifier),
            # conservation totale de la compatibilité avec /api/canva/auth-url.
            try:
                if hasattr(mc, "exchange_canva_code_for_token"):
                    jetons = mc.exchange_canva_code_for_token(code=code, redirect_uri=redirect_uri, state=state)
                else:  # pragma: no cover - rétrocompatibilité
                    jetons = mc.exchange_canva_code(code=code, redirect_uri=redirect_uri)
                mode_echange = jetons.get("mode") or "simulated"
            except Exception as e:
                erreur_echange = erreur_echange or str(e)

        if not jetons or not jetons.get("access_token"):
            message = erreur_echange or "Échange du code impossible."
            if en_json:
                return JSONResponse(status_code=502, content={
                    "status": "error",
                    "message": "Échange du code Canva impossible.",
                    "detail": message,
                })
            return _page_canva_html(
                "Échange Canva impossible",
                [message,
                 "Vérifiez CANVA_CLIENT_ID / CANVA_CLIENT_SECRET dans le .env, puis réessayez."],
                succes=False,
            )

        # --- Enrichissement & persistance ----------------------------------
        now = int(time.time())
        jetons.setdefault("obtained_at", now)
        jetons["mode"] = "live" if mode_echange == "live" else (jetons.get("mode") or "simulated")
        jetons["redirect_uri"] = redirect_uri
        jetons["connected_at"] = now
        jetons["state"] = state or ""
        if erreur_echange:
            jetons["exchange_warning"] = erreur_echange

        if jetons["mode"] == "live":
            profil = _profil_canva(str(jetons["access_token"]))
            if profil:
                jetons["profile"] = profil

        _sauver_jetons_canva(jetons)

        profil = jetons.get("profile") or {}
        nom_profil = (
            profil.get("name")
            or profil.get("email")
            or profil.get("username")
            or (profil.get("id") and f"Canva ID {profil['id']}")
            or None
        )
        ligne_mode = (
            "Mode direct (Canva Connect API) — jetons enregistrés dans canva_tokens.json."
            if jetons["mode"] == "live"
            else "Mode simulation — renseignez CANVA_CLIENT_ID / CANVA_CLIENT_SECRET pour un accès direct."
        )
        lignes = ["Compte Canva connecté à MarkEddy KDP Studio !", ligne_mode]
        if nom_profil:
            lignes.insert(1, f"Profil : {nom_profil}")
        if erreur_echange:
            lignes.append(f"Note technique : {erreur_echange}")

        if en_json:
            return JSONResponse(content={
                "status": "success",
                "message": "Compte Canva connecté.",
                "mode": jetons["mode"],
                "profile": jetons.get("profile"),
                "tokens_file": CANVA_TOKENS_FILE.name,
                "gitignore": assurer_gitignore(),
            })

        return _page_canva_html("Compte Canva Connecté !", lignes, succes=True)

    # ------------------------------------------------------------------
    # 6. STATUT DE LA CONNEXION CANVA
    # ------------------------------------------------------------------
    @router.get("/api/canva/status", summary="Statut Canva (connecté, profil, clés configurées)")
    def api_canva_status():
        """GET /api/canva/status"""
        assurer_gitignore()
        jetons = lire_jetons_canva() or {}
        connecte = bool(jetons.get("access_token"))
        mode = jetons.get("mode") if connecte else None

        profil = jetons.get("profile") or None
        if connecte and mode == "live" and not profil:
            profil = _profil_canva(str(jetons.get("access_token")))
            if profil:
                jetons["profile"] = profil
                _sauver_jetons_canva(jetons)

        cles = {
            "canva_client_id": _cle_configuree("CANVA_CLIENT_ID"),
            "canva_client_secret": _cle_configuree("CANVA_CLIENT_SECRET"),
            "unsplash_access_key": _cle_configuree("UNSPLASH_ACCESS_KEY", "UNSPLASH_CLIENT_ID"),
            "pixabay_api_key": _cle_configuree("PIXABAY_API_KEY"),
        }

        expire_le: Optional[int] = None
        expire_dans_s: Optional[int] = None
        if connecte and jetons.get("expires_in"):
            expire_le = int(jetons.get("obtained_at") or jetons.get("connected_at") or 0) + int(jetons["expires_in"])
            expire_dans_s = max(0, expire_le - int(time.time()))

        return JSONResponse(content={
            "status": "success",
            "connected": connecte,
            "mode": mode,
            "profile": profil,
            "keys_configured": cles,
            "keys_configured_all": all(cles.values()),
            "redirect_uri": _redirect_uri_canva(),
            "authorize_endpoint": CANVA_AUTHORIZE_ENDPOINT,
            "token_endpoint": CANVA_TOKEN_ENDPOINT,
            "scopes": CANVA_SCOPES,
            "tokens_file": CANVA_TOKENS_FILE.name,
            "gitignore": assurer_gitignore(),
            "connected_at": jetons.get("connected_at") or jetons.get("obtained_at"),
            "expires_in": jetons.get("expires_in"),
            "expires_at": expire_le,
            "expires_in_seconds": expire_dans_s,
            "exchange_warning": jetons.get("exchange_warning"),
            "message": (
                f"Connecté en mode {mode}." if connecte
                else "Aucun compte Canva connecté pour le moment."
            ),
        })

    # ------------------------------------------------------------------
    # 7. EXPORT DE COUVERTURE 300 DPI VERS CANVA
    # ------------------------------------------------------------------
    @router.post("/api/canva/export-cover", summary="Upload d'un PNG 300 DPI / design Canva / fallback local")
    def api_exporter_couverture_canva(req: CanvaExportCoverRequest):
        """
        POST /api/canva/export-cover
        - Connecté (jetons live) : upload du PNG 300 DPI vers Canva puis
          création d'un design (et export best effort).
        - Non connecté : génération du gabarit local PNG/PDF 300 DPI
          (Plat 1 + Dos + Plat 4, 16 formats KDP, réserve ISBN) prêt à importer.
        """
        assurer_gitignore()

        format_kdp = (req.format_kdp or "6x9").strip()
        nb_pages = int(req.nb_pages or 100)
        titre = (req.titre or "").strip() or "MON LIVRE BEST-SELLER"
        book_id = int(req.book_id) if req.book_id else 0

        # --- 1. Source PNG 300 DPI ----------------------------------------
        png_source: Optional[Path] = None
        if req.png_path:
            png_source = _chemin_local_securise(req.png_path)
            if not png_source.exists():
                raise HTTPException(status_code=404, detail=f"PNG introuvable : {png_source.name}")
        else:
            try:
                png_source = mc.generate_canva_cover_template(
                    book_id=book_id,
                    format_kdp=format_kdp,
                    nb_pages=nb_pages,
                    titre=titre,
                    author="MarkEddy",
                )
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))

        try:
            specs = calculate_kdp_specs(format_kdp, page_count=nb_pages, bleed=True)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        # --- 2. Connexion Canva -------------------------------------------
        jetons = lire_jetons_canva() or {}
        connecte = bool(
            jetons.get("access_token")
            and jetons.get("mode") == "live"
        )

        actif_info: Optional[Dict[str, Any]] = None
        design_info: Optional[Dict[str, Any]] = None
        export_info: Optional[Dict[str, Any]] = None

        if connecte:
            jeton = str(jetons["access_token"])
            actif_info = _uploader_asset_canva(png_source, titre, jeton)
            design_id = req.design_id
            if not design_id and actif_info and actif_info.get("id"):
                design_info = _creer_design_canva(
                    asset_id=str(actif_info.get("id")),
                    titre=titre,
                    larg_px=specs["cover"]["width_px"],
                    haut_px=specs["cover"]["height_px"],
                    jeton=jeton,
                )
                design_id = (design_info or {}).get("id")
            if design_id:
                export_info = _exporter_design_canva(str(design_id), jeton)
        else:
            # Repli local garanti : gabarit PNG/PDF 300 DPI complet
            export_info = mc.export_canva_design(design_id=None, template_path=str(png_source))

        mode = "live" if connecte and (actif_info or design_info) else "local_fallback"

        return JSONResponse(content={
            "status": "success",
            "mode": mode,
            "connected": connecte,
            "book_id": book_id,
            "format_kdp": specs["trim_id"],
            "nb_pages": nb_pages,
            "cover_px": [specs["cover"]["width_px"], specs["cover"]["height_px"]],
            "spine_in": specs["spine"]["width_in"],
            "png_path": str(png_source.relative_to(BASE_DIR)) if png_source.is_relative_to(BASE_DIR) else str(png_source),
            "template_png": str(png_source),
            "template_url": f"/api/canva/template/{book_id}" if book_id else None,
            "asset": actif_info,
            "design": design_info,
            "export": export_info,
            "message": (
                "PNG 300 DPI uploadé vers Canva Connect API."
                if mode == "live"
                else "Gabarit PNG/PDF 300 DPI généré localement, prêt à importer dans Canva (non connecté)."
            ),
        })

    # ------------------------------------------------------------------
    # 8. GÉNÉRATION RAPIDE D'UN LIVRE DE COLORIAGE
    # ------------------------------------------------------------------
    @router.post("/api/coloring/generate", summary="Génère un livre de coloriage 16 formats (moteur kdp_extensions)")
    def api_generer_coloriage(req: ColoringGenerateRequest):
        """
        POST /api/coloring/generate
        Production synchrone via kdp_extensions.coloring_book_engine
        (planches noir pur 300 DPI, option recto uniquement, PDF Playwright).
        Ne consomme aucun crédit : outil de prévisualisation du studio.
        """
        from kdp_extensions.coloring_book_engine import produire_livre_coloriage

        themes_valides = ("mandalas", "botanique", "animaux", "architecture")
        theme = (req.theme or "mandalas").strip().lower()
        if theme not in themes_valides:
            raise HTTPException(
                status_code=422,
                detail=f"Thème inconnu '{req.theme}'. Thèmes acceptés : {', '.join(themes_valides)}.",
            )

        format_kdp = (req.format_kdp or "8.5x11").strip()
        try:
            normalize = calculate_kdp_specs  # validation format via kdp_dimensions
            normalize(format_kdp, page_count=1)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        book_id = int(req.book_id) if req.book_id else int(time.time()) % 1_000_000
        nb_illustrations = max(1, min(int(req.nb_illustrations or 6), 60))
        titre = (req.titre or "").strip() or f"COLORIAGE ARTISTIQUE : {theme.upper()}"
        sous_titre = (req.sous_titre or "").strip() or (
            f"{nb_illustrations} planches d'art grand format pour apaiser l'esprit"
        )

        try:
            resultat = produire_livre_coloriage(
                book_id=book_id,
                titre=titre,
                sous_titre=sous_titre,
                theme=theme,
                nb_illustrations=nb_illustrations,
                recto_uniquement=bool(req.recto_uniquement if req.recto_uniquement is not None else True),
                format_kdp=format_kdp,
                paper_type=(req.paper_type or "white").strip(),
            )
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Échec de la génération du livre de coloriage : {e}",
            )

        return JSONResponse(content={
            "status": "success",
            "book_id": book_id,
            "message": (
                f"Livre de coloriage '{titre}' généré : {resultat.get('nb_pages')} pages "
                f"au format {resultat.get('format_kdp')}."
            ),
            "result": resultat,
        })

    return router


# Routeur public (sans authentification) réutilisable hors d'app_studio :
# tests, import direct, ou montage sur une autre instance FastAPI.
router = construire_router()


__all__ = [
    "router",
    "construire_router",
    "assurer_gitignore",
    "lire_jetons_canva",
    "CANVA_TOKENS_FILE",
    "CANVA_REDIRECT_URI_DEFAUT",
]
