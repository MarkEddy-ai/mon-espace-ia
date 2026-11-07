---
name: kdp-seo-mastery
description: "Méthodes et algorithmes d'optimisation SEO avancée pour Amazon KDP : 7 slots backend A9, LSI, structure de sous-titre et description HTML."
---

# 🚀 Skill : Maîtrise du Référencement Amazon KDP (Algorithme A9)

Ce skill détaille les protocoles d'ingénierie sémantique pour propulser un livre non-fiction en tête des résultats de recherche Amazon.

## 1. Algorithme de Vérification d'Unicité des Mots-Clés
Pour chaque mot $m$ présent dans les 7 slots backend :
1. Nettoyer les accents et mettre en minuscules.
2. Vérifier si $m \in \text{Mots}(\text{Titre}) \cup \text{Mots}(\text{Sous-Titre}) \cup \text{Mots}(\text{Auteur})$.
3. Si oui : **Éliminer $m$** et le remplacer par un synonyme sémantique non encore exploité.
4. Concaténer jusqu'à concurrence de 45 caractères utiles par slot.

## 2. Structure Sémantique de la Description (Copywriting AIDA + LSI)
* **A (Attention) :** Titre `<h2>` contenant l'émotion de la promesse.
* **I (Intérêt) :** Le constat douloureux de la situation actuelle (2 paragraphes).
* **D (Désir) :** Liste à puces de 7 transformations concrètes (`<ul><li><strong>...</strong></li></ul>`).
* **A (Action) :** L'instruction ferme et rassurante d'achat immédiat.
