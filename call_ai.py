import os
import requests
from dotenv import load_dotenv

# Chargement forcé des variables d'environnement
load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

# Modèle actif et validé pour votre clé
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"


def generer_texte_gemini(system_prompt: str, prompt: str, temperature: float = 0.4, max_tokens: int = 8192, **kwargs) -> str:
    """Envoie une requête à l'API Gemini et retourne le texte généré."""
    if not API_KEY:
        raise ValueError("❌ Aucune clé API GEMINI_API_KEY trouvée dans le fichier .env.")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    import time
    tentatives_max = 5
    for tentative in range(1, tentatives_max + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            if response.status_code in [503, 429] and tentative < tentatives_max:
                attente = tentative * 4
                print(f"    ⏳ [RETRY {tentative}/{tentatives_max}] Modèle occupé (Code {response.status_code}). Nouvelle tentative dans {attente}s...")
                time.sleep(attente)
                continue

            if not response.ok:
                raise RuntimeError(f"Erreur API Google ({response.status_code}) : {response.text}")

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            if tentative < tentatives_max:
                attente = tentative * 4
                print(f"    ⏳ [RETRY {tentative}/{tentatives_max}] Incident réseau ({e}). Nouvelle tentative dans {attente}s...")
                time.sleep(attente)
            else:
                raise e


if __name__ == "__main__":
    print("Test de connexion Gemini via call_ai.py...")
    reponse = generer_texte_gemini(
        system_prompt="Réponds en une phrase concise.",
        prompt="Confirme que le moteur IA fonctionne correctement."
    )
    print("✅ Réponse reçue :", reponse)