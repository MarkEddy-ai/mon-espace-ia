---
name: kdp-luxury-cover
description: "Directives et algorithmes pour la conception de couvertures Amazon KDP de prestige à 300 DPI avec calcul précis du dos et palettes de luxe."
---

# 🎨 Skill : Conception de Couverture Haute Gamme Amazon KDP

Ce skill enseigne le processus de calcul, de composition visuelle et de rendu vectoriel pour produire des couvertures prêtes pour l'impression industrielle Amazon KDP à 300 DPI.

## 1. Algorithme de Calcul des Dimensions
Le gabarit complet inclut : `[Fond perdu gauche] + [4ème de couverture] + [Tranche / Dos] + [1ère de couverture] + [Fond perdu droit]`.

* **Largeur page standard 6x9 po :** `6.0 pouces`
* **Hauteur page standard 6x9 po :** `9.0 pouces`
* **Fond perdu (Bleed) :** `0.125 pouce` par bord
* **Formule de la tranche :**
  $$\text{Largeur dos (po)} = \text{Nombre de pages} \times 0.002252$$
* **Largeur totale en pixels (à 300 DPI) :**
  $$\text{Largeur px} = \text{round}\left(((6.0 \times 2) + \text{Dos} + (0.125 \times 2)) \times 300\right)$$
* **Hauteur totale en pixels (à 300 DPI) :**
  $$\text{Hauteur px} = \text{round}((9.0 + (0.125 \times 2)) \times 300) = 2775 \text{ px}$$

## 2. Palettes Chromatiques Pré-configurées
* `obsidian_gold` : `#0A0F1D` (Fond), `#D4AF37` (Or chaud), `#F8FAFC` (Texte). Idéal pour Finance, Succès, Stratégie.
* `emerald_champagne` : `#062C22` (Émeraude), `#C5A059` (Champagne), `#FAF7F2` (Ivoire). Idéal pour Immobilier, Patrimoine.
* `royal_sapphire` : `#0B192C` (Saphir), `#00ADB5` (Cyan métallisé), `#FFFFFF` (Blanc). Idéal pour Tech & IA.
* `grand_cru_rose` : `#2C0B0E` (Lie-de-vin), `#E8C5C8` (Or rose), `#FFF8F8` (Poudré). Idéal pour Psychologie & Bien-être.

## 3. Éléments Obligatoires de la Couverture
1. **1ère de couverture :** Titre en capitales massives, filet de dorure horizontal, sous-titre explicite, mention d'autorité.
2. **Dos :** Titre tourné à 90° centré sur la tranche (si plus de 100 pages).
3. **4ème de couverture :** Accroche de transformation (H2 doré), 5 points forts à puces claires, zone réservée blanche pour code-barres ISBN (`600 × 360 px`).
