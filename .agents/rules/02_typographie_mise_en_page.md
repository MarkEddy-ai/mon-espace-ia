---
trigger: always_on
description: "Règles strictes de micro-typographie, mise en page intérieure 6x9 pouces, lettrines et folios alternés pour Amazon KDP."
---

# 🔤 RÈGLE 02 : TYPOGRAPHIE D'ÉDITION & MISE EN PAGE INTERNE (6×9 POUCES)

Cette règle régit la mise en page de tout livre imprimable KDP produit par la machine.

## 1. Métriques de Coupe & Marges de Reliure (Gutter)
Pour garantir une lecture fluide sans devoir écarter le livre avec force, les marges doivent respecter la géométrie asymétrique suivante :

* **Format de coupe (Trim Size) :** `6.0 in × 9.0 in` (15,24 × 22,86 cm).
* **Marge intérieure de reliure (Gutter) :** `0.85 in` (2,16 cm) minimum.
* **Marge extérieure :** `0.55 in` (1,40 cm).
* **Marges haute et basse :** `0.75 in` (1,90 cm).

---

## 2. Standards Typographiques d'Édition
* **Police de corps :** Garamond / Georgia / Baskerville avec empattements nobles (Serif).
* **Corps du texte :** `10.5 pt`, interlignage strict de `1.45` (ni trop serré, ni aéré artificiellement).
* **Justification :** Texte justifié des deux côtés avec césure automatique des mots (`hyphens: auto; text-align: justify;`).
* **Retrait de paragraphe (Alinéa) :** `1.2 em` sur tous les paragraphes de texte courant.
* **Suppression de l'alinéa :** Pas de retrait sur le tout premier paragraphe suivant un titre (`h1 + p`, `h2 + p`, `h3 + p`).
* **Lettrines (Drop Caps) :** Chaque premier paragraphe de grand chapitre arbore une lettrine élégante sur 2 ou 3 lignes de hauteur.

---

## 3. En-têtes Courants & Folios Alternés
* **Pages paires (gauche) :** Titre de l'ouvrage en petites capitales discrètes (8.5 pt) centré ou aligné à gauche.
* **Pages impaires (droite) :** Titre du chapitre en cours en italique (8.5 pt) centré ou aligné à droite.
* **Numéros de page (Folios) :** Centrés en pied de page (9 pt).
* **Pages muettes :** Aucune numérotation apparente sur la page de titre, la page de copyright et la première page d'un chapitre.
* **Sauts de page stricts :** Chaque grand chapitre doit obligatoirement commencer sur une nouvelle page (`page-break-before: always;`).
