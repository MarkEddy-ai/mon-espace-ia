---
trigger: always_on
description: "Règles d'audit technique et critères de rejet Amazon KDP pour garantir un taux d'acceptation de 100%."
---

# 🔬 RÈGLE 04 : CONFORMITÉ TECHNIQUE AMAZON KDP (ZÉRO REJET)

Cette règle définit la liste de vérification non négociable auditée par l'agent `kdp_qa.py` avant toute publication.

## 1. Critères de la Couverture
1. **Résolution industrielle :** Exactement `300 DPI` sans pixelisation.
2. **Fond Perdu (Bleed) :** `0.125 pouce` (3.2 mm) ajouté sur les 4 côtés extérieurs.
3. **Calcul de la tranche :** Épaisseur calculée au micron selon la formule :
   $$\text{Largeur dos} = \text{Pages} \times 0.002252 \text{ in (papier blanc)}$$
4. **Réserve Code-Barres ISBN :** Rectangle blanc strict de `600 × 360 px` positionné en bas à droite de la 4ème de couverture, sans aucun texte ou élément graphique entrant dans cette zone.
5. **Zone de sécurité texte :** Aucun texte ne doit se situer à moins de `0.25 pouce` du bord de coupe final.

---

## 2. Critères de l'Intérieur du Livre
1. **Format de coupe :** Déclaration CSS `@page { size: 6in 9in; }`.
2. **Marge de reliure (Gutter) :** Présence d'au moins `0.85 pouce` du côté intérieur du dos pour éviter l'absorption du texte par la couture.
3. **Numérotation continue :** Les numéros de page doivent être cohérents et absents des pages de faux-titre, titre et copyright.
4. **Volume textuel :** Un minimum de `25 000 mots` est requis pour la certification "Livre complet" (100-150 pages).
5. **Absence de termes de debug :** Zéro présence de termes comme "TODO", "Lorem ipsum", "NaN", "undefined".
