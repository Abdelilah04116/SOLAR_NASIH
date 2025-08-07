# 🚀 Guide de Déploiement Complet - Solar Nasih

Ce guide vous accompagne pour déployer **Solar Nasih** complet avec tous ses composants sur différentes plateformes.

## 📋 Table des Matières

1. [Architecture du Système](#architecture-du-système)
2. [Prérequis](#prérequis)
3. [Déploiement Docker Local](#déploiement-docker-local)
4. [Déploiement Render (Recommandé)](#déploiement-render)
5. [Déploiement Railway](#déploiement-railway)
6. [Déploiement Heroku](#déploiement-heroku)
7. [Configuration des Variables d'Environnement](#configuration-des-variables-denvironnement)
8. [Monitoring et Maintenance](#monitoring-et-maintenance)
9. [Résolution des Problèmes](#résolution-des-problèmes)

## 🏗️ Architecture du Système

```
Solar Nasih Complet
├── 🌐 Frontend (React/TypeScript) - Port 3000
│   ├── Interface utilisateur moderne
│   ├── Communication avec SMA et RAG APIs
│   └── Gestion des conversations
├── 🤖 SMA API (FastAPI) - Port 8000
│   ├── Assistant de gestion solaire
│   ├── Intégration Gemini et Tavily
│   └── Gestion des projets solaires
├── 🔍 RAG API (FastAPI) - Port 8001
│   ├── Recherche et génération augmentée
│   ├── Base de connaissances vectorielle
│   └── Traitement multimodal
├── 🗄️ Qdrant Vector DB - Port 6333
│   └── Stockage des embeddings
├── ⚡ Redis Cache - Port 6379
│   └── Cache et sessions
└── 🌍 Nginx Reverse Proxy - Port 80/443
    └── Routage et SSL
```

## ✅ Prérequis

### Système
- **Docker** et **Docker Compose** (pour le déploiement local)
- **Git** pour la gestion du code
- **Python 3.11+** (pour les scripts de déploiement)
- **Node.js 18+** (pour le frontend)

### Clés API
- **Google Gemini API Key**
- **Tavily API Key**
- **OpenAI API Key** (optionnel)
- **Anthropic API Key** (optionnel)

## 🐳 Déploiement Docker Local

### Étape 1: Préparation

```bash
# Cloner le projet
git clone <votre-repo>
cd SOLAR_NASIH

# Configurer l'environnement
cp SolarNasih_Deploiement_Complet/env.example .env
# Éditer .env avec vos clés API
```

### Étape 2: Démarrage

```bash
# Utiliser le script automatisé
./SolarNasih_Deploiement_Complet/deploy.sh

# Ou déployer manuellement
cd SolarNasih_Deploiement_Complet
docker-compose up -d
```

### Étape 3: Vérification

```bash
# Vérifier les services
docker-compose ps

# Vérifier les logs
docker-compose logs -f

# Tester les APIs
curl http://localhost:8000/health  # SMA
curl http://localhost:8001/health  # RAG
```

## 🌐 Déploiement Render (Recommandé)

### Option 1: Déploiement Automatique

```bash
# Exécuter le script de déploiement
python SolarNasih_Deploiement_Complet/deploy_render_complete.py
```

### Option 2: Déploiement Manuel

1. **Allez sur [render.com](https://render.com)**
2. **Créez un compte ou connectez-vous**
3. **Cliquez sur "New +" → "Blueprint"**
4. **Connectez votre repo GitHub**
5. **Sélectionnez le fichier `render-complete.yaml`**
6. **Configurez vos variables d'environnement**
7. **Cliquez sur "Apply"**

### Configuration des Services

#### Service SMA
- **Build Command**: `pip install -r SolarNasih_Deploiement_Complet/requirements_sma.txt`
- **Start Command**: `cd SolarNasih_SMA && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Variables**: `GEMINI_API_KEY`, `TAVILY_API_KEY`, `ENVIRONMENT=production`

#### Service RAG
- **Build Command**: `pip install -r SolarNasih_Deploiement_Complet/requirements_rag.txt`
- **Start Command**: `cd SolarNasih_RAG && uvicorn api_simple:app --host 0.0.0.0 --port $PORT`
- **Variables**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ENVIRONMENT=production`

#### Service Frontend
- **Build Command**: `cd SolarNasih_Template && npm install && npm run build`
- **Start Command**: `cd SolarNasih_Template && npm run preview -- --host 0.0.0.0 --port $PORT`
- **Variables**: `NODE_ENV=production`

## 🚂 Déploiement Railway

### Étape 1: Préparation

```bash
# Copier la configuration Railway
cp SolarNasih_Deploiement_Complet/railway-complete.json railway.json
```

### Étape 2: Déploiement

1. **Allez sur [railway.app](https://railway.app)**
2. **Connectez votre repo GitHub**
3. **Railway détectera automatiquement la configuration**
4. **Configurez vos variables d'environnement**
5. **Déployez**

## 🏰 Déploiement Heroku

### Étape 1: Préparation

```bash
# Installer Heroku CLI
# Créer les applications
heroku create solar-nasih-sma
heroku create solar-nasih-rag
heroku create solar-nasih-frontend
```

### Étape 2: Configuration

```bash
# Configuration SMA
heroku config:set GEMINI_API_KEY=votre_clé --app solar-nasih-sma
heroku config:set TAVILY_API_KEY=votre_clé --app solar-nasih-sma
heroku config:set ENVIRONMENT=production --app solar-nasih-sma

# Configuration RAG
heroku config:set OPENAI_API_KEY=votre_clé --app solar-nasih-rag
heroku config:set ANTHROPIC_API_KEY=votre_clé --app solar-nasih-rag
heroku config:set ENVIRONMENT=production --app solar-nasih-rag

# Configuration Frontend
heroku config:set NODE_ENV=production --app solar-nasih-frontend
heroku config:set VITE_SMA_API_URL=https://solar-nasih-sma.herokuapp.com --app solar-nasih-frontend
heroku config:set VITE_RAG_API_URL=https://solar-nasih-rag.herokuapp.com --app solar-nasih-frontend
```

### Étape 3: Déploiement

```bash
# Déployer chaque service
git push heroku main --app solar-nasih-sma
git push heroku main --app solar-nasih-rag
git push heroku main --app solar-nasih-frontend
```

## ⚙️ Configuration des Variables d'Environnement

### Variables Obligatoires

```bash
# Clés API
GEMINI_API_KEY=votre_clé_gemini
TAVILY_API_KEY=votre_clé_tavily
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic

# Configuration
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
NODE_VERSION=18
```

### Variables Optionnelles

```bash
# URLs des services (pour le frontend)
VITE_SMA_API_URL=https://solar-nasih-sma.onrender.com
VITE_RAG_API_URL=https://solar-nasih-rag.onrender.com

# Configuration des bases de données
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379

# Logs et monitoring
SMA_LOG_LEVEL=INFO
RAG_LOG_LEVEL=INFO
```

## 📊 Monitoring et Maintenance

### Vérification des Services

```bash
# Docker
docker-compose ps
docker-compose logs -f

# APIs
curl http://localhost:8000/health  # SMA
curl http://localhost:8001/health  # RAG
curl http://localhost:3000         # Frontend
```

### Logs par Service

```bash
# Logs SMA
docker-compose logs -f solar-nasih-sma

# Logs RAG
docker-compose logs -f solar-nasih-rag

# Logs Frontend
docker-compose logs -f solar-nasih-frontend

# Logs Bases de données
docker-compose logs -f solar-nasih-qdrant
docker-compose logs -f solar-nasih-redis
```

### Maintenance

```bash
# Mise à jour
docker-compose pull
docker-compose up -d

# Sauvegarde
docker-compose exec qdrant qdrant backup /backup
docker-compose exec redis redis-cli BGSAVE

# Redémarrage
docker-compose restart
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

# Vérifier les logs
docker-compose logs qdrant
docker-compose logs redis
```

### Erreur : "Build failed"

- Vérifiez les variables d'environnement
- Vérifiez les versions Python/Node.js
- Consultez les logs de build

### Erreur : "Memory limit exceeded"

- Augmentez les ressources allouées
- Optimisez les images Docker
- Utilisez des plans payants sur les plateformes cloud

## 🎯 URLs Typiques Après Déploiement

### Render
- 🌐 **Frontend**: `https://solar-nasih-frontend.onrender.com`
- 🤖 **SMA API**: `https://solar-nasih-sma.onrender.com`
- 🔍 **RAG API**: `https://solar-nasih-rag.onrender.com`
- 📚 **Documentation**: `https://solar-nasih-sma.onrender.com/docs`

### Railway
- 🌐 **Frontend**: `https://solar-nasih-frontend.railway.app`
- 🤖 **SMA API**: `https://solar-nasih-sma.railway.app`
- 🔍 **RAG API**: `https://solar-nasih-rag.railway.app`

### Heroku
- 🌐 **Frontend**: `https://solar-nasih-frontend.herokuapp.com`
- 🤖 **SMA API**: `https://solar-nasih-sma.herokuapp.com`
- 🔍 **RAG API**: `https://solar-nasih-rag.herokuapp.com`

### Local (Docker)
- 🌐 **Frontend**: `http://localhost:3000`
- 🤖 **SMA API**: `http://localhost:8000`
- 🔍 **RAG API**: `http://localhost:8001`
- 🗄️ **Qdrant**: `http://localhost:6333`
- ⚡ **Redis**: `redis://localhost:6379`

## 🎉 Félicitations !

Votre **Solar Nasih Complet** est maintenant déployé avec tous ses composants !

**Prochaines étapes :**
1. Testez toutes les fonctionnalités
2. Configurez un domaine personnalisé
3. Mettez en place le monitoring
4. Configurez les sauvegardes automatiques

---

**🚀 Solar Nasih est maintenant prêt à révolutionner la gestion solaire ! ☀️**
