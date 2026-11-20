# ==============================================================================
# MARKEDDY KDP STUDIO - DOCKERFILE PRODUCTION POUR CLOUD (VPS, RENDER, RAILWAY)
# Image officielle Playwright Python v1.48.0 (Ubuntu Jammy)
# Inclut Chromium, dépendances d'impression PDF et polices système typographiques
# ==============================================================================

FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Variables d'environnement pour Python et Playwright
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PORT=8000

# Installation des polices typographiques et utilitaires système pour rendu 300 DPI
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    fontconfig \
    curl \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'ensemble du code applicatif
COPY . .

# Création des dossiers de persistance
RUN mkdir -p /app/books /app/static /app/couvertures_finales /app/interieurs_finaux /app/ebooks_finaux

# Port d'écoute par défaut
EXPOSE 8000

# Commande de démarrage compatible Cloud VPS, Render et Railway (liaison dynamique avec $PORT)
CMD sh -c "uvicorn app_studio:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"
