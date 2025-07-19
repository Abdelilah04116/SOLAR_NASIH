# 🚀 Guide de Déploiement - RAG Multimodal System

Ce guide vous accompagne dans le déploiement du système RAG multimodal sur différents environnements.

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Déploiement Local](#déploiement-local)
3. [Déploiement Docker](#déploiement-docker)
4. [Déploiement Cloud](#déploiement-cloud)
5. [Configuration Production](#configuration-production)
6. [Monitoring et Logs](#monitoring-et-logs)

## 🔧 Prérequis

### Système
- Python 3.11+
- Docker & Docker Compose
- Git
- 4GB RAM minimum
- 10GB espace disque

### Services externes
- Qdrant (vector database)
- Redis (cache)
- OpenAI API key (optionnel)

## 🏠 Déploiement Local

### Option 1: Développement direct

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# 3. Lancer Qdrant (optionnel - peut être lancé via Docker)
docker run -p 6333:6333 qdrant/qdrant:latest

# 4. Lancer l'API
python run_api.py

# 5. Lancer le frontend (nouveau terminal)
python run_frontend.py
```

### Option 2: Avec Docker Compose

```bash
# 1. Construire et lancer tous les services
docker-compose up -d

# 2. Vérifier les services
docker-compose ps

# 3. Voir les logs
docker-compose logs -f rag-app
```

## 🐳 Déploiement Docker

### Construction de l'image

```bash
# Construire l'image
docker build -t rag-multimodal:latest .

# Tester l'image
docker run -p 8000:8000 -p 8501:8501 rag-multimodal:latest
```

### Docker Compose complet

```bash
# Lancer tous les services
docker-compose up -d

# Services disponibles:
# - API: http://localhost:8000
# - Frontend: http://localhost:8501
# - Qdrant: http://localhost:6333
# - Redis: localhost:6379
```

## ☁️ Déploiement Cloud

### AWS ECS

1. **Préparer l'image**
```bash
# Construire l'image
docker build -t rag-multimodal:latest .

# Pousser vers ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag rag-multimodal:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/rag-multimodal:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/rag-multimodal:latest
```

2. **Déployer avec ECS**
```bash
# Créer le cluster
aws ecs create-cluster --cluster-name rag-multimodal-cluster

# Créer la définition de tâche
aws ecs register-task-definition --cli-input-json file://deployment/aws/ecs-task-definition.json

# Créer le service
aws ecs create-service \
    --cluster rag-multimodal-cluster \
    --service-name rag-multimodal-service \
    --task-definition rag-multimodal-system \
    --desired-count 1
```

### Azure Container Instances

1. **Préparer l'image**
```bash
# Se connecter à Azure Container Registry
az acr login --name ragmultimodal

# Construire et pousser l'image
docker build -t ragmultimodal.azurecr.io/rag-multimodal:latest .
docker push ragmultimodal.azurecr.io/rag-multimodal:latest
```

2. **Déployer**
```bash
# Créer le groupe de ressources
az group create --name rag-multimodal-rg --location eastus

# Déployer avec Azure CLI
az container create \
    --resource-group rag-multimodal-rg \
    --name rag-multimodal-system \
    --image ragmultimodal.azurecr.io/rag-multimodal:latest \
    --ports 8000 8501 \
    --dns-name-label rag-multimodal \
    --environment-variables QDRANT_URL=http://qdrant:6333 REDIS_URL=redis://redis:6379
```

### Google Cloud Run

```bash
# Construire et pousser l'image
docker build -t gcr.io/PROJECT_ID/rag-multimodal:latest .
docker push gcr.io/PROJECT_ID/rag-multimodal:latest

# Déployer sur Cloud Run
gcloud run deploy rag-multimodal \
    --image gcr.io/PROJECT_ID/rag-multimodal:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8000
```

## ⚙️ Configuration Production

### Variables d'environnement critiques

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Base de données
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379

# Sécurité
SECRET_KEY=your-secret-key-here
DEBUG=false

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

### Configuration Nginx (optionnel)

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server rag-app:8000;
    }
    
    upstream frontend {
        server rag-app:8501;
    }
    
    server {
        listen 80;
        server_name your-domain.com;
        
        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## 📊 Monitoring et Logs

### Logs Docker

```bash
# Voir les logs de l'application
docker-compose logs -f rag-app

# Voir les logs de Qdrant
docker-compose logs -f qdrant

# Voir tous les logs
docker-compose logs -f
```

### Monitoring avec Prometheus/Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Health Checks

```bash
# Vérifier la santé de l'API
curl http://localhost:8000/health/

# Vérifier la santé détaillée
curl http://localhost:8000/health/detailed

# Vérifier le statut du système
curl http://localhost:8000/status
```

## 🔒 Sécurité

### Bonnes pratiques

1. **Variables d'environnement**
   - Ne jamais commiter les clés API
   - Utiliser des secrets managers en production
   - Chiffrer les données sensibles

2. **Réseau**
   - Utiliser des réseaux privés
   - Configurer des firewalls
   - Limiter l'accès aux ports

3. **Authentification**
   - Implémenter JWT tokens
   - Utiliser HTTPS en production
   - Configurer CORS correctement

### Exemple de configuration sécurisée

```bash
# .env.production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-domain.com

# Base de données sécurisée
QDRANT_URL=https://qdrant.your-domain.com
REDIS_URL=rediss://redis.your-domain.com:6379
```

## 🚨 Troubleshooting

### Problèmes courants

1. **Port déjà utilisé**
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8000
# Tuer le processus
kill -9 PID
```

2. **Mémoire insuffisante**
```bash
# Augmenter la mémoire Docker
# Dans Docker Desktop > Settings > Resources
```

3. **Erreurs de connexion à Qdrant**
```bash
# Vérifier que Qdrant est lancé
docker ps | grep qdrant
# Redémarrer le service
docker-compose restart qdrant
```

### Logs d'erreur

```bash
# Logs d'erreur de l'API
docker-compose logs rag-app | grep ERROR

# Logs de démarrage
docker-compose logs rag-app | grep "Starting"

# Logs de Qdrant
docker-compose logs qdrant
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale l'application
docker-compose up -d --scale rag-app=3

# Avec load balancer
docker-compose up -d nginx
```

### Vertical Scaling

```yaml
# docker-compose.yml
services:
  rag-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## 🎯 Conclusion

Ce guide couvre les principales méthodes de déploiement. Choisissez celle qui correspond le mieux à vos besoins :

- **Développement** : Déploiement local direct
- **Test/Staging** : Docker Compose
- **Production** : Cloud (AWS/Azure/GCP)

Pour toute question ou problème, consultez les logs et la documentation des services utilisés.

