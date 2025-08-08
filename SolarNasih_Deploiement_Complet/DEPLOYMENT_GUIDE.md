# 🚀 SolarNasih - Guide de Déploiement Complet

## 📋 Vue d'ensemble

Ce guide vous accompagne pour déployer **SolarNasih** en utilisant l'approche séparée :
- **SMA** : Déployé sur Render
- **RAG** : Déployé sur Render  
- **Frontend** : Déployé sur Vercel

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Service SMA   │    │   Service RAG   │
│   (Vercel)      │◄──►│   (Render)      │    │   (Render)      │
│                 │    │                 │    │                 │
│ - React/TS      │    │ - FastAPI       │    │ - FastAPI       │
│ - Interface     │    │ - IA Assistant  │    │ - Vector DB     │
│ - Upload Files  │    │ - Chat          │    │ - Document Q&A  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 Structure des Fichiers

```
SolarNasih_Deploiement_Complet/
├── SMA_Deploy/              # Service SMA
│   ├── requirements.txt
│   ├── render.yaml
│   ├── env.example
│   └── README.md
├── RAG_Deploy/              # Service RAG
│   ├── requirements.txt
│   ├── render.yaml
│   ├── env.example
│   └── README.md
├── Frontend_Deploy/         # Frontend
│   ├── vercel.json
│   ├── package.json
│   ├── env.example
│   └── README.md
├── Dockerfile.qdrant        # Base vectorielle
├── requirements_unified.txt # Dépendances unifiées
└── DEPLOYMENT_GUIDE.md     # Ce guide
```

## 🚀 Ordre de Déploiement

### 1️⃣ Service SMA (Render)
**Temps estimé : 10-15 minutes**

1. Suivez le guide dans `SMA_Deploy/README.md`
2. Configurez les API Keys (Gemini obligatoire)
3. Déployez via Render Blueprint
4. Notez l'URL : `https://solar-nasih-sma.onrender.com`

### 2️⃣ Service RAG (Render)
**Temps estimé : 10-15 minutes**

1. Suivez le guide dans `RAG_Deploy/README.md`
2. Configurez les API Keys (Gemini obligatoire)
3. Déployez via Render Blueprint
4. Notez l'URL : `https://solar-nasih-rag.onrender.com`

### 3️⃣ Frontend (Vercel)
**Temps estimé : 5-10 minutes**

1. Suivez le guide dans `Frontend_Deploy/README.md`
2. Configurez les URLs des APIs
3. Déployez via Vercel
4. Votre app sera accessible sur Vercel

## 🔑 Configuration des API Keys

### API Keys Requises

| Service | Clé | Obligatoire | Où l'obtenir |
|---------|-----|-------------|--------------|
| **Gemini** | `GEMINI_API_KEY` | ✅ | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **OpenAI** | `OPENAI_API_KEY` | ❌ | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **Anthropic** | `ANTHROPIC_API_KEY` | ❌ | [Anthropic Console](https://console.anthropic.com/) |
| **Tavily** | `TAVILY_API_KEY` | ❌ | [Tavily](https://tavily.com/) |

### Configuration

1. **Dans Render (SMA et RAG)** :
   - Variables d'environnement → Ajoutez les clés

2. **Dans Vercel (Frontend)** :
   - Settings → Environment Variables → Ajoutez les URLs

## 🧪 Tests de Validation

### Test des Services

```bash
# Test SMA
curl https://solar-nasih-sma.onrender.com/health

# Test RAG
curl https://solar-nasih-rag.onrender.com/health

# Test Frontend
curl https://solar-nasih-frontend.vercel.app
```

### Test d'Intégration

1. **Ouvrez le frontend** dans votre navigateur
2. **Testez le chat** avec SMA
3. **Uploadez un document** et testez RAG
4. **Vérifiez les logs** dans Render et Vercel

## 🔧 Configuration Avancée

### Services Optionnels

Chaque service Render inclut automatiquement :
- **Redis** : Cache et sessions
- **Qdrant** : Base vectorielle pour RAG

### Variables d'Environnement

Consultez les fichiers `env.example` dans chaque dossier pour :
- Configuration détaillée
- Variables optionnelles
- Paramètres de performance

## 🚨 Dépannage

### Erreurs Communes

1. **Service ne démarre pas** :
   - Vérifiez les logs Render
   - Contrôlez les API Keys
   - Vérifiez `requirements.txt`

2. **Frontend ne se connecte pas** :
   - Vérifiez les URLs dans Vercel
   - Contrôlez la configuration CORS
   - Testez les APIs directement

3. **Erreurs de build** :
   - Vérifiez les erreurs TypeScript
   - Contrôlez les dépendances
   - Testez localement

### Logs et Monitoring

- **Render** : Logs dans l'interface web
- **Vercel** : Logs dans l'interface web
- **Health Checks** : `/health` endpoints

## 📞 Support

### Ressources

- [Documentation Render](https://render.com/docs)
- [Documentation Vercel](https://vercel.com/docs)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Vite](https://vitejs.dev/)

### En cas de problème

1. Vérifiez les logs de déploiement
2. Testez localement chaque composant
3. Vérifiez la configuration des variables d'environnement
4. Consultez les guides spécifiques dans chaque dossier

## 🔄 Mise à Jour

### Déploiement Automatique

- **Render** : Redéploie automatiquement sur push GitHub
- **Vercel** : Redéploie automatiquement sur push GitHub

### Déploiement Manuel

```bash
# Render
# Via l'interface web ou API

# Vercel
vercel --prod
```

## 💰 Coûts

### Render (Gratuit)
- **SMA Service** : Free tier (limité)
- **RAG Service** : Free tier (limité)
- **Redis** : Free tier
- **Qdrant** : Free tier

### Vercel (Gratuit)
- **Frontend** : Free tier (généreux)
- **Bandwidth** : 100GB/mois
- **Builds** : 6000 minutes/mois

## 🎉 Félicitations !

Une fois tous les services déployés, votre application SolarNasih sera accessible via :
```
https://solar-nasih-frontend.vercel.app
```

**Fonctionnalités disponibles :**
- ✅ Chat intelligent avec SMA
- ✅ Upload et analyse de documents avec RAG
- ✅ Interface moderne et responsive
- ✅ Gestion des fichiers multimédia
- ✅ Base de connaissances vectorielle

---

**🚀 Votre application SolarNasih est maintenant prête pour la production !**
