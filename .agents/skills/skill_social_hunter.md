---
name: skill_social_hunter
description: "Règles d'extraction des tendances sociales, questions réelles et signaux de demande (Reddit, forums, TikTok, Instagram, Google Trends, Amazon A9)."
---

# 🕵️ SKILL : VEILLE SOCIALE & EXTRACTION DES DOULEURS DU MARCHÉ (AGENT 1)

Ce skill régit la détection des véritables interrogations humaines et des signaux de demande non satisfaits avant toute rédaction KDP.

## 1. Principes d'Isolation & Autorité
- **Rôle unique :** Identifier ce que les gens demandent vraiment sur le terrain social (Reddit, forums de niche, réseaux sociaux) et sur les plateformes de recherche (Google Trends, Amazon A9).
- **Entrée :** Niche (`str`), Langue (`fr` ou `en`).
- **Sortie obligatoire :** JSON strict validé contenant `top_questions`, `pain_points`, `book_ideas` (3 concepts différenciants) et `trending_keywords`.
- **Règle anti-hallucination :** Ne jamais inventer de tendances fictives. Si le réseau est indisponible, basculer sur les banques de questions qualifiées et marquer `verification_required: true`.

---

## 2. Canaux d'Écoute Sociale & Signaux de Frustration
Pour chaque niche, l'agent explore 4 vecteurs :
1. **Communautés Reddit & Forums de Spécialistes :**
   - Requêtes sur les subreddits pertinents (ex: `r/vosfinances`, `r/AskReddit`, `r/productivity`, `r/books`).
   - Recherche des formulations : *"comment faire pour..."*, *"pourquoi personne ne parle de..."*, *"le plus gros problème avec..."*.
2. **Google Trends & Requêtes Associées :**
   - Analyse des requêtes en hausse (+50%, Breakout).
   - Identification des questions en langage naturel ("Comment...", "Pourquoi...", "Quelle est la règle...").
3. **Amazon KDP Auto-Suggest & Bestsellers :**
   - Analyse des combinaisons saisies par les acheteurs dans la barre de recherche Amazon (`stripbooks`).
   - Détection des sous-niches émergentes : *débutant*, *guide pratique*, *cahier d'exercices*, *en 30 jours*.
4. **Réseaux Sociaux (TikTok / Instagram / Facebook Groups) :**
   - Termes récurrents dans les commentaires de vidéos virales.
   - Frustrations exprimées face aux solutions théoriques ou trop complexes.

---

## 3. Matrice des 3 Concepts de Livres Différenciants
L'agent doit transformer la matière brute en **3 concepts de livres best-sellers** :
* **Concept 1 (L'Approche Débutant / Déculpabilisante) :** Répond au blocage d'entrée par une méthode pas-à-pas simple.
* **Concept 2 (Le Système / Cadre Opératoire 30 Jours) :** Répond au manque de discipline par des fiches d'action et tableaux.
* **Concept 3 (Le Cas Concret & Contre-Pied Cognitif) :** Répond à la déception des livres trop théoriques en démontant les mythes de la niche.
