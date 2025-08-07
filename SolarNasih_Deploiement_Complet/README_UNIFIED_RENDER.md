# 🚀 SOLAR NASIH - Déploiement Unifié sur Render

## 📋 Vue d'ensemble

Ce dossier contient **un script unifié** qui démarre SMA + RAG + Template en un seul service sur Render.

## 🎯 Fichiers Créés

### 📁 **Fichiers principaux :**

1. **`start_all_unified.py`** - Script qui démarre tous les services
2. **`build_for_render.py`** - Script de build pour Render
3. **`startup.py`** - Script de démarrage pour Render (généré)
4. **`render-unified-config.yaml`** - Configuration Render (généré)

## 🚀 Build Command et Start Command pour Render

### 🔨 **Build Command :**
```bash
python SolarNasih_Deploiement_Complet/build_for_render.py
```

### 🚀 **Start Command :**
```bash
python startup.py
```

## 📊 Ce que fait le Build Command

Le **Build Command** exécute `build_for_render.py` qui :

1. ✅ **Vérifie** tous les composants (SMA, RAG, Template)
2. 📦 **Installe** les dépendances Python unifiées
3. 📦 **Installe** les dépendances Node.js
4. 🔨 **Build** le frontend React
5. 📝 **Crée** le fichier `startup.py`
6. ☁️ **Génère** la configuration Render

## 🎯 Ce que fait le Start Command

Le **Start Command** exécute `startup.py` qui :

1. 🚀 **Démarre** SMA API sur le port 8000
2. 🤖 **Démarre** RAG API sur le port 8001
3. 🌐 **Démarre** Frontend sur le port 3000
4. 🔄 **Gère** tous les services en parallèle

## 📋 Configuration Render Complète

### 🔧 **Service Principal :**
- **Environment** : `python`
- **Build Command** : `python SolarNasih_Deploiement_Complet/build_for_render.py`
- **Start Command** : `python startup.py`

### 🔑 **Variables d'environnement requises :**

```yaml
envVars:
  - key: GEMINI_API_KEY
    sync: false
  - key: TAVILY_API_KEY
    sync: false
  - key: OPENAI_API_KEY
    sync: false
  - key: ANTHROPIC_API_KEY
    sync: false
  - key: PYTHON_VERSION
    value: 3.11
  - key: NODE_VERSION
    value: 18
  - key: ENVIRONMENT
    value: production
  - key: SMA_PORT
    value: 8000
  - key: RAG_PORT
    value: 8001
  - key: FRONTEND_PORT
    value: 3000
```

## 🎯 Configuration Blueprint Render

Copiez cette configuration dans votre Blueprint Render :

```yaml
services:
  # Service unifié SolarNasih
  - type: web
    name: solar-nasih-unified
    env: python
    buildCommand: python SolarNasih_Deploiement_Complet/build_for_render.py
    startCommand: python startup.py
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11
      - key: NODE_VERSION
        value: 18
      - key: ENVIRONMENT
        value: production
      - key: SMA_PORT
        value: 8000
      - key: RAG_PORT
        value: 8001
      - key: FRONTEND_PORT
        value: 3000

  # Service Redis (optionnel)
  - type: redis
    name: solar-nasih-redis
    plan: free
    maxmemoryPolicy: allkeys-lru

  # Service Qdrant (optionnel)
  - type: web
    name: solar-nasih-qdrant
    env: docker
    dockerfilePath: ./SolarNasih_Deploiement_Complet/Dockerfile.qdrant
    envVars:
      - key: QDRANT__SERVICE__HTTP_PORT
        value: 6333
      - key: QDRANT__SERVICE__GRPC_PORT
        value: 6334
```

## 🚀 Étapes de Déploiement

### 1. Préparation
```bash
# Le build script sera exécuté automatiquement par Render
# Pas besoin de l'exécuter localement
```

### 2. Sur Render.com
1. 🌐 Allez sur [render.com](https://render.com)
2. 🔗 Connectez votre repository Git
3. 📋 Créez un nouveau **Blueprint**
4. 📄 Copiez la configuration ci-dessus
5. 🔑 Configurez vos variables d'environnement

### 3. Variables d'environnement à configurer
- `GEMINI_API_KEY` - Votre clé Google Gemini
- `TAVILY_API_KEY` - Votre clé Tavily
- `OPENAI_API_KEY` - Votre clé OpenAI
- `ANTHROPIC_API_KEY` - Votre clé Anthropic

### 4. Déploiement
- 🚀 Cliquez sur **"Apply"** pour déployer
- ⏱️ Attendez 10-15 minutes pour le premier déploiement
- ✅ Tous les services seront créés automatiquement

## 📊 Services Déployés

| Service | Type | URL | Description |
|---------|------|-----|-------------|
| `solar-nasih-unified` | Web Python | `https://solar-nasih-unified.onrender.com` | SMA + RAG + Frontend unifiés |
| `solar-nasih-redis` | Redis | `redis://solar-nasih-redis.onrender.com` | Cache (optionnel) |
| `solar-nasih-qdrant` | Web Docker | `https://solar-nasih-qdrant.onrender.com` | Base vectorielle (optionnel) |

## 🎯 Avantages de cette approche

✅ **Un seul service** pour SMA + RAG + Frontend  
✅ **Build automatique** de tous les composants  
✅ **Démarrage unifié** en un seul processus  
✅ **Gestion automatique** des ports  
✅ **Configuration simplifiée** pour Render  
✅ **Déploiement rapide** en une seule étape  

## 🚨 Dépannage

### Erreur de build
1. Vérifiez que tous les composants sont présents
2. Assurez-vous d'avoir les bonnes clés API
3. Consultez les logs de build sur Render

### Erreur de démarrage
1. Vérifiez les variables d'environnement
2. Consultez les logs de démarrage sur Render
3. Vérifiez que les ports ne sont pas en conflit

### Services non accessibles
1. Attendez que le déploiement soit terminé
2. Vérifiez les URLs générées par Render
3. Consultez les logs pour les erreurs

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que tous les composants sont présents
2. Assurez-vous d'avoir les bonnes clés API
3. Consultez les logs Render pour chaque service
4. Vérifiez que les URLs sont correctement configurées

---

**🎉 Déploiement unifié prêt ! Un seul service pour tout le projet !**
