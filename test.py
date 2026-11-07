import os
import requests
from dotenv import load_dotenv

# Chargement de la clé depuis le fichier .env : aucune clé n'est codée en dur ici.
load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

def lister_modeles() -> bool:
    """Interroge Google Generative Language API pour lister les modèles autorisés."""
    if not API_KEY:
        print("❌ GEMINI_API_KEY absente : aucune clé trouvée dans l'environnement ni dans .env.")
        print("   Renseignez GEMINI_API_KEY dans le fichier .env puis relancez ce script.")
        return False

    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {
        "x-goog-api-key": API_KEY
    }

    print("🔑 Clé API détectée dans l'environnement (valeur non affichée).")
    print("Interrogation des serveurs Google pour lister vos modèles autorisés...")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Code HTTP : {response.status_code}")

        if response.ok:
            data = response.json()
            print("\n✅ MODÈLES AUTORISÉS POUR VOTRE CLÉ :")
            generate_models = []
            for model in data.get("models", []):
                nom = model.get('name')
                methodes = model.get('supportedGenerationMethods', [])
                if "generateContent" in methodes:
                    generate_models.append(nom)
                    print(f"  👉 {nom}")
            if not generate_models:
                print("  (Aucun modèle avec generateContent retourné)")
            return True
        else:
            print(f"❌ ERREUR HTTP {response.status_code} : {response.text[:300]}")
            return False
    except Exception as e:
        # Redaction défensive : la clé ne doit jamais apparaître dans un message d'erreur.
        message = str(e)
        if API_KEY:
            message = message.replace(str(API_KEY), "[CLÉ Masquée]")
        print(f"❌ Erreur lors de la requête : {message}")
        return False

if __name__ == "__main__":
    lister_modeles()
