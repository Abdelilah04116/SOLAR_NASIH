#!/bin/bash

# Script de déploiement automatisé pour Solar Nasih SMA
echo "🚀 Déploiement Solar Nasih SMA"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
print_status "Vérification des prérequis..."

# Vérifier si git est installé
if ! command -v git &> /dev/null; then
    print_error "Git n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si les clés API sont définies
if [ -z "$GEMINI_API_KEY" ]; then
    print_warning "GEMINI_API_KEY n'est pas définie. Veuillez la définir."
fi

if [ -z "$TAVILY_API_KEY" ]; then
    print_warning "TAVILY_API_KEY n'est pas définie. Veuillez la définir."
fi

print_status "Prérequis vérifiés avec succès!"

# Menu de sélection de plateforme
echo ""
echo "📋 Sélectionnez votre plateforme de déploiement :"
echo "1) Render (Recommandé)"
echo "2) Railway"
echo "3) Heroku"
echo "4) Docker local"
echo "5) Quitter"
echo ""

read -p "Votre choix (1-5): " choice

case $choice in
    1)
        print_status "Déploiement sur Render..."
        deploy_render
        ;;
    2)
        print_status "Déploiement sur Railway..."
        deploy_railway
        ;;
    3)
        print_status "Déploiement sur Heroku..."
        deploy_heroku
        ;;
    4)
        print_status "Déploiement Docker local..."
        deploy_docker_local
        ;;
    5)
        print_status "Au revoir!"
        exit 0
        ;;
    *)
        print_error "Choix invalide"
        exit 1
        ;;
esac

# Fonction de déploiement Render
deploy_render() {
    print_status "Configuration pour Render..."
    
    # Vérifier si le repo est sur GitHub
    if ! git remote get-url origin | grep -q "github.com"; then
        print_error "Le repo doit être sur GitHub pour Render"
        print_status "Poussez votre code sur GitHub d'abord"
        exit 1
    fi
    
    print_status "✅ Prêt pour Render!"
    print_status "1. Allez sur https://render.com"
    print_status "2. Connectez votre repo GitHub"
    print_status "3. Créez un nouveau Web Service"
    print_status "4. Utilisez le fichier render.yaml"
    print_status "5. Ajoutez vos variables d'environnement"
}

# Fonction de déploiement Railway
deploy_railway() {
    print_status "Configuration pour Railway..."
    
    # Vérifier si Railway CLI est installé
    if ! command -v railway &> /dev/null; then
        print_status "Installation de Railway CLI..."
        npm install -g @railway/cli
    fi
    
    print_status "✅ Prêt pour Railway!"
    print_status "1. Allez sur https://railway.app"
    print_status "2. Importez votre repo GitHub"
    print_status "3. Ajoutez vos variables d'environnement"
}

# Fonction de déploiement Heroku
deploy_heroku() {
    print_status "Configuration pour Heroku..."
    
    # Vérifier si Heroku CLI est installé
    if ! command -v heroku &> /dev/null; then
        print_status "Installation de Heroku CLI..."
        npm install -g heroku
    fi
    
    # Vérifier si l'utilisateur est connecté à Heroku
    if ! heroku auth:whoami &> /dev/null; then
        print_status "Connexion à Heroku..."
        heroku login
    fi
    
    # Créer l'app Heroku
    print_status "Création de l'application Heroku..."
    heroku create solar-nasih-sma-$(date +%s)
    
    # Configurer les variables d'environnement
    if [ ! -z "$GEMINI_API_KEY" ]; then
        heroku config:set GEMINI_API_KEY="$GEMINI_API_KEY"
    fi
    
    if [ ! -z "$TAVILY_API_KEY" ]; then
        heroku config:set TAVILY_API_KEY="$TAVILY_API_KEY"
    fi
    
    heroku config:set ENVIRONMENT=production
    
    # Déployer
    print_status "Déploiement sur Heroku..."
    git push heroku main
    
    print_status "✅ Déployé sur Heroku!"
    print_status "URL: $(heroku info -s | grep web_url | cut -d= -f2)"
}

# Fonction de déploiement Docker local
deploy_docker_local() {
    print_status "Configuration Docker local..."
    
    # Vérifier si Docker est installé
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier si Docker Compose est installé
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f ".env" ]; then
        print_status "Création du fichier .env..."
        cp env.example .env
        print_warning "Veuillez configurer vos clés API dans le fichier .env"
    fi
    
    # Construire et démarrer les conteneurs
    print_status "Construction des images Docker..."
    docker-compose build
    
    print_status "Démarrage des services..."
    docker-compose up -d
    
    print_status "✅ Déployé localement avec Docker!"
    print_status "API: http://localhost:8000"
    print_status "Streamlit: http://localhost:8501"
    print_status "Documentation: http://localhost:8000/docs"
}

print_status "🎉 Déploiement terminé!"
print_status "Consultez DEPLOYMENT.md pour plus de détails" 