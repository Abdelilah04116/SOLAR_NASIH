# 🚀 SOLAR NASIH - Démarrage Unifié

## 📋 Vue d'ensemble

Ce dossier contient **un seul fichier requirements.txt** et **une seule commande** pour démarrer tout le projet SolarNasih (SMA + RAG + Template + Services).

## 📦 Fichier Requirements Unifié

### `requirements_unified.txt`
Ce fichier contient **TOUTES** les dépendances Python pour SMA et RAG :

```bash
# Installation en une seule commande
pip install -r SolarNasih_Deploiement_Complet/requirements_unified.txt
```

**Inclut :**
- ✅ FastAPI, Uvicorn (APIs)
- ✅ LangChain, Transformers (IA)
- ✅ Google Gemini, OpenAI, Anthropic (APIs)
- ✅ Qdrant, Redis (Bases de données)
- ✅ Pillow, OpenCV (Traitement d'images)
- ✅ Whisper, Librosa (Traitement audio)
- ✅ PyPDF2, python-docx (Documents)
- ✅ Et bien plus encore...

## 🚀 Démarrage en Une Seule Commande

### ⚡ Méthode Rapide

**Sur Windows (PowerShell) :**
```powershell
.\SolarNasih_Deploiement_Complet\start_all_services.ps1
```

**Sur Linux/Mac (Bash) :**
```bash
./SolarNasih_Deploiement_Complet/start_all_services.sh
```

**Ou avec Python :**
```bash
python SolarNasih_Deploiement_Complet/start_all_services.py
```

### 🔧 Ce que fait la commande

1. ✅ **Vérifie** tous les composants (SMA, RAG, Template)
2. 📦 **Installe** les dépendances Python unifiées
3. 📦 **Installe** les dépendances Node.js
4. 🗄️ **Démarre** Redis avec Docker (si disponible)
5. 🔍 **Démarre** Qdrant avec Docker (si disponible)
6. 🚀 **Démarre** SMA API sur le port 8000
7. 🤖 **Démarre** RAG API sur le port 8001
8. 🌐 **Démarre** Frontend sur le port 5173

## 📊 Services Démarés

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **SMA API** | 8000 | `http://localhost:8000` | Solar Management Assistant |
| **RAG API** | 8001 | `http://localhost:8001` | Retrieval-Augmented Generation |
| **Frontend** | 5173 | `http://localhost:5173` | Interface React/TypeScript |
| **Redis** | 6379 | `localhost:6379` | Cache (si Docker disponible) |
| **Qdrant** | 6333 | `localhost:6333` | Base vectorielle (si Docker disponible) |

## 🎯 Utilisation

### 1. Prérequis
- Python 3.11+
- Node.js 18+
- Git
- Docker (optionnel, pour Redis et Qdrant)

### 2. Démarrage
```bash
# Cloner le projet (si pas déjà fait)
git clone <votre-repo>
cd SOLAR_NASIH

# Démarrer tous les services
python SolarNasih_Deploiement_Complet/start_all_services.py
```

### 3. Accès aux services
- **Interface principale** : http://localhost:5173
- **SMA API Docs** : http://localhost:8000/docs
- **RAG API Docs** : http://localhost:8001/docs

### 4. Arrêt
Appuyez sur **Ctrl+C** pour arrêter tous les services proprement.

## 📁 Structure des Fichiers

```
SolarNasih_Deploiement_Complet/
├── requirements_unified.txt        # 📦 Dépendances unifiées
├── start_all_services.py          # 🐍 Script Python principal
├── start_all_services.ps1         # 💻 Script PowerShell (Windows)
├── start_all_services.sh          # 🐧 Script Bash (Linux/Mac)
├── deploy_render_unified.py       # ☁️ Déploiement Render
├── deploy-unified.ps1             # ☁️ Déploiement Render (Windows)
├── deploy-unified.sh              # ☁️ Déploiement Render (Linux/Mac)
├── render-unified.yaml            # ☁️ Configuration Render (généré)
├── Dockerfile.qdrant             # 🐳 Docker pour Qdrant
├── README_UNIFIED.md             # 📚 Documentation déploiement
└── README_START_ALL.md           # 📚 Ce fichier
```

## 🔧 Configuration des Variables d'Environnement

Créez un fichier `.env` à la racine du projet :

```bash
# API Keys
GEMINI_API_KEY=votre_clé_gemini
TAVILY_API_KEY=votre_clé_tavily
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic

# URLs locales
SMA_API_URL=http://localhost:8000
RAG_API_URL=http://localhost:8001
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
```

## 🎯 Avantages de cette approche

✅ **Un seul fichier requirements.txt** pour tout  
✅ **Une seule commande** pour démarrer tous les services  
✅ **Installation automatique** des dépendances  
✅ **Démarrage en parallèle** de tous les services  
✅ **Gestion automatique** des processus  
✅ **Arrêt propre** avec Ctrl+C  
✅ **Scripts multiplateformes** (Windows/Linux/Mac)  
✅ **Support Docker** pour Redis et Qdrant  

## 🚨 Dépannage

### Erreur "Composants manquants"
```bash
# Assurez-vous d'être dans le répertoire racine
cd /chemin/vers/SOLAR_NASIH
```

### Erreur de permissions (Linux/Mac)
```bash
chmod +x SolarNasih_Deploiement_Complet/start_all_services.sh
```

### Erreur PowerShell (Windows)
```powershell
# Exécutez en tant qu'administrateur ou changez la politique
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erreur de dépendances
```bash
# Réinstaller les dépendances
pip install -r SolarNasih_Deploiement_Complet/requirements_unified.txt --force-reinstall
```

### Services non accessibles
1. Vérifiez que les ports 8000, 8001, 5173 ne sont pas utilisés
2. Vérifiez que Docker est installé pour Redis/Qdrant
3. Consultez les logs dans le terminal

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que tous les composants sont présents
2. Assurez-vous d'avoir Python 3.11+ et Node.js 18+
3. Vérifiez que les ports sont libres
4. Consultez les messages d'erreur dans le terminal

---

**🎉 Démarrage unifié prêt ! Une seule commande pour tout démarrer !**
