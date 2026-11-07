"""
kdp_architect.py - Générateur d'architecture et de Blueprint de livre Amazon KDP.
Conçoit le plan complet (10 chapitres x 5 sections = 50 parties), les métadonnées SEO,
les 7 mots-clés et les catégories cibles.
"""

import os
import json
import re
import argparse
from pathlib import Path
from call_ai import generer_texte_gemini

def concevoir_livre_kdp(niche: str, public_cible: str, nb_chapitres: int = None) -> dict:
    """
    Génère l'architecture complète d'un livre KDP non-fiction de 150+ pages.
    Permet un nombre de chapitres flexible (7 à 18 chapitres) selon la logique du sujet.
    """
    consigne_chapitres = (
        f"Définis exactement {nb_chapitres} chapitres contenant 3 à 5 sous-sections détaillées chacun."
        if nb_chapitres
        else "Détermine le nombre idéal de chapitres pour couvrir ce sujet de manière exhaustive (généralement entre 7 et 15 chapitres selon la complexité du sujet), chaque chapitre contenant 3 à 5 sous-sections détaillées."
    )

    system_prompt = (
        "Tu es le meilleur éditeur, stratège de contenu et ghostwriter best-seller Amazon KDP non-fiction pour l'auteur MarkEddy. "
        "Ta mission est de structurer un livre complet, dense, ultra-actionnable et vendeur de plus de 150 pages. "
        "Tu dois impérativement répondre UNIQUEMENT avec un objet JSON valide, sans balises Markdown "
        "comme ```json au début ou à la fin, sans texte avant ou après."
    )

    prompt = f"""
    Conçois un plan de livre best-seller Amazon KDP pour :
    - Niche / Thématique : "{niche}"
    - Public cible spécifique : "{public_cible}"
    
    Structure JSON obligatoire et stricte :
    {{
      "titre": "Titre d'accroche percutant et mémorable",
      "sous_titre": "Sous-titre explicite avec mots-clés SEO pour le référencement Amazon",
      "promesse_client": "Ce que le lecteur aura accompli ou transformé après lecture",
      "auteur_suggere": "Nom de plume ou profil d'autorité adapté",
      "mots_cles_kdp": [
        "mot-clé 1", "mot-clé 2", "mot-clé 3", "mot-clé 4", "mot-clé 5", "mot-clé 6", "mot-clé 7"
      ],
      "categories_kdp": [
        "Catégorie principale Amazon / BISAC",
        "Catégorie secondaire Amazon / BISAC"
      ],
      "chapitres": [
        {{
          "numero": 1,
          "titre": "Titre explicite du chapitre 1",
          "objectif": "Objectif pédagogique et transformationnel du chapitre",
          "sections": [
            {{
              "titre": "1.1 Titre sous-partie",
              "points_cles": ["Concept fondamental", "Exemple concret / Étude de cas", "Erreur fréquente", "Action immédiate"]
            }},
            {{
              "titre": "1.2 Titre sous-partie",
              "points_cles": ["Concept", "Application pratique", "Checklist"]
            }},
            {{
              "titre": "1.3 Titre sous-partie",
              "points_cles": ["Point clé", "Méthode pas-à-pas"]
            }},
            {{
              "titre": "1.4 Titre sous-partie",
              "points_cles": ["Point clé", "Exercice d'application"]
            }},
            {{
              "titre": "1.5 Titre sous-partie",
              "points_cles": ["Synthèse", "Plan d'action à retenir"]
            }}
          ]
        }}
      ]
    }}
    
    Exigence de structure et de volume : {consigne_chapitres}
    Chaque sous-section doit être concrète, pratique, chiffrée et directement orientée vers la valeur pour le lecteur.
    """

    print("🧠 Analyse de la niche et modélisation de l'architecture du livre via Gemini...")
    reponse_brute = generer_texte_gemini(system_prompt=system_prompt, prompt=prompt, temperature=0.4, max_tokens=8192)

    # Nettoyage robuste pour extraire le JSON
    texte = reponse_brute.strip()
    match = re.search(r"(\{.*\})", texte, re.DOTALL)
    if match:
        texte_propre = match.group(1)
    else:
        texte_propre = re.sub(r"^```(?:json)?\s*", "", texte, flags=re.MULTILINE)
        texte_propre = re.sub(r"\s*```$", "", texte_propre, flags=re.MULTILINE)

    try:
        data = json.loads(texte_propre)
        return data
    except json.JSONDecodeError as err:
        print("❌ Erreur de décodage JSON. Réponse brute reçue :")
        print(reponse_brute[:500] + "...")
        raise err

def sauvegarder_blueprint(data: dict, nom_fichier: str = "book_blueprint.json") -> Path:
    chemin = Path(nom_fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Schéma du livre enregistré avec succès : {chemin.resolve()}")
    return chemin

def main():
    parser = argparse.ArgumentParser(description="Architecte de livre Amazon KDP professionnel.")
    parser.add_argument("--niche", type=str, default="Maîtriser ses finances personnelles et investir simplement", help="Thématique ou niche du livre")
    parser.add_argument("--cible", type=str, default="Jeunes actifs et débutants sans compétences financières préalables", help="Public cible du livre")
    parser.add_argument("--output", type=str, default="book_blueprint.json", help="Fichier de sortie JSON du blueprint")
    args = parser.parse_args()

    plan_livre = concevoir_livre_kdp(args.niche, args.cible)
    sauvegarder_blueprint(plan_livre, args.output)

    print("\n" + "=" * 60)
    print("📖 LIVRE KDP MODÉLISÉ AVEC SUCCÈS")
    print("=" * 60)
    print(f"📚 Titre       : {plan_livre.get('titre')}")
    print(f"🎯 Sous-titre  : {plan_livre.get('sous_titre')}")
    print(f"👥 Cible       : {args.cible}")
    print(f"📑 Chapitres   : {len(plan_livre.get('chapitres', []))}")
    total_sections = sum(len(c.get('sections', [])) for c in plan_livre.get('chapitres', []))
    print(f"📝 Sections    : {total_sections} sous-parties détaillées prêtes pour la rédaction")
    print(f"🔑 Mots-clés   : {', '.join(plan_livre.get('mots_cles_kdp', []))}")
    print("=" * 60)

if __name__ == "__main__":
    main()
