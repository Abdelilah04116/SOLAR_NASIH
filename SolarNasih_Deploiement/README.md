# 🚀 Solar Nasih - Fichiers de Déploiement

Ce dossier contient tous les fichiers nécessaires pour déployer votre **Solar Nasih SMA** sur différentes plateformes.

## 📁 Structure des Fichiers

### 🐳 **Docker & Containerisation**
- `Dockerfile` - Configuration Docker pour containeriser l'application
- `docker-compose.yml` - Orchestration multi-services (API + Streamlit)

### 🌐 **Plateformes de Déploiement**

#### **Render** (Recommandé) ⭐⭐⭐⭐⭐
- `render.yaml` - Configuration automatique pour Render
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

## 🎯 **Déploiement Rapide**

### Option 1 : Script Automatisé
```bash
cd SolarNasih_Deploiement
./deploy.sh
```

### Option 2 : Déploiement Manuel

#### **Render (Recommandé)**
1. Copiez `render.yaml` à la racine de votre projet
2. Allez sur [render.com](https://render.com)
3. Connectez votre repo GitHub
4. Créez un nouveau Web Service
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
```

## 📋 **Instructions par Plateforme**

### **Render**
1. Copiez `render.yaml` à la racine du projet
2. Poussez sur GitHub
3. Connectez sur Render.com
4. Déployez automatiquement

### **Railway**
1. Copiez `railway.json` à la racine du projet
2. Importez sur Railway.app
3. Configurez les variables d'environnement

### **Heroku**
1. Copiez `Procfile` et `runtime.txt` à la racine
2. Installez Heroku CLI
3. Déployez avec `git push heroku main`

### **Streamlit Cloud**
1. Copiez `.streamlit/` à la racine du projet
2. Allez sur share.streamlit.io
3. Connectez votre repo GitHub
4. Sélectionnez `streamlit_app.py`

## 🎉 **Félicitations !**

Votre **Solar Nasih SMA** est maintenant prêt pour le déploiement !

**URLs typiques après déploiement :**
- 🌐 **Application** : `https://solar-nasih.onrender.com`
- 📚 **Documentation** : `https://solar-nasih.onrender.com/docs`
- 🔧 **API** : `https://solar-nasih-api.onrender.com`
- 📱 **Interface** : `https://solar-nasih-streamlit.onrender.com`

---

**🚀 Votre SMA Solar Nasih va maintenant conquérir le monde ! ☀️** 