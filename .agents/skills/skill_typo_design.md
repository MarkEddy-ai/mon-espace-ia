---
name: skill_typo_design
description: "Directives de typographie éditoriale d'impression KDP, pairings Google Fonts et harmonie visuelle."
---

# 🔤 SKILL : TYPOGRAPHIE D'ÉDITION & GOOGLE FONTS PAIRING

Ce skill définit les règles de composition typographique pour les livres imprimés Amazon KDP.

## 1. Les 7 Pairings Éditoriaux de Référence
Chaque ouvrage doit adopter un pairing typographique cohérent selon sa niche :

1. **Prestige & Finance (Obsidienne & Or) :**
   - *Titre :* **Cinzel** (Monumental, romain, autorité impériale)
   - *Sous-titre :* **Montserrat** (Moderne, géométrique, lisibilité forte)
   - *Corps :* **Merriweather** (Sérif robuste, excellente tenue d'encrage)
   - *Accent / Citations :* **Cormorant Garamond** (Finesse aristocratique)

2. **Luxe & Patrimoine (Émeraude & Champagne) :**
   - *Titre :* **Playfair Display** (Didot moderne, raffinement)
   - *Sous-titre :* **Cormorant Garamond**
   - *Corps :* **Libre Baskerville** (Équilibre classique d'édition)
   - *Accent :* **Cinzel**

3. **Tech, IA & Productivité (Saphir & Platine) :**
   - *Titre :* **Inter** (Précision suisse, lisibilité écran et print)
   - *Sous-titre :* **Montserrat**
   - *Corps :* **Lato** (Chaleur sans empattements, repos des yeux)
   - *Accent :* **Roboto Mono** ou **Cinzel**

4. **Stoïcisme & Philosophie (Bordeaux & Or Rose) :**
   - *Titre :* **Cinzel**
   - *Sous-titre :* **Cormorant Garamond**
   - *Corps :* **Libre Baskerville** ou **EB Garamond**
   - *Accent :* **Playfair Display**

5. **Santé & Bien-Être (Harmonie Organique) :**
   - *Titre :* **Lora** (Calligraphie contemporaine apaisante)
   - *Sous-titre :* **Montserrat**
   - *Corps :* **Lato**
   - *Accent :* **Cormorant Garamond**

6. **Enfants & Coloriage (4-8 ans) :**
   - *Titre :* **Baloo 2** (Courbes généreuses et ludiques)
   - *Sous-titre :* **Fredoka** (Rondeur douce et chaleureuse)
   - *Corps :* **Nunito** (Clarté absolue pour jeunes lecteurs)
   - *Accent :* **Fredoka**

7. **Littérature & Roman d'Auteur :**
   - *Titre :* **Cormorant Garamond**
   - *Sous-titre :* **Playfair Display**
   - *Corps :* **Libre Baskerville**
   - *Accent :* **Lora**

---

## 2. Métriques Typographiques de Composition
* **Corps de texte :** `10.5 pt`, interlignage strict de `1.48` (ni trop serré, ni aéré artificiellement).
* **Justification bilatérale :** `text-align: justify; hyphens: auto; text-justify: inter-word;`.
* **Alinéa (Retrait de première ligne) :** `1.2 em` sur les paragraphes de texte courant.
* **Suppression de l'alinéa :** Pas d'alinéa sur le premier paragraphe après un titre ou un encadré (`h1 + p, h2 + p, h3 + p { text-indent: 0; }`).
* **Lettrine d'ouverture (Drop Cap) :** Sur 2 à 3 lignes de hauteur (`float: left; font-size: 3.4em; line-height: 0.8;`).
* **Contrôle prépresse :** Pas de lignes veuves ou orphelines (`orphans: 3; widows: 3;`).
