import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv(override=True)

app = FastAPI(
    title="API Espace IA - Hub d'Automatisation",
    description="Interface de communication multi-fournisseurs (Gemini / Groq) pour n8n, Hermes et vos automatisations",
    version="1.1.0"
)

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
    """Appel à l'API Google Gemini 1.5 Flash."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    prompt = f"Rédige une analyse technique sur : '{req.sujet}' pour le contexte suivant : {req.piece}."
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
    
    response = requests.post(url, headers=headers, json=payload, timeout=45)
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur API Google Gemini ({response.status_code}) : {response.text}"
        )
    
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=500, detail="Gemini n'a retourné aucun candidat.")
    
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts or "text" not in parts[0]:
        raise HTTPException(status_code=500, detail="Gemini a renvoyé une réponse vide.")
        
    return parts[0]["text"]

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
            detail=f"Erreur API Groq ({response.status_code}) : {response.text}"
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
def generate_content(req: AIRequest):
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
def create_kdp_blueprint(req: KDPBlueprintRequest):
    """Génère l'architecture complète d'un livre KDP non-fiction (10 chapitres x 5 sections)."""
    from kdp_architect import concevoir_livre_kdp, sauvegarder_blueprint
    try:
        data = concevoir_livre_kdp(req.niche, req.public_cible)
        if req.output_file:
            sauvegarder_blueprint(data, req.output_file)
        return {
            "status": "success",
            "titre": data.get("titre"),
            "sous_titre": data.get("sous_titre"),
            "blueprint": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la conception du blueprint KDP : {e}")

@app.post("/kdp/format")
def format_kdp_book(req: KDPFormatRequest):
    """Formate le livre au standard Amazon KDP 6x9 pouces (HTML, Markdown et description Amazon)."""
    from kdp_formatter import formater_projet_complet
    try:
        formater_projet_complet(draft_file=req.draft_file, blueprint_file=req.blueprint_file)
        return {
            "status": "success",
            "message": "Fichiers KDP générés avec succès",
            "livrables": [
                "livre_kdp_6x9.html",
                "manuscrit_complet.md",
                "amazon_description.html"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du formatage KDP : {e}")

