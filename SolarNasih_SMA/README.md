# ☀️ Solar Nasih SMA - Système Multi-Agent Solaire

Un système multi-agent intelligent spécialisé dans le conseil en énergie solaire, utilisant l'IA générative et le RAG (Retrieval-Augmented Generation).

## 🚀 Déploiement Rapide

### Option 1 : Déploiement Automatisé (Recommandé)

```bash
# Cloner le projet
git clone <votre-repo>
cd SolarNasih_SMA

# Exécuter le script de déploiement
./deploy.sh
```

### Option 2 : Déploiement Manuel

#### Prérequis
- Python 3.11+
- Clés API : Gemini et Tavily
- Compte sur une plateforme de déploiement

#### Étapes
1. **Configurer les variables d'environnement**
2. **Choisir une plateforme** (Render, Railway, Heroku)
3. **Suivre le guide** dans `DEPLOYMENT.md`

## 🎯 Plateformes Gratuites Recommandées

| Plateforme | Avantages | Limitations | Recommandation |
|------------|-----------|-------------|----------------|
| **Render** | 750h/mois, SSL gratuit, auto-déploiement | Sleep après 15min | ⭐⭐⭐⭐⭐ |
| **Railway** | $5 crédit/mois, très simple | Crédit limité | ⭐⭐⭐⭐ |
| **Heroku** | Très populaire, bonne documentation | 550-1000h/mois | ⭐⭐⭐ |

## 🏗️ Architecture

```
Solar Nasih SMA
├── 🤖 Agents Spécialisés
│   ├── EnergySimulatorAgent
│   ├── TechnicalAdvisorAgent
│   ├── CommercialAssistantAgent
│   ├── RegulatoryAssistantAgent
│   ├── CertificationAssistantAgent
│   ├── EducationalAgent
│   ├── DocumentGeneratorAgent
│   └── ResponseSummarizerAgent
├── 🔍 RAG System
├── 🌐 FastAPI Backend
└── 📱 Streamlit Frontend
```

## 🛠️ Fonctionnalités

### Agents Intelligents
- **Simulation énergétique** : Calculs de production et rentabilité
- **Conseils techniques** : Spécifications et installation
- **Assistance commerciale** : Devis et tarifs
- **Réglementation** : Lois et normes
- **Certification** : Standards et accréditations
- **Éducation** : Quiz et formation
- **Génération de documents** : Rapports professionnels
- **Formatage intelligent** : Réponses style ChatGPT

### Interface Utilisateur
- **Chat interactif** : Interface conversationnelle
- **Upload de documents** : Support multi-format
- **Traitement vocal** : Reconnaissance et synthèse
- **Historique** : Sauvegarde des conversations
- **Documentation API** : Swagger/OpenAPI

## 📋 Configuration

### Variables d'Environnement

```bash
# APIs requises
GEMINI_API_KEY=votre_clé_gemini
TAVILY_API_KEY=votre_clé_tavily

# Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Installation Locale

```bash
# Cloner le projet
git clone <votre-repo>
cd SolarNasih_SMA

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos clés API

# Lancer l'application
python main.py
```

## 🚀 Déploiement

### Render (Recommandé)

1. **Connecter GitHub** sur [render.com](https://render.com)
2. **Créer un Web Service** avec votre repo
3. **Configuration** :
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Variables d'environnement** : Ajouter vos clés API
5. **Déployer** !

### Docker

```bash
# Construction
docker build -t solar-nasih-sma .

# Exécution
docker run -p 8000:8000 -e GEMINI_API_KEY=votre_clé solar-nasih-sma
```

### Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# URLs
# API: http://localhost:8000
# Streamlit: http://localhost:8501
# Docs: http://localhost:8000/docs
```

## 📊 Monitoring

### Endpoints de Santé
- `GET /health` : Statut général
- `GET /agents` : Liste des agents
- `GET /documents` : Documents indexés

### Logs
- Fichiers : `logs/solar_nasih.log`
- Niveau : INFO/DEBUG
- Rotation automatique

## 🔧 Développement

### Structure du Projet

```
SolarNasih_SMA/
├── agents/           # Agents spécialisés
├── config/           # Configuration
├── graph/            # Workflow LangGraph
├── models/           # Modèles de données
├── services/         # Services externes
├── static/           # Fichiers statiques
├── utils/            # Utilitaires
├── main.py           # API FastAPI
├── streamlit_app.py  # Interface Streamlit
└── requirements.txt  # Dépendances
```

### Ajouter un Nouvel Agent

1. **Créer la classe** dans `agents/`
2. **Implémenter** `process()` et `_get_system_prompt()`
3. **Ajouter** au workflow dans `graph/workflow.py`
4. **Tester** avec l'endpoint `/agents`

### Tests

```bash
# Tests unitaires
python -m pytest tests/unit/

# Tests d'intégration
python -m pytest tests/integration/

# Tests de déploiement
./deploy.sh
```

## 🐛 Dépannage

### Problèmes Courants

1. **Erreur de clé API**
   - Vérifier les variables d'environnement
   - Tester les clés individuellement

2. **Timeout des requêtes**
   - Augmenter les timeouts
   - Vérifier la connectivité réseau

3. **Erreur de port**
   - Utiliser `$PORT` (variable d'environnement)
   - Vérifier les conflits de port

4. **Dépendances manquantes**
   - Vérifier `requirements.txt`
   - Installer `ffmpeg` si nécessaire

### Logs de Débogage

```bash
# Activer le mode debug
export DEBUG=true

# Voir les logs en temps réel
tail -f logs/solar_nasih.log
```

## 📈 Performance

### Optimisations
- **Cache** : Mise en cache des réponses fréquentes
- **Pooling** : Connexions réutilisées
- **Async** : Requêtes asynchrones
- **Compression** : Réponses compressées

### Métriques
- Temps de réponse : < 5s
- Disponibilité : 99.9%
- Utilisation mémoire : < 512MB

## 🔒 Sécurité

### Bonnes Pratiques
- Variables d'environnement sécurisées
- Validation des entrées utilisateur
- Rate limiting
- HTTPS obligatoire
- Logs sécurisés

### Variables Sensibles
- Clés API (Gemini, Tavily)
- URLs de base de données
- Secrets d'application

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche feature
3. **Commit** vos changements
4. **Push** vers la branche
5. **Créer** une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation** : `DEPLOYMENT.md`
- **Issues** : GitHub Issues
- **Email** : [votre-email]

---

## 🎉 Félicitations !

Votre SMA Solar Nasih est maintenant prêt pour le déploiement !

**Prochaines étapes** :
1. Choisir une plateforme de déploiement
2. Configurer les variables d'environnement
3. Déployer avec `./deploy.sh`
4. Tester l'application
5. Partager avec vos utilisateurs !

**URLs typiques après déploiement** :
- 🌐 Application : `https://solar-nasih.onrender.com`
- 📚 Documentation : `https://solar-nasih.onrender.com/docs`
- 🔧 API : `https://solar-nasih-api.onrender.com`
