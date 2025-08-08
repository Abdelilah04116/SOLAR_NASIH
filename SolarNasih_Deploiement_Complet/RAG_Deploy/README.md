# 🚀 SolarNasih RAG - Guide de Déploiement sur Render

## 📋 Vue d'ensemble

Ce guide vous accompagne pour déployer le service **RAG (Retrieval-Augmented Generation)** sur Render.

## 🛠️ Prérequis

- Compte Render (gratuit ou payant)
- API Keys pour les services IA :
  - Google Gemini API
  - OpenAI API (optionnel)
  - Anthropic API (optionnel)
  - Tavily API (optionnel)

## 📦 Structure du Projet

```
RAG_Deploy/
├── requirements.txt      # Dépendances Python
├── render.yaml          # Configuration Render
├── env.example          # Variables d'environnement
└── README.md           # Ce guide
```

## 🚀 Déploiement sur Render

### Étape 1 : Préparation du Repository

1. Assurez-vous que votre code RAG est dans le dossier `SolarNasih_RAG/`
2. Le fichier principal doit être `api_simple.py` avec une application FastAPI

### Étape 2 : Configuration Render

1. **Connectez votre repository GitHub à Render**
2. **Créez un nouveau Blueprint** :
   - Allez sur [Render Blueprints](https://render.com/docs/blueprint-spec)
   - Cliquez sur "New Blueprint Instance"
   - Collez le contenu de `render.yaml`

### Étape 3 : Configuration des Variables d'Environnement

Dans Render, configurez les variables suivantes :

#### 🔑 API Keys (OBLIGATOIRES)
```
GEMINI_API_KEY=votre_clé_gemini_ici
```

#### 🔑 API Keys (OPTIONNELLES)
```
OPENAI_API_KEY=votre_clé_openai_ici
ANTHROPIC_API_KEY=votre_clé_anthropic_ici
TAVILY_API_KEY=votre_clé_tavily_ici
```

#### ⚙️ Configuration
```
ENVIRONMENT=production
CORS_ORIGINS=https://solar-nasih-frontend.vercel.app,http://localhost:3000
```

### Étape 4 : Déploiement

1. **Cliquez sur "Apply"** dans Render
2. **Attendez le déploiement** (5-10 minutes)
3. **Vérifiez les logs** pour détecter d'éventuelles erreurs

## 🔧 Configuration Avancée

### Services Optionnels

Le Blueprint inclut automatiquement :
- **Redis** : Pour le cache
- **Qdrant** : Pour la base vectorielle

### Variables d'Environnement Avancées

```bash
# Configuration du serveur
HOST=0.0.0.0
PORT=8001
WORKERS=1

# Configuration des fichiers
UPLOAD_DIR=./uploads
VECTOR_STORE_DIR=./vector_store
MAX_FILE_SIZE=52428800  # 50MB

# Configuration de la base vectorielle
COLLECTION_NAME=solar_nasih_documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 🧪 Test du Déploiement

### Endpoints de Test

```bash
# Test de santé
curl https://solar-nasih-rag.onrender.com/health

# Test de l'API
curl https://solar-nasih-rag.onrender.com/docs

# Test d'upload de fichier
curl -X POST https://solar-nasih-rag.onrender.com/upload/file \
  -F "file=@document.pdf"
```

### Logs et Monitoring

- **Logs** : Accessibles dans l'interface Render
- **Métriques** : Monitoring automatique
- **Health Check** : `/health` endpoint

## 🔗 Intégration avec le Frontend

Le service RAG sera accessible à :
```
https://solar-nasih-rag.onrender.com
```

Le frontend Vercel utilisera cette URL pour les requêtes RAG.

## 🚨 Dépannage

### Erreurs Communes

1. **ModuleNotFoundError** :
   - Vérifiez `requirements.txt`
   - Redéployez après modification

2. **API Key manquante** :
   - Configurez `GEMINI_API_KEY` dans Render

3. **CORS Errors** :
   - Vérifiez `CORS_ORIGINS` dans les variables d'environnement

4. **Erreurs de stockage** :
   - Vérifiez les permissions d'écriture
   - Configurez `UPLOAD_DIR` et `VECTOR_STORE_DIR`

### Logs d'Erreur

```bash
# Vérifiez les logs dans Render
# Ou utilisez l'API Render pour récupérer les logs
```

## 📁 Gestion des Fichiers

### Upload de Documents

Le service RAG accepte :
- **PDF** : Documents PDF
- **DOCX** : Documents Word
- **TXT** : Fichiers texte
- **Images** : JPG, JPEG, PNG
- **Audio** : MP3, WAV
- **Vidéo** : MP4

### Base Vectorielle

- **Qdrant** : Stockage des embeddings
- **Collection** : `solar_nasih_documents`
- **Cache** : Redis pour les requêtes fréquentes

## 📞 Support

En cas de problème :
1. Vérifiez les logs Render
2. Testez localement avec `uvicorn api_simple:app --reload`
3. Vérifiez la configuration des variables d'environnement

## 🔄 Mise à Jour

Pour mettre à jour le service :
1. Poussez les changements sur GitHub
2. Render redéploiera automatiquement
3. Ou déclenchez un redéploiement manuel

---

**✅ Votre service RAG est maintenant prêt à être utilisé par le frontend !**
