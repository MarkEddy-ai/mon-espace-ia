---
name: kdp-interior-typography
description: "Directives et règles CSS d'impression pour la composition intérieure 6x9 pouces, lettrines, ornements d'édition et marges de reliure."
---

# 📐 Skill : Maquettisme & Typographie Intérieure KDP (6×9 po)

Ce skill formalise les techniques typographiques des maisons d'édition pour transformer un manuscrit brut en un livre papier haut de gamme.

## 1. Structure Normée du Livre d'Édition
Tout livre professionnel doit comporter les sections suivantes dans l'ordre strict :

1. **Pages Liminaires (Front Matter) :**
   * Page de Faux-Titre
   * Page de Grand Titre
   * Page de Mentions Légales & Copyright (avec avertissement légal / disclaimer)
   * Sommaire / Table des Matières
2. **Corps d'Ouvrage (Body Matter) :**
   * Avant-propos / Introduction
   * 10 Grands Chapitres avec saut de page obligatoire (`page-break-before: always;`)
   * 5 sous-sections par chapitre avec encadrés d'action
3. **Pages Finales (Back Matter) :**
   * Conclusion & Postface
   * Page « À Propos de l'Auteur »
   * Appel à l'action sincère pour les avis Amazon KDP

## 2. Feuille de Style CSS KDP de Référence
```css
@page {
    size: 6in 9in;
    margin-top: 0.75in;
    margin-bottom: 0.75in;
    @bottom-center {
        content: counter(page);
        font-family: 'Georgia', 'Garamond', serif;
        font-size: 9pt;
        color: #555;
    }
}

/* Marge de reliure asymétrique (Gutter) */
@page :right { margin-left: 0.85in; margin-right: 0.55in; }
@page :left  { margin-left: 0.55in; margin-right: 0.85in; }

/* Lettrine majestueuse (Drop Cap) */
p.chapter-lead::first-letter {
    font-size: 3.5em;
    float: left;
    line-height: 0.8;
    margin-right: 0.12em;
    font-family: 'Cinzel', 'Garamond', serif;
    color: #1a1a1a;
}
```
