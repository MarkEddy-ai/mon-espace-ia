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

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
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


class ColoringSheetRequest(BaseModel):
    theme: Optional[str] = Field("animaux_mignons", description="Thème de coloriage (enfants ou adultes)")
    index: Optional[int] = Field(1, ge=1, le=200, description="Numéro d'index de la planche")
    age_group: Optional[str] = Field("4-8", description="Tranche d'âge cible (ex: 4-6, 4-8, 6-8, adultes)")
    format_kdp: Optional[str] = Field("8.5x11", description="Format KDP de la planche")


class ColoringPackRequest(BaseModel):
    theme: Optional[str] = Field("animaux_mignons", description="Thème de coloriage")
    nb_sheets: Optional[int] = Field(10, ge=1, le=60, description="Nombre de planches à générer")
    age_group: Optional[str] = Field("4-8", description="Tranche d'âge cible")
    format_kdp: Optional[str] = Field("8.5x11", description="Format KDP")


class AnalyzeBestsellersRequest(BaseModel):
    """Requête de l'Agent 0 (intelligence marchande & autopsie best-sellers)."""
    niche: str = Field(..., min_length=2, description="Niche / thématique à analyser")
    cible: str = Field("Lecteurs exigeants cherchant des résultats concrets", description="Public cible")
    marketplace: str = Field("fr", description="fr | com | uk")
    use_ai: bool = Field(True, description="Utiliser Gemini si la clé est disponible")


class EditorialFrontMatterRequest(BaseModel):
    niche: Optional[str] = Field("Finances Personnelles", description="Niche du livre")
    title: Optional[str] = Field(None, description="Titre principal")
    subtitle: Optional[str] = Field(None, description="Sous-titre")
    author: Optional[str] = Field("MarkEddy", description="Nom d'auteur")
    publisher: Optional[str] = Field("MarkEddy Éditions", description="Maison d'édition")
    isbn: Optional[str] = Field(None, description="Numéro ISBN-13")
    format_output: Optional[str] = Field("markdown", description="'markdown' ou 'html'")


class EditorialBackMatterRequest(BaseModel):
    niche: Optional[str] = Field("Finances Personnelles", description="Niche du livre")
    title: Optional[str] = Field(None, description="Titre principal")
    author: Optional[str] = Field("MarkEddy", description="Nom d'auteur")
    publisher: Optional[str] = Field("MarkEddy Éditions", description="Maison d'édition")
    format_output: Optional[str] = Field("markdown", description="'markdown' ou 'html'")


class AssembleBookRequest(BaseModel):
    body_content: str = Field(..., description="Corps principal du manuscrit")
    niche: Optional[str] = Field("Finances Personnelles", description="Niche du livre")
    title: Optional[str] = Field("Livre KDP", description="Titre du livre")
    author: Optional[str] = Field("MarkEddy", description="Nom d'auteur")
    format_output: Optional[str] = Field("markdown", description="'markdown' ou 'html'")


class LayoutCompileRequest(BaseModel):
    content: str = Field(..., description="Contenu texte ou HTML du livre")
    niche: Optional[str] = Field("Finances", description="Niche du livre")
    title: Optional[str] = Field("Livre KDP", description="Titre du livre")
    author: Optional[str] = Field("MarkEddy Éditions", description="Nom d'auteur")
    format_id: Optional[str] = Field("6x9", description="Format de coupe KDP")
    page_count: Optional[int] = Field(150, ge=1, le=8000, description="Nombre de pages estimé")
    bleed: Optional[bool] = Field(False, description="Fond perdu 0.125 po")


class LayoutAuditRequest(BaseModel):
    html_content: str = Field(..., description="Code HTML complet à auditer")


class CoverGeometryRequest(BaseModel):
    trim_id: Optional[str] = Field("6x9", description="Format de coupe KDP (ex: 6x9, 8.5x11)")
    page_count: Optional[int] = Field(150, ge=1, le=8000, description="Nombre de pages de l'ouvrage")
    paper_type: Optional[str] = Field("white", description="white | cream | color_standard | color_premium")
    bleed: Optional[float] = Field(0.125, ge=0.0, le=1.0, description="Fond perdu en pouces (défaut: 0.125)")
    dpi: Optional[int] = Field(300, ge=72, le=600, description="Résolution d'impression (défaut: 300 DPI)")


class PuzzleCollectionRequest(BaseModel):
    book_title: str = "Grand Livre de Puzzles, Mots & Logique"
    theme: str = "general"
    age_group: str = "6-9"
    puzzle_types: Optional[List[str]] = None
    puzzles_per_type: int = Field(default=2, ge=1, le=20)
    custom_words: Optional[List[str]] = None
    secret_phrase: str = "BRAVO TU AS REUSSI"
    seed: int = 123
    language: str = Field(default="fr", description="Langue des puzzles (en, fr, es, de, ar)")


class SeoAuditKeywordsRequest(BaseModel):
    slots: List[str] = Field(default_factory=list, description="Les 7 slots de mots-clés backend")
    language: str = Field(default="fr", description="Langue cible (en, fr, es, de, ar)")
    title: str = Field(default="", description="Titre du livre pour détecter les doublons")
    subtitle: str = Field(default="", description="Sous-titre du livre")


class SeoOptimizeKeywordsRequest(BaseModel):
    title: str = Field(..., description="Titre du livre")
    subtitle: str = Field(default="", description="Sous-titre")
    niche: str = Field(default="Finances", description="Niche ou thématique")
    language: str = Field(default="fr", description="Langue cible (en, fr, es, de, ar)")
    target_audience: str = Field(default="", description="Public visé")


class MultilingualComplianceRequest(BaseModel):
    html_content: str = Field(..., description="Contenu HTML complet du livre")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées du livre")
    language: str = Field(default="fr", description="Langue (en, fr, es, de, ar)")
    format_id: str = Field(default="6x9", description="Format KDP")
    page_count: int = Field(default=150, description="Nombre de pages")
    cover_type: str = Field(default="paperback", description="Type de couverture (paperback / ebook)")


class ComplianceAuditRequest(BaseModel):
    title: str = Field(..., description="Titre du livre")
    subtitle: str = Field(default="", description="Sous-titre")
    author: str = Field(default="MarkEddy", description="Nom d'auteur")
    keywords: Optional[List[str]] = Field(default=None, description="Mots-clés A9")
    page_count: int = Field(default=24, ge=1, le=8000, description="Nombre de pages")
    format_id: str = Field(default="6x9", description="Format KDP")
    paper_type: str = Field(default="white", description="Type de papier (white, cream, color_standard, color_premium)")
    content_text_or_html: Optional[str] = Field(default=None, description="Contenu texte ou HTML")
    has_copyright: bool = Field(default=True, description="Mention copyright présente")
    has_disclaimer: bool = Field(default=True, description="Clause de non-responsabilité présente")
    has_author_bio: bool = Field(default=True, description="Biographie auteur présente")
    has_colophon: bool = Field(default=True, description="Colophon / achevé d'imprimer présent")
    cover_specs: Optional[Dict[str, Any]] = Field(default=None, description="Spécifications de couverture")
    project_type: str = Field(default="text", description="Type de projet (text, coloring_book, puzzle)")
    binding: str = Field(default="paperback", description="Type de reliure (paperback, hardcover)")


class KdpExportPackageRequest(BaseModel):
    book_id: str = "default_book"
    title: str = "Grand Guide KDP"
    author: str = "MarkEddy"
    subtitle: str = "Méthode Pas-à-Pas & Exercices Concrets"
    project_type: str = "text"
    format_id: str = "6x9"
    paper_type: str = "white"
    initial_pages: int = Field(default=12, ge=1, le=1000)
    html_content: Optional[str] = None
    raw_markdown: Optional[str] = None
    puzzle_config: Optional[Dict[str, Any]] = None
    coloring_config: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None
    niche: str = "general"
    description_html: Optional[str] = None
    target_audience: str = "Tous publics"
    enforce_24_pages: bool = True


class SocialTrendRequest(BaseModel):
    niche: str = Field("Finances Personnelles", description="Niche ou thématique du livre")
    language: str = Field("fr", description="fr | en")


class DeepSourcesRequest(BaseModel):
    topic: str = Field("Finances Personnelles", description="Sujet ou niche de l'ouvrage")
    chapter_outline: List[str] = Field(default_factory=lambda: [
        "1. Les Fondations et le Rapport Psychologique à l'Argent",
        "2. Le Cadre Opératoire : Budget Sans Privation",
        "3. Stratégies d'Investissement Passif et Bourse"
    ], description="Liste des titres de chapitres")
    language: str = Field("fr", description="fr | en")


class VerifyHumanizeRequest(BaseModel):
    text: str = Field(..., description="Texte du manuscrit ou de section à humaniser")
    author_voice: str = Field("expert_pedagogue", description="expert_pedagogue | praticien_terrain | storyteller")
    research_pack: Optional[Dict[str, Any]] = Field(None, description="Dossier de recherche éventuel pour la bibliographie")


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

    @router.get("/api/coloring/themes", summary="Liste des thèmes de coloriage disponibles (enfants & adultes)")
    def api_liste_themes_coloriage():
        from kdp_extensions.coloring_generator import list_coloring_themes
        return JSONResponse(content={"status": "success", "themes": list_coloring_themes()})

    @router.post("/api/coloring/generate-sheet", summary="Génère une planche de coloriage vectorielle haute précision")
    def api_generer_planche_coloriage(req: ColoringSheetRequest):
        from kdp_extensions.coloring_generator import generate_coloring_sheet
        try:
            planche = generate_coloring_sheet(
                theme=req.theme or "animaux_mignons",
                index=req.index or 1,
                age_group=req.age_group or "4-8",
                format_kdp=req.format_kdp or "8.5x11",
            )
            return JSONResponse(content={"status": "success", "sheet": planche})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Échec de génération de la planche : {e}")

    @router.post("/api/coloring/generate-pack", summary="Génère un pack complet de planches de coloriage")
    def api_generer_pack_coloriage(req: ColoringPackRequest):
        from kdp_extensions.coloring_generator import generate_coloring_pack
        try:
            pack = generate_coloring_pack(
                theme=req.theme or "animaux_mignons",
                nb_sheets=req.nb_sheets or 10,
                age_group=req.age_group or "4-8",
                format_kdp=req.format_kdp or "8.5x11",
            )
            return JSONResponse(content={"status": "success", "pack": pack})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Échec de génération du pack : {e}")

    # ------------------------------------------------------------------
    # 9. AGENT 0 — INTELLIGENCE MARCHÉ & AUTOPSIE BEST-SELLERS
    # ------------------------------------------------------------------
    @router.post("/api/research/analyze-bestsellers",
                 summary="Agent 0 : signaux Google/Amazon + faiblesses best-sellers")
    def api_analyser_bestsellers(req: AnalyzeBestsellersRequest):
        """Analyse concurrentielle utilisée pour pré-remplir titre/SEO et le blueprint."""
        from kdp_extensions.pipeline_bridge import prepare_competitive_context

        niche = (req.niche or "").strip()
        if len(niche) < 2:
            raise HTTPException(status_code=422, detail="La niche doit contenir au moins 2 caractères.")
        marketplace = (req.marketplace or "fr").strip().lower()
        if marketplace not in ("fr", "com", "uk"):
            raise HTTPException(status_code=422, detail="marketplace acceptées : fr, com, uk")

        try:
            contexte = prepare_competitive_context(
                niche=niche,
                cible=req.cible,
                marketplace=marketplace,
                output_dir=None,
                use_ai=bool(req.use_ai),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Échec Agent 0 : {e}")

        return JSONResponse(content={
            "status": "success",
            "report": contexte["report"],
            "report_path": contexte["report_path"],
            "recommended_title": contexte["recommended_title"],
            "recommended_subtitle_seo": contexte["recommended_subtitle_seo"],
            "backend_keywords_7": contexte["backend_keywords_7"],
            "design_directives": contexte["design_directives"],
            "editorial_directive_block": contexte["editorial_directive_block"],
        })

    # ------------------------------------------------------------------
    # 10. CONNECTEUR GOOGLE FONTS (catalogue curé hors-ligne en repli)
    # ------------------------------------------------------------------
    @router.get("/api/fonts/search", summary="Recherche de polices Google Fonts curées/KDP")
    def api_rechercher_polices(
        query: str = Query("", description="Recherche (ex : enfant, editorial, Fredoka)"),
        category: Optional[str] = Query(None, description="serif | sans-serif | display | handwriting | monospace"),
        sort: str = Query("popularity", description="Tri Google Fonts API"),
        limit: int = Query(12, ge=1, le=50),
    ):
        from kdp_extensions.fonts_connector import search_google_fonts

        try:
            resultat = search_google_fonts(query=query, category=category, sort=sort, limit=limit)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Échec connecteur polices : {e}")
        return JSONResponse(content={"status": "success", **resultat})

    # ------------------------------------------------------------------
    # 11. JOURNAL DES WEBHOOKS (audit n8n / Hermes)
    # ------------------------------------------------------------------
    @router.get("/api/webhooks/logs", summary="Journal d'audit des webhooks émis")
    def api_journal_webhooks(
        limit: int = Query(50, ge=1, le=500),
        current_user: Optional[Dict[str, Any]] = Depends(dependance),
    ):
        from kdp_extensions.webhooks import WEBHOOK_LOG_FILE

        entrees: List[Dict[str, Any]] = []
        try:
            if WEBHOOK_LOG_FILE.exists():
                lignes = WEBHOOK_LOG_FILE.read_text(encoding="utf-8").splitlines()
                for ligne in lignes[-limit:]:
                    try:
                        entrees.append(json.loads(ligne))
                    except Exception:
                        continue
        except Exception:
            entrees = []
        entrees.reverse()
        return JSONResponse(content={
            "status": "success",
            "total": len(entrees),
            "events": entrees,
        })

    # ------------------------------------------------------------------
    # 12. PAIRINGS TYPOGRAPHIQUES ÉDITORIAUX & GOOGLE FONTS
    # ------------------------------------------------------------------
    @router.get("/api/fonts/pairings", summary="Collection des 7 pairings éditoriaux de prestige")
    def api_liste_pairings():
        from kdp_extensions.fonts_connector import list_editorial_pairings
        return JSONResponse(content={"status": "success", "pairings": list_editorial_pairings()})

    @router.get("/api/fonts/recommend-pairing", summary="Recommande le pairing typographique adapté à une niche")
    def api_recommander_pairing(
        niche: str = Query("Finances", description="Niche ou thématique du livre"),
        cible: Optional[str] = Query(None, description="Public cible"),
    ):
        from kdp_extensions.fonts_connector import recommend_font_pairing
        pairing = recommend_font_pairing(niche, cible)
        return JSONResponse(content={"status": "success", "pairing": pairing})

    # ------------------------------------------------------------------
    # 13. VEILLE TRI-PLATEFORME (Google Trends + Amazon KDP + Pinterest)
    # ------------------------------------------------------------------
    @router.get("/api/trends/market", summary="Veille tri-plateforme en direct (Google, Amazon, Pinterest)")
    def api_veille_tri_plateforme(
        niche: str = Query(..., min_length=2, description="Niche ou thématique du livre"),
        cible: Optional[str] = Query(None, description="Public visé"),
        marketplace: str = Query("fr", description="fr | com | uk | de"),
    ):
        from kdp_extensions.market_trends_agent import analyze_market_trends
        try:
            rapport = analyze_market_trends(niche=niche, target_audience=cible, marketplace=marketplace)
            return JSONResponse(content={"status": "success", "trends": rapport})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la veille de marché : {e}")

    # ------------------------------------------------------------------
    # 14. FRONT-MATTER & BACK-MATTER ÉDITORIAL
    # ------------------------------------------------------------------
    @router.post("/api/editorial/front-matter", summary="Générateur de Front-Matter d'édition KDP")
    def api_editorial_front_matter(req: EditorialFrontMatterRequest):
        from kdp_extensions.editorial_structure import (
            get_default_editorial_metadata,
            generate_front_matter_markdown,
            generate_front_matter_html,
        )
        meta = get_default_editorial_metadata(
            niche=req.niche or "Finances",
            title=req.title,
            author=req.author or "MarkEddy",
            publisher=req.publisher or "MarkEddy Éditions",
            isbn=req.isbn,
        )
        if req.subtitle:
            meta["subtitle"] = req.subtitle

        if (req.format_output or "markdown").lower() == "html":
            rendu = generate_front_matter_html(meta)
        else:
            rendu = generate_front_matter_markdown(meta)

        return JSONResponse(content={
            "status": "success",
            "format": req.format_output,
            "content": rendu,
            "metadata": meta,
        })

    @router.post("/api/editorial/back-matter", summary="Générateur de Back-Matter d'édition KDP")
    def api_editorial_back_matter(req: EditorialBackMatterRequest):
        from kdp_extensions.editorial_structure import (
            get_default_editorial_metadata,
            generate_back_matter_markdown,
            generate_back_matter_html,
        )
        meta = get_default_editorial_metadata(
            niche=req.niche or "Finances",
            title=req.title,
            author=req.author or "MarkEddy",
            publisher=req.publisher or "MarkEddy Éditions",
        )
        if (req.format_output or "markdown").lower() == "html":
            rendu = generate_back_matter_html(meta)
        else:
            rendu = generate_back_matter_markdown(meta)

        return JSONResponse(content={
            "status": "success",
            "format": req.format_output,
            "content": rendu,
            "metadata": meta,
        })

    @router.post("/api/editorial/assemble", summary="Assemble Front-Matter + Manuscrit + Back-Matter")
    def api_editorial_assemble(req: AssembleBookRequest):
        from kdp_extensions.editorial_structure import (
            get_default_editorial_metadata,
            assemble_complete_book,
        )
        meta = get_default_editorial_metadata(
            niche=req.niche or "Finances",
            title=req.title,
            author=req.author or "MarkEddy",
        )
        livre_complet = assemble_complete_book(
            body_content=req.body_content,
            metadata=meta,
            output_format=req.format_output or "markdown",
        )
        return JSONResponse(content={
            "status": "success",
            "format": req.format_output,
            "full_book": livre_complet,
        })

    # ------------------------------------------------------------------
    # 15. MOTEUR CSS PAGED MEDIA PRO & AUDIT
    # ------------------------------------------------------------------
    @router.post("/api/layout/paged-css", summary="Génère la feuille de style CSS Paged Media W3C pour un format")
    def api_paged_css(
        format_id: str = Query("6x9", description="Format KDP"),
        page_count: int = Query(150, ge=1, le=8000),
        bleed: bool = Query(False),
        niche: str = Query("Business"),
    ):
        from kdp_extensions.layout_engine_pro import generate_paged_media_css
        from kdp_extensions.fonts_connector import recommend_font_pairing
        pairing = recommend_font_pairing(niche)
        css = generate_paged_media_css(
            format_id=format_id,
            page_count=page_count,
            bleed=bleed,
            font_pairing=pairing,
        )
        return Response(content=css, media_type="text/css")

    @router.post("/api/layout/compile", summary="Compile le document complet en HTML Paged Media")
    def api_paged_compile(req: LayoutCompileRequest):
        from kdp_extensions.layout_engine_pro import compile_paged_interior_html
        from kdp_extensions.editorial_structure import get_default_editorial_metadata
        meta = get_default_editorial_metadata(
            niche=req.niche or "Finances",
            title=req.title,
            author=req.author or "MarkEddy Éditions",
        )
        html = compile_paged_interior_html(
            content=req.content,
            metadata=meta,
            format_id=req.format_id or "6x9",
            page_count=req.page_count or 150,
            bleed=req.bleed or False,
        )
        return HTMLResponse(content=html)

    @router.post("/api/layout/audit", summary="Audit prépresse de conformité CSS Paged Media")
    def api_paged_audit(req: LayoutAuditRequest):
        from kdp_extensions.layout_engine_pro import audit_paged_css_compliance
        rapport = audit_paged_css_compliance(req.html_content)
        return JSONResponse(content={"status": "success", "audit": rapport})

    # ------------------------------------------------------------------
    # 16. CALCULATEUR COUVERTURE & GABARIT SVG VECTORIEL
    # ------------------------------------------------------------------
    @router.get("/api/cover/calculator", summary="Calcul au micron de la géométrie de couverture KDP")
    def api_cover_calculator(
        trim_id: str = Query("6x9", description="Format de coupe KDP (16 formats)"),
        page_count: int = Query(150, ge=1, le=8000),
        paper_type: str = Query("white", description="white | cream | color_standard | color_premium"),
        bleed: float = Query(0.125, ge=0.0, le=1.0),
        dpi: int = Query(300, ge=72, le=600),
    ):
        from kdp_extensions.cover_calculator import calculate_cover_dimensions
        try:
            specs = calculate_cover_dimensions(
                trim_id=trim_id,
                page_count=page_count,
                paper_type=paper_type,
                bleed=bleed,
                dpi=dpi,
            )
            return JSONResponse(content={"status": "success", "specs": specs})
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    @router.get("/api/cover/template-svg", summary="Génère un gabarit de couverture interactif SVG 300 DPI")
    def api_cover_template_svg(
        trim_id: str = Query("6x9", description="Format de coupe KDP"),
        page_count: int = Query(150, ge=1, le=8000),
        paper_type: str = Query("white"),
        title: str = Query("TITRE DU LIVRE"),
        author: str = Query("NOM DE L'AUTEUR"),
        subtitle: str = Query("SOUS-TITRE ÉDITORIAL"),
    ):
        from kdp_extensions.cover_calculator import calculate_cover_dimensions, generate_cover_template_svg
        try:
            specs = calculate_cover_dimensions(
                trim_id=trim_id,
                page_count=page_count,
                paper_type=paper_type,
            )
            svg = generate_cover_template_svg(
                specs_or_trim=specs,
                book_title=title,
                author_name=author,
                subtitle=subtitle,
            )
            return Response(content=svg, media_type="image/svg+xml")
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        # ==============================================================================
        # PUZZLES & JEUX DE MOTS (8 FORMATS + SOLUTIONNAIRE)
        # ==============================================================================

    @router.post("/api/puzzles/generate-collection", summary="Génère une collection multi-jeux de puzzles et mots")
    @router.post("/api/puzzles/collection", summary="Alias collection puzzles")
    def api_generate_puzzle_collection(req: PuzzleCollectionRequest):
        from kdp_extensions.puzzle_generator import generate_full_puzzle_collection
        return generate_full_puzzle_collection(
            book_title=req.book_title,
            theme=req.theme,
            age_group=req.age_group,
            puzzle_types=req.puzzle_types,
            puzzles_per_type=req.puzzles_per_type,
            custom_words=req.custom_words,
            secret_phrase=req.secret_phrase,
            seed=req.seed,
        )

    @router.post("/api/puzzles/export-pdf", summary="Exporte la collection de puzzles en PDF prépresse")
    def api_export_puzzle_pdf(req: PuzzleCollectionRequest):
        import re
        from pathlib import Path
        from datetime import datetime
        from kdp_extensions.puzzle_generator import generate_full_puzzle_collection

        res = generate_full_puzzle_collection(
            book_title=req.book_title,
            theme=req.theme,
            age_group=req.age_group,
            puzzle_types=req.puzzle_types,
            puzzles_per_type=req.puzzles_per_type,
            custom_words=req.custom_words,
            secret_phrase=req.secret_phrase,
            seed=req.seed,
        )

        out_dir = BASE_DIR / "output_puzzles"
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", req.book_title.strip().lower()).strip("_") or "puzzles"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = out_dir / f"{slug}_{stamp}.html"
        pdf_path = out_dir / f"{slug}_{stamp}.pdf"
        html_path.write_text(res["html"], encoding="utf-8")

        pdf_generated = False
        pdf_error = None
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch()
                except Exception:
                    browser = p.chromium.launch(channel="msedge")
                page = browser.new_page()
                page.set_content(res["html"], wait_until="load")
                page.pdf(
                    path=str(pdf_path),
                    format="Letter",
                    print_background=True,
                    margin={"top": "0.6in", "bottom": "0.6in", "left": "0.6in", "right": "0.6in"},
                )
                browser.close()
            pdf_generated = pdf_path.exists()
        except Exception as exc:
            pdf_error = str(exc)

        return {
            "status": "success",
            "book_title": res["book_title"],
            "total_puzzles": res["total_puzzles"],
            "html_path": str(html_path),
            "pdf_path": str(pdf_path) if pdf_generated else None,
            "pdf_generated": pdf_generated,
            "pdf_error": pdf_error,
        }

    # ==============================================================================
    # EXPORT PACK KDP 1-CLIC & TÉLÉCHARGEMENT ZIP (AVEC RÈGLE PRÉPRESSE 24 PAGES)
    # ==============================================================================

    @router.post("/api/kdp/export-package", summary="Génère un package KDP 1-clic complet (PDF, SVG, Métadonnées A9, Manifeste et ZIP)")
    def api_kdp_export_package(req: KdpExportPackageRequest):
        try:
            from kdp_extensions.kdp_export_orchestrator import build_kdp_export_package
            res = build_kdp_export_package(
                book_id=req.book_id,
                title=req.title,
                author=req.author,
                subtitle=req.subtitle,
                project_type=req.project_type,
                format_id=req.format_id,
                paper_type=req.paper_type,
                initial_pages=req.initial_pages,
                html_content=req.html_content,
                raw_markdown=req.raw_markdown,
                puzzle_config=req.puzzle_config,
                coloring_config=req.coloring_config,
                keywords=req.keywords,
                niche=req.niche,
                description_html=req.description_html,
                target_audience=req.target_audience,
                enforce_24_pages=req.enforce_24_pages,
            )
            return res
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur d'export KDP : {exc}")

    @router.get("/api/kdp/download-package/{package_name}", summary="Télécharge l'archive ZIP du package KDP 1-clic")
    def api_kdp_download_package(package_name: str):
        # Sécurité anti-traversal
        clean_name = Path(package_name).name
        if clean_name != package_name or ".." in package_name or "/" in package_name or "\\" in package_name:
            raise HTTPException(status_code=400, detail="Nom de package invalide")
        if not package_name.lower().endswith(".zip"):
            raise HTTPException(status_code=400, detail="Seules les archives .zip sont autorisées")

        exports_dir = BASE_DIR / "exports"
        target_file = (exports_dir / package_name).resolve()
        if not target_file.is_file() or not str(target_file).startswith(str(exports_dir.resolve())):
            raise HTTPException(status_code=404, detail="Archive KDP introuvable")

        return FileResponse(
            path=str(target_file),
            media_type="application/zip",
            filename=package_name,
        )

    # ==============================================================================
    # CHAÎNE D'INTELLIGENCE ÉDITORIALE (AGENTS 1, 2 & 3)
    # ==============================================================================

    @router.post("/api/research/social-trends", summary="Agent 1 : Veille Tendances Sociales, Questions réelles & 3 Concepts de Livres")
    def api_research_social_trends(req: SocialTrendRequest):
        try:
            from kdp_extensions.social_trend_hunter import harvest_market_ideas
            return harvest_market_ideas(niche=req.niche, language=req.language)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur Agent Veille Sociale : {exc}")

    @router.post("/api/research/deep-sources", summary="Agent 2 : Recherche Documentaire, Académique & Presse (Evidence Pack)")
    def api_research_deep_sources(req: DeepSourcesRequest):
        try:
            from kdp_extensions.deep_research_agent import build_chapter_evidence_pack
            return build_chapter_evidence_pack(
                topic=req.topic,
                chapter_outline=req.chapter_outline,
                language=req.language,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur Agent Recherche Documentaire : {exc}")

    @router.post("/api/editorial/verify-humanize", summary="Agent 3 : Synthèse Fact-Checking, Élimination des Tics IA & Humanisation")
    def api_editorial_verify_humanize(req: VerifyHumanizeRequest):
        try:
            from kdp_extensions.editorial_humanizer_agent import humanize_manuscript, synthesize_and_verify
            verification_summary = None
            if req.research_pack:
                verification_summary = synthesize_and_verify(req.research_pack)
            humanized_res = humanize_manuscript(
                text=req.text,
                author_voice=req.author_voice,
                research_pack=req.research_pack,
            )
            return {
                **humanized_res,
                "verification_audit": verification_summary,
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur Agent Humanisation & Fact-Checking : {exc}")

    # ==============================================================================
    # MULTILINGUAL I18N, SEO A9 & SUPERVISEUR DE CONFORMITÉ (5 LANGUES)
    # ==============================================================================

    @router.get("/api/i18n/languages", summary="Registre des 5 langues supportées (EN, FR, ES, DE, AR)")
    def api_i18n_languages():
        from kdp_extensions.i18n_config import get_supported_languages, LANGUAGE_CONFIGS
        return {
            "status": "success",
            "supported_codes": ["fr", "en", "es", "de", "ar"],
            "languages": LANGUAGE_CONFIGS,
        }

    @router.get("/api/i18n/language/{code}", summary="Détails de configuration pour une langue")
    def api_i18n_language_detail(code: str):
        from kdp_extensions.i18n_config import get_language_config, normalize_language
        try:
            clean_code = normalize_language(code)
            return {
                "status": "success",
                "language": get_language_config(clean_code),
            }
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.post("/api/seo/audit-keywords", summary="Agent SEO A9 : Audit chirurgical des 7 slots (UTF-8 50 octets & mots interdits)")
    def api_seo_audit_keywords(req: SeoAuditKeywordsRequest):
        try:
            from kdp_extensions.seo_a9_agent import audit_7_slots_a9
            return audit_7_slots_a9(
                slots=req.slots,
                language=req.language,
                title=req.title,
                subtitle=req.subtitle,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur d'audit SEO A9 : {exc}")

    @router.post("/api/seo/optimize-keywords", summary="Agent SEO A9 : Génération des 7 slots d'intention stratégique (Règle 05)")
    def api_seo_optimize_keywords(req: SeoOptimizeKeywordsRequest):
        try:
            from kdp_extensions.seo_a9_agent import optimize_7_slots_a9
            return optimize_7_slots_a9(
                title=req.title,
                subtitle=req.subtitle,
                niche=req.niche,
                language=req.language,
                target_audience=req.target_audience,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur d'optimisation SEO A9 : {exc}")

    @router.post("/api/compliance/audit-multilingual", summary="Superviseur : Audit de conformité KDP multilingue, RTL & alerte Arabe")
    def api_compliance_audit_multilingual(req: MultilingualComplianceRequest):
        try:
            from kdp_extensions.kdp_compliance_supervisor import audit_multilingual_kdp_project
            return audit_multilingual_kdp_project(
                html_content=req.html_content,
                metadata=req.metadata,
                language=req.language,
                format_id=req.format_id,
                page_count=req.page_count,
                cover_type=req.cover_type,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur du superviseur de conformité : {exc}")

    @router.post("/api/compliance/audit", summary="Agent 4 : Contrôle Lois KDP, Anti-Anonymat & Porte Qualité")
    def api_compliance_audit(req: ComplianceAuditRequest):
        try:
            from kdp_extensions.kdp_compliance_supervisor import audit_kdp_compliance
            return audit_kdp_compliance(
                title=req.title,
                subtitle=req.subtitle,
                author=req.author,
                keywords=req.keywords,
                page_count=req.page_count,
                format_id=req.format_id,
                paper_type=req.paper_type,
                content_text_or_html=req.content_text_or_html,
                has_copyright=req.has_copyright,
                has_disclaimer=req.has_disclaimer,
                has_author_bio=req.has_author_bio,
                has_colophon=req.has_colophon,
                cover_specs=req.cover_specs,
                project_type=req.project_type,
                binding=req.binding,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erreur du superviseur de conformité : {exc}")

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
    "PuzzleCollectionRequest",
    "KdpExportPackageRequest",
    "SocialTrendRequest",
    "DeepSourcesRequest",
    "VerifyHumanizeRequest",
    "SeoAuditKeywordsRequest",
    "SeoOptimizeKeywordsRequest",
    "MultilingualComplianceRequest",
    "ComplianceAuditRequest",
]
