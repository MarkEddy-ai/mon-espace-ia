---
name: skill_cover_packaging
description: "Calculs dimensionnels exacts au micron (Trim + Bleed + Spine), réserve ISBN 600x360 px et conformité prépresse KDP."
---

# 📐 SKILL : CALCULS DIMENSIONNELS & PACKAGING COUVERTURE AMAZON KDP

Ce skill définit les protocoles mathématiques et géométriques indispensables pour générer des fichiers de couverture 300 DPI sans aucun risque de rejet lors de la vérification prépresse Amazon KDP.

## 1. Calcul Dynamique du Dos (Spine) au Micron
L'épaisseur du dos dépend du nombre de pages exact et du grammage du papier KDP :

$$\text{Largeur du dos (pouces)} = \text{Nombre de pages} \times \text{Coeff Papier}$$

| Type de Papier KDP | Coefficient par page | Grammage KDP |
| :--- | :--- | :--- |
| **Blanc standard (`white`)** | `0.002252 in` | 50 lb (74 g/m²) |
| **Crème classique (`cream`)** | `0.002500 in` | 55 lb (80 g/m²) |
| **Couleur standard (`color_standard`)** | `0.002349 in` | 50 lb (74 g/m²) |
| **Couleur premium (`color_premium`)** | `0.002500 in` | 60 lb (90 g/m²) |

👉 **Règle KDP du texte sur le dos :** L'impression d'un texte sur la tranche n'est autorisée par Amazon que si le livre compte **au moins 79 pages**. En deçà, la tranche doit rester vierge de tout texte pour éviter les bavures de pliure.
👉 **Marge de sécurité tranche :** Préserver `0.0625 pouce` (1.6 mm) de vide entre le texte du dos et les rainures de pliure.

---

## 2. Géométrie du Fond Perdu (Bleed) & Dimensions Totales
* **Fond Perdu Standard :** `0.125 pouce` (3.175 mm) ajouté sur les 4 côtés extérieurs du document complet.
* **Largeur Totale Document :**
  $$\text{Largeur} = \text{Bleed} + \text{Plat 4 (Trim)} + \text{Dos (Spine)} + \text{Plat 1 (Trim)} + \text{Bleed}$$
* **Hauteur Totale Document :**
  $$\text{Hauteur} = \text{Bleed} + \text{Hauteur de Coupe (Trim)} + \text{Bleed}$$
* **Conversion Pixels 300 DPI :**
  $$\text{Pixels} = \text{round}(\text{Dimension en pouces} \times 300)$$

---

## 3. Réserve Code-Barres ISBN Normalisée
* **Emplacement :** En bas à droite de la 4ème de couverture (Plat 4).
* **Dimensions normalisées :** Strictement `600 × 360 px` à 300 DPI (`2.0 in × 1.2 in`).
* **Zone d'exclusion :** Aucun texte, logo ou élément graphique signifiant ne doit pénétrer dans ce rectangle blanc.
* **Distance des bords :** Au moins `0.25 pouce` de la ligne de coupe basse et extérieure.

---

## 4. Test de Miniature (Thumbnail Test)
Le titre principal de la 1ère de couverture doit rester instantanément lisible même lorsqu'il est réduit à **120 pixels de largeur** dans les résultats de recherche sur mobile et desktop.
