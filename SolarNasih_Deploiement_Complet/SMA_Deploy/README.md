# 🚀 SolarNasih SMA - Guide de Déploiement sur Render

## 📋 Vue d'ensemble

Ce guide vous accompagne pour déployer le service **SMA (Solar Management Assistant)** sur Render.

## 🛠️ Prérequis

- Compte Render (gratuit ou payant)
- API Keys pour les services IA :
  - Google Gemini API
  - OpenAI API (optionnel)
  - Anthropic API (optionnel)
  - Tavily API (optionnel)

## 📦 Structure du Projet

```
SMA_Deploy/
├── requirements.txt      # Dépendances Python
├── render.yaml          # Configuration Render
├── env.example          # Variables d'environnement
└── README.md           # Ce guide
```

## 🚀 Déploiement sur Render

### Étape 1 : Préparation du Repository

1. Assurez-vous que votre code SMA est dans le dossier `SolarNasih_SMA/`
2. Le fichier principal doit être `main.py` avec une application FastAPI

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
PORT=8000
WORKERS=1

# Configuration des fichiers
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Configuration de la sécurité
JWT_SECRET=votre_secret_jwt
JWT_EXPIRATION=3600
```

## 🧪 Test du Déploiement

### Endpoints de Test

```bash
# Test de santé
curl https://solar-nasih-sma.onrender.com/health

# Test de l'API
curl https://solar-nasih-sma.onrender.com/docs
```

### Logs et Monitoring

- **Logs** : Accessibles dans l'interface Render
- **Métriques** : Monitoring automatique
- **Health Check** : `/health` endpoint

## 🔗 Intégration avec le Frontend

Le service SMA sera accessible à :
```
https://solar-nasih-sma.onrender.com
```

Le frontend Vercel utilisera cette URL pour les requêtes API.

## 🚨 Dépannage

### Erreurs Communes

1. **ModuleNotFoundError** :
   - Vérifiez `requirements.txt`
   - Redéployez après modification

2. **API Key manquante** :
   - Configurez `GEMINI_API_KEY` dans Render

3. **CORS Errors** :
   - Vérifiez `CORS_ORIGINS` dans les variables d'environnement

### Logs d'Erreur

```bash
# Vérifiez les logs dans Render
# Ou utilisez l'API Render pour récupérer les logs
```

## 📞 Support

En cas de problème :
1. Vérifiez les logs Render
2. Testez localement avec `uvicorn main:app --reload`
3. Vérifiez la configuration des variables d'environnement

## 🔄 Mise à Jour

Pour mettre à jour le service :
1. Poussez les changements sur GitHub
2. Render redéploiera automatiquement
3. Ou déclenchez un redéploiement manuel

---

**✅ Votre service SMA est maintenant prêt à être utilisé par le frontend !**
