---
name: kdp-visual-pipeline
description: Pipeline visuel Amazon KDP — 16 formats officiels, connecteurs Unsplash/Pixabay 300 DPI, export Canva Connect et production de livres de coloriage noir et blanc pur. À utiliser pour tout travail de couverture, de galerie d'images ou de livre de coloriage.
---

# 🎯 Skill : Pipeline Visuel KDP

Ce skill orchestre les **deux subagents visuels** du dépôt `mon-espace-ia` et le
package d'extension **`kdp_extensions/`**. Il s'utilise pour toute demande
touchant un format d'impression, un visuel de couverture, une recherche d'image
ou un livre de coloriage.

## ⚙️ Environnement d'exécution obligatoire

```powershell
# Windows 11 — toujours via le venv du projet
.\.venv\Scripts\python.exe -m pytest test_suite.py test_extensions.py
```

Les scripts s'exécutent aussi directement :

```powershell
.\.venv\Scripts\python.exe -m kdp_extensions.kdp_dimensions
.\.venv\Scripts\python.exe -m kdp_extensions.media_connectors
.\.venv\Scripts\python.exe -m kdp_extensions.coloring_book_engine
```

## 🗂️ Architecture du package `kdp_extensions/`

```text
kdp_extensions/
├── __init__.py              # Package d'extension (sur-ensemble, rien déplacé)
├── kdp_dimensions.py        # 16 formats KDP + calculate_kdp_specs()
├── media_connectors.py      # Unsplash + Pixabay + Canva Connect API
└── coloring_book_engine.py  # Moteur de livres de coloriage 16 formats
```

**Règle zéro casse :** ce package n'altère aucun fichier de la racine. Les modules
racine (`media_connectors.py`, `coloring_book_engine.py`) restent intacts et
continuent de fonctionner ; `kdp_extensions/` est un sur-ensemble.

## 1️⃣ Référentiel des 16 formats (`kdp_dimensions.py`)

```python
from kdp_extensions.kdp_dimensions import (
    KDP_FORMAT_IDS, calculate_kdp_specs, list_kdp_formats, normalize_format,
)

KDP_FORMAT_IDS  # ['5x8', '5.06x7.81', '5.25x8', '5.5x8.5', '6x9', '6.14x9.21',
                #  '6.69x9.61', '7x10', '7.44x9.69', '7.5x9.25', '8.25x6',
                #  '8.25x8.25', '8.5x8.5', '8x10', '8.5x11', '8.27x11.69']

specs = calculate_kdp_specs("8.5x11", page_count=80, paper_type="white", bleed=True)
```

Retourne : `trim`, `spine` (coeff × pages), `margins` (gutter dynamique selon le
nombre de pages), `interior` (px @300 DPI), `cover` (Plat 4 + Dos + Plat 1 + bleed)
et `isbn_reserve_px` (**600 × 360**).

| Papier | Coeff dos (po/page) |
| :--- | :--- |
| `white` | 0.002252 |
| `cream` | 0.0025 |
| `color_standard` | 0.002349 |
| `color_premium` | 0.0025 |

Marges de reliure (gutter) : ≤150 p. → 0.375" · 151-300 → 0.5" · 301-400 → 0.625" · >400 → 0.75".
Fond perdu (bleed) : **0.125"** sur tout le pourtour, ajouté aux marges de sécurité.

## 2️⃣ Connecteurs média & Canva (`media_connectors.py`)

```python
from kdp_extensions.media_connectors import (
    search_stock_images, download_and_prepare_cover_bg,
    get_canva_auth_url, exchange_canva_code_for_token,
    upload_canva_asset, export_canva_design, generate_canva_cover_template,
)

imgs = search_stock_images("mandala", source="all", orientation="portrait", per_page=12)
local = download_and_prepare_cover_bg(imgs[0]["hd_url"], 2625, 3375)  # -> assets/media_cache/
```

- **Unsplash** : `UNSPLASH_ACCESS_KEY`, en-tête `Authorization: Client-ID <key>`.
- **Pixabay** : `PIXABAY_API_KEY`, `https://pixabay.com/api/`,
  `orientation='vertical'|'horizontal'`, `image_type='photo'|'vector'`,
  HD = `fullHDURL or largeImageURL`, aperçu = `webformatURL`.
- **Téléchargement obligatoire** dans `assets/media_cache/` (anti-hotlinking),
  recadrage `ImageOps.fit` sans déformation, sauvegarde JPEG **300 DPI**.
- **Canva OAuth 2.0** : `get_canva_auth_url()` → callback →
  `exchange_canva_code_for_token()` → `canva_tokens.json`.
  Sans secret client, un jeton simulé propre est persisté (mode `simulated`).
- **Repli** : si une clé manque ou qu'aucun résultat ne revient, le catalogue curé
  hors-ligne est servi — l'API ne renvoie jamais une liste vide.

## 3️⃣ Livres de coloriage (`coloring_book_engine.py`)

```python
from kdp_extensions.coloring_book_engine import produire_livre_coloriage

res = produire_livre_coloriage(
    book_id=42, titre="MANDALAS SACRÉS", sous_titre="30 motifs...",
    theme="mandalas", nb_illustrations=30, recto_uniquement=True,
    cover_bg_image=None, format_kdp="8.5x11",
)
```

- **Noir pur** `#000000` sur `#FFFFFF`, zéro gris (SVG ou line-art Pillow binaire).
- **Recto uniquement** : page verso blanche anti-bavure après chaque planche.
- **PDF 300 DPI via Playwright** (repli `msedge`), dimensions exactes du format.
- **Couverture via `cover_artisan_agent.fabriquer()`** : tranche au micron,
  proxy de mesure au format de coupe, palette selon le thème.
- Thèmes : `mandalas`, `botanique`, `animaux`, `architecture`.

## 4️⃣ Subagents OpenCode

| Subagent | Fichier | Rôle |
| :--- | :--- | :--- |
| `@kdp-media-designer` | `.opencode/agents/kdp-media-designer.md` | Images 300 DPI, galerie Unsplash/Pixabay, Canva |
| `@kdp-coloring-artisan` | `.opencode/agents/kdp-coloring-artisan.md` | Livres de coloriage 16 formats, PDF Playwright |

Routage :

- Besoin de **visuel de couverture / recherche d'image / export Canva** → `@kdp-media-designer`
- Besoin de **livre de coloriage / planche noir et blanc / verso anti-bavure** → `@kdp-coloring-artisan`

## 5️⃣ API HTTP exposée (`app_studio.py`)

| Route | Rôle |
| :--- | :--- |
| `GET /api/kdp/formats` | Les 16 formats officiels |
| `GET /api/media/search` | Galerie Unsplash + Pixabay |
| `GET /api/canva/auth-url` | URL OAuth 2.0 Canva |
| `GET /api/canva/callback` | Échange du code → `canva_tokens.json` |
| `GET /api/canva/template/{id}` | Gabarit PNG 300 DPI |
| `GET /api/canva/export/{id}` | Export design (live) ou gabarit local (fallback) |

Champs optionnels de `POST /api/books/create` :
`project_type` (`non_fiction` | `coloring_book`), `cover_image_url`,
`single_sided` (verso anti-bavure), `format_kdp` (16 formats).

## ✅ Contrôle qualité avant livraison

```powershell
.\.venv\Scripts\python.exe -m pytest test_suite.py test_extensions.py
```

- `test_suite.py` : 24/24 sans aucune modification (non-régression).
- `test_extensions.py` : formats, specs 300 DPI, connecteurs HTTP mockés
  (Unsplash/Pixabay), Canva mocké, moteur de coloriage mocké.
