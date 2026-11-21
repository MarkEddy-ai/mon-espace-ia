---
name: skill_factcheck_humanizer
description: "Règles d'évaluation de crédibilité, synthèse non redondante, élimination chirurgicale des tics d'écriture IA, calcul de naturalité et bibliographie KDP."
---

# 🔬 SKILL : SYNTHÈSE, FACT-CHECKING & HUMANISATION ÉDITORIALE (AGENT 3)

Ce skill régit la validation de crédibilité des sources documentaires et le polissage humain du manuscrit pour éliminer tout marqueur de génération synthétique.

## 1. Grille de Crédibilité des Sources (Tiering A / B / C)
L'agent évalue chaque source selon une matrice rigoureuse :
* **Tier A (Poids 1.0) :** Études universitaires, revues à comité de lecture, rapports d'institutions publiques (OCDE, INSEE, Fed, OMS).
* **Tier B (Poids 0.7) :** Livres d'éditeurs renommés, enquêtes de presse économique et scientifique de premier plan.
* **Tier C (Poids 0.4) :** Témoignages de terrain, retours d'expérience vérifiés sur forums spécialisés.
* **Rejet Immédiat :** Articles sans auteur, sites de contenu généré par IA, billets sponsorisés non sourcés ou statistiques non attribuées.

---

## 2. Détection & Éradication des Marqueurs IA (Anti-Robotic Engine)
L'agent traque et remplace impitoyablement les 10 tics d'écriture typiques des LLM :
1. *"Dans ce chapitre, nous allons explorer..."* -> Entrée directe dans l'action.
2. *"Comme nous l'avons mentionné précédemment..."* -> Suppression pure et simple.
3. *"Il est important de noter que..."* -> Remplacement par le fait brut.
4. *"En conclusion, on peut dire que..."* -> Remplacement par la synthèse active.
5. *"Plongeons dans l'univers de..."* -> Remplacement par l'analyse concrète.
6. *"Il convient de souligner..."* -> Suppression ou reformulation incisive.
7. *"Force est de constater..."* -> Présentation des données objectives.
8. *"En somme..."* / *"En fin de compte..."* -> Transition naturelle.
9. *"Dans un monde en constante évolution..."* -> Formulation contextualisée et précise.
10. *"Il ne fait aucun doute que..."* -> Nuance basée sur les preuves.

---

## 3. Score de Naturalité Humaine (Human Naturalness Score)
Le score (0 à 100) est calculé sur 3 piliers :
- **Variation de longueur des phrases (Burstiness) :** Alternance de phrases courtes et percutantes (< 10 mots) et de phrases articulées (15-25 mots).
- **Zéro Cliché IA :** Pénalité de 15 points par tic robotique résiduel.
- **Densité factuelle :** Ratio de faits concrets, chiffres et exemples par rapport aux abstractions.

---

## 4. Normalisation Bibliographique KDP
Toute fin d'ouvrage doit comporter une section `## Sources & Bibliographie` normalisée (style APA simplifié adapté à l'impression grand public KDP), classée par ordre alphabétique des auteurs ou par chapitre.
