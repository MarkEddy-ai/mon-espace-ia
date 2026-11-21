---
name: skill_illustration
description: "Règles de direction artistique, palettes chromatiques de prestige, images 300 DPI et moteur de coloriage vectoriel KDP."
---

# 🎨 SKILL : DIRECTION ARTISTIQUE, ILLUSTRATIONS & COULEURS HAUTE COUTURE

Ce skill régit la conception graphique des couvertures, bannières A+ Content et planches illustrées/coloriage.

## 1. Les 4 Palettes Chromatiques de Prestige
Aucune couleur criarde ou saturée à 100% n'est tolérée. Seules les 4 harmonies d'autorité suivantes doivent être appliquées selon la niche :

1. **Obsidienne & Or Impérial (Finances, Leadership, Stratégie, Business) :**
   - Fond primaire : `#0A0F1D` (Bleu nuit abyssal velouté)
   - Tranche (Dos) : `#1E293B` (Ardoise dense)
   - Accent / Dorure : `#D4AF37` (Or impérial chaud)
   - Typographie claire : `#F8FAFC` (Blanc lin noble)

2. **Émeraude Royale & Champagne (Immobilier, Patrimoine durable, Santé d'élite) :**
   - Fond primaire : `#062C22` (Émeraude profonde d'orfèvre)
   - Accent / Dorure : `#C5A059` (Champagne doux)
   - Typographie claire : `#FAF7F2` (Blanc ivoire)

3. **Saphir Majestueux & Argent Platine (Technologie, IA, Sciences, Méthodes) :**
   - Fond primaire : `#0B192C` (Saphir d'encre)
   - Accent / Métal : `#00ADB5` ou `#E2E8F0` (Argent vif / Platine)
   - Typographie claire : `#FFFFFF` (Blanc absolu)

4. **Bordeaux Grand Cru & Or Rose (Psychologie, Développement personnel, Philosophie) :**
   - Fond primaire : `#2C0B0E` (Lie-de-vin profond)
   - Accent : `#E8C5C8` (Or rose nacré)
   - Typographie claire : `#FFF8F8` (Blanc poudré)

---

## 2. Standards Techniques des Images & Anti-Hotlinking
* **Résolution Industrielle :** Strictement **300 DPI** pour l'impression papier Amazon KDP.
* **Téléchargement & Caching Local :** Toute image issue d'Unsplash ou Pixabay doit être **immédiatement téléchargée** dans `assets/media_cache/` pour éviter tout hotlinking ou disparition de ressource.
* **Recadrage sans déformation :** Utilisation systématique de `ImageOps.fit()` avec centrage automatique du sujet.

---

## 3. Normes Strictes des Livres de Coloriage
* **Binarisation Noire & Blanche Pure :** Les tracés doivent être strictement `#000000` sur fond `#FFFFFF`.
* **Zéro niveau de gris :** Aucun dégradé ou demi-teinte qui provoquerait du grain à l'impression standard KDP.
* **Option Recto Uniquement :** Insertion automatique d'une page verso blanche anti-bavure après chaque illustration pour préserver les feutres des enfants et adultes.
