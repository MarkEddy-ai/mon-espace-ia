# 🏛️ MarkEddy KDP Studio — Plateforme SaaS de Production Amazon KDP

**MarkEddy KDP Studio** est une plateforme SaaS industrielle automatisée de conception, rédaction, formatage typographique et publication de livres professionnels de non-fiction pour **Amazon KDP (Broché 6" × 9" et eBook Kindle EPUB 3)**.

---

## 🌟 Fonctionnalités Clés

* **🎨 Direction Artistique & Typographie Haute Couture :** Formatage intérieur strict 6×9 po avec marge de reliure (*Gutter 0.85 po*), lettrines royales, ornements et CSS d'impression certifié KDP.
* **📐 Couverture 300 DPI Dynamique :** Gabarit complet PDF haute résolution avec calcul au micron de la tranche (dos) selon le nombre exact de pages, fond perdu (*Bleed 0.125 po*) et réservation normalisée du code-barres ISBN.
* **📱 Exportation Kindle EPUB 3 :** Fichier eBook reflowable optimisé pour l'écosystème Amazon Kindle.
* **🛒 Pack Marketing & SEO A9 :** Description commerciale en HTML strict KDP, 7 slots de mots-clés backend sans redondance et structure A+ Content.
* **🛡️ Architecture SaaS Multi-Utilisateurs :** 
  * Authentification par jeton JWT conforme **RFC 7519** (HS256) et hachage fort (PBKDF2-HMAC-SHA256 à 100 000 itérations / Bcrypt).
  * Isolation stricte des données et des fichiers par utilisateur.
  * Système de crédits et quotas (3 crédits offerts à l'inscription, 1 crédit par livre, remboursement automatique sur incident).
  * Sécurité anti-Path Traversal sur la distribution de tous les livrables.
* **📚 Livre Pilote Vitrine Intégré :** *"L'INTELLIGENCE FINANCIÈRE PRATIQUE"* (112 pages, QA 100/100) consultable et téléchargeable dès le premier démarrage.

---

## 🏗️ Structure du Projet

```text
mon-espace-ia/
├── app_studio.py              # 🚀 Backend FastAPI SaaS & gestion des tâches d'arrière-plan
├── studio_db.py               # 💾 Base de données SQLite (users, books, quotas & migrations)
├── auth.py                    # 🔐 Authentification JWT (RFC 7519) et hachage de mots de passe
├── static/
│   └── index.html             # ✨ Interface Web Moderne (Tailwind CSS, Obsidienne & Or Impérial)
├── kdp_universal_publishing_engine.py # 📐 Moteur de mise en page CSS 6x9 Print-Ready
├── generate_luxury_cover.py   # 🎨 Moteur graphique de couverture complète 300 DPI (Pillow)
├── kdp_epub_exporter.py       # 📱 Exportateur EPUB 3 Kindle standardisé
├── kdp_marketing.py           # 🛒 Générateur de fiche produit et mots-clés A9
├── kdp_qa.py                  # 🔬 Auditeur de conformité industrielle Amazon KDP
├── Dockerfile                 # 🐳 Image Cloud Playwright Python v1.48.0 (Ubuntu Jammy)
├── docker-compose.yml         # 🚢 Orchestration Docker avec volumes persistants
├── test_suite.py              # 🧪 Banc d'essai automatisé (23 tests unitaires)
├── test_saas_auth.py          # 🧪 Suite de tests SaaS (Auth, Quotas, Isolation, 8 tests)
├── requirements.txt           # 📦 Dépendances Python de production
└── .env.example               # 🔒 Modèle des variables d'environnement
```

---

## 🚀 Démarrage Rapide en Local

### 1. Prérequis
* Python 3.10+
* Navigateur moderne (Chrome, Edge ou Firefox)

### 2. Installation
```bash
# Cloner le dépôt et entrer dans le dossier
git clone <url-du-repo>
cd mon-espace-ia

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate    # Sur Linux/macOS
# .\.venv\Scripts\Activate.ps1 # Sur Windows PowerShell

# Installer les dépendances
pip install -r requirements.txt
playwright install chromium
```

### 3. Configuration de l'environnement
```bash
cp .env.example .env
```
Éditez le fichier `.env` pour définir vos secrets (`GEMINI_API_KEY`, `JWT_SECRET`).

### 4. Lancement de l'application
```bash
python app_studio.py
```
* **Interface Web Studio :** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Documentation OpenAPI :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Identifiants par défaut
* **Compte Administrateur / Démo :** `admin@markeddy.com` / `Admin123!` (999 crédits)
* **Nouvel Utilisateur :** Inscription libre en 1 clic via le bouton *« Créer un Compte »* (3 crédits offerts).

---

## 🐳 Déploiement avec Docker & Docker Compose

Pour un déploiement conteneurisé instantané :

```bash
# Construction et lancement en arrière-plan
docker compose up -d --build

# Consulter les journaux d'exécution
docker compose logs -f

# Arrêter les services
docker compose down
```

Les volumes persistants conservent automatiquement la base SQLite (`kdp_studio.db`) ainsi que l'ensemble des livres générés (`books/`, `couvertures_finales/`, etc.).

---

## 🌐 Procédure de Déploiement en Production sur Serveur VPS (Ubuntu/Debian)

### Étape 1 : Préparation du serveur VPS
Connectez-vous à votre VPS en SSH et installez Docker et Docker Compose :
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl git ufw

# Installation officielle de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Étape 2 : Clonage et configuration
```bash
cd /opt
sudo git clone <url-du-repo> markeddy-studio
cd markeddy-studio
sudo chown -R $USER:$USER .

cp .env.example .env
nano .env  # Définir JWT_SECRET et GEMINI_API_KEY
```

### Étape 3 : Lancement du Studio KDP
```bash
docker compose up -d --build
```

### Étape 4 : Configuration du Reverse-Proxy Nginx & SSL Certbot (HTTPS)
Installez Nginx et configurez le nom de domaine :
```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Créez le fichier `/etc/nginx/sites-available/kdp-studio` :
```nginx
server {
    server_name studio.votredomaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
}
```

Activez le site et générez le certificat SSL gratuit Let's Encrypt :
```bash
sudo ln -s /etc/nginx/sites-available/kdp-studio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d studio.votredomaine.com
```

Votre studio SaaS est désormais accessible en HTTPS sécurisé avec renouvellement automatique des certificats.

---

## ☁️ Déploiement Cloud en 1 Clic (Render / Railway)

Le [`Dockerfile`](Dockerfile) utilise l'expansion dynamique de port `CMD sh -c "uvicorn app_studio:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"` :
* **Render :** Créez un nouveau *Web Service*, connectez votre dépôt Git, sélectionnez l'environnement *Docker*. Render injecte automatiquement `$PORT` et démarre le service.
* **Railway :** Déployez depuis votre dépôt GitHub. Configurez un volume persistant monté sur `/app/books` et `/app/kdp_studio.db`.

---

## 🧪 Banc d'Essai & Validation Automatisée

Pour lancer l'ensemble des validations avant mise en ligne :

```bash
# 1. Suite de tests du moteur KDP (23 tests d'intégration)
python -m pytest test_suite.py

# 2. Suite de tests de sécurité SaaS (Auth JWT, Quotas, Isolation)
python test_saas_auth.py
```

Résultats attendus :
* `test_suite.py` : **23/23 tests réussis**
* `test_saas_auth.py` : **8/8 tests réussis**

---

## 📄 Licence & Propriété
Développé par le Studio **MarkEddy**. Tous droits réservés.
