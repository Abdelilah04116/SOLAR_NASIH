# 🚀 Solar Nasih - Déploiement Complet (SMA + RAG + Template)

Ce dossier contient tous les fichiers nécessaires pour déployer **Solar Nasih** complet avec tous ses composants :
- **SMA (Solar Management Assistant)** - Assistant de gestion solaire
- **RAG (Retrieval-Augmented Generation)** - Système de recherche et génération
- **Template Frontend** - Interface utilisateur React/TypeScript

## 🏗️ Architecture de Déploiement

```
Solar Nasih Complet
├── 🌐 Frontend (React/TypeScript) - Port 3000
├── 🤖 SMA API (FastAPI) - Port 8000
├── 🔍 RAG API (FastAPI) - Port 8001
├── 🗄️ Qdrant Vector DB - Port 6333
├── ⚡ Redis Cache - Port 6379
└── 🌍 Nginx Reverse Proxy - Port 80/443
```

## 🚀 Déploiement Rapide

### Option 1 : Docker Compose (Recommandé)

```bash
# Cloner le projet
git clone <votre-repo>
cd SolarNasih_Deploiement_Complet

# Configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos clés API

# Démarrer tous les services
docker-compose up -d

# Vérifier les services
docker-compose ps
```

### Option 2 : Déploiement Cloud (Render)

```bash
# Utiliser le script de déploiement automatique
python deploy_render_complete.py
```

### Option 3 : Déploiement Manuel

```bash
# Déployer chaque composant séparément
./deploy_sma.sh
./deploy_rag.sh
./deploy_frontend.sh
```

## 📁 Structure des Fichiers

### 🐳 **Docker & Containerisation**
- `docker-compose.yml` - Orchestration complète de tous les services
- `Dockerfile.sma` - Container pour le SMA
- `Dockerfile.rag` - Container pour le RAG
- `Dockerfile.frontend` - Container pour le frontend
- `nginx.conf` - Configuration du reverse proxy

### 🌐 **Plateformes de Déploiement**
- `render-complete.yaml` - Configuration Render pour tous les services
- `railway-complete.json` - Configuration Railway
- `heroku-complete.yml` - Configuration Heroku
- `deploy_commands_complete.txt` - Commandes de déploiement

### ⚙️ **Configuration**
- `env.example` - Template des variables d'environnement
- `deploy_render_complete.py` - Script de déploiement automatique
- `deploy.sh` - Script de déploiement principal

## 🔧 Configuration des Variables d'Environnement

Copiez `env.example` vers `.env` et configurez :

```bash
# Clés API
GEMINI_API_KEY=votre_clé_gemini
TAVILY_API_KEY=votre_clé_tavily
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic

# Configuration des services
SMA_API_URL=http://localhost:8000
RAG_API_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000

# Base de données
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379

# Environnement
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
NODE_VERSION=18
```

## 🎯 URLs des Services

Après déploiement, vos services seront disponibles sur :

- 🌐 **Frontend** : `http://localhost:3000`
- 🤖 **SMA API** : `http://localhost:8000`
- 🔍 **RAG API** : `http://localhost:8001`
- 📚 **SMA Docs** : `http://localhost:8000/docs`
- 📚 **RAG Docs** : `http://localhost:8001/docs`
- 🗄️ **Qdrant** : `http://localhost:6333`
- ⚡ **Redis** : `redis://localhost:6379`

## 🚀 Déploiement sur Render

### Configuration Automatique

1. **Utilisez le script automatique** :
```bash
python deploy_render_complete.py
```

2. **Ou configurez manuellement** :
   - Créez 3 Web Services sur Render
   - Utilisez les commandes de `deploy_commands_complete.txt`
   - Configurez les variables d'environnement

### Services Render

1. **SMA Service** :
   - Build Command : `pip install -r requirements_sma.txt`
   - Start Command : `cd SolarNasih_SMA && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **RAG Service** :
   - Build Command : `pip install -r requirements_rag.txt`
   - Start Command : `cd SolarNasih_RAG && uvicorn api_simple:app --host 0.0.0.0 --port $PORT`

3. **Frontend Service** :
   - Build Command : `cd SolarNasih_Template && npm install && npm run build`
   - Start Command : `cd SolarNasih_Template && npm run preview`

## 🔍 Monitoring et Logs

### Vérification des Services

```bash
# Vérifier tous les services
docker-compose ps

# Voir les logs
docker-compose logs -f

# Vérifier la santé des APIs
curl http://localhost:8000/health  # SMA
curl http://localhost:8001/health  # RAG
```

### Logs par Service

```bash
# Logs SMA
docker-compose logs -f solar-nasih-sma

# Logs RAG
docker-compose logs -f solar-nasih-rag

# Logs Frontend
docker-compose logs -f solar-nasih-frontend
```

## 🛠️ Maintenance

### Mise à Jour

```bash
# Mettre à jour tous les services
docker-compose pull
docker-compose up -d

# Ou mettre à jour un service spécifique
docker-compose up -d --no-deps solar-nasih-sma
```

### Sauvegarde

```bash
# Sauvegarder les données
docker-compose exec qdrant qdrant backup /backup
docker-compose exec redis redis-cli BGSAVE
```

## 🐛 Résolution des Problèmes

### Erreur : "Port already in use"
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :3000

# Arrêter les services conflictuels
docker-compose down
```

### Erreur : "API key not found"
- Vérifiez que toutes les clés API sont configurées dans `.env`
- Redémarrez les services : `docker-compose restart`

### Erreur : "Database connection failed"
```bash
# Redémarrer les bases de données
docker-compose restart qdrant redis
```

## 🎉 Félicitations !

Votre **Solar Nasih Complet** est maintenant déployé avec tous ses composants !

**URLs typiques après déploiement :**
- 🌐 **Interface** : `https://solar-nasih-frontend.onrender.com`
- 🤖 **SMA API** : `https://solar-nasih-sma.onrender.com`
- 🔍 **RAG API** : `https://solar-nasih-rag.onrender.com`
- 📚 **Documentation** : `https://solar-nasih-sma.onrender.com/docs`

---

**🚀 Solar Nasih est maintenant prêt à révolutionner la gestion solaire ! ☀️**
