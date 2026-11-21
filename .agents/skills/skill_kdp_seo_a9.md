---
name: skill_kdp_seo_a9
description: "Optimisation SEO Amazon A9 pour KDP : titres/sous-titres, 7 slots backend (<=50 octets UTF-8), catégories, description HTML KDP, A+ et clusters PPC."
---

# 🔎 SKILL — KDP SEO A9 (Amazon)

Ce skill encadre la génération d’un package SEO KDP conforme aux contraintes Amazon A9.

## Règles strictes
- **Titre + Sous-titre** : longueur totale **<= 200 caractères**.
- **7 cases backend** (keywords) : chacune **<= 50 octets UTF-8** (`len(value.encode("utf-8")) <= 50`).
- **Zéro mot dupliqué** avec le titre/sous-titre (risque de gaspillage d’indexation).
- **3 catégories Amazon** : **1 volume + 2 niches** (structure recommandée).
- **Description HTML** : **<= 4000 caractères**, balises autorisées uniquement :
  - `<h4>`, `<b>`, `<i>`, `<p>`, `<br>`, `<ul>`, `<li>`
- Livrer aussi :
  - **Blueprint Contenu A+** (modules recommandés)
  - **Clusters PPC** (broad/phrase/exact)

## API Python
Fonction principale :
- `kdp_extensions.seo_a9_agent.optimize_kdp_seo(book_title, subtitle, niche, book_type, target_audience, seed_keywords, language="fr") -> dict`

Le résultat inclut (entre autres) : `backend_keywords`, `backend_keywords_audit`, `categories`, `description_html`, `a_plus_blueprint`, `ppc_clusters`.

## Bonnes pratiques
- Éviter ponctuation inutile dans les slots backend (Amazon indexe surtout les mots/espaces).
- Ne pas répéter des termes déjà présents dans le titre.
- Privilégier des intentions (problème → méthode → action → résultat) cohérentes avec la niche.
