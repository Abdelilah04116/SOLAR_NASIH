# 🚀 Solar Nasih - Fichiers de Déploiement

Ce dossier contient tous les fichiers nécessaires pour déployer votre **Solar Nasih SMA** sur différentes plateformes.

## 📁 Structure des Fichiers

### 🐳 **Docker & Containerisation**
- `Dockerfile` - Configuration Docker pour containeriser l'application
- `docker-compose.yml` - Orchestration multi-services (API + Streamlit)

### 🌐 **Plateformes de Déploiement**

#### **Render** (Recommandé) ⭐⭐⭐⭐⭐
- `render.yaml` - Configuration automatique pour Render
- `render_fixed.yaml` - **NOUVEAU** Configuration corrigée (recommandé)
- **Avantages** : 750h/mois gratuites, SSL automatique, déploiement GitHub

#### **Railway**
- `railway.json` - Configuration pour Railway
- **Avantages** : $5 crédit/mois, déploiement simple

#### **Heroku**
- `Procfile` - Configuration pour Heroku
- `runtime.txt` - Version Python spécifiée

#### **Streamlit Cloud**
- `.streamlit/config.toml` - Configuration Streamlit
- **Avantages** : Déploiement gratuit illimité pour l'interface

### ⚙️ **Configuration**
- `env.example` - Template des variables d'environnement
- `deploy.sh` - Script de déploiement automatisé
- `DEPLOYMENT.md` - Guide détaillé de déploiement
- `DEPLOYMENT_FIXED.md` - **NOUVEAU** Guide corrigé (recommandé)

### 📦 **Requirements (Dépendances)**
- `requirements_deploy.txt` - **NOUVEAU** Dépendances complètes
- `requirements_minimal.txt` - **NOUVEAU** Dépendances minimales (recommandé)

## 🎯 **Déploiement Rapide (Recommandé)**

### Option 1 : Render avec fichiers corrigés
```bash
# Copiez les fichiers corrigés
copy render_fixed.yaml ..\SolarNasih_SMA\render.yaml
copy requirements_minimal.txt ..\SolarNasih_SMA\requirements.txt
copy runtime.txt ..\SolarNasih_SMA\runtime.txt

# Poussez sur GitHub
cd ..\SolarNasih_SMA
git add .
git commit -m "Fix deployment configuration"
git push origin main

# Déployez sur Render
# Allez sur render.com et connectez votre repo
```

### Option 2 : Script Automatisé
```bash
cd SolarNasih_Deploiement
./deploy.sh
```

### Option 3 : Déploiement Manuel

#### **Render (Recommandé)**
1. Copiez `render_fixed.yaml` à la racine de votre projet
2. Allez sur [render.com](https://render.com)
3. Connectez votre repo GitHub
4. Render détectera automatiquement la configuration
5. Ajoutez vos variables d'environnement

#### **Docker Local**
```bash
# Copiez les fichiers Docker
cp Dockerfile ../SolarNasih_SMA/
cp docker-compose.yml ../SolarNasih_SMA/

# Démarrez les services
cd ../SolarNasih_SMA
docker-compose up -d
```

## 🔧 **Variables d'Environnement**

Copiez `env.example` vers `.env` et configurez :
```bash
GEMINI_API_KEY=votre_clé_gemini
TAVILY_API_KEY=votre_clé_tavily
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
```

## 📋 **Instructions par Plateforme**

### **Render (Recommandé)**
1. Utilisez `render_fixed.yaml` (corrigé)
2. Utilisez `requirements_minimal.txt`
3. Ajoutez `PYTHON_VERSION=3.11.0`
4. Poussez sur GitHub
5. Connectez sur Render.com

### **Railway**
1. Utilisez `requirements_minimal.txt`
2. Importez sur Railway.app
3. Configurez les variables d'environnement

### **Heroku**
1. Utilisez `requirements_minimal.txt`
2. Copiez `Procfile` et `runtime.txt`
3. Installez Heroku CLI
4. Déployez avec `git push heroku main`

### **Streamlit Cloud**
1. Copiez `.streamlit/` à la racine du projet
2. Allez sur share.streamlit.io
3. Connectez votre repo GitHub
4. Sélectionnez `streamlit_app.py`

## 🐛 **Résolution des Problèmes**

### Erreur : "No matching distribution found"
**Solution :** Utilisez `requirements_minimal.txt`

### Erreur : "Python version incompatible"
**Solution :** Ajoutez `PYTHON_VERSION=3.11.0`

### Erreur : "Build failed"
**Solution :** Vérifiez les variables d'environnement

## 🎉 **Félicitations !**

Votre **Solar Nasih SMA** est maintenant prêt pour le déploiement !

**URLs typiques après déploiement :**
- 🌐 **API** : `https://solar-nasih-api.onrender.com`
- 📱 **Interface** : `https://solar-nasih-streamlit.onrender.com`
- 📚 **Documentation** : `https://solar-nasih-api.onrender.com/docs`

---

**🚀 Votre SMA Solar Nasih va maintenant conquérir le monde ! ☀️** 