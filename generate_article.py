import os
import argparse
from datetime import date
import requests
from dotenv import load_dotenv

# Chargement dynamique de la clé d'API
load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERREUR : Aucune clé trouvée dans le fichier .env !")
    exit(1)

# Modèle par défaut (gemini-1.5-flash est stable et rapide)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def generer_article_eclairage(sujet: str, piece: str, model: str = DEFAULT_MODEL) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    system_prompt = (
        "Tu es un expert éclairagiste et rédacteur technique pour un blog d'architecture. "
        "Rédige en Markdown avec des sous-titres clairs (##), des unités précises "
        "(lumens, lux, kelvins) et des conseils pratiques d'implantation. "
        "Ne commence pas par des salutations, livre directement le contenu technique."
    )

    prompt = f"Rédige un guide technique détaillé sur : '{sujet}' pour une {piece}."

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.4
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=45)
    
    if not response.ok:
        print(f"❌ Erreur API Google ({response.status_code}) : {response.text}")
        response.raise_for_status()
        
    data = response.json()
    
    # Extraction sécurisée de la réponse
    candidates = data.get("candidates", [])
    if not candidates:
        feedback = data.get("promptFeedback", {})
        raise RuntimeError(f"Aucune réponse générée par l'IA. Détails : {feedback or data}")
        
    candidate = candidates[0]
    parts = candidate.get("content", {}).get("parts", [])
    if not parts or "text" not in parts[0]:
        finish_reason = candidate.get("finishReason", "INCONNU")
        raise RuntimeError(f"Réponse vide de l'IA (Raison de fin : {finish_reason}).")
        
    return parts[0]["text"]

def sauvegarder_en_markdown(titre: str, contenu: str, slug: str, dossier: str = "articles") -> str:
    aujourdhui = date.today().isoformat()
    
    frontmatter = f"""---
title: "{titre}"
pubDate: {aujourdhui}
description: "Guide technique et règles de calcul pour l'éclairage de votre espace."
tags: ["éclairage", "architecture", "tutoriel"]
---

"""
    if dossier:
        os.makedirs(dossier, exist_ok=True)
        nom_fichier = os.path.join(dossier, f"{slug}.md")
    else:
        nom_fichier = f"{slug}.md"
        
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(frontmatter + contenu)
    print(f"✅ Article généré et structuré avec succès : {nom_fichier}")
    return nom_fichier

def main():
    parser = argparse.ArgumentParser(description="Générateur d'articles techniques d'éclairage via Google Gemini.")
    parser.add_argument("--sujet", type=str, default="Calcul des lux et disposition des spots encastrés", help="Sujet technique")
    parser.add_argument("--piece", type=str, default="Cuisine contemporaine", help="Type de pièce / espace")
    parser.add_argument("--slug", type=str, default="calcul-lux-spots-cuisine", help="Nom du fichier Markdown de sortie (sans extension)")
    parser.add_argument("--dossier", type=str, default="articles", help="Dossier de destination (défaut: articles)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Modèle Gemini à utiliser")
    
    args = parser.parse_args()

    print(f"🚀 Génération de l'article avec le modèle [{args.model}]...")
    print(f"📌 Sujet : {args.sujet}")
    print(f"🏠 Pièce : {args.piece}")
    
    corps_article = generer_article_eclairage(args.sujet, args.piece, model=args.model)
    sauvegarder_en_markdown(f"Guide pratique : {args.sujet}", corps_article, args.slug, dossier=args.dossier)

if __name__ == "__main__":
    main()
