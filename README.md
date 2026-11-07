# 📚 Machine de Création de Livres Amazon KDP & Hub d'Automatisation IA

Plateforme professionnelle de production automatisée de **livres Amazon KDP non-fiction** (150+ pages, format 6x9 pouces, normes d'impression KDP) et hub d'API pour **n8n**, **Hermes** et modèles LLM (**Google Gemini** & **Groq**).

---

## 🏗️ Architecture du Projet

```text
mon-espace-ia/
├── kdp_machine.py         # 🏭 Orchestrateur central de la Machine KDP
├── kdp_architect.py       # 🧠 Concepteur du plan (10 chapitres x 5 sections, SEO, mots-clés)
├── kdp_writer.py          # ✍️ Moteur de rédaction séquentielle avec reprise sur incident
├── kdp_formatter.py       # 🎨 Moteur de mise en page conforme KDP 6x9 po (HTML Print & Markdown)
├── generate_article.py    # 💡 Générateur d'articles techniques Markdown
├── server.py              # 🌐 Hub API FastAPI (Gemini / Groq / KDP Endpoints)
├── call_ai.py             # ⚡ Client direct et utilitaire CLI d'appel LLM
├── test_suite.py          # 🧪 Suite de tests automatisés (14 tests unitaires)
├── test.py                # 🔑 Diagnostic de clé d'API et listing des modèles
├── .env                   # 🔒 Clés d'API et configuration locale (non commité)
├── requirements.txt       # 📦 Dépendances Python du projet
└── .gitignore             # 🛡️ Protection des secrets et fichiers temporaires
```

---

## 🏭 1. La Machine de Création de Livres KDP

La machine génère un livre complet de non-fiction prêt pour publication sur Amazon KDP en 3 étapes automatisées :

### Commande tout-en-un :
```powershell
python kdp_machine.py --niche "Maîtriser ses finances personnelles et investir simplement" --cible "Débutants et jeunes actifs"
```

### Options disponibles :
* **Mode Démo rapide (2 chapitres pour tester la chaîne en quelques minutes)** :
  ```powershell
  python kdp_machine.py --demo
  ```
* **Concevoir uniquement l'architecture (Blueprint)** :
  ```powershell
  python kdp_architect.py --niche "Productivité et gestion du temps" --cible "Entrepreneurs"
  ```
* **Reprendre une rédaction interrompue** :
  ```powershell
  python kdp_writer.py --blueprint book_blueprint.json --draft book_draft.json
  ```
* **Formater un livre existant sans régénérer l'IA** :
  ```powershell
  python kdp_formatter.py
  ```

---

## 📦 2. Livrables générés pour chaque livre

| Livrable | Fichier | Description |
| :--- | :--- | :--- |
| **Livre Imprimable KDP (6x9 po)** | `livre_kdp_6x9.html` | Conforme aux marges de reliure KDP (Gutter 0.8"), sauts de page, table des matières, copyright, lettrines. Ouvrez dans Chrome -> *Imprimer* -> *Enregistrer en PDF*. |
| **Manuscrit Complet** | `manuscrit_complet.md` | Manuscrit prêt pour Kindle Create, liseuses eBook ou relecture éditoriale. |
| **Fiche Produit Amazon KDP** | `amazon_description.html` | Description commerciale avec balises HTML autorisées par KDP (`<h2>`, `<b>`, `<ul>`, `<li>`), 7 mots-clés stratégiques et catégories BISAC. |
| **Blueprint Stratégique** | `book_blueprint.json` | Structure complète des 10 chapitres et 50 sous-sections avec objectifs pédagogiques. |

---

## 🌐 3. Hub API FastAPI & Intégration n8n

Le serveur expose des routes pour piloter la machine depuis **n8n**, **Hermes** ou vos webhooks :

```powershell
uvicorn server:app --reload --port 8000
```

### Endpoints disponibles :
* `POST /kdp/blueprint` : Génère le plan complet d'un livre à partir d'une niche et d'une cible.
* `POST /kdp/format` : Compile et formate le livre aux normes KDP 6x9.
* `POST /generate` : Route universelle de complétion LLM (Gemini ou Groq).
* `POST /generate-article` : Génération d'articles techniques en Markdown.
* `GET /docs` : Documentation Swagger interactive sur [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 🧪 4. Validation & Tests

Pour lancer la suite de 14 tests automatisés vérifiant tous les composants locaux :
```powershell
python test_suite.py
```
