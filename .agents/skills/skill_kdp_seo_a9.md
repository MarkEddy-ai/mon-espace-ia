---
name: skill_kdp_seo_a9
description: "Directives et algorithmes chirurgicaux de l'Agent 5 : Optimisation SEO Amazon A9/A10, Description HTML KDP, Catégories BISAC, Amazon Ads PPC et Contenu A+."
---

# 🚀 SKILL — KDP SEO A9/A10 & MARKETING AMAZON (AGENT 5)

Ce skill régit l'architecture complète du positionnement organique et payant des livres publiés via **MarkEddy KDP Studio** selon l'algorithme de classement Amazon A9/A10.

---

## 📐 1. La Sainte Trinité du Titre & Sous-Titre KDP

* **Longueur maximale combinée :** Stricte limite de **200 caractères** (titre + sous-titre).
* **Le Titre Principal (CTR & Thumbnail) :** 2 à 5 mots percutants à fort impact émotionnel, lisible à 120 px de large.
* **Le Sous-Titre (Moissonneur Longue Traîne) :** 12 à 25 mots intégrant les 3 intentions majeures :
  1. *Le Problème Résolu* (ex. : Sortir du découvert bancaire)
  2. *La Méthode Employée* (ex. : La méthode pas-à-pas en 50 étapes)
  3. *La Promesse Concrète de Transformation* (ex. : Bâtir son épargne sans sacrifice)
* **Indexation A9 :** Tous les mots du Titre et du Sous-titre sont indexés en priorité maximale par Amazon. **Interdiction formelle de les répéter dans les mots-clés backend.**

---

## 🎯 2. Les 7 Slots Backend Amazon A9 (Règles d'Or)

Chaque slot backend KDP doit cibler une intention distincte selon la Matrice Règle 05 :

| Slot | Typologie d'Intention | Longueur Cible | Exemple Concret (Niche Finances) |
| :---: | :--- | :---: | :--- |
| **Slot 1** | **Problème / Douleur urgente** | $\le 50$ octets | `sortir du decouvert bancaire fin de mois` |
| **Slot 2** | **Méthode / Cadre opérationnel** | $\le 50$ octets | `methode enveloppes virtuelles regle 50 30 20` |
| **Slot 3** | **Action / Investissement** | $\le 50$ octets | `investir en bourse petit budget etf pea` |
| **Slot 4** | **Sécurité / Épargne** | $\le 50$ octets | `constituer epargne securite matelas urgence` |
| **Slot 5** | **Profil / Cible spécifique** | $\le 50$ octets | `gestion budget debutant jeune actif salarie` |
| **Slot 6** | **Obstacle / Désendettement** | $\le 50$ octets | `rembourser credit consommation effet boule` |
| **Slot 7** | **Transformation / Objectif final** | $\le 50$ octets | `independance financiere liberte patrimoine` |

### Contraintes Techniques Strictes de l'Algorithme A9 :
1. **Limite UTF-8 par slot :** $\le 50$ octets UTF-8 par case (`len(slot.encode('utf-8')) <= 50`).
2. **Quota cumulé total :** $\le 250$ octets cumulés sur l'ensemble des 7 cases.
3. **Zéro Ponctuation :** Aucune virgule, aucun guillemet, point d'exclamation ou tiret. Amazon A9 indexe les espaces simples.
4. **Zéro Cannibalisation :** Aucun mot déjà présent dans le Titre ou le Sous-titre.
5. **Zéro Terme Prohibé KDP :** Bannissement total de `bestseller`, `n°1`, `gratuit`, `free`, `promo`, `kindle`, `prix`.
6. **Zéro Marque Notoire :** Bannissement total des marques tierces déposées (`lego`, `disney`, `marvel`, `pokemon`, etc.).

---

## 📚 3. Sélection des 3 Catégories Amazon & Codes BISAC

Chaque livre doit être classé dans exactement **3 catégories hiérarchiques** :
1. **1 Catégorie de Volume (Large) :** Assure la visibilité globale dans le rayon principal (ex: `Livres > Entreprise et Bourse > Finances personnelles` — BISAC `BUS027000`).
2. **2 Catégories de Sous-Niche (Ciblées) :** Permet d'obtenir rapidement le badge **#1 Meilleure Vente (Best-Seller Badge)** (ex: `Budget` — BISAC `BUS006000`, `Investissement` — BISAC `BUS036000`).

---

## 📝 4. Description Commerciale Amazon (HTML Strict & Persuasion AIDA)

Amazon KDP applique un filtre HTML strict sur la page produit :
* **Balises autorisées UNIQUEMENT :** `<h2>`, `<h3>`, `<h4>`, `<b>`, `<i>`, `<p>`, `<br>`, `<ul>`, `<li>`.
* **Toutes les autres balises sont interdites** (`<h1>`, `<div>`, `<span>`, `<a>`, `<script>`, `style`).
* **Limite stricte :** **4 000 caractères maximum**.
* **Structure Persuasive AIDA :**
  - **Attention (`<h2>`) :** Accroche émotionnelle percutante.
  - **Intérêt (`<h3>` + `<p>`) :** La promesse de transformation et l'identification au problème.
  - **Désir (`<ul><li><b>...</b></li></ul>`) :** 4 puces détaillant les livrables concrets (cas chiffrés, pièges évités, protocoles 24h).
  - **Action (`<p><b>👉 ...</b></p>`) :** Appel à l'action impératif orienté vers le bouton "Ajouter au panier".

---

## 📊 5. Stratégie Amazon Ads / PPC (Sponsored Products)

Structure de lancement publicitaire générée automatiquement :
1. **Campagne Exacte (Top Search) :**
   - 4 à 7 mots-clés de conversion maximale
   - Enchère suggérée : `0,65 €` | ACOS cible : `< 25%` | Budget quotidien : `10,00 €`
2. **Campagne Expression (Phrase) :**
   - Variations sémantiques et combinaisons à longue traîne
   - Enchère suggérée : `0,45 €` | ACOS cible : `< 30%` | Budget quotidien : `8,00 €`
3. **Campagne Large (Broad) :**
   - Moissonnage de nouvelles requêtes utilisateurs
   - Enchère suggérée : `0,35 €` | ACOS cible : `< 35%` | Budget quotidien : `5,00 €`
4. **Ciblage Produits (ASIN Targeting) :**
   - Ciblage direct des fiches des livres best-sellers concurrents de la même niche
   - Enchère suggérée : `0,50 €` | Budget quotidien : `7,00 €`
5. **Mots-Clés Négatifs Immédiats :**
   - `gratuit`, `free`, `pdf`, `torrent`, `occasion`, `telecharger`, `crack`, `pirate`.

---

## 🎨 6. Blueprint Contenu A+ (Informations de l'Éditeur)

Gabarit de 3 modules normalisés KDP :
* **Module 1 (Hero Banner) :** Bannière de marque grand format (`970x300 px` ou `970x600 px` @ 300 DPI).
* **Module 2 (3 Piliers Clés) :** 3 cartes visuelles carrées (`300x300 px`) détaillant la méthode, les études de cas et les outils d'action.
* **Module 3 (Tableau Comparatif) :** Grille comparative démontrant la supériorité du livre face aux ouvrages génériques du marché (typographie 6x9, zéro fluff, fiches pratiques).

---

## 📦 7. Livrables Fichiers Produits par l'Agent 5

* [`seo_amazon_ready.json`](file:///c:/Users/acer/OneDrive/Desktop/mon-espace-ia/exports/) : Fiche technique complète intégrant les 7 slots audités, les 3 catégories BISAC, le plan PPC et le blueprint A+.
* [`description_amazon.html`](file:///c:/Users/acer/OneDrive/Desktop/mon-espace-ia/exports/) : Code HTML strict de la description commerciale prêt à copier-coller dans le portail KDP.
