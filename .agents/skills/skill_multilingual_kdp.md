# 🌍 SKILL MULTILINGUAL KDP (FR / EN / ES / DE / AR)

Ce skill régit l'internationalisation intégrale de l'écosystème Amazon KDP pour les 5 langues majeures : **Français (`fr`)**, **Anglais (`en`)**, **Espagnol (`es`)**, **Allemand (`de`)** et **Arabe (`ar`)**.

---

## 🏛️ 1. Matrice des Marchés, Devises et Sens de Lecture

| Code | Langue | Nom Natif | Direction | Marché Amazon Principal | Devise | Césure (Hyphens) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`fr`** | Français | Français | LTR | `amazon.fr` | EUR (€) | `hyphens: auto;` |
| **`en`** | Anglais | English | LTR | `amazon.com` / `amazon.co.uk` | USD ($) / GBP (£) | `hyphens: auto;` |
| **`es`** | Espagnol | Español | LTR | `amazon.es` / `amazon.com.mx` | EUR (€) / USD ($) | `hyphens: auto;` |
| **`de`** | Allemand | Deutsch | LTR | `amazon.de` | EUR (€) | `hyphens: auto;` (Mots composés) |
| **`ar`** | Arabe | العربية | **RTL** | `amazon.ae` / `amazon.sa` / `amazon.eg` | AED / SAR / EGP | **`hyphens: none !important;`** |

---

## 🔤 2. Direction Typographique & Paires de Polices (Google Fonts CDN)

Chaque langue bénéficie d'une paire typographique certifiée sans incompatibilité de glyphes :

### 1. Français (`fr`) — *Garamond Noble*
* **Titre :** `'Cinzel', serif`
* **Corps :** `'EB Garamond', serif`
* **Accents :** Support complet Latin-1 étendu (`é`, `è`, `ê`, `ë`, `à`, `ç`, `ô`, `ù`, `œ`).

### 2. Anglais (`en`) — *Anglo-Saxon Authority*
* **Titre :** `'Cinzel', serif`
* **Corps :** `'Merriweather', serif`
* **Style :** Fort contraste, lisibilité optimale sur liseuse et impression papier.

### 3. Espagnol (`es`) — *Hispano Elegancia*
* **Titre :** `'Playfair Display', serif`
* **Corps :** `'Lora', serif`
* **Accents :** Support des accents aigus (`á`, `é`, `í`, `ó`, `ú`), du tilde (`ñ`) et des points d'exclamation inversés (`¡`, `¿`).

### 4. Allemand (`de`) — *Germanic Precision*
* **Titre :** `'Cinzel', serif`
* **Corps :** `'EB Garamond', serif`
* **Glyphes :** Umlauts majuscules/minuscules (`Ä`, `Ö`, `Ü`, `ä`, `ö`, `ü`) et eszett (`ß`). Gestion prioritaire des césures sur les longs substantifs composés.

### 5. Arabe (`ar`) — *Arabic Majestic (Naskh & Kufi)*
* **Google Fonts recommandées (obligatoires à inclure) :** `Cairo`, `Tajawal`, `Amiri` (et optionnellement `Noto Naskh Arabic`).
* **Titre :** `'Cairo', sans-serif`
* **Corps :** `'Amiri', serif` / `'Tajawal', sans-serif`
* **Spécificité :** Écriture cursive attachée, diacritiques (Tashkeel) optionnels, zéro césure syllabique (`hyphens: none !important;`).

---

## 📖 3. Géométrie de Reliure & Inversion RTL (Gutter Inversion)

En impression papier (Paperback), la reliure doit impérativement s'adapter au sens d'ouverture de l'ouvrage :

### Mode Occidental (LTR : FR, EN, ES, DE) :
* Le livre s'ouvre de gauche à droite.
* **Page Verso (Gauche / Paire) :** Marge intérieure (Gouttière) sur le bord **DROIT**.
* **Page Recto (Droite / Impaire) :** Marge intérieure (Gouttière) sur le bord **GAUCHE**.
```css
@page :left {
  margin-left: 0.55in;
  margin-right: 0.85in; /* Gouttière */
}
@page :right {
  margin-left: 0.85in; /* Gouttière */
  margin-right: 0.55in;
}
```

### Mode Arabe (RTL : AR) — Inversion Chirurgicale :
* Le livre s'ouvre de droite à gauche.
* **Page Verso (Gauche / Paire) :** Marge intérieure (Gouttière) sur le bord **GAUCHE**.
* **Page Recto (Droite / Impaire) :** Marge intérieure (Gouttière) sur le bord **DROIT**.
```css
@page :left {
  margin-left: 0.85in; /* Gouttière inversée */
  margin-right: 0.55in;
}
@page :right {
  margin-left: 0.55in;
  margin-right: 0.85in; /* Gouttière inversée */
}
```

---

## 🚀 4. Moteur SEO Amazon A9 & Limite Stricte de 50 Octets UTF-8

Amazon KDP limite chaque case de recherche backend en **octets UTF-8** :
$$\text{Octets UTF-8} = \text{len}(text.\text{encode}('utf-8')) \le 50$$

* Un caractère ASCII anglais = **1 octet**.
* Un caractère accentué français/espagnol (`é`, `ñ`) ou umlaut allemand (`ä`) = **2 octets**.
* Un caractère arabe (`م`, `ك`, `ت`) = **2 octets**.
* **Conséquence :** En Arabe ou Allemand, 25 caractères peuvent atteindre 50 octets ! Le calcul en nombre de caractères est une erreur éliminatoire.

### Mots Interdits Locaux (TOS Amazon KDP) :
Tout mot laudatif ou commercial générique disqualifie la fiche :
* **FR :** `meilleur`, `gratuit`, `livre`, `kindle`, `vente`, `promo`, `bestseller`
* **EN :** `best`, `free`, `book`, `kindle`, `sale`, `cheap`, `bestseller`
* **ES :** `mejor`, `gratis`, `libro`, `kindle`, `oferta`, `barato`
* **DE :** `beste`, `kostenlos`, `buch`, `kindle`, `angebot`, `billig`
* **AR :** `أفضل`, `مجاني`, `كتاب`, `كيندل`, `تخفيض`, `رخيص`

---

## ⚠️ 5. Alerte Réglementaire Amazon KDP — Broché Arabe vs Kindle eBook

> [!WARNING]
> **Règle KDP Officielle concernant la langue Arabe :**
> Amazon KDP supporte nativement la langue Arabe pour les **Kindle eBooks** (format KFX / Reflowable / Print Replica).
> Cependant, le service d'impression à la demande **Paperback (livre broché papier)** pour l'Arabe fait l'objet de restrictions techniques et géographiques strictes selon les ateliers d'impression Amazon.
> **Protocole recommandé :**
> 1. Déployer en priorité l'édition numérique Kindle eBook.
> 2. Pour le format papier, vérifier l'éligibilité du compte ou compiler en PDF prépresse aplati 300 DPI sans polices dynamiques non incorporées.

---

## 🛠️ 6. API & Endpoints REST Multilingues

* `GET /api/i18n/languages` : Registre des 5 langues, marchés, devises et drapeaux.
* `GET /api/i18n/language/{code}` : Configuration complète, polices Google Fonts et mots interdits.
* `POST /api/seo/audit-keywords` : Audit des 7 slots (50 octets UTF-8, doublons, mots interdits).
* `POST /api/seo/optimize-keywords` : Génération des 7 slots d'intention pour la langue choisie.
* `POST /api/compliance/audit-multilingual` : Audit de conformité HTML/CSS, gouttière RTL et conformité KDP.
