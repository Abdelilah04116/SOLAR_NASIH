# 🚀 Solar Nasih - Fichiers de Déploiement

Ce dossier contient tous les fichiers nécessaires pour déployer votre **Solar Nasih SMA** sur différentes plateformes, **sans modifier le projet principal**.

## 🎯 **Approche : Séparation des Composants**

Chaque composant garde sa fonction propre :
- **`SolarNasih_SMA/`** : Code source principal (inchangé)
- **`SolarNasih_Deploiement/`** : Fichiers de déploiement (séparé)

## 🚨 **DÉPLOIEMENT RAPIDE (Sans modifier le projet principal)**

### Option 1 : Configuration Render Manuelle (Recommandé)

1. **Ouvrez le fichier `deploy_commands.txt`** dans ce dossier
2. **Copiez les commandes** dans Render :
   - Build Command
   - Start Command
   - Variables d'environnement

### Option 2 : Script Automatisé

```bash
cd SolarNasih_Deploiement
python deploy_render_only.py
```

### Option 3 : Fichiers Temporaires

```bash
cd SolarNasih_Deploiement
python deploy_render_only.py --temp
# Puis copiez les fichiers temporaires vers votre projet
```

## 📁 Structure des Fichiers

### 🐳 **Docker & Containerisation**
- `Dockerfile` - Configuration Docker pour containeriser l'application
- `docker-compose.yml` - Orchestration multi-services (API + Streamlit)

### 🌐 **Plateformes de Déploiement**

#### **Render** (Recommandé) ⭐⭐⭐⭐⭐
- `render.yaml` - Configuration automatique pour Render
- `render_fixed.yaml` - Configuration corrigée
- `render_ultra_minimal.yaml` - Configuration ultra-minimale
- `deploy_commands.txt` - **NOUVEAU** Commandes à copier manuellement
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
- `deploy_render_only.py` - **NOUVEAU** Script de déploiement Render
- `DEPLOYMENT.md` - Guide détaillé de déploiement
- `DEPLOYMENT_FIXED.md` - Guide corrigé

### 📦 **Requirements (Dépendances)**
- `requirements_deploy.txt` - Dépendances complètes
- `requirements_minimal.txt` - Dépendances minimales
- `requirements_ultra_minimal.txt` - Dépendances ultra-minimales

## 🎯 **Déploiement Rapide**

### Option 1 : Configuration Manuelle Render

1. **Ouvrez `deploy_commands.txt`** dans ce dossier
2. **Allez sur [render.com](https://render.com)**
3. **Créez un nouveau Web Service**
4. **Connectez votre repo GitHub**
5. **Copiez les commandes** du fichier `deploy_commands.txt`
6. **Ajoutez vos variables d'environnement**

### Option 2 : Script Automatisé
```bash
cd SolarNasih_Deploiement
./deploy.sh
```

### Option 3 : Déploiement Manuel

#### **Render (Recommandé)**
1. Utilisez `deploy_commands.txt` pour les commandes
2. Allez sur [render.com](https://render.com)
3. Connectez votre repo GitHub
4. Configurez manuellement avec les commandes fournies

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
1. Utilisez `deploy_commands.txt` pour les commandes
2. Configurez manuellement dans Render
3. Ajoutez `PYTHON_VERSION=3.11.0`
4. Connectez sur Render.com

### **Railway**
1. Utilisez `requirements_ultra_minimal.txt`
2. Importez sur Railway.app
3. Configurez les variables d'environnement

### **Heroku**
1. Utilisez `requirements_ultra_minimal.txt`
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
**Solution :** Utilisez les commandes de `deploy_commands.txt`

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