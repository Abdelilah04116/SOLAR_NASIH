FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements_sma.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements_sma.txt

# Copier le code source SMA
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p logs static

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
