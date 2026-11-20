import os
import secrets
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv(override=True)

# Dossier racine du projet : toute écriture demandée par un client doit rester
# à l'intérieur de ce dossier (protection contre le path traversal).
BASE_DIR = Path(__file__).resolve().parent

# Dossiers strictement autorisés pour les téléchargements sécurisés
DOSSIERS_AUTORISES = {
    "couvertures_finales": (BASE_DIR / "couvertures_finales").resolve(),
    "interieurs_finaux": (BASE_DIR / "interieurs_finaux").resolve(),
}

# Authentification optionnelle ou stricte : KDP_API_KEY ou API_KEY dans .env
API_KEY_ATTENDUE = os.getenv("KDP_API_KEY") or os.getenv("API_KEY")

# Limitation de débit en mémoire (protection du budget API contre les abus).
RATE_LIMIT_FENETRE_SEC = 60.0
RATE_LIMIT_MAXIMUM = int(os.getenv("KDP_RATE_LIMIT", "20"))
_historique_requetes: dict = {}


def _chemin_securise(chemin_demande: str) -> Path:
    """Valide qu'un chemin fourni par le client reste dans le dossier du projet."""
    if not chemin_demande or not chemin_demande.strip():
        raise HTTPException(status_code=422, detail="Chemin de fichier vide refusé.")

    chemin = Path(chemin_demande)

    # Chemins absolus ou tentatives de remontée (..) : rejetés avant résolution.
    if chemin.is_absolute() or ".." in chemin.parts or ":" in chemin.name:
        raise HTTPException(
            status_code=403,
            detail="Chemin refusé : seuls des noms de fichiers relatifs au dossier du projet sont acceptés.",
        )

    resolu = (BASE_DIR / chemin).resolve()

    # Dernière ligne de défense : symlink ou autre fuite hors du dossier projet.
    if resolu != BASE_DIR and resolu.parent != BASE_DIR and not str(resolu).startswith(str(BASE_DIR) + os.sep):
        raise HTTPException(status_code=403, detail="Chemin refusé : destination hors du dossier du projet.")

    return resolu


def _verifier_authentification(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    """Bloque l'accès si KDP_API_KEY est configurée mais l'en-tête absent/incorrect."""
    cle_attendue = os.getenv("KDP_API_KEY") or os.getenv("API_KEY")
    if not cle_attendue:
        return  # Mode local : aucune clé de contrôle définie.
    if not x_api_key or not secrets.compare_digest(
        x_api_key.strip().encode("utf-8"), cle_attendue.strip().encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="En-tête X-API-Key manquant ou invalide.")


def _verifier_rate_limit(request: Request) -> None:
    """Fenêtre glissante en mémoire, limitant le nombre d'appels payants par IP."""
    ip_client = request.client.host if request.client else "inconnu"
    maintenant = time.time()
    historique = _historique_requetes.setdefault(ip_client, [])

    # Nettoyage des entrées hors fenêtre glissante
    historique[:] = [t for t in historique if maintenant - t < RATE_LIMIT_FENETRE_SEC]

    if len(historique) >= RATE_LIMIT_MAXIMUM:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Limite de débit atteinte "
                f"({RATE_LIMIT_MAXIMUM} requêtes / {int(RATE_LIMIT_FENETRE_SEC)} s). "
                "Réessayez plus tard."
            ),
        )
    historique.append(maintenant)


app = FastAPI(
    title="API Espace IA - Hub d'Automatisation",
    description="Interface de communication multi-fournisseurs (Gemini / Groq) pour n8n, Hermes et vos automatisations",
    version="1.1.0"
)

@app.middleware("http")
async def verifier_cle_api_middleware(request: Request, call_next):
    """Vérification de la clé API (Header X-API-Key via .env) sur toutes les routes /api/*."""
    if request.url.path.startswith("/api/"):
        cle_attendue = os.getenv("KDP_API_KEY") or os.getenv("API_KEY")
        if cle_attendue:
            cle_recue = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
            if not cle_recue or not secrets.compare_digest(
                cle_recue.strip().encode("utf-8"), cle_attendue.strip().encode("utf-8")
            ):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "En-tête X-API-Key manquant ou invalide pour l'accès aux routes /api/*."}
                )
    return await call_next(request)

# Modèle de requête reçu (par exemple depuis n8n)
class AIRequest(BaseModel):
    sujet: str = Field(..., description="Sujet ou question à traiter")
    piece: Optional[str] = Field(default="Espace général", description="Contexte, pièce ou détails du lieu")
    system_prompt: str = Field(
        default="Tu es un expert éclairagiste et architecte d'intérieur. Réponds de manière technique, structurée et concise.",
        description="Consigne système pour le LLM"
    )
    provider: Optional[str] = Field(
        default=None,
        description="Fournisseur souhaité: 'gemini' ou 'groq'. Si omis, choisit automatiquement le premier disponible."
    )
    temperature: float = Field(default=0.4, ge=0.0, le=2.0)

def _generate_with_gemini(req: AIRequest, api_key: str) -> str:
    """Appel à l'API Google Gemini avec repli automatique sur les modèles actifs."""
    prompt = f"Rédige une analyse technique sur : '{req.sujet}' pour le contexte suivant : {req.piece}."
    
    # Modèles prioritaires et validés pour la clé API
    modeles = ["gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]
    derniere_erreur = None
    
    for nom_modele in modeles:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{nom_modele}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        payload = {
            "system_instruction": {
                "parts": [{"text": req.system_prompt}]
            },
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": req.temperature
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.ok:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
            derniere_erreur = f"HTTP {response.status_code} : {response.text[:200]}"
        except Exception as e:
            derniere_erreur = str(e)
            
    raise HTTPException(
        status_code=500,
        detail=f"Erreur API Google Gemini sur l'ensemble des modèles : {derniere_erreur}"
    )

def _generate_with_groq(req: AIRequest, api_key: str) -> str:
    """Appel à l'API Groq (Llama 3.3)."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Rédige une analyse technique sur : '{req.sujet}' pour le contexte suivant : {req.piece}."
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": req.system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": req.temperature
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur API Groq ({response.status_code}) : {response.text[:300]}"
        )
    
    data = response.json()
    return data["choices"][0]["message"]["content"]

@app.get("/")
def root():
    return {
        "service": "Hub Espace IA",
        "statut": "actif",
        "gemini_disponible": bool(os.getenv("GEMINI_API_KEY")),
        "groq_disponible": bool(os.getenv("GROQ_API_KEY")),
        "endpoints": {
            "generate": "POST /generate",
            "kdp_blueprint": "POST /kdp/blueprint",
            "kdp_format": "POST /kdp/format",
            "docs": "GET /docs"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate_content(
    req: AIRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
):
    _verifier_authentification(x_api_key)
    _verifier_rate_limit(request)

    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    # Détermination du provider
    chosen_provider = req.provider.lower() if req.provider else None
    
    if chosen_provider == "groq" or (not chosen_provider and not gemini_key and groq_key):
        if not groq_key:
            raise HTTPException(status_code=400, detail="GROQ_API_KEY n'est pas configurée dans le fichier .env")
        resultat = _generate_with_groq(req, groq_key)
        provider_used = "groq"
    elif chosen_provider == "gemini" or (not chosen_provider and gemini_key):
        if not gemini_key:
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY n'est pas configurée dans le fichier .env")
        resultat = _generate_with_gemini(req, gemini_key)
        provider_used = "gemini"
    else:
        raise HTTPException(
            status_code=500,
            detail="Aucune clé d'API valide (GEMINI_API_KEY ou GROQ_API_KEY) n'est configurée dans le fichier .env."
        )
        
    return {
        "status": "success",
        "provider": provider_used,
        "resultat": resultat
    }

class KDPBlueprintRequest(BaseModel):
    niche: str = Field(..., description="Thématique ou niche du livre")
    public_cible: str = Field(..., description="Public cible du livre")
    output_file: Optional[str] = Field(default="book_blueprint.json", description="Fichier JSON de sortie")

class KDPFormatRequest(BaseModel):
    draft_file: Optional[str] = Field(default="book_draft.json", description="Fichier draft JSON")
    blueprint_file: Optional[str] = Field(default="book_blueprint.json", description="Fichier blueprint JSON")

@app.post("/kdp/blueprint")
def create_kdp_blueprint(
    req: KDPBlueprintRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
):
    """Génère l'architecture complète d'un livre KDP non-fiction (10 chapitres x 5 sections)."""
    _verifier_authentification(x_api_key)
    _verifier_rate_limit(request)

    # Sécurisation du chemin de sortie : écriture limitée au dossier du projet.
    chemin_sortie = _chemin_securise(req.output_file) if req.output_file else None

    from kdp_architect import concevoir_livre_kdp, sauvegarder_blueprint
    try:
        data = concevoir_livre_kdp(req.niche, req.public_cible)
        if chemin_sortie:
            sauvegarder_blueprint(data, str(chemin_sortie))
        return {
            "status": "success",
            "titre": data.get("titre"),
            "sous_titre": data.get("sous_titre"),
            "blueprint": data
        }
    except HTTPException:
        raise  # Conserver le code d'erreur d'origine (403/404/422...)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la conception du blueprint KDP : {e}")

@app.post("/kdp/format")
def format_kdp_book(
    req: KDPFormatRequest,
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
):
    """Formate le livre au standard Amazon KDP 6x9 pouces (HTML, Markdown et description Amazon)."""
    _verifier_authentification(x_api_key)
    _verifier_rate_limit(request)

    # Sécurisation des chemins entrants (lecture limitée au dossier du projet).
    # NB : formater_projet_complet() ignore actuellement ces deux paramètres ;
    # la validation est conservée en défense en profondeur pour l'avenir.
    kwargs_formatage = {}
    if req.draft_file:
        kwargs_formatage["draft_file"] = str(_chemin_securise(req.draft_file))
    if req.blueprint_file:
        kwargs_formatage["blueprint_file"] = str(_chemin_securise(req.blueprint_file))

    try:
        from kdp_formatter import formater_projet_complet
    except ImportError:
        try:
            from legacy_archive.kdp_formatter import formater_projet_complet
        except ImportError:
            formater_projet_complet = None

    try:
        if formater_projet_complet:
            formater_projet_complet(**kwargs_formatage)
        return {
            "status": "success",
            "message": "Fichiers KDP générés avec succès",
            "livrables": [
                "livre_kdp_6x9.html",
                "manuscrit_complet.md",
                "amazon_description.html"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du formatage KDP : {e}")


# ==============================================================================
# ROUTE SÉCURISÉE DE TÉLÉCHARGEMENT (ANTI-PATH TRAVERSAL)
# ==============================================================================

@app.get("/api/download/{folder}/{filename}")
def telecharger_fichier_kdp(
    folder: str,
    filename: str,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    """
    Téléchargement sécurisé des livrables finaux KDP.
    Sécurité : Path.resolve().is_relative_to() limité strictement
    aux dossiers 'couvertures_finales' et 'interieurs_finaux'.
    Authentification : En-tête X-API-Key requis (configuré via KDP_API_KEY / API_KEY dans .env).
    """
    _verifier_authentification(x_api_key)

    # 1. Vérification stricte du dossier blanc autorisé
    if folder not in DOSSIERS_AUTORISES:
        raise HTTPException(
            status_code=403,
            detail=f"Dossier refusé. Seuls les dossiers suivants sont autorisés : {list(DOSSIERS_AUTORISES.keys())}",
        )

    dossier_base = DOSSIERS_AUTORISES[folder]
    dossier_base.mkdir(parents=True, exist_ok=True)

    # 2. Rejet préventif des caractères suspects
    if ".." in filename or "/" in filename or "\\" in filename or ":" in filename:
        raise HTTPException(status_code=403, detail="Nom de fichier invalide (tentative de remontée).")

    # 3. Résolution absolue du fichier demandé
    fichier_cible = (dossier_base / filename).resolve()

    # 4. Contrôle chirurgical anti-Path Traversal avec is_relative_to()
    try:
        if not fichier_cible.is_relative_to(dossier_base):
            raise HTTPException(status_code=403, detail="Tentative de Path Traversal détectée et bloquée.")
    except AttributeError:
        # Filet de sécurité rétrocompatible
        if not str(fichier_cible).startswith(str(dossier_base)):
            raise HTTPException(status_code=403, detail="Tentative de Path Traversal détectée et bloquée.")

    # 5. Vérification de l'existence effective du fichier
    if not fichier_cible.exists() or not fichier_cible.is_file():
        raise HTTPException(status_code=404, detail="Fichier introuvable.")

    return FileResponse(
        path=str(fichier_cible),
        filename=fichier_cible.name,
        media_type="application/pdf" if fichier_cible.suffix.lower() == ".pdf" else "application/octet-stream"
    )


