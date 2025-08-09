# 🚀 Guide de Déploiement Rapide - Solar Nasih

## ⚡ Déploiement en 10 minutes

### 🎯 Vue d'ensemble
- **Frontend** : Vercel (gratuit)
- **SMA Service** : Render (gratuit/starter)
- **RAG Service** : Render (gratuit/starter)

### 📋 Prérequis
1. Compte GitHub avec le repository Solar Nasih
2. Compte [Render](https://render.com) (gratuit)
3. Compte [Vercel](https://vercel.com) (gratuit)
4. **API Key Gemini** (obligatoire) : [Obtenir ici](https://makersuite.google.com/app/apikey)

---

## 🚀 Déploiement Automatique (Recommandé)

### Option A : Script Python
```bash
cd SolarNasih_Deploiement_Complet
export RENDER_API_KEY="votre_clé_render"
python deploy_render_complete.py
```

### Option B : Déploiement Manuel
Suivez les étapes ci-dessous ↓

---

## 📝 Déploiement Manuel

### 1️⃣ Service SMA sur Render (5 min)

1. **Allez sur [Render Dashboard](https://dashboard.render.com)**
2. **Cliquez "New +" → "Blueprint"**
3. **Connectez votre repository GitHub**
4. **Copiez le contenu de** `SMA_Deploy/render.yaml`
5. **Configurez les variables d'environnement** :
   ```
   GEMINI_API_KEY=votre_clé_gemini
   CORS_ORIGINS=https://votre-app.vercel.app,http://localhost:3000
   ```
6. **Cliquez "Apply"**
7. **Notez l'URL** : `https://solar-nasih-sma.onrender.com`

### 2️⃣ Service RAG sur Render (5 min)

1. **Répétez les étapes ci-dessus**
2. **Utilisez** `RAG_Deploy/render.yaml`
3. **Mêmes variables d'environnement**
4. **Notez l'URL** : `https://solar-nasih-rag.onrender.com`

### 3️⃣ Frontend sur Vercel (3 min)

1. **Allez sur [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Cliquez "New Project"**
3. **Importez votre repository GitHub**
4. **Configurez** :
   - **Framework Preset** : Vite
   - **Root Directory** : `SolarNasih_Template`
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`

5. **Variables d'environnement** :
   ```
   VITE_SMA_API_URL=https://solar-nasih-sma.onrender.com
   VITE_RAG_API_URL=https://solar-nasih-rag.onrender.com
   VITE_APP_NAME=SolarNasih
   VITE_ENVIRONMENT=production
   ```

6. **Cliquez "Deploy"**

---

## ✅ Vérification

### Test des Services
```bash
# Test SMA
curl https://solar-nasih-sma.onrender.com/health

# Test RAG  
curl https://solar-nasih-rag.onrender.com/health

# Test Frontend
curl https://votre-app.vercel.app
```

### Test d'Intégration
1. **Ouvrez votre frontend Vercel**
2. **Testez le chat SMA**
3. **Uploadez un document pour RAG**
4. **Vérifiez les logs dans Render/Vercel**

---

## 🔧 Configuration Avancée

### Variables d'Environnement Optionnelles

#### Pour SMA et RAG
```bash
# APIs supplémentaires (optionnel)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...

# Configuration
ENVIRONMENT=production
PYTHON_VERSION=3.11
```

#### Pour Frontend
```bash
# Fonctionnalités
VITE_ENABLE_CHAT=true
VITE_ENABLE_FILE_UPLOAD=true
VITE_ENABLE_VOICE_INPUT=true

# Limites
VITE_MAX_FILE_SIZE=52428800  # 50MB
VITE_MAX_MESSAGE_LENGTH=4000
```

---

## 🚨 Résolution Rapide

### Service ne démarre pas
1. Vérifiez les logs Render
2. Vérifiez `GEMINI_API_KEY`
3. Attendez 5-10 minutes (cold start)

### Frontend ne se connecte pas
1. Vérifiez les URLs dans Vercel
2. Vérifiez CORS dans Render
3. Testez les APIs directement

### Build errors
1. Vérifiez TypeScript errors
2. Testez localement : `npm run build`
3. Vérifiez Node.js version (18+)

---

## 🎉 Résultats

**Après déploiement, vous aurez :**

- 🌐 **Frontend** : `https://votre-app.vercel.app`
- 🤖 **SMA API** : `https://solar-nasih-sma.onrender.com`
- 🔍 **RAG API** : `https://solar-nasih-rag.onrender.com`
- 📚 **Documentation** : `/docs` sur chaque API

**Fonctionnalités disponibles :**
- ✅ Chat intelligent avec IA
- ✅ Upload et analyse de documents
- ✅ Interface moderne et responsive
- ✅ Simulation énergétique
- ✅ Base de connaissances vectorielle

---

## 💰 Coûts

| Service | Plan | Coût | Limites |
|---------|------|------|---------|
| **Render SMA** | Free | 0€ | 750h/mois, sleep après inactivité |
| **Render RAG** | Free | 0€ | 750h/mois, sleep après inactivité |
| **Vercel Frontend** | Hobby | 0€ | 100GB bande passante/mois |
| **Total** | | **0€/mois** | Parfait pour démo/test |

**Pour la production :** Upgrade vers Render Starter (7$/mois/service)

---

**🚀 Votre Solar Nasih est maintenant en ligne et prêt à révolutionner la gestion solaire !**
