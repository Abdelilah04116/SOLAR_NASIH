# 🚀 SolarNasih Frontend - Guide de Déploiement sur Vercel

## 📋 Vue d'ensemble

Ce guide vous accompagne pour déployer le **Frontend React/TypeScript** de SolarNasih sur Vercel.

## 🛠️ Prérequis

- Compte Vercel (gratuit)
- Compte GitHub
- Node.js 18+ installé localement
- Les services SMA et RAG déployés sur Render

## 📦 Structure du Projet

```
Frontend_Deploy/
├── vercel.json          # Configuration Vercel
├── package.json         # Dépendances Node.js
├── env.example          # Variables d'environnement
└── README.md           # Ce guide
```

## 🚀 Déploiement sur Vercel

### Étape 1 : Préparation du Repository

1. Assurez-vous que votre code frontend est dans le dossier `SolarNasih_Template/`
2. Le projet doit être un projet Vite + React + TypeScript
3. Le fichier principal doit être `src/main.tsx`

### Étape 2 : Configuration Vercel

1. **Connectez votre repository GitHub à Vercel** :
   - Allez sur [Vercel](https://vercel.com)
   - Cliquez sur "New Project"
   - Importez votre repository GitHub

2. **Configuration du projet** :
   - **Framework Preset** : Vite
   - **Root Directory** : `SolarNasih_Template`
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`
   - **Install Command** : `npm install`

### Étape 3 : Configuration des Variables d'Environnement

Dans Vercel, configurez les variables suivantes :

#### 🔗 URLs des APIs (OBLIGATOIRES)
```
VITE_SMA_API_URL=https://solar-nasih-sma.onrender.com
VITE_RAG_API_URL=https://solar-nasih-rag.onrender.com
```

#### ⚙️ Configuration de l'Application
```
VITE_APP_NAME=SolarNasih
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

#### 🔧 Configuration des Fonctionnalités
```
VITE_ENABLE_CHAT=true
VITE_ENABLE_FILE_UPLOAD=true
VITE_ENABLE_VOICE_INPUT=true
VITE_ENABLE_IMAGE_ANALYSIS=true
```

### Étape 4 : Déploiement

1. **Cliquez sur "Deploy"** dans Vercel
2. **Attendez le déploiement** (2-5 minutes)
3. **Vérifiez les logs** pour détecter d'éventuelles erreurs

## 🔧 Configuration Avancée

### Configuration Vercel (vercel.json)

Le fichier `vercel.json` configure :
- **Build** : Configuration du build Vite
- **Routes** : Gestion des routes SPA
- **Headers** : Sécurité et performance
- **Environment** : Variables d'environnement

### Variables d'Environnement Avancées

```bash
# Configuration des limites
VITE_MAX_FILE_SIZE=52428800  # 50MB
VITE_MAX_MESSAGE_LENGTH=4000
VITE_MAX_CONVERSATION_LENGTH=50

# Configuration de l'interface
VITE_THEME=light
VITE_LANGUAGE=fr
VITE_TIMEZONE=Europe/Paris

# Configuration de la sécurité
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_ERROR_REPORTING=false
```

## 🧪 Test du Déploiement

### Test de l'Application

1. **Accédez à votre URL Vercel** :
   ```
   https://solar-nasih-frontend.vercel.app
   ```

2. **Testez les fonctionnalités** :
   - Interface utilisateur
   - Connexion aux APIs SMA et RAG
   - Upload de fichiers
   - Chat avec l'IA

### Logs et Monitoring

- **Logs** : Accessibles dans l'interface Vercel
- **Analytics** : Vercel Analytics (optionnel)
- **Performance** : Core Web Vitals automatiques

## 🔗 Intégration avec les APIs

### Configuration des URLs

Le frontend se connecte automatiquement à :
- **SMA** : `https://solar-nasih-sma.onrender.com`
- **RAG** : `https://solar-nasih-rag.onrender.com`

### CORS Configuration

Assurez-vous que les services Render autorisent les requêtes depuis :
```
https://solar-nasih-frontend.vercel.app
```

## 🚨 Dépannage

### Erreurs Communes

1. **Build Errors** :
   - Vérifiez les erreurs TypeScript
   - Corrigez les imports manquants
   - Vérifiez `package.json`

2. **API Connection Errors** :
   - Vérifiez les URLs dans les variables d'environnement
   - Testez les APIs directement
   - Vérifiez la configuration CORS

3. **Runtime Errors** :
   - Vérifiez les logs Vercel
   - Testez localement avec `npm run dev`

### Logs d'Erreur

```bash
# Vérifiez les logs dans Vercel
# Ou utilisez l'API Vercel pour récupérer les logs
```

## 🔄 Mise à Jour

### Déploiement Automatique

Vercel redéploie automatiquement quand vous :
1. Poussez sur la branche `main`
2. Créez une Pull Request
3. Modifiez les variables d'environnement

### Déploiement Manuel

```bash
# Installer Vercel CLI
npm i -g vercel

# Déployer manuellement
vercel --prod
```

## 📱 Optimisations

### Performance

- **Code Splitting** : Automatique avec Vite
- **Lazy Loading** : Images et composants
- **Caching** : Headers optimisés dans `vercel.json`

### SEO

- **Meta Tags** : Configuration dans `index.html`
- **Sitemap** : Génération automatique
- **Open Graph** : Tags pour les réseaux sociaux

## 📞 Support

En cas de problème :
1. Vérifiez les logs Vercel
2. Testez localement avec `npm run dev`
3. Vérifiez la configuration des variables d'environnement
4. Consultez la [documentation Vercel](https://vercel.com/docs)

## 🔄 Mise à Jour

Pour mettre à jour le frontend :
1. Poussez les changements sur GitHub
2. Vercel redéploiera automatiquement
3. Ou déclenchez un redéploiement manuel

---

**✅ Votre frontend est maintenant prêt et connecté aux services SMA et RAG !**
