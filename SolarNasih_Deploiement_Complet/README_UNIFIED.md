# 🚀 SOLAR NASIH - Déploiement Unifié

## 📋 Vue d'ensemble

Ce dossier contient **une seule commande** pour déployer tout le projet SolarNasih (SMA + RAG + Template) sur Render.

## 🎯 Déploiement en Une Seule Commande

### ⚡ Méthode Rapide

**Sur Windows (PowerShell) :**
```powershell
.\deploy-unified.ps1
```

**Sur Linux/Mac (Bash) :**
```bash
./deploy-unified.sh
```

**Ou directement avec Python :**
```bash
python SolarNasih_Deploiement_Complet/deploy_render_unified.py
```

### 🔧 Ce que fait la commande

1. ✅ **Vérifie** tous les composants (SMA, RAG, Template)
2. 📝 **Crée** le fichier `render-unified.yaml`
3. 🎯 **Génère** les scripts de déploiement
4. 📋 **Affiche** les instructions pour Render

## 📊 Services Déployés

| Service | Type | URL | Description |
|---------|------|-----|-------------|
| `solar-nasih-sma` | API Python | `https://solar-nasih-sma.onrender.com` | Solar Management Assistant |
| `solar-nasih-rag` | API Python | `https://solar-nasih-rag.onrender.com` | Retrieval-Augmented Generation |
| `solar-nasih-frontend` | App Node.js | `https://solar-nasih-frontend.onrender.com` | Interface React/TypeScript |
| `solar-nasih-redis` | Cache Redis | `redis://solar-nasih-redis.onrender.com` | Cache partagé |
| `solar-nasih-qdrant` | Base Docker | `https://solar-nasih-qdrant.onrender.com` | Base de données vectorielle |

## 🚀 Étapes de Déploiement

### 1. Préparation
```bash
# Exécutez la commande unifiée
python SolarNasih_Deploiement_Complet/deploy_render_unified.py
```

### 2. Sur Render.com
1. 🌐 Allez sur [render.com](https://render.com)
2. 🔗 Connectez votre repository Git
3. 📋 Créez un nouveau **Blueprint**
4. 📄 Copiez le contenu de `render-unified.yaml`
5. 🔑 Configurez vos variables d'environnement

### 3. Variables d'environnement requises

**Pour SMA :**
- `GEMINI_API_KEY` - Clé Google Gemini
- `TAVILY_API_KEY` - Clé Tavily

**Pour RAG :**
- `GEMINI_API_KEY` - Clé Google Gemini
- `OPENAI_API_KEY` - Clé OpenAI
- `ANTHROPIC_API_KEY` - Clé Anthropic

**Automatiques :**
- `REDIS_URL` - Configuré automatiquement
- `QDRANT_URL` - Configuré automatiquement
- `VITE_SMA_API_URL` - Configuré automatiquement
- `VITE_RAG_API_URL` - Configuré automatiquement

### 4. Déploiement
- 🚀 Cliquez sur **"Apply"** pour déployer
- ⏱️ Attendez 10-15 minutes pour le premier déploiement
- ✅ Tous les services seront créés automatiquement

## 📁 Structure des Fichiers

```
SolarNasih_Deploiement_Complet/
├── deploy_render_unified.py      # Script principal
├── deploy-unified.ps1           # Script PowerShell (Windows)
├── deploy-unified.sh            # Script Bash (Linux/Mac)
├── render-unified.yaml          # Configuration Render (généré)
├── requirements_sma.txt         # Dépendances SMA
├── requirements_rag.txt         # Dépendances RAG
├── Dockerfile.qdrant           # Docker pour Qdrant
└── README_UNIFIED.md           # Ce fichier
```

## 🔧 Build Commands et Start Commands

### Service SMA
- **Build** : `pip install -r SolarNasih_Deploiement_Complet/requirements_sma.txt`
- **Start** : `cd SolarNasih_SMA && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Service RAG
- **Build** : `pip install -r SolarNasih_Deploiement_Complet/requirements_rag.txt`
- **Start** : `cd SolarNasih_RAG && uvicorn api_simple:app --host 0.0.0.0 --port $PORT`

### Service Frontend
- **Build** : `cd SolarNasih_Template && npm install && npm run build`
- **Start** : `cd SolarNasih_Template && npm run preview -- --host 0.0.0.0 --port $PORT`

### Service Qdrant
- **Build** : Géré par Docker
- **Start** : Géré par Docker

### Service Redis
- **Build** : Géré par Render
- **Start** : Géré par Render

## 🎯 Avantages de cette approche

✅ **Une seule commande** pour tout configurer  
✅ **Configuration automatique** des URLs entre services  
✅ **Gestion automatique** des variables d'environnement  
✅ **Déploiement en parallèle** de tous les services  
✅ **Scripts multiplateformes** (Windows/Linux/Mac)  
✅ **Documentation complète** et instructions claires  

## 🚨 Dépannage

### Erreur "Composants manquants"
```bash
# Assurez-vous d'être dans le répertoire racine
cd /chemin/vers/SOLAR_NASIH
```

### Erreur de permissions (Linux/Mac)
```bash
chmod +x deploy-unified.sh
```

### Erreur PowerShell (Windows)
```powershell
# Exécutez en tant qu'administrateur ou changez la politique
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que tous les composants sont présents
2. Assurez-vous d'avoir les bonnes clés API
3. Consultez les logs Render pour chaque service
4. Vérifiez que les URLs sont correctement configurées

---

**🎉 Déploiement unifié prêt ! Une seule commande pour tout déployer !**
