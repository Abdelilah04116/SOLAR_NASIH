# 🚀 Guide de Déploiement - Solar Nasih SMA

## 📋 Prérequis

- Compte GitHub avec votre code
- Clés API : Gemini et Tavily
- Compte sur la plateforme de déploiement choisie

## 🎯 Plateformes Recommandées

### 1. **Render** (Recommandé) ⭐

#### Étapes de déploiement :

1. **Connecter GitHub** :
   - Allez sur [render.com](https://render.com)
   - Créez un compte et connectez votre repo GitHub

2. **Déployer l'API** :
   - Cliquez "New Web Service"
   - Sélectionnez votre repo
   - Configuration :
     ```
     Name: solar-nasih-api
     Environment: Python
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Variables d'environnement** :
   ```
   GEMINI_API_KEY=votre_clé_gemini
   TAVILY_API_KEY=votre_clé_tavily
   ENVIRONMENT=production
   ```

4. **Déployer Streamlit** :
   - Nouveau service web
   - Configuration :
     ```
     Name: solar-nasih-streamlit
     Build Command: pip install -r requirements.txt
     Start Command: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
     ```

### 2. **Railway**

1. **Connecter le repo** :
   - Allez sur [railway.app](https://railway.app)
   - Importez votre repo GitHub

2. **Configuration automatique** :
   - Railway détecte automatiquement Python
   - Utilise le `Dockerfile` ou `requirements.txt`

3. **Variables d'environnement** :
   - Ajoutez vos clés API dans l'interface

### 3. **Heroku**

1. **Installation CLI** :
   ```bash
   npm install -g heroku
   ```

2. **Déploiement** :
   ```bash
   heroku create solar-nasih-sma
   git push heroku main
   ```

3. **Variables d'environnement** :
   ```bash
   heroku config:set GEMINI_API_KEY=votre_clé
   heroku config:set TAVILY_API_KEY=votre_clé
   ```

## 🔧 Configuration Post-Déploiement

### 1. **Mise à jour de l'URL API**

Dans `streamlit_app.py`, remplacez :
```python
response = requests.post(
    "http://localhost:8000/chat",  # ← Ancien
    json={"message": user_input}
)
```

Par :
```python
response = requests.post(
    "https://votre-api-url.render.com/chat",  # ← Nouveau
    json={"message": user_input}
)
```

### 2. **Test des endpoints**

Testez votre API déployée :
```bash
curl -X POST "https://votre-api-url/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour, comment ça va ?"}'
```

### 3. **Monitoring**

- **Render** : Dashboard intégré
- **Railway** : Logs en temps réel
- **Heroku** : `heroku logs --tail`

## 🛠️ Dépannage

### Problèmes courants :

1. **Erreur de port** :
   - Assurez-vous d'utiliser `$PORT` (variable d'environnement)

2. **Dépendances manquantes** :
   - Vérifiez `requirements.txt`
   - Ajoutez `ffmpeg` si nécessaire

3. **Clés API manquantes** :
   - Vérifiez les variables d'environnement
   - Testez localement d'abord

4. **Timeout** :
   - Augmentez les timeouts dans la configuration

## 📊 Monitoring et Maintenance

### Logs à surveiller :
- Erreurs d'API
- Timeouts de requêtes
- Utilisation mémoire/CPU

### Mise à jour :
- Déploiement automatique depuis GitHub
- Tests avant déploiement
- Rollback en cas de problème

## 🔒 Sécurité

### Recommandations :
- Variables d'environnement sécurisées
- HTTPS obligatoire
- Rate limiting
- Validation des entrées

### Variables sensibles :
- Clés API
- URLs de base de données
- Secrets d'application

## 📈 Optimisation

### Performance :
- Cache Redis (optionnel)
- CDN pour les fichiers statiques
- Optimisation des requêtes

### Coûts :
- Monitoring de l'utilisation
- Optimisation des ressources
- Planification des mises à l'échelle

---

## 🎉 Félicitations !

Votre SMA Solar Nasih est maintenant déployé et accessible en ligne !

**URLs typiques** :
- API : `https://solar-nasih-api.onrender.com`
- Interface : `https://solar-nasih-streamlit.onrender.com`
- Documentation : `https://solar-nasih-api.onrender.com/docs` 